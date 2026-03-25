import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.transport import (
    create_transport,
    prepare_transport,
    destroy_transport,
    get_transport_list,
    get_transport_state,
    execute_transport_action,
)
from typing import Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name="SK Wwise MCP Audition")


@mcp.tool()
def create_wwise_transport(
    object_path: Optional[str] = None,
    object_guid: Optional[str] = None,
    object_name_with_type: Optional[str] = None,
    game_object: Optional[int] = None,
) -> dict:
    """Create a transport object for previewing/auditioning a Wwise object.

    A transport is required before you can play, stop, or pause an object.
    Use the returned transport ID with play_transport, stop_transport, etc.

    Args:
        object_path:           Project path to the object to audition.
                               e.g. "\\Actor-Mixer Hierarchy\\Default Work Unit\\Footstep"
        object_guid:           GUID of the object.
        object_name_with_type: type:name. e.g. "Event:Play_Footstep", "Sound:Footstep_Walk"
        game_object:           Optional game object ID (unsigned 64-bit) to use for playback.

    Provide exactly one of object_path, object_guid, or object_name_with_type.

    Returns {"transport": int} — the transport ID (unsigned 32-bit) to use with other transport functions."""
    query = {}
    if object_path:
        query["object"] = object_path
    elif object_guid:
        query["object"] = object_guid
    elif object_name_with_type:
        query["object"] = object_name_with_type
    if game_object is not None:
        query["gameObject"] = game_object
    try:
        result = create_transport(query)
        prepare_transport({"transport": result["transport"]})
        return result
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def destroy_wwise_transport(transport_id: int) -> dict:
    """Destroy a transport object, stopping any playback associated with it.

    Args:
        transport_id: The transport ID (unsigned 32-bit) returned by create_wwise_transport.

    Call this when done auditioning to clean up transport resources."""
    try:
        return destroy_transport({"transport": transport_id})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool
def list_wwise_transports() -> dict:
    """List all active transport objects. No arguments required.

    Returns {"list": [...]} — array of transport objects, each containing:
        transport:  transport ID (unsigned 32-bit)
        object:     GUID of the Wwise object controlled by this transport
        gameObject: game object ID (unsigned 64-bit) used by the transport"""
    try:
        return get_transport_list()
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def execute_wwise_transport_action(
    action: str,
    transport_id: Optional[int] = None,
) -> dict:
    """Execute a playback action on a transport object, or all transports if none specified.

    Args:
        action:       The action to execute. One of:
                      "play"          — start playback
                      "stop"          — stop playback
                      "pause"         — pause playback
                      "playStop"      — toggle play/stop
                      "playDirectly"  — play without virtual voice behavior
        transport_id: Optional transport ID (unsigned 32-bit) from create_wwise_transport.
                      If omitted, the action is applied to ALL active transports."""
    query = {"action": action}
    if transport_id is not None:
        query["transport"] = transport_id
    try:
        return execute_transport_action(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
