---
name: wwise-pipeline
description: Import audio files, manage SoundBanks (inclusions, generation, definitions), convert external sources, save the project, and check logs. Use for asset pipeline and build operations.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise Pipeline (Import, Build, Save)

## Tools

- `import_audio_files` — import audio and create Wwise objects (per-file entries)
- `import_audio_directory` — scan a WAV directory, auto-match to existing Wwise objects, and import (most token-efficient)
- `import_tab_delimited_file` — batch import from tab-delimited file
- `convert_audio_to_wav` — convert non-WAV audio (OGG, FLAC, MP3) to WAV using ffmpeg
- `generate_tab_delimited_file` — generate a Wwise-compatible TSV file from structured data
- `set_wwise_soundbank_inclusions` / `get_wwise_soundbank_inclusions` — manage SoundBank contents
- `generate_wwise_soundbanks` — generate SoundBanks
- `process_wwise_soundbank_definitions` — import SoundBank definition files
- `convert_wwise_external_sources` — convert external sources
- `save_wwise_project` — save the project
- `get_wwise_log` — check logs after operations (channels: soundbankGenerate, conversion, waapi, general, etc.)

## Audio Import Rules

### WAV only
WAAPI import only creates AudioFileSource links for **WAV** files. OGG, FLAC, and MP3 get silently
copied to Originals but are never linked to the Sound object. Always convert to WAV before importing.

### SFX vs Voice
The `importLanguage` parameter controls where files are stored and how Sound objects are typed:

| importLanguage | Originals path | Sound type | Use for |
|---|---|---|---|
| `"SFX"` | `Originals/SFX/` | Sound SFX | Music, SFX, ambience, jingles — anything not localized |
| `"English(US)"` etc. | `Originals/Voices/<lang>/` | Sound Voice | Dialogue, VO — content that varies by language |

Use `<Sound SFX>` or `<Sound Voice>` type prefixes in objectPath to match.

### Organizing with originalsSubFolder
Use `originalsSubFolder` to keep files organized within `Originals/SFX/` or `Originals/Voices/`:
- `"Music"` → `Originals/SFX/Music/`
- `"Cries"` → `Originals/SFX/Cries/`
- `"Weapons"` → `Originals/SFX/Weapons/`

### objectPath format
Import tools expect `\Actor-Mixer Hierarchy\...` paths (not `\Containers\...`):
- `\Actor-Mixer Hierarchy\Default Work Unit\<Sound SFX>MySound` ✓
- `\Containers\Default Work Unit\<Sound SFX>MySound` ✗ (won't link audio)

## Bulk Import Strategy

Choose the right tool based on scale:

| Scenario | Tool | Token cost |
|---|---|---|
| 1-49 files, known paths | `import_audio_files` | Medium (per-file entries) |
| 50+ files, known paths | `generate_tab_delimited_file` → `import_tab_delimited_file` | Low (TSV file) |
| Directory of WAVs matching existing objects | `import_audio_directory` | Minimal (one call) |
| Non-WAV source audio | `convert_audio_to_wav` first, then import | One extra call |

**`import_audio_directory`** is the most efficient: pass a directory path and a Wwise parent, it auto-matches WAV filenames to child objects by name. Handles both Sound objects (exact match) and RandomSequenceContainers (base name + digit variants).

## Tips

- After import or generation, use `get_wwise_log` to check for errors/warnings.
- `import_audio_files` does not return errors for individual failures — check the Wwise log.
- `import_audio_files` rejects non-WAV files with a clear error before calling WAAPI.
- Set `importLanguage` in the `default` dict to avoid repeating it per entry.
