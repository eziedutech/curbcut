---
name: wcag-audit
description: Review web UI code changes against WCAG 2.2 Level A and AA, separating proven, flagged and out-of-reach findings.
---

# WCAG Audit Reviewer

Use this skill when asked to review a pull request or diff for accessibility against WCAG 2.2 Level A and AA.

## Evidence tiers

**Proven** - A finding is proven only when it cites a `fact_id` from `facts.json` produced by the engine. State the fact_id, the SC number, and one sentence on how the fact violates the criterion. Never claim a finding is proven without a fact_id.

**Flagged** - A finding is flagged when the code or design raises a reasonable concern but no engine measurement exists to confirm it. Give one sentence explaining what you observed in the code and why it may fail the criterion.

**Out of reach** - Some criteria cannot be measured from code alone. Always list these explicitly so the reader knows they were considered and not just skipped.

## How to say who is affected

For every finding, say who is affected in plain terms: for example, "screen reader users", "keyboard-only users", "people with low vision", or "people with cognitive disabilities". Do not use jargon like "AT users" without explaining it.

## Review steps

1. Load `reports/curbcut/<id>/facts.json` if it exists. Note each `fact_id`, `sc`, and `value`.
2. Load `.bob/skills/wcag-audit/policy/wcag22-aa.json`. This lists every Level A and AA criterion with its method (`engine`, `judgment`, or `out_of_reach`) and the axe rules that cover it.
3. For each criterion with `method: engine`: check facts.json for a matching fact. If a fact fails the criterion, write a **Proven** finding with the fact_id. If no fact exists, note it as untested.
4. For each criterion with `method: judgment`: read the diff or rendered code and apply the `review_questions` from the policy file. If a problem is visible, write a **Flagged** finding with one sentence of reasoning. Do not invent measurements.
5. For each criterion with `method: out_of_reach`: list it under **Out of reach** with one sentence explaining why it cannot be verified from code review.

## Output format

```
## Proven findings
- [SC X.Y.Z] <title> (fact_id: <id>): <one sentence on the violation and who is affected>

## Flagged findings
- [SC X.Y.Z] <title>: <one sentence on what was observed and why it may fail>

## Out of reach
- [SC X.Y.Z] <title>: <one sentence on why this cannot be checked>

## Untested (engine criteria with no fact in facts.json)
- [SC X.Y.Z] <title>
```

## Rules

- Never invent measurements, contrast ratios, pixel sizes, or computed values. Only quote values that appear in facts.json.
- A finding must trace to a specific SC number from WCAG 2.2.
- Do not use em dashes. Use a comma or a new sentence instead.
- Plain language. Write for a developer who is not an accessibility specialist.
- Keep findings short. One paragraph per finding is enough.
