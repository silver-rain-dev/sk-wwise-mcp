"""Verify MCP tool routing for the current eval test case.

Compares tool_log.jsonl (actual tools called) against test_cases.json
(expected tools). Appends result to test_results.json.

Usage:
    python tests/eval/verify.py          # Verify next untested case
    python tests/eval/verify.py --reset  # Clear all results
"""

import json
import re
import sys
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


def find_current_case(cases: list[dict], results: list[dict]) -> dict | None:
    """Find the most recent case that was tested (last in results)."""
    if not results:
        # No results yet — return first case
        return cases[0] if cases else None

    tested_ids = {r["id"] for r in results}
    # Find the first untested case
    for case in cases:
        if case["id"] not in tested_ids:
            # This is the next to test, but we just ran the previous one
            break

    # The case we just ran is the last one in results
    last_result = results[-1]
    last_id = last_result["id"]
    for case in cases:
        if case["id"] == last_id:
            return case

    # If results exist but can't find matching case, use last result's case_id
    # to find next untested
    for case in cases:
        if case["id"] not in tested_ids:
            return case
    return None


def get_next_untested_case(cases: list[dict], results: list[dict]) -> dict | None:
    """Find the next case that hasn't been tested yet."""
    tested_ids = {r["id"] for r in results}
    for case in cases:
        if case["id"] not in tested_ids:
            return case
    return None


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

    result = {
        "id": case["id"],
        "prompt": case["prompt"],
        "category": case.get("category", "unknown"),
        "pass": passed,
        "expected": sorted(expected),
        "actual": sorted(actual_set),
    }
    if missing:
        result["missing"] = sorted(missing)

    results.append(result)
    save_results(results)

    # Print result
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] Case {case['id']}: {case['prompt'][:60]}...")
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
    else:
        verify()
