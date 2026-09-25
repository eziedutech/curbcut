# CurbCut

Accessibility review that proves its fixes.

CurbCut is an accessibility review agent for pull requests, built on IBM Bob 2.0 for the IBM Bob 2.0 Hackathon. It checks UI changes against WCAG 2.2 Level A and AA, separates findings by strength of evidence, proposes fixes, and proves each fix with a test that fails before the fix and passes after it.

Work in progress. Full documentation follows.

## Repository layout

| Path | Contents |
|---|---|
| `codes/engine` | Deterministic engine (Python, Playwright, axe-core) |
| `codes/fixture` | OpenClass, a small demo class app with planted accessibility issues |
| `codes/backpy` | Report API (FastAPI) |
| `codes/frontrouter` | Dashboard (React Router, Radix Themes) |
| `.bob/` | IBM Bob skill, custom modes and rules, written with IBM Bob |
| `bob_sessions/` | IBM Bob task session consumption summaries |
| `reports/curbcut/` | Review outputs per pull request |
| `tests/a11y` | Accessibility regression tests |
| `scripts/benchmark` | Benchmark ground truth and scoring |
