---
name: wwise-profiling
description: Read profiler data — voices, busses, CPU usage, meters, RTPCs, game objects, loaded media, streams, audio objects, performance counters. Use when analyzing runtime performance or inspecting profiler captures. Read-only.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise Profiling (Read-Only Data)

## Tools

- `get_profiler_voices` — playing voices with volume, priority, virtual status
- `get_profiler_voice_contributions` — detailed voice parameter breakdown (Voice Inspector)
- `get_profiler_busses` — bus instances with volume, voice count
- `get_profiler_audio_objects` — Audio Objects with position, channel config
- `get_profiler_cpu_usage` — CPU stats per element (codec, effect, mixer)
- `get_profiler_performance_monitor` — all performance counters
- `get_profiler_meters` — bus/device meter data (register meters first via wwise-profiling-control)
- `get_profiler_rtpcs` — active Game Parameters, LFOs, Envelopes
- `get_profiler_loaded_media` / `get_profiler_streamed_media` — media info
- `get_profiler_game_objects` — registered game objects
- `get_profiler_cursor_time` — current profiler cursor position

## Prerequisites

Most data requires `enable_wwise_profiler_data` (from wwise-profiling-control) to be called first. Meter data requires `register_profiler_meter` on the target bus.
