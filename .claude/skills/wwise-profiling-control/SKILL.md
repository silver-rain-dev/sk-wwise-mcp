---
name: wwise-profiling-control
description: Control profiler capture — start/stop capture, save to .prof files, enable data types, register meters for bus monitoring, navigate the profiler timeline. Use before reading profiler data.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise Profiling Control

## Tools

- `enable_wwise_profiler_data` — enable/disable specific data types for capture
- `start_profiler_capture` / `stop_profiler_capture` — control capture
- `save_profiler_capture` — save to .prof file
- `register_profiler_meter` / `unregister_profiler_meter` — register busses for meter data
- `set_profiler_cursor` — move cursor (first/last/next/previous or specific time in ms)

## Notes

- Every `register_profiler_meter` must have a matching `unregister_profiler_meter`.
- Only the Main Audio Bus is registered for meters by default.
