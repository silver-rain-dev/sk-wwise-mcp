import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from waapi import CannotConnectToWaapiException
from mcp_remote.server import (
    get_available_remote_consoles, connect_to_remote,
    get_remote_connection_status, disconnect_from_remote,
)


@patch("mcp_remote.server._get_available_consoles")
def test_get_consoles(m):
    m.return_value = {"consoles": [{"name": "PC", "host": "127.0.0.1"}]}
    assert len(get_available_remote_consoles()["consoles"]) == 1

@patch("mcp_remote.server._get_available_consoles", side_effect=CannotConnectToWaapiException)
def test_get_consoles_error(m):
    assert "error" in get_available_remote_consoles()

@patch("mcp_remote.server._connect_remote")
def test_connect(m):
    m.return_value = {}
    connect_to_remote(host="127.0.0.1")
    m.assert_called_once_with({"host": "127.0.0.1"})

@patch("mcp_remote.server._connect_remote")
def test_connect_with_app(m):
    m.return_value = {}
    connect_to_remote(host="192.168.1.100", app_name="MyGame", command_port=24024)
    m.assert_called_once_with({"host": "192.168.1.100", "appName": "MyGame", "commandPort": 24024})

@patch("mcp_remote.server._connect_remote", side_effect=CannotConnectToWaapiException)
def test_connect_error(m):
    assert "error" in connect_to_remote(host="bad")

@patch("mcp_remote.server._get_connection_status")
def test_connection_status(m):
    m.return_value = {"isConnected": True, "status": "Connected"}
    assert get_remote_connection_status()["isConnected"]

@patch("mcp_remote.server._get_connection_status", side_effect=CannotConnectToWaapiException)
def test_connection_status_error(m):
    assert "error" in get_remote_connection_status()

@patch("mcp_remote.server._disconnect_remote")
def test_disconnect(m):
    m.return_value = {}
    disconnect_from_remote()
    m.assert_called_once()

@patch("mcp_remote.server._disconnect_remote", side_effect=CannotConnectToWaapiException)
def test_disconnect_error(m):
    assert "error" in disconnect_from_remote()
