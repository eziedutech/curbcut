# CurbCut Global Rules

These rules apply to every CurbCut mode (cc-review, cc-fixer, cc-prover).

## Evidence tiers

Every finding must be assigned exactly one of these tiers:

- **proven**: The finding is backed by a `fact_id` from `facts.json` produced by the
  deterministic engine. State the fact_id, the SC number, and one sentence on how the
  fact violates the criterion. Never claim proven without a fact_id.
- **flagged**: The code or design raises a reasonable concern but no engine measurement
  exists to confirm it. Give one sentence explaining what was observed and why it may
  fail.
- **out_of_reach**: The criterion cannot be measured from code or a rendered page
  alone. Always list these explicitly so the reader knows they were considered.

## Immutable measurements

Never change, round, or editorialize any numeric value that appears in facts.json
(contrast ratios, pixel sizes, computed values). Quote them verbatim or not at all.

## No em dashes

Do not use em dashes (--) anywhere: not in findings, not in code comments, not in
commit messages, not in generated UI text. Use a comma, a colon, or a new sentence.

## Language

All output must be in English.
