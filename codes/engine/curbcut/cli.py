"""Command line entry point: curbcut scan | validate | verify | sarif."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .gitutil import repo_root


def _repo() -> Path:
    return repo_root(Path.cwd())


def _abs(repo: Path, p: str) -> Path:
    path = Path(p)
    return path if path.is_absolute() else (Path.cwd() / path).resolve()


def cmd_scan(a: argparse.Namespace) -> int:
    from .scan import scan
    repo = _repo()
    r = scan(repo, a.base, a.head, _abs(repo, a.out), all_pages=a.all_pages)
    s = r["summary"]
    print(f"scanned {s['pages_scanned']}/{s['pages_total']} pages, {s['facts_total']} facts "
          f"({s['facts_introduced']} introduced by head) -> {a.out}")
    print("by kind: " + ", ".join(f"{k}={v}" for k, v in s["by_kind"].items()))
    for p in r["pages"]:
        if not p["scanned"]:
            print(f"NOT SCANNED {p['page']}: {p['reason']}")
    print(f"digest {r['digest']}  ({r['run']['duration_s']} s)")
    return 1 if s["pages_not_scanned"] else 0


def cmd_validate(a: argparse.Namespace) -> int:
    from .validate import validate
    repo = _repo()
    path = _abs(repo, a.findings)
    errors = validate(path, repo, _abs(repo, a.facts) if a.facts else None)
    if errors:
        print(f"INVALID {a.findings}: {len(errors)} error(s)")
        for e in errors:
            print(f"- {e}")
        return 1
    s = json.loads(path.read_text(encoding="utf-8"))["summary"]
    print(f"OK {a.findings}: proven {s['proven']}, flagged {s['flagged']}, "
          f"out of reach {s['out_of_reach']}, not scanned {s['not_scanned']}")
    return 0


def cmd_verify(a: argparse.Namespace) -> int:
    from .verify import verify
    repo = _repo()
    r = verify(repo, a.id, a.base, a.head, _abs(repo, a.tests), _abs(repo, a.out))
    s = r["summary"]
    print(f"{s['total']} test(s): verified {s['verified']}, not proving {s['not_proving']}, "
          f"still failing {s['still_failing']}, error {s['error']} -> {a.out}")
    for row in r["results"]:
        print(f"  {row['verdict']:<14} base={row['base']} head={row['head']}  {row['test']}")
    for name in r["test_files_not_collected"]:
        print(f"  NOT COLLECTED  {name}")
    for fid in r["fixes_without_test"]:
        print(f"  NO TEST        {fid}")
    return 0 if s["total"] and s["error"] == 0 else 1


def cmd_sarif(a: argparse.Namespace) -> int:
    from .sarif import to_sarif
    repo = _repo()
    out = a.out or str(Path(a.findings).with_name("findings.sarif"))
    sarif = to_sarif(_abs(repo, a.findings), repo, _abs(repo, out))
    print(f"SARIF 2.1.0 with {len(sarif['runs'][0]['results'])} result(s) -> {out}")
    return 0


def cmd_report(a: argparse.Namespace) -> int:
    from .report import build_report
    repo = _repo()
    report_dir = _abs(repo, a.dir or f"reports/curbcut/{a.id}")
    out = _abs(repo, a.out) if a.out else report_dir / "report.json"
    r = build_report(repo, a.id, report_dir, _abs(repo, a.after) if a.after else None, out)
    s = r["review"]["summary"]
    v = r["verify"]["summary"]["verified"] if r["verify"] else "no verify.json"
    print(f"report {a.id}: proven {s['proven']}, flagged {s['flagged']}, out of reach {s['out_of_reach']}, "
          f"not scanned {s['not_scanned']}, verified fixes {v} -> {out}")
    return 0


def cmd_publish(a: argparse.Namespace) -> int:
    import os
    from .report import publish
    repo = _repo()
    token = os.environ.get("CURBCUT_INGEST_TOKEN", "")
    if not token:
        print("error: CURBCUT_INGEST_TOKEN is not set", file=sys.stderr)
        return 2
    res = publish(_abs(repo, a.report), a.url, token)
    print(f"published {res['id']} at {res['head_sha'][:7]} to {a.url}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="curbcut", description="CurbCut deterministic accessibility engine.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("scan", help="Measure changed fixture pages on base and head; write facts.json.")
    p.add_argument("--base", required=True)
    p.add_argument("--head", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--all-pages", action="store_true", help="Scan every page, not only changed ones.")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("validate", help="Check findings.json against the schema and the facts it cites.")
    p.add_argument("findings")
    p.add_argument("--facts", help="Override the facts file named in findings.json.")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("verify", help="Run tests on base (must fail) and head (must pass); write verify.json.")
    p.add_argument("--id", required=True, help="Report id, for example pr-1. Selects tests named test_pr1_*.py.")
    p.add_argument("--base", required=True)
    p.add_argument("--head", required=True)
    p.add_argument("--tests", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("sarif", help="Export findings.json as SARIF 2.1.0.")
    p.add_argument("findings")
    p.add_argument("--out")
    p.set_defaults(func=cmd_sarif)

    p = sub.add_parser("report", help="Assemble report.json from facts, findings, fixes and verify.")
    p.add_argument("--id", required=True)
    p.add_argument("--dir", help="Folder with findings.json and friends. Default reports/curbcut/<id>.")
    p.add_argument("--after", help="Folder with a scan of the fixed branch, for before and after narration.")
    p.add_argument("--out")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("publish", help="POST report.json to the dashboard. Token from CURBCUT_INGEST_TOKEN.")
    p.add_argument("report")
    p.add_argument("--url", required=True, help="Dashboard base URL, for example https://curbcut.eziedutech.dev")
    p.set_defaults(func=cmd_publish)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
