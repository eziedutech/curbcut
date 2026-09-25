"""`curbcut verify`: a fix is verified only if its test fails on base and passes on head.

The tests come from the current working copy. Each ref's fixture is checked out
into its own worktree and served separately, and the same test files run against
both. The runner decides, not a model.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import FIXTURE_ROOT
from .gitutil import rev_parse, worktree
from .server import serve

VERDICTS = ("verified", "not_proving", "still_failing", "error")


def _outcomes(junit: Path) -> dict[str, dict[str, str]]:
    results: dict[str, dict[str, str]] = {}
    if not junit.exists():
        return results
    for case in ET.parse(junit).getroot().iter("testcase"):
        file = Path(case.get("file") or case.get("classname", "").replace(".", "/") + ".py").name
        name = f"{file}::{case.get('name', '')}"
        outcome, message = "passed", ""
        for tag in ("failure", "error", "skipped"):
            el = case.find(tag)
            if el is not None:
                outcome = {"failure": "failed", "error": "error", "skipped": "skipped"}[tag]
                message = (el.get("message") or el.text or "").strip().splitlines()[0][:300] if (el.get("message") or el.text) else ""
                break
        results[name] = {"outcome": outcome, "message": message}
    return results


def _run_pytest(repo: Path, files: list[Path], base_url: str, label: str) -> tuple[dict[str, dict[str, str]], str]:
    junit = Path(tempfile.mkdtemp(prefix="curbcut-junit-")) / f"{label}.xml"
    cmd = [sys.executable, "-m", "pytest", *[str(f) for f in files], "--base-url", base_url,
           "--browser", "chromium", "-p", "no:cacheprovider", "-q", f"--junitxml={junit}",
           "-o", "junit_family=xunit1"]
    env = {**os.environ, "CURBCUT_BASE_URL": base_url}
    res = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, encoding="utf-8", env=env)
    return _outcomes(junit), (res.stdout + res.stderr)[-4000:]


def _verdict(base: str | None, head: str | None) -> str:
    if base is None or head is None or "error" in (base, head) or "skipped" in (base, head):
        return "error"
    if base == "failed" and head == "passed":
        return "verified"
    if base == "passed":
        return "not_proving"
    return "still_failing"


def verify(repo: Path, report_id: str, base: str, head: str, tests_dir: Path, out: Path) -> dict[str, Any]:
    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    prefix = "test_" + re.sub(r"[^a-z0-9]", "", report_id.split("-run")[0].lower()) + "_"
    files = sorted(p for p in tests_dir.glob(f"{prefix}*.py"))
    base_sha, head_sha = rev_parse(repo, base), rev_parse(repo, head)

    logs: dict[str, str] = {}
    with worktree(repo, base_sha) as bdir, worktree(repo, head_sha) as hdir:
        with serve(bdir / FIXTURE_ROOT) as base_url, serve(hdir / FIXTURE_ROOT) as head_url:
            base_res, logs["base"] = _run_pytest(repo, files, base_url, "base") if files else ({}, "")
            head_res, logs["head"] = _run_pytest(repo, files, head_url, "head") if files else ({}, "")

    results = []
    for name in sorted(set(base_res) | set(head_res)):
        b, h = base_res.get(name), head_res.get(name)
        stem = Path(name.split("::")[0]).stem
        finding_id = stem[len(prefix):] if stem.startswith(prefix) else None
        results.append({
            "test": name, "finding_id": finding_id.upper() if finding_id else None,
            "base": b["outcome"] if b else None, "head": h["outcome"] if h else None,
            "base_message": b["message"] if b else "", "head_message": h["message"] if h else "",
            "verdict": _verdict(b["outcome"] if b else None, h["outcome"] if h else None),
        })

    collected = {Path(r["test"].split("::")[0]).stem for r in results}
    not_collected = [p.name for p in files if p.stem not in collected]

    fixes_path = repo / "reports" / "curbcut" / report_id / "fixes.json"
    untested: list[str] = []
    if fixes_path.exists():
        try:
            fixes = json.loads(fixes_path.read_text(encoding="utf-8"))
            entries = fixes.get("fixes", fixes) if isinstance(fixes, dict) else fixes
            tested = {r["finding_id"] for r in results if r["finding_id"]}
            for e in entries if isinstance(entries, list) else []:
                fid = str(e.get("finding_id", "")).upper()
                if fid and fid not in tested:
                    untested.append(fid)
        except (json.JSONDecodeError, AttributeError) as exc:
            untested.append(f"fixes.json unreadable: {exc}")

    summary = {v: sum(1 for r in results if r["verdict"] == v) for v in VERDICTS}
    summary["total"] = len(results)
    result = {
        "schema_version": "1.0",
        "id": report_id,
        "base": {"ref": base, "sha": base_sha},
        "head": {"ref": head, "sha": head_sha},
        "tests_dir": tests_dir.relative_to(repo).as_posix() if tests_dir.is_relative_to(repo) else str(tests_dir),
        "rule": "verified means the test failed on base and passed on head. Nothing else counts.",
        "summary": summary,
        "results": results,
        "test_files_not_collected": not_collected,
        "fixes_without_test": sorted(set(untested)),
        "log_tail": logs,
        "run": {"started_at": started_at, "duration_s": round(time.perf_counter() - started, 2)},
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return result
