import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from waapi import CannotConnectToWaapiException
from mcp_browse.server import (
    build_object_info_query,
    get_wwise_object_info,
    get_wwise_attenuation_curve,
    build_property_reference_query,
    build_property_info_query,
    get_property_and_reference_names,
    get_wwise_property_info,
    diff_wwise_objects,
    is_wwise_property_linked,
    is_wwise_property_enabled,
    get_wwise_object_types,
    get_wwise_installation_info,
    get_wwise_project_info,
)


def test_build_object_info_query_returns_dict():
    result = build_object_info_query(from_path=["\\Events"])
    assert isinstance(result, dict)
    assert "from" in result


def test_build_property_reference_query_returns_dict():
    result = build_property_reference_query(object_path="\\Events\\Play")
    assert result["object"] == "\\Events\\Play"


@patch("mcp_browse.server.execute_object_query")
@patch("mcp_browse.server.summarize_and_save")
def test_get_wwise_object_info_success(mock_summarize, mock_execute):
    mock_execute.return_value = [{"id": "a"}]
    mock_summarize.return_value = {"total_count": 1}
    result = get_wwise_object_info({"from": {"path": ["\\Events"]}})
    assert result["total_count"] == 1


@patch("mcp_browse.server.execute_object_query", side_effect=CannotConnectToWaapiException)
def test_get_wwise_object_info_connection_error(mock_execute):
    result = get_wwise_object_info({"from": {"path": ["\\Events"]}})
    assert "error" in result


@patch("mcp_browse.server.get_object_property")
def test_get_property_and_reference_names_success(mock_prop):
    mock_prop.return_value = {"properties": ["Volume"]}
    result = get_property_and_reference_names({"object": "\\Events\\Play"})
    assert result["properties"] == ["Volume"]


@patch("mcp_browse.server.get_object_property", side_effect=CannotConnectToWaapiException)
def test_get_property_and_reference_names_connection_error(mock_prop):
    result = get_property_and_reference_names({"object": "\\Events\\Play"})
    assert "error" in result


@patch("mcp_browse.server.get_installation_info")
def test_get_wwise_installation_info_success(mock_info):
    mock_info.return_value = {"version": {"year": 2025}}
    result = get_wwise_installation_info()
    assert result["version"]["year"] == 2025


@patch("mcp_browse.server.get_installation_info", side_effect=CannotConnectToWaapiException)
def test_get_wwise_installation_info_connection_error(mock_info):
    result = get_wwise_installation_info()
    assert "error" in result


@patch("mcp_browse.server.get_project_info")
def test_get_wwise_project_info_success(mock_info):
    mock_info.return_value = {"name": "MyProject"}
    result = get_wwise_project_info()
    assert result["name"] == "MyProject"


@patch("mcp_browse.server.get_project_info", side_effect=CannotConnectToWaapiException)
def test_get_wwise_project_info_connection_error(mock_info):
    result = get_wwise_project_info()
    assert "error" in result


# --- get_wwise_attenuation_curve ---

@patch("mcp_browse.server._get_attenuation_curve")
def test_get_wwise_attenuation_curve_success(mock_curve):
    mock_curve.return_value = {"curveType": "VolumeDryUsage", "use": "Custom", "points": []}
    result = get_wwise_attenuation_curve(
        curve_type="VolumeDryUsage",
        object_path="\\Attenuations\\Att_Footstep",
    )
    assert result["curveType"] == "VolumeDryUsage"
    mock_curve.assert_called_once_with({
        "curveType": "VolumeDryUsage",
        "object": "\\Attenuations\\Att_Footstep",
    })


@patch("mcp_browse.server._get_attenuation_curve")
def test_get_wwise_attenuation_curve_with_platform(mock_curve):
    mock_curve.return_value = {"curveType": "VolumeDryUsage", "use": "Custom", "points": []}
    result = get_wwise_attenuation_curve(
        curve_type="VolumeDryUsage",
        object_path="\\Attenuations\\Att_Footstep",
        platform="Windows",
    )
    mock_curve.assert_called_once_with({
        "curveType": "VolumeDryUsage",
        "object": "\\Attenuations\\Att_Footstep",
        "platform": "Windows",
    })


@patch("mcp_browse.server._get_attenuation_curve", side_effect=CannotConnectToWaapiException)
def test_get_wwise_attenuation_curve_connection_error(mock_curve):
    result = get_wwise_attenuation_curve(curve_type="VolumeDryUsage", object_path="\\test")
    assert "error" in result


# --- build_property_info_query ---

