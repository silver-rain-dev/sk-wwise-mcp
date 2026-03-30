import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from waapi import CannotConnectToWaapiException
from mcp_objects.server import (
    create_wwise_objects,
    delete_wwise_objects,
    set_wwise_object_name,
    set_wwise_object_notes,
    set_wwise_object_properties,
    move_wwise_objects,
    copy_wwise_object,
)


# --- create_wwise_objects ---


@patch("mcp_objects.server._create_objects")
def test_create_wwise_objects_single(mock_create):
    mock_create.return_value = [{"id": "{aabb}", "name": "NewSound"}]
    result = create_wwise_objects(
        objects=[{
            "parent": "\\Containers\\Default Work Unit",
            "type": "Sound",
            "name": "NewSound",
        }],
    )
    assert result[0]["name"] == "NewSound"
    mock_create.assert_called_once_with(objects=[{
        "parent": "\\Containers\\Default Work Unit",
        "type": "Sound",
        "name": "NewSound",
    }], default_parent=None)


@patch("mcp_objects.server._create_objects")
def test_create_wwise_objects_multiple(mock_create):
    mock_create.return_value = [
        {"id": "{aa}", "name": "Obj1"},
        {"id": "{bb}", "name": "Obj2"},
    ]
    result = create_wwise_objects(
        objects=[
            {"parent": "\\Events\\Default Work Unit", "type": "Event", "name": "Obj1"},
            {"parent": "\\Busses\\Master Audio Bus", "type": "Bus", "name": "Obj2"},
        ],
    )
    assert len(result) == 2
    assert result[0]["name"] == "Obj1"
    assert result[1]["name"] == "Obj2"


@patch("mcp_objects.server._create_objects")
def test_create_wwise_objects_with_children(mock_create):
    mock_create.return_value = [{"id": "{aabb}", "name": "Container", "children": []}]
    children = [{"type": "Sound", "name": "Child1"}]
    result = create_wwise_objects(
        objects=[{
            "parent": "\\Containers\\Default Work Unit",
            "type": "RandomSequenceContainer",
            "name": "Container",
            "children": children,
            "properties": {"Volume": -6.0},
        }],
    )
    assert result[0]["name"] == "Container"


@patch("mcp_objects.server._create_objects", side_effect=CannotConnectToWaapiException)
def test_create_wwise_objects_connection_error(mock_create):
    result = create_wwise_objects(objects=[{"parent": "\\test", "type": "Sound", "name": "S"}])
    assert "error" in result


# --- delete_wwise_objects ---


@patch("mcp_objects.server._delete_objects")
def test_delete_wwise_objects_single(mock_delete):
    mock_delete.return_value = [{}]
    result = delete_wwise_objects(objects=["\\Containers\\Default Work Unit\\MySound"])
    assert result == [{}]
    mock_delete.assert_called_once_with(objects=["\\Containers\\Default Work Unit\\MySound"])


@patch("mcp_objects.server._delete_objects")
def test_delete_wwise_objects_multiple(mock_delete):
    mock_delete.return_value = [{}, {}]
    result = delete_wwise_objects(objects=["Event:Play_Move_01", "Event:Play_Cry_01"])
    assert len(result) == 2


@patch("mcp_objects.server._delete_objects")
def test_delete_wwise_objects_by_guid(mock_delete):
    mock_delete.return_value = [{}]
    result = delete_wwise_objects(objects=["{aabbcc00-1122-3344-5566-77889900aabb}"])
    mock_delete.assert_called_once_with(objects=["{aabbcc00-1122-3344-5566-77889900aabb}"])


@patch("mcp_objects.server._delete_objects", side_effect=CannotConnectToWaapiException)
def test_delete_wwise_objects_connection_error(mock_delete):
    result = delete_wwise_objects(objects=["\\test"])
    assert "error" in result


# --- set_wwise_object_name ---


@patch("mcp_objects.server._set_name")
def test_set_wwise_object_name_success(mock_set):
    mock_set.return_value = {}
    result = set_wwise_object_name(object="\\path\\Sound", value="NewName")
    assert result == {}
    mock_set.assert_called_once_with(object="\\path\\Sound", value="NewName")


@patch("mcp_objects.server._set_name", side_effect=CannotConnectToWaapiException)
def test_set_wwise_object_name_connection_error(mock_set):
    result = set_wwise_object_name(object="\\test", value="X")
    assert "error" in result


# --- set_wwise_object_notes ---


@patch("mcp_objects.server._set_notes")
def test_set_wwise_object_notes_success(mock_set):
    mock_set.return_value = {}
    result = set_wwise_object_notes(object="\\path\\Sound", value="Some notes")
    assert result == {}
    mock_set.assert_called_once_with(object="\\path\\Sound", value="Some notes")


