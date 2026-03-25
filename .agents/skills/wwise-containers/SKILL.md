---
name: wwise-containers
description: Configure Switch Containers, Blend Containers, State Groups, randomizers, attenuation curves, and Game Parameter ranges. Use for container-specific and type-specific configuration that goes beyond basic object properties.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise Containers (Type-Specific Configuration)

## Tools

- `add_wwise_switch_assignment` / `remove_wwise_switch_assignment` — Switch Container child-to-switch mapping
- `add_wwise_blend_assignment` / `remove_wwise_blend_assignment` — Blend Track child assignments with crossfade edges
- `set_wwise_state_groups` / `set_wwise_state_properties` — state configuration
- `set_wwise_randomizer` — randomizer on properties (Volume, Pitch, etc.)
- `set_wwise_attenuation_curve` — set attenuation curve points
- `set_wwise_game_parameter_range` — set RTPC min/max range

## Warnings

- `set_wwise_state_groups` and `set_wwise_state_properties` REPLACE ALL existing values. Include current values in the list to keep them.
- `set_wwise_game_parameter_range` modifies existing RTPC curves and blend tracks that use the Game Parameter.
