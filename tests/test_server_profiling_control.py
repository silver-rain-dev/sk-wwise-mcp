import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from waapi import CannotConnectToWaapiException
from mcp_profiling_control.server import (
    stop_profiler_capture, start_profiler_capture, save_profiler_capture,
    enable_wwise_profiler_data, register_profiler_meter,
    unregister_profiler_meter, set_profiler_cursor,
)


@patch("mcp_profiling_control.server._start_capture")
def test_start_capture(m):
    m.return_value = {"return": 1000}
    assert start_profiler_capture()["return"] == 1000

@patch("mcp_profiling_control.server._start_capture", side_effect=CannotConnectToWaapiException)
def test_start_capture_error(m):
    assert "error" in start_profiler_capture()

@patch("mcp_profiling_control.server._stop_capture")
def test_stop_capture(m):
    m.return_value = {"return": 5000}
    assert stop_profiler_capture()["return"] == 5000

@patch("mcp_profiling_control.server._stop_capture", side_effect=CannotConnectToWaapiException)
def test_stop_capture_error(m):
    assert "error" in stop_profiler_capture()

@patch("mcp_profiling_control.server._save_capture")
def test_save_capture(m):
    m.return_value = {}
    save_profiler_capture(file="C:/test.prof")
    m.assert_called_once_with({"file": "C:/test.prof"})

@patch("mcp_profiling_control.server._save_capture", side_effect=CannotConnectToWaapiException)
def test_save_capture_error(m):
    assert "error" in save_profiler_capture(file="C:/test.prof")

@patch("mcp_profiling_control.server._enable_profiler_data")
def test_enable_profiler_data(m):
    m.return_value = {}
    enable_wwise_profiler_data(data_types=[{"dataType": "cpu"}])
    m.assert_called_once_with({"dataTypes": [{"dataType": "cpu"}]})

@patch("mcp_profiling_control.server._enable_profiler_data", side_effect=CannotConnectToWaapiException)
def test_enable_profiler_data_error(m):
    assert "error" in enable_wwise_profiler_data(data_types=[])

@patch("mcp_profiling_control.server._register_meter")
def test_register_meter(m):
    m.return_value = {}
    register_profiler_meter(object="Bus:Master")
    m.assert_called_once_with({"object": "Bus:Master"})

@patch("mcp_profiling_control.server._register_meter", side_effect=CannotConnectToWaapiException)
def test_register_meter_error(m):
    assert "error" in register_profiler_meter(object="Bus:Master")

@patch("mcp_profiling_control.server._unregister_meter")
def test_unregister_meter(m):
    m.return_value = {}
    unregister_profiler_meter(object="Bus:Master")
    m.assert_called_once_with({"object": "Bus:Master"})

@patch("mcp_profiling_control.server._unregister_meter", side_effect=CannotConnectToWaapiException)
def test_unregister_meter_error(m):
    assert "error" in unregister_profiler_meter(object="Bus:Master")

@patch("mcp_profiling_control.server._move_cursor")
def test_set_cursor_position(m):
    m.return_value = {"return": 0}
    set_profiler_cursor(position="first")
    m.assert_called_once_with({"position": "first"})

@patch("mcp_profiling_control.server._set_cursor_time")
def test_set_cursor_time(m):
    m.return_value = {"return": 500}
    result = set_profiler_cursor(time_ms=500)
    m.assert_called_once_with({"time": 500})
    assert result["return"] == 500

def test_set_cursor_no_args():
    result = set_profiler_cursor()
    assert "error" in result
