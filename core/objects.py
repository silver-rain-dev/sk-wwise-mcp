from typing import Any, Optional
from core.waapi_util import call


def create_object(
    parent: str,
    type: str,
    name: str,
    on_name_conflict: str = "fail",
    platform: Optional[str] = None,
    notes: Optional[str] = None,
    children: Optional[list[dict]] = None,
    properties: Optional[dict[str, Any]] = None,
    list_name: Optional[str] = None,
) -> dict:
    """Create a Wwise object via ak.wwise.core.object.create.

    Args:
        parent:           Path, GUID, or qualified type:name of the parent object.
        type:             Wwise object type to create.
        name:             Name for the new object.
        on_name_conflict: "fail", "rename", "replace", or "merge".
        platform:         Platform name or GUID. When set, properties apply to
                          that platform only. Omit to set for all linked platforms.
        notes:            Notes/comments to attach to the object.
        children:         Recursive list of child objects to create. Each child is
                          a dict with at least "type" and "name", and optionally
                          "notes", "children", and "@PropertyName" keys.
        properties:       Dict of property values to set on the new object.
                          Keys are property names (without @), values are the
                          property values (str, number, bool, or null).
                          e.g. {"Volume": -6.0, "Pitch": 100}
        list_name:        If set, the object is inserted into a named list owned
                          by the parent, rather than as a direct child.

    Returns dict with "id", "name", and optionally "children" of created objects.
    """
    args = {
        "parent": parent,
        "type": type,
        "name": name,
        "onNameConflict": on_name_conflict,
    }
    if platform:
        args["platform"] = platform
    if notes:
        args["notes"] = notes
    if children:
        args["children"] = children
    if list_name:
        args["list"] = list_name
    if properties:
        for key, value in properties.items():
            args[f"@{key}"] = value
    return call("ak.wwise.core.object.create", args)


def delete_object(object: str) -> dict:
    """Delete a Wwise object via ak.wwise.core.object.delete."""
    return call("ak.wwise.core.object.delete", {"object": object})


def set_name(object: str, value: str) -> dict:
    """Rename a Wwise object via ak.wwise.core.object.setName."""
    return call("ak.wwise.core.object.setName", {"object": object, "value": value})


def set_notes(object: str, value: str) -> dict:
    """Set notes on a Wwise object via ak.wwise.core.object.setNotes."""
    return call("ak.wwise.core.object.setNotes", {"object": object, "value": value})


def set_property(object: str, property: str, value, platform: Optional[str] = None) -> dict:
    """Set a property on a Wwise object via ak.wwise.core.object.setProperty."""
    args = {"object": object, "property": property, "value": value}
    if platform:
        args["platform"] = platform
    return call("ak.wwise.core.object.setProperty", args)


def set_reference(object: str, reference: str, value: str) -> dict:
    """Set a reference on a Wwise object via ak.wwise.core.object.setReference."""
    return call(
        "ak.wwise.core.object.setReference",
        {"object": object, "reference": reference, "value": value},
    )


def move_object(object: str, parent: str, on_name_conflict: str = "fail") -> dict:
    """Move a Wwise object via ak.wwise.core.object.move."""
    return call(
        "ak.wwise.core.object.move",
        {"object": object, "parent": parent, "onNameConflict": on_name_conflict},
    )


def copy_object(object: str, parent: str, on_name_conflict: str = "fail") -> dict:
    """Copy a Wwise object via ak.wwise.core.object.copy."""
    return call(
        "ak.wwise.core.object.copy",
        {"object": object, "parent": parent, "onNameConflict": on_name_conflict},
    )


def set_attenuation_curve(
    object: str,
    curve_type: str,
    use: str,
    points: list[dict],
    platform: Optional[str] = None,
) -> dict:
    """Set an attenuation curve via ak.wwise.core.object.setAttenuationCurve."""
    args = {
        "object": object,
        "curveType": curve_type,
        "use": use,
        "points": points,
    }
    if platform:
        args["platform"] = platform
    return call("ak.wwise.core.object.setAttenuationCurve", args)


def set_randomizer(
    object: str,
    property: str,
    enabled: Optional[bool] = None,
    min: Optional[float] = None,
    max: Optional[float] = None,
    platform: Optional[str] = None,
) -> dict:
    """Set randomizer values on a property via ak.wwise.core.object.setRandomizer."""
    args = {"object": object, "property": property}
    if enabled is not None:
        args["enabled"] = enabled
    if min is not None:
        args["min"] = min
    if max is not None:
        args["max"] = max
    if platform:
        args["platform"] = platform
    return call("ak.wwise.core.object.setRandomizer", args)


def set_state_groups(object: str, state_groups: list[str]) -> dict:
    """Set State Group associations via ak.wwise.core.object.setStateGroups."""
    return call(
        "ak.wwise.core.object.setStateGroups",
        {"object": object, "stateGroups": state_groups},
    )


def set_state_properties(object: str, state_properties: list[str]) -> dict:
    """Set state properties via ak.wwise.core.object.setStateProperties."""
    return call(
        "ak.wwise.core.object.setStateProperties",
        {"object": object, "stateProperties": state_properties},
    )


def switch_container_add_assignment(child: str, state_or_switch: str) -> dict:
    """Assign a Switch Container child to a State/Switch via ak.wwise.core.switchContainer.addAssignment."""
    return call(
        "ak.wwise.core.switchContainer.addAssignment",
        {"child": child, "stateOrSwitch": state_or_switch},
    )


def switch_container_remove_assignment(child: str, state_or_switch: str) -> dict:
    """Remove a Switch Container child assignment via ak.wwise.core.switchContainer.removeAssignment."""
    return call(
        "ak.wwise.core.switchContainer.removeAssignment",
        {"child": child, "stateOrSwitch": state_or_switch},
    )


def blend_container_add_assignment(query: dict) -> dict:
    """Add an assignment to a Blend Track via ak.wwise.core.blendContainer.addAssignment."""
    return call("ak.wwise.core.blendContainer.addAssignment", query)


def blend_container_remove_assignment(query: dict) -> dict:
    """Remove an assignment from a Blend Track via ak.wwise.core.blendContainer.removeAssignment."""
    return call("ak.wwise.core.blendContainer.removeAssignment", query)


def set_game_parameter_range(query: dict) -> dict:
    """Set min/max range on a Game Parameter via ak.wwise.core.gameParameter.setRange."""
    return call("ak.wwise.core.gameParameter.setRange", query)
