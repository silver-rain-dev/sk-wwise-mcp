import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.profiling import (
    get_loaded_media as _get_loaded_media,
    get_game_objects as _get_game_objects,
    get_cursor_time as _get_cursor_time,
    get_streamed_media as _get_streamed_media,
    get_rtpcs as _get_rtpcs,
    get_performance_monitor as _get_performance_monitor,
    get_meters as _get_meters,
    get_cpu_usage as _get_cpu_usage,
    get_busses as _get_busses,
    get_audio_objects as _get_audio_objects,
    get_voices as _get_voices,
    get_voice_contributions as _get_voice_contributions,
)
from typing import Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name="SK Wwise MCP Profiling")


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_profiler_loaded_media(
    time: int | str = "capture",
):
    """Retrieve loaded media files at a specific profiler capture time.

    Equivalent to the Loaded Media tab in the Advanced Profiler.
    Requires "loadedMedia" profiler data capture to be enabled.

    Args:
        time: Time to query. Either:
              - milliseconds (int): specific capture time
              - "user": the user-controlled profiler cursor
              - "capture": the latest capture time (default)

    Returns {"return": [...]} — array of loaded media, each containing:
        mediaId:   short ID of the media file
        fileName:  name of the media file
        format:    audio format (e.g. "Vorbis", "PCM")
        size:      size in bytes
        soundBank: name of the SoundBank containing this media"""
    try:
        return _get_loaded_media({"time": time})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_profiler_game_objects(
    time: int | str = "capture",
):
    """Retrieve game objects at a specific profiler capture time.

    Args:
        time: Time to query. Either:
              - milliseconds (int): specific capture time
              - "user": the user-controlled profiler cursor
              - "capture": the latest capture time (default)

    Returns {"return": [...]} — array of game objects, each containing:
        id:             game object ID (unsigned 64-bit)
        name:           game object name
        registerTime:   time (ms) when the game object was registered
        unregisterTime: time (ms) when the game object was unregistered"""
    try:
        return _get_game_objects({"time": time})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_profiler_cursor_time(
    cursor: str = "capture",
):
    """Get the current time of a profiler cursor, in milliseconds.

    Args:
        cursor: Which cursor to query:
                "user"    — the cursor the user can drag in the profiler timeline
                "capture" — the latest time of the current capture (default)

    Returns {"return": int} — the cursor position in milliseconds."""
    try:
        return _get_cursor_time({"cursor": cursor})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_profiler_streamed_media(
    time: int | str = "capture",
):
    """Retrieve streaming media info at a specific profiler capture time.

    Equivalent to the Streams tab in the Advanced Profiler.
    Requires "stream" profiler data capture to be enabled.

    Args:
        time: Time to query. Either:
              - milliseconds (int): specific capture time
              - "user": the user-controlled profiler cursor
              - "capture": the latest capture time (default)

    Returns {"return": [...]} — array of streams, each containing:
        deviceName:          streaming device name
        streamName:          name of the stream
        fileSize:            size of the streamed file (bytes)
        filePosition:        position within the file (percentage)
        priority:            stream priority
        bandwidthTotal:      total streaming rate (bytes/s, includes cache)
        bandwidthLowLevel:   low-level device streaming rate (bytes/s)
        referencedMemory:    memory referenced by the stream (bytes)
        estimatedThroughput: estimated data consumption rate (bytes/s)
        active:              true if stream was active in last profiling frame
        targetBufferSize:    device's target buffer length (bytes)
        bufferStatusBuffered: portion of data buffered (% of target)"""
    try:
        return _get_streamed_media({"time": time})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_profiler_rtpcs(
    time: int | str = "capture",
):
    """Retrieve active RTPCs (Game Parameters, LFOs, Envelopes, etc.) at a specific profiler capture time.

    Args:
        time: Time to query. Either:
              - milliseconds (int): specific capture time
              - "user": the user-controlled profiler cursor
              - "capture": the latest capture time (default)

    Returns {"return": [...]} — array of active RTPCs, each containing:
        id:           GUID of the Game Parameter / LFO / Envelope / MIDI Parameter
        name:         name of the parameter
        gameObjectId: game object ID for scoped RTPCs (AK_INVALID_GAME_OBJECT for global)
        value:        current value at the queried time"""
    try:
        return _get_rtpcs({"time": time})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_profiler_performance_monitor(
    time: int | str = "capture",
):
    """Retrieve Performance Monitor statistics at a specific profiler capture time.

    Returns all available counters (total voices, virtual voices, CPU %, memory, etc.).

    Args:
        time: Time to query. Either:
              - milliseconds (int): specific capture time
              - "user": the user-controlled profiler cursor
              - "capture": the latest capture time (default)

    Returns {"return": [...]} — array of counters, each containing:
        name:  counter name as shown in Wwise (e.g. "Total Voices", "Virtual Voices")
        id:    unique counter identifier
        value: counter value at the given time"""
    try:
        return _get_performance_monitor({"time": time})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_profiler_meters(
    time: int | str = "capture",
    return_fields: list[str] = ["id", "name", "path"],
):
    """Retrieve meter data for all registered busses, aux busses, and devices.

    Only the Main Audio Bus is registered by default. Use ak.wwise.core.profiler.registerMeter
    (via mcp_generic) for other busses before retrieving meter data.
    Requires "meter" profiler data capture to be enabled.

    Args:
        time:          Time to query. Either:
                       - milliseconds (int): specific capture time
                       - "user": the user-controlled profiler cursor
                       - "capture": the latest capture time (default)
        return_fields: Fields to return for the metered object.
                       Default: ["id", "name", "path"]

    Returns {"meters": [...]} — array of meter entries, each containing:
        object:  the metered Wwise object (with requested return fields)
        peak:    array of peak values per channel (dB)
        rms:     array of RMS values per channel (dB)
        truePeak: array of true peak values per channel (dB)"""
    query = {"time": time}
    options = {"return": return_fields}
    try:
        return _get_meters(query, options)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_profiler_cpu_usage(
    time: int | str = "capture",
):
    """Retrieve CPU usage statistics at a specific profiler capture time.

    Requires "cpu" profiler data capture to be enabled (use enable_wwise_profiler_data).
    Equivalent to the CPU tab in the Advanced Profiler.

    Args:
        time: Time to query. Either:
              - milliseconds (int): specific capture time
              - "user": the user-controlled profiler cursor
              - "capture": the latest capture time (default)

    Returns {"return": [...]} — array of CPU stats per element, each containing:
        elementName:          name of the element (codec, effect, etc.)
        id:                   class ID of the element
        instances:            estimated number of active instances
        type:                 element type — "Codec", "Source", "Effect", "Mixer", or "Sink"
        percentInclusive:     CPU % including called elements
        percentExclusive:     CPU % for only this element
        millisecondsInclusive: CPU ms including called elements
        millisecondsExclusive: CPU ms for only this element"""
    try:
        return _get_cpu_usage({"time": time})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_profiler_busses(
    time: int | str = "capture",
    bus_pipeline_id: Optional[int] = None,
    return_fields: list[str] = ["pipelineID", "objectGUID", "objectName",
                                 "gameObjectName", "volume", "voiceCount", "depth"],
):
    """Retrieve bus instances at a specific profiler capture time.

    Args:
        time:            Time to query. Either:
                         - milliseconds (int): specific capture time
                         - "user": the user-controlled profiler cursor
                         - "capture": the latest capture time (default)
        bus_pipeline_id: Optional pipeline ID of a specific bus instance to get.
        return_fields:   Fields to return per bus. Available:
                         "pipelineID", "mixBusID", "objectGUID", "objectName",
                         "gameObjectID", "gameObjectName", "deviceID",
                         "volume", "downstreamGain", "voiceCount",
                         "effectCount", "depth"

    Returns {"return": [...]} — array of bus objects with requested fields."""
    query = {"time": time}
    if bus_pipeline_id is not None:
        query["busPipelineID"] = bus_pipeline_id
    options = {"return": return_fields}
    try:
        return _get_busses(query, options)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_profiler_audio_objects(
    time: int | str = "capture",
    bus_pipeline_id: Optional[int] = None,
    return_fields: list[str] = ["audioObjectID", "busPipelineID", "busName",
                                 "gameObjectName", "audioObjectName",
                                 "channelConfig", "x", "y", "z"],
):
    """Retrieve Audio Objects at a specific profiler capture time.

    Requires profiler data capture to be enabled (use enable_wwise_profiler_data with "audioObjects").

    Args:
        time:            Time to query. Either:
                         - milliseconds (int): specific capture time
                         - "user": the user-controlled profiler cursor
                         - "capture": the latest capture time (default)
        bus_pipeline_id: Optional pipeline ID of a specific Bus instance to filter by.
        return_fields:   Fields to return per Audio Object. Available:
                         "busName", "effectPluginName", "audioObjectID", "busPipelineID",
                         "gameObjectID", "gameObjectName", "audioObjectName",
                         "instigatorPipelineID", "busID", "busGUID",
                         "spatializationMode", "x", "y", "z", "spread", "focus",
                         "channelConfig", "effectClassID", "effectIndex",
                         "metadata", "rmsMeter", "peakMeter"

    Returns {"return": [...]} — array of Audio Objects with requested fields."""
    query = {"time": time}
    if bus_pipeline_id is not None:
        query["busPipelineID"] = bus_pipeline_id
    options = {"return": return_fields}
    try:
        return _get_audio_objects(query, options)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_profiler_voices(
    time: int | str = "capture",
    voice_pipeline_id: Optional[int] = None,
    return_fields: list[str] = ["pipelineID", "objectGUID", "objectName",
                                 "gameObjectName", "baseVolume", "priority",
                                 "isVirtual", "isStarted"],
):
    """Retrieve playing voices at a specific profiler capture time.

    Requires "voices" profiler data capture to be enabled.

    Args:
        time:              Time to query. Either:
                           - milliseconds (int): specific capture time
                           - "user": the user-controlled profiler cursor
                           - "capture": the latest capture time (default)
        voice_pipeline_id: Optional pipeline ID of a specific voice to get.
        return_fields:     Fields to return per voice. Available:
                           "pipelineID", "playingID", "soundID", "gameObjectID",
                           "gameObjectName", "objectGUID", "objectName",
                           "playTargetID", "playTargetGUID", "playTargetName",
                           "baseVolume", "gameAuxSendVolume", "envelope",
                           "normalizationGain", "lowPassFilter", "highPassFilter",
                           "priority", "isStarted", "isVirtual", "isForcedVirtual"

    Returns {"return": [...]} — array of voices with requested fields."""
    query = {"time": time}
    if voice_pipeline_id is not None:
        query["voicePipelineID"] = voice_pipeline_id
    options = {"return": return_fields}
    try:
        return _get_voices(query, options)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_profiler_voice_contributions(
    voice_pipeline_id: int,
    time: int | str = "capture",
    busses_pipeline_id: Optional[list[int]] = None,
):
    """Retrieve all parameters affecting a voice's volume, highpass, and lowpass along its path.

    Equivalent to the Voice Inspector in the Profiler. Shows the hierarchy of contributions
    from parent objects, RTPCs, states, etc. that affect the final voice output.
    Requires "voiceInspector" profiler data capture to be enabled.

    Args:
        voice_pipeline_id:  Pipeline ID of the voice to inspect.
                            Get from get_profiler_voices.
        time:               Time to query. Either:
                            - milliseconds (int): specific capture time
                            - "user": the user-controlled profiler cursor
                            - "capture": the latest capture time (default)
        busses_pipeline_id: Optional array of bus pipeline IDs defining the voice path.
                            Empty or omitted defaults to the dry path.

    Returns {"return": {...}} containing:
        volume: total volume contribution (dB)
        LPF:    total lowpass filter contribution
        HPF:    total highpass filter contribution
        objects: hierarchy of contributing objects, each with name, volume, LPF, HPF,
                 children, and parameters (propertyType, reason, driver, value)"""
    query = {"voicePipelineID": voice_pipeline_id, "time": time}
    if busses_pipeline_id is not None:
        query["bussesPipelineID"] = busses_pipeline_id
    try:
        return _get_voice_contributions(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
