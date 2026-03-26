import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.wwise_cli import (
    _run_cli,
    create_project,
    move_media_ids_to_single_file,
    update_media_ids_in_single_file,
    move_media_ids_to_work_units,
    verify_project,
    migrate_project,
    tab_delimited_import_cli,
    convert_external_sources_cli,
    generate_soundbanks_cli,
    start_waapi_server,
)


# --- _run_cli ---

@patch("core.wwise_cli.subprocess.run")
def test_run_cli_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")
    result = _run_cli(["echo", "test"])
    assert result["success"]
    assert result["returncode"] == 0


@patch("core.wwise_cli.subprocess.run")
def test_run_cli_failure(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error")
    result = _run_cli(["bad_cmd"])
    assert not result["success"]
    assert result["stderr"] == "Error"


@patch("core.wwise_cli.subprocess.run", side_effect=FileNotFoundError)
def test_run_cli_not_found(mock_run):
    result = _run_cli(["nonexistent"])
    assert "error" in result
    assert "not found" in result["error"]


@patch("core.wwise_cli.subprocess.run", side_effect=__import__("subprocess").TimeoutExpired("cmd", 5))
def test_run_cli_timeout(mock_run):
    result = _run_cli(["slow_cmd"], timeout=5)
    assert "error" in result
    assert "timed out" in result["error"]


# --- create_project ---

@patch("core.wwise_cli._run_cli")
@patch("core.wwise_cli._find_wwise_cli", return_value="WwiseConsole")
def test_create_project_default(mock_find, mock_run):
    mock_run.return_value = {"success": True}
    create_project("C:/Test.wproj")
    mock_run.assert_called_once_with(["WwiseConsole", "create-new-project", "C:/Test.wproj"])


@patch("core.wwise_cli._run_cli")
@patch("core.wwise_cli._find_wwise_cli", return_value="WwiseConsole")
def test_create_project_platforms(mock_find, mock_run):
    mock_run.return_value = {"success": True}
    create_project("C:/Test.wproj", platforms=["Windows", "PS5"])
    mock_run.assert_called_once_with([
        "WwiseConsole", "create-new-project", "C:/Test.wproj",
        "--platform", "Windows", "--platform", "PS5",
    ])


# --- move/update media ids ---

@patch("core.wwise_cli._run_cli")
@patch("core.wwise_cli._find_wwise_cli", return_value="WwiseConsole")
def test_move_media_ids_to_single_file(mock_find, mock_run):
    mock_run.return_value = {"success": True}
    move_media_ids_to_single_file("C:/Test.wproj")
    mock_run.assert_called_once_with(["WwiseConsole", "move-media-ids-to-single-file", "C:/Test.wproj"])


@patch("core.wwise_cli._run_cli")
@patch("core.wwise_cli._find_wwise_cli", return_value="WwiseConsole")
def test_update_media_ids(mock_find, mock_run):
    mock_run.return_value = {"success": True}
    update_media_ids_in_single_file("C:/Test.wproj")
    mock_run.assert_called_once_with(["WwiseConsole", "update-media-ids-in-single-file", "C:/Test.wproj"])


@patch("core.wwise_cli._run_cli")
@patch("core.wwise_cli._find_wwise_cli", return_value="WwiseConsole")
def test_move_media_ids_to_work_units(mock_find, mock_run):
    mock_run.return_value = {"success": True}
    move_media_ids_to_work_units("C:/Test.wproj")
    mock_run.assert_called_once_with(["WwiseConsole", "move-media-ids-to-work-units", "C:/Test.wproj"])


# --- verify ---

@patch("core.wwise_cli._run_cli")
@patch("core.wwise_cli._find_wwise_cli", return_value="WwiseConsole")
def test_verify_project(mock_find, mock_run):
    mock_run.return_value = {"success": True}
    verify_project("C:/Test.wproj", verbose=True)
    mock_run.assert_called_once_with(["WwiseConsole", "verify", "C:/Test.wproj", "--verbose"])


# --- migrate ---

@patch("core.wwise_cli._run_cli")
@patch("core.wwise_cli._find_wwise_cli", return_value="WwiseConsole")
def test_migrate_project(mock_find, mock_run):
    mock_run.return_value = {"success": True}
    migrate_project("C:/Test.wproj", no_source_control=True)
    mock_run.assert_called_once_with([
        "WwiseConsole", "migrate", "C:/Test.wproj", "--no-source-control",
    ])


# --- tab delimited import ---

@patch("core.wwise_cli._run_cli")
@patch("core.wwise_cli._find_wwise_cli", return_value="WwiseConsole")
def test_tab_delimited_import(mock_find, mock_run):
    mock_run.return_value = {"success": True}
    tab_delimited_import_cli("C:/Test.wproj", "C:/import.tsv", operation="createNew")
    mock_run.assert_called_once_with([
        "WwiseConsole", "tab-delimited-import", "C:/Test.wproj", "C:/import.tsv",
        "--tab-delimited-operation", "createNew",
    ])


# --- generate soundbanks ---

@patch("core.wwise_cli._run_cli")
@patch("core.wwise_cli._find_wwise_cli", return_value="WwiseConsole")
def test_generate_soundbanks_cli(mock_find, mock_run):
    mock_run.return_value = {"success": True}
    generate_soundbanks_cli("C:/Test.wproj", platforms=["Windows"], soundbanks=["MyBank"])
    mock_run.assert_called_once_with([
        "WwiseConsole", "generate-soundbank", "C:/Test.wproj",
        "--platform", "Windows", "--soundbank", "MyBank",
    ])


# --- waapi server ---

@patch("core.wwise_cli.subprocess.Popen")
@patch("core.wwise_cli._find_wwise_cli", return_value="WwiseConsole")
def test_start_waapi_server(mock_find, mock_popen):
    mock_proc = MagicMock()
    mock_proc.pid = 9999
    mock_popen.return_value = mock_proc
    result = start_waapi_server("C:/Test.wproj", wamp_port=8085)
    assert result["pid"] == 9999
    assert result["success"]
