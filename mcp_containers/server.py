import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.objects import (
    set_attenuation_curve as _set_attenuation_curve,
    set_randomizer as _set_randomizer,
    set_state_groups as _set_state_groups,
    set_state_properties as _set_state_properties,
    switch_container_add_assignment as _switch_container_add_assignment,
    switch_container_remove_assignment as _switch_container_remove_assignment,
    blend_container_add_assignment as _blend_container_add_assignment,
    blend_container_remove_assignment as _blend_container_remove_assignment,
    set_game_parameter_range as _set_game_parameter_range,
)
from typing import Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name="SK Wwise MCP Containers")


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def set_wwise_attenuation_curve(
    object: str,
    curve_type: str,
    use: str,
    points: list[dict],
    platform: Optional[str] = None,
):
    """Set an attenuation curve on an attenuation object.

    Args:
        object:     The attenuation object. Accepts:
                    - Project path: "\\\\Attenuations\\\\Default Work Unit\\\\MyAttenuation"
                    - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                    - Qualified name: "Attenuation:MyAttenuation"
        curve_type: The type of attenuation curve. One of:
                    Volume:       "VolumeDryUsage", "VolumeWetGameUsage", "VolumeWetUserUsage"
                    Filter:       "LowPassFilterUsage", "HighPassFilterUsage", "HighShelfUsage"
                    Spatial:      "SpreadUsage", "FocusUsage"
                    Obstruction:  "ObstructionVolumeUsage", "ObstructionHPFUsage",
                                  "ObstructionLPFUsage", "ObstructionHSFUsage"
                    Occlusion:    "OcclusionVolumeUsage", "OcclusionHPFUsage",
                                  "OcclusionLPFUsage", "OcclusionHSFUsage"
                    Diffraction:  "DiffractionVolumeUsage", "DiffractionHPFUsage",
                                  "DiffractionLPFUsage", "DiffractionHSFUsage"
                    Transmission: "TransmissionVolumeUsage", "TransmissionHPFUsage",
                                  "TransmissionLPFUsage", "TransmissionHSFUsage"
        use:        Curve mode:
                    "None"          — no points (disabled)
                    "Custom"        — use the provided points
                    "UseVolumeDry"  — reuse the VolumeDryUsage curve
                    "UseProject"    — use the global curve from Project Settings
        points:     Array of curve points. Each point is a dict with:
                    "x"     — X coordinate (distance)
                    "y"     — Y coordinate (value)
                    "shape" — interpolation to next point: "Constant", "Linear",
                              "Log3", "Log2", "Log1", "InvertedSCurve", "SCurve",
                              "Exp1", "Exp2", "Exp3"
                    e.g. [{"x": 0, "y": 0, "shape": "Linear"},
                          {"x": 100, "y": -200, "shape": "Linear"}]
        platform:   Platform name or GUID. Set to null-guid for unlinked curve.
    """
    try:
        return _set_attenuation_curve(
            object=object,
            curve_type=curve_type,
            use=use,
            points=points,
            platform=platform,
        )
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def set_wwise_randomizer(
    object: str,
    property: str,
    enabled: Optional[bool] = None,
    min: Optional[float] = None,
    max: Optional[float] = None,
    platform: Optional[str] = None,
):
    """Set randomizer values on a property of a Wwise object.

    At least one of 'enabled', 'min', or 'max' must be provided.

    Args:
        object:   The object owning the property. Accepts path, GUID, or type:name.
        property: The property name to randomize. e.g. "Volume", "Pitch"
        enabled:  Enable or disable the randomizer on this property.
        min:      Minimum offset value (must be <= 0).
        max:      Maximum offset value (must be >= 0).
        platform: Platform name or GUID. Optional.
    """
    try:
        return _set_randomizer(
            object=object,
            property=property,
            enabled=enabled,
            min=min,
            max=max,
            platform=platform,
        )
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": False})
def set_wwise_state_groups(
    object: str,
    state_groups: list[str],
):
    """Set the State Group objects associated with a Wwise object.

    WARNING: This replaces ALL previously associated State Groups on the object.

    Args:
        object:       The object to set State Groups on. Accepts path, GUID, or type:name.
        state_groups: Array of State Group identifiers to associate.
                      e.g. ["StateGroup:Alive", "\\\\States\\\\Default Work Unit\\\\PlayerHealth"]
    """
    try:
        return _set_state_groups(object=object, state_groups=state_groups)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": False})
