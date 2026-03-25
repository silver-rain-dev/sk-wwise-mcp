---
name: wwise-pipeline
description: Import audio files, manage SoundBanks (inclusions, generation, definitions), convert external sources, save the project, and check logs. Use for asset pipeline and build operations.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise Pipeline (Import, Build, Save)

## Tools

- `import_audio_files` — import audio and create Wwise objects
- `import_tab_delimited_file` — batch import from tab-delimited file
- `set_wwise_soundbank_inclusions` / `get_wwise_soundbank_inclusions` — manage SoundBank contents
- `generate_wwise_soundbanks` — generate SoundBanks
- `process_wwise_soundbank_definitions` — import SoundBank definition files
- `convert_wwise_external_sources` — convert external sources
- `save_wwise_project` — save the project
- `get_wwise_log` — check logs after operations (channels: soundbankGenerate, conversion, waapi, general, etc.)

## Tips

- After import or generation, use `get_wwise_log` to check for errors/warnings.
- `import_audio_files` does not return errors for individual failures — check the Wwise log.
