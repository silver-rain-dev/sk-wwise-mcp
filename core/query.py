import json
from pathlib import Path
from typing import Optional
from core.waapi_util import call


def build_object_info_query(
    from_path: Optional[list[str]] = None,
    from_type: Optional[list[str]] = None,
    return_fields: list[str] = None,
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

    where_clauses = []
    if where_name_contains:
        where_clauses.append(["name:contains", where_name_contains])
    if where_type_is:
        where_clauses.append(["type:isIn", where_type_is])

    transform = []
    if select_transform:
        transform.append({"select": [select_transform]})
    for clause in where_clauses:
        transform.append({"where": clause})
    if transform:
        query["transform"] = transform

    if return_fields is None:
        return_fields = ["id", "name", "type", "path", "shortId"]
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
    """Execute a WAAPI ak.wwise.core.object.get query and return the results.

    Raises ValueError if WAAPI returns an error instead of results.
    """
    query = dict(query)  # Shallow copy to avoid mutating caller's dict
    options = query.pop("options", {})
    result = call("ak.wwise.core.object.get", query, options)
    if result is None:
        return []
    if "error" in result and "return" not in result:
        raise ValueError(f"WAAPI query error: {result['error']}")
    return result.get("return", [])

def get_switch_assignments(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.switchContainer.getAssignments query."""
    return call("ak.wwise.core.switchContainer.getAssignments", query)


def get_blend_assignments(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.blendContainer.getAssignments query."""
    return call("ak.wwise.core.blendContainer.getAssignments", query)


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


_MASTER_AUDIO_BUS_NAME = "Master Audio Bus"
def get_effective_output_bus(
        object_path: Optional[str] = None,
        object_guid: Optional[str] = None,
        object_name_with_type: Optional[str] = None) -> dict:
    """Resolve the effective output bus for an Actor-Mixer hierarchy object.

    WAAPI's @OutputBus returns the locally stored value regardless of whether the
    object is actually routing through it. The authoritative signal is @OverrideOutput:
    when false, the local @OutputBus is ignored at runtime and the object inherits from
    the nearest ancestor with @OverrideOutput=true. This function walks self + ancestors
    and returns the first @OutputBus where @OverrideOutput is true, falling back to
    Master Audio Bus if nothing in the chain overrides.
    """
    if object_path:
        from_clause = {"path": [object_path]}
    elif object_guid:
        from_clause = {"id": [object_guid]}
    elif object_name_with_type:
        from_clause = {"name": [object_name_with_type]}
    else:
        return {"error": "Must specify object_path, object_guid, or object_name_with_type"}

    return_fields = ["id", "name", "type", "path", "@OutputBus", "@OverrideOutput"]

    obj_results = execute_object_query({"from": from_clause, "options": {"return": return_fields}})
    if not obj_results:
        return {"error": "Object not found"}
    obj = obj_results[0]

    ancestor_results = execute_object_query({
        "from": from_clause,
        "transform": [{"select": ["ancestors"]}],
        "options": {"return": return_fields},
    })

    effective_bus = None
    set_by = None
    for index, node in enumerate([obj, *ancestor_results]):
        if node.get("@OverrideOutput") is not True:
            continue
        bus = node.get("@OutputBus") or {}
        if not (bus.get("id") or bus.get("name")):
            continue
        effective_bus = bus
        set_by = "self" if index == 0 else node.get("path", "unknown ancestor")
        break

    if not effective_bus:
        effective_bus = {"name": _MASTER_AUDIO_BUS_NAME}
        set_by = "default (no ancestor overrides)"

    # 5. Look up full bus path + HDR check (HDR is established at the topmost
    #    HdrEnable=true bus in the chain; any descendant bus is inside that window)
    bus_path = None
    is_hdr = False
    hdr_bus = None
    bus_id = effective_bus.get("id")
    if bus_id:
        bus_return = ["id", "name", "path", "@HdrEnable"]
        bus_results = execute_object_query({
            "from": {"id": [bus_id]},
            "options": {"return": bus_return},
        })
        if bus_results:
            bus_path = bus_results[0].get("path", "")

        bus_ancestors = execute_object_query({
            "from": {"id": [bus_id]},
            "transform": [{"select": ["ancestors"]}],
            "options": {"return": bus_return},
        })
        for node in [*bus_results, *bus_ancestors]:
            if node.get("@HdrEnable") is True:
                is_hdr = True
                hdr_bus = {"id": node.get("id"), "name": node.get("name"), "path": node.get("path")}
                break

    return {
        "object": {"name": obj.get("name"), "path": obj.get("path"), "type": obj.get("type")},
        "effective_bus": effective_bus,
        "bus_path": bus_path,
        "is_hdr": is_hdr,
        "hdr_bus": hdr_bus,
        "set_by": set_by
    }