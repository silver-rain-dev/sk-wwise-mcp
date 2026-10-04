# SK Wwise MCP

MCP servers that let Claude browse and interact with Wwise via the Wwise Authoring API (WAAPI).

## Quick start

1. **Unzip / copy** this folder anywhere on disk.
2. **Make sure Wwise is running** with the Authoring API enabled (Project Settings → Authoring API → "Enable Wwise Authoring API"). `sk-wwise-mcp.exe --server command-line` works headlessly without Wwise.
3. **Open a terminal in this folder** and run:
   ```
   claude
   ```
   Claude CLI auto-detects `.mcp.json` (registers the server) and `.claude/skills/` (loads routing guidance) on launch.
4. **Allow the MCP server** when Claude prompts you (one-time).

That's it. Try: *"Ping Wwise"* or *"List all events in my project"*.

> **Using a different agent?** This is a plain MCP server — any MCP-capable host (Claude Desktop, VS Code Copilot, Cursor, Windsurf, …) works. The steps above are written for Claude because that's the config shipped here (`.mcp.json`). For another host, register the same `sk-wwise-mcp.exe` per that host's MCP setup docs — or simply **ask your agent to register the MCP server in this folder** and let it wire up its own config from the included `.mcp.json`.

## What's in this folder

| Path | Purpose |
| --- | --- |
| `sk-wwise-mcp.exe` | Single binary that hosts all 12 servers. With no flag it mounts every server in one process; `--server <name>` exposes just one. |
| `.mcp.json` | MCP host registry — a single entry, no flag, so one exe process mounts all 12 servers. Relative path, so the folder is safe to move. |
| `.mcp.per-server.json` | Alternate registry: 12 entries, one `--server <name>` each. Rename to `.mcp.json` to use it. |
| `.vscode/mcp.json` | Same registry for VS Code Copilot (`.vscode/mcp.per-server.json` is the per-server variant). |
| `.claude/skills/` | Routing skills — short docs that teach Claude which MCP tool fits which task. Loaded automatically. |

### One process vs per-server

The default `.mcp.json` mounts **every server in a single process** (one entry, no flag) — fewest permission prompts, simplest setup. All ~80+ tools share one server.

`.mcp.per-server.json` registers **one MCP server per `--server`** (12 entries). Each server's tool set stays small, which improves Claude's tool-routing accuracy and lets you scope access per role (see below). To switch, replace `.mcp.json` with the contents of `.mcp.per-server.json`.

## Requirements

- **Windows 10 / 11** (this build is Windows-only).
- **Wwise 2022 or later** with WAAPI enabled (for everything except `--server command-line`).
- **An MCP-capable host** — Claude Code, Claude Desktop, VS Code Copilot, Cursor, Windsurf, or any other agent that supports MCP. For Claude Code: `npm install -g @anthropic-ai/claude-code`. (Config for Claude and VS Code Copilot ships in this folder; other hosts register the exe per their own MCP docs — see the note under Quick start.)

### Custom WAAPI URL

The WAAPI servers connect to `ws://127.0.0.1:8080/waapi` by default. If your Wwise Authoring API listens on another port or host, set `SK_WWISE_WAAPI_URL` before launching `claude`:

```
set SK_WWISE_WAAPI_URL=ws://127.0.0.1:9090/waapi
```

- Unset, empty or whitespace-only means the default URL.
- It applies to every server (they share one connection layer).
- If the connection fails, the error message names the URL that was tried.
- This is separate from `wamp_port` in `cli_start_waapi_server`, which sets the port a headless WwiseConsole listens on.

### Multiple Wwise versions installed?

The `command-line` server (WwiseConsole) auto-picks the **newest 2022+ install** under `Program Files\Audiokinetic`. To pin a specific version, set `SK_WWISE_CONSOLE` to the full path of that version's `WwiseConsole.exe` before launching `claude`:

