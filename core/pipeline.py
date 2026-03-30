import csv
import io
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from core.audio_convert import _CONVERTIBLE_EXTENSIONS, convert_file_to_wav
from core.waapi_util import call


def _get_originals_dir() -> Path:
    """Get the Originals directory of the currently open Wwise project."""
    info = call("ak.wwise.core.getProjectInfo")
    return Path(info["directories"]["originals"])


def _convert_non_wav_imports(imports: list[dict]) -> None:
    """Auto-convert non-WAV audio files to WAV before import.

    WAAPI silently fails to create AudioFileSource links for non-WAV files.
    If ffmpeg is available, convertible formats are converted to WAV in a temp
    directory and the import entry is rewritten to point at the converted file.
    If ffmpeg is not available, raises FileNotFoundError with install instructions.
    Unsupported formats raise ValueError.
    """
    for entry in imports:
        audio = entry.get("audioFile")
        if not audio:
            continue
        src = Path(audio)
        ext = src.suffix.lower()
        if not ext or ext == ".wav":
            continue
        if ext not in _CONVERTIBLE_EXTENSIONS:
            raise ValueError(
                f"Unsupported audio format '{ext}' for '{src.name}'. "
                f"Supported formats: WAV, {', '.join(sorted(e.lstrip('.').upper() for e in _CONVERTIBLE_EXTENSIONS))}."
            )
        # Convert to WAV in a temp directory (survives until process exit)
        tmp_dir = Path(tempfile.mkdtemp(prefix="wwise_convert_"))
        wav_path = convert_file_to_wav(src, tmp_dir)
        entry["audioFile"] = str(wav_path)


def _stage_audio_files(query: dict) -> dict:
    """Copy audio files into the project's Originals folder so Wwise can find them.

    For each import entry with an ``audioFile`` that lives outside the
    project's Originals tree, the file is copied into
    ``<Originals>/<originalsSubFolder>/`` (defaulting to ``SFX/``).
    The ``audioFile`` value is then rewritten to the destination path.
    """
    imports = query.get("imports")
    if not imports or not any(e.get("audioFile") for e in imports):
        return query

    _convert_non_wav_imports(imports)

    originals = _get_originals_dir()
    default_sub = query.get("default", {}).get("originalsSubFolder", "SFX")

    for entry in imports:
        audio = entry.get("audioFile")
        if not audio:
            continue

        src = Path(audio)
        if not src.is_file():
            continue  # let Wwise report the error

        # Already inside the Originals tree — nothing to do
        try:
            src.resolve().relative_to(originals.resolve())
            continue
        except ValueError:
            pass

        sub = entry.get("originalsSubFolder", default_sub)
        dest_dir = originals / sub
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        shutil.copy2(str(src), str(dest))
        entry["audioFile"] = str(dest)

    return query


