"""Integration tests for container operations against a live Wwise project."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.objects import (
    create_object,
    delete_object,
    switch_container_add_assignment,
    switch_container_add_assignments,
    switch_container_remove_assignment,
    set_attenuation_curve,
    set_state_groups,
)
from core.waapi_util import call

pytestmark = pytest.mark.integration


def test_switch_assignment_add_remove(wwise):
    """Test adding and removing a switch assignment."""
    # Get existing assignments on Weapons
    assignments = call("ak.wwise.core.switchContainer.getAssignments", {
        "id": "\\Containers\\Default Work Unit\\TestSFX\\Weapons",
    })
    initial_count = len(assignments.get("return", []))

    # Create a new Sound under Weapons
    obj = create_object(
        parent="\\Containers\\Default Work Unit\\TestSFX\\Weapons",
        type="Sound", name="IntTestSwitchChild",
        on_name_conflict="replace",
    )

    # Assign to Wood switch
    add_result = switch_container_add_assignment(
        child=obj["id"],
        state_or_switch="\\Switches\\Default Work Unit\\Surface\\Wood",
    )
    assert add_result is not None

    # Verify assignment exists
    after_add = call("ak.wwise.core.switchContainer.getAssignments", {
        "id": "\\Containers\\Default Work Unit\\TestSFX\\Weapons",
    })
    assert len(after_add["return"]) == initial_count + 1

    # Remove assignment
    remove_result = switch_container_remove_assignment(
        child=obj["id"],
        state_or_switch="\\Switches\\Default Work Unit\\Surface\\Wood",
    )
    assert remove_result is not None

    # Cleanup
    delete_object(object=obj["id"])


def test_set_attenuation_curve(wwise):
    """Test setting an attenuation curve."""
    result = set_attenuation_curve(
        object="\\Attenuations\\Default Work Unit\\TestAtten",
        curve_type="VolumeDryUsage",
        use="Custom",
        points=[
            {"x": 0, "y": 0, "shape": "Linear"},
            {"x": 100, "y": -200, "shape": "Linear"},
        ],
    )
    assert result is not None


def test_switch_assignment_batch(wwise):
    """Test adding multiple switch assignments in one batch."""
    obj1 = create_object(
        parent="\\Containers\\Default Work Unit\\TestSFX\\Weapons",
        type="Sound", name="IntTestBatchSwitch1",
        on_name_conflict="replace",
    )
    obj2 = create_object(
        parent="\\Containers\\Default Work Unit\\TestSFX\\Weapons",
        type="Sound", name="IntTestBatchSwitch2",
        on_name_conflict="replace",
    )

    results = switch_container_add_assignments([
        {"child": obj1["id"], "state_or_switch": "\\Switches\\Default Work Unit\\Surface\\Wood"},
        {"child": obj2["id"], "state_or_switch": "\\Switches\\Default Work Unit\\Surface\\Wood"},
    ])
    assert len(results) == 2

    # Cleanup
    delete_object(object=obj1["id"])
    delete_object(object=obj2["id"])


def test_set_state_groups(wwise):
    """Test associating state groups with an object."""
    result = set_state_groups(
        object="\\Containers\\Default Work Unit\\TestSFX\\Footsteps",
        state_groups=["StateGroup:PlayerHealth"],
    )
    assert result is not None
