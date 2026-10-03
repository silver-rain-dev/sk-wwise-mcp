import asyncio
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import cli
from core import instructions as instr
from core.instructions import (
    ADMIN_BUDGET_CHARS,
    GLOBAL_GUIDANCE,
    SERVER_NOTES,
    build_instructions,
)
from core.profiles import PROFILE_NAMES, PROFILES, resolve_profile
from core.tool_names import extract_tool_names, unknown_tool_names

REPO_ROOT = Path(__file__).parent.parent.parent


def _mounted_tools(servers):
    """Tool names exposed by the given servers (real FastMCP objects)."""
    import importlib

    names = set()
    for server in servers:
        module = importlib.import_module(cli.SERVERS[server])
        names.update(t.name for t in asyncio.run(module.mcp.list_tools()))
    return names


def test_every_server_has_a_routing_note():
    assert set(SERVER_NOTES) == set(cli.SERVERS)


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_instructions_name_only_tools_the_mounted_servers_expose(profile):
    servers = resolve_profile(profile)
    mounted = _mounted_tools(servers)
    text = build_instructions(servers)
    # The check must not pass vacuously: tool names are really found in the text.
    found = extract_tool_names(text, known=mounted)
    assert found, "instructions contain no backticked tool names"
    assert unknown_tool_names(text, known=mounted) == []
    # ...and every mounted server contributes at least one tool name.
    for server in servers:
        server_tools = _mounted_tools([server])
        assert extract_tool_names(SERVER_NOTES[server], known=mounted) & server_tools, server


@pytest.mark.parametrize("server", sorted(cli.SERVERS))
def test_note_only_names_its_own_servers_tools(server):
    own = _mounted_tools([server])
    assert unknown_tool_names(SERVER_NOTES[server], known=own) == []


def test_global_guidance_names_no_tools():
    assert extract_tool_names(GLOBAL_GUIDANCE) == set()


def test_unmounted_server_notes_are_left_out():
    text = build_instructions(["audition"])
    assert SERVER_NOTES["audition"] in text
    assert SERVER_NOTES["browse"] not in text
    assert "create_wwise_objects" not in text


def test_order_follows_input_and_duplicates_are_dropped():
    text = build_instructions(["objects", "browse", "objects"])
    assert text.count(SERVER_NOTES["objects"]) == 1
    assert text.index(SERVER_NOTES["objects"]) < text.index(SERVER_NOTES["browse"])


def test_unknown_server_raises():
    with pytest.raises(ValueError, match="nope"):
        build_instructions(["browse", "nope"])


def test_browse_note_keeps_the_root_path_gotcha():
    assert "from_path" in SERVER_NOTES["browse"]


def test_admin_instructions_size_is_reported_and_under_budget(record_property):
    size = len(build_instructions(resolve_profile("admin")))
    record_property("admin_instructions_chars", size)
    print(f"\nadmin instructions size: {size} chars (budget {ADMIN_BUDGET_CHARS})")
    assert size <= ADMIN_BUDGET_CHARS


# --- both launch paths send instructions (via the FastMCP instance) ---

class _FakeRun:
    """Stops mcp.run() from starting stdio; records the call."""

    def __init__(self, monkeypatch):
        self.calls = []
        from fastmcp import FastMCP

        monkeypatch.setattr(
            FastMCP, "run", lambda self_, *a, **k: self.calls.append((self_, a, k))
        )


def _launch(monkeypatch, argv):
    run = _FakeRun(monkeypatch)
    monkeypatch.setattr(sys, "argv", argv)
    cli.main()
    assert len(run.calls) == 1
    return run.calls[0][0]


def test_single_server_launch_sends_instructions(monkeypatch):
    import mcp_audition.server as audition

    monkeypatch.setattr(audition.mcp, "instructions", audition.mcp.instructions)
    server = _launch(monkeypatch, ["sk-wwise-mcp", "--server", "audition"])
    assert server is audition.mcp
    assert server.instructions == build_instructions(["audition"])


def test_multi_server_launch_sends_instructions(monkeypatch):
    server = _launch(monkeypatch, ["sk-wwise-mcp", "--profile", "listen"])
    assert server.instructions == build_instructions(resolve_profile("listen"))
    assert SERVER_NOTES["browse"] in server.instructions
    assert SERVER_NOTES["objects"] not in server.instructions


def test_default_all_in_one_launch_sends_instructions(monkeypatch):
    server = _launch(monkeypatch, ["sk-wwise-mcp"])
    assert server.instructions == build_instructions(list(cli.SERVERS))


# --- skills carry the profile guard line ---

def _expected_profiles(server):
    return [p for p in PROFILE_NAMES if server in PROFILES[p]]


@pytest.mark.parametrize("server", sorted(cli.SERVERS))
def test_skill_has_profile_guard_line_naming_correct_profiles(server):
    text = (REPO_ROOT / ".claude" / "skills" / f"wwise-{server}" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    lines = [l for l in text.splitlines() if l.startswith("**Missing tools?**")]
    assert len(lines) == 1, f"wwise-{server}: expected one 'Missing tools?' guard line"
    named = re.findall(r"`(listen|author|build|qa|admin)`", lines[0])
    assert named == _expected_profiles(server)


def test_guard_line_helper_matches_profile_table():
    assert _expected_profiles("browse") == list(PROFILE_NAMES)
    assert _expected_profiles("command-line") == ["build", "admin"]
    assert _expected_profiles("profiling") == ["qa", "admin"]
