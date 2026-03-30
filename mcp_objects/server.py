import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.objects import (
    create_object as _create_object,
    create_objects as _create_objects,
    delete_object as _delete_object,
    delete_objects as _delete_objects,
    set_name as _set_name,
    set_notes as _set_notes,
    set_property as _set_property,
    set_reference as _set_reference,
    set_properties as _set_properties,
    move_object as _move_object,
    move_objects as _move_objects,
    copy_object as _copy_object,
)
from typing import Any, Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name="SK Wwise MCP Objects")


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def create_wwise_objects(
    objects: list[dict],
    default_parent: Optional[str] = None,
):
    """Create one or more Wwise objects, potentially under different parents.

    Each entry in objects is a dict with:
        parent:             The parent object (optional when default_parent is set). Accepts:
                            - Project path: "\\\\Containers\\\\Default Work Unit"
                            - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                            - Qualified name (globally-unique types only):
                              "Bus:Master Audio Bus", "Event:Play_Sound_01"
        type (required):    Wwise object type to create.
                            e.g. "ActorMixer", "RandomSequenceContainer", "Sound",
                                 "Event", "Action", "Folder", "BlendContainer",
                                 "SwitchContainer", "MusicSwitchContainer",
                                 "MusicPlaylistContainer", "MusicSegment", "MusicTrack"
        name (required):    Name for the new object.
        on_name_conflict:   What to do if the name already exists under the parent.
                            "fail" (default), "rename", "replace", "merge"
        platform:           Platform name or GUID. When set, properties apply to that
                            platform only. Omit to set for all linked platforms.
        notes:              Notes/comments to attach to the object.
        children:           Recursive list of child objects to create. Each child is
                            a dict with at least "type" and "name", and optionally
                            "notes", "children", and "@PropertyName" keys.
                            e.g. [{"type": "Sound", "name": "Footstep_01", "@Volume": -3.0}]
        properties:         Dict of property values to set on the new object.
                            Keys are property names (without @), values are
                            str, number, bool, or null.
                            e.g. {"Volume": -6.0, "Pitch": 100}
        list_name:          If set, the object is inserted into a named list owned
                            by the parent, rather than as a direct child.
                            Use "actions" when creating Action objects under Events.
                            e.g. list_name="actions" for Event Actions.

    Args:
        default_parent: Optional default parent for all objects. Individual entries can
                        override by specifying their own "parent". Reduces token usage
                        when creating many siblings under the same parent.
                        Example: default_parent="\\\\Actor-Mixer Hierarchy\\\\Default Work Unit\\\\SFX"
                        Then objects can omit "parent": [{"type": "Sound", "name": "Shot_01"}, ...]

    For a single object, pass a list with one entry.

    Returns a list of result dicts, one per object. Each contains "id" and "name"
    of the created object, and "children" list if children were created.
    On individual failure, that entry contains an "error" key.
    """
    try:
        return _create_objects(objects=objects, default_parent=default_parent)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": False})
