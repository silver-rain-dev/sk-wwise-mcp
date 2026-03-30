from typing import Any, Optional
from core.waapi_util import call


def _build_create_args(
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
    """Build args dict for ak.wwise.core.object.create."""
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
    return args


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
    args = _build_create_args(
        parent=parent, type=type, name=name,
        on_name_conflict=on_name_conflict, platform=platform,
        notes=notes, children=children, properties=properties,
        list_name=list_name,
    )
    return call("ak.wwise.core.object.create", args)


def create_objects(objects: list[dict], default_parent: Optional[str] = None) -> list[dict]:
    """Create multiple Wwise objects, potentially under different parents.

    Each entry in objects should be a dict with at least "type", "name",
    and optionally "parent", "on_name_conflict", "platform", "notes", "children",
    "properties", "list_name".

    Args:
        default_parent: Optional default parent for all objects. Individual entries
                        can override by specifying their own "parent".

    Returns a list of results, one per object. On individual failure, that entry
    contains an "error" key.
    """
    results = []
    for obj in objects:
        parent = obj.get("parent", default_parent)
        if not parent:
            results.append({"error": "No parent specified and no default_parent set", "name": obj.get("name", "?")})
            continue
        args = _build_create_args(
            parent=parent,
            type=obj["type"],
            name=obj["name"],
            on_name_conflict=obj.get("on_name_conflict", "fail"),
            platform=obj.get("platform"),
            notes=obj.get("notes"),
            children=obj.get("children"),
            properties=obj.get("properties"),
            list_name=obj.get("list_name"),
        )
        try:
            results.append(call("ak.wwise.core.object.create", args))
        except Exception as e:
            results.append({"error": str(e), "name": obj["name"]})
    return results


def delete_object(object: str) -> dict:
    """Delete a Wwise object via ak.wwise.core.object.delete."""
    return call("ak.wwise.core.object.delete", {"object": object})


def delete_objects(objects: list[str]) -> list[dict]:
    """Delete multiple Wwise objects.

    Args:
        objects: List of object identifiers (path, GUID, or qualified name).

    Returns a list of results, one per object. On individual failure, that entry
    contains an "error" key.
    """
    results = []
    for obj in objects:
        try:
            results.append(call("ak.wwise.core.object.delete", {"object": obj}))
        except Exception as e:
            results.append({"error": str(e), "object": obj})
    return results


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


def set_properties(operations: list[dict], parent: Optional[str] = None) -> list[dict]:
    """Set properties and/or references on multiple Wwise objects in one batch.

    Each entry in operations is a dict with:
        object:     The object to modify (path, GUID, qualified name, or short name
                    when parent is set).
        properties: Optional dict of {property_name: value} to set.
        references: Optional dict of {reference_name: value} to set.
        platform:   Optional platform name or GUID.

    Args:
        parent: Optional parent path or GUID. When provided, short names in "object"
                are resolved to full paths by querying the parent's children.

    Returns a list of result dicts, one per operation. Each result contains
    "object" and either "ok": True or "errors": [...] for failed sub-operations.
    """
    child_map = {}
    if parent:
        try:
            child_map = _resolve_children_names(parent)
        except Exception as e:
            return [{"error": f"Failed to resolve parent children: {e}"}]

    results = []
    for op in operations:
        obj = op["object"]

        # Resolve short name if parent context provided
        if parent and _is_short_name(obj):
            if obj in child_map:
                obj = child_map[obj]
            else:
                results.append({"object": op["object"], "ok": False, "errors": [{"error": f"Child '{obj}' not found under parent"}]})
                continue

        platform = op.get("platform")
        entry_result = {"object": obj, "ok": True}
        errors = []

        for prop_name, prop_value in (op.get("properties") or {}).items():
            try:
                args = {"object": obj, "property": prop_name, "value": prop_value}
                if platform:
                    args["platform"] = platform
                call("ak.wwise.core.object.setProperty", args)
            except Exception as e:
                errors.append({"property": prop_name, "error": str(e)})

        for ref_name, ref_value in (op.get("references") or {}).items():
            try:
                call(
                    "ak.wwise.core.object.setReference",
                    {"object": obj, "reference": ref_name, "value": ref_value},
                )
            except Exception as e:
                errors.append({"reference": ref_name, "error": str(e)})

        if errors:
            entry_result["ok"] = False
            entry_result["errors"] = errors
        results.append(entry_result)
    return results


def move_object(object: str, parent: str, on_name_conflict: str = "fail") -> dict:
    """Move a Wwise object via ak.wwise.core.object.move."""
    return call(
        "ak.wwise.core.object.move",
        {"object": object, "parent": parent, "onNameConflict": on_name_conflict},
    )


def move_objects(
    objects: list[dict],
    source_parent: Optional[str] = None,
    new_parent: Optional[str] = None,
) -> list[dict]:
    """Move multiple Wwise objects.

    Each entry in objects is a dict with:
        object:           The object to move (path, GUID, qualified name, or short
                          name when source_parent is set).
        parent:           The new parent (path, GUID, or qualified name).
                          Optional when new_parent is set.
        on_name_conflict: Optional. "fail" (default), "rename", or "replace".

    Args:
        source_parent: Optional source parent path or GUID. When provided, short names
                       in "object" are resolved to full paths by querying children.
        new_parent:    Optional default destination parent. Individual entries can
                       override by specifying their own "parent".

    Returns a list of results, one per object. On individual failure, that entry
    contains an "error" key.
    """
    child_map = {}
    if source_parent:
        try:
            child_map = _resolve_children_names(source_parent)
        except Exception as e:
            return [{"error": f"Failed to resolve source parent children: {e}"}]

    results = []
    for entry in objects:
        obj_ref = entry["object"]
        parent_ref = entry.get("parent", new_parent)

        # Resolve short name if source_parent context provided
        if source_parent and _is_short_name(obj_ref):
            if obj_ref in child_map:
                obj_ref = child_map[obj_ref]
            else:
                results.append({"error": f"Child '{obj_ref}' not found under source parent", "object": entry["object"]})
                continue

        if not parent_ref:
            results.append({"error": "No parent specified and no new_parent set", "object": entry["object"]})
            continue

        try:
            result = call(
                "ak.wwise.core.object.move",
                {
                    "object": obj_ref,
                    "parent": parent_ref,
                    "onNameConflict": entry.get("on_name_conflict", "fail"),
                },
            )
            results.append(result)
        except Exception as e:
            results.append({"error": str(e), "object": entry["object"]})
    return results


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


def _is_short_name(value: str) -> bool:
    """Return True if value is a short name (not a path, GUID, or type:name)."""
    return not value.startswith("\\") and not value.startswith("{") and ":" not in value


def _resolve_children_names(parent: str) -> dict:
    """Query a parent object's children and return a name -> path map.

    Args:
        parent: Path or GUID of the parent object.

    Returns dict mapping child short name -> full path.
    """
    from core.query import execute_object_query

    children = execute_object_query({
        "from": {"path": [parent]} if parent.startswith("\\") else {"id": [parent]},
        "transform": [{"select": ["children"]}],
        "options": {"return": ["name", "path"]},
    })
    return {c["name"]: c["path"] for c in children}


def _resolve_switch_container_names(container: str) -> tuple[dict, dict]:
    """Query a Switch Container's children and its switch group's switches.

    Returns (child_map, switch_map) where each maps short name -> path.
    """
    from core.query import execute_object_query

    # Get children of the container
    children = execute_object_query({
        "from": {"path": [container]} if container.startswith("\\") else {"id": [container]},
        "transform": [{"select": ["children"]}],
        "options": {"return": ["name", "path"]},
    })
    child_map = {c["name"]: c["path"] for c in children}

    # Get the SwitchGroupOrStateGroup reference to find the switch group
    ref_result = call(
        "ak.wwise.core.object.get",
        {"from": {"path": [container]} if container.startswith("\\") else {"id": [container]}},
        {"return": ["@SwitchGroupOrStateGroup"]},
    )
    switch_group_ref = None
    for obj in ref_result.get("return", []):
        sg = obj.get("@SwitchGroupOrStateGroup")
        if sg:
            switch_group_ref = sg.get("id")
            break

    switch_map = {}
    if switch_group_ref:
        switches = execute_object_query({
            "from": {"id": [switch_group_ref]},
            "transform": [{"select": ["children"]}],
            "options": {"return": ["name", "path"]},
        })
        switch_map = {s["name"]: s["path"] for s in switches}

    return child_map, switch_map


def switch_container_add_assignments(
    assignments: list[dict],
    container: Optional[str] = None,
) -> list[dict]:
    """Assign multiple Switch Container children to States/Switches in one batch.

    Each entry in assignments is a dict with:
        child:           The child object (path, GUID, or type:name).
                         When container is set, can be a short name (e.g. "Absorb").
        state_or_switch: The State or Switch to assign to.
                         When container is set, can be a short name (e.g. "Absorb").

    Args:
        container: Optional Switch Container path or GUID. When provided, short names
                   in child/state_or_switch are resolved relative to the container's
                   children and its switch group's switches.

    Returns a list of results, one per assignment. On individual failure,
    that entry contains an "error" key.
    """
    child_map = {}
    switch_map = {}
    if container:
        try:
            child_map, switch_map = _resolve_switch_container_names(container)
        except Exception as e:
            return [{"error": f"Failed to resolve container names: {e}"}]

    results = []
    for a in assignments:
        child_ref = a["child"]
        switch_ref = a["state_or_switch"]

        # Resolve short names if container was provided
        if container and _is_short_name(child_ref):
            if child_ref in child_map:
                child_ref = child_map[child_ref]
            else:
                results.append({"error": f"Child '{child_ref}' not found in container", "child": a["child"]})
                continue
        if container and _is_short_name(switch_ref):
            if switch_ref in switch_map:
                switch_ref = switch_map[switch_ref]
            else:
                results.append({"error": f"Switch '{switch_ref}' not found in switch group", "child": a["child"]})
                continue

        try:
            result = call(
                "ak.wwise.core.switchContainer.addAssignment",
                {"child": child_ref, "stateOrSwitch": switch_ref},
            )
            results.append(result)
        except Exception as e:
            results.append({"error": str(e), "child": a["child"]})
    return results


def switch_container_remove_assignment(child: str, state_or_switch: str) -> dict:
    """Remove a Switch Container child assignment via ak.wwise.core.switchContainer.removeAssignment."""
    return call(
        "ak.wwise.core.switchContainer.removeAssignment",
        {"child": child, "stateOrSwitch": state_or_switch},
    )


def switch_container_remove_assignments(
    assignments: list[dict],
    container: Optional[str] = None,
) -> list[dict]:
    """Remove multiple Switch Container child assignments in one batch.

    Each entry in assignments is a dict with:
        child:           The child object (path, GUID, or type:name).
                         When container is set, can be a short name.
        state_or_switch: The State or Switch to unassign from.
                         When container is set, can be a short name.

    Args:
        container: Optional Switch Container path or GUID. When provided, short names
                   are resolved relative to the container's children and switch group.

    Returns a list of results, one per assignment. On individual failure,
    that entry contains an "error" key.
    """
    child_map = {}
    switch_map = {}
    if container:
        try:
            child_map, switch_map = _resolve_switch_container_names(container)
        except Exception as e:
            return [{"error": f"Failed to resolve container names: {e}"}]

    results = []
    for a in assignments:
        child_ref = a["child"]
        switch_ref = a["state_or_switch"]

        if container and _is_short_name(child_ref):
            if child_ref in child_map:
                child_ref = child_map[child_ref]
            else:
                results.append({"error": f"Child '{child_ref}' not found in container", "child": a["child"]})
                continue
        if container and _is_short_name(switch_ref):
            if switch_ref in switch_map:
                switch_ref = switch_map[switch_ref]
            else:
                results.append({"error": f"Switch '{switch_ref}' not found in switch group", "child": a["child"]})
                continue

        try:
            result = call(
                "ak.wwise.core.switchContainer.removeAssignment",
                {"child": child_ref, "stateOrSwitch": switch_ref},
            )
            results.append(result)
        except Exception as e:
            results.append({"error": str(e), "child": a["child"]})
    return results


def blend_container_add_assignment(query: dict) -> dict:
    """Add an assignment to a Blend Track via ak.wwise.core.blendContainer.addAssignment."""
    return call("ak.wwise.core.blendContainer.addAssignment", query)


def blend_container_remove_assignment(query: dict) -> dict:
    """Remove an assignment from a Blend Track via ak.wwise.core.blendContainer.removeAssignment."""
    return call("ak.wwise.core.blendContainer.removeAssignment", query)


def set_game_parameter_range(query: dict) -> dict:
    """Set min/max range on a Game Parameter via ak.wwise.core.gameParameter.setRange."""
    return call("ak.wwise.core.gameParameter.setRange", query)
