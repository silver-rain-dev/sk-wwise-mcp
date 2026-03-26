---
name: eval-teardown
description: "[TEST ONLY] Tear down the eval test environment. Stops headless WAAPI and deletes the test project."
disable-model-invocation: true
---

⚠️ TEST TEARDOWN ONLY.

### Instructions

1. Read `tests/eval/setup_manifest.json` to get the WAAPI server PID and project path
2. Kill the headless WAAPI server process using the PID from the manifest
   - On Windows: `taskkill /PID <pid> /F`
   - On Mac/Linux: `kill <pid>`
3. Wait 2 seconds for process to terminate
4. Delete the test project directory (`tests/eval/EvalTestProject/`)
5. Delete `tests/eval/setup_manifest.json`
6. Delete `tests/eval/test_results.json` (if it exists)
7. Delete `tests/eval/tool_log.jsonl` (if it exists)
8. Delete `tests/eval/picks.txt` (if it exists)
9. Print "Teardown complete"
