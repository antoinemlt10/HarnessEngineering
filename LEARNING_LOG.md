# LEARNING_LOG

Qualitative companion to `skill-log.jsonl`. Where `skill-log.jsonl` holds
*metrics* (what ran, did the gate pass, tokens), this holds *lessons* (what
went wrong and what we changed). agent-learning appends here.

**Format per entry:**

```
### [YYYY-MM-DD HH:MM] | <type> | [tag:project] [tag:skill]
What happened: ...
Root cause: ...
Fix applied: ... (AGENTS.md rule / new sensor / skill edit / nothing-yet)
Quadrant (Böckeler): FF+Comp | FF+Inf | FB+Comp | FB+Inf
Recurrence: 1st time | seen Nx before
```

Types: `🐛 bug-caught` · `🤝 false-positive` · `⚠️ regression` ·
`💡 insight` · `🔧 harness-change` · `📊 calibration`

---

## Entries

<!-- newest first -->

### [2026-06-01 14:32] | 💡 insight | [tag:codelab] [tag:elite-design]
What happened: elite-design output looked great on desktop, broke <640px.
Root cause: no responsive breakpoints generated; no computational check for it.
Fix applied: added elite-design/scripts/design-lint.sh (checks viewport,
breakpoints, fixed px widths). FB+Comp.
Quadrant: FB+Comp
Recurrence: seen 2x before (see skill-log errors_found_later)
