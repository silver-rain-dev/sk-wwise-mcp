import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from waapi import CannotConnectToWaapiException
from mcp_profiling.server import (
    get_profiler_loaded_media, get_profiler_game_objects, get_profiler_cursor_time,
    get_profiler_streamed_media, get_profiler_rtpcs, get_profiler_performance_monitor,
    get_profiler_meters, get_profiler_cpu_usage, get_profiler_busses,
    get_profiler_audio_objects, get_profiler_voices, get_profiler_voice_contributions,
)


@patch("mcp_profiling.server._get_loaded_media")
def test_loaded_media(m):
    m.return_value = {"return": []}
    assert get_profiler_loaded_media()["return"] == []

@patch("mcp_profiling.server._get_loaded_media", side_effect=CannotConnectToWaapiException)
def test_loaded_media_error(m):
    assert "error" in get_profiler_loaded_media()

@patch("mcp_profiling.server._get_game_objects")
def test_game_objects(m):
    m.return_value = {"return": [{"id": 1, "name": "P"}]}
    assert len(get_profiler_game_objects()["return"]) == 1

@patch("mcp_profiling.server._get_game_objects", side_effect=CannotConnectToWaapiException)
def test_game_objects_error(m):
    assert "error" in get_profiler_game_objects()

@patch("mcp_profiling.server._get_cursor_time")
def test_cursor_time(m):
    m.return_value = {"return": 1000}
    assert get_profiler_cursor_time()["return"] == 1000

@patch("mcp_profiling.server._get_cursor_time", side_effect=CannotConnectToWaapiException)
def test_cursor_time_error(m):
    assert "error" in get_profiler_cursor_time()

@patch("mcp_profiling.server._get_streamed_media")
def test_streamed_media(m):
    m.return_value = {"return": []}
    assert get_profiler_streamed_media()["return"] == []

@patch("mcp_profiling.server._get_rtpcs")
def test_rtpcs(m):
    m.return_value = {"return": [{"name": "Health", "value": 50}]}
    assert get_profiler_rtpcs()["return"][0]["value"] == 50

@patch("mcp_profiling.server._get_performance_monitor")
def test_performance_monitor(m):
    m.return_value = {"return": [{"name": "Total Voices", "value": 10}]}
    assert get_profiler_performance_monitor()["return"][0]["value"] == 10

@patch("mcp_profiling.server._get_meters")
def test_meters(m):
    m.return_value = {"meters": []}
    assert get_profiler_meters()["meters"] == []

@patch("mcp_profiling.server._get_cpu_usage")
def test_cpu_usage(m):
    m.return_value = {"return": [{"elementName": "Vorbis"}]}
    assert get_profiler_cpu_usage()["return"][0]["elementName"] == "Vorbis"

@patch("mcp_profiling.server._get_busses")
def test_busses(m):
    m.return_value = {"return": [{"objectName": "Master"}]}
    assert get_profiler_busses()["return"][0]["objectName"] == "Master"

@patch("mcp_profiling.server._get_audio_objects")
def test_audio_objects(m):
    m.return_value = {"return": []}
    assert get_profiler_audio_objects()["return"] == []

@patch("mcp_profiling.server._get_voices")
def test_voices(m):
    m.return_value = {"return": [{"pipelineID": 1}]}
    assert get_profiler_voices()["return"][0]["pipelineID"] == 1

@patch("mcp_profiling.server._get_voices", side_effect=CannotConnectToWaapiException)
def test_voices_error(m):
    assert "error" in get_profiler_voices()

@patch("mcp_profiling.server._get_voice_contributions")
def test_voice_contributions(m):
    m.return_value = {"return": {"volume": -6, "LPF": 0, "HPF": 0, "objects": []}}
    result = get_profiler_voice_contributions(voice_pipeline_id=1)
    assert result["return"]["volume"] == -6

@patch("mcp_profiling.server._get_voice_contributions", side_effect=CannotConnectToWaapiException)
def test_voice_contributions_error(m):
    assert "error" in get_profiler_voice_contributions(voice_pipeline_id=1)
