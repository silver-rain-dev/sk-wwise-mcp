import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.query import execute_object_query, get_object_property, get_installation_info, get_project_info


@patch("core.query.call")
def test_execute_object_query_returns_list(mock_call):
    mock_call.return_value = {"return": [{"id": "a", "name": "Foo"}]}
    result = execute_object_query({"from": {"path": ["\\Events"]}})
    assert result == [{"id": "a", "name": "Foo"}]
    mock_call.assert_called_once_with("ak.wwise.core.object.get", {"from": {"path": ["\\Events"]}})


@patch("core.query.call")
def test_execute_object_query_empty(mock_call):
    mock_call.return_value = {"return": []}
    result = execute_object_query({"from": {"path": ["\\Events"]}})
    assert result == []


@patch("core.query.call")
def test_execute_object_query_missing_return_key(mock_call):
    mock_call.return_value = {}
    result = execute_object_query({"from": {"path": ["\\Events"]}})
    assert result == []


@patch("core.query.call")
def test_get_object_property(mock_call):
    mock_call.return_value = {"properties": ["Volume", "Pitch"], "references": ["OutputBus"]}
    query = {"object": "\\Actor-Mixer Hierarchy\\Default Work Unit\\Footstep"}
    result = get_object_property(query)
    assert result["properties"] == ["Volume", "Pitch"]
    mock_call.assert_called_once_with("ak.wwise.core.object.getPropertyAndReferenceNames", query)


@patch("core.query.call")
def test_get_installation_info(mock_call):
    mock_call.return_value = {"version": {"year": 2025, "major": 1}, "platform": "x64"}
    result = get_installation_info()
    assert result["platform"] == "x64"
    mock_call.assert_called_once_with("ak.wwise.core.getInfo")


@patch("core.query.call")
def test_get_project_info(mock_call):
    mock_call.return_value = {"name": "MyProject", "defaultLanguage": "English(US)"}
    result = get_project_info()
    assert result["name"] == "MyProject"
    mock_call.assert_called_once_with("ak.wwise.core.getProjectInfo")
