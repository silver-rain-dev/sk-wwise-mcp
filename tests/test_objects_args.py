"""Tests that core.objects functions build WAAPI-compliant arg dicts.

These tests mock core.waapi_util.call and assert the exact args dict
sent to WAAPI matches the expected schema format. This catches format
bugs like the where-clause issue (object-based vs array-based) before
they hit a live Wwise instance.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.objects import (
    create_object,
    delete_object,
    set_name,
    set_notes,
    set_property,
    set_reference,
    move_object,
    copy_object,
    set_attenuation_curve,
    set_randomizer,
    set_state_groups,
    set_state_properties,
    switch_container_add_assignment,
    switch_container_remove_assignment,
)


# --- create_object ---


@patch("core.objects.call")
def test_create_object_basic_args(mock_call):
    mock_call.return_value = {"id": "{x}", "name": "S"}
    create_object(parent="\\path\\WU", type="Sound", name="S")
    mock_call.assert_called_once_with("ak.wwise.core.object.create", {
        "parent": "\\path\\WU",
        "type": "Sound",
        "name": "S",
        "onNameConflict": "fail",
    })


@patch("core.objects.call")
def test_create_object_properties_use_at_prefix(mock_call):
    mock_call.return_value = {"id": "{x}", "name": "S"}
    create_object(
        parent="\\path\\WU", type="Sound", name="S",
        properties={"Volume": -6.0, "Pitch": 100},
    )
    args = mock_call.call_args[0][1]
    assert args["@Volume"] == -6.0
    assert args["@Pitch"] == 100
    assert "Volume" not in args
    assert "properties" not in args


@patch("core.objects.call")
def test_create_object_children_passed_directly(mock_call):
    mock_call.return_value = {"id": "{x}", "name": "C"}
    children = [
        {"type": "Sound", "name": "A", "@Volume": -3.0},
        {"type": "Sound", "name": "B"},
    ]
    create_object(parent="\\path\\WU", type="RandomSequenceContainer", name="C", children=children)
    args = mock_call.call_args[0][1]
    assert args["children"] == children


@patch("core.objects.call")
def test_create_object_with_platform_and_notes(mock_call):
    mock_call.return_value = {"id": "{x}", "name": "S"}
    create_object(
        parent="\\path\\WU", type="Sound", name="S",
        platform="Windows", notes="Test notes",
    )
    args = mock_call.call_args[0][1]
    assert args["platform"] == "Windows"
    assert args["notes"] == "Test notes"


@patch("core.objects.call")
def test_create_object_with_list_name(mock_call):
    mock_call.return_value = {"id": "{x}", "name": "S"}
    create_object(parent="\\path\\WU", type="Sound", name="S", list_name="myList")
    args = mock_call.call_args[0][1]
    assert args["list"] == "myList"


@patch("core.objects.call")
def test_create_object_omits_none_optionals(mock_call):
    mock_call.return_value = {"id": "{x}", "name": "S"}
    create_object(parent="\\path\\WU", type="Sound", name="S")
    args = mock_call.call_args[0][1]
    assert "platform" not in args
    assert "notes" not in args
    assert "children" not in args
    assert "list" not in args


@patch("core.objects.call")
def test_create_object_on_name_conflict_merge(mock_call):
    mock_call.return_value = {"id": "{x}", "name": "S"}
    create_object(parent="\\path\\WU", type="Sound", name="S", on_name_conflict="merge")
    args = mock_call.call_args[0][1]
    assert args["onNameConflict"] == "merge"


# --- delete_object ---


@patch("core.objects.call")
def test_delete_object_args(mock_call):
    mock_call.return_value = {}
    delete_object(object="\\path\\Sound")
    mock_call.assert_called_once_with("ak.wwise.core.object.delete", {"object": "\\path\\Sound"})


# --- set_name ---


@patch("core.objects.call")
def test_set_name_args(mock_call):
    mock_call.return_value = {}
    set_name(object="\\path\\Sound", value="NewName")
    mock_call.assert_called_once_with(
        "ak.wwise.core.object.setName", {"object": "\\path\\Sound", "value": "NewName"}
    )


# --- set_notes ---


@patch("core.objects.call")
def test_set_notes_args(mock_call):
    mock_call.return_value = {}
    set_notes(object="\\path\\Sound", value="My notes")
    mock_call.assert_called_once_with(
        "ak.wwise.core.object.setNotes", {"object": "\\path\\Sound", "value": "My notes"}
    )


# --- set_property ---


@patch("core.objects.call")
def test_set_property_args_no_platform(mock_call):
    mock_call.return_value = {}
    set_property(object="\\path\\Sound", property="Volume", value=-6.0)
    mock_call.assert_called_once_with("ak.wwise.core.object.setProperty", {
        "object": "\\path\\Sound",
        "property": "Volume",
        "value": -6.0,
    })


@patch("core.objects.call")
def test_set_property_args_with_platform(mock_call):
    mock_call.return_value = {}
    set_property(object="\\path\\Sound", property="Volume", value=-6.0, platform="Windows")
    args = mock_call.call_args[0][1]
    assert args["platform"] == "Windows"


@patch("core.objects.call")
def test_set_property_omits_platform_when_none(mock_call):
    mock_call.return_value = {}
    set_property(object="\\path\\Sound", property="Volume", value=0)
    args = mock_call.call_args[0][1]
    assert "platform" not in args


# --- set_reference ---


@patch("core.objects.call")
def test_set_reference_args(mock_call):
    mock_call.return_value = {}
    set_reference(object="\\path\\Sound", reference="OutputBus", value="Bus:Master Audio Bus")
    mock_call.assert_called_once_with("ak.wwise.core.object.setReference", {
        "object": "\\path\\Sound",
        "reference": "OutputBus",
        "value": "Bus:Master Audio Bus",
    })


# --- move_object ---


@patch("core.objects.call")
def test_move_object_args(mock_call):
    mock_call.return_value = {"id": "{x}"}
    move_object(object="\\old\\Sound", parent="\\new", on_name_conflict="rename")
    mock_call.assert_called_once_with("ak.wwise.core.object.move", {
        "object": "\\old\\Sound",
        "parent": "\\new",
        "onNameConflict": "rename",
    })


# --- copy_object ---


@patch("core.objects.call")
def test_copy_object_args(mock_call):
    mock_call.return_value = {"id": "{x}"}
    copy_object(object="\\src\\Sound", parent="\\dst", on_name_conflict="replace")
    mock_call.assert_called_once_with("ak.wwise.core.object.copy", {
        "object": "\\src\\Sound",
        "parent": "\\dst",
        "onNameConflict": "replace",
    })


# --- set_attenuation_curve ---


@patch("core.objects.call")
def test_set_attenuation_curve_args(mock_call):
    mock_call.return_value = {}
    points = [{"x": 0, "y": 0, "shape": "Linear"}, {"x": 100, "y": -200, "shape": "Exp3"}]
    set_attenuation_curve(
        object="Attenuation:MyAtt", curve_type="VolumeDryUsage", use="Custom", points=points
    )
    mock_call.assert_called_once_with("ak.wwise.core.object.setAttenuationCurve", {
        "object": "Attenuation:MyAtt",
        "curveType": "VolumeDryUsage",
        "use": "Custom",
        "points": points,
    })


@patch("core.objects.call")
def test_set_attenuation_curve_camelcase_key(mock_call):
    """curveType must be camelCase, not snake_case."""
    mock_call.return_value = {}
    set_attenuation_curve(object="\\att", curve_type="SpreadUsage", use="None", points=[])
    args = mock_call.call_args[0][1]
    assert "curveType" in args
    assert "curve_type" not in args


@patch("core.objects.call")
def test_set_attenuation_curve_with_platform(mock_call):
    mock_call.return_value = {}
    set_attenuation_curve(
        object="\\att", curve_type="VolumeDryUsage", use="Custom", points=[], platform="Mac"
    )
    args = mock_call.call_args[0][1]
    assert args["platform"] == "Mac"


@patch("core.objects.call")
def test_set_attenuation_curve_omits_platform_when_none(mock_call):
    mock_call.return_value = {}
    set_attenuation_curve(object="\\att", curve_type="VolumeDryUsage", use="None", points=[])
    args = mock_call.call_args[0][1]
    assert "platform" not in args


# --- set_randomizer ---


@patch("core.objects.call")
def test_set_randomizer_enabled_only(mock_call):
    mock_call.return_value = {}
    set_randomizer(object="\\path\\Sound", property="Volume", enabled=True)
    mock_call.assert_called_once_with("ak.wwise.core.object.setRandomizer", {
        "object": "\\path\\Sound",
        "property": "Volume",
        "enabled": True,
    })


@patch("core.objects.call")
def test_set_randomizer_min_max(mock_call):
    mock_call.return_value = {}
    set_randomizer(object="\\path\\Sound", property="Pitch", min=-50.0, max=50.0)
    args = mock_call.call_args[0][1]
    assert args["min"] == -50.0
    assert args["max"] == 50.0
    assert "enabled" not in args


@patch("core.objects.call")
def test_set_randomizer_all_fields(mock_call):
    mock_call.return_value = {}
    set_randomizer(
        object="\\path\\Sound", property="Volume",
        enabled=True, min=-6.0, max=6.0, platform="Windows",
    )
    args = mock_call.call_args[0][1]
    assert args == {
        "object": "\\path\\Sound",
        "property": "Volume",
        "enabled": True,
        "min": -6.0,
        "max": 6.0,
        "platform": "Windows",
    }


@patch("core.objects.call")
def test_set_randomizer_omits_none_fields(mock_call):
    mock_call.return_value = {}
    set_randomizer(object="\\path\\Sound", property="Volume", enabled=False)
    args = mock_call.call_args[0][1]
    assert "min" not in args
    assert "max" not in args
    assert "platform" not in args


# --- set_state_groups ---


@patch("core.objects.call")
def test_set_state_groups_args(mock_call):
    mock_call.return_value = {}
    groups = ["StateGroup:Alive", "{aabb-1122}"]
    set_state_groups(object="\\path\\Sound", state_groups=groups)
    mock_call.assert_called_once_with("ak.wwise.core.object.setStateGroups", {
        "object": "\\path\\Sound",
        "stateGroups": groups,
    })


# --- set_state_properties ---


@patch("core.objects.call")
def test_set_state_properties_args(mock_call):
    mock_call.return_value = {}
    props = ["Volume", "Pitch"]
    set_state_properties(object="\\path\\Sound", state_properties=props)
    mock_call.assert_called_once_with("ak.wwise.core.object.setStateProperties", {
        "object": "\\path\\Sound",
        "stateProperties": props,
    })


# --- switch_container_add_assignment ---


@patch("core.objects.call")
def test_switch_container_add_assignment_args(mock_call):
    mock_call.return_value = {}
    switch_container_add_assignment(child="\\path\\Child", state_or_switch="\\switches\\Switch1")
    mock_call.assert_called_once_with("ak.wwise.core.switchContainer.addAssignment", {
        "child": "\\path\\Child",
        "stateOrSwitch": "\\switches\\Switch1",
    })


@patch("core.objects.call")
def test_switch_container_add_assignment_camelcase_key(mock_call):
    """stateOrSwitch must be camelCase."""
    mock_call.return_value = {}
    switch_container_add_assignment(child="\\c", state_or_switch="\\s")
    args = mock_call.call_args[0][1]
    assert "stateOrSwitch" in args
    assert "state_or_switch" not in args


# --- switch_container_remove_assignment ---


@patch("core.objects.call")
def test_switch_container_remove_assignment_args(mock_call):
    mock_call.return_value = {}
    switch_container_remove_assignment(child="\\path\\Child", state_or_switch="\\switches\\Switch1")
    mock_call.assert_called_once_with("ak.wwise.core.switchContainer.removeAssignment", {
        "child": "\\path\\Child",
        "stateOrSwitch": "\\switches\\Switch1",
    })
