import sys
from pathlib import Path
from unittest.mock import patch, call

sys.path.insert(0, str(Path(__file__).parent.parent))

from waapi import CannotConnectToWaapiException
from mcp_audition.server import (
    create_wwise_transport,
    destroy_wwise_transport,
    list_wwise_transports,
    execute_wwise_transport_action,
)


# --- create_wwise_transport ---


@patch("mcp_audition.server.prepare_transport")
@patch("mcp_audition.server.create_transport")
def test_create_transport_by_path(mock_create, mock_prepare):
    mock_create.return_value = {"transport": 1}
    result = create_wwise_transport(object_path="\\Actor-Mixer Hierarchy\\Default Work Unit\\Sound")
    assert result == {"transport": 1}
    mock_create.assert_called_once_with({"object": "\\Actor-Mixer Hierarchy\\Default Work Unit\\Sound"})
    mock_prepare.assert_called_once_with({"transport": 1})


@patch("mcp_audition.server.prepare_transport")
@patch("mcp_audition.server.create_transport")
def test_create_transport_by_guid(mock_create, mock_prepare):
    mock_create.return_value = {"transport": 2}
    result = create_wwise_transport(object_guid="{aabbcc00-1122-3344-5566-77889900aabb}")
    mock_create.assert_called_once_with({"object": "{aabbcc00-1122-3344-5566-77889900aabb}"})


@patch("mcp_audition.server.prepare_transport")
@patch("mcp_audition.server.create_transport")
def test_create_transport_by_name_with_type(mock_create, mock_prepare):
    mock_create.return_value = {"transport": 3}
    result = create_wwise_transport(object_name_with_type="Event:Play_Footstep")
    mock_create.assert_called_once_with({"object": "Event:Play_Footstep"})


@patch("mcp_audition.server.prepare_transport")
@patch("mcp_audition.server.create_transport")
def test_create_transport_with_game_object(mock_create, mock_prepare):
    mock_create.return_value = {"transport": 4}
    result = create_wwise_transport(object_path="\\path\\Sound", game_object=12345)
    mock_create.assert_called_once_with({"object": "\\path\\Sound", "gameObject": 12345})


@patch("mcp_audition.server.prepare_transport")
@patch("mcp_audition.server.create_transport")
def test_create_transport_game_object_camelcase(mock_create, mock_prepare):
    """gameObject must be camelCase, not snake_case."""
    mock_create.return_value = {"transport": 5}
    create_wwise_transport(object_path="\\path\\Sound", game_object=99)
    args = mock_create.call_args[0][0]
    assert "gameObject" in args
    assert "game_object" not in args


@patch("mcp_audition.server.prepare_transport")
@patch("mcp_audition.server.create_transport")
def test_create_transport_omits_game_object_when_none(mock_create, mock_prepare):
    mock_create.return_value = {"transport": 6}
    create_wwise_transport(object_path="\\path\\Sound")
    args = mock_create.call_args[0][0]
    assert "gameObject" not in args


@patch("mcp_audition.server.prepare_transport")
@patch("mcp_audition.server.create_transport")
def test_create_transport_calls_prepare_after_create(mock_create, mock_prepare):
    """create_wwise_transport must call prepare_transport with the transport ID."""
    mock_create.return_value = {"transport": 7}
    create_wwise_transport(object_path="\\path\\Sound")
    mock_prepare.assert_called_once_with({"transport": 7})


@patch("mcp_audition.server.create_transport", side_effect=CannotConnectToWaapiException)
def test_create_transport_connection_error(mock_create):
    result = create_wwise_transport(object_path="\\test")
    assert "error" in result


# --- destroy_wwise_transport ---


@patch("mcp_audition.server.destroy_transport")
def test_destroy_transport_args(mock_destroy):
    mock_destroy.return_value = {}
    result = destroy_wwise_transport(transport_id=42)
    assert result == {}
    mock_destroy.assert_called_once_with({"transport": 42})


@patch("mcp_audition.server.destroy_transport", side_effect=CannotConnectToWaapiException)
def test_destroy_transport_connection_error(mock_destroy):
    result = destroy_wwise_transport(transport_id=0)
    assert "error" in result


# --- list_wwise_transports ---


@patch("mcp_audition.server.get_transport_list")
def test_list_transports_success(mock_list):
    mock_list.return_value = {"list": [{"transport": 1, "object": "{aabb}"}]}
    result = list_wwise_transports()
    assert len(result["list"]) == 1
    mock_list.assert_called_once_with()


@patch("mcp_audition.server.get_transport_list", side_effect=CannotConnectToWaapiException)
def test_list_transports_connection_error(mock_list):
    result = list_wwise_transports()
    assert "error" in result


# --- execute_wwise_transport_action ---


@patch("mcp_audition.server.execute_transport_action")
def test_execute_action_play(mock_exec):
    mock_exec.return_value = {}
    result = execute_wwise_transport_action(action="play", transport_id=1)
    assert result == {}
    mock_exec.assert_called_once_with({"action": "play", "transport": 1})


@patch("mcp_audition.server.execute_transport_action")
def test_execute_action_without_transport_id(mock_exec):
    """When transport_id is omitted, action applies to ALL transports."""
    mock_exec.return_value = {}
    execute_wwise_transport_action(action="stop")
    mock_exec.assert_called_once_with({"action": "stop"})


@patch("mcp_audition.server.execute_transport_action")
def test_execute_action_omits_transport_when_none(mock_exec):
    mock_exec.return_value = {}
    execute_wwise_transport_action(action="play")
    args = mock_exec.call_args[0][0]
    assert "transport" not in args


@patch("mcp_audition.server.execute_transport_action", side_effect=CannotConnectToWaapiException)
def test_execute_action_connection_error(mock_exec):
    result = execute_wwise_transport_action(action="play")
    assert "error" in result
