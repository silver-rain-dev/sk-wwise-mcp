import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.pipeline import (
    import_audio,
    import_tab_delimited,
    scan_and_import_directory as _scan_and_import_directory,
    set_soundbank_inclusions,
    generate_soundbanks,
    get_soundbank_inclusions as _get_soundbank_inclusions,
    process_definition_files as _process_definition_files,
    save_project as _save_project,
    convert_external_sources as _convert_external_sources,
    get_log as _get_log,
    generate_tab_delimited as _generate_tab_delimited,
)
from core.audio_convert import convert_to_wav as _convert_to_wav
from typing import Optional
from waapi import CannotConnectToWaapiException

mcp = FastMCP(name="SK Wwise MCP Pipeline")


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def import_audio_files(
    imports: list[dict],
    import_operation: str = "useExisting",
    default: Optional[dict] = None,
    auto_add_to_source_control: bool = True,
):
    """Import audio files into the Wwise project. Creates Wwise objects and links audio files to them.

    This function does not return errors for individual import failures — check the Wwise log for details.
    Returns an array of all objects created, replaced, or re-used.

    IMPORTANT — Audio file format:
        WAV files are imported directly. Non-WAV formats (OGG, FLAC, MP3, AAC, AIFF, M4A, WMA)
        are auto-converted to WAV via ffmpeg if available. If ffmpeg is not installed, the import
        returns an error with install instructions. Unsupported formats are rejected.

    IMPORTANT — SFX vs Voice:
        The importLanguage field determines where audio is stored and how Sound objects are typed:
          "SFX"           → Originals/SFX/, creates Sound SFX objects. Use for all non-voiced audio
                            (music, SFX, ambience, jingles, etc.)
          "<language>"    → Originals/Voices/<language>/, creates Sound Voice objects. Use for
                            localized dialogue/VO (e.g. "English(US)", "Japanese")
        Use <Sound SFX> or <Sound Voice> type prefixes in objectPath to match.
        Set importLanguage in the "default" dict to avoid repeating it per entry.

    Args:
        imports:        Array of import commands. Each requires at minimum "objectPath".
                        Each entry can contain:
                          objectPath (required): Path and name of object(s) to create. Supports type prefixes.
                              Use <Sound SFX> for non-voiced audio, <Sound Voice> for localized VO.
                              e.g. "\\\\Actor-Mixer Hierarchy\\\\Default Work Unit\\\\<Random Container>Footsteps\\\\<Sound SFX>Footstep_01"
                          audioFile:        Absolute path to the audio file. MUST be WAV format.
                              e.g. "C:/audio/footstep_01.wav"
                          audioFileBase64:  Base64 encoded WAV data with filename, separated by |.
                              e.g. "MySound.wav|UklGRu..."
                          importLanguage:   "SFX" for sound effects/music, or a language name for VO.
                              e.g. "SFX", "English(US)", "Japanese"
                          importLocation:   Object path/GUID used as root for relative paths.
                          originalsSubFolder: Subfolder within Originals/SFX/ or Originals/Voices/<lang>/
                              to organize files. e.g. "Music", "Cries", "Weapons"
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
        Import SFX (non-voiced audio):
            default={"importLanguage": "SFX"},
            imports=[{
                "audioFile": "C:/audio/footstep.wav",
                "objectPath": "\\\\Actor-Mixer Hierarchy\\\\Default Work Unit\\\\<Sound SFX>Footstep"
            }]

        Import with subfolder organization:
            default={"importLanguage": "SFX"},
            imports=[
                {"audioFile": "C:/audio/fs_01.wav",
                 "objectPath": "\\\\Actor-Mixer Hierarchy\\\\Default Work Unit\\\\<Sound SFX>Footstep_01",
                 "originalsSubFolder": "Footsteps"},
                {"audioFile": "C:/audio/fs_02.wav",
                 "objectPath": "\\\\Actor-Mixer Hierarchy\\\\Default Work Unit\\\\<Sound SFX>Footstep_02",
                 "originalsSubFolder": "Footsteps"},
            ]

        Import voice/dialogue (localized):
            default={"importLanguage": "English(US)"},
            imports=[{
                "audioFile": "C:/vo/greeting_EN.wav",
                "objectPath": "\\\\Actor-Mixer Hierarchy\\\\Default Work Unit\\\\<Sound Voice>Greeting"
            }]

        Import with hierarchy + event creation:
            default={"importLanguage": "SFX"},
            imports=[{
                "audioFile": "C:/audio/gunshot.wav",
                "objectPath": "\\\\Actor-Mixer Hierarchy\\\\Default Work Unit\\\\<Random Container>Weapons\\\\<Sound SFX>Gunshot",
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
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        return {"error": str(e)}
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}
    except TimeoutError as e:
        return {"error": f"Import timed out: {e}. The import may still be running in Wwise — check the Wwise log."}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def import_tab_delimited_file(
    import_file: str,
    import_language: str,
    import_operation: str = "useExisting",
    import_location: Optional[str] = None,
    auto_add_to_source_control: bool = True,
    return_fields: list[str] = ["id", "name", "type", "path"],
):
    """Import Wwise objects and audio files from a tab-delimited text file.

    Uses the same import processor as the Tab Delimited Import in Wwise's Audio File Importer.
    The file format follows Wwise's tab-delimited specification — see Wwise Help for details.

    IMPORTANT — Audio file format:
        Only WAV files create proper AudioFileSource links. Other formats (OGG, FLAC, MP3)
        get copied to Originals but are NOT linked to the Sound object. Convert to WAV first.

    IMPORTANT — SFX vs Voice:
        import_language determines where audio is stored and how Sounds are typed:
          "SFX"           → Originals/SFX/, creates Sound SFX objects (music, SFX, ambience)
          "<language>"    → Originals/Voices/<language>/, creates Sound Voice objects (dialogue/VO)

    Args:
        import_file:      Absolute path to the tab-delimited import file.
                          Must be accessible from Wwise.
                          e.g. "C:/imports/my_import.txt"
        import_language:  "SFX" for non-voiced audio (music, SFX, ambience, jingles), or
                          a language name for localized VO (e.g. "English(US)", "Japanese").
        import_operation: How to handle existing objects. One of:
                          "createNew"       — always create new (unique name if conflict)
                          "useExisting"     — update if exists, create if not (default)
                          "replaceExisting" — destroy existing with same name, create new
        import_location:  Optional root object path/GUID for relative paths in the file.
                          e.g. "\\Containers\\Default Work Unit"
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


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def import_audio_directory(
    directory: str,
    import_location: str,
    import_language: str = "SFX",
    import_operation: str = "useExisting",
    originals_sub_folder: Optional[str] = None,
):
    """Scan a directory of WAV files and auto-import by matching filenames to existing Wwise objects.

    Queries the children of import_location and matches each WAV file by name:
      - Sound objects: exact filename match (e.g. Acid.wav matches child "Acid")
      - RandomSequenceContainer: matches by base name after stripping trailing digits
        (e.g. Absorb.wav, Absorb1.wav, Absorb2.wav all match RSC "Absorb" and are
        imported as child Sounds underneath it)

    This is the most token-efficient import method — a single call replaces hundreds
    of per-file import entries. Use for bulk imports where WAV filenames correspond
    to existing Wwise object names.

    Args:
        directory:           Absolute path to directory containing WAV files.
        import_location:     Wwise parent object whose children to match against.
                             Accepts path or GUID.
                             e.g. "\\\\Actor-Mixer Hierarchy\\\\Default Work Unit\\\\SFX\\\\SFX_Moves"
        import_language:     "SFX" (default) or a language name for localized VO.
        import_operation:    "useExisting" (default), "createNew", or "replaceExisting".
        originals_sub_folder: Optional subfolder within Originals/SFX/ to organize files.

    Returns dict with:
        matched:            Number of WAV files matched to Wwise objects.
        imported:           Number of objects created/updated in Wwise.
        unmatched_files:    WAV files with no matching Wwise object.
        unmatched_objects:  Wwise objects with no matching WAV file.
        objects:            Array of created/updated Wwise objects.
    """
    try:
        return _scan_and_import_directory(
            directory=directory,
            import_location=import_location,
            import_language=import_language,
            import_operation=import_operation,
            originals_sub_folder=originals_sub_folder,
        )
    except NotADirectoryError as e:
        return {"error": str(e)}
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def set_wwise_soundbank_inclusions(
    soundbank: str,
    operation: str,
    inclusions: list[dict],
):
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


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_wwise_soundbank_inclusions(
    soundbank: str,
):
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


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def generate_wwise_soundbanks(
    soundbanks: Optional[list[dict]] = None,
    platforms: Optional[list[str]] = None,
    languages: Optional[list[str]] = None,
    skip_languages: bool = False,
    rebuild_soundbanks: bool = False,
    clear_audio_file_cache: bool = False,
    write_to_disk: bool = False,
    rebuild_init_bank: bool = False,
):
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


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def process_wwise_soundbank_definitions(
    files: list[str],
):
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


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def convert_wwise_external_sources(
    sources: list[dict],
):
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


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def save_wwise_project(
    auto_checkout: bool = True,
):
    """Save the current Wwise project.

    Args:
        auto_checkout: Automatically checkout affected work units and project file
                       from source control. Default true."""
    try:
        return _save_project(auto_checkout=auto_checkout)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
