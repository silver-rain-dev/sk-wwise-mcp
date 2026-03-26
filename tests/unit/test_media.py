import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.media import get_min_max_peaks, get_min_max_peaks_trimmed, get_media_pool, get_media_pool_fields


# --- get_min_max_peaks ---

@patch("core.media.call")
def test_get_min_max_peaks(mock_call):
    mock_call.return_value = {"peaksBinaryStrings": ["abc"], "numChannels": 1}
    query = {"object": "\\path\\Sound", "timeFrom": 0, "timeTo": 1, "numPeaks": 100}
    result = get_min_max_peaks(query)
    assert result["numChannels"] == 1
    mock_call.assert_called_once_with("ak.wwise.core.audioSourcePeaks.getMinMaxPeaksInRegion", query)


# --- get_min_max_peaks_trimmed ---

@patch("core.media.call")
def test_get_min_max_peaks_trimmed(mock_call):
    mock_call.return_value = {"peaksBinaryStrings": ["abc"], "numChannels": 2}
    query = {"object": "\\path\\Sound", "numPeaks": 50}
    result = get_min_max_peaks_trimmed(query)
    assert result["numChannels"] == 2
    mock_call.assert_called_once_with("ak.wwise.core.audioSourcePeaks.getMinMaxPeaksInTrimmedRegion", query)


# --- get_media_pool ---

@patch("core.media.call")
def test_get_media_pool(mock_call):
    mock_call.return_value = {"return": [{"Filename": "footstep.wav"}]}
    query = {"searchText": "footstep"}
    result = get_media_pool(query)
    assert len(result["return"]) == 1
    mock_call.assert_called_once_with("ak.wwise.core.mediaPool.get", query)


# --- get_media_pool_fields ---

@patch("core.media.call")
def test_get_media_pool_fields(mock_call):
    mock_call.return_value = {"return": ["Filename", "WAV/Duration", "WAV/Sample Rate"]}
    result = get_media_pool_fields()
    assert "Filename" in result["return"]
    mock_call.assert_called_once_with("ak.wwise.core.mediaPool.getFields")
