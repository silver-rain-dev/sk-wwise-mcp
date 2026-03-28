import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.wwise_cli import (
    create_project,
    move_media_ids_to_single_file,
    update_media_ids_in_single_file,
    move_media_ids_to_work_units,
    start_waapi_server,
    verify_project,
    migrate_project,
    tab_delimited_import_cli,
    convert_external_sources_cli,
    generate_soundbanks_cli,
)
from typing import Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name="SK Wwise MCP Command Line")


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def cli_create_new_project(
    project_path: str,
    platforms: Optional[list[str]] = None,
):
    """Create a blank new Wwise project using WwiseConsole CLI. Does NOT require WAAPI or Wwise to be running.

    The project must not already exist. If the directory does not exist, it is created.

    Args:
        project_path: Absolute path to the .wproj file to create.
                      e.g. "C:/MyProject/MyProject.wproj"
        platforms:    List of platforms the project supports.
                      e.g. ["Windows", "Linux", "PS5", "XboxSeriesX"]
                      Default: Windows only if omitted.

    Returns:
        returncode: 0 = success, 1 = errors occurred, 2 = only warnings
        stdout/stderr: console output"""
    return create_project(project_path=project_path, platforms=platforms)


@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": False})
def cli_move_media_ids(
    project_path: str,
):
    """Move media IDs from work units (.wwu) to a single <project-name>.mediaid file.
    Does NOT require WAAPI or Wwise to be running. Forces a save of all work units.

    Args:
        project_path: Absolute path to the .wproj file.
                      e.g. "C:/MyProject/MyProject.wproj"

    Returns:
        returncode: 0 = success, 1 = errors occurred, 2 = only warnings
        stdout/stderr: console output"""
    return move_media_ids_to_single_file(project_path=project_path)


@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": False})
def cli_move_media_ids_to_work_units(
    project_path: str,
):
    """Move media IDs from the <project-name>.mediaid file back into individual work units (.wwu).
    Does NOT require WAAPI or Wwise to be running. Forces a save of all work units.

    This is the reverse of cli_move_media_ids.

    Args:
        project_path: Absolute path to the .wproj file.
                      e.g. "C:/MyProject/MyProject.wproj"

    Returns:
        returncode: 0 = success, 1 = errors occurred, 2 = only warnings
        stdout/stderr: console output"""
    return move_media_ids_to_work_units(project_path=project_path)


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def cli_update_media_ids(
    project_path: str,
):
    """Update the <project-name>.mediaid file with the current project state.
    Does NOT require WAAPI or Wwise to be running. Only works if the .mediaid file already exists.

    Use this after making changes to keep the .mediaid file in sync with the project.

    Args:
        project_path: Absolute path to the .wproj file.
                      e.g. "C:/MyProject/MyProject.wproj"

    Returns:
        returncode: 0 = success, 1 = errors occurred, 2 = only warnings
        stdout/stderr: console output"""
    return update_media_ids_in_single_file(project_path=project_path)


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": True})
def cli_start_waapi_server(
    project_path: Optional[str] = None,
    wamp_port: Optional[int] = None,
    http_port: Optional[int] = None,
    allow_migration: bool = False,
    verbose: bool = False,
):
    """Start a headless WAAPI server using WwiseConsole CLI. Does NOT require Wwise UI.

    Once running, other MCP servers can connect to it via WAAPI for headless automation and CI/CD.
    The server runs in the background and must be stopped manually (kill the process).

    Args:
        project_path:    Optional path to .wproj to load on startup.
                         If omitted, no project is loaded — use WAAPI to open one later.
        wamp_port:       WAMP port number (0-65535). Default 8080.
        http_port:       HTTP POST port number (0-65535). Default 8090.
        allow_migration: Allow migration and save if the project needs it. Default false.
        verbose:         Enable extra console output. Default false.

    Returns:
        pid: process ID of the WAAPI server (use to stop it later)"""
    result = start_waapi_server(
        project_path=project_path,
        wamp_port=wamp_port,
        http_port=http_port,
        allow_migration=allow_migration,
        verbose=verbose,
    )
    # Write a lockfile so other MCP servers can auto-restart if the server dies
    if result.get("success") and project_path:
        from core.waapi_util import write_server_lockfile
        write_server_lockfile(pid=result["pid"], project_path=project_path)
    return result


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def cli_verify_project(
    project_path: str,
    abort_on_load_issues: bool = False,
    verbose: bool = False,
):
    """Verify a Wwise project by loading it without saving. Does NOT require WAAPI or Wwise to be running.

    Useful to check for load issues, warnings, or errors without modifying the project.

    Args:
        project_path:         Absolute path to the .wproj file.
                              e.g. "C:/MyProject/MyProject.wproj"
        abort_on_load_issues: If true, abort if any load issues are detected.
                              All issues are printed to output. Default false.
        verbose:              Enable extra console output. Default false.

    Returns:
        returncode: 0 = success, 1 = errors occurred, 2 = only warnings
        stdout/stderr: console output"""
    return verify_project(
        project_path=project_path,
        abort_on_load_issues=abort_on_load_issues,
        verbose=verbose,
    )


