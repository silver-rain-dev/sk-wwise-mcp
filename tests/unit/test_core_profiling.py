import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.profiling import (
    get_available_consoles, connect_remote, get_connection_status, disconnect_remote,
    stop_capture, start_capture, save_capture,
    register_meter, unregister_meter, move_cursor, set_cursor_time,
    enable_profiler_data, get_loaded_media, get_game_objects, get_cursor_time,
    get_streamed_media, get_rtpcs, get_performance_monitor, get_meters,
    get_cpu_usage, get_busses, get_audio_objects, get_voices, get_voice_contributions,
)


@patch("core.profiling.call")
def test_get_available_consoles(m):
    m.return_value = {"consoles": []}
    assert get_available_consoles()["consoles"] == []
    m.assert_called_once_with("ak.wwise.core.remote.getAvailableConsoles")

@patch("core.profiling.call")
def test_connect_remote(m):
    m.return_value = {}
    connect_remote({"host": "127.0.0.1"})
    m.assert_called_once_with("ak.wwise.core.remote.connect", {"host": "127.0.0.1"})

@patch("core.profiling.call")
def test_get_connection_status(m):
    m.return_value = {"isConnected": True, "status": "Connected"}
    assert get_connection_status()["isConnected"]

@patch("core.profiling.call")
def test_disconnect_remote(m):
    m.return_value = {}
    disconnect_remote()
    m.assert_called_once_with("ak.wwise.core.remote.disconnect")

@patch("core.profiling.call")
def test_start_capture(m):
    m.return_value = {"return": 1000}
    assert start_capture()["return"] == 1000

@patch("core.profiling.call")
def test_stop_capture(m):
    m.return_value = {"return": 5000}
    assert stop_capture()["return"] == 5000

@patch("core.profiling.call")
def test_save_capture(m):
    m.return_value = {}
    save_capture({"file": "C:/test.prof"})
    m.assert_called_once_with("ak.wwise.core.profiler.saveCapture", {"file": "C:/test.prof"})

@patch("core.profiling.call")
def test_enable_profiler_data(m):
    m.return_value = {}
    enable_profiler_data({"dataTypes": [{"dataType": "cpu"}]})
    m.assert_called_once_with("ak.wwise.core.profiler.enableProfilerData", {"dataTypes": [{"dataType": "cpu"}]})

@patch("core.profiling.call")
def test_register_meter(m):
    m.return_value = {}
    register_meter({"object": "Bus:Master"})
    m.assert_called_once_with("ak.wwise.core.profiler.registerMeter", {"object": "Bus:Master"})

@patch("core.profiling.call")
def test_unregister_meter(m):
    m.return_value = {}
    unregister_meter({"object": "Bus:Master"})
    m.assert_called_once_with("ak.wwise.core.profiler.unregisterMeter", {"object": "Bus:Master"})

@patch("core.profiling.call")
def test_move_cursor(m):
    m.return_value = {"return": 100}
    assert move_cursor({"position": "first"})["return"] == 100

@patch("core.profiling.call")
def test_set_cursor_time(m):
    m.return_value = {"return": 500}
    assert set_cursor_time({"time": 500})["return"] == 500

@patch("core.profiling.call")
def test_get_loaded_media(m):
    m.return_value = {"return": [{"mediaId": 1, "fileName": "a.wem"}]}
    assert len(get_loaded_media({"time": "capture"})["return"]) == 1

@patch("core.profiling.call")
def test_get_game_objects(m):
    m.return_value = {"return": [{"id": 100, "name": "Player"}]}
    assert get_game_objects({"time": "capture"})["return"][0]["name"] == "Player"

@patch("core.profiling.call")
def test_get_cursor_time(m):
    m.return_value = {"return": 2000}
    assert get_cursor_time({"cursor": "capture"})["return"] == 2000

@patch("core.profiling.call")
def test_get_streamed_media(m):
    m.return_value = {"return": []}
    assert get_streamed_media({"time": "capture"})["return"] == []

@patch("core.profiling.call")
def test_get_rtpcs(m):
    m.return_value = {"return": [{"name": "Health", "value": 50}]}
    assert get_rtpcs({"time": "capture"})["return"][0]["value"] == 50

@patch("core.profiling.call")
def test_get_performance_monitor(m):
    m.return_value = {"return": [{"name": "Total Voices", "value": 10}]}
    assert get_performance_monitor({"time": "capture"})["return"][0]["name"] == "Total Voices"

@patch("core.profiling.call")
def test_get_meters(m):
    m.return_value = {"meters": []}
    assert get_meters({"time": "capture"})["meters"] == []

@patch("core.profiling.call")
def test_get_cpu_usage(m):
    m.return_value = {"return": [{"elementName": "Vorbis", "percentExclusive": 1.5}]}
    assert get_cpu_usage({"time": "capture"})["return"][0]["elementName"] == "Vorbis"

@patch("core.profiling.call")
def test_get_busses(m):
    m.return_value = {"return": [{"objectName": "Master"}]}
    assert get_busses({"time": "capture"})["return"][0]["objectName"] == "Master"

@patch("core.profiling.call")
def test_get_audio_objects(m):
    m.return_value = {"return": []}
    assert get_audio_objects({"time": "capture"})["return"] == []

@patch("core.profiling.call")
def test_get_voices(m):
    m.return_value = {"return": [{"pipelineID": 1}]}
    assert get_voices({"time": "capture"})["return"][0]["pipelineID"] == 1

@patch("core.profiling.call")
def test_get_voice_contributions(m):
    m.return_value = {"return": {"volume": -6, "LPF": 0, "HPF": 0, "objects": []}}
    result = get_voice_contributions({"voicePipelineID": 1, "time": "capture"})
    assert result["return"]["volume"] == -6
