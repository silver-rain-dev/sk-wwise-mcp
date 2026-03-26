import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.objects import (
    create_object as _create_object,
    delete_object as _delete_object,
    set_name as _set_name,
    set_notes as _set_notes,
    set_property as _set_property,
    set_reference as _set_reference,
    move_object as _move_object,
    copy_object as _copy_object,
)
from typing import Any, Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name="SK Wwise MCP Objects")


@mcp.tool()
def create_wwise_object(
    parent: str,
    type: str,
    name: str,
    on_name_conflict: str = "fail",
    platform: Optional[str] = None,
    notes: Optional[str] = None,
    children: Optional[list[dict]] = None,
    properties: Optional[dict[str, Any]] = None,
    list_name: Optional[str] = None,
):
    """Create a new Wwise object under a parent, optionally with children and properties.

    Args:
        parent:           The parent object. Accepts:
                          - Project path: "\\\\Containers\\\\Default Work Unit"
                          - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                          - Qualified name (globally-unique types only):
                            "Bus:Master Audio Bus", "Event:Play_Sound_01"
        type:             Wwise object type to create.
                          e.g. "ActorMixer", "RandomSequenceContainer", "Sound",
                               "Event", "Folder", "BlendContainer", "SwitchContainer"
        name:             Name for the new object.
        on_name_conflict: What to do if the name already exists under the parent.
                          "fail"    — return an error (default)
                          "rename"  — auto-rename the new object
                          "replace" — replace the existing object
                          "merge"   — merge with the existing object
        platform:         Platform name or GUID. When set, properties apply to that
                          platform only. Omit to set for all linked platforms.
        notes:            Notes/comments to attach to the object.
        children:         Recursive list of child objects to create. Each child is
                          a dict with at least "type" and "name", and optionally
                          "notes", "children", and "@PropertyName" keys.
                          e.g. [{"type": "Sound", "name": "Footstep_01", "@Volume": -3.0},
                                {"type": "Sound", "name": "Footstep_02"}]
        properties:       Dict of property values to set on the new object.
                          Keys are property names (without @), values are
                          str, number, bool, or null.
                          e.g. {"Volume": -6.0, "Pitch": 100}
        list_name:        If set, the object is inserted into a named list owned
                          by the parent, rather than as a direct child.

    Returns dict with "id" and "name" of the created object, and "children"
    list if children were created (each with their own "id", "name", "children").
    """
    try:
        return _create_object(
            parent=parent,
            type=type,
            name=name,
            on_name_conflict=on_name_conflict,
            platform=platform,
            notes=notes,
            children=children,
            properties=properties,
            list_name=list_name,
        )
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def delete_wwise_object(
    object: str,
):
    """Delete a Wwise object (including its children).

    Args:
        object: The object to delete. Accepts:
                - Project path: "\\\\Containers\\\\Default Work Unit\\\\MySound"
                - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                - Qualified name (globally-unique types only):
                  "Event:Play_Sound_01", "Bus:MyBus", "Global:245489792"
                  Supported types: StateGroup, SwitchGroup, SoundBank, GameParameter,
                  Event, Effect, AudioDevice, Trigger, Attenuation, DialogueEvent,
                  Bus, AuxBus, Conversion, ModulatorLfo, ModulatorEnvelope,
                  ModulatorTime, Platform, Language, AcousticTexture
    """
    try:
        return _delete_object(object=object)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
def set_wwise_object_property(
    object: str,
    property: str,
    value,
    platform: Optional[str] = None,
):
    """Set a property value on a Wwise object.

    Use get_wwise_property_info (browse server) to discover valid properties
    and their types/ranges before setting.

    Args:
        object:   The object to set the property on. Accepts:
                  - Project path: "\\\\Containers\\\\Default Work Unit\\\\MySound"
                  - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                  - Qualified name (globally-unique types only):
                    "Event:Play_Sound_01", "Bus:MyBus", "Global:245489792"
                    Supported types: StateGroup, SwitchGroup, SoundBank, GameParameter,
                    Event, Effect, AudioDevice, Trigger, Attenuation, DialogueEvent,
                    Bus, AuxBus, Conversion, ModulatorLfo, ModulatorEnvelope,
                    ModulatorTime, Platform, Language, AcousticTexture
        property: The property name. e.g. "Volume", "Pitch", "Lowpass",
                  "Highpass", "InitialDelay", "Priority"
        value:    The value to set. Accepts null, string, number, or boolean
                  depending on the property type.
        platform: Platform name or GUID. Used to set values for unlinked
                  properties. Omit to use the current platform.
    """
    try:
        return _set_property(object=object, property=property, value=value, platform=platform)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def set_wwise_object_reference(
    object: str,
    reference: str,
    value: str,
):
    """Set a reference on a Wwise object (e.g. OutputBus, Conversion, Attenuation).

    Args:
        object:    The object which has the reference. Accepts:
                   - Project path: "\\\\Containers\\\\Default Work Unit\\\\MySound"
                   - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                   - Qualified name (globally-unique types only):
                     "Event:Play_Sound_01", "Bus:Master Audio Bus", "Global:245489792"
                     Supported types: StateGroup, SwitchGroup, SoundBank, GameParameter,
                     Event, Effect, AudioDevice, Trigger, Attenuation, DialogueEvent,
                     Bus, AuxBus, Conversion, ModulatorLfo, ModulatorEnvelope,
                     ModulatorTime, Platform, Language, AcousticTexture
        reference: The reference name. e.g. "OutputBus", "Conversion",
                   "Attenuation", "Effect0", "Effect1"
        value:     The object to be referred to. Same formats as 'object' above
                   (path, GUID, or qualified name).
    """
    try:
        return _set_reference(object=object, reference=reference, value=value)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def move_wwise_object(
    object: str,
    parent: str,
    on_name_conflict: str = "fail",
):
    """Move a Wwise object to a new parent.

    Args:
        object:           The object to move. Accepts:
                          - Project path: "\\\\Containers\\\\Default Work Unit\\\\MySound"
                          - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                          - Qualified name (globally-unique types only):
                            "Event:Play_Sound_01", "Bus:MyBus", "Global:245489792"
                            Supported types: StateGroup, SwitchGroup, SoundBank, GameParameter,
                            Event, Effect, AudioDevice, Trigger, Attenuation, DialogueEvent,
                            Bus, AuxBus, Conversion, ModulatorLfo, ModulatorEnvelope,
                            ModulatorTime, Platform, Language, AcousticTexture
        parent:           The new parent. Same formats as 'object' above.
        on_name_conflict: What to do if the parent already has a child with the same name.
                          "fail"    — return an error (default)
                          "rename"  — auto-rename with appended numbers
                          "replace" — delete existing object and move this one in

    Returns the moved object with id, name, type, path, and parent info.
    """
    try:
        return _move_object(object=object, parent=parent, on_name_conflict=on_name_conflict)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
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
