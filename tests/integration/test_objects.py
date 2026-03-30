"""Integration tests for object CRUD operations against a live Wwise project."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.objects import (
    create_object,
    create_objects,
    delete_object,
    delete_objects,
    set_name,
    set_notes,
    set_property,
    set_reference,
    set_properties,
    move_object,
    move_objects,
    copy_object,
)

pytestmark = pytest.mark.integration


def test_create_and_delete(wwise):
    result = create_object(
        parent="\\Containers\\Default Work Unit",
        type="ActorMixer",
        name="IntegrationTestObj",
        on_name_conflict="replace",
    )
    assert "id" in result
    assert result["name"] == "IntegrationTestObj"

    del_result = delete_object(object=result["id"])
    assert del_result is not None


def test_create_with_children(wwise):
    result = create_object(
        parent="\\Containers\\Default Work Unit",
        type="ActorMixer",
        name="IntTestParent",
        on_name_conflict="replace",
        children=[
            {"type": "Sound", "name": "Child_01"},
            {"type": "Sound", "name": "Child_02"},
        ],
    )
    assert "id" in result
    assert "children" in result
    assert len(result["children"]) == 2

    # Cleanup
    delete_object(object=result["id"])


def test_create_with_properties(wwise):
    result = create_object(
        parent="\\Containers\\Default Work Unit",
        type="Sound",
        name="IntTestSound",
        on_name_conflict="replace",
        properties={"Volume": -6.0, "Pitch": 200},
    )
    assert "id" in result

    # Cleanup
    delete_object(object=result["id"])


def test_create_objects_batch(wwise):
    """Test creating multiple objects across different parents in one batch."""
    results = create_objects([
        {
            "parent": "\\Containers\\Default Work Unit",
            "type": "ActorMixer",
            "name": "IntTestBatch1",
            "on_name_conflict": "replace",
        },
        {
            "parent": "\\Containers\\Default Work Unit",
            "type": "Sound",
            "name": "IntTestBatch2",
            "on_name_conflict": "replace",
        },
    ])
    assert len(results) == 2
    assert "id" in results[0]
    assert "id" in results[1]

    # Cleanup
    delete_objects([results[0]["id"], results[1]["id"]])


def test_delete_objects_batch(wwise):
    """Test deleting multiple objects in one batch."""
    obj1 = create_object(
        parent="\\Containers\\Default Work Unit",
        type="Sound", name="IntTestDelBatch1", on_name_conflict="replace",
    )
    obj2 = create_object(
        parent="\\Containers\\Default Work Unit",
        type="Sound", name="IntTestDelBatch2", on_name_conflict="replace",
    )

    results = delete_objects([obj1["id"], obj2["id"]])
    assert len(results) == 2


def test_set_property(wwise):
    # Create a temp object
    obj = create_object(
        parent="\\Containers\\Default Work Unit",
        type="Sound",
        name="IntTestPropSound",
        on_name_conflict="replace",
    )

    result = set_property(object=obj["id"], property="Volume", value=-12.0)
    assert result is not None

    # Cleanup
    delete_object(object=obj["id"])


def test_set_properties_batch(wwise):
    """Test setting properties and references on multiple objects in one batch."""
    obj1 = create_object(
        parent="\\Containers\\Default Work Unit",
        type="Sound", name="IntTestPropBatch1", on_name_conflict="replace",
    )
    obj2 = create_object(
        parent="\\Containers\\Default Work Unit",
        type="Sound", name="IntTestPropBatch2", on_name_conflict="replace",
    )

    results = set_properties([
        {"object": obj1["id"], "properties": {"Volume": -6.0, "Pitch": 100}},
        {"object": obj2["id"], "properties": {"Volume": -3.0}},
    ])
    assert len(results) == 2
    assert results[0]["ok"] is True
    assert results[1]["ok"] is True

    # Cleanup
    delete_objects([obj1["id"], obj2["id"]])


def test_set_name(wwise):
    obj = create_object(
        parent="\\Containers\\Default Work Unit",
        type="Sound",
        name="IntTestRenameMe",
        on_name_conflict="replace",
    )

    result = set_name(object=obj["id"], value="IntTestRenamed")
    assert result is not None

    # Cleanup
    delete_object(object=obj["id"])


def test_set_notes(wwise):
    obj = create_object(
        parent="\\Containers\\Default Work Unit",
        type="Sound",
        name="IntTestNotesObj",
        on_name_conflict="replace",
    )

    result = set_notes(object=obj["id"], value="Integration test notes")
    assert result is not None

    # Cleanup
    delete_object(object=obj["id"])


def test_move_object(wwise):
    # Create parent and child
    parent1 = create_object(
        parent="\\Containers\\Default Work Unit",
        type="ActorMixer", name="IntTestMoveFrom",
        on_name_conflict="replace",
    )
    child = create_object(
        parent=parent1["id"],
        type="Sound", name="IntTestMoveChild",
    )
    parent2 = create_object(
        parent="\\Containers\\Default Work Unit",
        type="ActorMixer", name="IntTestMoveTo",
        on_name_conflict="replace",
    )

    result = move_object(object=child["id"], parent=parent2["id"])
    assert result is not None

    # Cleanup
    delete_object(object=parent1["id"])
    delete_object(object=parent2["id"])


def test_move_objects_batch(wwise):
    """Test moving multiple objects in one batch."""
    parent1 = create_object(
        parent="\\Containers\\Default Work Unit",
        type="ActorMixer", name="IntTestMoveBatchFrom",
        on_name_conflict="replace",
        children=[
            {"type": "Sound", "name": "IntTestMoveB1"},
            {"type": "Sound", "name": "IntTestMoveB2"},
        ],
    )
    parent2 = create_object(
        parent="\\Containers\\Default Work Unit",
        type="ActorMixer", name="IntTestMoveBatchTo",
        on_name_conflict="replace",
    )

    child_ids = [c["id"] for c in parent1["children"]]
    results = move_objects([
        {"object": child_ids[0], "parent": parent2["id"]},
        {"object": child_ids[1], "parent": parent2["id"]},
    ])
    assert len(results) == 2
    assert "id" in results[0]
    assert "id" in results[1]

    # Cleanup
    delete_objects([parent1["id"], parent2["id"]])


def test_copy_object(wwise):
    source = create_object(
        parent="\\Containers\\Default Work Unit",
        type="Sound", name="IntTestCopySource",
        on_name_conflict="replace",
    )
    dest = create_object(
        parent="\\Containers\\Default Work Unit",
        type="ActorMixer", name="IntTestCopyDest",
        on_name_conflict="replace",
    )

    result = copy_object(object=source["id"], parent=dest["id"])
    assert result is not None

    # Cleanup
    delete_object(object=source["id"])
    delete_object(object=dest["id"])
