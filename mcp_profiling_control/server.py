import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.profiling import (
    register_meter as _register_meter,
    unregister_meter as _unregister_meter,
    move_cursor as _move_cursor,
    set_cursor_time as _set_cursor_time,
    enable_profiler_data as _enable_profiler_data,
    stop_capture as _stop_capture,
    start_capture as _start_capture,
    save_capture as _save_capture,
)
from typing import Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name="SK Wwise MCP Profiling Control")


@mcp.tool()
def enable_wwise_profiler_data(
    data_types: list[dict],
):
    """Specify which types of profiler data to capture. Overrides the user's profiler settings.

    Args:
        data_types: Array of data type entries. Each requires "dataType", optionally "enable" (default true).
                    Available data types:
                      "cpu", "memory", "stream", "voices", "listener",
                      "obstructionOcclusion", "markersNotification", "soundbanks",
                      "loadedMedia", "preparedObjects", "preparedGameSyncs",
                      "interactiveMusic", "streamingDevice", "meter",
                      "auxiliarySends", "apiCalls", "spatialAudio",
                      "spatialAudioRaycasting", "voiceInspector", "audioObjects",
                      "gameSyncs", "customerSupportData"

                    Example:
                      [{"dataType": "cpu", "enable": true},
                       {"dataType": "voices", "enable": true},
                       {"dataType": "memory", "enable": false}]"""
    try:
        return _enable_profiler_data({"dataTypes": data_types})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool
def stop_profiler_capture():
    """Stop profiler capture and return the capture end time. No arguments required.

    Returns {"return": int} — the Capture Time Cursor position in milliseconds."""
    try:
        return _stop_capture()
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool
def start_profiler_capture():
    """Start profiler capture and return the capture start time. No arguments required.

    Returns {"return": int} — the Capture Time Cursor position in milliseconds."""
    try:
        return _start_capture()
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def save_profiler_capture(
    file: str,
):
    """Save the current profiler capture to a .prof file.

    Args:
        file: Absolute path to save the .prof file.
              e.g. "C:/captures/session_2026-03-24.prof\""""
    try:
        return _save_capture({"file": file})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def register_profiler_meter(
    object: str,
):
    """Register a bus, aux bus, or device to receive meter data from the profiler.

    Only the Main Audio Bus is registered by default. Call this before using get_profiler_meters.
    Every register call must have a matching unregister_profiler_meter call.

    Args:
        object: The bus/aux bus/device to register. Accepts:
                - path: "\\Busses\\Default Work Unit\\SFX_Bus"
                - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                - type:name: "Bus:SFX_Bus", "AuxBus:Reverb\""""
    try:
        return _register_meter({"object": object})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def unregister_profiler_meter(
    object: str,
):
    """Unregister a bus, aux bus, or device from receiving meter data.

    Must match a previous register_profiler_meter call.

    Args:
        object: The bus/aux bus/device to unregister. Same formats as register_profiler_meter."""
    try:
        return _unregister_meter({"object": object})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def set_profiler_cursor(
    position: Optional[str] = None,
    time_ms: Optional[int] = None,
):
    """Move the user time cursor in the profiler. Provide either position OR time_ms.

    Args:
        position: Move cursor to a relative position:
                  "first"    — first captured frame
                  "last"     — last captured frame
                  "next"     — next frame
                  "previous" — previous frame
        time_ms:  Set cursor to a specific time in milliseconds.
                  The time will be snapped to the nearest buffer interval (~10ms).

    Returns {"return": int} — the new cursor position in milliseconds."""
    try:
        if time_ms is not None:
            return _set_cursor_time({"time": time_ms})
        elif position:
            return _move_cursor({"position": position})
        else:
            return {"error": "Provide either 'position' or 'time_ms'."}
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
