"""`curbcut report` and `curbcut publish`: one report.json per review, sent to backpy.

The report is assembled from files already on disk (facts, findings, fixes,
verify). Nothing is re-judged here. The screen reader narration is derived from
the accessibility tree snapshot line by line, with no model involved.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .gitutil import git

# Roles a screen reader user meets while moving through a form or a lesson page.
NARRATED_ROLES = {
    "button", "link", "textbox", "checkbox", "radio", "combobox", "img", "heading",
    "iframe", "table", "list", "slider", "switch", "tab", "searchbox", "spinbutton", "video", "audio",
}
_LINE = re.compile(r'^\s*-\s+(?P<role>[a-z]+)(?:\s+"(?P<name>(?:[^"\\]|\\.)*)")?(?P<rest>[^:]*)')
_EMPTY_NAME = {"img": "no description", "iframe": "untitled frame"}
_NAME_REQUIRED = {"button", "link", "textbox", "checkbox", "radio", "combobox", "slider", "switch", "tab",
                  "searchbox", "spinbutton"}


def narrate(snapshot: str) -> list[str]:
    """Turn a Playwright aria snapshot into the lines a screen reader would roughly announce."""
    lines = []
    for raw in snapshot.splitlines():
        m = _LINE.match(raw)
        if not m or m.group("role") not in NARRATED_ROLES:
            continue
        role, name = m.group("role"), (m.group("name") or "").replace('\\"', '"')
        states = " ".join(s.strip("[]") for s in re.findall(r"\[[^\]]+\]", m.group("rest") or ""))
        if name:
            text = f"{role}, {name}"
        elif role in _NAME_REQUIRED or role in _EMPTY_NAME:
            text = f"{role}, {_EMPTY_NAME.get(role, 'unlabeled')}"
        else:
            text = role
        # Lists, tables and headings do not need a name, so their absence is not announced as a gap.
        if states:
            text += f", {states.replace('=', ' ')}"
        lines.append(text)
    return lines


def _load(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_slug(repo: Path) -> str:
    try:
        url = git(repo, "remote", "get-url", "origin").strip()
    except RuntimeError:
        return "local/unknown"
    m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
    return m.group(1) if m else url


def build_report(repo: Path, report_id: str, report_dir: Path, after_dir: Path | None, out: Path) -> dict[str, Any]:
    findings = _load(report_dir / "findings.json")
    if findings is None:
        raise RuntimeError(f"{report_dir / 'findings.json'} is missing; run the review first.")
    facts = _load(repo / findings["facts_file"]) or _load(report_dir / "facts.json")
    if facts is None:
        raise RuntimeError("facts.json is missing.")
    snapshots = _load(report_dir / "snapshots.json") or {"snapshots": []}
    fixes = _load(report_dir / "fixes.json")
    verify = _load(report_dir / "verify.json")

    after = None
    if after_dir is not None:
        after_facts = _load(after_dir / "facts.json")
        after_snaps = _load(after_dir / "snapshots.json") or {"snapshots": []}
        if after_facts is not None:
            after = {"head": after_facts["head"], "summary": after_facts["summary"],
                     "remaining_facts": [{k: f[k] for k in ("fact_id", "kind", "page", "rule", "selector")}
                                         for f in after_facts["facts"]],
                     "snapshots": after_snaps["snapshots"]}

    pages_with_findings = sorted({f["page"] for f in findings["findings"]})
    narration = []
    for page in pages_with_findings:
        before = next((s for s in snapshots["snapshots"] if s["page"] == page and s["side"] == "head"), None)
        fixed = next((s for s in (after or {}).get("snapshots", []) if s["page"] == page and s["side"] == "head"), None)
        narration.append({
            "page": page,
            "before": narrate(before["aria_snapshot"]) if before else None,
            "after": narrate(fixed["aria_snapshot"]) if fixed else None,
        })

    report = {
        "schema_version": "1.0",
        "id": report_id,
        "repo": _repo_slug(repo),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "engine": facts["tool"] | {"curbcut": __version__},
        "pr": {"base": facts["base"]["ref"], "head": facts["head"]["ref"],
               "base_sha": facts["base"]["sha"], "head_sha": facts["head"]["sha"]},
        "facts": {"summary": facts["summary"], "digest": facts["digest"], "pages": facts["pages"],
                  "facts": facts["facts"], "duration_s": facts["run"]["duration_s"]},
        "review": {k: findings[k] for k in ("summary", "findings", "out_of_reach", "not_scanned")},
        "fixes": fixes,
        "verify": verify and {k: verify[k] for k in ("base", "head", "rule", "summary", "results",
                                                      "test_files_not_collected", "fixes_without_test", "run")},
        "after": after and {k: after[k] for k in ("head", "summary", "remaining_facts")},
        "narration": narration,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return report


def publish(report_path: Path, url: str, token: str) -> dict[str, Any]:
    data = report_path.read_bytes()
    req = urllib.request.Request(url.rstrip("/") + "/api/reports/ingest", data=data, method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"ingest answered {exc.code}: {exc.read().decode('utf-8', 'replace')[:300]}") from exc
