---
name: wwise-audition
description: Preview and audition Wwise sounds using transport objects. Use when the user wants to play, stop, or pause audio in the Wwise authoring tool.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise Audition (Playback)

## Tools

- `create_wwise_transport` — create transport for an object (auto-prepares for instant playback)
- `execute_wwise_transport_action` — play, stop, pause, playStop, playDirectly
- `list_wwise_transports` — list active transports
- `destroy_wwise_transport` — clean up transport

## Notes

- Transports persist until destroyed or Wwise closes — no need to actively clean up.
- Omitting transport_id in `execute_wwise_transport_action` applies the action to ALL transports.
