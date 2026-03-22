from typing import Optional
from core.waapi_util import call


def bring_to_foreground() -> dict:
    """Bring the Wwise application window to the foreground."""
    return call("ak.wwise.ui.bringToForeground")


def capture_screen(rect: Optional[dict] = None) -> dict:
    """Capture a screenshot of the Wwise UI."""
    args = {}
    if rect:
        args["rect"] = rect
    return call("ak.wwise.ui.captureScreen", args)


def get_selected_objects(return_fields: list[str] = ["id", "name", "type", "path"]) -> dict:
    """Get the currently selected objects in the Wwise UI."""
    options = {"return": return_fields}
    return call("ak.wwise.ui.getSelectedObjects", {}, options)


def get_selected_files() -> dict:
    """Get the files currently selected in the Wwise UI."""
    return call("ak.wwise.ui.getSelectedFiles")


def execute_command(command: str, objects: Optional[list[str]] = None, platforms: Optional[list[str]] = None, languages: Optional[list[str]] = None) -> dict:
    """Execute a Wwise UI command by name."""
    args = {"command": command}
    if objects:
        args["objects"] = objects
    if platforms:
        args["platforms"] = platforms
    if languages:
        args["languages"] = languages
    return call("ak.wwise.ui.commands.execute", args)


def get_commands() -> dict:
    """Get the list of all available UI commands in Wwise."""
    return call("ak.wwise.ui.commands.getCommands")


def get_current_layout_name() -> dict:
    """Get the name of the current Wwise UI layout."""
    return call("ak.wwise.ui.layout.getCurrentLayoutName")


def get_layout_names() -> dict:
    """Get all available Wwise UI layout names."""
    return call("ak.wwise.ui.layout.getLayoutNames")


def switch_layout(layout_name: str) -> dict:
    """Switch the Wwise UI to a different layout."""
    return call("ak.wwise.ui.layout.switchLayout", {"layoutName": layout_name})


def get_view_types() -> dict:
    """Get all available view types in the Wwise UI."""
    return call("ak.wwise.ui.layout.getViewTypes")


def get_view_instances() -> dict:
    """Get all currently open view instances in the Wwise UI."""
    return call("ak.wwise.ui.layout.getViewInstances")


def open_project(path: str) -> dict:
    """Open a Wwise project file."""
    return call("ak.wwise.ui.project.open", {"path": path})


def close_project() -> dict:
    """Close the currently open Wwise project."""
    return call("ak.wwise.ui.project.close")