@mcp.tool(annotations={"destructiveHint": True, "openWorldHint": False})
def cli_migrate_project(
    project_path: str,
    abort_on_load_issues: bool = False,
    no_source_control: bool = False,
    verbose: bool = False,
):
    """Migrate and save a Wwise project to the current version using WwiseConsole CLI.
    Does NOT require WAAPI or Wwise to be running.

    Use this when opening a project created with an older Wwise version.

    Args:
        project_path:         Absolute path to the .wproj file.
                              e.g. "C:/MyProject/MyProject.wproj"
        abort_on_load_issues: If true, abort migration if any project load issues are detected.
                              All issues are printed to output. Default false.
        no_source_control:    Skip automatic checkout of migrated files from source control.
                              Default false.
        verbose:              Enable extra console output. Default false.

    Returns:
        returncode: 0 = success, 1 = errors occurred, 2 = only warnings
        stdout/stderr: console output"""
    return migrate_project(
        project_path=project_path,
        abort_on_load_issues=abort_on_load_issues,
        no_source_control=no_source_control,
        verbose=verbose,
    )


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def cli_tab_delimited_import(
    project_path: str,
    import_file: str,
    operation: str = "useExisting",
    import_language: Optional[str] = None,
    audio_source_from_original: bool = False,
    continue_on_error: bool = False,
    no_source_control: bool = False,
    verbose: bool = False,
):
    """Import a tab-delimited file to create and modify object hierarchies using WwiseConsole CLI.
    Does NOT require WAAPI or Wwise to be running.

    The project is automatically migrated (if required) and saved after import.

    Args:
        project_path:              Absolute path to the .wproj file.
                                   e.g. "C:/MyProject/MyProject.wproj"
        import_file:               Absolute path to the tab-delimited file to import.
                                   e.g. "C:/imports/my_import.tsv"
        operation:                 How to handle existing objects:
                                   "createNew"       — always create new (unique name if conflict)
                                   "useExisting"     — update if exists, create if not (default)
                                   "replaceExisting" — destroy existing with same name, create new
        import_language:           Language for voice imports. e.g. "English(US)"
                                   Only audio files are added; other operations are ignored.
        audio_source_from_original: If true, reuse existing audio sources with the same name
                                   instead of replacing them. Default false.
        continue_on_error:         Continue importing even if an error occurs. Default false.
        no_source_control:         Skip automatic source control add/checkout. Default false.
        verbose:                   Enable extra console output. Default false.

    Returns:
        returncode: 0 = success, 1 = errors occurred, 2 = only warnings
        stdout/stderr: console output"""
    return tab_delimited_import_cli(
        project_path=project_path,
        import_file=import_file,
        operation=operation,
        import_language=import_language,
        audio_source_from_original=audio_source_from_original,
        continue_on_error=continue_on_error,
        no_source_control=no_source_control,
        verbose=verbose,
    )


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def cli_convert_external_sources(
    project_path: str,
    platforms: Optional[list[str]] = None,
    source_files: Optional[list[str]] = None,
    source_by_platform: Optional[list[list[str]]] = None,
    output: Optional[str] = None,
    output_by_platform: Optional[list[list[str]]] = None,
    verbose: bool = False,
):
    """Convert external sources using WwiseConsole CLI. Does NOT require WAAPI or Wwise to be running.

    External Sources are audio data provided at runtime rather than baked into SoundBanks.
    This converts them using the project's conversion settings.

    Args:
        project_path:       Absolute path to the .wproj file.
                            e.g. "C:/MyProject/MyProject.wproj"
        platforms:          List of platform names to convert for. All if omitted.
                            e.g. ["Windows", "PS5"]
        source_files:       List of .wsources file paths to use for all platforms.
                            e.g. ["C:/project/VO.wsources"]
        source_by_platform: List of [platform, wsources_file] pairs. Overrides project
                            settings for that platform.
                            e.g. [["Windows", "C:/project/VO_Win.wsources"],
                                  ["PS5", "C:/project/VO_PS5.wsources"]]
        output:             Single output directory for all platforms.
                            Default: WwiseProject/.cache/ExternalSources/Platform
        output_by_platform: List of [platform, output_path] pairs for per-platform output.
                            e.g. [["Windows", "C:/builds/Win/ExternalSources"],
                                  ["PS5", "C:/builds/PS5/ExternalSources"]]
        verbose:            Enable extra console output. Default false.

    Returns:
        returncode: 0 = success, 1 = errors occurred, 2 = only warnings
        stdout/stderr: console output"""
    return convert_external_sources_cli(
        project_path=project_path,
        platforms=platforms,
        source_files=source_files,
        source_by_platform=source_by_platform,
        output=output,
        output_by_platform=output_by_platform,
        verbose=verbose,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
