# SK Wwise MCP

A modular suite of [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) servers for [Audiokinetic Wwise](https://www.audiokinetic.com/), enabling AI agents to browse, edit, audition, profile, and build Wwise projects through the [Wwise Authoring API (WAAPI)](https://www.audiokinetic.com/library/edge/?id=waapi.html).

Built for AAA production — each server is capped at 15 tools to minimize LLM tool confusion, with [Agent Skills](https://agentskills.io/) routing for multi-agent orchestration.

## Features

- **95 tools** across **12 MCP servers**, covering the full WAAPI surface
- **Agent Skills spec** compliant — works with Claude Code, Cursor, VS Code Copilot, Gemini CLI, and 30+ other agent tools
- **Thread-safe WAAPI dispatcher** with queue-based serialization and backpressure handling
- **WwiseConsole CLI integration** for headless operations (project creation, SoundBank generation, migration)
- **351 unit tests** with full mock coverage

## Servers

| Server | Tools | Description |
|--------|-------|-------------|
| `mcp_browse` | 14 | Read-only project inspection, object queries, property discovery |
| `mcp_objects` | 8 | Create, delete, rename, move, copy objects; set properties and references |
| `mcp_containers` | 9 | Switch/Blend Container assignments, State Groups, randomizer, attenuations, Game Parameter ranges |
| `mcp_pipeline` | 9 | Audio import, SoundBank management, project save, logs |
| `mcp_audition` | 4 | Transport-based playback preview |
| `mcp_media_read` | 3 | Audio source peaks, Media Pool queries |
| `mcp_ui` | 13 | Wwise UI automation — layouts, commands, selection, screenshots |
| `mcp_profiling` | 12 | Read-only profiler data — voices, busses, CPU, meters, RTPCs |
| `mcp_profiling_control` | 7 | Profiler capture control, meter registration, cursor navigation |
| `mcp_remote` | 4 | Remote connection to devkits and game instances |
| `mcp_command_line` | 9 | WwiseConsole CLI — no WAAPI needed |
| `mcp_generic` | 3 | Fallback — discover and call any WAAPI function |

## Requirements

- Python 3.12+
- Wwise 2024.1+ (with WAAPI enabled for most servers)
- `uv` (recommended) or `pip` for dependency management

### Wwise 2025.1 Hierarchy Rename

Wwise 2025.1 renamed the top-level hierarchies:

| Pre-2025.1 | 2025.1+ |
|-------------|---------|
| `\Actor-Mixer Hierarchy` | `\Containers` |
| `\Master-Mixer Hierarchy` | `\Busses` |

All paths in this project (tool descriptions, test cases, examples) use the **2025.1+ names**. If you're running Wwise 2024.x or earlier, replace `\Containers` with `\Actor-Mixer Hierarchy` and `\Busses` with `\Master-Mixer Hierarchy` in your queries.

## Quick Start

### 1. Clone and run setup

**Windows:**
```bash
git clone https://github.com/silver-rain-dev/sk-wwise-mcp
cd sk-wwise-mcp/sk-wwise-mcp
setup.bat
```

**macOS / Linux:**
```bash
git clone https://github.com/silver-rain-dev/sk-wwise-mcp
cd sk-wwise-mcp/sk-wwise-mcp
./setup.sh
```

The setup script will:
- Install dependencies (via `uv` or `pip`)
- Let you choose which servers to enable
- Generate a `.mcp.json` with the correct paths for your machine

### 2. Start Wwise

Open Wwise with a project and ensure WAAPI is enabled (Project > User Preferences > Enable Wwise Authoring API).

### 3. Verify connectivity

In Claude Code or your agent:

```
Ping Wwise to check if it's available
```

<details>
<summary><strong>Manual setup (without setup script)</strong></summary>

```bash
cd sk-wwise-mcp/sk-wwise-mcp
uv sync   # or: python -m venv .venv && .venv/Scripts/pip install -e .
```

Then add servers to your `.mcp.json` (project root) or `~/.claude.json` (global):

```json
{
  "mcpServers": {
    "sk-wwise-browse": {
      "command": "/path/to/.venv/Scripts/python.exe",
      "args": ["/path/to/mcp_browse/server.py"]
    }
  }
}
```

Use forward slashes on Windows. Repeat for each server — see `.mcp.json` in the repo root for the full list.

</details>

## Project Structure

```
sk-wwise-mcp/
├── .agents/skills/         # Agent Skills (SKILL.md per server)
│   ├── wwise-global/       # Global rules and workflows
│   ├── wwise-browse/       # Browse server skill
│   ├── wwise-objects/      # Objects server skill
│   └── ...                 # One per server
├── core/                   # Shared business logic
│   ├── waapi_util.py       # WAAPI connection, dispatcher, ping
│   ├── query.py            # Object queries, property inspection
│   ├── objects.py          # Object CRUD operations
│   ├── pipeline.py         # Import, SoundBank, save
│   ├── transport.py        # Transport playback
│   ├── media.py            # Audio peaks, Media Pool
│   ├── profiling.py        # Profiler data retrieval
│   ├── ui.py               # UI automation
│   ├── wwise_cli.py        # WwiseConsole CLI wrapper
│   └── generic_handling.py # Generic WAAPI passthrough
├── mcp_browse/             # Read-only project inspection
├── mcp_objects/            # Object editing
├── mcp_containers/         # Container-specific config
├── mcp_pipeline/           # Import and build pipeline
├── mcp_audition/           # Transport playback
├── mcp_media_read/         # Audio analysis
├── mcp_ui/                 # UI automation
├── mcp_profiling/          # Profiler data (read-only)
├── mcp_profiling_control/  # Profiler control
├── mcp_remote/             # Remote connection
├── mcp_command_line/       # WwiseConsole CLI
├── mcp_generic/            # Fallback WAAPI passthrough
└── tests/                  # 351 unit tests
```

## Architecture

### Server Separation Philosophy

Servers are split by **intent and access level**, not by WAAPI namespace:

- **Read-only** servers (browse, profiling, media_read) cannot modify the project
- **Edit** servers (objects, containers) modify project state
- **Pipeline** servers (pipeline, command_line) handle import/build operations
- **Runtime** servers (audition, remote, profiling_control) control playback, profiling, and remote connections through the authoring tool

This enables **role-based access control** — a junior sound designer can have browse + audition without access to pipeline or objects.

### Thread-Safe WAAPI Dispatcher

All WAAPI calls are serialized through a queue-based dispatcher (`core/waapi_util.py`), ensuring:

- Thread-safe access to the WebSocket connection
- Backpressure handling (queue max: 10,000)
- Automatic reconnection on stale connections

### Agent Skills

The `.agents/skills/` directory contains [Agent Skills](https://agentskills.io/) files that route LLMs to the correct server based on the task. The `wwise-global` skill contains shared rules and workflow patterns.

## Testing

### Unit Tests

```bash
cd sk-wwise-mcp
uv run pytest tests/ -v
```

Unit tests use mocked WAAPI calls — no Wwise instance needed.

### Integration / Eval Tests

The `tests/eval/` directory contains an integration test suite that verifies MCP tool routing against a live Wwise project. It checks that the LLM selects the correct tools for each prompt.

**39 test cases** across 6 categories: browse, audition, generic, objects, media-read, cross-server.

#### Running the eval

1. **Setup** — create a test project with known objects via the `eval-setup` Claude Code skill:
   ```
   /eval-setup
   ```
   This creates a headless WwiseConsole project at `tests/eval/EvalTestProject/` with:
   - Actor-Mixer hierarchy (Sounds, Random Container, Switch Container)
   - Events, State Groups, Switch Groups with assignments
   - Audio files imported into all Sounds (for media/peaks tests)
   - Attenuation ShareSet with volume curve
   - Differing properties on Footstep_01/02 (for diff tests)

2. **Run** — iterate through all test cases:
   ```
   /loop 30s /eval-routing
   ```
   Each iteration runs one case, logs which MCP tools were called, and verifies against expected tools.

   > **Why `/loop` instead of `/eval-run`?** The `/eval-run` skill processes all 39 cases sequentially in a single conversation. By case ~33, the accumulated tool calls, results, and verification output can exhaust the context window, causing the run to abort before finishing. `/loop` with `/eval-routing` avoids this by running one case per conversation turn, keeping context usage flat.

3. **Report** — view results:
   ```bash
   python tests/eval/report.py
   ```

4. **Teardown** — clean up:
   ```
   /eval-teardown
   ```

#### Eval architecture

- `test_cases.json` — prompt + expected tools for each case
- `verify.py` — compares actual tool calls against expected, writes `test_results.json`
- `report.py` — generates pass/fail summary by category
- `log_tool.py` — PostToolUse hook that logs MCP tool calls to `tool_log.jsonl`
- `.claude/settings.json` — configures the PostToolUse hook

#### Connection resilience

`core/waapi_util.py` includes self-healing connection logic:
- **Ping before call** — detects stale WAAPI connections
- **Auto-reconnect** — creates a fresh WaapiClient if the connection is dead
- **Auto-restart headless server** — if a `.waapi_server.lock` file exists (written by `cli_start_waapi_server`), the server is automatically restarted when unresponsive
- **No-op for UI sessions** — if the user runs Wwise with the UI (no lockfile), connection failures surface as clear errors without attempting restart

## Example Prompts

```
Show me all Events in my Wwise project
How many Sound objects are under Containers?
Compare the settings between Footstep_Walk and Footstep_Run
Import all .wav files from C:/audio/ into a Random Container
Play the sound at \Containers\Default Work Unit\Footstep
What's the CPU usage in the profiler right now?
Create a new Wwise project at C:/MyGame/MyGame.wproj for Windows and PS5
```

## Contributing

This project is not accepting direct tool contributions. Adding or modifying MCP tools affects LLM routing accuracy across the entire suite — each change requires running the eval framework against a live Wwise project, which involves LLM API costs and manual verification.

If you'd like to extend the tool suite:

- **Bug reports and feature requests** — please open an issue
- **Custom tools for your team** — fork the repo and add tools to your fork. Use the eval framework (`tests/eval/`) to validate that your changes don't break routing accuracy

> **Why not automate routing tests in CI?** Full routing validation requires sending prompts to an LLM to see which tools it selects — results aren't fully deterministic, and each run takes time to verify. The current eval framework runs interactively via Claude Code skills, validating routing accuracy across 39 test cases with manual review. If you're already on a Claude Max/Pro subscription, running the eval incurs no additional API costs.

## License

See [LICENSE](LICENSE) for details.
