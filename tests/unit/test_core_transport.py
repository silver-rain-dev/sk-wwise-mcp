import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.transport import (
    create_transport,
    prepare_transport,
    destroy_transport,
    get_transport_list,
    get_transport_state,
    execute_transport_action,
)


@patch("core.transport.call")
def test_create_transport(mock_call):
    mock_call.return_value = {"transport": 1}
    result = create_transport({"object": "\\path\\Sound"})
    assert result["transport"] == 1
    mock_call.assert_called_once_with("ak.wwise.core.transport.create", {"object": "\\path\\Sound"})


@patch("core.transport.call")
def test_prepare_transport(mock_call):
    mock_call.return_value = {}
    prepare_transport({"transport": 1})
    mock_call.assert_called_once_with("ak.wwise.core.transport.prepare", {"transport": 1})


@patch("core.transport.call")
def test_destroy_transport(mock_call):
    mock_call.return_value = {}
    destroy_transport({"transport": 1})
    mock_call.assert_called_once_with("ak.wwise.core.transport.destroy", {"transport": 1})


@patch("core.transport.call")
def test_get_transport_list(mock_call):
    mock_call.return_value = {"list": [{"transport": 1, "object": "{guid}"}]}
    result = get_transport_list()
    assert len(result["list"]) == 1
    mock_call.assert_called_once_with("ak.wwise.core.transport.getList")


@patch("core.transport.call")
def test_get_transport_state(mock_call):
    mock_call.return_value = {"state": "playing"}
    result = get_transport_state({"transport": 1})
    assert result["state"] == "playing"
    mock_call.assert_called_once_with("ak.wwise.core.transport.getState", {"transport": 1})


@patch("core.transport.call")
def test_execute_transport_action(mock_call):
    mock_call.return_value = {}
    execute_transport_action({"action": "play", "transport": 1})
    mock_call.assert_called_once_with("ak.wwise.core.transport.executeAction", {"action": "play", "transport": 1})
