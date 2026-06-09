#!/usr/bin/env python3
"""
analyze.py — quantitative analysis of skill-log.jsonl.

Computes per-skill stats (verify-pass rate, avg tokens, recurring missed bugs)
so you rate and improve skills with DATA, not intuition. Run it weekly.

Usage: python3 analyze.py [skill-log.jsonl]
"""
import json
import sys
from collections import defaultdict

def load(path):
    rows = []
    try:
        with open(path) as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"  ! skipping malformed line {i}", file=sys.stderr)
    except FileNotFoundError:
        print(f"No log at {path}. Append one JSON object per session to start.")
        sys.exit(0)
    return rows

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "skill-log.jsonl"
    rows = load(path)
    if not rows:
        print("Log empty. Come back after ~20 sessions for meaningful patterns.")
        sys.exit(0)

    per_skill = defaultdict(lambda: {
        "uses": 0, "verify_pass": 0, "tokens": 0,
        "sensor_errors": 0, "later_errors": 0, "later_list": []
    })
    per_project = defaultdict(lambda: {"sessions": 0, "tokens": 0, "verify_pass": 0})

    for r in rows:
        proj = per_project[r.get("project", "?")]
        proj["sessions"] += 1
        proj["tokens"] += r.get("tokens_est", 0) or 0
        if r.get("verify_passed"):
            proj["verify_pass"] += 1
        for sk in r.get("skills_used", []):
            s = per_skill[sk]
            s["uses"] += 1
            if r.get("verify_passed"):
                s["verify_pass"] += 1
            s["tokens"] += r.get("tokens_est", 0) or 0
            s["sensor_errors"] += len(r.get("errors_caught_by_sensors") or [])
            later = r.get("errors_found_later")
            if later:
                s["later_errors"] += 1
                s["later_list"].append(later)

    print(f"\n=== SKILL ANALYSIS — {len(rows)} sessions ===\n")
    h = f"{'skill':<22}{'uses':>5}{'verify%':>9}{'avg_tok':>9}{'later_bugs':>12}"
    print(h); print("-" * len(h))
    for skill, s in sorted(per_skill.items(), key=lambda kv: (kv[1]['verify_pass']/kv[1]['uses']) if kv[1]['uses'] else 1):
        rate = (s["verify_pass"]/s["uses"]*100) if s["uses"] else 0
        avg = (s["tokens"]//s["uses"]) if s["uses"] else 0
        flag = "  <-- review" if rate < 75 or s["later_errors"] >= 3 else ""
        print(f"{skill:<22}{s['uses']:>5}{rate:>8.0f}%{avg:>9}{s['later_errors']:>12}{flag}")

    print(f"\n=== BY PROJECT ===\n")
    for proj, p in sorted(per_project.items(), key=lambda kv: -kv[1]['sessions']):
        rate = (p["verify_pass"]/p["sessions"]*100) if p["sessions"] else 0
        print(f"  {proj:<16} {p['sessions']:>3} sessions | {rate:>3.0f}% verify | {p['tokens']:>8} tok total")

    print("\n=== RECURRING 'errors_found_later' (what your sensors MISS) ===")
    found = False
    for skill, s in per_skill.items():
        if s["later_list"]:
            found = True
            print(f"\n  {skill}:")
            counts = defaultdict(int)
            for e in s["later_list"]:
                counts[e] += 1
            for err, n in sorted(counts.items(), key=lambda x: -x[1]):
                marker = "  ← add a sensor for this" if n >= 2 else ""
                print(f"    {n}x  {err}{marker}")
    if not found:
        print("  (none logged yet — fill errors_found_later when bugs surface)")

    print("\n=== ACTION ===")
    print("  Skill flagged <-- review OR recurring later-error (≥2x):")
    print("  add a computational sensor (scripts/) or AGENTS.md rule so the miss")
    print("  becomes catchable next time. Steering loop, closed with data.\n")

if __name__ == "__main__":
    main()
