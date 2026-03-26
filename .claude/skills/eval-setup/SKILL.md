---
name: eval-setup
description: "[TEST ONLY] Set up a Wwise test project with known objects for eval runs."
disable-model-invocation: true
---

⚠️ TEST SETUP ONLY. Do NOT use for production.
This creates a throwaway Wwise project and populates it with test objects.

Execute these steps in order using MCP tools. Stop if any step fails.

### Step 1: Create test project and start headless WAAPI

1. Use `cli_create_new_project` to create a fresh project at `tests/eval/EvalTestProject/EvalTestProject.wproj`
2. Use `cli_start_waapi_server` to launch a headless WAAPI server with that project
3. Wait 5 seconds, then ping Wwise to confirm connection
4. Get project info to verify the project loaded

### Step 2: Create Actor-Mixer hierarchy

Under `\Containers\Default Work Unit`, create:

- ActorMixer "EvalTest_SFX"
  - RandomSequenceContainer "Footsteps" (set Volume to -6.0)
    - Sound "Footstep_01"
    - Sound "Footstep_02"
  - SwitchContainer "Weapons"
    - Sound "Sword_Hit"
    - Sound "Bow_Shot"
  - ActorMixer "Ambience"
    - Sound "Forest_Loop"
    - Sound "Wind_Loop"

### Step 3: Create Events

Under `\Events\Default Work Unit`, create:

- Folder "EvalTest_Events"
  - Event "Play_Footstep"
  - Event "Play_Sword"
  - Event "Play_Ambience"

### Step 4: Create States and Switches

- Under `\States\Default Work Unit`: StateGroup "PlayerHealth" with States: "Alive", "Low", "Dead"
- Under `\Switches\Default Work Unit`: SwitchGroup "Surface" with Switches: "Grass", "Stone", "Wood"

### Step 5: Set references

- Set Weapons SwitchContainer to use SwitchGroup "Surface"
- Assign Sword_Hit to "Grass" switch
- Assign Bow_Shot to "Stone" switch

### Step 6: Write setup manifest

Write the WAAPI server PID, project path, and created object paths to `tests/eval/setup_manifest.json`:

```json
{
  "project_path": "tests/eval/EvalTestProject/EvalTestProject.wproj",
  "waapi_pid": <PID from cli_start_waapi_server>,
  "objects": {
    "actor_mixer": "\\Containers\\Default Work Unit\\EvalTest_SFX",
    "footsteps": "\\Containers\\Default Work Unit\\EvalTest_SFX\\Footsteps",
    "weapons": "\\Containers\\Default Work Unit\\EvalTest_SFX\\Weapons",
    "events_folder": "\\Events\\Default Work Unit\\EvalTest_Events"
  }
}
```

Print "Setup complete" when done.
