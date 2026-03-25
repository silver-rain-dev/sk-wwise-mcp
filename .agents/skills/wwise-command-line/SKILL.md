---
name: wwise-command-line
description: Headless Wwise operations via WwiseConsole CLI — create projects, migrate, verify, generate SoundBanks, import, convert external sources, start WAAPI server. Does NOT require WAAPI or Wwise to be running. Use for CI/CD, project creation, or when Wwise is closed.
compatibility: Requires WwiseConsole.exe. Set WWISEROOT environment variable or add to PATH.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise Command Line (No WAAPI Needed)

## Tools

- `cli_create_new_project` — create a blank Wwise project
- `cli_verify_project` — load and verify without saving
- `cli_migrate_project` — migrate to current Wwise version
- `cli_tab_delimited_import` — import from tab-delimited file
- `cli_convert_external_sources` — convert external sources
- `cli_move_media_ids` / `cli_move_media_ids_to_work_units` / `cli_update_media_ids` — media ID management
- `cli_start_waapi_server` — start headless WAAPI server (returns PID)

## Key Difference

This server shells out to WwiseConsole.exe directly — no WAAPI connection needed. Use it when Wwise is not running or for headless/CI workflows.
