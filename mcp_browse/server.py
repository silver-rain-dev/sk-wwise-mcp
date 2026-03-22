import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.query import (
    build_object_info_query as _build_object_info_query,
    build_property_reference_query as _build_property_reference_query,
    execute_object_query,
    summarize_and_save,
    get_project_info,
    get_installation_info,
    get_object_property,
)
from typing import Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name = "SK Wwise MCP Browse")

@mcp.tool()
def build_object_info_query(
    from_path: Optional[list[str]] = None,
    from_type: Optional[list[str]] = None,
    return_fields: list[str] = ["id", "name", "type", "path", "shortId"],
    select_transform: Optional[str] = None,
    where_name_contains: Optional[str] = None,
    where_type_is: Optional[list[str]] = None,
) -> dict:
    """
    Builds a WAAPI ak.wwise.core.object.get query dict from structured parameters.
    Use this to construct a query before calling execute_waapi_query.

    Args:
        from_path:           Root paths to query from.
                             e.g. ["\\Actor-Mixer Hierarchy"] or ["\\Events"]
        from_type:           Object types to query from.
                             e.g. ["Sound", "Event", "RandomSequenceContainer"]
        return_fields:       Fields to return per object.
                             Common: "id", "name", "type", "path", "shortId", "parent"
        select_transform:    Traversal direction.
                             One of: "descendants", "ancestors", "children", "parent"
        where_name_contains: Filter results to objects whose name contains this string.
        where_type_is:       Filter results to specific object types.
                             e.g. ["Sound", "BlendContainer"]

    Examples:
        All descendants of Actor-Mixer Hierarchy:
            from_path=["\\Actor-Mixer Hierarchy"], select_transform="descendants"

        All Events containing "footstep":
            from_path=["\\Events"], select_transform="descendants",
            where_name_contains="footstep", where_type_is=["Event"]

        All busses:
            from_path=["\\Master-Mixer Hierarchy"], select_transform="descendants",
            where_type_is=["Bus", "AuxBus"]

        Children of a specific container:
            from_path=["\\Actor-Mixer Hierarchy\\Default Work Unit\\SFX"],
            select_transform="children"

    IMPORTANT — Inherited properties:
        Properties like @OutputBus return the LOCAL value, not the effective
        (inherited) value. If @OverrideOutput is false, the object inherits
        its output bus from an ancestor. To find the actual routing, query
        the object's ancestors (select_transform="ancestors") and return
        @OutputBus and @OverrideOutput to find the nearest ancestor that
        sets the effective bus.
    """
    return _build_object_info_query(
        from_path=from_path,
        from_type=from_type,
        return_fields=return_fields,
        select_transform=select_transform,
        where_name_contains=where_name_contains,
        where_type_is=where_type_is,
    )


@mcp.tool
def get_wwise_object_info(query: dict) -> dict:
    """
    Query Wwise objects and return a summary preview.

    IMPORTANT: The returned 'preview' only contains the first 10 results.
    The COMPLETE results are saved to the file path in 'output_file'.
    You MUST read that file to see all results — do not treat the preview as the full dataset.
    """
    try:
        results = execute_object_query(query)
        return summarize_and_save(results)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}  

@mcp.tool()
def build_property_reference_query(
    object_path: Optional[str] = None,
    object_guid: Optional[str] = None,
    object_name_with_type: Optional[str] = None,
    class_id: Optional[int] = None,
) -> dict:
    """
    Builds a WAAPI ak.wwise.core.object.getPropertyAndReferenceNames query dict.
    Use this to discover all valid property and reference names for a specific Wwise object.

    Args:
        object_path:           Project path to the object.
                               e.g. "\\Actor-Mixer Hierarchy\\Default Work Unit\\Footstep"
        object_guid:           GUID of the object.
                               e.g. "{aabbcc00-1122-3344-5566-77889900aabb}"
        object_name_with_type: Name qualified by type or short ID.
                               e.g. "Sound:Footstep_Walk", "Event:Play_Sound_01", "Global:245489792"
        class_id:              Class ID (unsigned 32-bit integer) of the object type.

    Provide exactly one of object_path, object_guid, or object_name_with_type.

    Examples:
        By path:
            object_path="\\Actor-Mixer Hierarchy\\Default Work Unit\\Footstep"
        By type:name:
            object_name_with_type="Sound:Footstep_Walk"
        By GUID:
            object_guid="{aabbcc00-1122-3344-5566-77889900aabb}"
    """
    return _build_property_reference_query(
        object_path=object_path,
        object_guid=object_guid,
        object_name_with_type=object_name_with_type,
        class_id=class_id,
    )


@mcp.tool
def get_property_and_reference_names(query: dict) -> dict:
    """Get all valid property and reference names for a Wwise object.

    Pass in a query built by build_property_reference_query.
    Returns lists of properties (e.g. Volume, Pitch) and references (e.g. Attenuation, OutputBus)
    that can be used with setProperty / setReference calls."""
    try:
        return get_object_property(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool
def get_wwise_installation_info() -> dict:
    """Get information about the running Wwise installation, including version, platform, and build number.

    Use this to verify which version of Wwise is running and confirm connectivity to the authoring tool."""
    try:
        return get_installation_info()
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}

@mcp.tool
def get_wwise_project_info() -> dict:
    """Get metadata about the currently open Wwise project, including project name, default language, and available platforms.

    Use this to understand the project context before performing queries or modifications."""
    try:
        return get_project_info()
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}  
    

if __name__ == "__main__":
    mcp.run(transport="stdio")