"""Tests for core.waapi_util module-level functions.

Covers ping(), call(), write_server_lockfile(), _normalize_paths(),
_read_server_lockfile(), _is_process_alive(), and connection management.
The WaapiDispatcher class is tested separately in test_dispatcher.py.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.waapi_util import (
    ping,
    call,
    write_server_lockfile,
    _normalize_paths,
    _read_server_lockfile,
    _is_process_alive,
    _LOCKFILE,
    WaapiQueueFullError,
)


# --- _normalize_paths ---


def test_normalize_paths_double_backslash():
    d = {"path": "\\\\Containers\\\\Default Work Unit"}
    result = _normalize_paths(d)
    assert result["path"] == "\\Containers\\Default Work Unit"


def test_normalize_paths_single_backslash_untouched():
    d = {"path": "\\Containers\\Default Work Unit"}
    result = _normalize_paths(d)
    assert result["path"] == "\\Containers\\Default Work Unit"


def test_normalize_paths_nested_dict():
    d = {"from": {"path": ["\\\\Events\\\\Default Work Unit"]}}
    result = _normalize_paths(d)
    assert result["from"]["path"] == ["\\Events\\Default Work Unit"]


def test_normalize_paths_list_of_strings():
    d = {"items": ["\\\\Events\\\\WU", "\\\\Containers\\\\WU"]}
    result = _normalize_paths(d)
    assert result["items"] == ["\\Events\\WU", "\\Containers\\WU"]


def test_normalize_paths_list_of_dicts():
    d = {"items": [{"path": "\\\\Events\\\\WU"}]}
    result = _normalize_paths(d)
    assert result["items"][0]["path"] == "\\Events\\WU"


def test_normalize_paths_non_string_values():
    d = {"count": 5, "flag": True, "nothing": None}
    result = _normalize_paths(d)
    assert result == d


def test_normalize_paths_empty_dict():
    assert _normalize_paths({}) == {}


def test_normalize_paths_mixed_list():
    d = {"items": ["\\\\Path", 42, {"nested": "\\\\Inner"}]}
    result = _normalize_paths(d)
    assert result["items"][0] == "\\Path"
    assert result["items"][1] == 42
    assert result["items"][2]["nested"] == "\\Inner"


# --- ping ---


@patch("core.waapi_util._get_dispatcher")
def test_ping_success(mock_get):
    mock_dispatcher = MagicMock()
    mock_dispatcher.call.return_value = {"isAvailable": True}
    mock_get.return_value = mock_dispatcher
    result = ping()
    assert result == {"isAvailable": True}
    mock_dispatcher.call.assert_called_once_with("ak.wwise.core.ping", {})


@patch("core.waapi_util._get_dispatcher")
def test_ping_exception_returns_false(mock_get):
    mock_get.side_effect = Exception("No connection")
    result = ping()
    assert result == {"isAvailable": False}


# --- call ---


@patch("core.waapi_util._reconnect")
@patch("core.waapi_util._ensure_connection")
def test_call_basic(mock_ensure, mock_reconnect):
    mock_dispatcher = MagicMock()
    mock_dispatcher.call.return_value = {"return": []}
    mock_ensure.return_value = mock_dispatcher
    result = call("ak.wwise.core.object.get", {"from": {"path": ["\\Events"]}})
    assert result == {"return": []}
    mock_dispatcher.call.assert_called_once()


@patch("core.waapi_util._reconnect")
@patch("core.waapi_util._ensure_connection")
def test_call_merges_options(mock_ensure, mock_reconnect):
    mock_dispatcher = MagicMock()
    mock_dispatcher.call.return_value = {"return": []}
    mock_ensure.return_value = mock_dispatcher
    call(
        "ak.wwise.core.object.get",
        args={"from": {"path": ["\\Events"]}},
        options={"return": ["name"]},
    )
    payload = mock_dispatcher.call.call_args[0][1]
    assert "options" in payload
    assert payload["options"]["return"] == ["name"]


@patch("core.waapi_util._reconnect")
@patch("core.waapi_util._ensure_connection")
def test_call_normalizes_paths(mock_ensure, mock_reconnect):
    mock_dispatcher = MagicMock()
    mock_dispatcher.call.return_value = {}
    mock_ensure.return_value = mock_dispatcher
    call("ak.wwise.core.object.get", {"from": {"path": ["\\\\Events\\\\WU"]}})
    payload = mock_dispatcher.call.call_args[0][1]
    assert payload["from"]["path"] == ["\\Events\\WU"]


@patch("core.waapi_util._reconnect")
@patch("core.waapi_util._ensure_connection")
def test_call_none_args_defaults_to_empty(mock_ensure, mock_reconnect):
    mock_dispatcher = MagicMock()
    mock_dispatcher.call.return_value = {}
    mock_ensure.return_value = mock_dispatcher
    call("ak.wwise.core.ping")
    payload = mock_dispatcher.call.call_args[0][1]
    assert payload == {}


@patch("core.waapi_util._reconnect")
@patch("core.waapi_util._ensure_connection")
def test_call_timeout_triggers_reconnect(mock_ensure, mock_reconnect):
    mock_dispatcher = MagicMock()
    mock_dispatcher.call.side_effect = TimeoutError("timed out")
    mock_ensure.return_value = mock_dispatcher
    try:
        call("ak.wwise.core.object.get", {})
    except TimeoutError:
        pass
    mock_reconnect.assert_called_once()


@patch("core.waapi_util._reconnect")
@patch("core.waapi_util._ensure_connection")
def test_call_queue_full_not_retried(mock_ensure, mock_reconnect):
    mock_dispatcher = MagicMock()
    mock_dispatcher.call.side_effect = WaapiQueueFullError("full")
    mock_ensure.return_value = mock_dispatcher
    try:
        call("ak.wwise.core.object.get", {})
    except WaapiQueueFullError:
        pass
    mock_reconnect.assert_not_called()


@patch("core.waapi_util._reconnect")
@patch("core.waapi_util._ensure_connection")
def test_call_retries_on_generic_exception(mock_ensure, mock_reconnect):
    mock_dispatcher_bad = MagicMock()
    mock_dispatcher_bad.call.side_effect = ConnectionError("lost")
    mock_dispatcher_good = MagicMock()
    mock_dispatcher_good.call.return_value = {"ok": True}
    mock_ensure.side_effect = [mock_dispatcher_bad, mock_dispatcher_good]
    result = call("ak.wwise.core.object.get", {})
    assert result == {"ok": True}
    assert mock_reconnect.call_count == 1


# --- write_server_lockfile / _read_server_lockfile ---


def test_write_and_read_lockfile(tmp_path):
    lockfile = tmp_path / ".waapi_server.lock"
    with patch("core.waapi_util._LOCKFILE", lockfile):
        write_server_lockfile(12345, "C:/project/test.wproj")
        data = json.loads(lockfile.read_text(encoding="utf-8"))
        assert data["pid"] == 12345
        assert data["project_path"] == "C:/project/test.wproj"


def test_read_server_lockfile_missing(tmp_path):
    lockfile = tmp_path / "nonexistent.lock"
    with patch("core.waapi_util._LOCKFILE", lockfile):
        result = _read_server_lockfile()
        assert result is None


def test_read_server_lockfile_invalid_json(tmp_path):
    lockfile = tmp_path / ".waapi_server.lock"
    lockfile.write_text("not json", encoding="utf-8")
    with patch("core.waapi_util._LOCKFILE", lockfile):
        result = _read_server_lockfile()
        assert result is None


# --- _is_process_alive ---


def test_is_process_alive_current_process():
    import os
    assert _is_process_alive(os.getpid()) is True


def test_is_process_alive_invalid_pid():
    assert _is_process_alive(9999999) is False