def import_audio(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.audio.import query."""
    query = _stage_audio_files(query)
    return call("ak.wwise.core.audio.import", query, timeout=300)


def _query_children_with_types(parent: str) -> list[dict]:
    """Query children of a Wwise object, returning name, path, and type."""
    from core.query import execute_object_query
    from_clause = {"path": [parent]} if parent.startswith("\\") else {"id": [parent]}
    return execute_object_query({
        "from": from_clause,
        "transform": [{"select": ["children"]}],
        "options": {"return": ["name", "path", "type"]},
    })


def _match_wavs_to_objects(
    wav_files: list[Path],
    children: list[dict],
) -> tuple[list[dict], list[str], list[str]]:
    """Match WAV files to Wwise objects by name.

    For Sound objects: exact stem match (e.g. Acid.wav → Acid).
    For RandomSequenceContainer: match by base name (strip trailing digits).
        Each matching WAV becomes a child Sound import.

    Returns (imports, unmatched_files, unmatched_objects).
    """
    from collections import defaultdict

    # Group WAVs by base name (strip trailing digits)
    wav_by_base = defaultdict(list)
    wav_exact = {}
    for f in wav_files:
        stem = f.stem
        wav_exact[stem] = f
        base = re.sub(r"\d+$", "", stem)
        wav_by_base[base].append(f)

    imports = []
    matched_wavs = set()
    unmatched_objects = []

    for child in children:
        name = child["name"]
        ctype = child["type"]
        cpath = child["path"]

        if ctype == "Sound":
            if name in wav_exact:
                imports.append({
                    "objectPath": f"{cpath}",
                    "audioFile": str(wav_exact[name]).replace("\\", "/"),
                })
                matched_wavs.add(str(wav_exact[name]))
            else:
                unmatched_objects.append(name)
        elif ctype == "RandomSequenceContainer":
            variants = wav_by_base.get(name, [])
            if variants:
                for wav in variants:
                    imports.append({
                        "objectPath": f"{cpath}\\<Sound SFX>{wav.stem}",
                        "audioFile": str(wav).replace("\\", "/"),
                    })
                    matched_wavs.add(str(wav))
            else:
                unmatched_objects.append(name)
        else:
            # Other container types — try exact match
            if name in wav_exact:
                imports.append({
                    "objectPath": f"{cpath}",
                    "audioFile": str(wav_exact[name]).replace("\\", "/"),
                })
                matched_wavs.add(str(wav_exact[name]))

    unmatched_files = [str(f) for f in wav_files if str(f) not in matched_wavs]

    return imports, unmatched_files, unmatched_objects


def scan_and_import_directory(
    directory: str,
    import_location: str,
    import_language: str = "SFX",
    import_operation: str = "useExisting",
    originals_sub_folder: Optional[str] = None,
) -> dict:
    """Scan a directory of WAV files and import them by matching to existing Wwise objects.

    Args:
        directory:           Path to directory containing WAV files.
        import_location:     Wwise parent object (path or GUID) whose children to match against.
        import_language:     "SFX" or language name. Default "SFX".
        import_operation:    "useExisting" (default), "createNew", or "replaceExisting".
        originals_sub_folder: Optional subfolder within Originals/SFX/.

    Returns dict with matched, imported, unmatched_files, unmatched_objects, objects.
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Directory does not exist: {directory}")

    # Collect audio files (WAV + convertible formats)
    supported = {".wav"} | _CONVERTIBLE_EXTENSIONS
    wav_files = sorted(
        f for f in dir_path.iterdir()
        if f.is_file() and f.suffix.lower() in supported
    )
    if not wav_files:
        return {"matched": 0, "imported": 0, "unmatched_files": [], "unmatched_objects": [], "objects": []}

    # Query Wwise children
    children = _query_children_with_types(import_location)

    # Match WAVs to objects
    imports, unmatched_files, unmatched_objects = _match_wavs_to_objects(wav_files, children)

    if not imports:
        return {
            "matched": 0, "imported": 0,
            "unmatched_files": unmatched_files,
            "unmatched_objects": unmatched_objects,
            "objects": [],
        }

    # Build default dict
    default = {"importLanguage": import_language}
    if originals_sub_folder:
        default["originalsSubFolder"] = originals_sub_folder

    # Import in batches of 50
    all_objects = []
    batch_size = 50
    for i in range(0, len(imports), batch_size):
        batch = imports[i:i + batch_size]
        query = {
            "imports": batch,
            "importOperation": import_operation,
            "default": default,
        }
        result = import_audio(query)
        all_objects.extend(result.get("objects", []))

    return {
        "matched": len(imports),
        "imported": len(all_objects),
        "unmatched_files": unmatched_files,
        "unmatched_objects": unmatched_objects,
        "objects": all_objects,
    }


def import_tab_delimited(query: dict, options: dict = None) -> dict:
    """Execute a WAAPI ak.wwise.core.audio.importTabDelimited query."""
    return call("ak.wwise.core.audio.importTabDelimited", query, options, timeout=300)


def set_soundbank_inclusions(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.soundbank.setInclusions query."""
    return call("ak.wwise.core.soundbank.setInclusions", query)


def generate_soundbanks(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.soundbank.generate query."""
    return call("ak.wwise.core.soundbank.generate", query, timeout=600)


def get_soundbank_inclusions(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.soundbank.getInclusions query."""
    return call("ak.wwise.core.soundbank.getInclusions", query)


def convert_external_sources(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.soundbank.convertExternalSources query."""
    return call("ak.wwise.core.soundbank.convertExternalSources", query, timeout=300)


def process_definition_files(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.soundbank.processDefinitionFiles query."""
    return call("ak.wwise.core.soundbank.processDefinitionFiles", query)


def save_project(auto_checkout: bool = True) -> dict:
    """Execute a WAAPI ak.wwise.core.project.save query."""
    query = {}
    if not auto_checkout:
        query["autoCheckOutToSourceControl"] = False
    return call("ak.wwise.core.project.save", query)


def get_log(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.log.get query."""
    return call("ak.wwise.core.log.get", query)


# -- Tab-delimited file generation --

# Standard Wwise tab-delimited columns
_TSV_COLUMNS = [
    "Audio File",
    "Object Path",
    "Object Type",
    "Switch Assignation",
    "Event",
    "Notes",
    "Originals Sub Folder",
]


def generate_tab_delimited(
    rows: list[dict],
    output_path: str,
    columns: Optional[list[str]] = None,
) -> dict:
    """Generate a Wwise-compatible tab-delimited import file from structured data.

    Args:
        rows:        List of row dicts. Keys map to column headers (case-insensitive
                     matching with underscore-to-space conversion):
                       audio_file / Audio File
                       object_path / Object Path
                       object_type / Object Type
                       switch_assignation / Switch Assignation
                       event / Event
                       notes / Notes
                       originals_sub_folder / Originals Sub Folder
                     Plus any @PropertyName columns (e.g. "@Volume", "@Pitch").
        output_path: Absolute path to write the .tsv file.
        columns:     Optional explicit column list. If omitted, auto-detected from
                     row keys. Standard columns come first, then @Property columns.

    Returns dict with "output_path" and "row_count".
    """
    if not rows:
        return {"error": "No rows provided"}

    # Normalize keys: snake_case → Title Case with spaces
    def _normalize_key(k: str) -> str:
        if k.startswith("@"):
            return k  # Keep @Property keys as-is
        return k.replace("_", " ").title()

    normalized_rows = []
    for row in rows:
        normalized_rows.append({_normalize_key(k): v for k, v in row.items()})

    # Determine columns
    if columns:
        col_list = columns
    else:
        # Collect all keys, standard columns first, then @Properties
        all_keys = set()
        for row in normalized_rows:
            all_keys.update(row.keys())
        standard = [c for c in _TSV_COLUMNS if c in all_keys]
        props = sorted(k for k in all_keys if k.startswith("@"))
        extra = sorted(k for k in all_keys if k not in _TSV_COLUMNS and not k.startswith("@"))
        col_list = standard + extra + props

    # Write TSV
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar=None)
        writer.writerow(col_list)
        for row in normalized_rows:
            writer.writerow([row.get(col, "") for col in col_list])

    return {"output_path": str(out), "row_count": len(normalized_rows)}
