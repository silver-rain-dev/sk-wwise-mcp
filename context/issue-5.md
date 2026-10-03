- [2026-10-03, wave 2, issue #5] Routing guidance (MCP instructions) is built by `core/instructions.py`: `build_instructions(servers: Iterable[str]) -> str`, plus `GLOBAL_GUIDANCE`, `SERVER_NOTES` (dict: `cli.SERVERS` key -> note text) and `ADMIN_BUDGET_CHARS`.
  - Why: one deep module turns the mounted server names into the instructions text. Unknown server names raise `ValueError`; duplicates are dropped; order follows the input.
  - Affects: #9 (add the `show_wwise_object` hint) and any card that adds a tool or server.

- [2026-10-03, wave 2, issue #5] To add a tool hint, edit that server's string in `SERVER_NOTES` (e.g. `SERVER_NOTES["browse"]`). Write the tool name in single backticks, and name only tools of that same server (other servers may not be mounted). `tests/unit/test_instructions.py` fails if a note names an unknown tool or a tool of a different server.
  - Why: the checker in `core/tool_names.py` only sees backticked names, so unticked names would pass untested.
  - Affects: #9. Add the tool to `mcp_browse/server.py` in the same change, or the test fails.

- [2026-10-03, wave 2, issue #5] Budget: `ADMIN_BUDGET_CHARS = 5500`. Admin instructions measured 4706 chars when written (listen 1661, author 3414, build 3676, qa 2363). The test prints the size (`pytest -s`) and records it with `record_property`.
  - Why: the instructions are always in the client context, so they are capped. A new note or hint must fit, or trim another.
  - Affects: #9 and later cards that add notes. About 800 chars of headroom remain.

- [2026-10-03, wave 2, issue #5] `cli._build_server(names)` returns the FastMCP instance to run, with instructions set on both paths: single server sets `module.mcp.instructions`; multi-server uses `FastMCP("sk-wwise", instructions=...)`. `cli.main()` calls it and runs stdio. The `mcp_*/server.py` files were not changed.
  - Why: one place sets instructions; tests inspect the instance without starting stdio.
  - Affects: #6 (the `.mcpb` runs `cli.py`/exe, so it gets instructions with no extra work). #6 must not edit `cli.py`.

- [2026-10-03, wave 2, issue #5] Every `wwise-<server>` skill has one line starting `**Missing tools?**` naming the profiles that include the server (derived from `core/profiles.PROFILES`, in `PROFILE_NAMES` order). `tests/unit/test_instructions.py` checks each line against the table. `wwise-global` has a general bullet instead.
  - Why: if tools are missing, the profile excludes them; the user needs to know which profile adds them.
  - Affects: any card that changes `core/profiles.py` or adds a skill: update the guard line (regenerate by hand, the test names the mismatch).
