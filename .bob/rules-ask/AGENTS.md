# Project Documentation Context (Non-Obvious Only)

- **Primary rules files are in Indonesian** (`project-global-rule.md`, `agents/ATURAN-MAIN.md`, `docs/`). All UI text and commit messages must be in English.
- **`codes/fixture/`** is a static HTML demo app (OpenClass), not the product. The product is the engine + Bob modes + API + dashboard.
- **`codes/engine/` is a Python package named `curbcut`** installed via `uv` as a CLI tool. The four commands are `scan`, `validate`, `verify`, `sarif` — documented in `docs/BOB-PROMPTS.md`.
- **`tests/a11y/`** (repo root) holds the accessibility regression tests written by the `cc-prover` Bob mode — separate from `codes/engine/tests/` (engine self-tests).
- **`scripts/benchmark/`** is in `.bobignore`. Bob cannot and must not read `ground-truth.json` at any time.
- **Three evidence tiers** are the product core: Proven (deterministic), Flagged (model judgment with written reason), Out of reach (fixed list per page). These map to `facts.json` → `findings.json` → dashboard labels.
- **Data files** flow in one direction: `facts.json` (engine, no verdicts) → `findings.json` (orchestrator, verdicts) → `fixes.json` (fixer) → `verify.json` (prover) → `report.json` (assembled by `curbcut report`) → published to backpy.
- **Bob session evidence** is mandatory for submission: PNG screenshots of task consumption summaries saved to `bob_sessions/` with naming `curbcut_taskNN_description_summary.png`.
- **Subagents cannot use custom modes** — WCAG principle reviewers are Explore (read-only) subagents, not custom modes.
- **`.bob/` does not exist yet** — it is created by Bob during Task 02 and 03. Its planned layout is in `docs/KONVENSI-NAMA.md`.
