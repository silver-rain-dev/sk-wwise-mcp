- [2026-10-03, wave 1, issue #4] Reusable tool-name checker lives in `core/tool_names.py`
  - Why: guidance (skills, and generated server instructions) must only name tools that exist.
  - Affects: #5 (instructions builder) calls it on generated text. API, all take plain text:
    - `known_tool_names() -> set[str]` — built from the 12 real `mcp_*.server` FastMCP objects (cached; safe inside a running event loop).
    - `extract_tool_names(text, known=None) -> set[str]` — tool-shaped names found in text.
    - `unknown_tool_names(text, known=None) -> list[str]` — sorted names not in the registry. Pass `known=` to check against only the mounted servers' tools (e.g. the profile's subset).
    - `unknown_tool_names_in_files(paths, known=None) -> dict[Path, list[str]]`.
    - `SERVER_MODULES` — tuple of the 12 server module names.

- [2026-10-03, wave 1, issue #4] Extraction convention: only single-backticked, lowercase snake_case tokens with at least one underscore are checked; a trailing `(...)` call suffix is stripped
  - Why: avoids false positives on WAAPI URIs, `@Property` names, paths, camelCase args and single words.
  - Affects: #5 and any skill/instruction author. A token is a tool name if its first segment is a verb used by a real tool (get, set, import, cli, ...) OR it contains `wwise`, `waapi`, `profiler` or `remote`. Names written without backticks are NOT checked. Backticked args that share a tool verb go in `IGNORED_TOKENS` (currently only `list_name`). Server names like `mcp_browse` are not checked.

- [2026-10-03, wave 1, issue #4] `tests/unit/test_skill_tool_names.py` fails if any `.claude/skills/wwise-*/SKILL.md` names an unknown tool
  - Why: guards against stale tool names (see standalone-pyside#9, `query_wwise_objects`).
  - Affects: #5 adds a profile-guard line and #9 adds a tool to wwise-browse. New tool names written in skills must be backticked and must exist on a server, or the test fails. Add the tool to the server in the same change.
