# HarnessEngineering

The measurement backbone for my agent harness. This repo is the **persistent
memory layer** that the session filesystem can't provide — it survives across
sessions because git survives.

It does two things:
1. **Logs every agent session** (quantitative) → `skill-log.jsonl`
2. **Records lessons + harness changes** (qualitative) → `LEARNING_LOG.md`

Then a weekly analysis turns that data into concrete skill improvements. That's
the steering loop, closed with data instead of intuition.

---

## How it works

```
session ends
   │
   ▼
log-session.sh appends a JSON entry  ──►  skill-log.jsonl  ──► git push
   │                                                              │
agent-learning notes a lesson  ──►  LEARNING_LOG.md  ────────────┘
   │
   ▼ (weekly)
analyze.py reads skill-log.jsonl  ──►  per-skill verify%, tokens,
                                        recurring missed bugs
   │
   ▼
each recurring miss  ──►  new computational sensor (scripts/) or AGENTS.md rule
```

The cascade that produces these sessions is documented in [`docs/cascade.md`](docs/cascade.md).

---

## Logging a session

At the end of a session, append one entry. Claude can do this automatically; the
helper validates against the schema before writing so the log never corrupts:

```bash
bash scripts/log-session.sh '{
  "session_id":"2026-06-08-codelab-x",
  "date":"2026-06-08T12:00:00Z",
  "project":"codelab",
  "task":"build X",
  "skills_used":["elite-design","adversarial-agents"],
  "agents_spawned":4,
  "verify_passed":true,
  "tokens_est":47000,
  "errors_caught_by_sensors":["eslint: unused import"],
  "errors_found_later":null
}' --push
```

**Rule:** log *objective facts only* — what ran, did the gate pass, tokens. NOT
self-graded quality (agents over-rate their own work). The one human-filled field
is `errors_found_later` — add it days later when a bug surfaces. It's the most
valuable signal because it reveals what the sensors MISS.

Schema: [`schema/session-entry.schema.json`](schema/session-entry.schema.json).
See [`skill-log.example.jsonl`](skill-log.example.jsonl) for filled examples.

---

## Weekly analysis

```bash
python3 scripts/analyze.py skill-log.jsonl
```

Outputs per-skill verify-pass rate, avg tokens, and recurring `errors_found_later`
patterns — flagging skills to review. Any miss seen ≥2× → add a sensor for it.

---

## Files

| Path | Role |
|------|------|
| `skill-log.jsonl` | Quantitative session log (one JSON per line) |
| `skill-log.example.jsonl` | Filled examples (not analyzed) |
| `LEARNING_LOG.md` | Qualitative lessons + harness changes |
| `schema/session-entry.schema.json` | JSON Schema for entries |
| `scripts/log-session.sh` | Validate + append (+ optional push) |
| `scripts/validate-log.py` | Validate every line vs schema |
| `scripts/analyze.py` | Weekly quantitative analysis |
| `docs/cascade.md` | The canonical skill cascade |
| `.github/workflows/validate.yml` | CI: validate log + print stats on push |

---

## CI

Every push that touches `skill-log.jsonl` runs `validate-log.py` (rejects a
corrupt entry) and prints `analyze.py` output in the Actions log. The log
validates itself — a computational check on the measurement system, so a
malformed entry can't silently skew the analysis.
