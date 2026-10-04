"""Tests for the Object Inspector MCP App: `show_wwise_object` and its ui:// resource.

WAAPI is mocked at `core.query.call`, so no Wwise is needed.
"""

import asyncio
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.inspector_html import INSPECTOR_HTML
from fastmcp import Client
from fastmcp.server.apps import UI_EXTENSION_ID, UI_MIME_TYPE
from waapi import CannotConnectToWaapiException

from mcp_browse.server import mcp, show_wwise_object

GUID = "{11111111-2222-3333-4444-555555555555}"
CHILD_GUID = "{aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee}"

SELF_OBJ = {
    "id": GUID,
    "name": "Footsteps",
    "type": "RandomSequenceContainer",
    "path": "\\Actor-Mixer Hierarchy\\Default Work Unit\\Footsteps",
    "notes": "Player steps",
    "@Volume": -3.0,
    "@Pitch": 0,
    "@LowPassFilter": 0,
    "@HighPassFilter": 0,
}
CHILD_OBJ = {
    "id": CHILD_GUID,
    "name": "Step_01",
    "type": "Sound",
    "path": "\\Actor-Mixer Hierarchy\\Default Work Unit\\Footsteps\\Step_01",
}
PARENT_OBJ = {
    "id": "{99999999-0000-0000-0000-000000000000}",
    "name": "Default Work Unit",
    "type": "WorkUnit",
    "path": "\\Actor-Mixer Hierarchy\\Default Work Unit",
}


def _fake_call(uri, args=None, options=None, timeout=30):
    """Answer ak.wwise.core.object.get by looking at the transform."""
    assert uri == "ak.wwise.core.object.get"
    transform = args.get("transform") or []
    selects = [t["select"][0] for t in transform if "select" in t]
    if selects == ["children"]:
        return {"return": [CHILD_OBJ]}
    if selects == ["parent"]:
        return {"return": [PARENT_OBJ]}
    return {"return": [SELF_OBJ]}


def test_show_wwise_object_returns_key_data():
    with patch("core.query.call", side_effect=_fake_call):
        result = show_wwise_object(object_guid=GUID)
    assert result["name"] == "Footsteps"
    assert result["type"] == "RandomSequenceContainer"
    assert result["path"].endswith("Footsteps")
    assert result["id"] == GUID
    assert result["properties"]["Volume"] == -3.0
    assert result["children_count"] == 1
    assert result["children"] == [
        {"id": CHILD_GUID, "name": "Step_01", "type": "Sound", "path": CHILD_OBJ["path"]}
    ]
    assert result["parent"]["name"] == "Default Work Unit"


def test_show_wwise_object_is_read_only_and_links_ui_resource():
    tool = asyncio.run(mcp.get_tool("show_wwise_object"))
    ann = tool.annotations
    assert ann.readOnlyHint is True
    assert ann.destructiveHint is False
    assert ann.idempotentHint is True
    assert ann.openWorldHint is False
    ui = tool.meta["ui"]
    assert ui["resourceUri"].startswith("ui://")
    # the app calls this tool back to drill down, so it must stay app-visible
    assert "app" in ui.get("visibility", ["app", "model"])


async def _read_ui_resource():
    uri = (await mcp.get_tool("show_wwise_object")).meta["ui"]["resourceUri"]
    async with Client(mcp) as client:
        contents = await client.read_resource(uri)
    return uri, contents[0]


def test_ui_resource_is_served_with_mcp_app_mime_type():
    uri, content = asyncio.run(_read_ui_resource())
    assert content.mimeType == UI_MIME_TYPE
    assert content.text.lstrip().lower().startswith("<!doctype html")


def test_ui_resource_is_self_contained_and_declares_no_connect_domains():
    uri, content = asyncio.run(_read_ui_resource())
    html = content.text
    # no remote scripts, styles or other http(s) references at all
    assert not re.search(r"<script[^>]+\bsrc\s*=", html, re.I)
    assert not re.search(r"<link[^>]+href\s*=", html, re.I)
    assert "http://" not in html and "https://" not in html
    assert "<script" in html  # inline script only

    async def meta():
        resource = await mcp.get_resource(uri)
        return resource.meta

    ui_meta = (asyncio.run(meta()) or {}).get("ui", {})
    csp = ui_meta.get("csp") or {}
    assert not csp.get("connectDomains")
    assert not csp.get("resourceDomains")


