"""Tests for core.objects batch operations and helper functions.

Covers create_objects, delete_objects, set_properties, move_objects,
switch_container_add_assignments, switch_container_remove_assignments,
blend_container_add_assignment, blend_container_remove_assignment,
set_game_parameter_range, and _is_short_name.
"""

import sys
from pathlib import Path
from unittest.mock import patch, call as mock_call

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.objects import (
    create_objects,
    delete_objects,
    set_properties,
    move_objects,
    switch_container_add_assignments,
    switch_container_remove_assignments,
    blend_container_add_assignment,
    blend_container_remove_assignment,
    set_game_parameter_range,
    _is_short_name,
)


# --- _is_short_name ---


def test_is_short_name_true():
    assert _is_short_name("MySound") is True


def test_is_short_name_path():
    assert _is_short_name("\\Containers\\WU\\MySound") is False


def test_is_short_name_guid():
    assert _is_short_name("{aabb-1122-3344}") is False


def test_is_short_name_qualified():
    assert _is_short_name("Event:Play_Sound") is False


# --- create_objects ---


@patch("core.objects.call")
def test_create_objects_basic(mock_call_fn):
    mock_call_fn.return_value = {"id": "{x}", "name": "S"}
    objects = [{"type": "Sound", "name": "S"}]
    results = create_objects(objects, default_parent="\\path\\WU")
    assert len(results) == 1
    assert results[0]["name"] == "S"
    mock_call_fn.assert_called_once()


@patch("core.objects.call")
def test_create_objects_per_object_parent(mock_call_fn):
    mock_call_fn.return_value = {"id": "{x}", "name": "S"}
    objects = [{"type": "Sound", "name": "S", "parent": "\\other\\WU"}]
    create_objects(objects)
    args = mock_call_fn.call_args[0][1]
    assert args["parent"] == "\\other\\WU"


def test_create_objects_no_parent_returns_error():
    objects = [{"type": "Sound", "name": "S"}]
    results = create_objects(objects)
    assert "error" in results[0]


@patch("core.objects.call")
def test_create_objects_handles_exception(mock_call_fn):
    mock_call_fn.side_effect = Exception("WAAPI error")
    objects = [{"type": "Sound", "name": "S"}]
    results = create_objects(objects, default_parent="\\path\\WU")
    assert "error" in results[0]
    assert results[0]["name"] == "S"


@patch("core.objects.call")
def test_create_objects_with_properties(mock_call_fn):
    mock_call_fn.return_value = {"id": "{x}", "name": "S"}
    objects = [{"type": "Sound", "name": "S", "properties": {"Volume": -6.0}}]
    create_objects(objects, default_parent="\\path\\WU")
    args = mock_call_fn.call_args[0][1]
    assert args["@Volume"] == -6.0


@patch("core.objects.call")
def test_create_objects_multiple(mock_call_fn):
    mock_call_fn.side_effect = [
        {"id": "{1}", "name": "A"},
        {"id": "{2}", "name": "B"},
    ]
    objects = [
        {"type": "Sound", "name": "A"},
        {"type": "Sound", "name": "B"},
    ]
    results = create_objects(objects, default_parent="\\path\\WU")
    assert len(results) == 2
    assert results[0]["name"] == "A"
    assert results[1]["name"] == "B"


# --- delete_objects ---


@patch("core.objects.call")
def test_delete_objects_basic(mock_call_fn):
    mock_call_fn.return_value = {}
    results = delete_objects(["\\path\\Sound1", "\\path\\Sound2"])
    assert len(results) == 2
    assert mock_call_fn.call_count == 2


@patch("core.objects.call")
def test_delete_objects_handles_exception(mock_call_fn):
    mock_call_fn.side_effect = [Exception("not found"), {}]
    results = delete_objects(["\\bad\\path", "\\good\\path"])
    assert "error" in results[0]
    assert "error" not in results[1]


# --- set_properties ---


