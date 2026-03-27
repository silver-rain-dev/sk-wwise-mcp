import subprocess
import os
from pathlib import Path
from typing import Optional


def _find_wwise_cli() -> str:
    """Find the WwiseConsole executable path."""
    # Common install locations on Windows
    candidates = [
        Path(os.environ.get("WWISEROOT", "")) / "Authoring" / "x64" / "Release" / "bin" / "WwiseConsole.exe",
        Path(os.environ.get("WWISEROOT", "")) / "Authoring" / "arm64" / "Release" / "bin" / "WwiseConsole.exe",
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    # Fallback: assume it's on PATH
    return "WwiseConsole"


def _run_cli(args: list[str], timeout: int = 300) -> dict:
    """Run a WwiseConsole command and return the result."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }
    except FileNotFoundError:
        return {"error": "WwiseConsole not found. Set WWISEROOT environment variable or add WwiseConsole to PATH."}
    except subprocess.TimeoutExpired:
        return {"error": f"WwiseConsole timed out after {timeout} seconds."}


def create_project(project_path: str, platforms: Optional[list[str]] = None) -> dict:
    """Create a new Wwise project using WwiseConsole."""
    cli = _find_wwise_cli()
    args = [cli, "create-new-project", project_path]
    if platforms:
        for platform in platforms:
            args.extend(["--platform", platform])
    return _run_cli(args)


def move_media_ids_to_single_file(project_path: str) -> dict:
    """Move media IDs from work units to a single .mediaid file using WwiseConsole."""
    cli = _find_wwise_cli()
    return _run_cli([cli, "move-media-ids-to-single-file", project_path])


def update_media_ids_in_single_file(project_path: str) -> dict:
    """Update the .mediaid file with current project state using WwiseConsole."""
    cli = _find_wwise_cli()
    return _run_cli([cli, "update-media-ids-in-single-file", project_path])


def move_media_ids_to_work_units(project_path: str) -> dict:
    """Move media IDs from .mediaid file back to work units using WwiseConsole."""
    cli = _find_wwise_cli()
    return _run_cli([cli, "move-media-ids-to-work-units", project_path])


def start_waapi_server(
    project_path: Optional[str] = None,
    wamp_port: Optional[int] = None,
    http_port: Optional[int] = None,
    wamp_max_clients: Optional[int] = None,
    http_max_clients: Optional[int] = None,
    allowed_addr: Optional[str] = None,
    allowed_origin: Optional[str] = None,
    allow_migration: bool = False,
    no_source_control: bool = False,
    watchdog_timeout: Optional[int] = None,
    verbose: bool = False,
    quiet: bool = False,
) -> dict:
    """Start a headless WAAPI server using WwiseConsole."""
    cli = _find_wwise_cli()
    args = [cli, "waapi-server"]
    if project_path:
        args.append(project_path)
    if wamp_port is not None:
        args.extend(["--wamp-port", str(wamp_port)])
    if http_port is not None:
        args.extend(["--http-port", str(http_port)])
    if wamp_max_clients is not None:
        args.extend(["--wamp-max-clients", str(wamp_max_clients)])
    if http_max_clients is not None:
        args.extend(["--http-max-clients", str(http_max_clients)])
    if allowed_addr:
        args.extend(["--allowed-addr", allowed_addr])
    if allowed_origin:
        args.extend(["--allowed-origin", allowed_origin])
    if allow_migration:
        args.append("--allow-migration")
    if no_source_control:
        args.append("--no-source-control")
    if watchdog_timeout is not None:
        args.extend(["--watchdog-timeout", str(watchdog_timeout)])
    if verbose:
        args.append("--verbose")
    if quiet:
        args.append("--quiet")
    # Server runs indefinitely — use Popen instead of run
    try:
        proc = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {
            "success": True,
            "pid": proc.pid,
            "message": f"WAAPI server started (PID: {proc.pid})",
        }
    except FileNotFoundError:
        return {"error": "WwiseConsole not found. Set WWISEROOT environment variable or add WwiseConsole to PATH."}


def verify_project(
    project_path: str,
    abort_on_load_issues: bool = False,
    verbose: bool = False,
    quiet: bool = False,
) -> dict:
    """Verify a Wwise project by loading it without saving using WwiseConsole."""
    cli = _find_wwise_cli()
    args = [cli, "verify", project_path]
    if abort_on_load_issues:
        args.append("--abort-on-load-issues")
    if verbose:
        args.append("--verbose")
    if quiet:
        args.append("--quiet")
    return _run_cli(args)


def migrate_project(
    project_path: str,
    abort_on_load_issues: bool = False,
    no_source_control: bool = False,
    verbose: bool = False,
    quiet: bool = False,
) -> dict:
    """Migrate and save a Wwise project using WwiseConsole."""
    cli = _find_wwise_cli()
    args = [cli, "migrate", project_path]
    if abort_on_load_issues:
        args.append("--abort-on-load-issues")
    if no_source_control:
        args.append("--no-source-control")
    if verbose:
        args.append("--verbose")
    if quiet:
        args.append("--quiet")
    return _run_cli(args)


def convert_external_sources_cli(
    project_path: str,
    platforms: Optional[list[str]] = None,
    source_files: Optional[list[str]] = None,
    source_by_platform: Optional[list[list[str]]] = None,
    output: Optional[str] = None,
    output_by_platform: Optional[list[list[str]]] = None,
    verbose: bool = False,
    quiet: bool = False,
) -> dict:
    """Convert external sources using WwiseConsole."""
    cli = _find_wwise_cli()
    args = [cli, "convert-external-source", project_path]
    if platforms:
        for platform in platforms:
            args.extend(["--platform", platform])
    if source_files:
        args.append("--source-file")
        args.extend(source_files)
    if source_by_platform:
        for platform, file in source_by_platform:
            args.extend(["--source-by-platform", platform, file])
    if output:
        args.extend(["--output", output])
    if output_by_platform:
        for platform, path in output_by_platform:
            args.extend(["--output", platform, path])
    if verbose:
        args.append("--verbose")
    if quiet:
        args.append("--quiet")
    return _run_cli(args)


def tab_delimited_import_cli(
    project_path: str,
    import_file: str,
    operation: Optional[str] = None,
    import_language: Optional[str] = None,
    audio_source_from_original: bool = False,
    continue_on_error: bool = False,
    no_source_control: bool = False,
    custom_global_opening_cmd: Optional[str] = None,
    custom_global_closing_cmd: Optional[str] = None,
    verbose: bool = False,
    quiet: bool = False,
) -> dict:
    """Import a tab-delimited file using WwiseConsole."""
    cli = _find_wwise_cli()
    args = [cli, "tab-delimited-import", project_path, import_file]
    if operation:
        args.extend(["--tab-delimited-operation", operation])
    if import_language:
        args.extend(["--import-language", import_language])
    if audio_source_from_original:
        args.append("--audio-source-from-original")
    if continue_on_error:
        args.append("--continue-on-error")
    if no_source_control:
        args.append("--no-source-control")
    if custom_global_opening_cmd is not None:
        args.extend(["--custom-global-opening-cmd", custom_global_opening_cmd])
    if custom_global_closing_cmd is not None:
        args.extend(["--custom-global-closing-cmd", custom_global_closing_cmd])
    if verbose:
        args.append("--verbose")
    if quiet:
        args.append("--quiet")
    return _run_cli(args)


def generate_soundbanks_cli(
    project_path: str,
    platforms: Optional[list[str]] = None,
    languages: Optional[list[str]] = None,
    soundbanks: Optional[list[str]] = None,
    output: Optional[str] = None,
    clear_audio_file_cache: bool = False,
) -> dict:
    """Generate SoundBanks using WwiseConsole (no WAAPI needed)."""
    cli = _find_wwise_cli()
    args = [cli, "generate-soundbank", project_path]
    if platforms:
        for platform in platforms:
            args.extend(["--platform", platform])
    if languages:
        for language in languages:
            args.extend(["--language", language])
    if soundbanks:
        for bank in soundbanks:
            args.extend(["--soundbank", bank])
    if output:
        args.extend(["--output", output])
    if clear_audio_file_cache:
        args.append("--clear-audio-file-cache")
    return _run_cli(args)
