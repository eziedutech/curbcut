import json
from pathlib import Path

from curbcut.validate import validate

FACTS = {"facts": [{"fact_id": "axe-12345678"}]}


def finding(**kw):
    base = {"id": "F001", "tier": "proven", "sc": "4.1.2", "title": "No name", "principle": "robust",
            "severity": "critical", "page": "p.html", "selector": "#b", "fact_ids": ["axe-12345678"],
            "reason": "axe button-name failed.", "who_is_affected": "Screen reader users.",
            "how_to_fix": "Add an accessible name.", "fixable": True, "source": "engine"}
    base.update(kw)
    return base


def write(tmp: Path, findings, summary=None):
    (tmp / "facts.json").write_text(json.dumps(FACTS))
    data = {"schema_version": "1.0", "pr_id": "t", "base": "main", "head": "h", "facts_file": "facts.json",
            "summary": summary or {"proven": 1, "flagged": 0, "out_of_reach": 0, "not_scanned": 0},
            "findings": findings, "out_of_reach": [], "not_scanned": []}
    path = tmp / "findings.json"
    path.write_text(json.dumps(data))
    return path


def test_valid_file(tmp_path):
    assert validate(write(tmp_path, [finding()]), tmp_path) == []


def test_every_problem_listed_in_one_pass(tmp_path):
    errors = validate(write(tmp_path, [finding(fact_ids=["axe-00000000"], principle="operable")],
                            summary={"proven": 2, "flagged": 0, "out_of_reach": 0, "not_scanned": 0}), tmp_path)
    text = "\n".join(errors)
    assert "does not exist" in text and "belongs to robust" in text and "summary.proven is 2" in text


def test_proven_needs_fact(tmp_path):
    assert any("non-empty" in e for e in validate(write(tmp_path, [finding(fact_ids=[])]), tmp_path))


def test_flagged_without_fact_is_fine(tmp_path):
    f = finding(tier="flagged", fact_ids=[], source="subagent:robust")
    assert validate(write(tmp_path, [f], {"proven": 0, "flagged": 1, "out_of_reach": 0, "not_scanned": 0}), tmp_path) == []
