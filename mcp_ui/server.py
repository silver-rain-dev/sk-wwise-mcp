import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.ui import (
    bring_to_foreground as _bring_to_foreground,
    capture_screen as _capture_screen,
    get_selected_objects as _get_selected_objects,
    get_selected_files as _get_selected_files,
    execute_command as _execute_command,
    get_commands as _get_commands,
    get_current_layout_name as _get_current_layout_name,
    get_layout_names as _get_layout_names,
    switch_layout as _switch_layout,
    get_view_types as _get_view_types,
    get_view_instances as _get_view_instances,
    open_project as _open_project,
    close_project as _close_project,
)
from typing import Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name = "SK Wwise MCP UI")

_WAAPI_ERROR = {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}

@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def bring_to_foreground():
    """Bring the Wwise application window to the foreground."""
    try:
        return _bring_to_foreground()
    except CannotConnectToWaapiException:
        return _WAAPI_ERROR

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False})
def capture_screen(rect: Optional[dict] = None):
    """Capture a screenshot of the Wwise UI.

    Args:
        rect: Optional rectangle dict with x, y, width, height to capture a specific region.
    """
    try:
        return _capture_screen(rect)
    except CannotConnectToWaapiException:
        return _WAAPI_ERROR

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_selected_objects(return_fields: list[str] = ["id", "name", "type", "path"]):
    """Get the currently selected objects in the Wwise UI.

    Args:
        return_fields: Fields to return per object. Common: "id", "name", "type", "path", "shortId"
    """
    try:
        return _get_selected_objects(return_fields)
    except CannotConnectToWaapiException:
        return _WAAPI_ERROR

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_selected_files():
    """Get the files currently selected in the Wwise UI (e.g. in the Source Editor)."""
    try:
        return _get_selected_files()
    except CannotConnectToWaapiException:
        return _WAAPI_ERROR

@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": False})
def execute_command(command: str, objects: Optional[list[str]] = None, platforms: Optional[list[str]] = None, languages: Optional[list[str]] = None):
    """Execute a Wwise UI command by name.

    Args:
        command:   The command to execute (e.g. "FindInProjectExplorerSyncGroup1").
        objects:   Optional list of object GUIDs to pass as context.
        platforms: Optional list of platform GUIDs.
        languages: Optional list of language GUIDs.
    """
    try:
        return _execute_command(command, objects, platforms, languages)
    except CannotConnectToWaapiException:
        return _WAAPI_ERROR

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_commands():
    """Get the list of all available UI commands in Wwise."""
    try:
        return _get_commands()
    except CannotConnectToWaapiException:
        return _WAAPI_ERROR

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_current_layout_name():
    """Get the name of the current Wwise UI layout."""
    try:
        return _get_current_layout_name()
    except CannotConnectToWaapiException:
        return _WAAPI_ERROR

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_layout_names():
    """Get all available Wwise UI layout names."""
    try:
        return _get_layout_names()
    except CannotConnectToWaapiException:
        return _WAAPI_ERROR

@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def switch_layout(layout_name: str):
    """Switch the Wwise UI to a different layout.

    Args:
        layout_name: Name of the layout to switch to.
    """
    try:
        return _switch_layout(layout_name)
    except CannotConnectToWaapiException:
        return _WAAPI_ERROR

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_view_types():
    """Get all available view types in the Wwise UI (e.g. 'Property Editor', 'Transport Control')."""
    try:
        return _get_view_types()
    except CannotConnectToWaapiException:
        return _WAAPI_ERROR

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_view_instances():
    """Get all currently open view instances in the Wwise UI."""
    try:
        return _get_view_instances()
    except CannotConnectToWaapiException:
        return _WAAPI_ERROR

@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def open_project(path: str):
    """Open a Wwise project file.

    Args:
        path: Full path to the .wproj file.
    """
    try:
        return _open_project(path)
    except CannotConnectToWaapiException:
        return _WAAPI_ERROR

@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": False})
def close_project():
    """Close the currently open Wwise project."""
    try:
        return _close_project()
    except CannotConnectToWaapiException:
        return _WAAPI_ERROR


if __name__ == "__main__":
    mcp.run(transport="stdio")