@patch("mcp_objects.server._set_notes", side_effect=CannotConnectToWaapiException)
def test_set_wwise_object_notes_connection_error(mock_set):
    result = set_wwise_object_notes(object="\\test", value="X")
    assert "error" in result


# --- set_wwise_object_properties ---


@patch("mcp_objects.server._set_properties")
def test_set_wwise_object_properties_single_property(mock_set):
    mock_set.return_value = [{"object": "\\path\\Sound", "ok": True}]
    result = set_wwise_object_properties(
        operations=[{"object": "\\path\\Sound", "properties": {"Volume": -6.0}}]
    )
    assert result[0]["ok"] is True
    mock_set.assert_called_once_with(operations=[{
        "object": "\\path\\Sound", "properties": {"Volume": -6.0},
    }], parent=None)


@patch("mcp_objects.server._set_properties")
def test_set_wwise_object_properties_with_references(mock_set):
    mock_set.return_value = [{"object": "\\path\\Sound", "ok": True}]
    result = set_wwise_object_properties(
        operations=[{
            "object": "\\path\\Sound",
            "properties": {"OverrideOutput": True},
            "references": {"OutputBus": "Bus:Music_Bus"},
        }]
    )
    assert result[0]["ok"] is True


@patch("mcp_objects.server._set_properties")
def test_set_wwise_object_properties_multiple(mock_set):
    mock_set.return_value = [
        {"object": "\\a", "ok": True},
        {"object": "\\b", "ok": True},
    ]
    result = set_wwise_object_properties(
        operations=[
            {"object": "\\a", "properties": {"Volume": -3.0}},
            {"object": "\\b", "references": {"OutputBus": "Bus:SFX_Bus"}},
        ]
    )
    assert len(result) == 2


@patch("mcp_objects.server._set_properties", side_effect=CannotConnectToWaapiException)
def test_set_wwise_object_properties_connection_error(mock_set):
    result = set_wwise_object_properties(
        operations=[{"object": "\\test", "properties": {"Volume": 0}}]
    )
    assert "error" in result


# --- move_wwise_objects ---


@patch("mcp_objects.server._move_objects")
def test_move_wwise_objects_single(mock_move):
    mock_move.return_value = [{"id": "{aabb}", "name": "Sound", "path": "\\new\\path"}]
    result = move_wwise_objects(objects=[{"object": "\\old\\Sound", "parent": "\\new"}])
    assert result[0]["path"] == "\\new\\path"
    mock_move.assert_called_once_with(objects=[{"object": "\\old\\Sound", "parent": "\\new"}], source_parent=None, new_parent=None)


@patch("mcp_objects.server._move_objects")
def test_move_wwise_objects_multiple(mock_move):
    mock_move.return_value = [
        {"id": "{aa}", "name": "A"},
        {"id": "{bb}", "name": "B"},
    ]
    result = move_wwise_objects(objects=[
        {"object": "{aa}", "parent": "{cc}"},
        {"object": "{bb}", "parent": "{cc}"},
    ])
    assert len(result) == 2


@patch("mcp_objects.server._move_objects")
def test_move_wwise_objects_with_rename(mock_move):
    mock_move.return_value = [{"id": "{aabb}", "name": "Sound_01"}]
    result = move_wwise_objects(
        objects=[{"object": "\\old\\Sound", "parent": "\\new", "on_name_conflict": "rename"}]
    )
    mock_move.assert_called_once_with(
        objects=[{"object": "\\old\\Sound", "parent": "\\new", "on_name_conflict": "rename"}],
        source_parent=None, new_parent=None,
    )


@patch("mcp_objects.server._move_objects", side_effect=CannotConnectToWaapiException)
def test_move_wwise_objects_connection_error(mock_move):
    result = move_wwise_objects(objects=[{"object": "\\a", "parent": "\\b"}])
    assert "error" in result


# --- copy_wwise_object ---


@patch("mcp_objects.server._copy_object")
def test_copy_wwise_object_success(mock_copy):
    mock_copy.return_value = {"id": "{ccdd}", "name": "Sound"}
    result = copy_wwise_object(object="\\src\\Sound", parent="\\dst")
    assert result["id"] == "{ccdd}"
    mock_copy.assert_called_once_with(object="\\src\\Sound", parent="\\dst", on_name_conflict="fail")


@patch("mcp_objects.server._copy_object", side_effect=CannotConnectToWaapiException)
def test_copy_wwise_object_connection_error(mock_copy):
    result = copy_wwise_object(object="\\a", parent="\\b")
    assert "error" in result