```
set SK_WWISE_CONSOLE=C:\Program Files\Audiokinetic\Wwise 2023.1.3.8471\Authoring\x64\Release\bin\WwiseConsole.exe
```

Ask Claude to *"run cli_diagnostics"* to see which console was picked and every version it found. The WAAPI servers always talk to whichever Wwise instance is **running** — *"get the Wwise installation info"* reports that version and whether it's supported.

## Role-based access (profiles)

Want a sound designer to only browse and audition, not delete anything? Run the exe with a **profile**: `sk-wwise-mcp.exe --profile listen`. Only that profile's servers load, so the other tools physically don't exist in Claude's context — no prompt-engineered guardrails to circumvent. `--profile` cannot be combined with `--server`. `--server a,b` still mounts an exact list.

| Profile | Servers (`--profile <name>`) |
|---|---|
| `listen` | `browse`, `audition`, `media-read` |
| `author` | `browse`, `audition`, `media-read`, `objects`, `containers`, `pipeline`, `ui` |
| `build` | `browse`, `audition`, `media-read`, `objects`, `containers`, `pipeline`, `ui`, `command-line` |
| `qa` | `browse`, `audition`, `profiling`, `profiling-control`, `remote` |
| `admin` | `browse`, `audition`, `media-read`, `objects`, `containers`, `pipeline`, `ui`, `command-line`, `generic`, `profiling`, `profiling-control`, `remote` |

`author` is the default profile for the plugin. `build` is `author` plus `command-line`. `admin` is all 12 servers. The old role names are renamed: `viewer` and `designer` are now `listen`; `editor` is now `author`.

## Bundle (`sk-wwise-mcp.mcpb`)

`build.ps1` also writes `sk-wwise-mcp.mcpb` next to `sk-wwise-mcp.zip`. It is an MCP Bundle: the exe, a generated `manifest.json` and three install-time settings. Double-click it in Claude Desktop to install. No Python or terminal is needed.

Settings (`user_config` in the manifest):

- **`profile`** — required, default `author`. Passed to the exe as `--profile <value>`. The valid names are the profile table above. MCPB settings have no enum type, so this is a text field and the exe checks the value: an unknown or empty profile exits with an error that lists the valid names.
- **`waapi_url`** — optional, default `ws://127.0.0.1:8080/waapi`. Set as `SK_WWISE_WAAPI_URL` for the exe.
- **`wwise_console`** — optional file path to a `WwiseConsole.exe`. Set as `SK_WWISE_CONSOLE` for the exe. Left empty, the newest 2022+ install is used.

An optional setting the user leaves empty is treated as unset: the exe ignores an empty value and an unsubstituted `${user_config.<key>}` placeholder.

The manifest is generated by `release/build_mcpb.py` (`build_mcpb(exe, out)` to call it from Python). The manifest schema is vendored in `release/schema/`.

## Plugin (`sk-wwise-plugin.zip`)

`build.ps1` also writes `sk-wwise-plugin.zip`: the Claude plugin. It is the release zip that the marketplace points at (ADR 0001). Layout (plugin root at the top of the archive):

| Path | Purpose |
| --- | --- |
| `.claude-plugin/plugin.json` | Plugin manifest: name `sk-wwise-mcp`, description, version (from `pyproject.toml`), `"mcpServers": "./sk-wwise-mcp.mcpb"` |
| `sk-wwise-mcp.mcpb` | The Bundle above. Claude Code extracts it under `.mcpb-cache/` and reads its server config and `user_config` |
| `skills/wwise-*/SKILL.md` | The `wwise-*` skills, copied from `.claude/skills/`. The `eval-*` skills are not shipped |

Built by `release/build_plugin.py` (`python release/build_plugin.py [--mcpb ...] [--out ...] [--version X]`). Python: `build_plugin_zip(mcpb, out, version=None)`.

### Marketplace file

`.claude-plugin/marketplace.json` at the repo root lists the plugin with an `archive` source at the GitHub release asset:

