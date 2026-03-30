"""Tests for core.pipeline functions not covered by test_core_pipeline.py.

Covers save_project, generate_tab_delimited, and scan_and_import_directory.
"""

import csv
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pipeline import (
    save_project,
    generate_tab_delimited,
    scan_and_import_directory,
)


# --- save_project ---


@patch("core.pipeline.call")
def test_save_project_default(mock_call):
    mock_call.return_value = {}
    save_project()
    mock_call.assert_called_once_with("ak.wwise.core.project.save", {})


@patch("core.pipeline.call")
def test_save_project_no_checkout(mock_call):
    mock_call.return_value = {}
    save_project(auto_checkout=False)
    args = mock_call.call_args[0][1]
    assert args["autoCheckOutToSourceControl"] is False


# --- generate_tab_delimited ---


def test_generate_tab_delimited_basic(tmp_path):
    output = tmp_path / "test.tsv"
    rows = [
        {"audio_file": "C:/sound.wav", "object_path": "\\AM\\Sound"},
        {"audio_file": "C:/sound2.wav", "object_path": "\\AM\\Sound2"},
    ]
    result = generate_tab_delimited(rows, str(output))
    assert result["row_count"] == 2
    assert Path(result["output_path"]).exists()

    # Verify content
    with open(output, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)
        assert "Audio File" in header
        assert "Object Path" in header
        data_rows = list(reader)
        assert len(data_rows) == 2


def test_generate_tab_delimited_empty_rows():
    result = generate_tab_delimited([], "/tmp/test.tsv")
    assert "error" in result


def test_generate_tab_delimited_property_columns(tmp_path):
    output = tmp_path / "test.tsv"
    rows = [{"audio_file": "C:/s.wav", "object_path": "\\AM\\S", "@Volume": "-6"}]
    result = generate_tab_delimited(rows, str(output))
    with open(output, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)
        assert "@Volume" in header


def test_generate_tab_delimited_custom_columns(tmp_path):
    output = tmp_path / "test.tsv"
    rows = [{"audio_file": "C:/s.wav", "object_path": "\\AM\\S"}]
    result = generate_tab_delimited(rows, str(output), columns=["Audio File", "Object Path"])
    with open(output, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)
        assert header == ["Audio File", "Object Path"]


def test_generate_tab_delimited_creates_parent_dirs(tmp_path):
    output = tmp_path / "sub" / "dir" / "test.tsv"
    rows = [{"audio_file": "C:/s.wav"}]
    result = generate_tab_delimited(rows, str(output))
    assert Path(result["output_path"]).exists()


# --- scan_and_import_directory ---


def test_scan_and_import_directory_not_a_dir():
    import pytest
    with pytest.raises(NotADirectoryError):
        scan_and_import_directory("C:/nonexistent/dir", "\\AM\\SFX")


@patch("core.pipeline.import_audio")
@patch("core.pipeline._query_children_with_types")
def test_scan_and_import_directory_no_wavs(mock_children, mock_import, tmp_path):
    # Empty directory
    result = scan_and_import_directory(str(tmp_path), "\\AM\\SFX")
    assert result["matched"] == 0
    assert result["imported"] == 0
    mock_import.assert_not_called()


@patch("core.pipeline.import_audio")
@patch("core.pipeline._query_children_with_types")
def test_scan_and_import_directory_matches(mock_children, mock_import, tmp_path):
    # Create WAV files
    (tmp_path / "Acid.wav").write_bytes(b"RIFF")
    (tmp_path / "Bite.wav").write_bytes(b"RIFF")

    mock_children.return_value = [
        {"name": "Acid", "type": "Sound", "path": "\\AM\\SFX\\Acid"},
        {"name": "Bite", "type": "Sound", "path": "\\AM\\SFX\\Bite"},
    ]
    mock_import.return_value = {"objects": [{"id": "1"}, {"id": "2"}]}

    result = scan_and_import_directory(str(tmp_path), "\\AM\\SFX")
    assert result["matched"] == 2
    assert result["imported"] == 2
    assert len(result["unmatched_files"]) == 0


@patch("core.pipeline.import_audio")
@patch("core.pipeline._query_children_with_types")
def test_scan_and_import_directory_unmatched(mock_children, mock_import, tmp_path):
    (tmp_path / "Unknown.wav").write_bytes(b"RIFF")

    mock_children.return_value = [
        {"name": "Acid", "type": "Sound", "path": "\\AM\\SFX\\Acid"},
    ]
    mock_import.return_value = {"objects": []}

    result = scan_and_import_directory(str(tmp_path), "\\AM\\SFX")
    assert result["matched"] == 0
    assert len(result["unmatched_files"]) == 1
    assert len(result["unmatched_objects"]) == 1


@patch("core.pipeline.import_audio")
@patch("core.pipeline._query_children_with_types")
def test_scan_and_import_directory_with_subfolder(mock_children, mock_import, tmp_path):
    (tmp_path / "Acid.wav").write_bytes(b"RIFF")

    mock_children.return_value = [
        {"name": "Acid", "type": "Sound", "path": "\\AM\\SFX\\Acid"},
    ]
    mock_import.return_value = {"objects": [{"id": "1"}]}

    result = scan_and_import_directory(
        str(tmp_path), "\\AM\\SFX", originals_sub_folder="Attacks"
    )
    assert result["matched"] == 1
    # Verify subfolder was passed in import query
    import_query = mock_import.call_args[0][0]
    assert import_query["default"]["originalsSubFolder"] == "Attacks"