def test_clients_without_mcp_apps_get_a_json_text_block():
    """A plain MCP client (no UI support) reads the text content block."""

    async def run():
        async with Client(mcp) as client:
            return await client.call_tool("show_wwise_object", {"object_guid": GUID})

    with patch("core.query.call", side_effect=_fake_call):
        result = asyncio.run(run())
    blocks = [b for b in result.content if b.type == "text"]
    assert blocks, "tool result must carry a text content block"
    data = json.loads(blocks[0].text)
    assert data["name"] == "Footsteps"
    assert data["children"][0]["name"] == "Step_01"
    assert data["children_count"] == 1


def test_show_wwise_object_needs_an_identifier():
    assert "error" in show_wwise_object()


def test_show_wwise_object_not_found():
    with patch("core.query.call", return_value={"return": []}):
        assert show_wwise_object(object_path="\\Nope") == {"error": "Object not found"}


def test_show_wwise_object_waapi_unavailable():
    with patch("core.query.call", side_effect=CannotConnectToWaapiException):
        result = show_wwise_object(object_guid=GUID)
    assert "Could not connect to Waapi" in result["error"]


def test_browse_skill_and_routing_note_mention_the_tool():
    from core.instructions import SERVER_NOTES

    skill = Path(__file__).parent.parent.parent / ".claude" / "skills" / "wwise-browse" / "SKILL.md"
    assert "`show_wwise_object`" in skill.read_text(encoding="utf-8")
    assert "`show_wwise_object`" in SERVER_NOTES["browse"]


# ---------------------------------------------------------------------------
# Clicking a child must go through the host (MCP Apps bridge), not the network.
# ---------------------------------------------------------------------------

NETWORK_APIS = ("fetch(", "XMLHttpRequest", "WebSocket", "EventSource", "sendBeacon", "importScripts", "import(")


def test_inspector_js_has_no_direct_network_calls():
    html = INSPECTOR_HTML
    for api in NETWORK_APIS:
        assert api not in html, f"inspector must not use {api}"


def test_inspector_js_drills_down_with_host_tool_call():
    html = INSPECTOR_HTML
    assert "window.parent.postMessage" in html
    assert '"tools/call"' in html
    assert '"show_wwise_object"' in html
    assert '"ui/initialize"' in html


JS_HARNESS = r"""
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
const script = html.split("<script>")[1].split("</script>")[0];

function El(tag) {
  return {
    tag, children: [], listeners: {}, hidden: false, disabled: false, className: "",
    textContent: "", title: "", type: "",
    appendChild(c) { this.children.push(c); return c; },
    addEventListener(name, fn) { this.listeners[name] = fn; },
  };
}
const byId = {};
const document = {
  getElementById(id) { return byId[id] || (byId[id] = El("#" + id)); },
  createElement: El,
  querySelectorAll() { return Object.values(byId); },
};
const posted = [];
const winListeners = {};
const window = {
  parent: { postMessage(msg, origin) { posted.push(msg); } },
  addEventListener(name, fn) { winListeners[name] = fn; },
};
const banned = () => { throw new Error("direct network call"); };
global.fetch = banned; global.XMLHttpRequest = banned; global.WebSocket = banned;

new Function("window", "document", script)(window, document);

const send = (msg) => winListeners.message({ data: msg });
const init = posted.find((m) => m.method === "ui/initialize");
send({ jsonrpc: "2.0", id: init.id, result: {} });
send({
  jsonrpc: "2.0", method: "ui/notifications/tool-result",
  params: { content: [{ type: "text", text: "{}" }], structuredContent: {
    id: "{root}", name: "Footsteps", type: "RandomSequenceContainer", path: "\\X",
    notes: "", properties: { Volume: -3 }, parent: null, children_count: 1,
    children: [{ id: "{child-guid}", name: "Step_01", type: "Sound", path: "\\X\\Step_01" }],
  } },
});
const list = document.getElementById("children");
const button = list.children[0].children[0];
button.listeners.click();
const calls = posted.filter((m) => m.method === "tools/call");
console.log(JSON.stringify({
  title: document.getElementById("name").textContent,
  calls,
  initNotified: posted.some((m) => m.method === "ui/notifications/initialized"),
}));
"""


def test_inspector_child_click_posts_tools_call_to_host(tmp_path):
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not installed")
    html_file = tmp_path / "inspector.html"
    html_file.write_text(INSPECTOR_HTML, encoding="utf-8")
    harness = tmp_path / "harness.js"
    harness.write_text(JS_HARNESS, encoding="utf-8")
    out = subprocess.run(
        [node, str(harness), str(html_file)], capture_output=True, text=True, timeout=30
    )
    assert out.returncode == 0, out.stderr
    result = json.loads(out.stdout)
    assert result["title"] == "Footsteps"
    assert len(result["calls"]) == 1
    params = result["calls"][0]["params"]
    assert params == {"name": "show_wwise_object", "arguments": {"object_guid": "{child-guid}"}}
