"""Integration tests for object CRUD operations against a live Wwise project."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.objects import (
    create_object,
    delete_object,
    set_name,
    set_notes,
    set_property,
    set_reference,
    move_object,
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
