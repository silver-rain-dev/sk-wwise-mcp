import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.tool_names import (
    extract_tool_names,
    known_tool_names,
    unknown_tool_names,
    unknown_tool_names_in_files,
)

REPO_ROOT = Path(__file__).parent.parent.parent
SKILL_FILES = sorted((REPO_ROOT / ".claude" / "skills").glob("wwise-*/SKILL.md"))


def test_skill_files_found():
    assert len(SKILL_FILES) >= 12


def test_registry_has_all_servers():
    known = known_tool_names()
    assert {"get_wwise_object_info", "call_waapi", "cli_diagnostics", "switch_layout"} <= known


def test_every_tool_name_in_skills_exists():
    bad = unknown_tool_names_in_files(SKILL_FILES)
    report = "\n".join(
        f"{path.relative_to(REPO_ROOT).as_posix()}: {', '.join(names)}"
        for path, names in bad.items()
    )
    assert not bad, f"Unknown tool names in skills:\n{report}"


# --- checker behavior (fixtures, no files) ---

def test_wrong_tool_name_is_flagged():
    text = "Use `query_wwise_objects` to search, then `get_wwise_object_info`."
    assert unknown_tool_names(text) == ["query_wwise_objects"]


def test_wrong_name_in_file_fails_and_names_the_file(tmp_path):
    f = tmp_path / "SKILL.md"
    f.write_text("- `get_wwise_object_info` ok\n- `find_wwise_object` stale\n", encoding="utf-8")
    assert unknown_tool_names_in_files([f]) == {f: ["find_wwise_object"]}


def test_valid_names_pass():
    assert unknown_tool_names("`ping_wwise` and `call_waapi`") == []


def test_non_tool_tokens_are_ignored():
    text = (
        "`ak.wwise.core.object.get` `@OutputBus` `from_path` `parent` "
        "`importLanguage` `Originals/SFX/` `mcp_browse` `list_name` `output_file`"
    )
    assert extract_tool_names(text) == set()


def test_call_syntax_is_checked():
    text = "`build_object_info_query()` then `execute_wwise_transport_action(\"play\")` then `find_wwise_thing()`"
    assert extract_tool_names(text) == {
        "build_object_info_query", "execute_wwise_transport_action", "find_wwise_thing",
    }
    assert unknown_tool_names(text) == ["find_wwise_thing"]


def test_text_outside_backticks_is_ignored():
    assert unknown_tool_names("plain query_wwise_objects mention") == []
