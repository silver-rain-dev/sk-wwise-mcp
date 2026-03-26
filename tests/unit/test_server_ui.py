import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from waapi import CannotConnectToWaapiException
from mcp_ui.server import (
    bring_to_foreground,
    capture_screen,
    get_selected_objects,
    get_selected_files,
    execute_command,
    get_commands,
    get_current_layout_name,
    get_layout_names,
    switch_layout,
    get_view_types,
    get_view_instances,
    open_project,
    close_project,
)

import core.ui as _ui_module


@patch.object(_ui_module, "call")
def test_bring_to_foreground_success(mock_call):
    mock_call.return_value = {}
    assert bring_to_foreground() == {}


@patch.object(_ui_module, "call", side_effect=CannotConnectToWaapiException)
def test_bring_to_foreground_error(mock_call):
    result = bring_to_foreground()
    assert "error" in result


@patch.object(_ui_module, "call")
def test_capture_screen_success(mock_call):
    mock_call.return_value = {"image": "data"}
    assert capture_screen()["image"] == "data"


@patch.object(_ui_module, "call", side_effect=CannotConnectToWaapiException)
def test_capture_screen_error(mock_call):
    result = capture_screen()
    assert "error" in result


@patch.object(_ui_module, "call")
def test_get_selected_objects_success(mock_call):
    mock_call.return_value = {"objects": [{"id": "a"}]}
    result = get_selected_objects()
    assert len(result["objects"]) == 1


@patch.object(_ui_module, "call", side_effect=CannotConnectToWaapiException)
def test_get_selected_objects_error(mock_call):
    result = get_selected_objects()
    assert "error" in result


@patch.object(_ui_module, "call")
def test_get_selected_files_success(mock_call):
    mock_call.return_value = {"files": []}
    assert get_selected_files() == {"files": []}


@patch.object(_ui_module, "call", side_effect=CannotConnectToWaapiException)
def test_get_selected_files_error(mock_call):
    result = get_selected_files()
    assert "error" in result


@patch.object(_ui_module, "call")
def test_execute_command_success(mock_call):
    mock_call.return_value = {}
    assert execute_command("SomeCmd") == {}


@patch.object(_ui_module, "call", side_effect=CannotConnectToWaapiException)
def test_execute_command_error(mock_call):
    result = execute_command("SomeCmd")
    assert "error" in result


@patch.object(_ui_module, "call")
def test_get_commands_success(mock_call):
    mock_call.return_value = {"commands": []}
    assert get_commands() == {"commands": []}


@patch.object(_ui_module, "call", side_effect=CannotConnectToWaapiException)
def test_get_commands_error(mock_call):
    result = get_commands()
    assert "error" in result


@patch.object(_ui_module, "call")
def test_get_current_layout_name_success(mock_call):
    mock_call.return_value = {"layoutName": "Designer"}
    assert get_current_layout_name()["layoutName"] == "Designer"


@patch.object(_ui_module, "call", side_effect=CannotConnectToWaapiException)
def test_get_current_layout_name_error(mock_call):
    result = get_current_layout_name()
    assert "error" in result


@patch.object(_ui_module, "call")
def test_get_layout_names_success(mock_call):
    mock_call.return_value = {"layoutNames": ["A", "B"]}
    assert len(get_layout_names()["layoutNames"]) == 2


@patch.object(_ui_module, "call", side_effect=CannotConnectToWaapiException)
def test_get_layout_names_error(mock_call):
    result = get_layout_names()
    assert "error" in result


@patch.object(_ui_module, "call")
def test_switch_layout_success(mock_call):
    mock_call.return_value = {}
    assert switch_layout("Profiler") == {}


@patch.object(_ui_module, "call", side_effect=CannotConnectToWaapiException)
def test_switch_layout_error(mock_call):
    result = switch_layout("Profiler")
    assert "error" in result


@patch.object(_ui_module, "call")
def test_get_view_types_success(mock_call):
    mock_call.return_value = {"viewTypes": []}
    assert get_view_types() == {"viewTypes": []}


@patch.object(_ui_module, "call", side_effect=CannotConnectToWaapiException)
def test_get_view_types_error(mock_call):
    result = get_view_types()
    assert "error" in result


@patch.object(_ui_module, "call")
def test_get_view_instances_success(mock_call):
    mock_call.return_value = {"viewInstances": []}
    assert get_view_instances() == {"viewInstances": []}


@patch.object(_ui_module, "call", side_effect=CannotConnectToWaapiException)
def test_get_view_instances_error(mock_call):
    result = get_view_instances()
    assert "error" in result


@patch.object(_ui_module, "call")
def test_open_project_success(mock_call):
    mock_call.return_value = {}
    assert open_project("C:\\test.wproj") == {}


@patch.object(_ui_module, "call", side_effect=CannotConnectToWaapiException)
def test_open_project_error(mock_call):
    result = open_project("C:\\test.wproj")
    assert "error" in result


@patch.object(_ui_module, "call")
def test_close_project_success(mock_call):
    mock_call.return_value = {}
    assert close_project() == {}


@patch.object(_ui_module, "call", side_effect=CannotConnectToWaapiException)
def test_close_project_error(mock_call):
    result = close_project()
    assert "error" in result
