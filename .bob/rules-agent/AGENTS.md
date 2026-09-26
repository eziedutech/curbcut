# Project Coding Rules (Non-Obvious Only)

- **All Python components use `uv`**, not `pip`. Run commands as `uv run <cmd>` from the component directory (`codes/engine`, `codes/backpy`). `uv run pytest` in `codes/engine` may trigger a rebuild on first run after a branch switch — that is normal.
- **axe-core is vendored** at `codes/engine/curbcut/vendor/`. Never install or import from npm. Bob must not read this directory (`.bobignore`).
- **Engine tests (`codes/engine/tests/`)** use pytest-playwright's `page` fixture directly. No `@pytest.mark.playwright` annotation needed. Test infrastructure is in `curbcut.testkit` — assert on requirements (a name exists, contrast ≥ 4.5), never on implementation details.
- **Regression tests live in `tests/a11y/`** (repo root), not `codes/engine/tests/`. `curbcut verify --id <id>` collects files matching `test_<id-without-dash>_*.py` (e.g., `test_pr1_*.py` for id `pr-1`).
- **`page.clock.pause_at` hangs axe** — engine holds `setInterval` via an init script and allows `setTimeout`. Do not pause the clock in any test.
- **`target-size` (WCAG 2.5.8) is off by default in axe 4.13.0** — engine opts in explicitly. `td-has-header` is experimental. Do not rely on default axe rule sets.
- **After every DB write, read back** to confirm storage (global rule 22). The `ingest` endpoint in `codes/backpy/app/main.py` is the canonical example.
- **`verbatimModuleSyntax` is on** in `tsconfig.json`. Use `import type` for type-only imports in TypeScript or the build will fail.
- **`react-router.config.ts` sets `allowedActionOrigins`** to the production domain only. Add `localhost` when testing form actions locally.
- **CSS class prefix `cc-`** is mandatory for custom classes to avoid collisions with Radix's `rt-` classes.
- **No emdash anywhere** — not in code, comments, commit messages, or any generated UI text (global rule 38). Use a comma, colon, or new sentence instead.
- **Git identity is per-repo**: `Zia <320255445+eziedutech@users.noreply.github.com>`. Machine global (`ZiaDev`) is wrong. Verify before every commit with `git config user.email`.
- **`scripts/benchmark/ground-truth.json` must never be read by Bob** during any review task — it is in `.bobignore`. Do not open it.
- **Bob budget is 40 Bobcoin total** — one benchmark run per command; do not re-run for video. Use Bob IDE instance `ibm-coding-challenge-uat` (us-east); wrong instance bills personal Bobcoin.
