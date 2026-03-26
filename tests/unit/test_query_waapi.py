import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.query import (
    build_property_info_query,
    execute_object_query,
    get_attenuation_curve,
    get_object_property,
    get_property_info,
    diff_objects,
    is_property_linked,
    is_property_enabled,
    get_object_types,
    get_installation_info,
    get_project_info,
)


@patch("core.query.call")
def test_execute_object_query_returns_list(mock_call):
    mock_call.return_value = {"return": [{"id": "a", "name": "Foo"}]}
    result = execute_object_query({"from": {"path": ["\\Events"]}})
    assert result == [{"id": "a", "name": "Foo"}]
    mock_call.assert_called_once_with("ak.wwise.core.object.get", {"from": {"path": ["\\Events"]}}, {})


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
    query = {"object": "\\Containers\\Default Work Unit\\Footstep"}
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


# --- build_property_info_query ---

def test_build_property_info_query_by_path():
    result = build_property_info_query("Volume", object_path="\\Containers\\Footstep")
    assert result["property"] == "Volume"
    assert result["object"] == "\\Containers\\Footstep"


def test_build_property_info_query_by_guid():
    result = build_property_info_query("Pitch", object_guid="{aabbcc00-1122-3344-5566-77889900aabb}")
    assert result["property"] == "Pitch"
    assert result["object"] == "{aabbcc00-1122-3344-5566-77889900aabb}"


def test_build_property_info_query_by_name_with_type():
    result = build_property_info_query("Lowpass", object_name_with_type="Sound:Footstep_Walk")
    assert result["object"] == "Sound:Footstep_Walk"


def test_build_property_info_query_with_class_id():
    result = build_property_info_query("Volume", class_id=123)
    assert result["classId"] == 123
    assert "object" not in result


def test_build_property_info_query_path_priority():
    result = build_property_info_query("Volume", object_path="\\path", object_guid="{guid}")
    assert result["object"] == "\\path"


# --- get_attenuation_curve ---

@patch("core.query.call")
def test_get_attenuation_curve(mock_call):
    mock_call.return_value = {
        "curveType": "VolumeDryUsage",
        "use": "Custom",
        "points": [{"x": 0, "y": 0, "shape": "Linear"}, {"x": 100, "y": -200, "shape": "Linear"}]
    }
    query = {"object": "\\Attenuations\\Att_Footstep", "curveType": "VolumeDryUsage"}
    result = get_attenuation_curve(query)
    assert result["curveType"] == "VolumeDryUsage"
    assert len(result["points"]) == 2
    mock_call.assert_called_once_with("ak.wwise.core.object.getAttenuationCurve", query)


# --- get_property_info ---

@patch("core.query.call")
def test_get_property_info(mock_call):
    mock_call.return_value = {"type": "Real64", "default": 0.0, "min": -200.0, "max": 12.0}
    query = {"object": "\\Containers\\Footstep", "property": "Volume"}
    result = get_property_info(query)
    assert result["type"] == "Real64"
    assert result["min"] == -200.0
    mock_call.assert_called_once_with("ak.wwise.core.object.getPropertyInfo", query)


# --- diff_objects ---

@patch("core.query.call")
def test_diff_objects(mock_call):
    mock_call.return_value = {"properties": ["Volume", "Pitch"], "lists": ["Effects"]}
    query = {"source": "\\path\\SoundA", "target": "\\path\\SoundB"}
    result = diff_objects(query)
    assert result["properties"] == ["Volume", "Pitch"]
    assert result["lists"] == ["Effects"]
    mock_call.assert_called_once_with("ak.wwise.core.object.diff", query)


# --- is_property_linked ---

@patch("core.query.call")
def test_is_property_linked(mock_call):
    mock_call.return_value = {"linked": True}
    query = {"object": "\\path\\Sound", "property": "Volume", "platform": "Windows"}
    result = is_property_linked(query)
    assert result["linked"] is True
    mock_call.assert_called_once_with("ak.wwise.core.object.isLinked", query)


# --- is_property_enabled ---

@patch("core.query.call")
def test_is_property_enabled(mock_call):
    mock_call.return_value = {"return": True}
    query = {"object": "\\path\\Sound", "property": "Volume", "platform": "Windows"}
    result = is_property_enabled(query)
    assert result["return"] is True
    mock_call.assert_called_once_with("ak.wwise.core.object.isPropertyEnabled", query)


# --- get_object_types ---

@patch("core.query.call")
def test_get_object_types(mock_call):
    mock_call.return_value = {"return": [
        {"classId": 1, "name": "Sound", "type": "Sound"},
        {"classId": 2, "name": "Event", "type": "Event"},
    ]}
    result = get_object_types()
    assert len(result["return"]) == 2
    mock_call.assert_called_once_with("ak.wwise.core.object.getTypes")
