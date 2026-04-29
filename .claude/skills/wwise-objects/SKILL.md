---
name: wwise-objects
description: Create, delete, rename, move, copy Wwise objects. Set properties (Volume, Pitch, etc.) and references (OutputBus, Attenuation, Effects). Use for general object manipulation that applies to any Wwise object type.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise Objects (General Editing)

## Tools

- `create_wwise_objects` — create one or more objects (batch), with optional children and properties
- `delete_wwise_objects` — delete one or more objects (batch) and their children
- `set_wwise_object_name` / `set_wwise_object_notes` — rename or annotate
- `set_wwise_object_properties` — set properties AND/OR references on one or more objects (batch). Replaces separate property/reference tools.
- `move_wwise_objects` — move one or more objects to new parents (batch)
- `copy_wwise_object` — duplicate an object to a new parent

## Batch Guidance

All batch tools accept a list — use a single-entry list for single operations.
Prefer setting properties at creation time via `@Property` keys in `children` dicts
when possible, to avoid post-creation property calls.

## Short Name / Default Parent Support

Three batch tools support optional context parameters to reduce token usage:

- **`create_wwise_objects`** — `default_parent`: shared parent for all objects. Individual entries can omit `parent`.
- **`set_wwise_object_properties`** — `parent`: resolves short names in `object` fields by querying the parent's children.
- **`move_wwise_objects`** — `source_parent` (resolves short names in `object`) + `new_parent` (default destination, entries can omit `parent`).

When a context parameter is set, object references can use **short names** (e.g. `"Footstep_01"`) instead of full paths. Full paths/GUIDs still work alongside short names.

Example — set volume on 3 siblings:
```json
{
  "parent": "\\Actor-Mixer Hierarchy\\Default Work Unit\\SFX\\Footsteps",
  "operations": [
    {"object": "Step_01", "properties": {"Volume": -6}},
    {"object": "Step_02", "properties": {"Volume": -6}},
    {"object": "Step_03", "properties": {"Volume": -6}}
  ]
}
```

## Event Actions

Use `create_wwise_objects` to add Actions to Events:
- `type`: `"Action"`
- `parent`: the Event (path, GUID, or `"Event:Play_Sound_01"`)
- `properties`: `{"ActionType": 1}` — values: 1=Play, 2=Stop, 3=Pause, 4=Resume, etc.
- `list_name`: `"actions"` (inserts into the Event's action list)
- After creation, set the `Target` reference via `set_wwise_object_properties` to point at the playable object

Example:
```json
[{
  "parent": "Event:Play_Gunshot",
  "type": "Action",
  "name": "",
  "on_name_conflict": "rename",
  "list_name": "actions",
  "properties": {"ActionType": 1}
}]
```
Then set the target:
```json
[{"object": "<action GUID>", "references": {"Target": "\\Actor-Mixer Hierarchy\\...\\Gunshot"}}]
```

**Valid Action targets** must be playable objects: Sound, ActorMixer, RandomSequenceContainer, SwitchContainer, BlendContainer, MusicSwitchContainer, MusicPlaylistContainer, MusicSegment, etc. Virtual folders (PropertyContainer/WorkUnit) **cannot** be targeted — WAAPI silently ignores the reference.

## When NOT to Use

For container-specific operations (switch assignments, blend tracks, state groups, randomizer, attenuation curves, game parameter ranges), use **wwise-containers** instead.
