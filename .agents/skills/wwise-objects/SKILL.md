---
name: wwise-objects
description: Create, delete, rename, move, copy Wwise objects. Set properties (Volume, Pitch, etc.) and references (OutputBus, Attenuation, Effects). Use for general object manipulation that applies to any Wwise object type.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise Objects (General Editing)

## Tools

- `create_wwise_object` — create objects with optional children and properties
- `delete_wwise_object` — delete an object and its children
- `set_wwise_object_name` / `set_wwise_object_notes` — rename or annotate
- `set_wwise_object_property` — set Volume, Pitch, Lowpass, etc.
- `set_wwise_object_reference` — set OutputBus, Attenuation, Effects, Conversion
- `move_wwise_object` / `copy_wwise_object` — reparent or duplicate

## When NOT to Use

For container-specific operations (switch assignments, blend tracks, state groups, randomizer, attenuation curves, game parameter ranges), use **wwise-containers** instead.
