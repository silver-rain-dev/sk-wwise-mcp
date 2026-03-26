"""Integration tests for audition (transport) operations."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.transport import (
    create_transport,
    destroy_transport,
    execute_transport_action,
    get_transport_list,
)

pytestmark = pytest.mark.integration


def test_create_and_destroy_transport(wwise):
    result = create_transport({"object": "Event:Play_Footstep"})
    assert "transport" in result
    transport_id = result["transport"]

    destroy_result = destroy_transport({"transport": transport_id})
    assert destroy_result is not None


def test_transport_play_stop(wwise):
    result = create_transport({"object": "Event:Play_Footstep"})
    tid = result["transport"]

    play_result = execute_transport_action({"action": "play", "transport": tid})
    assert play_result is not None

    stop_result = execute_transport_action({"action": "stop", "transport": tid})
    assert stop_result is not None

    destroy_transport({"transport": tid})


def test_list_transports(wwise):
    result = create_transport({"object": "Event:Play_Footstep"})
    tid = result["transport"]

    transports = get_transport_list()
    assert "list" in transports
    assert len(transports["list"]) >= 1

    destroy_transport({"transport": tid})
