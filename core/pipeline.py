from core.waapi_util import call


def import_audio(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.audio.import query."""
    return call("ak.wwise.core.audio.import", query)


def import_tab_delimited(query: dict, options: dict = {}) -> dict:
    """Execute a WAAPI ak.wwise.core.audio.importTabDelimited query."""
    return call("ak.wwise.core.audio.importTabDelimited", query, options)


def set_soundbank_inclusions(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.soundbank.setInclusions query."""
    return call("ak.wwise.core.soundbank.setInclusions", query)


def generate_soundbanks(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.soundbank.generate query."""
    return call("ak.wwise.core.soundbank.generate", query)


def get_soundbank_inclusions(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.soundbank.getInclusions query."""
    return call("ak.wwise.core.soundbank.getInclusions", query)


def convert_external_sources(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.soundbank.convertExternalSources query."""
    return call("ak.wwise.core.soundbank.convertExternalSources", query)


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
