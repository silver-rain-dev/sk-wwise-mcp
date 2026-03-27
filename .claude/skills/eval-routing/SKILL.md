---
name: eval-routing
description: "[TEST ONLY] Run the next MCP tool routing eval case. NOT for production use."
user-invocable: true
---

This is a TEST/EVAL SKILL ONLY. Do NOT use for production MCP usage.
This skill evaluates tool routing decisions one case at a time.

### Running all cases automatically

Use `/loop` to iterate through every test case unattended:

```
/loop 30s /eval-routing
```

This invokes `/eval-routing` every 30 seconds, advancing one case per iteration.
When all cases are tested the skill prints **"All cases evaluated"** — stop the loop at that point.

After the loop finishes, generate the report:

```
python tests/eval/report.py
```

### First run

Before the first `/eval-routing` (or `/loop`), always reset previous results:

```
python tests/eval/verify.py --reset
```

### Instructions (single case)

1. Read `tests/eval/test_cases.json` to get all test cases
2. Read `tests/eval/test_results.json` to find which cases have already been tested
   - If the file doesn't exist, no cases have been tested yet
3. Find the next case (by `id`) that has no entry in test_results
4. If all cases are tested, print "All cases evaluated" and stop

5. Clear `tests/eval/tool_log.jsonl` (write empty string to it)

6. Now handle the test case prompt as if a real user asked it:
   - The prompt is in the `"prompt"` field of the test case
   - Use MCP tools normally to fulfill the request
   - For write operations (create, delete, move), always clean up after
     (e.g., if you create an object, delete it when done)

7. After fulfilling the prompt, run: `python tests/eval/verify.py`

8. Report the result (pass/fail and any tool mismatches)
