import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_command_line.server import (
    cli_create_new_project,
    cli_move_media_ids,
    cli_move_media_ids_to_work_units,
    cli_update_media_ids,
    cli_start_waapi_server,
    cli_verify_project,
    cli_migrate_project,
    cli_tab_delimited_import,
    cli_convert_external_sources,
)


# --- create project ---

@patch("mcp_command_line.server.create_project")
def test_create_project_default(mock):
    mock.return_value = {"returncode": 0, "stdout": "", "stderr": "", "success": True}
    result = cli_create_new_project(project_path="C:/Test/Test.wproj")
    assert result["success"]
    mock.assert_called_once_with(project_path="C:/Test/Test.wproj", platforms=None)


@patch("mcp_command_line.server.create_project")
def test_create_project_with_platforms(mock):
    mock.return_value = {"returncode": 0, "stdout": "", "stderr": "", "success": True}
    result = cli_create_new_project(project_path="C:/Test/Test.wproj", platforms=["Windows", "PS5"])
    mock.assert_called_once_with(project_path="C:/Test/Test.wproj", platforms=["Windows", "PS5"])


# --- move media ids ---

@patch("mcp_command_line.server.move_media_ids_to_single_file")
def test_move_media_ids(mock):
    mock.return_value = {"returncode": 0, "success": True}
    result = cli_move_media_ids(project_path="C:/Test/Test.wproj")
    assert result["success"]


@patch("mcp_command_line.server.move_media_ids_to_work_units")
def test_move_media_ids_to_work_units(mock):
    mock.return_value = {"returncode": 0, "success": True}
    result = cli_move_media_ids_to_work_units(project_path="C:/Test/Test.wproj")
    assert result["success"]


# --- update media ids ---

@patch("mcp_command_line.server.update_media_ids_in_single_file")
def test_update_media_ids(mock):
    mock.return_value = {"returncode": 0, "success": True}
    result = cli_update_media_ids(project_path="C:/Test/Test.wproj")
    assert result["success"]


# --- waapi server ---

@patch("mcp_command_line.server.start_waapi_server")
def test_start_waapi_server(mock):
    mock.return_value = {"success": True, "pid": 1234}
    result = cli_start_waapi_server(project_path="C:/Test/Test.wproj")
    assert result["pid"] == 1234


@patch("mcp_command_line.server.start_waapi_server")
def test_start_waapi_server_no_project(mock):
    mock.return_value = {"success": True, "pid": 5678}
    result = cli_start_waapi_server()
    mock.assert_called_once_with(
        project_path=None, wamp_port=None, http_port=None,
        allow_migration=False, verbose=False,
    )


# --- verify ---

@patch("mcp_command_line.server.verify_project")
def test_verify_project(mock):
    mock.return_value = {"returncode": 0, "success": True}
    result = cli_verify_project(project_path="C:/Test/Test.wproj")
    assert result["success"]


@patch("mcp_command_line.server.verify_project")
def test_verify_project_abort_on_issues(mock):
    mock.return_value = {"returncode": 1, "success": False}
    result = cli_verify_project(project_path="C:/Test/Test.wproj", abort_on_load_issues=True)
    assert not result["success"]


# --- migrate ---

@patch("mcp_command_line.server.migrate_project")
def test_migrate_project(mock):
    mock.return_value = {"returncode": 0, "success": True}
    result = cli_migrate_project(project_path="C:/Test/Test.wproj")
    assert result["success"]


# --- tab delimited import ---

@patch("mcp_command_line.server.tab_delimited_import_cli")
def test_tab_delimited_import(mock):
    mock.return_value = {"returncode": 0, "success": True}
    result = cli_tab_delimited_import(
        project_path="C:/Test/Test.wproj", import_file="C:/import.tsv",
    )
    assert result["success"]


@patch("mcp_command_line.server.tab_delimited_import_cli")
def test_tab_delimited_import_with_options(mock):
    mock.return_value = {"returncode": 0, "success": True}
    result = cli_tab_delimited_import(
        project_path="C:/Test/Test.wproj", import_file="C:/import.tsv",
        operation="createNew", import_language="French", continue_on_error=True,
    )
    mock.assert_called_once_with(
        project_path="C:/Test/Test.wproj", import_file="C:/import.tsv",
        operation="createNew", import_language="French",
        audio_source_from_original=False, continue_on_error=True,
        no_source_control=False, verbose=False,
    )


# --- convert external sources ---

@patch("mcp_command_line.server.convert_external_sources_cli")
def test_convert_external_sources(mock):
    mock.return_value = {"returncode": 0, "success": True}
    result = cli_convert_external_sources(
        project_path="C:/Test/Test.wproj",
        platforms=["Windows"],
        source_files=["C:/VO.wsources"],
    )
    assert result["success"]