```json
"source": {
  "source": "archive",
  "url": "https://github.com/silver-rain-dev/sk-wwise-mcp/releases/download/v<version>/sk-wwise-plugin.zip"
}
```

- The entry `name` must equal the `name` in `plugin.json` (`sk-wwise-mcp`). If they differ, `claude plugin install <manifest-name>` reports "not found in marketplace".
- `version` and `source.url` move together. `build_plugin.marketplace_entry(version, sha256=None)` and `build_plugin.write_marketplace(version, sha256=None)` produce them; `python release/build_plugin.py --write-marketplace` rewrites the file and pins `source.sha256` to the zip it just built (Claude Code refuses a download that does not match). The committed file has no `sha256` until a release is built.
- The marketplace name is `sk-wwise`, so the install id is `sk-wwise-mcp@sk-wwise`.

### Validate

```
claude plugin validate <unpacked plugin dir>
claude plugin validate <marketplace root dir>
```

The unit tests (`tests/unit/test_plugin_zip.py`) run both when `claude` is on PATH, and always run a field check (required fields, name match, no `..` paths).

### Try an install from a local copy (manual)

Use a throwaway config dir so your real Claude Code settings are not touched. Replace `<scratch>` with any empty folder. `$S` is PowerShell; use `set` on cmd.

1. Build the zip: `python release/build_plugin.py --mcpb sk-wwise-mcp.mcpb --out <scratch>\sk-wwise-plugin.zip`
2. Make a marketplace folder with the zip unpacked inside it:
   ```
   <scratch>\mkt\.claude-plugin\marketplace.json
   <scratch>\mkt\plugin\            <- unzip sk-wwise-plugin.zip here
   ```
   In that `marketplace.json`, set the entry's `"source"` to the relative path `"./plugin"` (a local marketplace cannot use the release URL before the release exists).
3. Isolate the config and install:
   ```
   $S = "<scratch>"
   $env:CLAUDE_CONFIG_DIR = "$S\cfg"
   claude plugin validate $S\mkt
   claude plugin marketplace add $S\mkt
   claude plugin install sk-wwise-mcp@sk-wwise --config sk-wwise-mcp.profile=author
   ```
4. Check:
   - `claude plugin details sk-wwise-mcp` lists 13 skills (`wwise-*`, no `eval-*`).
   - `claude mcp list` shows `plugin:sk-wwise-mcp:sk-wwise-mcp` with the command `...\.mcpb-cache\<hash>/server/sk-wwise-mcp.exe --profile author`. It connects only with a real exe; a dummy exe fails to spawn.
5. Clean up: `claude plugin marketplace remove sk-wwise`, then delete the scratch folder.

Without `--config`, the install prints `MCP server "sk-wwise-mcp" needs configuration before it can start: set sk-wwise-mcp.profile ...`. That is expected: the bundle's required `profile` setting has no value yet. `--config` for a bundled `.mcpb` needs Claude Code v2.1.285+.

Result of this check on Claude Code 2.1.289 with a dummy exe (real PyInstaller exe not run): marketplace add and install succeed, 13 skills load, the bundle is extracted to `.mcpb-cache`, `user_config.profile` is stored under `pluginConfigs`, and the server command resolves to `server/sk-wwise-mcp.exe --profile author`. Spawning the real exe from the plugin is not yet verified here.

## Troubleshooting

**"Could not connect to Waapi"** — Wwise isn't running, or WAAPI is disabled. Check Project Settings → Authoring API.

**"Windows protected your PC" SmartScreen warning** — the exe isn't code-signed. Click **More info → Run anyway**. Windows remembers the exe after the first time.

**Servers don't appear in Claude** — make sure you launched `claude` from inside this folder. `.mcp.json` is project-scoped (cwd-relative).

**Need to move the folder** — fine, paths in `.mcp.json` are relative. Just `cd` to the new location and run `claude` again.
