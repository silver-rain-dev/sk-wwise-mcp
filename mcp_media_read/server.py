import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.media import get_min_max_peaks, get_min_max_peaks_trimmed
from typing import Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name = "SK Wwise MCP Media Read")


@mcp.tool()
def get_audio_source_peaks(
    num_peaks: int,
    object_path: Optional[str] = None,
    object_guid: Optional[str] = None,
    object_name_with_type: Optional[str] = None,
    time_from: Optional[float] = None,
    time_to: Optional[float] = None,
    get_cross_channel_peaks: bool = False,
) -> dict:
    """Get min/max peak pairs of an audio source, as base-64 encoded binary strings (one per channel).
    The strings are 16-bit signed int arrays with min and max values interleaved.
    If getCrossChannelPeaks is true, only one string represents peaks across all channels globally.

    Read-only — does not modify the project.
    Use this to analyze waveform data, check loudness levels, or inspect audio content
    without needing to open the source file directly.

    If time_from and time_to are provided, peaks are returned for that specific time range.
    If omitted, peaks are returned for the entire trimmed region (respecting Wwise trim markers).

    Args:
        num_peaks:              Number of peak data points to return (minimum 1).
                                More peaks = higher resolution waveform data.
        object_path:            Project path to the audio source object.
                                e.g. "\\Actor-Mixer Hierarchy\\Default Work Unit\\Footstep"
        object_guid:            GUID of the audio source object.
        object_name_with_type:  type:name. e.g. "Sound:Footstep_Walk"
        time_from:              Optional start time in seconds. Must be < time_to.
                                If omitted (along with time_to), uses the trimmed region.
        time_to:                Optional end time in seconds. Must be > time_from.
                                If omitted (along with time_from), uses the trimmed region.
        get_cross_channel_peaks: When true, peaks are calculated globally across all channels
                                instead of per channel. Default false.

    Provide exactly one of object_path, object_guid, or object_name_with_type.

    Returns:
        peaksBinaryStrings: array of base-64 encoded binary strings, one per channel
        numChannels:        number of channels (1 if getCrossChannelPeaks is true)
        maxAbsValue:        maximum peak value — divide peaks by this to normalize to [-1, 1]
        peaksArrayLength:   actual number of peaks returned (may be < num_peaks if fewer samples available)
        peaksDataSize:      size of data in peak arrays — use with peaksArrayLength to decode to int16 arrays
        channelConfig:      the channel configuration string"""
    query = {"numPeaks": num_peaks}
    if object_path:
        query["object"] = object_path
    elif object_guid:
        query["object"] = object_guid
    elif object_name_with_type:
        query["object"] = object_name_with_type
    if get_cross_channel_peaks:
        query["getCrossChannelPeaks"] = True

    try:
        if time_from is not None and time_to is not None:
            query["timeFrom"] = time_from
            query["timeTo"] = time_to
            return get_min_max_peaks(query)
        else:
            return get_min_max_peaks_trimmed(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
