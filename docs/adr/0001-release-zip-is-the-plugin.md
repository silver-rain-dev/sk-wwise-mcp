# The release zip is the Claude plugin, and it embeds the .mcpb

Sound designers should install Claude Desktop plus one plugin, with no Python, uv or terminal. So CI builds one `sk-wwise-mcp.mcpb` Desktop Extension: the PyInstaller exe, its manifest, and `user_config` such as the WAAPI URL and the role profile. CI then wraps it in the release zip together with `.claude-plugin/plugin.json` (`"mcpServers": "./sk-wwise-mcp.mcpb"`) and the `wwise-*` skills. A `marketplace.json` at the repo root lists the plugin with an `archive` source at the GitHub release asset URL. The same `.mcpb` is also offered on its own for people who only use Desktop chat. The plugin reaches the Claude Code CLI, the Desktop Code tab, and Cowork sessions that run locally in Claude Desktop.

## Considered options

- **Git source + `uvx`**: a small plugin that is always current, but every user needs uv/Python. Rejected because the target users are not developers.
- **Git source + first-run downloader**: a smaller plugin, but it adds a network step and a moving part to first launch. Rejected for that extra failure point.
- **Plugin `.mcp.json` runs the exe directly**: simpler on its own, but it would need a second server manifest and config schema kept in sync with the `.mcpb`. Rejected in favor of one manifest.

## Consequences

- Each update needs a version tag and a new release. The marketplace entry's archive URL and version must move with the tag.
- A standalone `.mcpb` can't carry skills, so the chat-only path gets a condensed routing guide in the MCP server `instructions` instead.
- Setting bundle config at install from the shell (`--config`) needs Claude Code v2.1.285+.
- The exe is not code-signed, so SmartScreen still warns on first run.
