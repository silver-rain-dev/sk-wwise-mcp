# SK Wwise MCP

A modular suite of [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) servers for [Audiokinetic Wwise](https://www.audiokinetic.com/), enabling AI agents to browse, edit, audition, profile, and build Wwise projects through the [Wwise Authoring API (WAAPI)](https://www.audiokinetic.com/library/edge/?id=waapi.html).

Each server is capped at 15 tools to minimize LLM tool confusion, with [Agent Skills](https://agentskills.io/) routing for multi-agent orchestration.

## Features

- **97 tools** across **12 MCP servers**, covering the full WAAPI surface
- **Agent Skills spec** compliant — works with Claude Code, Cursor, VS Code Copilot, Gemini CLI, and 30+ other agent tools
- **Thread-safe WAAPI dispatcher** with queue-based serialization and backpressure handling
- **WwiseConsole CLI integration** for headless operations (project creation, SoundBank generation, migration)
- **450 unit tests** (mocked WAAPI) + **44 integration tests** (live Wwise)

## Servers

| Server | Tools | Description |
|--------|-------|-------------|
| `mcp_browse` | 14 | Read-only project inspection, object queries, property discovery |
| `mcp_objects` | 7 | Create, delete, rename, move, copy objects; set properties and references |
| `mcp_containers` | 9 | Switch/Blend Container assignments, State Groups, randomizer, attenuations, Game Parameter ranges |
| `mcp_pipeline` | 12 | Audio import/conversion, SoundBank management, tab-delimited generation, project save, logs |
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
│   ├── audio_convert.py    # Non-WAV to WAV conversion (ffmpeg)
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
└── tests/                  # 450 unit + 44 integration tests
```

## Philosophy

This project is an **exploration** of how AI agents can assist with large-scale Wwise production work — the tedious, repetitive tasks that eat hours (bulk renaming, auditing property consistency across hundreds of objects, generating SoundBanks, diffing configurations) — while **minimizing the risk of unwanted changes** to the project.

The core tension: AI is most useful when it can take action, but Wwise projects are complex and a wrong edit can silently break audio behavior in ways that surface much later. This project's architecture is designed around that tension — let the agent help with the heavy lifting, but make it structurally difficult for it to do things it shouldn't.

This is not a finished product. It's a working experiment in finding the right boundary between AI assistance and human control for audio middleware.

### Why no Sound Engine (`ak.soundengine`) coverage

WAAPI exposes both **authoring** functions (`ak.wwise.*`) and **sound engine** functions (`ak.soundengine.*`). This project deliberately covers only the authoring side.

The sound engine API triggers real-time audio behavior — posting events, setting RTPCs, setting states and switches, seeking — the same operations that the game runtime performs. Exposing these to an AI agent creates a debugging nightmare: if something sounds wrong during a session, was it the game posting an event, or the LLM? With authoring operations the scope is clear — the agent changed a property in the project, and the change is visible in the UI and saved to the work unit. Sound engine calls leave no such trail.

Sound engine interaction belongs in a more controlled environment: game-side tooling, automated test harnesses, or direct scripting where every call is logged and traceable. Not behind an AI agent whose decision-making is opaque by nature.

The one exception is **transport-based playback** (`mcp_audition`), which uses `ak.wwise.core.transport.*` — an authoring API that previews sounds within the Wwise editor without affecting game-side state.

## Architecture

### Server Separation Philosophy

Most MCP projects expose one server with all tools. This project deliberately splits into 12 servers for three reasons:

#### Role-based access control

Not every user needs every tool. By separating servers along permission boundaries, teams can grant access by role:

| Role                     | Servers                                  | Can do                                                       |
| ------------------------ | ---------------------------------------- | ------------------------------------------------------------ |
| Sound designer (junior)  | browse, audition, media_read             | Explore the project, preview sounds, inspect audio           |
| Sound designer (senior)  | + objects, containers                    | Create/edit objects, configure containers                    |
| Build engineer           | + pipeline, command_line                 | Import audio, generate SoundBanks, run CLI operations        |
| QA / profiling           | + profiling, profiling_control, remote   | Profile performance, connect to devkits                      |
| Admin                    | all servers                              | Full access including UI automation and generic WAAPI        |

An agent with only `browse` enabled physically cannot delete objects or overwrite SoundBank settings — the tools don't exist in its context. This is a stronger guarantee than relying on prompt instructions like "don't modify anything."

#### Read/write separation

Servers are split by **intent and access level**, not by WAAPI namespace:

- **Read-only** servers (`browse`, `profiling`, `media_read`) cannot modify the project. Safe to give to any agent or user without risk.
- **Edit** servers (`objects`, `containers`) modify project state — object creation, deletion, property changes.
- **Pipeline** servers (`pipeline`, `command_line`) handle import/build operations that affect files on disk.
- **Runtime** servers (`audition`, `remote`, `profiling_control`) control playback, profiling, and remote connections through the authoring tool.

This means you can build a "read-only assistant" by enabling only the read servers, or a "full authoring agent" by enabling everything. The separation is enforced at the transport level — there's no way to accidentally call a write tool from a read-only server.

#### LLM tool routing accuracy

LLMs get worse at selecting the right tool as the tool count grows. By capping each server at ~15 tools, the model sees a focused set of tools relevant to the task. Agent Skills (`.agents/skills/`) route the LLM to the correct server based on the user's intent, keeping the active tool set small even though 95 tools exist across the suite.

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

2. **Run** — iterate through all test cases using either skill:

   **`/eval-batch`** — runs up to 10 cases per invocation (recommended):
   ```
   /loop 60s /eval-batch
   ```
   Finishes all 39 cases in ~4 iterations. Each invocation picks up where the last left off.

   **`/eval-routing`** — runs 1 case per invocation (fine-grained):
   ```
   /loop 30s /eval-routing
   ```

   Both log which MCP tools were called and verify against expected tools.

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
