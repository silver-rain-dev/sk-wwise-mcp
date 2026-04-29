---
name: wwise-browse
description: Read-only Wwise project inspection. Use when querying objects, counting, searching, inspecting properties, comparing objects, checking platform linking, or verifying connectivity. Never modifies the project.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise Browse (Read-Only)

## Tools

- `ping_wwise` — check WAAPI connectivity
- `get_wwise_installation_info` / `get_wwise_project_info` — version and project metadata
- `build_object_info_query` + `get_wwise_object_info` — query objects (always build first, then execute)
- `get_wwise_object_types` — discover valid object types and classIds
- `get_property_and_reference_names` — discover properties/references for an object
- `get_wwise_property_info` — get property type, min/max, default value
- `get_wwise_attenuation_curve` — read attenuation curve points
- `diff_wwise_objects` — compare two objects for property differences
- `is_wwise_property_linked` / `is_wwise_property_enabled` — platform-specific checks
- `get_switch_container_assignments` / `get_blend_track_assignments` — container assignment queries

## Important Notes

- `get_wwise_object_info` returns only a 10-item preview. Read the `output_file` path for complete results.
- Always use `build_object_info_query()` before `get_wwise_object_info()` — do not hand-craft the query dict.
- `@OutputBus` returns the LOCAL value, not inherited. Check `@OverrideOutput` and walk ancestors if needed.

## Query Path Gotcha

**NEVER query from the absolute root path `["\\"]`** — WAAPI returns 0 results when querying from root.
Always use specific hierarchy paths in `from_path`:
- `["\\Containers"]` — for RandomSequenceContainers, SwitchContainers, BlendContainers, Sounds
- `["\\Events"]` — for Events
- `["\\Master-Mixer Hierarchy"]` — for Busses
- `["\\Actor-Mixer Hierarchy"]` — same objects as Containers but via the Actor-Mixer view
- `["\\SoundBanks"]`, `["\\Switches"]`, `["\\States"]`, `["\\Game Parameters"]`, etc.

If a query returns 0 results, try a different `from_path` before concluding objects don't exist.
