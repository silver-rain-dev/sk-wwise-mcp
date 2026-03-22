import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.query import execute_object_query, summarize_and_save, get_project_info, get_installation_info
from typing import Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name = "SK Wwise MCP Browse")

@mcp.tool()
def build_waapi_query(
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
    """
    query = {}

    # from
    if from_path:
        query["from"] = {"path": from_path}
    elif from_type:
        query["from"] = {"ofType": from_type}

    # where
    where = []
    if where_name_contains:
        where.append({"name": {"contains": where_name_contains}})
    if where_type_is:
        where.append({"type": {"isIn": where_type_is}})
    if where:
        query["where"] = where

    # transform
    if select_transform:
        query["transform"] = [{"select": [select_transform]}]

    # options
    query["options"] = {"return": return_fields}

    return query


@mcp.tool
def get_wwise_object_info(query: dict) -> dict:
    """
    Get information about the Wwise project, including instance info and Actor-Mixer hierarchy objects.

    Returns a summary with total_count, type breakdown, and a preview of the first 10 results.
    Full raw JSON output is saved to the file path in 'output_file'. Read that file for complete results or follow-up queries.
    """
    try:
        results = execute_object_query(query)
        return summarize_and_save(results)
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