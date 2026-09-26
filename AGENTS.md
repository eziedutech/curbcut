# AGENTS.md

This file provides guidance to agents when working with code in this repository.

**Read before working, in order:** `project-global-rule.md` → `agents/ATURAN-MAIN.md` → `read_folder.md` → `docs/PLAN-EKSEKUSI.md` + `docs/KONVENSI-NAMA.md` → `agents/SESSION-HANDOFF.md` → `agents/memory.md`

---

## Project: CurbCut (IBM Bob 2.0 Hackathon)

Accessibility review agent for pull requests. Engine is deterministic Python; Bob provides reasoning. Three evidence tiers: **Proven** (deterministic), **Flagged** (model judgment), **Out of reach** (not measurable).

## Stack

| Component | Location | Tech |
|---|---|---|
| Engine (deterministic) | `codes/engine` | Python 3.14.6, uv, Playwright 1.63.0, axe-core 4.13.0 (vendored) |
| Backend API | `codes/backpy` | FastAPI 0.141.1, SQLAlchemy async, Postgres (aiosqlite in tests) |
| Frontend | `codes/frontrouter` | React Router v8 (SSR), Radix Themes 3.3.0, TypeScript strict, Node ≥24.21.0 |
| Fixture/demo app | `codes/fixture` | Static HTML — OpenClass |
| Bob config | `.bob/` (not yet created) | custom modes, skills, rules — created by Bob in Task 02/03 |

## Commands

### Engine (`codes/engine`)
```bash
uv run pytest                          # all tests
uv run pytest tests/test_measurements.py::test_contrast_matches_wcag_formula  # single test
uv run curbcut scan --base <sha> --head <sha> --out reports/curbcut/<id>/facts.json
uv run curbcut validate reports/curbcut/<id>/findings.json
uv run curbcut verify --id pr-1 --base <sha> --head <sha> --tests tests/a11y --out reports/curbcut/pr-1/verify.json
uv run curbcut sarif reports/curbcut/<id>/findings.json
uv run curbcut report --id pr-1
uv run curbcut publish report.json --url https://curbcut.eziedutech.dev
```
Run `uv run pytest` from `codes/engine/`. First run after branch switch triggers `uv` rebuild — expected, not an error.

### Backend (`codes/backpy`)
```bash
uv run pytest                          # all tests (uses aiosqlite, no Postgres needed)
uv run pytest tests/test_reports.py::test_ingest_then_list_and_get  # single test
uv run uvicorn app.main:app --reload   # local dev
```
Run from `codes/backpy/`. Set `DATABASE_URL`, `CURBCUT_INGEST_TOKEN`, `APP_ENV`, `GIT_SHA` env vars (see `codes/backpy/.env.example`).

### Frontend (`codes/frontrouter`)
```bash
npm run dev          # local dev (SSR)
npm run build        # production build
npm run typecheck    # react-router typegen + tsc (must pass before commit)
```
Run from `codes/frontrouter/`. SSR is on. `BACKPY_INTERNAL_URL` is server-side only. `allowedActionOrigins` is set to `curbcut.eziedutech.dev` in `react-router.config.ts` — add `localhost` if testing actions locally.

## Critical Patterns

- **axe-core is vendored** at `codes/engine/curbcut/vendor/` and excluded from Bob via `.bobignore`. Do not import from npm.
- **`target-size` rule is disabled by default** in axe 4.13.0 — engine enables it explicitly. `td-has-header` is experimental.
- **`page.clock.pause_at` in Playwright causes `axe.run` to hang** — engine uses `setInterval` hold via init script but allows `setTimeout`.
- **Engine tests use `page` fixture from pytest-playwright** (no `@pytest.mark.playwright` needed; conftest at `tests/a11y/conftest.py`).
- **Regression tests go in `tests/a11y/`** (not inside `codes/engine/tests/`). `curbcut verify --id pr-1` collects files matching `test_pr1_*.py`.
- **After writing to DB, always read back** to confirm — `ingest` endpoint does this explicitly (global rule 22).
- **`scripts/benchmark/ground-truth.json` is in `.bobignore`** — Bob must not read it during any review task.
- **Bob instance for hackathon**: `ibm-coding-challenge-uat` (region: us-east). Wrong instance = personal Bobcoin.
- **Bob budget**: 40 Bobcoin total. One benchmark run per command. No re-runs for video purposes.
- **Subagents cannot use custom modes** — WCAG reviewers use Explore (read-only) subagent type.

## Code Style

- **Python**: `snake_case` functions/modules/vars, `PascalCase` classes and Pydantic models. `from __future__ import annotations` at top of engine files.
- **TypeScript**: `camelCase` functions/vars, `PascalCase` components and types. `verbatimModuleSyntax: true` — use `import type` for type-only imports.
- **Components**: `PascalCase.tsx`, one primary component per file.
- **CSS classes**: prefix `cc-` to avoid collisions with Radix's `rt-` prefix.
- **API routes**: `/api/<group>/<action>`, lowercase. Example: `/api/reports/ingest`.
- **No emdash anywhere** — not in code, comments, commit messages, or UI text (global rule 38).
- **No `Co-Authored-By` lines** in commits (global rule 52).
- **Commit messages in English**, explain the reason not the file list (global rule 66).
- **UI**: Radix Themes with `radius="none"`. Skeleton loading (not spinners). No left borders on boxes. All UI text in English.

## Git & Credentials

- Git identity per repo: `Zia <320255445+eziedutech@users.noreply.github.com>`. Global identity on this machine (`ZiaDev`) is wrong for this project — always verify with `git config user.email`.
- Push token lives in `credentials/githubtoken.txt`. Use credential helper one-shot in CLI, never write to git config.
- `credentials/`, `agents/`, `docs/`, `resources/`, `project-global-rule.md`, `CLAUDE.md` are git-ignored from the public repo.
- Bob session screenshots → `bob_sessions/curbcut_taskNN_description_summary.png`.
