---
name: eval-run
description: "[TEST ONLY] Run the full MCP eval pipeline: setup → run all cases → report → teardown."
user-invocable: true
---

Full MCP tool routing evaluation. Runs setup, all test cases, report, and teardown in one go.

Do NOT use for production. This creates a temporary Wwise project and tests tool routing.

### Test cases

Test prompts and expected tools are defined in `tests/eval/test_cases.json`. Each entry has:
- `id` — sequential case number
- `prompt` — the user prompt to execute
- `expected_tools` — list of tool names (without `mcp__sk-wwise-*__` prefix) that should be called
- `category` — browse, audition, generic, objects, media-read, or cross-server

Additional test prompt ideas (not yet in test_cases.json) are in `TEST_PROMPTS.md`.

### Phase 1: Setup

1. If `tests/eval/EvalTestProject/EvalTestProject.wproj` already exists, skip to step 4
2. Use `cli_create_new_project` to create a project at `tests/eval/EvalTestProject/EvalTestProject.wproj`
3. Use `cli_start_waapi_server` with that project (set `allow_migration` to true)
4. Wait 5 seconds, then ping Wwise to confirm connection
5. Create the test hierarchy under `\Containers\Default Work Unit`:
   - ActorMixer "EvalTest_SFX" with children:
     - RandomSequenceContainer "Footsteps" (Volume: -6) → Sound "Footstep_01", Sound "Footstep_02"
     - SwitchContainer "Weapons" → Sound "Sword_Hit", Sound "Bow_Shot"
     - ActorMixer "Ambience" → Sound "Forest_Loop", Sound "Wind_Loop"
6. Create Events under `\Events\Default Work Unit`:
   - Folder "EvalTest_Events" → Event "Play_Footstep", Event "Play_Sword", Event "Play_Ambience"
7. Create StateGroup "PlayerHealth" (States: Alive, Low, Dead) under `\States\Default Work Unit`
8. Create SwitchGroup "Surface" (Switches: Grass, Stone, Wood) under `\Switches\Default Work Unit`
9. Set Weapons SwitchContainer to use SwitchGroup "Surface"
10. Assign Sword_Hit → Grass, Bow_Shot → Stone

If any setup step fails, print the error and stop.

### Phase 2: Reset previous results

Run: `python tests/eval/verify.py --reset`

### Phase 3: Run all test cases

Read `tests/eval/test_cases.json` to get all cases.

For **each** case (in order by id):

1. Clear `tests/eval/tool_log.jsonl` (write empty string to it)
2. Execute the prompt in the `"prompt"` field as if a real user asked it:
   - Use MCP tools normally to fulfill the request
   - For write operations (create, delete, move, rename), always clean up after
     (e.g., if you create an object, delete it when done; if you rename, rename back)
3. Run: `python tests/eval/verify.py`
4. Print the result (pass/fail)
5. Move to the next case immediately — do not stop between cases

### Phase 4: Report

Run: `python tests/eval/report.py`

Print the full report output.

### Phase 5: Teardown

1. Read `tests/eval/setup_manifest.json` to get the WAAPI server PID
2. Kill the headless WAAPI server process:
   - On Windows: `taskkill /PID <pid> /F`
   - On Mac/Linux: `kill <pid>`
3. Wait 2 seconds
4. Delete `tests/eval/EvalTestProject/` directory
5. Delete `tests/eval/setup_manifest.json`
6. Print "Eval complete"
