"""`curbcut sarif`: findings.json to SARIF 2.1.0 for GitHub code scanning."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from . import FIXTURE_ROOT, __version__
from .gitutil import git

SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"


def _level(f: dict[str, Any]) -> str:
    if f["tier"] == "proven":
        return "error" if f["severity"] in ("critical", "serious") else "warning"
    return "note"


def _locate(repo: Path, ref: str, file_rel: str, selector: str) -> int | None:
    """Best effort: the line of the first id or class the selector names, in the head ref."""
    try:
        lines = git(repo, "show", f"{ref}:{file_rel}").splitlines()
    except RuntimeError:
        return None
    needles = []
    for m in re.finditer(r"#([A-Za-z][\w-]*)", selector):
        needles.append(f'id="{m.group(1)}"')
    for m in re.finditer(r"\.([A-Za-z][\w-]*)", selector):
        needles.append(m.group(1))
    for m in re.finditer(r'\[(?:src|href)\$?="([^"]+)"\]', selector):
        needles.append(m.group(1))
    tag = re.match(r"^([a-z]+)", selector)
    if tag:
        needles.append(f"<{tag.group(1)}")
    for needle in needles:
        for i, line in enumerate(lines, start=1):
            if needle in line:
                return i
    return None


def to_sarif(findings_path: Path, repo: Path, out: Path) -> dict[str, Any]:
    data = json.loads(findings_path.read_text(encoding="utf-8"))
    rules: dict[str, dict[str, Any]] = {}
    results = []
    for f in data["findings"]:
        rule_id = f"WCAG-{f['sc']}"
        rules.setdefault(rule_id, {
            "id": rule_id,
            "name": f"WCAG22_{f['sc'].replace('.', '_')}",
            "shortDescription": {"text": f"WCAG 2.2 success criterion {f['sc']}"},
            "helpUri": f.get("understanding_url") or "https://www.w3.org/WAI/WCAG22/Understanding/",
            "properties": {"principle": f["principle"]},
        })
        file_rel = f.get("file") or f"{FIXTURE_ROOT}/{f['page']}"
        line = f.get("line") or _locate(repo, data["head"], file_rel, f["selector"])
        location: dict[str, Any] = {"physicalLocation": {"artifactLocation": {"uri": file_rel}}}
        if line:
            location["physicalLocation"]["region"] = {"startLine": line}
        tier_label = "Proven" if f["tier"] == "proven" else "Flagged (reviewer judgment, may be wrong)"
        results.append({
            "ruleId": rule_id,
            "level": _level(f),
            "message": {"text": f"[{tier_label}] {f['title']}. Who is affected: {f['who_is_affected']} Fix: {f['how_to_fix']}"},
            "locations": [location],
            "partialFingerprints": {"curbcut/v1": f"{f['sc']}|{f['page']}|{f['selector']}"},
            "properties": {"tier": f["tier"], "severity": f["severity"], "selector": f["selector"],
                           "fact_ids": f["fact_ids"], "finding_id": f["id"], "source": f["source"]},
        })
    sarif = {
        "$schema": SARIF_SCHEMA,
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {"name": "CurbCut", "version": __version__,
                                "informationUri": "https://github.com/eziedutech/curbcut",
                                "rules": sorted(rules.values(), key=lambda r: r["id"])}},
            "results": results,
            "properties": {"pr_id": data["pr_id"], "out_of_reach": data["out_of_reach"],
                           "not_scanned": data["not_scanned"]},
        }],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sarif, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return sarif