@patch("core.objects.call")
def test_set_properties_single_property(mock_call_fn):
    mock_call_fn.return_value = {}
    ops = [{"object": "\\path\\Sound", "properties": {"Volume": -6.0}}]
    results = set_properties(ops)
    assert len(results) == 1
    assert results[0]["ok"] is True


@patch("core.objects.call")
def test_set_properties_with_references(mock_call_fn):
    mock_call_fn.return_value = {}
    ops = [{"object": "\\path\\Sound", "references": {"OutputBus": "Bus:Master Audio Bus"}}]
    results = set_properties(ops)
    assert results[0]["ok"] is True
    args = mock_call_fn.call_args[0][1]
    assert args["reference"] == "OutputBus"
    assert args["value"] == "Bus:Master Audio Bus"


@patch("core.objects.call")
def test_set_properties_with_platform(mock_call_fn):
    mock_call_fn.return_value = {}
    ops = [{"object": "\\path\\Sound", "properties": {"Volume": -3.0}, "platform": "Windows"}]
    results = set_properties(ops)
    assert results[0]["ok"] is True
    args = mock_call_fn.call_args[0][1]
    assert args["platform"] == "Windows"


@patch("core.objects.call")
def test_set_properties_error_in_property(mock_call_fn):
    mock_call_fn.side_effect = Exception("invalid property")
    ops = [{"object": "\\path\\Sound", "properties": {"BadProp": 0}}]
    results = set_properties(ops)
    assert results[0]["ok"] is False
    assert len(results[0]["errors"]) == 1


@patch("core.objects._resolve_children_names")
@patch("core.objects.call")
def test_set_properties_with_parent_short_names(mock_call_fn, mock_resolve):
    mock_resolve.return_value = {"Step_01": "\\path\\Footsteps\\Step_01"}
    mock_call_fn.return_value = {}
    ops = [{"object": "Step_01", "properties": {"Volume": -6.0}}]
    results = set_properties(ops, parent="\\path\\Footsteps")
    assert results[0]["ok"] is True


@patch("core.objects._resolve_children_names")
@patch("core.objects.call")
def test_set_properties_short_name_not_found(mock_call_fn, mock_resolve):
    mock_resolve.return_value = {}
    ops = [{"object": "Unknown", "properties": {"Volume": 0}}]
    results = set_properties(ops, parent="\\path\\Parent")
    assert results[0]["ok"] is False


# --- move_objects ---


@patch("core.objects.call")
def test_move_objects_basic(mock_call_fn):
    mock_call_fn.return_value = {"id": "{x}", "name": "S", "path": "\\new\\S"}
    objects = [{"object": "\\old\\S"}]
    results = move_objects(objects, new_parent="\\new")
    assert len(results) == 1
    mock_call_fn.assert_called_once()


def test_move_objects_no_parent_returns_error():
    objects = [{"object": "\\old\\S"}]
    results = move_objects(objects)
    assert "error" in results[0]


@patch("core.objects.call")
def test_move_objects_per_entry_parent(mock_call_fn):
    mock_call_fn.return_value = {"id": "{x}"}
    objects = [{"object": "\\old\\S", "parent": "\\specific\\dest"}]
    move_objects(objects)
    args = mock_call_fn.call_args[0][1]
    assert args["parent"] == "\\specific\\dest"


@patch("core.objects._resolve_children_names")
@patch("core.objects.call")
def test_move_objects_with_source_parent(mock_call_fn, mock_resolve):
    mock_resolve.return_value = {"MySound": "\\src\\MySound"}
    mock_call_fn.return_value = {"id": "{x}"}
    objects = [{"object": "MySound"}]
    results = move_objects(objects, source_parent="\\src", new_parent="\\dst")
    assert "error" not in results[0]


@patch("core.objects._resolve_children_names")
def test_move_objects_short_name_not_found(mock_resolve):
    mock_resolve.return_value = {}
    objects = [{"object": "Unknown"}]
    results = move_objects(objects, source_parent="\\src", new_parent="\\dst")
    assert "error" in results[0]


