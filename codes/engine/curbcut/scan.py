"""`curbcut scan`: measure the pages a pull request changes, on base and head.

Output is facts.json: measurements only, no verdicts about what they mean.
Pages that fail to load stay in the list as not scanned, with the reason.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, sync_playwright

from . import AXE_CORE_VERSION, FIXTURE_ROOT, __version__, browser
from .gitutil import changed_files, rev_parse, worktree
from .server import serve

VIEWPORT = {"width": 1280, "height": 800}
AXE_KIND = {"violations": "axe_violation", "incomplete": "axe_needs_review"}


def fact_id(kind: str, page: str, rule: str, selector: str) -> str:
    digest = hashlib.sha1(f"{kind}|{page}|{rule}|{selector}".encode("utf-8")).hexdigest()[:8]
    prefix = {"axe_violation": "axe", "axe_needs_review": "axr"}.get(kind, kind.split("_")[0][:5])
    return f"{prefix}-{digest}"


def _wcag_from_tags(tags: list[str]) -> list[str]:
    out = []
    for t in tags:
        if t.startswith("wcag") and t[4:].isdigit() and len(t) >= 7:
            d = t[4:]
            out.append(f"{d[0]}.{d[1]}.{d[2:]}")
    return out


def measure_page(b: Browser, url: str) -> dict[str, Any]:
    page = b.new_page(viewport=VIEWPORT, locale="en-US")
    try:
        browser.prepare(page)
        resp = page.goto(url, wait_until="load")
        if resp is None or resp.status >= 400:
            raise RuntimeError(f"HTTP {resp.status if resp else 'no response'}")
        axe = browser.run_axe(page)
        contrast = browser.contrast_measurements(page)
        clickable = browser.clickable_not_focusable(page)
        snapshot = browser.aria_snapshot(page)
        crawl = browser.focus_crawl(page)
        focus = browser.analyse_focus(crawl)
        return {"axe": axe, "contrast": contrast, "clickable": clickable, "focus": focus,
                "focus_left_document": crawl["left_document"], "snapshot": snapshot}
    finally:
        page.close()


def page_facts(page_path: str, m: dict[str, Any]) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for bucket, kind in AXE_KIND.items():
        for v in m["axe"][bucket]:
            for n in v["nodes"]:
                selector = " >>> ".join(n["target"]) if isinstance(n["target"], list) else str(n["target"])
                facts.append({
                    "kind": kind, "page": page_path, "selector": selector, "rule": v["id"],
                    "wcag": _wcag_from_tags(v["tags"]), "best_practice": "best-practice" in v["tags"],
                    "impact": n["impact"] or v["impact"], "help": v["help"], "help_url": v["helpUrl"],
                    "html": n["html"][:300], "detail": n["summary"][:500],
                })
    for c in m["contrast"]:
        if c["determinable"] and c["ratio_exact"] >= c["required"]:
            continue
        kind = "contrast_below_minimum" if c["determinable"] else "contrast_indeterminate"
        facts.append({
            "kind": kind, "page": page_path, "selector": c["selector"], "rule": "wcag-1.4.3", "wcag": ["1.4.3"],
            "ratio": c["ratio"], "required": c["required"], "fg": c["fg"], "bg": c["bg"],
            "font_size_px": c["font_size_px"], "bold": c["bold"], "large_text": c["large_text"],
            "text": c["text"], "detail": c["reason"],
        })
    f = m["focus"]
    if f["trap"]:
        facts.append({
            "kind": "focus_trap", "page": page_path, "selector": f["trap"]["cycle"][0] if f["trap"]["cycle"] else "body",
            "rule": "tab-crawl", "wcag": ["2.1.2"], "cycle": f["trap"]["cycle"], "unreachable": f["trap"]["unreachable"],
            "detail": "Repeated Tab presses never left the page; focus cycled between the listed elements.",
        })
    for p in f["positive_tabindex"]:
        facts.append({
            "kind": "positive_tabindex", "page": page_path, "selector": p["selector"], "rule": "tab-crawl",
            "wcag": ["2.4.3"], "tabindex": p["tabindex"], "dom_position": p["dom_position"],
            "focus_position": p["focus_position"],
            "detail": f"tabindex={p['tabindex']}: focus position {p['focus_position']}, DOM position {p['dom_position']}.",
        })
    for sel in f["focus_not_visible"]:
        facts.append({
            "kind": "focus_not_visible", "page": page_path, "selector": sel, "rule": "tab-crawl", "wcag": ["2.4.7"],
            "detail": "Outline, box-shadow, border, background, colour and underline of the element, its parent and next sibling were identical with and without keyboard focus.",
        })
    for c in m["clickable"]:
        facts.append({
            "kind": "clickable_not_focusable", "page": page_path, "selector": c["selector"], "rule": "click-listener",
            "wcag": ["2.1.1"], "listeners": c["listeners"], "html": c["html"],
            "detail": "Has a pointer listener but is not focusable and is not a native control.",
        })
    for c in f.get("focus_not_measured", []):
        facts.append({"kind": "focus_not_measured", "page": page_path, "selector": c["selector"],
                      "rule": "tab-crawl", "wcag": ["2.4.7"], "detail": c["reason"]})
    return facts


def _key(f: dict[str, Any]) -> tuple[str, str, str]:
    return (f["kind"], f["rule"], f["selector"])


def scan(repo: Path, base: str, head: str, out: Path, all_pages: bool = False) -> dict[str, Any]:
    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    base_sha, head_sha = rev_parse(repo, base), rev_parse(repo, head)
    changes = changed_files(repo, base_sha, head_sha, FIXTURE_ROOT)

    pages: list[dict[str, Any]] = []
    facts: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []

    with worktree(repo, base_sha) as base_dir, worktree(repo, head_sha) as head_dir:
        base_root, head_root = base_dir / FIXTURE_ROOT, head_dir / FIXTURE_ROOT
        head_html = sorted(p.relative_to(head_root).as_posix() for p in head_root.rglob("*.html"))
        status = {Path(name).relative_to(FIXTURE_ROOT).as_posix(): st for st, name in changes}
        targets: dict[str, str] = {}
        for rel, st in status.items():
            if rel.endswith(".html"):
                targets[rel] = {"A": "added", "M": "modified", "D": "deleted"}.get(st, "modified")
        if all_pages or any(not r.endswith(".html") for r in status):
            # A shared asset changed (CSS, JS, image), so every page may look different.
            for rel in head_html:
                targets.setdefault(rel, "dependency" if not all_pages else "all_pages")

        with serve(base_root) as base_url, serve(head_root) as head_url, sync_playwright() as pw:
            b = pw.chromium.launch()
            chromium = b.version
            for rel in sorted(targets):
                change = targets[rel]
                entry = {"page": rel, "change": change, "scanned": False, "reason": None}
                if change == "deleted":
                    entry["reason"] = "Page deleted in head."
                    pages.append(entry)
                    continue
                try:
                    head_m = measure_page(b, head_url + rel)
                except Exception as exc:  # noqa: BLE001 - reported, never swallowed
                    entry["reason"] = f"Head page failed to load or measure: {exc}"
                    print(f"not scanned {rel}: {exc}", file=sys.stderr)
                    pages.append(entry)
                    continue
                base_keys: set[tuple[str, str, str]] = set()
                if (base_root / rel).exists():
                    try:
                        base_m = measure_page(b, base_url + rel)
                        base_keys = {_key(f) for f in page_facts(rel, base_m)}
                        snapshots.append({"page": rel, "side": "base", "aria_snapshot": base_m["snapshot"]})
                    except Exception as exc:  # noqa: BLE001
                        entry["base_reason"] = f"Base page failed: {exc}"
                        print(f"base not measured {rel}: {exc}", file=sys.stderr)
                snapshots.append({"page": rel, "side": "head", "aria_snapshot": head_m["snapshot"]})
                for f in page_facts(rel, head_m):
                    f["introduced"] = _key(f) not in base_keys
                    f["fact_id"] = fact_id(f["kind"], rel, f["rule"], f["selector"])
                    facts.append(f)
                entry["scanned"] = True
                entry["focus_sequence"] = head_m["focus"]["sequence"]
                pages.append(entry)
            b.close()

    facts.sort(key=lambda f: (f["page"], f["kind"], f["rule"], f["selector"]))
    ids = [f["fact_id"] for f in facts]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate fact_id; the selector scheme is not unique enough.")
    by_kind: dict[str, int] = {}
    for f in facts:
        by_kind[f["kind"]] = by_kind.get(f["kind"], 0) + 1
    body = {"pages": pages, "facts": facts, "snapshots": snapshots}
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    result = {
        "schema_version": "1.0",
        "tool": {"name": "curbcut", "version": __version__, "axe_core": AXE_CORE_VERSION,
                 "chromium": chromium, "viewport": VIEWPORT},
        "base": {"ref": base, "sha": base_sha},
        "head": {"ref": head, "sha": head_sha},
        "fixture_root": FIXTURE_ROOT,
        "summary": {
            "pages_total": len(pages), "pages_scanned": sum(1 for p in pages if p["scanned"]),
            "pages_not_scanned": sum(1 for p in pages if not p["scanned"]),
            "facts_total": len(facts), "facts_introduced": sum(1 for f in facts if f["introduced"]),
            "by_kind": dict(sorted(by_kind.items())),
        },
        "digest": digest,
        **body,
        "run": {"started_at": started_at, "duration_s": round(time.perf_counter() - started, 2)},
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return result
