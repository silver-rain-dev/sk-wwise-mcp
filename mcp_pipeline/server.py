import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.pipeline import (
    import_audio,
    import_tab_delimited,
    set_soundbank_inclusions,
    generate_soundbanks,
    get_soundbank_inclusions as _get_soundbank_inclusions,
    process_definition_files as _process_definition_files,
    save_project as _save_project,
    convert_external_sources as _convert_external_sources,
    get_log as _get_log,
)
from typing import Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name="SK Wwise MCP Pipeline")


@mcp.tool()
def import_audio_files(
    imports: list[dict],
    import_operation: str = "useExisting",
    default: Optional[dict] = None,
    auto_add_to_source_control: bool = True,
) -> dict:
    """Import audio files into the Wwise project. Creates Wwise objects and links audio files to them.

    This function does not return errors for individual import failures — check the Wwise log for details.
    Returns an array of all objects created, replaced, or re-used.

    Args:
        imports:        Array of import commands. Each requires at minimum "objectPath".
                        Each entry can contain:
                          objectPath (required): Path and name of object(s) to create. Supports type prefixes.
                              e.g. "\\\\Actor-Mixer Hierarchy\\\\Default Work Unit\\\\<Random Container>Footsteps\\\\<Sound>Footstep_01"
                          audioFile:        Absolute path to the audio file (must be accessible from Wwise).
                              e.g. "C:/audio/footstep_01.wav"
                          audioFileBase64:  Base64 encoded WAV data with filename, separated by |.
                              e.g. "MySound.wav|UklGRu..."
                          importLanguage:   Language for the import (from project's language list).
                          importLocation:   Object path/GUID used as root for relative paths.
                          originalsSubFolder: Subfolder within Originals to place the file.
                          objectType:       Type of object to create (can also be in objectPath).
                          notes:            Notes field for the created object.
                          event:            Path/name of Event to create for the imported object.
                          switchAssignation: Switch/State assignment for Switch Containers.
                          @PropertyName:    Set any Wwise property, e.g. "@Volume": -6.0

        import_operation: How to handle existing objects. One of:
                          "createNew"       — always create new (unique name if conflict)
                          "useExisting"     — update if exists, create if not (default)
                          "replaceExisting" — destroy existing with same name, create new

        default:        Default values applied to all imports (same fields as import entries).
                        Individual import entries override these defaults.
                        Useful to avoid repeating importLocation, importLanguage, etc.

        auto_add_to_source_control: Auto-add imported files to source control. Default true.

    Examples:
        Simple import:
            imports=[{
                "audioFile": "C:/audio/footstep.wav",
                "objectPath": "\\\\Actor-Mixer Hierarchy\\\\Default Work Unit\\\\<Sound>Footstep"
            }]

        Batch import with defaults:
            default={"importLocation": "\\\\Actor-Mixer Hierarchy\\\\Default Work Unit"},
            imports=[
                {"audioFile": "C:/audio/fs_01.wav", "objectPath": "<Sound>Footstep_01"},
                {"audioFile": "C:/audio/fs_02.wav", "objectPath": "<Sound>Footstep_02"},
            ]

        Import with hierarchy + event creation:
            imports=[{
                "audioFile": "C:/audio/gunshot.wav",
                "objectPath": "\\\\Actor-Mixer Hierarchy\\\\Default Work Unit\\\\<Random Container>Weapons\\\\<Sound>Gunshot",
                "event": "\\\\Events\\\\Default Work Unit\\\\Play_Gunshot",
                "@Volume": -3.0
            }]

    Returns {"objects": [...]} — array of created/updated objects with id, name, type, path."""
    query = {"imports": imports, "importOperation": import_operation}
    if default:
        query["default"] = default
    if not auto_add_to_source_control:
        query["autoAddToSourceControl"] = False
    try:
        return import_audio(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def import_tab_delimited_file(
    import_file: str,
    import_language: str,
    import_operation: str = "useExisting",
    import_location: Optional[str] = None,
    auto_add_to_source_control: bool = True,
    return_fields: list[str] = ["id", "name", "type", "path"],
) -> dict:
    """Import Wwise objects and audio files from a tab-delimited text file.

    Uses the same import processor as the Tab Delimited Import in Wwise's Audio File Importer.
    The file format follows Wwise's tab-delimited specification — see Wwise Help for details.

    Args:
        import_file:      Absolute path to the tab-delimited import file.
                          Must be accessible from Wwise.
                          e.g. "C:/imports/my_import.txt"
        import_language:  Language for the import (from project's language list).
                          e.g. "English(US)", "French", "Japanese"
        import_operation: How to handle existing objects. One of:
                          "createNew"       — always create new (unique name if conflict)
                          "useExisting"     — update if exists, create if not (default)
                          "replaceExisting" — destroy existing with same name, create new
        import_location:  Optional root object path/GUID for relative paths in the file.
                          e.g. "\\Actor-Mixer Hierarchy\\Default Work Unit"
        auto_add_to_source_control: Auto-add imported files to source control. Default true.
        return_fields:    Fields to return for each imported object.
                          Default: ["id", "name", "type", "path"]

    Returns {"objects": [...]} — array of created/updated objects with requested fields."""
    query = {
        "importFile": import_file,
        "importLanguage": import_language,
        "importOperation": import_operation,
    }
    if import_location:
        query["importLocation"] = import_location
    if not auto_add_to_source_control:
        query["autoAddToSourceControl"] = False
    options = {"return": return_fields}
    try:
        return import_tab_delimited(query, options)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def set_wwise_soundbank_inclusions(
    soundbank: str,
    operation: str,
    inclusions: list[dict],
) -> dict:
    """Modify a SoundBank's inclusion list — add, remove, or replace included objects.

    Args:
        soundbank:  The SoundBank to modify. Accepts:
                    - path: "\\SoundBanks\\Default Work Unit\\SFX_Weapons"
                    - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                    - type:name: "SoundBank:SFX_Weapons"
        operation:  How to modify the inclusion list:
                    "add"     — add the inclusions to the existing list
                    "remove"  — remove the inclusions from the existing list
                    "replace" — replace the entire inclusion list
        inclusions: Array of inclusion entries. Each requires:
                    object: path/GUID/type:name of the object to include
                    filter: array of inclusion types — "events", "structures", "media"
                    Example:
                      [{"object": "Event:Play_Gunshot", "filter": ["events", "structures", "media"]},
                       {"object": "\\Events\\Default Work Unit\\Play_Reload", "filter": ["events"]}]"""
    try:
        return set_soundbank_inclusions({
            "soundbank": soundbank,
            "operation": operation,
            "inclusions": inclusions,
        })
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def get_wwise_soundbank_inclusions(
    soundbank: str,
) -> dict:
    """Get a SoundBank's inclusion list — which objects are included and with what filter types.

    Args:
        soundbank: The SoundBank to query. Accepts:
                   - path: "\\SoundBanks\\Default Work Unit\\SFX_Weapons"
                   - GUID: "{aabbcc00-1122-3344-5566-77889900aabb}"
                   - type:name: "SoundBank:SFX_Weapons"

    Returns {"inclusions": [...]} — array of inclusions, each containing:
        object: GUID of the included object
        filter: array of inclusion types — "events", "structures", "media\""""
    try:
        return _get_soundbank_inclusions({"soundbank": soundbank})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def generate_wwise_soundbanks(
    soundbanks: Optional[list[dict]] = None,
    platforms: Optional[list[str]] = None,
    languages: Optional[list[str]] = None,
    skip_languages: bool = False,
    rebuild_soundbanks: bool = False,
    clear_audio_file_cache: bool = False,
    write_to_disk: bool = False,
    rebuild_init_bank: bool = False,
) -> dict:
    """Generate SoundBanks. This is a synchronous operation.

    If no soundbanks are specified, all user-defined SoundBanks are generated.
    Auto-defined SoundBanks are always generated regardless.

    Args:
        soundbanks:             List of SoundBanks to generate. Each requires "name", optionally:
                                  events:     list of event paths/GUIDs/names to include
                                  auxBusses:  list of AuxBus paths/GUIDs/names to include
                                  inclusions: list of inclusion types: "event", "structure", "media"
                                  rebuild:    force rebuild of this specific bank (default false)
                                Example:
                                  [{"name": "SFX_Weapons", "events": ["Event:Play_Gunshot"],
                                    "inclusions": ["event", "structure", "media"]}]
        platforms:              List of platform names/GUIDs to generate for. All if omitted.
        languages:              List of language names/GUIDs to generate. All if omitted.
        skip_languages:         If true, no localized SoundBanks are generated. Default false.
        rebuild_soundbanks:     Force rebuild all SoundBanks. Default false.
        clear_audio_file_cache: Clear the entire audio cache before converting. Default false.
        write_to_disk:          Write SoundBank and info files to disk. Default false.
        rebuild_init_bank:      Force rebuild the Init bank per platform. Default false.

    Returns {"logs": [...]} — array of log entries with severity, time, messageId, message."""
    query = {}
    if soundbanks is not None:
        query["soundbanks"] = soundbanks
    if platforms:
        query["platforms"] = platforms
    if languages:
        query["languages"] = languages
    if skip_languages:
        query["skipLanguages"] = True
    if rebuild_soundbanks:
        query["rebuildSoundBanks"] = True
    if clear_audio_file_cache:
        query["clearAudioFileCache"] = True
    if write_to_disk:
        query["writeToDisk"] = True
    if rebuild_init_bank:
        query["rebuildInitBank"] = True
    try:
        return generate_soundbanks(query)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def process_wwise_soundbank_definitions(
    files: list[str],
) -> dict:
    """Import SoundBank definitions from one or more definition files.

    Check the WAAPI log (get_wwise_log channel "soundbankGenerate") for status messages.

    Args:
        files: Array of absolute paths to SoundBank definition files.
               e.g. ["C:/project/SoundBankDefinitions/SFX.txt",
                      "C:/project/SoundBankDefinitions/Music.txt"]"""
    try:
        return _process_definition_files({"files": files})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def convert_wwise_external_sources(
    sources: list[dict],
) -> dict:
    """Convert external source files for the project as defined in wsources files.

    External Sources are audio data provided at runtime rather than baked into SoundBanks.
    This converts them into the platform-specific format. While SoundBank generation also
    triggers this, this tool can process sources not contained in the Wwise project.

    Args:
        sources: Array of external source entries. Each requires:
                 input:    Path to the .wsources file.
                           e.g. "C:/project/ExternalSources/VO.wsources"
                 platform: Platform name or GUID to convert for.
                           e.g. "Windows", "PS5", "XboxSeriesX"
                 output:   (Optional) Output folder path. Defaults to
                           WwiseProject/.cache/ExternalSources/Platform.

    Example:
        sources=[
            {"input": "C:/project/VO.wsources", "platform": "Windows"},
            {"input": "C:/project/VO.wsources", "platform": "PS5",
             "output": "C:/builds/PS5/ExternalSources"}
        ]"""
    try:
        return _convert_external_sources({"sources": sources})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def save_wwise_project(
    auto_checkout: bool = True,
) -> dict:
    """Save the current Wwise project.

    Args:
        auto_checkout: Automatically checkout affected work units and project file
                       from source control. Default true."""
    try:
        return _save_project(auto_checkout=auto_checkout)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def get_wwise_log(
    channel: str,
) -> dict:
    """Retrieve the latest log entries for a specific Wwise log channel.

    Use this after pipeline operations (import, soundbank generate, conversion) to check for
    errors or warnings. The log is empty when used with WwiseConsole.

    Args:
        channel: The log channel to retrieve. One of:
                 "soundbankGenerate" — SoundBank generation log
                 "conversion"       — audio conversion log
                 "copyPlatformSettings" — platform settings copy log
                 "waapi"            — WAAPI call log
                 "projectLoad"      — project load log
                 "general"          — general Wwise log
                 "sourceControl"    — source control operations log
                 "lua"              — Lua scripting log

    Returns {"items": [...]} — array of log entries, each containing:
        severity:  "Message", "Warning", "Error", or "Fatal Error"
        time:      UTC timestamp (seconds since epoch)
        messageId: message identifier string
        message:   the log message text
        platform:  platform info (if applicable)"""
    try:
        return _get_log({"channel": channel})
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
