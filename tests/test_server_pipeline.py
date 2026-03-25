import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from waapi import CannotConnectToWaapiException
from mcp_pipeline.server import (
    import_audio_files,
    import_tab_delimited_file,
    set_wwise_soundbank_inclusions,
    get_wwise_soundbank_inclusions,
    generate_wwise_soundbanks,
    process_wwise_soundbank_definitions,
    convert_wwise_external_sources,
    get_wwise_log,
)


# --- import audio ---

@patch("mcp_pipeline.server.import_audio")
def test_import_audio_files_success(mock):
    mock.return_value = {"objects": [{"id": "a", "name": "Sound1"}]}
    result = import_audio_files(imports=[{"objectPath": "\\path\\Sound", "audioFile": "C:/a.wav"}])
    assert len(result["objects"]) == 1


@patch("mcp_pipeline.server.import_audio", side_effect=CannotConnectToWaapiException)
def test_import_audio_files_error(mock):
    result = import_audio_files(imports=[{"objectPath": "\\test"}])
    assert "error" in result


# --- import tab delimited ---

@patch("mcp_pipeline.server.import_tab_delimited")
def test_import_tab_delimited_success(mock):
    mock.return_value = {"objects": []}
    result = import_tab_delimited_file(
        import_file="C:/file.tsv", import_language="English(US)",
    )
    assert "objects" in result


@patch("mcp_pipeline.server.import_tab_delimited", side_effect=CannotConnectToWaapiException)
def test_import_tab_delimited_error(mock):
    result = import_tab_delimited_file(import_file="C:/file.tsv", import_language="English(US)")
    assert "error" in result


# --- set soundbank inclusions ---

@patch("mcp_pipeline.server.set_soundbank_inclusions")
def test_set_soundbank_inclusions_success(mock):
    mock.return_value = {}
    result = set_wwise_soundbank_inclusions(
        soundbank="SoundBank:MyBank", operation="add",
        inclusions=[{"object": "Event:Play", "filter": ["events"]}],
    )
    assert "error" not in result


@patch("mcp_pipeline.server.set_soundbank_inclusions", side_effect=CannotConnectToWaapiException)
def test_set_soundbank_inclusions_error(mock):
    result = set_wwise_soundbank_inclusions(
        soundbank="SoundBank:MyBank", operation="add", inclusions=[],
    )
    assert "error" in result


# --- get soundbank inclusions ---

@patch("mcp_pipeline.server._get_soundbank_inclusions")
def test_get_soundbank_inclusions_success(mock):
    mock.return_value = {"inclusions": [{"object": "{guid}", "filter": ["events"]}]}
    result = get_wwise_soundbank_inclusions(soundbank="SoundBank:MyBank")
    assert len(result["inclusions"]) == 1


@patch("mcp_pipeline.server._get_soundbank_inclusions", side_effect=CannotConnectToWaapiException)
def test_get_soundbank_inclusions_error(mock):
    result = get_wwise_soundbank_inclusions(soundbank="SoundBank:MyBank")
    assert "error" in result


# --- generate soundbanks ---

@patch("mcp_pipeline.server.generate_soundbanks")
def test_generate_soundbanks_success(mock):
    mock.return_value = {"logs": []}
    result = generate_wwise_soundbanks(soundbanks=[{"name": "MyBank"}], write_to_disk=True)
    assert result["logs"] == []


@patch("mcp_pipeline.server.generate_soundbanks")
def test_generate_soundbanks_all(mock):
    mock.return_value = {"logs": []}
    result = generate_wwise_soundbanks()
    mock.assert_called_once_with({})


@patch("mcp_pipeline.server.generate_soundbanks", side_effect=CannotConnectToWaapiException)
def test_generate_soundbanks_error(mock):
    result = generate_wwise_soundbanks()
    assert "error" in result


# --- process definition files ---

@patch("mcp_pipeline.server._process_definition_files")
def test_process_definition_files_success(mock):
    mock.return_value = {}
    result = process_wwise_soundbank_definitions(files=["C:/defs.txt"])
    mock.assert_called_once_with({"files": ["C:/defs.txt"]})


@patch("mcp_pipeline.server._process_definition_files", side_effect=CannotConnectToWaapiException)
def test_process_definition_files_error(mock):
    result = process_wwise_soundbank_definitions(files=["C:/defs.txt"])
    assert "error" in result


# --- convert external sources ---

@patch("mcp_pipeline.server._convert_external_sources")
def test_convert_external_sources_success(mock):
    mock.return_value = {}
    result = convert_wwise_external_sources(
        sources=[{"input": "C:/VO.wsources", "platform": "Windows"}],
    )
    assert "error" not in result


@patch("mcp_pipeline.server._convert_external_sources", side_effect=CannotConnectToWaapiException)
def test_convert_external_sources_error(mock):
    result = convert_wwise_external_sources(sources=[])
    assert "error" in result


# --- get log ---

@patch("mcp_pipeline.server._get_log")
def test_get_log_success(mock):
    mock.return_value = {"items": [{"severity": "Message", "message": "Done"}]}
    result = get_wwise_log(channel="soundbankGenerate")
    assert result["items"][0]["severity"] == "Message"


@patch("mcp_pipeline.server._get_log", side_effect=CannotConnectToWaapiException)
def test_get_log_error(mock):
    result = get_wwise_log(channel="general")
    assert "error" in result
