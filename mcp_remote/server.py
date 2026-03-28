import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.profiling import (
    get_available_consoles as _get_available_consoles,
    get_connection_status as _get_connection_status,
    connect_remote as _connect_remote,
    disconnect_remote as _disconnect_remote,
)
from typing import Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name="SK Wwise MCP Remote")


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True})
def get_available_remote_consoles():
    """Get a list of running Wwise/game instances available for remote connection. No arguments required.

    Use this to discover devkits, remote game instances, or other Wwise processes on the network
    before connecting for profiling.

    Returns {"consoles": [...]} — array of remote consoles, each containing:
        name:           Name of the remote console
        platform:       Platform (e.g. "Windows", "PS5", "XboxSeriesX")
        customPlatform: Platform as defined in project settings
        host:           IPv4 address or file path (for local profiler sessions)
        appName:        Name of the connected application (use when connecting to a specific instance)
        commandPort:    Command port number (0-65535) for connecting to a specific instance"""
    try:
        return _get_available_consoles()
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": True})
def connect_to_remote(
    host: str,
    app_name: Optional[str] = None,
    command_port: Optional[int] = None,
):
    """Connect Wwise to a remote Sound Engine instance or a saved profile (.prof) file.

    Use get_available_remote_consoles first to discover available instances.

    Args:
        host:         Host to connect to. Accepts:
                      - Computer name: "DEVKIT-PS5-01"
                      - IPv4: "192.168.1.100"
                      - IP:PORT: "192.168.1.100:24024"
                      - Localhost: "127.0.0.1"
                      - Saved profile: "C:/captures/session.prof"
        app_name:     Application name to connect to (from get_available_remote_consoles).
                      Use when multiple Sound Engine instances are running on the same host.
        command_port: Command port (0-65535) to distinguish between instances sharing the
                      same app_name. Must also provide app_name when using this.
                      Get from get_available_remote_consoles."""
    query = {"host": host}
    if app_name:
        query["appName"] = app_name
    if command_port is not None:
        query["commandPort"] = command_port
    try:
        return _connect_remote(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_remote_connection_status():
    """Get the current remote connection status. No arguments required.

    Returns:
        isConnected: true if connected to a remote Sound Engine instance
        status:      connection status text
        console:     (when connected) remote console info — name, platform, customPlatform, host, appName"""
    try:
        return _get_connection_status()
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": True})
def disconnect_from_remote():
    """Disconnect Wwise from a connected remote Sound Engine instance. No arguments required."""
    try:
        return _disconnect_remote()
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
