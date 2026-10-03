# PRD: sk-wwise-mcp as a Claude plugin

Campaign `wwise-claude-plugin` · created 2026-10-02 · repo `silver-rain-dev/sk-wwise-mcp`
Decisions: `docs/adr/0001-release-zip-is-the-plugin.md` · Terms: `CONTEXT.md`

## Problem Statement

Getting the Wwise tools into Claude today takes three steps: unzip a release folder, open a terminal in it, and run the `claude` CLI there. Sound designers are not developers. They will not keep a terminal open in a special folder, and they don't use the CLI. The tools also have two role maps that disagree (`profiles/*.mcp.json` vs. the release README). The routing guidance lives in skills that can name tools the user doesn't have loaded.

## Solution

A sound designer installs Claude Desktop, adds this repo's plugin marketplace, and installs one plugin. At install they choose a profile (default **author**) and can set the WAAPI URL and the WwiseConsole path. The Wwise tools then work in the Desktop Code tab, in local Cowork sessions and in the Claude Code CLI. People who only use Desktop chat can install the same server as a standalone `.mcpb`. One tool, `show_wwise_object`, renders an interactive Object Inspector inside Claude. It is the first MCP App and proves the UI path for later work.

## User Stories

1. As a sound designer, I want to install the Wwise tools from inside Claude Desktop, so that I never open a terminal.
2. As a sound designer, I want the install to need no Python, uv or other runtime, so that it works on a plain studio machine.
3. As a sound designer, I want to choose my profile at install, so that I only get the tools my role needs.
4. As a sound designer, I want **author** to be the default profile, so that the common case needs no decision.
5. As a sound designer, I want to change my profile later from the plugin settings, so that I don't need to reinstall.
6. As a sound designer, I want to set a custom WAAPI URL, so that the tools work when my studio moved the WAAPI port.
7. As a sound designer with several Wwise versions installed, I want to pin a WwiseConsole path, so that command-line tools use the right version.
8. As a sound designer, I want Claude to only suggest tools that are actually loaded, so that it never calls a tool that doesn't exist.
9. As a sound designer on a restricted profile, I want Claude to tell me which profile adds a missing capability, so that I know how to get it.
10. As a sound designer, I want write and delete tools to still ask before running, so that a profile is not my only safety net.
11. As a sound designer who only uses Desktop chat, I want a single `.mcpb` file I can double-click, so that I get the tools without the Code tab.
12. As a chat-only user, I want routing guidance to come with the server itself, so that Claude picks the right tools without skills.
13. As a sound designer working in Cowork, I want the plugin to work in my local Cowork session, so that I can use Claude's non-coding surface.
14. As a sound designer, I want to ask Claude to show a Wwise object and see an interactive inspector card, so that I can read its properties and children at a glance.
15. As a sound designer, I want to click a child in the inspector to drill into it, so that I can browse the hierarchy without typing paths.
16. As a sound designer, I want the inspector to respect my profile and permissions, so that the UI can't do more than the chat can.
17. As a sound designer, I want installed plugins to update when a new release ships, so that I get fixes without reinstalling.
18. As a maintainer, I want one tag push to build the exe, the `.mcpb`, the plugin zip and the release, so that releasing is one step.
19. As a maintainer, I want CI to update `marketplace.json` with the exact release URL and version, so that updates reach users and a bad release can be reverted by one line.
20. As a maintainer, I want one canonical profile table in code, so that the role maps can't drift apart again.
21. As a maintainer, I want the legacy `profiles/*.mcp.json` and the release README role table generated from or checked against that table, so that docs match behavior.
22. As a maintainer, I want a test that every tool name in the skills and the routing guidance exists, so that stale tool references fail CI.
23. As a maintainer, I want a recorded per-surface result for the inspector MCP App (chat, Cowork, Code tab), so that the next UI campaign knows what renders where.
24. As a studio lead, I want the old zip-and-CLI release to keep working, so that existing users aren't broken.

## Implementation Decisions

- **Plugin home**: this repo. The PySide app keeps using it as a submodule and is not changed by this campaign.
- **Delivery (ADR 0001)**: the release zip is the plugin. It contains `.claude-plugin/plugin.json`, the `wwise-*` skills and `sk-wwise-mcp.mcpb`. `plugin.json` sets `mcpServers` to the embedded `.mcpb`. A `marketplace.json` at the repo root lists the plugin with an `archive` source pointing at the exact tagged release asset URL.
- **Bundle (`.mcpb`)**: wraps the PyInstaller onefile exe. Its manifest declares `user_config`:
  - `profile`: enum listen / author / build / qa / admin. Default `author`.
  - `waapi_url`: optional. Default `ws://127.0.0.1:8080/waapi`.
  - `wwise_console`: optional file path, mapped to `SK_WWISE_CONSOLE`.
