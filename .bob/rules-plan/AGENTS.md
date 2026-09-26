# Project Architecture Rules (Non-Obvious Only)

- **Engine is intentionally stateless and deterministic.** `facts.json` contains only measured facts with no verdicts (global rule 25). Bob interprets; engine does not judge. This is auditable: anyone can re-run the engine without Bob access.
- **Three-tier separation is a hard design constraint** (global rule 60): engine measures (Proven), Bob subagents flag (Flagged), `cc-prover` verifies fixes (Verified fix). No tier may override another's output.
- **Subagents cannot use custom modes** — four WCAG-principle reviewers run as Explore (read-only) subagents in parallel, not as custom modes. Privilege separation comes from the platform type, not from configuration.
- **`cc-fixer` file-edit scope is limited by `fileRegex`** to `codes/fixture/src/**` and `reports/curbcut/[^/]+/fixes.json`. Writing outside these paths is a design violation.
- **`cc-prover` file-edit scope is limited to `tests/a11y/test_*.py`**. It writes tests, not code fixes.
- **Determinism is the benchmark gate.** `curbcut scan` on the same branch must produce the same `digest` on two consecutive runs. Non-determinism in `facts.json` is a bug, not variance.
- **`aria snapshot` is separated into `snapshots.json`** to avoid charging Bob context for every reader of `facts.json`.
- **SSR is on** in frontrouter (`ssr: true` in `react-router.config.ts`). `BACKPY_INTERNAL_URL` is server-only; never expose it to the browser bundle.
- **Postgres is required in production; aiosqlite is used only in tests.** `create_tables` is called at lifespan; migrations are not rolled back — forward-only.
- **`/api/health` must return the running `GIT_SHA`** — used to prove the deployed build matches the expected commit (global rule 9).
- **Bob IDE instance for all Bob work**: `ibm-coding-challenge-uat` (us-east). Budget: 40 Bobcoin total per participant. Bob Shell is optional and not used in CI.
- **`.bob/` directory does not yet exist** — created by Bob in Task 02 (skill `wcag-audit`) and Task 03 (modes + rules). Plan is in `docs/KONVENSI-NAMA.md` and `docs/BOB-PROMPTS.md`.
