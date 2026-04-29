import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.query import (
    build_object_info_query as _build_object_info_query,
    build_property_reference_query as _build_property_reference_query,
    build_property_info_query as _build_property_info_query,
    execute_object_query,
    summarize_and_save,
    get_project_info,
    get_installation_info,
    get_object_property,
    get_property_info as _get_property_info,
    get_object_types as _get_object_types,
    get_switch_assignments as _get_switch_assignments,
    get_blend_assignments as _get_blend_assignments,
    get_attenuation_curve as _get_attenuation_curve,
    diff_objects as _diff_objects,
    is_property_linked as _is_property_linked,
    is_property_enabled as _is_property_enabled,
    get_effective_output_bus as _get_effective_output_bus,
)
from core.waapi_util import ping as _ping
from typing import Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name = "SK Wwise MCP Browse")

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def build_object_info_query(
    from_path: Optional[list[str]] = None,
    from_type: Optional[list[str]] = None,
    return_fields: list[str] = ["id", "name", "type", "path", "shortId"],
    select_transform: Optional[str] = None,
    where_name_contains: Optional[str] = None,
    where_type_is: Optional[list[str]] = None,
):
    """
    Builds a WAAPI ak.wwise.core.object.get query dict from structured parameters.
    Use this to construct a query before calling execute_waapi_query.

    Args:
        from_path:           Root paths to query from.
                             e.g. ["\\Containers"] or ["\\Events"]
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
        All descendants of Containers:
            from_path=["\\Containers"], select_transform="descendants"

        All Events containing "footstep":
            from_path=["\\Events"], select_transform="descendants",
            where_name_contains="footstep", where_type_is=["Event"]

        All busses:
            from_path=["\\Busses"], select_transform="descendants",
            where_type_is=["Bus", "AuxBus"]

        Children of a specific container:
            from_path=["\\Containers\\Default Work Unit\\SFX"],
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


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_wwise_object_info(query: dict):
    """
    Query Wwise objects and return a summary preview.

    IMPORTANT: Always use build_object_info_query() first to construct the query dict,
    then pass its output to this function. Do NOT hand-craft the query dict directly —
    the WAAPI query format is complex and error-prone; build_object_info_query() ensures
    correct structure (from, transform, options) every time.

    IMPORTANT: The returned 'preview' only contains the first 10 results.
    The COMPLETE results are saved to the file path in 'output_file'.
    You MUST read that file to see all results — do not treat the preview as the full dataset.

    Example workflow:
        query = build_object_info_query(
            from_path=["\\\\Events"],
            select_transform="descendants",
            where_type_is=["Event"],
        )
        results = get_wwise_object_info(query=query)
    """
    try:
        results = execute_object_query(query)
        return summarize_and_save(results)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}  

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_wwise_attenuation_curve(
    curve_type: str,
    object_path: Optional[str] = None,
    object_guid: Optional[str] = None,
    object_name_with_type: Optional[str] = None,
    platform: Optional[str] = None,
):
    """Get the curve points for an attenuation object.

    Args:
        curve_type:            Type of attenuation curve. One of:
                               Volume:      "VolumeDryUsage", "VolumeWetGameUsage", "VolumeWetUserUsage"
                               Filter:      "LowPassFilterUsage", "HighPassFilterUsage", "DualShelfUsage"
                               Spatial:     "SpreadUsage", "FocusUsage"
                               Obstruction: "ObstructionVolumeUsage", "ObstructionHPFUsage",
                                            "ObstructionLPFUsage", "ObstructionDSFUsage"
                               Occlusion:   "OcclusionVolumeUsage", "OcclusionHPFUsage",
                                            "OcclusionLPFUsage", "OcclusionDSFUsage"
                               Diffraction: "DiffractionVolumeUsage", "DiffractionHPFUsage",
                                            "DiffractionLPFUsage", "DiffractionDSFUsage"
                               Transmission:"TransmissionVolumeUsage", "TransmissionHPFUsage",
                                            "TransmissionLPFUsage", "TransmissionDSFUsage"
        object_path:           Project path to the attenuation object.
                               e.g. "\\Attenuations\\Default Work Unit\\Att_Footstep"
        object_guid:           GUID of the attenuation object.
        object_name_with_type: type:name. e.g. "Attenuation:Att_Footstep"
        platform:              Platform name or GUID. Optional — omit for linked/default curve.

    Provide exactly one of object_path, object_guid, or object_name_with_type.

    Returns:
        curveType: the curve type name
        use:       "None" (no points), "Custom" (own points), "UseVolumeDry" (shares VolumeDry curve),
                   or "UseProject" (uses global Project Settings curve)
        points:    array of {x, y, shape} where x=distance, y=value,
                   shape=curve segment type (Constant, Linear, Log1-3, Exp1-3, SCurve, InvertedSCurve)"""
    query = {"curveType": curve_type}
    if object_path:
        query["object"] = object_path
    elif object_guid:
        query["object"] = object_guid
    elif object_name_with_type:
        query["object"] = object_name_with_type
    if platform:
        query["platform"] = platform
    try:
        return _get_attenuation_curve(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_property_and_reference_names(
    object_path: Optional[str] = None,
    object_guid: Optional[str] = None,
    object_name_with_type: Optional[str] = None,
    class_id: Optional[int] = None,
):
    """Get all valid property and reference names for a Wwise object.

    Returns lists of properties (e.g. Volume, Pitch) and references (e.g. Attenuation, OutputBus)
    that can be used with setProperty / setReference calls.

    Args:
        object_path:           Project path to the object.
                               e.g. "\\Containers\\Default Work Unit\\Footstep"
        object_guid:           GUID of the object.
                               e.g. "{aabbcc00-1122-3344-5566-77889900aabb}"
        object_name_with_type: Name qualified by type or short ID.
                               e.g. "Sound:Footstep_Walk", "Event:Play_Sound_01", "Global:245489792"
                               Supported types: StateGroup, SwitchGroup, SoundBank, GameParameter,
                               Event, Effect, AudioDevice, Trigger, Attenuation, DialogueEvent,
                               Bus, AuxBus, Conversion, ModulatorLfo, ModulatorEnvelope,
                               ModulatorTime, Platform, Language, AcousticTexture, Global
        class_id:              Class ID (unsigned 32-bit integer) of the object type.

    Provide exactly one of object_path, object_guid, object_name_with_type, or class_id."""
    query = _build_property_reference_query(
        object_path=object_path,
        object_guid=object_guid,
        object_name_with_type=object_name_with_type,
        class_id=class_id,
    )
    try:
        return get_object_property(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_wwise_property_info(
    property_name: str,
    object_path: Optional[str] = None,
    object_guid: Optional[str] = None,
    object_name_with_type: Optional[str] = None,
    class_id: Optional[int] = None,
):
    """Get detailed info about a specific property on a Wwise object (type, min, max, default).

    Use get_property_and_reference_names first to discover valid property names.
    Use this to validate values before calling setProperty.

    Args:
        property_name:         The property name to get info for.
                               e.g. "Volume", "Pitch", "Lowpass", "IsLoopingEnabled"
        object_path:           Project path to the object.
                               e.g. "\\Containers\\Default Work Unit\\Footstep"
        object_guid:           GUID of the object.
                               e.g. "{aabbcc00-1122-3344-5566-77889900aabb}"
        object_name_with_type: Name qualified by type or short ID.
                               e.g. "Sound:Footstep_Walk", "Event:Play_Sound_01", "Global:245489792"
        class_id:              Class ID (unsigned 32-bit integer) as an alternative to object.

    Provide property_name plus one of object_path, object_guid, object_name_with_type, or class_id.

    Returns the property's type, default value, min/max range, and display name."""
    query = _build_property_info_query(
        property_name=property_name,
        object_path=object_path,
        object_guid=object_guid,
        object_name_with_type=object_name_with_type,
        class_id=class_id,
    )
    try:
        return _get_property_info(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def diff_wwise_objects(
    source_path: Optional[str] = None,
    source_guid: Optional[str] = None,
    source_name_with_type: Optional[str] = None,
    target_path: Optional[str] = None,
    target_guid: Optional[str] = None,
    target_name_with_type: Optional[str] = None,
):
    """Compare two Wwise objects and return the properties, references, and lists that differ between them.

    Useful for auditing ("do these two sounds have the same settings?") and Paste Properties workflows.

    Args:
        source_path:           Project path of source object.
        source_guid:           GUID of source object.
        source_name_with_type: type:name of source object. e.g. "Sound:Footstep_Walk"
        target_path:           Project path of target object.
        target_guid:           GUID of target object.
        target_name_with_type: type:name of target object. e.g. "Sound:Footstep_Run"

    Provide exactly one source identifier and one target identifier.

    Object identification (same for source and target):
        - path:      "\\Containers\\Default Work Unit\\Footstep"
        - GUID:      "{aabbcc00-1122-3344-5566-77889900aabb}"
        - type:name: "Sound:Footstep_Walk", "Event:Play_Sound_01", "Global:245489792"

    Returns:
        properties: array of property/reference names that differ (e.g. ["Volume", "Pitch", "Lowpass"])
        lists:      array of list names that differ (e.g. ["Effects", "RTPC"])"""
    query = {}
    if source_path:
        query["source"] = source_path
    elif source_guid:
        query["source"] = source_guid
    elif source_name_with_type:
        query["source"] = source_name_with_type

    if target_path:
        query["target"] = target_path
    elif target_guid:
        query["target"] = target_guid
    elif target_name_with_type:
        query["target"] = target_name_with_type

    try:
        return _diff_objects(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def is_wwise_property_linked(
    property_name: str,
    platform: str,
    object_path: Optional[str] = None,
    object_guid: Optional[str] = None,
    object_name_with_type: Optional[str] = None,
):
    """Check if a property on a Wwise object is linked (shared across all platforms) or unlinked (has platform-specific values).

    All three arguments (object, property, platform) are required.

    Args:
        property_name:         The property to check. e.g. "Volume", "Pitch", "Lowpass"
        platform:              Platform name or GUID to check against.
                               e.g. "Windows", "Mac", "iOS", "Android", "PS5", "XboxSeriesX"
                               or a platform GUID "{aabbcc00-1122-3344-5566-77889900aabb}"
        object_path:           Project path. e.g. "\\Containers\\Default Work Unit\\Footstep"
        object_guid:           GUID. e.g. "{aabbcc00-1122-3344-5566-77889900aabb}"
        object_name_with_type: type:name. e.g. "Sound:Footstep_Walk"

    Provide exactly one of object_path, object_guid, or object_name_with_type.

    Returns {"linked": true} if the property is linked (shared across platforms),
    or {"linked": false} if it has a platform-specific override for the given platform."""
    query = {"property": property_name, "platform": platform}
    if object_path:
        query["object"] = object_path
    elif object_guid:
        query["object"] = object_guid
    elif object_name_with_type:
        query["object"] = object_name_with_type
    try:
        return _is_property_linked(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def is_wwise_property_enabled(
    property_name: str,
    platform: str,
    object_path: Optional[str] = None,
    object_guid: Optional[str] = None,
    object_name_with_type: Optional[str] = None,
):
    """Check if a property is enabled on a Wwise object for a given platform.

    A property can be disabled when it's overridden by a parent or not applicable
    on a specific platform. All three arguments (object, property, platform) are required.

    Args:
        property_name:         The property to check. e.g. "Volume", "Pitch", "Lowpass"
        platform:              Platform name or GUID.
                               e.g. "Windows", "Mac", "iOS", "Android", "PS5", "XboxSeriesX"
                               or a GUID "{aabbcc00-1122-3344-5566-77889900aabb}"
        object_path:           Project path. e.g. "\\Containers\\Default Work Unit\\Footstep"
        object_guid:           GUID. e.g. "{aabbcc00-1122-3344-5566-77889900aabb}"
        object_name_with_type: type:name. e.g. "Sound:Footstep_Walk"

    Provide exactly one of object_path, object_guid, or object_name_with_type.

    Returns {"return": true} if the property is enabled,
    or {"return": false} if the property is disabled."""
    query = {"property": property_name, "platform": platform}
    if object_path:
        query["object"] = object_path
    elif object_guid:
        query["object"] = object_guid
    elif object_name_with_type:
        query["object"] = object_name_with_type
    try:
        return _is_property_enabled(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_wwise_object_types():
    """Get all available Wwise object types. No arguments required.

    Use this to discover valid type names for queries — pass them to build_object_info_query's
    from_type or where_type_is parameters. Also useful for getting classId values for
    build_property_reference_query and build_property_info_query.

    Returns {"return": [{"classId": int, "name": str, "type": str}, ...]}
    Each entry contains:
        classId: The class ID (unsigned 32-bit integer) of the object type.
        name:    The display name of the object type.
        type:    The type identifier string (e.g. "Sound", "Event", "Bus")."""
    try:
        return _get_object_types()
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_wwise_installation_info():
    """Get information about the running Wwise installation, including version, platform, and build number.

    Use this to verify which version of Wwise is running and confirm connectivity to the authoring tool."""
    try:
        return get_installation_info()
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_wwise_project_info():
    """Get metadata about the currently open Wwise project, including project name, default language, and available platforms.

    Use this to understand the project context before performing queries or modifications."""
    try:
        return get_project_info()
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_switch_container_assignments(
    object_path: Optional[str] = None,
    object_guid: Optional[str] = None,
    object_name_with_type: Optional[str] = None,
):
    """Get the switch/state-to-child assignments for a Switch Container.

    Returns which child object plays for each switch or state value.
    Use this to audit assignments, find unassigned switches, or document switch mappings.

    Args:
        object_path:           Project path to the Switch Container.
                               e.g. "\\Containers\\Default Work Unit\\Footstep_Switch"
        object_guid:           GUID of the Switch Container.
        object_name_with_type: type:name. e.g. "Global:245489792"

    Provide exactly one of object_path, object_guid, or object_name_with_type.

    Returns {"return": [...]} — array of assignment pairs, each containing:
        child:         GUID/name/path of the child object assigned to a switch/state
        stateOrSwitch: GUID/name/path of the switch or state value"""
    query = {}
    if object_path:
        query["id"] = object_path
    elif object_guid:
        query["id"] = object_guid
    elif object_name_with_type:
        query["id"] = object_name_with_type
    try:
        return _get_switch_assignments(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_blend_track_assignments(
    blend_track_guid: str,
):
    """Get the list of assignments for a Blend Track. Only accepts GUIDs.

    Use this to inspect which children are assigned to a Blend Track and their crossfade edge config.

    Args:
        blend_track_guid: The GUID of the Blend Track.
                          e.g. "{aabbcc00-1122-3344-5566-77889900aabb}"

    Returns {"return": [...]} — array of assignments, each containing:
        child: GUID of the assigned child object
        index: position among the Blend Track's assignments
        edges: array of 2 edge configs [left, right], each with:
            fadeMode:     "None", "Manual", or "Automatic"
            fadeShape:    curve shape (Linear, SCurve, etc.)
            edgePosition: position within the Game Parameter range
            fadePosition: fade curve start/end (Manual mode only)"""
    try:
        return _get_blend_assignments({"object": blend_track_guid})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_effective_output_bus(
    object_path: Optional[str] = None,
    object_guid: Optional[str] = None,
    object_name_with_type: Optional[str] = None,
):
    """Resolve the effective (inherited) output bus for an Actor-Mixer hierarchy object.

    WAAPI's @OutputBus returns the LOCAL value, which defaults to "Master Audio Bus"
    when an object has not set Override Output. This tool walks the ancestor chain to
    find the first non-default @OutputBus assignment and returns its full bus path.

    Args:
        object_path:           Project path. e.g. "\\Actor-Mixer Hierarchy\\Default Work Unit\\SFX\\Barrage"
        object_guid:           GUID. e.g. "{aabbcc00-1122-3344-5566-77889900aabb}"
        object_name_with_type: type:name. e.g. "Sound:Barrage"

    Provide exactly one of object_path, object_guid, or object_name_with_type.

    Returns:
        object:        {name, path, type} of the queried object
        effective_bus: {id, name} of the resolved output bus
        bus_path:      full project path of the bus (e.g. "\\Master-Mixer Hierarchy\\Default Work Unit\\Master Audio Bus\\SFX")
        is_hdr:        whether the object is inside an HDR window (true if the resolved bus or any of its bus ancestors has HdrEnable=true)
        hdr_bus:       {id, name, path} of the bus that establishes the HDR window, or null if not in one
        set_by:        "self", the ancestor path that sets the override, or "default (no ancestor overrides)"
    """
    try:
        return _get_effective_output_bus(
            object_path=object_path,
            object_guid=object_guid,
            object_name_with_type=object_name_with_type,
        )
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def ping_wwise():
    """Check if WAAPI is currently available. No arguments required.

    Returns {"isAvailable": true} if Wwise is running and WAAPI is ready.
    Returns {"isAvailable": false} if Wwise is not running, WAAPI is disabled,
    or a modal dialog is blocking WAAPI access.

    Use this before other calls to verify connectivity."""
    return _ping()


if __name__ == "__main__":
    mcp.run(transport="stdio")