def set_wwise_state_properties(
    object: str,
    state_properties: list[str],
):
    """Set the state properties of a Wwise object (properties controllable by States).

    WARNING: This replaces ALL previous state properties, including defaults.
    To keep existing state properties, include them in the list.

    Args:
        object:           The object to set state properties on. Accepts path, GUID, or type:name.
        state_properties: Array of property names that can be controlled by States.
                          e.g. ["Volume", "Pitch", "Lowpass", "Highpass"]
    """
    try:
        return _set_state_properties(object=object, state_properties=state_properties)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def add_wwise_switch_assignment(
    child: str,
    state_or_switch: str,
):
    """Assign a Switch Container's child to a State or Switch.

    Equivalent to drag-and-dropping a child onto a state in the Assigned Objects view.

    Args:
        child:           The child object of the Switch Container. Accepts path, GUID, or type:name.
        state_or_switch: The State or Switch to assign to. Must be a child of the
                         Switch/State Group set on the Switch Container.
    """
    try:
        return _switch_container_add_assignment(child=child, state_or_switch=state_or_switch)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def remove_wwise_switch_assignment(
    child: str,
    state_or_switch: str,
):
    """Remove an assignment between a Switch Container's child and a State or Switch.

    Args:
        child:           The child object currently assigned. Accepts path, GUID, or type:name.
        state_or_switch: The State or Switch from which to remove the assignment.
    """
    try:
        return _switch_container_remove_assignment(child=child, state_or_switch=state_or_switch)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def add_wwise_blend_assignment(
    blend_track_guid: str,
    child: str,
    index: Optional[int] = None,
    edges: Optional[list[dict]] = None,
):
    """Add a child assignment to a Blend Track. Equivalent to drag-and-drop in the Blend Tracks Editor.

    Args:
        blend_track_guid: The GUID of the Blend Track to add the assignment to.
                          e.g. "{aabbcc00-1122-3344-5566-77889900aabb}"
                          Note: Blend Tracks only accept GUIDs, not paths.
        child:            The child object to assign. Must be a child of the Blend Container
                          that owns this Blend Track. Accepts path, GUID, or type:name.
        index:            Optional position among existing assignments (0-based).
                          Clamped to [0, n]. If omitted, added at the end.
        edges:            Optional crossfade edge configuration. Only useful if the Blend Track
                          has a crossfade Game Parameter. Must be exactly 2 entries: [left, right].
                          Each edge requires:
                            fadeMode:     "None", "Manual", or "Automatic"
                            fadeShape:    "Constant", "Linear", "Log1"-"Log3", "Exp1"-"Exp3",
                                          "SCurve", "InvertedSCurve"
                            edgePosition: position within the Game Parameter range
                            fadePosition: (Manual mode only) start/end of the fade curve

    Returns:
        child: GUID of the assigned object
        index: final index position
        edges: array of 2 edge configs [left, right] with fadeMode, fadeShape, edgePosition, fadePosition"""
    query = {"object": blend_track_guid, "child": child}
    if index is not None:
        query["index"] = index
    if edges is not None:
        query["edges"] = edges
    try:
        return _blend_container_add_assignment(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def remove_wwise_blend_assignment(
    blend_track_guid: str,
    child: str,
):
    """Remove a child assignment from a Blend Track.

    Args:
        blend_track_guid: The GUID of the Blend Track. Only GUIDs are accepted.
                          e.g. "{aabbcc00-1122-3344-5566-77889900aabb}"
        child:            The child object to unassign. Accepts:
                          - Project path: "\\\\Containers\\\\Default Work Unit\\\\MySound"
                          - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                          - type:name (globally-unique types only): "Event:Play_Sound_01", "Global:245489792\""""
    try:
        return _blend_container_remove_assignment({"object": blend_track_guid, "child": child})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def set_wwise_game_parameter_range(
    object: str,
    min: float,
    max: float,
    on_curve_update: str,
):
    """Set the Min and Max range on a Game Parameter (RTPC).

    WARNING: This modifies RTPC curves and blend tracks that use this Game Parameter for their X axis.

    Args:
        object:          The Game Parameter. Accepts:
                         - path: "\\Game Parameters\\Default Work Unit\\Health"
                         - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                         - type:name: "GameParameter:Health"
        min:             The minimum value of the Game Parameter.
        max:             The maximum value of the Game Parameter.
        on_curve_update: How to handle existing RTPC curves and blend tracks:
                         "stretch"   — keep all items but stretch/compress X positions
                                       to match the new range. Set Game Parameter action
                                       values are also scaled.
                         "preserveX" — keep X positions as-is, but delete items that
                                       fall outside the new range. Set Game Parameter
                                       action values are clamped."""
    try:
        return _set_game_parameter_range({
            "object": object,
            "min": min,
            "max": max,
            "onCurveUpdate": on_curve_update,
        })
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
