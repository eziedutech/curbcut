# CurbCut engine

The deterministic half of CurbCut. It measures; IBM Bob interprets. A finding can only be
called proven if it cites a `fact_id` produced here.

Python 3.14, uv, Playwright 1.63 (Chromium), axe-core 4.13.0 (vendored in `curbcut/vendor`,
MPL-2.0, integrity checked against the npm registry). All versions are pinned exactly.

```bash
cd codes/engine && uv sync && uv run playwright install chromium
```

## Commands

Run from the repository root.

| Command | Does |
|---|---|
| `uv run --project codes/engine curbcut scan --base main --head <branch> --out reports/curbcut/<id>/facts.json` | Checks out base and head in temporary git worktrees, serves each fixture, and measures every changed page: axe-core (WCAG 2.2 A and AA tags plus best practices, with `target-size` switched on), text contrast by the WCAG formula, a Tab crawl for traps, positive tabindex and missing focus indicators, pointer listeners on elements a keyboard cannot reach, and the accessibility tree snapshot. Each fact says whether head introduced it. |
| `uv run --project codes/engine curbcut validate reports/curbcut/<id>/findings.json` | Checks the schema in `schema/findings.schema.json` and what a schema cannot: every cited `fact_id` exists, principle matches the success criterion, no duplicates, summary counts equal list lengths, no em dashes. Lists every problem in one pass. |
| `uv run --project codes/engine curbcut verify --id <id> --base <branch> --head <branch> --tests tests/a11y --out reports/curbcut/<id>/verify.json` | Runs `tests/a11y/test_<id>_*.py` against the base fixture and the head fixture. Verified means failed on base and passed on head, nothing else. |
| `uv run --project codes/engine curbcut sarif reports/curbcut/<id>/findings.json` | Exports SARIF 2.1.0 for GitHub code scanning, with line numbers read from the head ref. |

`curbcut.testkit` holds the helpers regression tests use, so a test and the scan share one implementation.

## What the engine does not do

- It does not judge meaning: whether alt text is useful, whether a link text is clear, whether captions are accurate.
- Contrast over background images or with opacity is reported as indeterminate, never guessed.
- Focus indicators drawn inside an iframe are reported as not measured.
- Repeating timers (`setInterval`) are held during a scan so two scans see the same page. Content that only appears after a timer fires is not measured.

## Self-tests

```bash
cd codes/engine && uv run pytest tests
```
