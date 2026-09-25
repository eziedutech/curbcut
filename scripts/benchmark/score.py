"""Score CurbCut against the planted ground truth.

    uv run --project codes/engine python scripts/benchmark/score.py pr-1 [pr-1-run2 ...]

A finding counts for a planted issue when it names an accepted success criterion
and its selector resolves to at least one of the same DOM elements on the head
page. Selectors are resolved in a real browser, so "#signup-form > div > p" and
".hint" match when they point at the same element.

Three columns are compared on the same pages:
  axe-core only   axe violations from facts.json
  engine          every fact from facts.json (axe plus contrast, Tab crawl, listeners)
  CurbCut         findings.json from the IBM Bob review

Findings that match no planted issue are listed for a human to judge. They are
not automatically called false positives: some are real issues nobody planted.
A decoy is hit when a finding points at a decoy element with the criterion the
decoy imitates.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright

from curbcut import FIXTURE_ROOT
from curbcut.gitutil import rev_parse, worktree
from curbcut.server import serve

REPO = Path(__file__).resolve().parents[2]
GT = json.loads((Path(__file__).with_name("ground-truth.json")).read_text(encoding="utf-8"))

_TAG = r"""
([sels]) => {
  const all = Array.from(document.querySelectorAll('*'));
  const index = el => all.indexOf(el);
  return sels.map(sel => {
    try { return Array.from(document.querySelectorAll(sel)).map(index); }
    catch (e) { return null; }
  });
}
"""


def resolve(page_url: str, selectors: list[str], browser) -> list[set[int] | None]:
    page = browser.new_page()
    try:
        page.goto(page_url, wait_until="load")
        raw = page.evaluate(_TAG, [selectors])
    finally:
        page.close()
    return [set(r) if r is not None else None for r in raw]


def items_from_facts(facts: dict[str, Any], axe_only: bool) -> list[dict[str, Any]]:
    out = []
    for f in facts["facts"]:
        if axe_only and f["kind"] != "axe_violation":
            continue
        if f["kind"] in ("axe_needs_review", "focus_not_measured", "contrast_indeterminate"):
            continue
        selectors = [f["selector"]] + (f.get("cycle") or [])
        out.append({"id": f["fact_id"], "scs": f["wcag"], "page": f["page"], "selectors": selectors,
                    "label": f"{f['kind']}:{f['rule']}"})
    return out


def items_from_findings(findings: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"id": f["id"], "scs": [f["sc"]], "page": f["page"], "selectors": [f["selector"]],
             "label": f"{f['tier']}:{f['title']}", "tier": f["tier"]} for f in findings["findings"]]


def score(pr: dict[str, Any], items: list[dict[str, Any]], head_url: str, browser) -> dict[str, Any]:
    pages = sorted({i["page"] for i in pr["issues"]} | {d["page"] for d in pr["decoys"]} | {i["page"] for i in items})
    resolved: dict[tuple[str, str], set[int] | None] = {}
    for page in pages:
        sels = sorted({s for i in items if i["page"] == page for s in i["selectors"]}
                      | {g["selector"] for g in pr["issues"] + pr["decoys"] if g["page"] == page})
        for sel, els in zip(sels, resolve(head_url + page, sels, browser)):
            resolved[(page, sel)] = els

    def elements(page: str, selectors: list[str]) -> set[int]:
        out: set[int] = set()
        for s in selectors:
            out |= resolved.get((page, s)) or set()
        return out

    matched_items: set[str] = set()
    per_issue = []
    for g in pr["issues"]:
        accept = {g["sc"], *g["also_accept_sc"]}
        g_els = elements(g["page"], [g["selector"]])
        hits = [i["id"] for i in items if i["page"] == g["page"] and accept & set(i["scs"])
                and g_els & elements(i["page"], i["selectors"])]
        matched_items.update(hits)
        per_issue.append({"gt_id": g["gt_id"], "sc": g["sc"], "principle": g["principle"],
                          "engine_signal": g["engine_signal"], "found": bool(hits), "by": hits})
    decoy_hits = []
    for d in pr["decoys"]:
        d_els = elements(d["page"], [d["selector"]])
        hits = [i["id"] for i in items if i["page"] == d["page"] and d["looks_like_sc"] in i["scs"]
                and d_els & elements(i["page"], i["selectors"]) and i["id"] not in matched_items]
        if hits:
            decoy_hits.append({"gt_id": d["gt_id"], "by": hits})
    unmatched = [{"id": i["id"], "scs": i["scs"], "label": i["label"]} for i in items if i["id"] not in matched_items]
    by_principle = {}
    for p in ("perceivable", "operable", "understandable", "robust"):
        rows = [r for r in per_issue if r["principle"] == p]
        by_principle[p] = {"found": sum(r["found"] for r in rows), "planted": len(rows)}
    return {
        "found": sum(r["found"] for r in per_issue), "planted": len(per_issue),
        "judgment_only_found": sum(r["found"] for r in per_issue if not r["engine_signal"]),
        "judgment_only_planted": sum(1 for r in per_issue if not r["engine_signal"]),
        "decoys_hit": len(decoy_hits), "decoys": len(pr["decoys"]),
        "items": len(items), "unmatched": unmatched, "decoy_hits": decoy_hits,
        "by_principle": by_principle, "per_issue": per_issue,
    }


def main(run_ids: list[str]) -> None:
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for run_id in run_ids:
            pr_id = run_id.split("-run")[0]
            pr = next(p for p in GT["prs"] if p["id"] == pr_id)
            run_dir = REPO / "reports" / "curbcut" / run_id
            facts = json.loads((run_dir / "facts.json").read_text(encoding="utf-8"))
            findings = json.loads((run_dir / "findings.json").read_text(encoding="utf-8"))
            head_sha = rev_parse(REPO, facts["head"]["sha"])
            with worktree(REPO, head_sha) as wt, serve(wt / FIXTURE_ROOT) as url:
                row = {
                    "run": run_id, "pr": pr_id, "head_sha": head_sha,
                    "axe_only": score(pr, items_from_facts(facts, axe_only=True), url, browser),
                    "engine": score(pr, items_from_facts(facts, axe_only=False), url, browser),
                    "curbcut": score(pr, items_from_findings(findings), url, browser),
                    "scan_seconds": facts["run"]["duration_s"],
                }
            verify_path = run_dir / "verify.json"
            if verify_path.exists():
                row["verify"] = json.loads(verify_path.read_text(encoding="utf-8"))["summary"]
            results.append(row)
            print(f"\n{run_id}  (planted {row['curbcut']['planted']}, decoys {row['curbcut']['decoys']})")
            for col in ("axe_only", "engine", "curbcut"):
                c = row[col]
                print(f"  {col:<9} found {c['found']:>2}/{c['planted']}  judgment-only {c['judgment_only_found']}/{c['judgment_only_planted']}"
                      f"  decoys hit {c['decoys_hit']}  unmatched {len(c['unmatched'])} of {c['items']}")
            missed = [r["gt_id"] for r in row["curbcut"]["per_issue"] if not r["found"]]
            print(f"  CurbCut missed: {missed}")
            for u in row["curbcut"]["unmatched"]:
                print(f"  unmatched {u['id']} {u['scs']} {u['label'][:70]}")
        browser.close()
    out = Path(__file__).with_name("results.json")
    out.write_text(json.dumps({"schema_version": "1.0", "runs": results}, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"\n-> {out.relative_to(REPO).as_posix()}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["pr-1"])
