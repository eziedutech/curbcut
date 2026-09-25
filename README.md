# CurbCut

> Accessibility review for pull requests, built on IBM Bob: it checks UI changes against WCAG 2.2, separates measured facts from judgment, fixes what it finds, and proves every fix with a test that fails before and passes after.

![IBM Bob 2.0](https://img.shields.io/badge/IBM%20Bob-2.0-0F62FE)
![WCAG 2.2 A and AA](https://img.shields.io/badge/WCAG-2.2%20A%20%2B%20AA-6f42c1)
![Python 3.14](https://img.shields.io/badge/Python-3.14-3776AB)
![axe-core 4.13](https://img.shields.io/badge/axe--core-4.13-663399)
![React Router 8.4](https://img.shields.io/badge/React%20Router-8.4-CA4245)

Built for the **IBM Bob 2.0 Hackathon** (lablab.ai, September 2026).

Live demo: [curbcut.eziedutech.dev](https://curbcut.eziedutech.dev). IBM Bob task session summaries: [`bob_sessions/`](bob_sessions).

## Table of Contents

- [What it is](#what-it-is)
- [Who it is for](#who-it-is-for)
- [How IBM Bob is used](#how-ibm-bob-is-used)
- [How to test](#how-to-test)
- [Architecture](#architecture)
- [Running locally](#running-locally)
- [Configuration](#configuration)
- [Results](#results)
- [What it does not claim](#what-it-does-not-claim)
- [Roadmap](#roadmap)
- [Credits and licenses](#credits-and-licenses)
- [How this was built](#how-this-was-built)
- [License](#license)

## What it is

Accessibility issues pass code review because most reviewers are not WCAG experts, and linters only catch what a rule can match. CurbCut puts an accessibility reviewer into the pull request.

Every finding carries one of three evidence tiers:

| Tier | Meaning |
|---|---|
| **Proven** | Measured by the deterministic engine and cites a `fact_id` |
| **Flagged** | IBM Bob's judgment, with a one-sentence reason |
| **Out of reach** | Cannot be checked this way; always listed |

A fix is **verified** only when its test fails on the pull request and passes on the fixed branch.

## Who it is for

Teams building education, public service and non-profit products, where an inaccessible form or lesson means a student or citizen is left out.

## How IBM Bob is used

Everything that reviews, fixes and proves is IBM Bob, configured in [`.bob/`](.bob):

1. **Skill `wcag-audit`**: Bob read the WCAG 2.2 Recommendation and wrote the skill and a policy pack of all 55 Level A and AA criteria ([`.bob/skills/wcag-audit`](.bob/skills/wcag-audit)).
2. **Custom mode `cc-review`**: runs the engine, then spawns **four Explore subagents in parallel**, one per WCAG principle, and merges their findings. The reviewers are read-only by design.
3. **Custom mode `cc-fixer`**: may edit only the app and its fixes list (`fileRegex`), and makes the smallest change per finding.
4. **Custom mode `cc-prover`**: may edit only `tests/a11y`, writes one test per fix, and runs `curbcut verify`.

The engine measures; Bob interprets. A model never changes a measured value.

## How to test

1. Open [curbcut.eziedutech.dev](https://curbcut.eziedutech.dev) and open **PR-1**.
2. Compare the screen reader narration before and after the fix, then read the findings by WCAG principle.
3. **Evidence** shows the benchmark against planted issues.

To review a branch yourself in IBM Bob, select the **CurbCut Review** mode and follow the steps in `.bob/rules-cc-review/`.

## Architecture

![CurbCut architecture: the engine measures a pull request into facts.json; in IBM Bob, cc-review runs four Explore subagents in parallel and writes findings.json, cc-fixer writes fixes, cc-prover writes tests; curbcut verify proves each fix, and the report goes to the dashboard and GitHub code scanning.](assets/architecture.svg)

```
Pull request
  -> curbcut scan        axe-core, WCAG contrast, Tab crawl, accessibility tree   facts.json
  -> Bob cc-review       4 Explore subagents in parallel, one per principle        findings.json
  -> Bob cc-fixer        smallest fix per finding                                  fixes.json
  -> Bob cc-prover       one test per fix, then curbcut verify (red, then green)   verify.json
  -> curbcut report      report.json -> dashboard; curbcut sarif -> GitHub code scanning

codes/
  engine/        Python CLI: scan, validate, verify, sarif, report, publish, testkit
  backpy/        FastAPI report API (Postgres)
  frontrouter/   React Router dashboard (Radix Themes)
  fixture/       OpenClass, the demo class app
tests/a11y/      regression tests written by cc-prover
reports/curbcut/ review outputs per pull request
```

## Running locally

Requires Docker, `uv` and Node 24.

```bash
cd codes/engine && uv sync && uv run playwright install chromium
```

```bash
GIT_SHA=$(git rev-parse --short HEAD) docker compose up --build
```

Open `http://localhost:3320`, then publish a report:

```bash
CURBCUT_INGEST_TOKEN=local-token uv run --project codes/engine curbcut publish reports/curbcut/pr-1/report.json --url http://localhost:3320
```

Tests:

```bash
cd codes/engine && uv run pytest tests
```

```bash
cd codes/backpy && uv run pytest
```

## Configuration

| Variable | Service | Purpose |
|---|---|---|
| `DATABASE_URL` | backpy | Postgres for reports |
| `CURBCUT_INGEST_TOKEN` | backpy | required on `POST /api/reports/ingest` |
| `BACKPY_INTERNAL_URL` | frontrouter | internal address of backpy, read server-side only |
| `GIT_SHA` | both | build version, returned by `/health` |

## Results

Scored by [`scripts/benchmark/score.py`](scripts/benchmark/score.py) against the issues planted in [OpenClass](codes/fixture) ([ground truth](scripts/benchmark/ground-truth.json)). A finding counts only when it points at the same DOM element with an accepted success criterion.

| Pull request | axe-core alone | CurbCut engine | **CurbCut with IBM Bob** | Decoys flagged |
|---|---|---|---|---|
| PR-1 quiz sign-up, run 1 | 8 of 18 | 11 of 18 | **16 of 18** | 0 of 6 |
| PR-1 quiz sign-up, run 2 | 8 of 18 | 11 of 18 | **14 of 18** | 0 of 6 |
| PR-2 lesson media | 6 of 16 | 7 of 16 | **14 of 16** | 0 of 6 |

- **23 of 23 fixes on PR-1 verified**: each test fails on the pull request and passes on the fixed branch. After the fix, the engine finds 0 of the 13 measured violations.
- The engine is deterministic: both PR-1 runs produced the same facts. The two runs differ only in IBM Bob's judgment findings (5 and 3 of 7), which is run-to-run variation.
- Missed in both PR-1 runs: a radio group without fieldset and legend, and a sensory instruction whose finding pointed at the neighbouring paragraph.

## What it does not claim

- It does not certify WCAG conformance. Testing with disabled people cannot be replaced.
- It does not judge real screen reader experience, cognitive load, or caption quality.
- Flagged findings are IBM Bob's judgment and can be wrong.
- The issues were planted by the team that built CurbCut, in a demo app. Other code bases may differ.

## Roadmap

- Run the review from a GitHub Action when a pull request opens.
- A status check that blocks merge on proven critical findings.
- Output in Indonesian.

## Credits and licenses

- **IBM Bob** 2.0 (IDE): skill, custom modes, subagents, fixes and tests.
- **WCAG 2.2**, W3C Recommendation 12 December 2024, W3C Document License.
- **axe-core** 4.13.0 by Deque Systems, MPL-2.0, vendored unmodified with its license.
- **Playwright**, **pytest**, **FastAPI**, **SQLAlchemy**, **PostgreSQL**, **React Router**, **React**, **Radix Themes**: their respective open source licences.
- OpenClass, its images, video and audio were made for this project. No personal data.

## How this was built

IBM Bob built the review itself: the skill, the three modes, the parallel review, the fixes and the tests. A code assistant was used to speed up development and debugging of the supporting engine and dashboard.

## License

Apache 2.0, see [LICENSE](LICENSE).
