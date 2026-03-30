"""Tests for mcp_browse/server.py tools not covered by test_server_browse.py.

Covers ping_wwise, get_switch_container_assignments, get_blend_track_assignments.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_browse.server import (
    ping_wwise,
    get_switch_container_assignments,
    get_blend_track_assignments,
)


# --- ping_wwise ---


@patch("mcp_browse.server._ping")
def test_ping_wwise_available(mock_ping):
    mock_ping.return_value = {"isAvailable": True}
    result = ping_wwise()
    assert result == {"isAvailable": True}
    mock_ping.assert_called_once()


@patch("mcp_browse.server._ping")
def test_ping_wwise_unavailable(mock_ping):
    mock_ping.return_value = {"isAvailable": False}
    result = ping_wwise()
    assert result == {"isAvailable": False}


# --- get_switch_container_assignments ---


@patch("mcp_browse.server._get_switch_assignments")
def test_get_switch_container_assignments_by_path(mock_get):
    mock_get.return_value = [{"child": "Sound1", "stateOrSwitch": "Switch1"}]
    result = get_switch_container_assignments(object_path="\\Containers\\WU\\SC")
    assert len(result) == 1
    assert result[0]["child"] == "Sound1"


@patch("mcp_browse.server._get_switch_assignments")
def test_get_switch_container_assignments_by_guid(mock_get):
    mock_get.return_value = []
    result = get_switch_container_assignments(object_guid="{aabb-1122}")
    mock_get.assert_called_once()
    assert result == []


@patch("mcp_browse.server._get_switch_assignments")
def test_get_switch_container_assignments_by_name(mock_get):
    mock_get.return_value = [{"child": "C1", "stateOrSwitch": "S1"}]
    result = get_switch_container_assignments(object_name_with_type="SwitchContainer:MySC")
    assert len(result) == 1


def test_get_switch_container_assignments_no_identifier():
    result = get_switch_container_assignments()
    assert "error" in result


# --- get_blend_track_assignments ---


@patch("mcp_browse.server._get_blend_assignments")
def test_get_blend_track_assignments_basic(mock_get):
    mock_get.return_value = [{"child": "Sound1", "crossfadeEdge": "front"}]
    result = get_blend_track_assignments(blend_track_guid="{aabb-1122}")
    assert len(result) == 1
    assert result[0]["child"] == "Sound1"
    mock_get.assert_called_once()
