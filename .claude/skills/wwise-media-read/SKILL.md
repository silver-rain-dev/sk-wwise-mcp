---
name: wwise-media-read
description: Analyze audio source waveform peaks and search the Wwise Media Pool. Use when inspecting audio content, checking loudness, or finding media files. Read-only.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise Media Read (Audio Analysis, Read-Only)

## Tools

- `get_audio_source_peaks` — waveform peak data (specify time range, or omit for trimmed region)
- `query_media_pool` — search/filter media files (fuzzy search, field filters, audio similarity)
- `get_media_pool_fields` — discover available Media Pool fields for filtering
