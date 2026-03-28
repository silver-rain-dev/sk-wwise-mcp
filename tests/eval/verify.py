"""Verify MCP tool routing for the current eval test case.

Compares tool_log.jsonl (actual tools called) against test_cases.json
(expected tools). Appends result to test_results.json.

Usage:
    python tests/eval/verify.py                # Verify next untested case
    python tests/eval/verify.py --reset        # Clear all results
    python tests/eval/verify.py --check-stale  # Check if results are stale (all done), auto-reset if so
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

EVAL_DIR = Path(__file__).parent
CASES_FILE = EVAL_DIR / "test_cases.json"
RESULTS_FILE = EVAL_DIR / "test_results.json"
LOG_FILE = EVAL_DIR / "tool_log.jsonl"


def strip_mcp_prefix(tool_name: str) -> str:
    """Strip mcp__sk-wwise-*__ prefix to get bare tool name.

    e.g. "mcp__sk-wwise-browse__get_wwise_object_info" -> "get_wwise_object_info"
    """
    match = re.match(r"^mcp__[^_]+(?:_[^_]+)*__(.+)$", tool_name)
    if match:
        return match.group(1)
    return tool_name


def load_cases() -> list[dict]:
    if not CASES_FILE.exists():
        print("ERROR: test_cases.json not found")
        sys.exit(1)
    return json.loads(CASES_FILE.read_text(encoding="utf-8"))


def load_results() -> list[dict]:
    if not RESULTS_FILE.exists():
        return []
    return json.loads(RESULTS_FILE.read_text(encoding="utf-8"))


def save_results(results: list[dict]):
    RESULTS_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")


def load_tool_log() -> list[str]:
    """Load tool names from tool_log.jsonl."""
    if not LOG_FILE.exists():
        return []
    tools = []
    for line in LOG_FILE.read_text(encoding="utf-8").strip().splitlines():
        if line.strip():
            entry = json.loads(line)
            tools.append(strip_mcp_prefix(entry["tool"]))
    return tools


def get_next_untested_case(cases: list[dict], results: list[dict]) -> dict | None:
    """Find the next case that hasn't been tested yet."""
    tested_ids = {r["id"] for r in results}
    for case in cases:
        if case["id"] not in tested_ids:
            return case
    return None


def is_stale(cases: list[dict], results: list[dict]) -> bool:
    """Check if results are stale (all cases already tested)."""
    if not results:
        return False
    tested_ids = {r["id"] for r in results}
    case_ids = {c["id"] for c in cases}
    return case_ids.issubset(tested_ids)


def check_stale():
    """Check for stale results and auto-reset if all cases are already done."""
    cases = load_cases()
    results = load_results()

    if not results:
        print("No existing results. Ready to run.")
        return

    if is_stale(cases, results):
        mtime = datetime.fromtimestamp(
            RESULTS_FILE.stat().st_mtime, tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"Stale results detected (from {mtime}, {len(results)}/{len(cases)} complete). Auto-resetting.")
        reset()
    else:
        tested = len({r["id"] for r in results})
        print(f"Results in progress: {tested}/{len(cases)} tested. Resuming.")


def verify():
    cases = load_cases()
    results = load_results()
    actual_tools = load_tool_log()

    # The case we're verifying is the next untested one
    case = get_next_untested_case(cases, results)
    if case is None:
        print("All cases already verified.")
        return

    expected = set(case["expected_tools"])
    actual_set = set(actual_tools)
    missing = expected - actual_set
    passed = len(missing) == 0

    # Check expected_error field
    expected_error = case.get("expected_error", False)

    result = {
        "id": case["id"],
        "prompt": case["prompt"],
        "category": case.get("category", "unknown"),
        "pass": passed,
        "expected": sorted(expected),
        "actual": sorted(actual_set),
    }
    if expected_error:
        result["expected_error"] = True
    if missing:
        result["missing"] = sorted(missing)

    results.append(result)
    save_results(results)

    # Print result with progress
    total = len(cases)
    tested = len(results)
    status = "PASS" if passed else "FAIL"
    error_note = " (expected error)" if expected_error else ""
    print(f"[{status}] [{tested}/{total}] Case {case['id']}: {case['prompt'][:55]}...{error_note}")
    if not passed:
        print(f"  Expected: {sorted(expected)}")
        print(f"  Actual:   {sorted(actual_set)}")
        print(f"  Missing:  {sorted(missing)}")
    else:
        print(f"  Tools called: {sorted(actual_set)}")


def reset():
    if RESULTS_FILE.exists():
        RESULTS_FILE.unlink()
        print("Cleared test_results.json")
    if LOG_FILE.exists():
        LOG_FILE.unlink()
        print("Cleared tool_log.jsonl")
    print("Reset complete.")


if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset()
    elif "--check-stale" in sys.argv:
        check_stale()
    else:
        verify()
