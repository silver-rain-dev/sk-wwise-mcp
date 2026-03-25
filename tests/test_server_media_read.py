import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from waapi import CannotConnectToWaapiException
from mcp_media_read.server import (
    get_audio_source_peaks,
    query_media_pool,
    get_media_pool_fields,
)


# --- get_audio_source_peaks (region mode) ---

@patch("mcp_media_read.server.get_min_max_peaks")
def test_get_audio_source_peaks_region(mock_peaks):
    mock_peaks.return_value = {"peaksBinaryStrings": ["abc"], "numChannels": 1}
    result = get_audio_source_peaks(
        num_peaks=100,
        object_path="\\path\\Sound",
        time_from=0.0,
        time_to=1.0,
    )
    assert result["numChannels"] == 1
    mock_peaks.assert_called_once_with({
        "numPeaks": 100,
        "object": "\\path\\Sound",
        "timeFrom": 0.0,
        "timeTo": 1.0,
    })


# --- get_audio_source_peaks (trimmed mode) ---

@patch("mcp_media_read.server.get_min_max_peaks_trimmed")
def test_get_audio_source_peaks_trimmed(mock_peaks):
    mock_peaks.return_value = {"peaksBinaryStrings": ["abc"], "numChannels": 2}
    result = get_audio_source_peaks(
        num_peaks=50,
        object_path="\\path\\Sound",
    )
    assert result["numChannels"] == 2
    mock_peaks.assert_called_once_with({
        "numPeaks": 50,
        "object": "\\path\\Sound",
    })


# --- get_audio_source_peaks with cross channel ---

@patch("mcp_media_read.server.get_min_max_peaks_trimmed")
def test_get_audio_source_peaks_cross_channel(mock_peaks):
    mock_peaks.return_value = {"peaksBinaryStrings": ["abc"], "numChannels": 1}
    result = get_audio_source_peaks(
        num_peaks=50,
        object_guid="{aabb-1122}",
        get_cross_channel_peaks=True,
    )
    mock_peaks.assert_called_once_with({
        "numPeaks": 50,
        "object": "{aabb-1122}",
        "getCrossChannelPeaks": True,
    })


# --- get_audio_source_peaks connection error ---

@patch("mcp_media_read.server.get_min_max_peaks_trimmed", side_effect=CannotConnectToWaapiException)
def test_get_audio_source_peaks_connection_error(mock_peaks):
    result = get_audio_source_peaks(num_peaks=10, object_path="\\test")
    assert "error" in result


# --- query_media_pool ---

@patch("mcp_media_read.server.get_media_pool")
def test_query_media_pool_search_text(mock_pool):
    mock_pool.return_value = {"return": [{"Filename": "footstep.wav"}]}
    result = query_media_pool(search_text="footstep")
    assert len(result["return"]) == 1
    mock_pool.assert_called_once_with({"searchText": "footstep"})


@patch("mcp_media_read.server.get_media_pool")
def test_query_media_pool_with_filters(mock_pool):
    mock_pool.return_value = {"return": []}
    filters = [{"type": "field", "field": "WAV/Sample Rate", "operator": "equals", "value": 48000}]
    result = query_media_pool(filters=filters)
    mock_pool.assert_called_once_with({"filters": filters})


@patch("mcp_media_read.server.get_media_pool")
def test_query_media_pool_with_max_results(mock_pool):
    mock_pool.return_value = {"return": []}
    result = query_media_pool(max_results=10)
    mock_pool.assert_called_once_with({"maxResults": 10})


@patch("mcp_media_read.server.get_media_pool")
def test_query_media_pool_with_databases(mock_pool):
    mock_pool.return_value = {"return": []}
    result = query_media_pool(databases=["\\Databases\\Project Originals"])
    mock_pool.assert_called_once_with({"databases": ["\\Databases\\Project Originals"]})


@patch("mcp_media_read.server.get_media_pool")
def test_query_media_pool_no_args(mock_pool):
    mock_pool.return_value = {"return": []}
    result = query_media_pool()
    mock_pool.assert_called_once_with({})


@patch("mcp_media_read.server.get_media_pool", side_effect=CannotConnectToWaapiException)
def test_query_media_pool_connection_error(mock_pool):
    result = query_media_pool(search_text="test")
    assert "error" in result


# --- get_media_pool_fields ---

@patch("mcp_media_read.server._get_media_pool_fields")
def test_get_media_pool_fields_success(mock_fields):
    mock_fields.return_value = {"return": ["Filename", "WAV/Duration", "WAV/Sample Rate"]}
    result = get_media_pool_fields()
    assert "Filename" in result["return"]
    assert len(result["return"]) == 3


@patch("mcp_media_read.server._get_media_pool_fields", side_effect=CannotConnectToWaapiException)
def test_get_media_pool_fields_connection_error(mock_fields):
    result = get_media_pool_fields()
    assert "error" in result
