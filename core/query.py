import json
from pathlib import Path
from typing import Optional
from core.waapi_util import call


def build_object_info_query(
    from_path: Optional[list[str]] = None,
    from_type: Optional[list[str]] = None,
    return_fields: list[str] = ["id", "name", "type", "path", "shortId"],
    select_transform: Optional[str] = None,
    where_name_contains: Optional[str] = None,
    where_type_is: Optional[list[str]] = None,
) -> dict:
    """Build a WAAPI ak.wwise.core.object.get query dict from structured parameters."""
    query = {}

    if from_path:
        query["from"] = {"path": from_path}
    elif from_type:
        query["from"] = {"ofType": from_type}

    where = []
    if where_name_contains:
        where.append({"name": {"contains": where_name_contains}})
    if where_type_is:
        where.append({"type": {"isIn": where_type_is}})
    if where:
        query["where"] = where

    if select_transform:
        query["transform"] = [{"select": [select_transform]}]

    query["options"] = {"return": return_fields}

    return query


def build_property_reference_query(
    object_path: Optional[str] = None,
    object_guid: Optional[str] = None,
    object_name_with_type: Optional[str] = None,
    class_id: Optional[int] = None,
) -> dict:
    """Build a WAAPI ak.wwise.core.object.getPropertyAndReferenceNames query dict."""
    query = {}
    if object_path:
        query["object"] = object_path
    elif object_guid:
        query["object"] = object_guid
    elif object_name_with_type:
        query["object"] = object_name_with_type
    if class_id is not None:
        query["classId"] = class_id
    return query


def build_property_info_query(
    property_name: str,
    object_path: Optional[str] = None,
    object_guid: Optional[str] = None,
    object_name_with_type: Optional[str] = None,
    class_id: Optional[int] = None,
) -> dict:
    """Build a WAAPI ak.wwise.core.object.getPropertyInfo query dict."""
    query = {"property": property_name}
    if object_path:
        query["object"] = object_path
    elif object_guid:
        query["object"] = object_guid
    elif object_name_with_type:
        query["object"] = object_name_with_type
    if class_id is not None:
        query["classId"] = class_id
    return query


def execute_object_query(query: dict) -> list[dict]:
    """Execute a WAAPI ak.wwise.core.object.get query and return the results."""
    options = query.pop("options", {})
    result = call("ak.wwise.core.object.get", query, options)
    return result.get("return", []) if result else []

def get_attenuation_curve(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.object.getAttenuationCurve query."""
    return call("ak.wwise.core.object.getAttenuationCurve", query)


def get_object_property(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.object.getPropertyAndReferenceNames query."""
    return call("ak.wwise.core.object.getPropertyAndReferenceNames", query)

def get_property_info(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.object.getPropertyInfo query."""
    return call("ak.wwise.core.object.getPropertyInfo", query)


def diff_objects(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.object.diff query."""
    return call("ak.wwise.core.object.diff", query)


def is_property_linked(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.object.isLinked query."""
    return call("ak.wwise.core.object.isLinked", query)


def is_property_enabled(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.object.isPropertyEnabled query."""
    return call("ak.wwise.core.object.isPropertyEnabled", query)


def get_object_types() -> dict:
    """Execute a WAAPI ak.wwise.core.object.getTypes query."""
    return call("ak.wwise.core.object.getTypes")


def get_installation_info() -> dict:
    """Executes ak.wwise.core.getInfo and return the results"""
    return call("ak.wwise.core.getInfo")

def get_project_info() -> dict:
    """Executes ak.wwise.core.getProjectInfo and return the results"""
    return call("ak.wwise.core.getProjectInfo")


def summarize_and_save(results: list[dict], output_file: str = None) -> dict:
    """Save full query results to a JSON file and return a compact summary."""
    if output_file is None:
        output_file = "wwise_query_output.json"

    output_path = Path(output_file).resolve()
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    type_counts = {}
    for obj in results:
        t = obj.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    return {
        "total_count": len(results),
        "types": type_counts,
        "output_file": str(output_path),
        "preview": results[:10],
    }
