import shutil
from pathlib import Path

from core.waapi_util import call


def _get_originals_dir() -> Path:
    """Get the Originals directory of the currently open Wwise project."""
    info = call("ak.wwise.core.getProjectInfo")
    return Path(info["directories"]["originals"])


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
