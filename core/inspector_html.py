"""HTML for the Object Inspector MCP App.

Kept as a Python string (not a data file) so it ships inside the PyInstaller exe
with no `datas` entry and no `sys._MEIPASS` path logic.

Rules for this page:
- Self-contained: inline CSS and JS only. No remote scripts, styles or fonts.
- It never opens WAAPI or any network connection itself. Drill-down uses the MCP
  Apps bridge: `postMessage` to the host with a JSON-RPC `tools/call` request.
  The host then runs the browse tool `show_wwise_object` and replies.
- Data is written into the page with `textContent`, never `innerHTML`.
"""

INSPECTOR_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wwise Object Inspector</title>
<style>
  :root {
    --bg: #ffffff; --fg: #1f2328; --muted: #656d76; --line: #d0d7de;
    --card: #f6f8fa; --accent: #0969da;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #1b1d21; --fg: #e6e8eb; --muted: #9aa3ad; --line: #3a3f47;
      --card: #24272c; --accent: #6cb6ff;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 12px; background: var(--bg); color: var(--fg);
    font: 13px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  header { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
  h1 { margin: 0; font-size: 16px; }
  .type { color: var(--muted); font-size: 12px; }
  .path { color: var(--muted); font-size: 12px; word-break: break-all; margin: 2px 0 10px; }
  .toolbar { margin-left: auto; display: flex; gap: 6px; }
  button {
    font: inherit; color: var(--fg); background: var(--card);
    border: 1px solid var(--line); border-radius: 6px; padding: 3px 9px; cursor: pointer;
  }
  button:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
  button:disabled { opacity: .5; cursor: default; }
  h2 { font-size: 12px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); margin: 14px 0 6px; }
  table { border-collapse: collapse; width: 100%; }
  td { padding: 3px 8px 3px 0; border-bottom: 1px solid var(--line); }
  td:first-child { color: var(--muted); width: 40%; }
  ul { list-style: none; margin: 0; padding: 0; }
  li button { width: 100%; text-align: left; margin-bottom: 4px; display: flex; gap: 8px; }
  li .ctype { color: var(--muted); font-size: 12px; margin-left: auto; }
  .notes { white-space: pre-wrap; background: var(--card); border: 1px solid var(--line); border-radius: 6px; padding: 6px 8px; }
  .status { color: var(--muted); margin: 8px 0; }
  .error { color: #cf222e; }
  [hidden] { display: none !important; }
</style>
</head>
<body>
<div id="status" class="status">Waiting for Wwise object data...</div>
<main id="view" hidden>
  <header>
    <h1 id="name"></h1>
    <span id="type" class="type"></span>
    <div class="toolbar">
      <button id="up" type="button" title="Go to parent">Parent</button>
      <button id="refresh" type="button" title="Reload this object">Refresh</button>
    </div>
  </header>
  <div id="path" class="path"></div>
  <section id="notes-section" hidden>
    <h2>Notes</h2>
    <div id="notes" class="notes"></div>
  </section>
  <section id="props-section" hidden>
    <h2>Properties</h2>
    <table><tbody id="props"></tbody></table>
  </section>
  <section>
    <h2 id="children-title">Children</h2>
    <ul id="children"></ul>
  </section>
</main>
<script>
(function () {
  "use strict";

  // The only tool this page calls. It is a read-only browse tool.
  var DRILL_TOOL = "show_wwise_object";

  var statusEl = document.getElementById("status");
  var viewEl = document.getElementById("view");
  var current = null;
  var nextId = 1;
  var pending = {};

  // ---- MCP Apps bridge: JSON-RPC over postMessage to the host window ----
  function post(message) {
    message.jsonrpc = "2.0";
    window.parent.postMessage(message, "*");
  }

  function request(method, params) {
    return new Promise(function (resolve, reject) {
      var id = nextId++;
      pending[id] = { resolve: resolve, reject: reject };
      post({ id: id, method: method, params: params });
    });
  }

  function notify(method, params) {
    post({ method: method, params: params || {} });
  }

  // Ask the host to call a browse tool. This is the only way data is fetched.
  function callTool(name, args) {
    return request("tools/call", { name: name, arguments: args });
  }

  window.addEventListener("message", function (event) {
    var msg = event.data;
    if (!msg || msg.jsonrpc !== "2.0") return;
    if (msg.id !== undefined && !msg.method && pending[msg.id]) {
      var entry = pending[msg.id];
      delete pending[msg.id];
      if (msg.error) entry.reject(new Error(msg.error.message || "Request failed"));
      else entry.resolve(msg.result);
      return;
    }
    if (msg.method === "ui/notifications/tool-result") {
      showResult(msg.params);
    }
  });

  // ---- Result handling ----
  function extractData(result) {
    if (!result) return null;
    var sc = result.structuredContent;
    if (sc && typeof sc === "object") {
      if (sc.name !== undefined || sc.error !== undefined) return sc;
      if (sc.result && typeof sc.result === "object") return sc.result;
    }
    var blocks = result.content || [];
    for (var i = 0; i < blocks.length; i++) {
      if (blocks[i].type === "text") {
        try { return JSON.parse(blocks[i].text); } catch (e) { /* not JSON */ }
      }
    }
    return null;
  }

  function showResult(result) {
    var data = extractData(result);
    if (!data) { showStatus("Could not read the tool result.", true); return; }
    if (data.error) { showStatus(data.error, true); return; }
    render(data);
  }

  function showStatus(text, isError) {
    statusEl.textContent = text;
    statusEl.className = "status" + (isError ? " error" : "");
    statusEl.hidden = false;
  }

  function open(args) {
    showStatus("Loading...", false);
    setBusy(true);
    callTool(DRILL_TOOL, args).then(function (result) {
      setBusy(false);
      if (result && result.isError) { showStatus("The tool call failed.", true); return; }
      showResult(result);
    }, function (err) {
      setBusy(false);
      showStatus(err.message, true);
    });
  }

  function setBusy(busy) {
    var buttons = document.querySelectorAll("button");
    for (var i = 0; i < buttons.length; i++) buttons[i].disabled = busy;
  }

  // ---- Rendering (textContent only) ----
  function text(id, value) { document.getElementById(id).textContent = value || ""; }

  function render(data) {
    current = data;
    statusEl.hidden = true;
    viewEl.hidden = false;
    setBusy(false);
    text("name", data.name);
    text("type", data.type);
    text("path", data.path);

    document.getElementById("notes-section").hidden = !data.notes;
    text("notes", data.notes);

    var props = data.properties || {};
    var keys = Object.keys(props);
    document.getElementById("props-section").hidden = keys.length === 0;
    var tbody = document.getElementById("props");
    tbody.textContent = "";
    keys.forEach(function (key) {
      var tr = document.createElement("tr");
      var k = document.createElement("td");
      var v = document.createElement("td");
      k.textContent = key;
      v.textContent = typeof props[key] === "object" ? JSON.stringify(props[key]) : String(props[key]);
      tr.appendChild(k);
      tr.appendChild(v);
      tbody.appendChild(tr);
    });

    var children = data.children || [];
    var total = data.children_count === undefined ? children.length : data.children_count;
    text("children-title", "Children (" + total + ")");
    var list = document.getElementById("children");
    list.textContent = "";
    children.forEach(function (child) {
      var li = document.createElement("li");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.title = child.path || "";
      var label = document.createElement("span");
      label.textContent = child.name;
      var ctype = document.createElement("span");
      ctype.className = "ctype";
      ctype.textContent = child.type;
      btn.appendChild(label);
      btn.appendChild(ctype);
      btn.addEventListener("click", function () { open({ object_guid: child.id }); });
      li.appendChild(btn);
      list.appendChild(li);
    });
    if (total > children.length) {
      var more = document.createElement("li");
      more.className = "status";
      more.textContent = "Showing " + children.length + " of " + total + ".";
      list.appendChild(more);
    }

    document.getElementById("up").disabled = !data.parent;
  }

  document.getElementById("up").addEventListener("click", function () {
    if (current && current.parent) open({ object_guid: current.parent.id });
  });
  document.getElementById("refresh").addEventListener("click", function () {
    if (current) open({ object_guid: current.id });
  });

  // ---- Start: handshake with the host ----
  request("ui/initialize", {
    appInfo: { name: "sk-wwise-object-inspector", version: "1.0.0" },
    appCapabilities: {},
    protocolVersion: "2025-11-21"
  }).then(function () {
    notify("ui/notifications/initialized");
  }, function () {
    showStatus("Could not reach the host.", true);
  });
})();
</script>
</body>
</html>
"""
