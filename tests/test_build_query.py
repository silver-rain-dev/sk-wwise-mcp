import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_browse.server import build_waapi_query


def test_from_path():
    result = build_waapi_query(from_path=["\\Actor-Mixer Hierarchy"])
    assert result["from"] == {"path": ["\\Actor-Mixer Hierarchy"]}


def test_from_type():
    result = build_waapi_query(from_type=["Sound"])
    assert result["from"] == {"ofType": ["Sound"]}


def test_path_takes_priority_over_type():
    result = build_waapi_query(from_path=["\\Events"], from_type=["Sound"])
    assert result["from"] == {"path": ["\\Events"]}


def test_default_return_fields():
    result = build_waapi_query(from_path=["\\Events"])
    assert result["options"]["return"] == ["id", "name", "type", "path", "shortId"]


def test_custom_return_fields():
    result = build_waapi_query(from_path=["\\Events"], return_fields=["id", "name"])
    assert result["options"]["return"] == ["id", "name"]


def test_select_transform():
    result = build_waapi_query(from_path=["\\Events"], select_transform="descendants")
    assert result["transform"] == [{"select": ["descendants"]}]


def test_no_transform_by_default():
    result = build_waapi_query(from_path=["\\Events"])
    assert "transform" not in result


def test_where_name_contains():
    result = build_waapi_query(from_path=["\\Events"], where_name_contains="footstep")
    assert {"name": {"contains": "footstep"}} in result["where"]


def test_where_type_is():
    result = build_waapi_query(from_path=["\\Events"], where_type_is=["Event"])
    assert {"type": {"isIn": ["Event"]}} in result["where"]


def test_combined_where_filters():
    result = build_waapi_query(
        from_path=["\\Events"],
        where_name_contains="footstep",
        where_type_is=["Event"],
    )
    assert len(result["where"]) == 2


def test_no_where_by_default():
    result = build_waapi_query(from_path=["\\Events"])
    assert "where" not in result


def test_no_from():
    result = build_waapi_query()
    assert "from" not in result
    assert "options" in result