def delete_wwise_objects(
    objects: list[str],
):
    """Delete one or more Wwise objects (including their children).

    Args:
        objects: List of objects to delete. Each accepts:
                 - Project path: "\\\\Containers\\\\Default Work Unit\\\\MySound"
                 - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                 - Qualified name (globally-unique types only):
                   "Event:Play_Sound_01", "Bus:MyBus", "Global:245489792"
                   Supported types: StateGroup, SwitchGroup, SoundBank, GameParameter,
                   Event, Effect, AudioDevice, Trigger, Attenuation, DialogueEvent,
                   Bus, AuxBus, Conversion, ModulatorLfo, ModulatorEnvelope,
                   ModulatorTime, Platform, Language, AcousticTexture

    For a single object, pass a list with one entry.

    Returns a list of result dicts, one per object. On individual failure,
    that entry contains an "error" key.
    """
    try:
        return _delete_objects(objects=objects)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def set_wwise_object_name(
    object: str,
    value: str,
):
    """Rename a Wwise object.

    Args:
        object: The object to rename. Accepts:
                - Project path: "\\\\Containers\\\\Default Work Unit\\\\MySound"
                - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                - Qualified name (globally-unique types only):
                  "Event:Play_Sound_01", "Bus:MyBus", "Global:245489792"
                  Supported types: StateGroup, SwitchGroup, SoundBank, GameParameter,
                  Event, Effect, AudioDevice, Trigger, Attenuation, DialogueEvent,
                  Bus, AuxBus, Conversion, ModulatorLfo, ModulatorEnvelope,
                  ModulatorTime, Platform, Language, AcousticTexture
        value:  The new name of the object.
    """
    try:
        return _set_name(object=object, value=value)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def set_wwise_object_notes(
    object: str,
    value: str,
):
    """Set notes/comments on a Wwise object.

    Args:
        object: The object to set notes on. Accepts:
                - Project path: "\\\\Containers\\\\Default Work Unit\\\\MySound"
                - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                - Qualified name (globally-unique types only):
                  "Event:Play_Sound_01", "Bus:MyBus", "Global:245489792"
                  Supported types: StateGroup, SwitchGroup, SoundBank, GameParameter,
                  Event, Effect, AudioDevice, Trigger, Attenuation, DialogueEvent,
                  Bus, AuxBus, Conversion, ModulatorLfo, ModulatorEnvelope,
                  ModulatorTime, Platform, Language, AcousticTexture
        value:  The new notes of the object.
    """
    try:
        return _set_notes(object=object, value=value)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def set_wwise_object_properties(
    operations: list[dict],
    parent: Optional[str] = None,
):
    """Set properties and/or references on one or more Wwise objects.

    Replaces both set_wwise_object_property and set_wwise_object_reference with a
    single batch call. For a single object, pass a list with one entry.

    Each entry in operations is a dict with:
        object (required): The object to modify. Accepts:
                           - Project path: "\\\\Containers\\\\Default Work Unit\\\\MySound"
                           - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                           - Qualified name (globally-unique types only):
                             "Event:Play_Sound_01", "Bus:MyBus", "Global:245489792"
                           - Short name (when parent is set): "MySound"
        properties:        Optional dict of property name-value pairs.
                           e.g. {"Volume": -6.0, "Pitch": 100, "OverrideOutput": true}
        references:        Optional dict of reference name-value pairs.
                           e.g. {"OutputBus": "Bus:Music_Bus", "Conversion": "Conversion:Default"}
        platform:          Optional platform name or GUID. Used to set values for
                           unlinked properties. Omit to use the current platform.

    Args:
        parent: Optional parent path or GUID. When provided, short names in "object"
                are resolved to full paths by querying the parent's children.
                Reduces token usage when setting properties on many siblings.
                Example: parent="\\\\Actor-Mixer Hierarchy\\\\Default Work Unit\\\\SFX\\\\Footsteps"
                Then operations can use: [{"object": "Step_01", "properties": {"Volume": -6}}, ...]

    Examples:
        Single object, one property:
            operations=[{"object": "\\\\path\\\\Sound", "properties": {"Volume": -6.0}}]

        Set volume on many siblings using parent context:
            parent="\\\\Actor-Mixer Hierarchy\\\\...\\\\Footsteps",
            operations=[
                {"object": "Step_01", "properties": {"Volume": -6.0}},
                {"object": "Step_02", "properties": {"Volume": -6.0}},
            ]

    Returns a list of result dicts, one per operation. Each contains "object" and
    "ok": true on success, or "ok": false with "errors" list on partial failure.
    """
    try:
        return _set_properties(operations=operations, parent=parent)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def move_wwise_objects(
    objects: list[dict],
    source_parent: Optional[str] = None,
    new_parent: Optional[str] = None,
):
    """Move one or more Wwise objects to new parents.

    Each entry in objects is a dict with:
        object (required):  The object to move. Accepts:
                            - Project path: "\\\\Containers\\\\Default Work Unit\\\\MySound"
                            - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                            - Qualified name (globally-unique types only):
                              "Event:Play_Sound_01", "Bus:MyBus", "Global:245489792"
                            - Short name (when source_parent is set): "MySound"
        parent:             The new parent (optional when new_parent is set).
                            Same formats as 'object' above.
        on_name_conflict:   What to do if the parent already has a child with the same name.
                            "fail" (default), "rename", "replace"

    Args:
        source_parent: Optional source parent path or GUID. When provided, short names
                       in "object" are resolved by querying the parent's children.
        new_parent:    Optional default destination parent. Individual entries can
                       override by specifying their own "parent".
                       Example: new_parent="\\\\Actor-Mixer Hierarchy\\\\...\\\\NewFolder"
                       Then objects can omit "parent": [{"object": "Sound_01"}, {"object": "Sound_02"}]

    For a single object, pass a list with one entry.

    Returns a list of result dicts with id, name, type, path, and parent info.
    On individual failure, that entry contains an "error" key.
    """
    try:
        return _move_objects(objects=objects, source_parent=source_parent, new_parent=new_parent)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def copy_wwise_object(
    object: str,
    parent: str,
    on_name_conflict: str = "fail",
):
    """Copy a Wwise object to a new parent.

    Args:
        object:           The object to copy. Accepts:
                          - Project path: "\\\\Containers\\\\Default Work Unit\\\\MySound"
                          - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                          - Qualified name (globally-unique types only):
                            "Event:Play_Sound_01", "Bus:MyBus", "Global:245489792"
                            Supported types: StateGroup, SwitchGroup, SoundBank, GameParameter,
                            Event, Effect, AudioDevice, Trigger, Attenuation, DialogueEvent,
                            Bus, AuxBus, Conversion, ModulatorLfo, ModulatorEnvelope,
                            ModulatorTime, Platform, Language, AcousticTexture
        parent:           The destination parent. Same formats as 'object' above.
        on_name_conflict: What to do if the parent already has a child with the same name.
                          "fail"    — return an error (default)
                          "rename"  — auto-rename with appended numbers
                          "replace" — delete existing object and place the copy

    Returns the copied object with id, name, type, path, and parent info.
    """
    try:
        return _copy_object(object=object, parent=parent, on_name_conflict=on_name_conflict)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
