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
When all cases are tested the skill prints **"All cases evaluated"**, auto-generates the report, and tells you to stop the loop.

### Instructions (single case)

1. Read `tests/eval/test_cases.json` to get all test cases
2. Read `tests/eval/test_results.json` to find which cases have already been tested
   - If the file doesn't exist, no cases have been tested yet
3. **Stale-result guard**: If ALL cases already have results, auto-reset by running:
   `python tests/eval/verify.py --check-stale`
   This will detect stale results (from a prior session) and reset automatically.
   Then re-read `test_results.json` (it will now be empty).
4. Find the next case (by `id`) that has no entry in test_results
5. If all cases are tested:
   - Run `python tests/eval/report.py` to generate the report inline
   - Print "All cases evaluated" and tell the user to stop the loop (`CronDelete <id>`)
   - Stop — do not run any more cases

6. Clear `tests/eval/tool_log.jsonl` (write empty string to it)

7. Now handle the test case prompt as if a real user asked it:
   - The prompt is in the `"prompt"` field of the test case
   - Use MCP tools normally to fulfill the request
   - For write operations (create, delete, move), always clean up after:
     - Check if the case has a `"cleanup"` field in test_cases.json
     - If `cleanup.tool` is `"set_wwise_object_property"`: restore the original value using
       `set_wwise_object_property(object=cleanup.object, property=cleanup.property, value=cleanup.restore_value)`
     - If `cleanup.tool` is `"set_wwise_object_name"`: rename back using
       `set_wwise_object_name(object=cleanup.object_after, value=cleanup.restore_name)`
     - If `cleanup.bulk_restore` exists: iterate and restore each entry
     - If no cleanup field: use your judgment (e.g., delete created objects)
   - Cases with `"expected_error": true` will have the tool fail at runtime — that's OK.
     The eval only checks routing (which tools were called), not whether they succeeded.

8. After fulfilling the prompt, run: `python tests/eval/verify.py`

9. Report the result (pass/fail and any tool mismatches).
   The progress counter is shown automatically: `[PASS] [15/39] Case 15: ...`
