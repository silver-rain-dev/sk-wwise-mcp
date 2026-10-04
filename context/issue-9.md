- [2026-10-03, wave 3, issue #9] MCP App pattern (FastMCP 3.1.1): tool uses `@mcp.tool(..., app=AppConfig(resource_uri=URI))` and a `@mcp.resource(URI, app=AppConfig(...))` serves the HTML. Both come from `fastmcp.server.apps`. A `ui://` URI gets MIME `text/html;profile=mcp-app` automatically.
  - Why: this is the real API in the venv (`fastmcp/server/apps.py`). `app=` on a tool writes `meta["ui"]={"resourceUri": ...}`; tool visibility defaults to model + app, so the iframe may call the tool back.
  - Affects: later MCP App cards (sliders, playback). Put data code in `core/<name>.py`, HTML in `core/<name>_html.py`, register both in the server file.

- [2026-10-03, wave 3, issue #9] The inspector HTML is a Python string constant (`core/inspector_html.py: INSPECTOR_HTML`), not a data file.
  - Why: it ships in the PyInstaller exe with no `sk-wwise-mcp.spec` `datas` change and no `sys._MEIPASS` path logic. `collect_submodules("core")` already picks the module up.
  - Affects: later App cards: follow the same pattern; only use a data file if a page grows too big or needs binary assets (then add it to `datas` and read via `sys._MEIPASS` when frozen).

- [2026-10-03, wave 3, issue #9] App HTML rules: inline CSS/JS only, no remote `<script src>`/`<link>`/`http(s)://`, no `fetch`/`XMLHttpRequest`/`WebSocket`, no `csp` connect or resource domains. Data is fetched only by posting JSON-RPC `tools/call` to `window.parent` (MCP Apps bridge) naming a browse tool. Render with `textContent`, never `innerHTML`.
  - Why: the page must never open WAAPI itself, and must respect the profile (it can only call tools the host exposes).
  - Affects: later App cards. `tests/unit/test_show_wwise_object.py` has static checks plus a node-based harness for click behavior (skipped if `node` is missing).

- [2026-10-03, wave 3, issue #9] Browse server now has 16 tools (was 15): `show_wwise_object` added. Admin routing instructions are 4809 chars (budget 5500, ~690 headroom).
  - Why: tool counts and the instructions budget move with each tool hint.
  - Affects: #7 and README tool counts (root `README.md` still says 97 tools / browse 14; it was already out of date, not changed here).
