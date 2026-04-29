# SK Wwise MCP

MCP servers that let Claude browse and interact with Wwise via the Wwise Authoring API (WAAPI).

## Quick start

1. **Unzip** this folder anywhere on disk.
2. **Make sure Wwise is running** with the Authoring API enabled (Project Settings → Authoring API → "Enable Wwise Authoring API").
3. **Open a terminal in this folder** and run:
   ```
   claude
   ```
   Claude CLI auto-detects `.mcp.json` (registers 12 MCP servers) and `.claude/skills/` (loads routing guidance) on launch.
4. **Allow MCP servers** when Claude prompts you (one-time per server).

That's it. Try: *"Ping Wwise"* or *"List all events in my project"*.

## What's in this folder

| Path | Purpose |
| --- | --- |
| `sk-wwise-mcp.exe` | Single binary that hosts all 12 MCP servers. Claude launches it once per server with a `--server <name>` argument. |
| `.mcp.json` | MCP server registry. Tells Claude which servers exist and how to launch them. |
| `.claude/skills/` | Routing skills — short docs that teach Claude which MCP tool fits which task. Loaded automatically. |

## Requirements

- **Windows 10/11** (this build is Windows-only).
- **Wwise** with WAAPI enabled.
- **Claude CLI** installed (`npm install -g @anthropic-ai/claude-code`).

## Troubleshooting

**"Could not connect to Waapi"** — Wwise isn't running, or WAAPI is disabled. Check Project Settings → Authoring API.

**"Windows protected your PC" SmartScreen warning** — the exe isn't code-signed. Click "More info" → "Run anyway".

**Servers don't appear in Claude** — make sure you launched `claude` from inside this folder. `.mcp.json` is project-scoped.

**Need to move the folder** — fine, paths in `.mcp.json` are relative. Just `cd` to the new location and run `claude` again.