@patch("core.objects.call")
def test_move_objects_handles_exception(mock_call_fn):
    mock_call_fn.side_effect = Exception("move failed")
    objects = [{"object": "\\path\\S"}]
    results = move_objects(objects, new_parent="\\dst")
    assert "error" in results[0]


# --- switch_container_add_assignments ---


@patch("core.objects.call")
def test_switch_add_assignments_full_paths(mock_call_fn):
    mock_call_fn.return_value = {}
    assignments = [{"child": "\\path\\Child", "state_or_switch": "\\switches\\S1"}]
    results = switch_container_add_assignments(assignments)
    assert len(results) == 1
    mock_call_fn.assert_called_once_with(
        "ak.wwise.core.switchContainer.addAssignment",
        {"child": "\\path\\Child", "stateOrSwitch": "\\switches\\S1"},
    )


@patch("core.objects._resolve_switch_container_names")
@patch("core.objects.call")
def test_switch_add_assignments_short_names(mock_call_fn, mock_resolve):
    mock_resolve.return_value = (
        {"Sound1": "\\c\\Sound1"},
        {"Switch1": "\\s\\Switch1"},
    )
    mock_call_fn.return_value = {}
    assignments = [{"child": "Sound1", "state_or_switch": "Switch1"}]
    results = switch_container_add_assignments(assignments, container="\\c\\SC")
    assert len(results) == 1
    mock_call_fn.assert_called_once_with(
        "ak.wwise.core.switchContainer.addAssignment",
        {"child": "\\c\\Sound1", "stateOrSwitch": "\\s\\Switch1"},
    )


@patch("core.objects._resolve_switch_container_names")
def test_switch_add_assignments_child_not_found(mock_resolve):
    mock_resolve.return_value = ({}, {"Switch1": "\\s\\Switch1"})
    assignments = [{"child": "Missing", "state_or_switch": "Switch1"}]
    results = switch_container_add_assignments(assignments, container="\\c\\SC")
    assert "error" in results[0]


@patch("core.objects._resolve_switch_container_names")
def test_switch_add_assignments_switch_not_found(mock_resolve):
    mock_resolve.return_value = ({"Sound1": "\\c\\Sound1"}, {})
    assignments = [{"child": "Sound1", "state_or_switch": "Missing"}]
    results = switch_container_add_assignments(assignments, container="\\c\\SC")
    assert "error" in results[0]


# --- switch_container_remove_assignments ---


@patch("core.objects.call")
def test_switch_remove_assignments_full_paths(mock_call_fn):
    mock_call_fn.return_value = {}
    assignments = [{"child": "\\path\\Child", "state_or_switch": "\\switches\\S1"}]
    results = switch_container_remove_assignments(assignments)
    assert len(results) == 1
    mock_call_fn.assert_called_once_with(
        "ak.wwise.core.switchContainer.removeAssignment",
        {"child": "\\path\\Child", "stateOrSwitch": "\\switches\\S1"},
    )


# --- blend_container_add_assignment ---


@patch("core.objects.call")
def test_blend_add_assignment(mock_call_fn):
    mock_call_fn.return_value = {}
    query = {"blendTrack": "{guid}", "child": "\\path\\Sound"}
    blend_container_add_assignment(query)
    mock_call_fn.assert_called_once_with(
        "ak.wwise.core.blendContainer.addAssignment", query
    )


# --- blend_container_remove_assignment ---


@patch("core.objects.call")
def test_blend_remove_assignment(mock_call_fn):
    mock_call_fn.return_value = {}
    query = {"blendTrack": "{guid}", "child": "\\path\\Sound"}
    blend_container_remove_assignment(query)
    mock_call_fn.assert_called_once_with(
        "ak.wwise.core.blendContainer.removeAssignment", query
    )


# --- set_game_parameter_range ---


@patch("core.objects.call")
def test_set_game_parameter_range(mock_call_fn):
    mock_call_fn.return_value = {}
    query = {"object": "GameParameter:Speed", "min": 0, "max": 100}
    set_game_parameter_range(query)
    mock_call_fn.assert_called_once_with(
        "ak.wwise.core.gameParameter.setRange", query
    )
