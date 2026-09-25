# OpenClass fixture

A small online class app used only as the CurbCut demo and benchmark target. Static HTML, CSS and JavaScript in `src/`. It stores no personal data and uses no third-party content.

Run it locally:

    python -m http.server 8080 --directory codes/fixture/src

Branches:

- `main`: accessible baseline
- `demo/pr-1-quiz-signup`: adds a quiz sign-up form
- `demo/pr-2-lesson-media`: adds a lesson page with media

The planted issues are listed only in `scripts/benchmark/ground-truth.json`, which IBM Bob is not allowed to read during a review.
