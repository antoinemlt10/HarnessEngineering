#!/bin/bash
# ============================================================
# log-session.sh — append one session entry to skill-log.jsonl
# ------------------------------------------------------------
# Called at the END of a session (by Claude, or by you). It validates
# the JSON against the schema BEFORE appending, so the log never gets
# corrupted. Optionally commits + pushes.
#
# Usage:
#   bash scripts/log-session.sh '<json-entry>'            # append only
#   bash scripts/log-session.sh '<json-entry>' --push     # append + commit + push
#
# Example:
#   bash scripts/log-session.sh '{"session_id":"2026-06-08-codelab-x",
#     "date":"2026-06-08T12:00:00Z","project":"codelab","task":"...",
#     "skills_used":["elite-design"],"verify_passed":true}' --push
# ============================================================

set -uo pipefail
cd "$(dirname "$0")/.." || exit 2   # repo root

ENTRY="${1:-}"
PUSH="${2:-}"
LOG="skill-log.jsonl"

[ -z "$ENTRY" ] && { echo "Usage: log-session.sh '<json>' [--push]"; exit 1; }

# 1. Validate it's well-formed JSON
echo "$ENTRY" | python3 -c "import sys,json; json.loads(sys.stdin.read())" 2>/dev/null || {
  echo "❌ Not valid JSON. Aborting."; exit 1;
}

# 2. Validate required fields (quick check)
echo "$ENTRY" | python3 -c "
import sys, json
o = json.loads(sys.stdin.read())
req = ['session_id','date','project','skills_used','verify_passed']
missing = [r for r in req if r not in o]
if missing:
    print('❌ missing fields:', ', '.join(missing)); sys.exit(1)
" || exit 1

# 3. Append (compact, one line)
echo "$ENTRY" | python3 -c "import sys,json; print(json.dumps(json.loads(sys.stdin.read())))" >> "$LOG"
echo "✓ Appended to $LOG ($(wc -l < "$LOG") entries total)"

# 4. Full schema validation of the whole file
python3 scripts/validate-log.py "$LOG" "schema/session-entry.schema.json" || {
  echo "⚠️ Log now has validation issues — review before pushing."; exit 1;
}

# 5. Optional commit + push
if [ "$PUSH" = "--push" ]; then
  git add "$LOG"
  git commit -m "log: session $(echo "$ENTRY" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read())["session_id"])')" >/dev/null 2>&1
  git push >/dev/null 2>&1 && echo "✓ Pushed to remote" || echo "⚠️ Push failed (check remote/auth)"
fi
