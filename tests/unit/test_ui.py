import sys
from pathlib import Path
from unittest.mock import patch, call as mock_call_obj
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ui import (
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


@patch("core.ui.call")
def test_bring_to_foreground(mock_call):
    mock_call.return_value = {}
    result = bring_to_foreground()
    assert result == {}
    mock_call.assert_called_once_with("ak.wwise.ui.bringToForeground")


@patch("core.ui.call")
def test_capture_screen_no_rect(mock_call):
    mock_call.return_value = {"image": "base64data"}
    result = capture_screen()
    assert result["image"] == "base64data"
    mock_call.assert_called_once_with("ak.wwise.ui.captureScreen", {})


@patch("core.ui.call")
def test_capture_screen_with_rect(mock_call):
    mock_call.return_value = {"image": "base64data"}
    rect = {"x": 0, "y": 0, "width": 100, "height": 100}
    capture_screen(rect=rect)
    mock_call.assert_called_once_with("ak.wwise.ui.captureScreen", {"rect": rect})


@patch("core.ui.call")
def test_get_selected_objects_default_fields(mock_call):
    mock_call.return_value = {"objects": [{"id": "a", "name": "Foo"}]}
    get_selected_objects()
    mock_call.assert_called_once_with(
        "ak.wwise.ui.getSelectedObjects", {}, {"return": ["id", "name", "type", "path"]}
    )


@patch("core.ui.call")
def test_get_selected_objects_custom_fields(mock_call):
    mock_call.return_value = {"objects": []}
    get_selected_objects(return_fields=["id", "name"])
    mock_call.assert_called_once_with(
        "ak.wwise.ui.getSelectedObjects", {}, {"return": ["id", "name"]}
    )


@patch("core.ui.call")
def test_get_selected_files(mock_call):
    mock_call.return_value = {"files": ["/path/to/file.wav"]}
    result = get_selected_files()
    assert result["files"] == ["/path/to/file.wav"]
    mock_call.assert_called_once_with("ak.wwise.ui.getSelectedFiles")


@patch("core.ui.call")
def test_execute_command_basic(mock_call):
    mock_call.return_value = {}
    execute_command("FindInProjectExplorerSyncGroup1")
    mock_call.assert_called_once_with(
        "ak.wwise.ui.commands.execute", {"command": "FindInProjectExplorerSyncGroup1"}
    )


@patch("core.ui.call")
def test_execute_command_with_objects(mock_call):
    mock_call.return_value = {}
    execute_command("FindInProjectExplorerSyncGroup1", objects=["{guid1}", "{guid2}"])
    args = mock_call.call_args[0][1]
    assert args["objects"] == ["{guid1}", "{guid2}"]


@patch("core.ui.call")
def test_execute_command_with_platforms_and_languages(mock_call):
    mock_call.return_value = {}
    execute_command("SomeCommand", platforms=["{plat1}"], languages=["{lang1}"])
    args = mock_call.call_args[0][1]
    assert args["platforms"] == ["{plat1}"]
    assert args["languages"] == ["{lang1}"]


@patch("core.ui.call")
def test_get_commands(mock_call):
    mock_call.return_value = {"commands": [{"id": "cmd1"}]}
    result = get_commands()
    assert len(result["commands"]) == 1
    mock_call.assert_called_once_with("ak.wwise.ui.commands.getCommands")


@patch("core.ui.call")
def test_get_current_layout_name(mock_call):
    mock_call.return_value = {"layoutName": "Designer"}
    result = get_current_layout_name()
    assert result["layoutName"] == "Designer"
    mock_call.assert_called_once_with("ak.wwise.ui.layout.getCurrentLayoutName")


@patch("core.ui.call")
def test_get_layout_names(mock_call):
    mock_call.return_value = {"layoutNames": ["Designer", "Profiler"]}
    result = get_layout_names()
    assert "Designer" in result["layoutNames"]
    mock_call.assert_called_once_with("ak.wwise.ui.layout.getLayoutNames")


@patch("core.ui.call")
def test_switch_layout(mock_call):
    mock_call.return_value = {}
    switch_layout("Profiler")
    mock_call.assert_called_once_with("ak.wwise.ui.layout.switchLayout", {"layoutName": "Profiler"})


@patch("core.ui.call")
def test_get_view_types(mock_call):
    mock_call.return_value = {"viewTypes": ["PropertyEditor", "TransportControl"]}
    result = get_view_types()
    assert "PropertyEditor" in result["viewTypes"]
    mock_call.assert_called_once_with("ak.wwise.ui.layout.getViewTypes")


@patch("core.ui.call")
def test_get_view_instances(mock_call):
    mock_call.return_value = {"viewInstances": [{"id": "v1"}]}
    result = get_view_instances()
    assert len(result["viewInstances"]) == 1
    mock_call.assert_called_once_with("ak.wwise.ui.layout.getViewInstances")


@patch("core.ui.call")
def test_open_project(mock_call):
    mock_call.return_value = {}
    open_project("C:\\Projects\\MyGame.wproj")
    mock_call.assert_called_once_with("ak.wwise.ui.project.open", {"path": "C:\\Projects\\MyGame.wproj"})


@patch("core.ui.call")
def test_close_project(mock_call):
    mock_call.return_value = {}
    close_project()
    mock_call.assert_called_once_with("ak.wwise.ui.project.close")
