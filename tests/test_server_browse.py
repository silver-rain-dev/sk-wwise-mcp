import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from waapi import CannotConnectToWaapiException
from mcp_browse.server import (
    build_object_info_query,
    get_wwise_object_info,
    build_property_reference_query,
    get_property_and_reference_names,
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
