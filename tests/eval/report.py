"""Generate a summary report from eval test results.

Usage:
    python tests/eval/report.py
"""

import json
import sys
from collections import Counter
from pathlib import Path

RESULTS_FILE = Path(__file__).parent / "test_results.json"
CASES_FILE = Path(__file__).parent / "test_cases.json"


def main():
    if not RESULTS_FILE.exists():
        print("No results found. Run /eval-routing first.")
        sys.exit(1)

    results = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    cases = json.loads(CASES_FILE.read_text(encoding="utf-8")) if CASES_FILE.exists() else []

    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    failed = total - passed
    total_cases = len(cases)
    untested = total_cases - total

    print("=" * 60)
    print("MCP Tool Routing Eval Report")
    print("=" * 60)
    print(f"Total cases:  {total_cases}")
    print(f"Tested:       {total}")
    print(f"Passed:       {passed}")
    print(f"Failed:       {failed}")
    print(f"Untested:     {untested}")
    print(f"Pass rate:    {passed/total*100:.1f}%" if total > 0 else "Pass rate:    N/A")
    print()

    # By category
    cat_results = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in cat_results:
            cat_results[cat] = {"pass": 0, "fail": 0}
        if r["pass"]:
            cat_results[cat]["pass"] += 1
        else:
            cat_results[cat]["fail"] += 1

    if cat_results:
        print("By category:")
        for cat, counts in sorted(cat_results.items()):
            total_cat = counts["pass"] + counts["fail"]
            rate = counts["pass"] / total_cat * 100
            print(f"  {cat:20s}  {counts['pass']}/{total_cat} ({rate:.0f}%)")
        print()

    # Expected-error cases
    error_cases = [r for r in results if r.get("expected_error")]
    if error_cases:
        print("Expected-error cases (routed correctly, tool error expected):")
        for r in error_cases:
            status = "PASS" if r["pass"] else "FAIL"
            print(f"  [{status}] Case {r['id']}: {r['prompt'][:50]}...")
        print()

    # Failures detail
    failures = [r for r in results if not r["pass"]]
    if failures:
        print("Failures:")
        for r in failures:
            print(f"  Case {r['id']}: {r['prompt'][:50]}...")
            print(f"    Missing: {r.get('missing', [])}")
            print(f"    Actual:  {r['actual']}")
        print()

    # Most missed tools
    missed = Counter()
    for r in failures:
        for tool in r.get("missing", []):
            missed[tool] += 1
    if missed:
        print("Most missed tools:")
        for tool, count in missed.most_common(10):
            print(f"  {tool}: missed {count} time(s)")


if __name__ == "__main__":
    main()