def get_wwise_log(
    channel: str,
):
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


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": False})
def generate_tab_delimited_file(
    rows: list[dict],
    output_path: str,
    columns: Optional[list[str]] = None,
):
    """Generate a Wwise-compatible tab-delimited import file from structured data.

    Use this to create TSV files for import via import_tab_delimited_file (WAAPI)
    or cli_tab_delimited_import (headless CLI). Avoids manual TSV formatting.

    Args:
        rows:        List of row dicts. Keys use snake_case (auto-converted to
                     Wwise column headers):
                       audio_file       → "Audio File"
                       object_path      → "Object Path"
                       object_type      → "Object Type"
                       switch_assignation → "Switch Assignation"
                       event            → "Event"
                       notes            → "Notes"
                       originals_sub_folder → "Originals Sub Folder"
                     Property columns use @-prefix: "@Volume", "@Pitch"

        output_path: Absolute path to write the .tsv file.
                     e.g. "C:/imports/my_import.tsv"

        columns:     Optional explicit column order. If omitted, auto-detected
                     from row keys (standard columns first, then @Properties).

    Examples:
        Basic audio import file:
            rows=[
                {"audio_file": "C:/audio/step1.wav",
                 "object_path": "\\\\Containers\\\\Default Work Unit\\\\<Sound>Step1"},
                {"audio_file": "C:/audio/step2.wav",
                 "object_path": "\\\\Containers\\\\Default Work Unit\\\\<Sound>Step2"},
            ],
            output_path="C:/imports/footsteps.tsv"

        With properties:
            rows=[
                {"audio_file": "C:/audio/gun.wav",
                 "object_path": "\\\\Containers\\\\Default Work Unit\\\\<Sound>Gunshot",
                 "object_type": "Sound", "@Volume": "-3.0"},
            ],
            output_path="C:/imports/weapons.tsv"

    Returns {"output_path": "...", "row_count": N} on success."""
    return _generate_tab_delimited(rows=rows, output_path=output_path, columns=columns)


@mcp.tool(annotations={"destructiveHint": False, "openWorldHint": True})
def convert_audio_to_wav(
    input_directory: str,
    output_directory: str,
    ffmpeg_path: Optional[str] = None,
):
    """Convert non-WAV audio files (OGG, FLAC, MP3, AAC, AIFF) to WAV using ffmpeg.

    Use this before import_audio_files or import_audio_directory when source audio
    is not in WAV format. WAAPI only links WAV files — other formats silently fail.

    Args:
        input_directory:  Directory containing audio files to convert.
        output_directory: Directory to write converted WAV files. Created if missing.
        ffmpeg_path:      Optional explicit path to ffmpeg executable. If omitted,
                          searches PATH and known install locations automatically.

    Returns dict with:
        output_directory: Path to output directory.
        converted: List of successfully converted WAV file paths.
        skipped: List of skipped files (already WAV or unsupported format).
        errors: List of {file, error} dicts for failed conversions.
    """
    try:
        return _convert_to_wav(
            input_dir=input_directory,
            output_dir=output_directory,
            ffmpeg_path=ffmpeg_path,
        )
    except (FileNotFoundError, NotADirectoryError) as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
