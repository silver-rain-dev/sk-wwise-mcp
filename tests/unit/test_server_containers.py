import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from waapi import CannotConnectToWaapiException
from mcp_containers.server import (
    set_wwise_attenuation_curve,
    set_wwise_randomizer,
    set_wwise_state_groups,
    set_wwise_state_properties,
    add_wwise_switch_assignments,
    remove_wwise_switch_assignments,
    add_wwise_blend_assignment,
    remove_wwise_blend_assignment,
    set_wwise_game_parameter_range,
)


# --- attenuation curve ---

@patch("mcp_containers.server._set_attenuation_curve")
def test_set_attenuation_curve_success(mock):
    mock.return_value = {}
    result = set_wwise_attenuation_curve(
        object="\\Attenuations\\Att", curve_type="VolumeDryUsage",
        use="Custom", points=[{"x": 0, "y": 0, "shape": "Linear"}],
    )
    assert "error" not in result


@patch("mcp_containers.server._set_attenuation_curve", side_effect=CannotConnectToWaapiException)
def test_set_attenuation_curve_error(mock):
    result = set_wwise_attenuation_curve(
        object="\\test", curve_type="VolumeDryUsage",
        use="Custom", points=[],
    )
    assert "error" in result


# --- randomizer ---

@patch("mcp_containers.server._set_randomizer")
def test_set_randomizer_success(mock):
    mock.return_value = {}
    result = set_wwise_randomizer(object="\\path\\Sound", property="Volume", enabled=True, min=-3.0, max=3.0)
    assert "error" not in result


@patch("mcp_containers.server._set_randomizer", side_effect=CannotConnectToWaapiException)
def test_set_randomizer_error(mock):
    result = set_wwise_randomizer(object="\\test", property="Volume")
    assert "error" in result


# --- state groups ---

@patch("mcp_containers.server._set_state_groups")
def test_set_state_groups_success(mock):
    mock.return_value = {}
    result = set_wwise_state_groups(object="\\path\\Sound", state_groups=["StateGroup:Alive"])
    assert "error" not in result


@patch("mcp_containers.server._set_state_groups", side_effect=CannotConnectToWaapiException)
def test_set_state_groups_error(mock):
    result = set_wwise_state_groups(object="\\test", state_groups=[])
    assert "error" in result


# --- state properties ---

@patch("mcp_containers.server._set_state_properties")
def test_set_state_properties_success(mock):
    mock.return_value = {}
    result = set_wwise_state_properties(object="\\path\\Sound", state_properties=["Volume", "Pitch"])
    assert "error" not in result


@patch("mcp_containers.server._set_state_properties", side_effect=CannotConnectToWaapiException)
def test_set_state_properties_error(mock):
    result = set_wwise_state_properties(object="\\test", state_properties=[])
    assert "error" in result


# --- switch assignment add (batch) ---

@patch("mcp_containers.server._switch_container_add_assignments")
def test_add_switch_assignments_single(mock):
    mock.return_value = [{}]
    result = add_wwise_switch_assignments(
        assignments=[{"child": "\\path\\Child", "state_or_switch": "\\path\\Switch"}]
    )
    assert len(result) == 1
    assert "error" not in result[0]


@patch("mcp_containers.server._switch_container_add_assignments")
def test_add_switch_assignments_multiple(mock):
    mock.return_value = [{}, {}]
    result = add_wwise_switch_assignments(
        assignments=[
            {"child": "\\path\\Child1", "state_or_switch": "\\path\\Switch1"},
            {"child": "\\path\\Child2", "state_or_switch": "\\path\\Switch2"},
        ]
    )
    assert len(result) == 2


@patch("mcp_containers.server._switch_container_add_assignments")
def test_add_switch_assignments_with_container(mock):
    mock.return_value = [{}, {}]
    result = add_wwise_switch_assignments(
        assignments=[
            {"child": "Absorb", "state_or_switch": "Absorb"},
            {"child": "Acid", "state_or_switch": "Acid"},
        ],
        container="\\Actor-Mixer Hierarchy\\Default Work Unit\\SFX\\SFX_Moves",
    )
    assert len(result) == 2
    mock.assert_called_once_with(
        assignments=[
            {"child": "Absorb", "state_or_switch": "Absorb"},
            {"child": "Acid", "state_or_switch": "Acid"},
        ],
        container="\\Actor-Mixer Hierarchy\\Default Work Unit\\SFX\\SFX_Moves",
    )


@patch("mcp_containers.server._switch_container_add_assignments", side_effect=CannotConnectToWaapiException)
def test_add_switch_assignments_error(mock):
    result = add_wwise_switch_assignments(
        assignments=[{"child": "\\test", "state_or_switch": "\\test"}]
    )
    assert "error" in result


# --- switch assignment remove (batch) ---

@patch("mcp_containers.server._switch_container_remove_assignments")
def test_remove_switch_assignments_single(mock):
    mock.return_value = [{}]
    result = remove_wwise_switch_assignments(
        assignments=[{"child": "\\path\\Child", "state_or_switch": "\\path\\Switch"}]
    )
    assert len(result) == 1


@patch("mcp_containers.server._switch_container_remove_assignments", side_effect=CannotConnectToWaapiException)
def test_remove_switch_assignments_error(mock):
    result = remove_wwise_switch_assignments(
        assignments=[{"child": "\\test", "state_or_switch": "\\test"}]
    )
    assert "error" in result


# --- blend assignment add ---

@patch("mcp_containers.server._blend_container_add_assignment")
def test_add_blend_assignment_success(mock):
    mock.return_value = {"child": "{guid}", "index": 0}
    result = add_wwise_blend_assignment(blend_track_guid="{aabb}", child="\\path\\Child")
    assert result["index"] == 0
    mock.assert_called_once_with({"object": "{aabb}", "child": "\\path\\Child"})


@patch("mcp_containers.server._blend_container_add_assignment", side_effect=CannotConnectToWaapiException)
def test_add_blend_assignment_error(mock):
    result = add_wwise_blend_assignment(blend_track_guid="{aabb}", child="\\test")
    assert "error" in result


# --- blend assignment remove ---

@patch("mcp_containers.server._blend_container_remove_assignment")
def test_remove_blend_assignment_success(mock):
    mock.return_value = {}
    result = remove_wwise_blend_assignment(blend_track_guid="{aabb}", child="\\path\\Child")
    mock.assert_called_once_with({"object": "{aabb}", "child": "\\path\\Child"})


@patch("mcp_containers.server._blend_container_remove_assignment", side_effect=CannotConnectToWaapiException)
def test_remove_blend_assignment_error(mock):
    result = remove_wwise_blend_assignment(blend_track_guid="{aabb}", child="\\test")
    assert "error" in result


# --- game parameter range ---

@patch("mcp_containers.server._set_game_parameter_range")
def test_set_game_parameter_range_success(mock):
    mock.return_value = {}
    result = set_wwise_game_parameter_range(
        object="GameParameter:Health", min=0, max=100, on_curve_update="stretch",
    )
    mock.assert_called_once_with({
        "object": "GameParameter:Health", "min": 0, "max": 100, "onCurveUpdate": "stretch",
    })


@patch("mcp_containers.server._set_game_parameter_range", side_effect=CannotConnectToWaapiException)
def test_set_game_parameter_range_error(mock):
    result = set_wwise_game_parameter_range(
        object="GameParameter:Health", min=0, max=100, on_curve_update="stretch",
    )
    assert "error" in result
