import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.audio_convert import find_ffmpeg, convert_to_wav


# --- find_ffmpeg ---


@patch("core.audio_convert.shutil.which", return_value="/usr/bin/ffmpeg")
def test_find_ffmpeg_on_path(mock_which):
    assert find_ffmpeg() == "/usr/bin/ffmpeg"


@patch("core.audio_convert.shutil.which", return_value=None)
@patch("core.audio_convert.Path.is_file", return_value=False)
def test_find_ffmpeg_not_found(mock_is_file, mock_which):
    assert find_ffmpeg() is None


# --- convert_to_wav ---


@patch("core.audio_convert.find_ffmpeg", return_value=None)
def test_convert_no_ffmpeg_raises(mock_find):
    with pytest.raises(FileNotFoundError, match="ffmpeg not found"):
        convert_to_wav("/input", "/output")


def test_convert_bad_input_dir_raises(tmp_path):
    with pytest.raises(NotADirectoryError):
        convert_to_wav(str(tmp_path / "nonexistent"), str(tmp_path / "out"), ffmpeg_path="ffmpeg")


@patch("core.audio_convert.subprocess.run")
def test_convert_ogg_to_wav(mock_run, tmp_path):
    # Create fake input files
    (tmp_path / "input").mkdir()
    (tmp_path / "input" / "cry.ogg").write_text("fake")
    (tmp_path / "input" / "already.wav").write_text("fake")
    (tmp_path / "input" / "readme.txt").write_text("fake")

    mock_run.return_value = MagicMock(returncode=0)
    out_dir = str(tmp_path / "output")

    result = convert_to_wav(
        str(tmp_path / "input"), out_dir, ffmpeg_path="ffmpeg"
    )
    assert len(result["converted"]) == 1
    assert result["converted"][0].endswith("cry.wav")
    assert len(result["skipped"]) == 2  # wav + txt
    assert len(result["errors"]) == 0
    mock_run.assert_called_once()


@patch("core.audio_convert.subprocess.run")
def test_convert_ffmpeg_failure(mock_run, tmp_path):
    (tmp_path / "input").mkdir()
    (tmp_path / "input" / "bad.flac").write_text("fake")

    mock_run.return_value = MagicMock(returncode=1, stderr="decode error")

    result = convert_to_wav(
        str(tmp_path / "input"), str(tmp_path / "output"), ffmpeg_path="ffmpeg"
    )
    assert len(result["converted"]) == 0
    assert len(result["errors"]) == 1
    assert "decode error" in result["errors"][0]["error"]
