---
name: wwise-containers
description: Configure Switch Containers, Blend Containers, State Groups, randomizers, attenuation curves, and Game Parameter ranges. Use for container-specific and type-specific configuration that goes beyond basic object properties.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise Containers (Type-Specific Configuration)

## Tools

- `add_wwise_switch_assignments` / `remove_wwise_switch_assignments` — Switch Container child-to-switch mapping (batch)
- `add_wwise_blend_assignment` / `remove_wwise_blend_assignment` — Blend Track child assignments with crossfade edges
- `set_wwise_state_groups` / `set_wwise_state_properties` — state configuration
- `set_wwise_randomizer` — randomizer on properties (Volume, Pitch, etc.)
- `set_wwise_attenuation_curve` — set attenuation curve points
- `set_wwise_game_parameter_range` — set RTPC min/max range

## Short Name Resolution for Switch Assignments

`add_wwise_switch_assignments` and `remove_wwise_switch_assignments` support a `container` parameter.
When provided, `child` and `state_or_switch` can be **short names** instead of full paths:

```json
{
  "container": "\\Actor-Mixer Hierarchy\\Default Work Unit\\SFX\\SFX_Moves",
  "assignments": [
    {"child": "Absorb", "state_or_switch": "Absorb"},
    {"child": "Acid", "state_or_switch": "Acid"}
  ]
}
```

The tool queries the container's children and its switch group's switches to resolve names to paths.
Full paths and GUIDs still work alongside short names. Use this for bulk assignments to reduce token usage.

## Warnings

- `set_wwise_state_groups` and `set_wwise_state_properties` REPLACE ALL existing values. Include current values in the list to keep them.
- `set_wwise_game_parameter_range` modifies existing RTPC curves and blend tracks that use the Game Parameter.
