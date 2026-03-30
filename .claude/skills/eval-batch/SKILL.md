---
name: eval-batch
description: "[TEST ONLY] Run the next batch of MCP tool routing eval cases (up to 10). Works with /loop for full coverage."
user-invocable: true
---

This is a TEST/EVAL SKILL ONLY. Do NOT use for production MCP usage.
Runs up to 5 test cases per invocation, picking up where the last batch left off.

### Running all cases automatically

Use `/loop` to iterate through every test case unattended:

```
/loop 60s /eval-batch
```

Each iteration runs up to 5 cases. With 39 total cases, this finishes in ~8 iterations.
When all cases are tested the skill prints **"All cases evaluated"**, auto-generates the report, and tells you to stop the loop.

### How it differs from /eval-routing

- `/eval-routing` — 1 case per invocation (fine-grained, `/loop 30s`)
- `/eval-batch` — up to 5 cases per invocation (faster, `/loop 60s`)

Both pick up where they left off using `test_results.json`.

### Instructions

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

6. Determine the batch: take the next **5 untested cases** (or fewer if less than 5 remain).

7. For **each** case in the batch (in order by id):

   a. Clear `tests/eval/tool_log.jsonl` (write empty string to it)

   b. Handle the test case prompt as if a real user asked it:
      - The prompt is in the `"prompt"` field of the test case
      - Use MCP tools normally to fulfill the request
      - For write operations (create, delete, move), always clean up after:
        - Check if the case has a `"cleanup"` field in test_cases.json
        - If `cleanup.tool` is `"set_wwise_object_properties"`: restore the original value using
          `set_wwise_object_properties(operations=[{"object": cleanup.object, "properties": {cleanup.property: cleanup.restore_value}}])`
        - If `cleanup.tool` is `"set_wwise_object_name"`: rename back using
          `set_wwise_object_name(object=cleanup.object_after, value=cleanup.restore_name)`
        - If `cleanup.bulk_restore` exists: iterate and restore each entry
        - If no cleanup field: use your judgment (e.g., delete created objects)
      - Cases with `"expected_error": true` will have the tool fail at runtime — that's OK.
        The eval only checks routing (which tools were called), not whether they succeeded.

   c. After fulfilling the prompt, run: `python tests/eval/verify.py`

   d. Report the result (pass/fail and any tool mismatches).
      The progress counter is shown automatically: `[PASS] [15/39] Case 15: ...`

   e. Move to the next case in the batch immediately — do not stop between cases.

8. After the batch completes, print a summary line:
   `Batch done: X/Y cases tested so far (Z remaining)`

9. If all cases are now tested:
   - Run `python tests/eval/report.py` to generate the report inline
   - Print "All cases evaluated" and tell the user to stop the loop (`CronDelete <id>`)