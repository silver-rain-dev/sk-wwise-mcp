- [2026-10-03, wave 2, issue #6] Bundle generator entry point is `release/build_mcpb.py`. CLI: `python release/build_mcpb.py [--exe dist/sk-wwise-mcp.exe] [--out sk-wwise-mcp.mcpb] [--version X]`. From Python (put `release/` on `sys.path`): `build_mcpb(exe_path, out_path, version=None) -> Path`, `build_manifest(version=None) -> dict`, `resolve_mcp_config(manifest, install_dir, user_config)` (mimics host substitution, used in tests).
  - Why: #7 (plugin zip) and #8 (release CI) can call it without re-deriving the manifest. Stdlib only, no node needed.
  - Output: `<repo root>/sk-wwise-mcp.mcpb` (default), next to `sk-wwise-mcp.zip`; gitignored. It is a zip: `manifest.json`, `server/sk-wwise-mcp.exe`, `LICENSE`. Version comes from `pyproject.toml` unless `--version` is passed (CI can pass the tag).
  - Affects: #7 embeds `sk-wwise-mcp.mcpb` in the plugin zip; #8 runs `build.ps1` (or calls the script after PyInstaller) and uploads the `.mcpb` as a release asset.

- [2026-10-03, wave 2, issue #6] `build.ps1` step 9 runs the script, then runs `npx --yes @anthropic-ai/mcpb validate` on the extracted manifest if `npx` is on PATH (skips with a note otherwise; a validation failure fails the build). The legacy zip step is unchanged and does not include the `.mcpb`.
  - Why: official validator when available; unit tests do not need it.
  - Affects: #8 (CI runner needs node for the extra check, or it is skipped). Verified locally: full `build.ps1` run gives exe 27.7 MB, `.mcpb` 27.4 MB, official validate passes.

- [2026-10-03, wave 2, issue #6] Manifest schema is vendored at `release/schema/mcpb-manifest-v0.3.schema.json` (source URL and commit in `release/schema/SOURCE.txt`; mcpb main 70fe3b3, CLI 2.1.2). `manifest_version` is `"0.3"` (the mcpb CLI default; `latest.schema.json` is the same file). Tests in `tests/unit/test_mcpb_manifest.py` validate with `jsonschema` (already in the venv as a transitive dep of fastmcp; not added to `pyproject.toml`).
  - Why: schema check without network or node.
  - Affects: #7 can reuse the same validator pattern for `plugin.json`/`marketplace.json`.

- [2026-10-03, wave 2, issue #6] MCPB `user_config` has no enum type (string, number, boolean, directory, file only). `profile` is a required string, default `author`, with the valid names in its description (built from `PROFILE_NAMES`). The exe is the validator: unknown or empty profile exits non-zero with the valid names. `build_mcpb.profile_names(manifest)` reads the names back for the table-equality test.
  - Why: the spec cannot constrain the field in the UI.
  - Affects: #5/#7 docs should not promise a dropdown.

- [2026-10-03, wave 2, issue #6] Manifest wiring: `command` `${__dirname}/server/sk-wwise-mcp.exe`, `args` `["--profile", "${user_config.profile}"]`, `env` `SK_WWISE_WAAPI_URL=${user_config.waapi_url}`, `SK_WWISE_CONSOLE=${user_config.wwise_console}`. `waapi_url` has default `ws://127.0.0.1:8080/waapi`; `wwise_console` has no default. The reference mcpb host (`src/shared/config.ts`) leaves a variable with no value as the literal `${user_config.<key>}` text, so the exe now treats that placeholder as unset: new `core/env_setting.read_env_setting(name)` is used by `resolve_waapi_url()` and `resolve_wwise_cli()` (empty, whitespace and placeholder all mean unset).
  - Why: an unset optional must not reach the exe as a bogus value.
  - Affects: any new env-var setting should read through `read_env_setting`.
