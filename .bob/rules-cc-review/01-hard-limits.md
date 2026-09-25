# CurbCut Review: Hard Limits

- Never edit source code (fixture, engine, backend, or frontend). The only file you
  may write is reports/curbcut/<id>/findings.json.
- Never claim a finding is proven unless you have a matching fact_id from facts.json.
- Never downgrade a finding's severity or evidence tier to reduce the count of issues.
- Spawn subagents as Explore type (read-only). Do not grant them edit access.
- Run curbcut scan exactly once per review. Do not re-run to change results.
- Do not read scripts/benchmark/ground-truth.json under any circumstances.
