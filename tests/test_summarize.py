import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.query import summarize_and_save


MOCK_RESULTS = [
    {"id": "aaa", "name": "Footstep_Walk", "type": "Sound", "path": "\\Containers\\SFX\\Footstep_Walk"},
    {"id": "bbb", "name": "Footstep_Run", "type": "Sound", "path": "\\Containers\\SFX\\Footstep_Run"},
    {"id": "ccc", "name": "SFX", "type": "RandomSequenceContainer", "path": "\\Containers\\SFX"},
    {"id": "ddd", "name": "Play_Footstep", "type": "Event", "path": "\\Events\\Play_Footstep"},
]


def test_total_count(tmp_path):
    result = summarize_and_save(MOCK_RESULTS, output_file=str(tmp_path / "out.json"))
    assert result["total_count"] == 4


def test_type_breakdown(tmp_path):
    result = summarize_and_save(MOCK_RESULTS, output_file=str(tmp_path / "out.json"))
    assert result["types"] == {"Sound": 2, "RandomSequenceContainer": 1, "Event": 1}


def test_preview_limit(tmp_path):
    many_results = [{"id": str(i), "name": f"obj_{i}", "type": "Sound"} for i in range(25)]
    result = summarize_and_save(many_results, output_file=str(tmp_path / "out.json"))
    assert len(result["preview"]) == 10


def test_output_file_written(tmp_path):
    out = tmp_path / "out.json"
    summarize_and_save(MOCK_RESULTS, output_file=str(out))
    assert out.exists()
    data = json.loads(out.read_text())
    assert len(data) == 4


def test_output_file_path_in_result(tmp_path):
    out = tmp_path / "out.json"
    result = summarize_and_save(MOCK_RESULTS, output_file=str(out))
    assert result["output_file"] == str(out.resolve())


def test_empty_results(tmp_path):
    result = summarize_and_save([], output_file=str(tmp_path / "out.json"))
    assert result["total_count"] == 0
    assert result["types"] == {}
    assert result["preview"] == []