def test_build_property_info_query_returns_dict():
    result = build_property_info_query(property_name="Volume", object_path="\\path\\Sound")
    assert result["property"] == "Volume"
    assert result["object"] == "\\path\\Sound"


def test_build_property_info_query_by_guid():
    result = build_property_info_query(property_name="Pitch", object_guid="{aabb-1122}")
    assert result["object"] == "{aabb-1122}"


# --- get_wwise_property_info ---

@patch("mcp_browse.server._get_property_info")
def test_get_wwise_property_info_success(mock_info):
    mock_info.return_value = {"type": "Real64", "default": 0.0, "min": -200.0, "max": 12.0}
    result = get_wwise_property_info({"object": "\\path\\Sound", "property": "Volume"})
    assert result["type"] == "Real64"


@patch("mcp_browse.server._get_property_info", side_effect=CannotConnectToWaapiException)
def test_get_wwise_property_info_connection_error(mock_info):
    result = get_wwise_property_info({"object": "\\path\\Sound", "property": "Volume"})
    assert "error" in result


# --- diff_wwise_objects ---

@patch("mcp_browse.server._diff_objects")
def test_diff_wwise_objects_success(mock_diff):
    mock_diff.return_value = {"properties": ["Volume"], "lists": []}
    result = diff_wwise_objects(source_path="\\path\\SoundA", target_path="\\path\\SoundB")
    assert result["properties"] == ["Volume"]
    mock_diff.assert_called_once_with({"source": "\\path\\SoundA", "target": "\\path\\SoundB"})


@patch("mcp_browse.server._diff_objects")
def test_diff_wwise_objects_by_guid(mock_diff):
    mock_diff.return_value = {"properties": [], "lists": []}
    result = diff_wwise_objects(source_guid="{guid1}", target_guid="{guid2}")
    mock_diff.assert_called_once_with({"source": "{guid1}", "target": "{guid2}"})


@patch("mcp_browse.server._diff_objects", side_effect=CannotConnectToWaapiException)
def test_diff_wwise_objects_connection_error(mock_diff):
    result = diff_wwise_objects(source_path="\\a", target_path="\\b")
    assert "error" in result


# --- is_wwise_property_linked ---

@patch("mcp_browse.server._is_property_linked")
def test_is_wwise_property_linked_success(mock_linked):
    mock_linked.return_value = {"linked": True}
    result = is_wwise_property_linked(
        property_name="Volume", platform="Windows",
        object_path="\\path\\Sound",
    )
    assert result["linked"] is True
    mock_linked.assert_called_once_with({
        "property": "Volume", "platform": "Windows",
        "object": "\\path\\Sound",
    })


@patch("mcp_browse.server._is_property_linked", side_effect=CannotConnectToWaapiException)
def test_is_wwise_property_linked_connection_error(mock_linked):
    result = is_wwise_property_linked(property_name="Volume", platform="Windows", object_path="\\test")
    assert "error" in result


# --- is_wwise_property_enabled ---

@patch("mcp_browse.server._is_property_enabled")
def test_is_wwise_property_enabled_success(mock_enabled):
    mock_enabled.return_value = {"return": True}
    result = is_wwise_property_enabled(
        property_name="Volume", platform="Windows",
        object_path="\\path\\Sound",
    )
    assert result["return"] is True


@patch("mcp_browse.server._is_property_enabled")
def test_is_wwise_property_enabled_by_name_with_type(mock_enabled):
    mock_enabled.return_value = {"return": False}
    result = is_wwise_property_enabled(
        property_name="Pitch", platform="PS5",
        object_name_with_type="Sound:Footstep",
    )
    mock_enabled.assert_called_once_with({
        "property": "Pitch", "platform": "PS5",
        "object": "Sound:Footstep",
    })


@patch("mcp_browse.server._is_property_enabled", side_effect=CannotConnectToWaapiException)
def test_is_wwise_property_enabled_connection_error(mock_enabled):
    result = is_wwise_property_enabled(property_name="Volume", platform="Windows", object_path="\\test")
    assert "error" in result


# --- get_wwise_object_types ---

@patch("mcp_browse.server._get_object_types")
def test_get_wwise_object_types_success(mock_types):
    mock_types.return_value = {"return": [{"classId": 1, "name": "Sound", "type": "Sound"}]}
    result = get_wwise_object_types()
    assert len(result["return"]) == 1


@patch("mcp_browse.server._get_object_types", side_effect=CannotConnectToWaapiException)
def test_get_wwise_object_types_connection_error(mock_types):
    result = get_wwise_object_types()
    assert "error" in result
