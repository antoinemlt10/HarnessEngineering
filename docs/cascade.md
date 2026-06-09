# The Cascade

The canonical pipeline that orchestrates the skills. `architect-agent` runs it.

```
office-hours (frame the problem — optional, for fuzzy requests)
  │
  ▼
architect-agent (decompose + assign roles)
  │
  ▼
BUILD PHASE (parallel)
  builders [elite-design | secure-deploy | …] + code-simplify (always-on)
  ‖ adversarial-agents trio (Skeptic / Architect / Minimalist) runs CONCURRENTLY
  │
  ▼
COMPUTATIONAL GATE  ◀── hard gate; must pass before synthesis
  each builder runs its scripts/:
    adversarial-agents/scripts/static-checks.sh     (lint + type + test + secrets)
    code-simplify/scripts/complexity-check.sh       (complexity budget)
    elite-design/scripts/design-lint.sh             (responsive + a11y)
    secure-deploy/scripts/pre-deploy-scan.sh        (security, if shipping)
  │  (if the gate reveals a bug whose cause is unclear)
  ▼
investigate (5-phase root cause) → fix → re-run gate
  │
  ▼
secure-deploy pre-deploy scan (before going live)
  │
  ▼
agent-learning
  → LEARNING_LOG.md      (qualitative: what went wrong + the fix)
  → skill-log.jsonl      (quantitative: skills used, gate pass, tokens)

[OUT of cascade — manual] code-armada
  12 reviewers, ~15× cost. Fire at checkpoints / high-stakes code
  (auth, payments, data) / when adversarial flags something needing depth.
```

## Why this shape

- **Review is concurrent, not sequential.** adversarial-agents was built to run
  *in parallel with* builders. Catching issues during the build is cheaper than
  a separate pass after.
- **The gate is computational and hard.** Cheap deterministic checks (lint, type,
  tests, secrets, complexity, responsive) run before any expensive LLM reasoning
  or synthesis. Keep quality left.
- **code-armada is the big gun, kept holstered.** 12 reviewers cost ~15×. The
  3-reviewer adversarial pass covers the default flow; code-armada is reserved.
- **Everything feeds the steering loop.** Each session logs to skill-log.jsonl;
  weekly `analyze.py` surfaces what the sensors miss; each miss becomes a new
  sensor. The harness improves itself with data.

## The two columns (Böckeler 2×2)

|             | Computational (deterministic, ~0 token) | Inferential (LLM reasoning) |
|-------------|------------------------------------------|------------------------------|
| Feedforward | type system, scaffolds, schemas          | office-hours, elite-design guidance |
| Feedback    | the scripts/ gate, tests, mutation       | adversarial-agents, code-armada |

The scripts in each skill's `scripts/` folder are what filled the previously
empty **computational** column.
