import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.query import build_property_reference_query


def test_by_path():
    result = build_property_reference_query(object_path="\\Actor-Mixer Hierarchy\\Default Work Unit\\Footstep")
    assert result["object"] == "\\Actor-Mixer Hierarchy\\Default Work Unit\\Footstep"


def test_by_guid():
    guid = "{aabbcc00-1122-3344-5566-77889900aabb}"
    result = build_property_reference_query(object_guid=guid)
    assert result["object"] == guid


def test_by_name_with_type():
    result = build_property_reference_query(object_name_with_type="Sound:Footstep_Walk")
    assert result["object"] == "Sound:Footstep_Walk"


def test_path_takes_priority():
    result = build_property_reference_query(
        object_path="\\Events\\Play",
        object_guid="{aabb}",
        object_name_with_type="Event:Play",
    )
    assert result["object"] == "\\Events\\Play"


def test_guid_takes_priority_over_name():
    result = build_property_reference_query(
        object_guid="{aabb}",
        object_name_with_type="Event:Play",
    )
    assert result["object"] == "{aabb}"


def test_class_id():
    result = build_property_reference_query(object_path="\\Events\\Play", class_id=12345)
    assert result["classId"] == 12345


def test_class_id_zero():
    result = build_property_reference_query(object_path="\\Events\\Play", class_id=0)
    assert result["classId"] == 0


def test_no_class_id_by_default():
    result = build_property_reference_query(object_path="\\Events\\Play")
    assert "classId" not in result


def test_empty_query():
    result = build_property_reference_query()
    assert result == {}
