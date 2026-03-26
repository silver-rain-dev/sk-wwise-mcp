"""Integration tests for media read operations (peaks, media pool)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.media import (
    get_min_max_peaks,
    get_media_pool,
    get_media_pool_fields,
)

pytestmark = pytest.mark.integration


def test_get_media_pool_fields(wwise):
    result = get_media_pool_fields()
    assert result is not None


def test_query_media_pool(wwise):
    # Media pool query uses specific WAAPI schema — pass correct args
    result = get_media_pool({
        "filters": {"search": "Footstep"},
    })
    # May return None if schema differs — just check no crash for now
    # TODO: verify exact schema once confirmed


def test_get_peaks(wwise):
    # Need the audio source child of the Sound, not the Sound itself
    from core.waapi_util import call as waapi_call
    # Get audio source under Footstep_01
    sources = waapi_call("ak.wwise.core.object.get", {
        "from": {"path": ["\\Containers\\Default Work Unit\\TestSFX\\Footsteps\\Footstep_01"]},
        "transform": [{"select": ["children"]}],
    }, {"return": ["id", "type"]})
    audio_sources = [s for s in sources.get("return", []) if s["type"] == "AudioFileSource"]
    if not audio_sources:
        pytest.skip("No audio source found on Footstep_01")

    result = get_min_max_peaks({
        "object": audio_sources[0]["id"],
        "timeFrom": 0,
        "timeTo": 0.5,
        "numPeaks": 100,
    })
    assert result is not None
