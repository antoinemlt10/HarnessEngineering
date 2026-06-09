#!/usr/bin/env python3
"""
validate-log.py — validate every line of a .jsonl log against the schema.

This is a FB+Computational check on the LOG ITSELF: a malformed entry would
silently corrupt your weekly analysis, so we catch it at commit time (CI runs
this on push). Uses jsonschema if available, falls back to a minimal check.

Usage: python3 validate-log.py [skill-log.jsonl] [schema/session-entry.schema.json]
Exit:  0 = all lines valid | 1 = at least one invalid line
"""
import json
import sys
from pathlib import Path

LOG = sys.argv[1] if len(sys.argv) > 1 else "skill-log.jsonl"
SCHEMA = sys.argv[2] if len(sys.argv) > 2 else "schema/session-entry.schema.json"

REQUIRED = ["session_id", "date", "project", "skills_used", "verify_passed"]

def minimal_check(obj, i):
    errs = []
    for r in REQUIRED:
        if r not in obj:
            errs.append(f"line {i}: missing required field '{r}'")
    if "verify_passed" in obj and not isinstance(obj["verify_passed"], bool):
        errs.append(f"line {i}: verify_passed must be boolean")
    if "skills_used" in obj and not isinstance(obj["skills_used"], list):
        errs.append(f"line {i}: skills_used must be array")
    return errs

def main():
    if not Path(LOG).exists():
        print(f"OK: {LOG} does not exist yet (empty log is valid).")
        sys.exit(0)

    lines = [l for l in Path(LOG).read_text().splitlines() if l.strip()]
    if not lines:
        print(f"OK: {LOG} is empty.")
        sys.exit(0)

    # Try jsonschema for full validation
    validator = None
    try:
        import jsonschema
        schema = json.loads(Path(SCHEMA).read_text())
        validator = jsonschema.Draft202012Validator(schema)
    except ImportError:
        print("(jsonschema not installed — using minimal field check)")
    except Exception as e:
        print(f"(could not load schema: {e} — using minimal check)")

    all_errs = []
    for i, line in enumerate(lines, 1):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            all_errs.append(f"line {i}: invalid JSON ({e})")
            continue
        if validator:
            for err in validator.iter_errors(obj):
                all_errs.append(f"line {i}: {err.message}")
        else:
            all_errs.extend(minimal_check(obj, i))

    if all_errs:
        print(f"❌ {len(all_errs)} validation error(s) in {LOG}:")
        for e in all_errs:
            print(f"  {e}")
        sys.exit(1)
    print(f"✓ All {len(lines)} entries in {LOG} are valid.")
    sys.exit(0)

if __name__ == "__main__":
    main()
