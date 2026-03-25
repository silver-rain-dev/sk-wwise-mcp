import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from waapi import CannotConnectToWaapiException
from mcp_objects.server import (
    create_wwise_object,
    delete_wwise_object,
    set_wwise_object_name,
    set_wwise_object_notes,
    set_wwise_object_property,
    set_wwise_object_reference,
    move_wwise_object,
    copy_wwise_object,
)


# --- create_wwise_object ---


@patch("mcp_objects.server._create_object")
def test_create_wwise_object_basic(mock_create):
    mock_create.return_value = {"id": "{aabb}", "name": "NewSound"}
    result = create_wwise_object(
        parent="\\Actor-Mixer Hierarchy\\Default Work Unit",
        type="Sound",
        name="NewSound",
    )
    assert result["name"] == "NewSound"
    mock_create.assert_called_once_with(
        parent="\\Actor-Mixer Hierarchy\\Default Work Unit",
        type="Sound",
        name="NewSound",
        on_name_conflict="fail",
        platform=None,
        notes=None,
        children=None,
        properties=None,
        list_name=None,
    )


@patch("mcp_objects.server._create_object")
def test_create_wwise_object_with_children_and_properties(mock_create):
    mock_create.return_value = {"id": "{aabb}", "name": "Container", "children": []}
    children = [{"type": "Sound", "name": "Child1"}]
    props = {"Volume": -6.0}
    result = create_wwise_object(
        parent="\\Actor-Mixer Hierarchy\\Default Work Unit",
        type="RandomSequenceContainer",
        name="Container",
        children=children,
        properties=props,
    )
    assert result["name"] == "Container"
    mock_create.assert_called_once_with(
        parent="\\Actor-Mixer Hierarchy\\Default Work Unit",
        type="RandomSequenceContainer",
        name="Container",
        on_name_conflict="fail",
        platform=None,
        notes=None,
        children=children,
        properties=props,
        list_name=None,
    )


@patch("mcp_objects.server._create_object", side_effect=CannotConnectToWaapiException)
def test_create_wwise_object_connection_error(mock_create):
    result = create_wwise_object(parent="\\test", type="Sound", name="S")
    assert "error" in result


# --- delete_wwise_object ---


@patch("mcp_objects.server._delete_object")
def test_delete_wwise_object_by_path(mock_delete):
    mock_delete.return_value = {}
    result = delete_wwise_object(object="\\Actor-Mixer Hierarchy\\Default Work Unit\\MySound")
    assert result == {}
    mock_delete.assert_called_once_with(object="\\Actor-Mixer Hierarchy\\Default Work Unit\\MySound")


@patch("mcp_objects.server._delete_object")
def test_delete_wwise_object_by_guid(mock_delete):
    mock_delete.return_value = {}
    result = delete_wwise_object(object="{aabbcc00-1122-3344-5566-77889900aabb}")
    mock_delete.assert_called_once_with(object="{aabbcc00-1122-3344-5566-77889900aabb}")


@patch("mcp_objects.server._delete_object", side_effect=CannotConnectToWaapiException)
def test_delete_wwise_object_connection_error(mock_delete):
    result = delete_wwise_object(object="\\test")
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


# --- set_wwise_object_property ---


@patch("mcp_objects.server._set_property")
def test_set_wwise_object_property_success(mock_set):
    mock_set.return_value = {}
    result = set_wwise_object_property(object="\\path\\Sound", property="Volume", value=-6.0)
    assert result == {}
    mock_set.assert_called_once_with(object="\\path\\Sound", property="Volume", value=-6.0, platform=None)


@patch("mcp_objects.server._set_property")
def test_set_wwise_object_property_with_platform(mock_set):
    mock_set.return_value = {}
    result = set_wwise_object_property(
        object="\\path\\Sound", property="Volume", value=-3.0, platform="Windows"
    )
    mock_set.assert_called_once_with(
        object="\\path\\Sound", property="Volume", value=-3.0, platform="Windows"
    )


@patch("mcp_objects.server._set_property", side_effect=CannotConnectToWaapiException)
def test_set_wwise_object_property_connection_error(mock_set):
    result = set_wwise_object_property(object="\\test", property="Volume", value=0)
    assert "error" in result


# --- set_wwise_object_reference ---


@patch("mcp_objects.server._set_reference")
def test_set_wwise_object_reference_success(mock_set):
    mock_set.return_value = {}
    result = set_wwise_object_reference(
        object="\\path\\Sound", reference="OutputBus", value="Bus:Master Audio Bus"
    )
    assert result == {}
    mock_set.assert_called_once_with(
        object="\\path\\Sound", reference="OutputBus", value="Bus:Master Audio Bus"
    )


@patch("mcp_objects.server._set_reference", side_effect=CannotConnectToWaapiException)
def test_set_wwise_object_reference_connection_error(mock_set):
    result = set_wwise_object_reference(object="\\test", reference="OutputBus", value="\\bus")
    assert "error" in result


# --- move_wwise_object ---


@patch("mcp_objects.server._move_object")
def test_move_wwise_object_success(mock_move):
    mock_move.return_value = {"id": "{aabb}", "name": "Sound", "path": "\\new\\path"}
    result = move_wwise_object(object="\\old\\Sound", parent="\\new")
    assert result["path"] == "\\new\\path"
    mock_move.assert_called_once_with(object="\\old\\Sound", parent="\\new", on_name_conflict="fail")


@patch("mcp_objects.server._move_object")
def test_move_wwise_object_with_rename(mock_move):
    mock_move.return_value = {"id": "{aabb}", "name": "Sound_01"}
    result = move_wwise_object(object="\\old\\Sound", parent="\\new", on_name_conflict="rename")
    mock_move.assert_called_once_with(object="\\old\\Sound", parent="\\new", on_name_conflict="rename")


@patch("mcp_objects.server._move_object", side_effect=CannotConnectToWaapiException)
def test_move_wwise_object_connection_error(mock_move):
    result = move_wwise_object(object="\\a", parent="\\b")
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
