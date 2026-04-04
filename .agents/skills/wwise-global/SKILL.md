---
name: wwise-global
description: Global rules and best practices for all Wwise MCP operations. Always load this alongside any other wwise-* skill when working with a Wwise project.
compatibility: Requires Wwise with WAAPI enabled for most servers. mcp_command_line works without WAAPI.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise MCP Global Rules

## Always Follow These Rules

- Never use edit servers (objects, containers, pipeline) for read-only tasks — use browse
- Always query before editing — confirm the object exists and check its current state
- When `get_wwise_object_info` results are large, read the saved `output_file` — the preview only shows 10 items
- For bulk operations (50+ objects), warn the user before proceeding
- Use `mcp_generic` as a last resort only — check specialized servers first
- Clean up temporary files (JSON, TSV, Python scripts) created for batch operations after the operation completes successfully
- `mcp_command_line` works without WAAPI — use it when Wwise is not running
- Profiler data requires `enable_wwise_profiler_data` to be called first for most data types

## WAAPI Gotchas

### Root Path Queries Return Empty
**Never use `from_path: ["\\"]`** (the absolute root) in object queries — WAAPI returns 0 results. Always query from specific hierarchy roots: `["\\Containers"]`, `["\\Events"]`, `["\\Master-Mixer Hierarchy"]`, `["\\Actor-Mixer Hierarchy"]`, etc. If a query returns 0 results, try a different `from_path` before concluding the project is empty.

### Output Bus Inheritance
When querying `@OutputBus` on a Wwise object, WAAPI returns the LOCAL value, not the effective (inherited) one. If `@OverrideOutput` is false, the object inherits its output bus from an ancestor. To find the actual routing, walk the ancestor chain (using `select_transform="ancestors"`) and find the nearest ancestor where `@OutputBus` is set. Always check `@OverrideOutput`.

### Audio Import Requires WAV
WAAPI's audio import (`import_audio_files`, `import_tab_delimited_file`) only creates AudioFileSource objects for **WAV** files. Other formats (OGG, FLAC, MP3) get copied to the Originals folder but are **not linked** to their Sound objects — the import silently succeeds with no AudioFileSource created. If source audio is not WAV, convert to WAV first (e.g. via ffmpeg) before importing.

### Event Action Targets Must Be Playable
When setting the `Target` reference on an Action, the target must be a playable object type (Sound, ActorMixer, RandomSequenceContainer, SwitchContainer, BlendContainer, MusicSwitchContainer, MusicPlaylistContainer, MusicSegment). Virtual folders (`PropertyContainer`) and Work Units **cannot** be Action targets — WAAPI silently ignores the `setReference` call with no error.

## Common Workflows

### Find and Fix
1. **wwise-browse** — query objects to find the issue
2. **wwise-objects** — apply the fix
3. **wwise-browse** — verify the change

### Import and Configure
1. **wwise-pipeline** — `import_audio_files` to import audio
2. **wwise-objects** — create containers, set properties, assign busses
3. **wwise-containers** — set up switch assignments, state groups
4. **wwise-objects** — create Events
5. **wwise-objects** — create Actions under Events (`type: "Action"`, set ActionType + Target reference)
6. **wwise-pipeline** — add to SoundBank and generate

### Audition
1. **wwise-audition** — `create_wwise_transport` (auto-prepares)
2. **wwise-audition** — `execute_wwise_transport_action("play")`
3. **wwise-audition** — `execute_wwise_transport_action("stop")` when done

### Profile a Game Session
1. **wwise-remote** — `get_available_remote_consoles` then `connect_to_remote`
2. **wwise-profiling-control** — `enable_wwise_profiler_data` for desired data types
3. **wwise-profiling-control** — `start_profiler_capture`
4. **wwise-profiling** — query data (voices, CPU, busses, etc.)
5. **wwise-profiling-control** — `stop_profiler_capture`, optionally `save_profiler_capture`
6. **wwise-remote** — `disconnect_from_remote`

### Create Project from Scratch
1. **wwise-command-line** — `cli_create_new_project`
2. **wwise-ui** — `open_project`
3. **wwise-objects** — build hierarchy
4. **wwise-pipeline** — import audio, generate SoundBanks

### Set Up Project from GDD + Audio Assets
1. Read the GDD (file read)
2. Scan the audio folder (Glob/Bash)
3. **wwise-objects** — create hierarchy based on GDD structure
4. **wwise-pipeline** — `import_audio_files` to link audio to objects
5. **wwise-containers** — set up switches, states, blend tracks
6. **wwise-objects** — create Events, set references (busses, attenuations)
7. **wwise-objects** — create Actions under Events (set ActionType + Target)
8. **wwise-pipeline** — create SoundBanks, set inclusions, generate
9. **wwise-audition** — preview results

## Server Overview

| Server | Skills Name | Tools | Purpose |
|--------|-------------|-------|---------|
| mcp_browse | wwise-browse | 14 | Read-only project inspection |
| mcp_objects | wwise-objects | 8 | Object CRUD, properties, references |
| mcp_containers | wwise-containers | 9 | Container-specific configuration |
| mcp_pipeline | wwise-pipeline | 9 | Import, SoundBanks, save, logs |
| mcp_audition | wwise-audition | 4 | Transport playback |
| mcp_media_read | wwise-media-read | 3 | Audio analysis, Media Pool |
| mcp_ui | wwise-ui | 13 | Wwise UI automation |
| mcp_profiling | wwise-profiling | 12 | Read-only profiler data |
| mcp_profiling_control | wwise-profiling-control | 7 | Profiler control |
| mcp_remote | wwise-remote | 4 | Remote connection |
| mcp_command_line | wwise-command-line | 9 | WwiseConsole CLI (no WAAPI) |
| mcp_generic | wwise-generic | 3 | Fallback WAAPI passthrough |