- **Profiles**: one canonical table in code maps each profile to its servers.

  | Profile | Servers |
  |---|---|
  | listen | browse, audition, media-read |
  | author | listen + objects, containers, pipeline, ui |
  | build | author + command-line |
  | qa | browse, audition, profiling, profiling-control, remote |
  | admin | all 12 |

  The exe gains a profile option that resolves to a server list. The existing comma-list `--server` stays. Legacy `profiles/*.mcp.json` files are generated from the table, or a test checks them against it.
- **WAAPI URL**: the WAAPI connection layer reads an optional URL setting (env var) with the current default. This is new behavior; today the URL is fixed.
- **Routing guidance**: when the exe starts, it builds its MCP `instructions` from the global guidance plus a short routing note per *mounted* server. So guidance only names tools that are loaded, and the standalone `.mcpb` gets guidance with no skills. Each server needs a short routing note (condensed from its skill). This is a deep module: input = mounted server set, output = instructions text, easy to test alone.
- **Skills**: the plugin ships the `wwise-*` skills for detailed how-to. Each skill gains one line: if its tools are missing, the active profile excludes them; tell the user which profile adds them.
- **MCP App tracer**: a new read-only `show_wwise_object` tool, using FastMCP 3.1.1's MCP Apps support. It returns object data and links a `ui://` Object Inspector resource. The iframe gets refreshes and children by asking the host to call browse tools. It never opens WAAPI itself.
- **Release CI**: on a `v*` tag, build the exe, then the `.mcpb`, then the plugin zip. Publish the release with the plugin zip, the standalone `.mcpb` and the legacy zip. Then commit `marketplace.json` with the new URL and version.
- **Legacy path kept**: the existing zip (exe + `.mcp.json` + `.claude/skills`) still ships.

## Testing Decisions

- Test external behavior only: inputs → outputs of the profile resolver, the instructions builder, the manifest/plugin generators, and tool results. Don't assert on internals.
- **Profile table**: each profile resolves to its exact server list; unknown profile is an error; legacy profile files match the table.
- **Instructions builder**: for each profile, the output mentions only tools that the mounted servers actually expose. This uses the same "every referenced tool name exists" check as the skills test.
- **Skills / guidance tool-name test**: scan all `wwise-*` SKILL.md files and the routing notes for tool names, and assert each exists in the server registry. This guards against the `query_wwise_objects` class of bug.
- **Manifest / plugin generation**: generated `.mcpb` manifest, `plugin.json` and `marketplace.json` validate against their schemas. Run `claude plugin validate` in CI if it is available on the runner; otherwise run a schema check.
- **WAAPI URL setting**: the connection layer uses the env var when set and the default otherwise.
- **`show_wwise_object`**: unit tests with the mocked WAAPI pattern already used by the `test_server_*` tests. Check that the result carries the UI resource link and that the resource is served with the MCP App MIME type.
- Prior art: `tests/unit/test_server_*.py` (server tools with mocked WAAPI), `tests/unit/test_core_wwise_cli.py`, `tests/integration/` (live Wwise, not run in CI).
- A known failure, `tests/unit/test_browse_extra.py::test_get_switch_container_assignments_no_identifier`, needs a live Wwise and also fails on `main`. Don't count it against slices.
- End-to-end install in real Claude surfaces is manual (HITL).

## Out of Scope

- Code signing (SmartScreen warning stays; documented).
- Submitting the plugin to Anthropic's public directory.
- Property sliders, playback controls, and any further MCP Apps beyond the read-only inspector.
- A Claude Code mod (approval pane, object chips).
- Changes to the PySide app (its prompt bug is tracked separately as sk-wwise-mcp-standalone-pyside#9).
- macOS / Linux builds.

## Further Notes

- Prerequisite: PR silver-rain-dev/sk-wwise-mcp#1 (multi-server mounting, version checks, release path fix) must be merged before foreman starts. Profiles depend on its comma-list `--server`.
- `origin` in the local clone uses SSH, which fails on this machine. The `main` remote (HTTPS) works.
- A local stdio server in a plugin runs in Claude Code and in local Cowork, but not on claude.ai (per Claude Code plugin docs). That's expected.
- Bundle config set at install from the shell (`--config`) needs Claude Code v2.1.285+.
- Follow-up campaign candidates: sliders/playback MCP Apps, a Code-tab mod, directory submission, code signing.
