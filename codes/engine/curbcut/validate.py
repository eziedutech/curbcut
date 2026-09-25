"""`curbcut validate`: schema check plus the rules a schema cannot express."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "findings.schema.json"
PRINCIPLE_BY_DIGIT = {"1": "perceivable", "2": "operable", "3": "understandable", "4": "robust"}
EM_DASH = "\u2014"


def _path(parts: Any) -> str:
    out = "$"
    for p in parts:
        out += f"[{p}]" if isinstance(p, int) else f".{p}"
    return out


def validate(findings_path: Path, repo: Path, facts_path: Path | None = None) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(findings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read {findings_path}: {exc}"]

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    for e in sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: [str(x) for x in e.absolute_path]):
        errors.append(f"schema {_path(e.absolute_path)}: {e.message}")
    # Keep going: one pass should list every problem, so a fix round is not wasted.
    if not isinstance(data, dict) or not isinstance(data.get("findings"), list):
        return errors
    findings = [f for f in data["findings"] if isinstance(f, dict)]

    known: set[str] | None = None
    if facts_path is None and isinstance(data.get("facts_file"), str):
        facts_path = repo / data["facts_file"]
    if facts_path is not None:
        try:
            facts = json.loads(facts_path.read_text(encoding="utf-8"))
            known = {f["fact_id"] for f in facts["facts"]}
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            errors.append(f"cannot read facts file {facts_path}: {exc}")

    ids = [f.get("id") for f in findings]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        errors.append(f"duplicate finding id {dup}")

    for i, f in enumerate(findings):
        where = f"$.findings[{i}] ({f.get('id')})"
        if known is not None and isinstance(f.get("fact_ids"), list):
            for fid in f["fact_ids"]:
                if fid not in known:
                    errors.append(f"{where}: fact_id {fid} does not exist in {facts_path.name}")
        sc = f.get("sc")
        if isinstance(sc, str) and sc[:1] in PRINCIPLE_BY_DIGIT and PRINCIPLE_BY_DIGIT[sc[0]] != f.get("principle"):
            errors.append(f"{where}: sc {sc} belongs to {PRINCIPLE_BY_DIGIT[sc[0]]}, not {f.get('principle')}")

    seen: dict[tuple[str, str, str], str] = {}
    for f in findings:
        key = (f.get("sc"), f.get("page"), f.get("selector"))
        if key in seen:
            errors.append(f"{f['id']} duplicates {seen[key]} (same sc, page and selector)")
        seen[key] = f["id"]

    s = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    actual = {
        "proven": sum(1 for f in findings if f.get("tier") == "proven"),
        "flagged": sum(1 for f in findings if f.get("tier") == "flagged"),
        "out_of_reach": len(data.get("out_of_reach") or []),
        "not_scanned": len(data.get("not_scanned") or []),
    }
    for k, v in actual.items():
        if k in s and s[k] != v:
            errors.append(f"summary.{k} is {s[k]} but the list has {v}")

    if EM_DASH in findings_path.read_text(encoding="utf-8"):
        errors.append("em dash found; use a comma, colon or full stop")
    return errors
