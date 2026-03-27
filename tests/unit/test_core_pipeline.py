import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pipeline import (
    import_audio,
    import_tab_delimited,
    set_soundbank_inclusions,
    get_soundbank_inclusions,
    generate_soundbanks,
    process_definition_files,
    convert_external_sources,
    get_log,
)


@patch("core.pipeline.call")
def test_import_audio(mock_call):
    mock_call.return_value = {"objects": [{"id": "a", "name": "Sound1"}]}
    result = import_audio({"imports": [{"objectPath": "\\path\\Sound"}]})
    assert len(result["objects"]) == 1
    mock_call.assert_called_once_with("ak.wwise.core.audio.import", {"imports": [{"objectPath": "\\path\\Sound"}]}, timeout=300)


@patch("core.pipeline.call")
def test_import_tab_delimited(mock_call):
    mock_call.return_value = {"objects": []}
    query = {"importFile": "C:/file.tsv", "importLanguage": "English(US)", "importOperation": "useExisting"}
    result = import_tab_delimited(query, {"return": ["id"]})
    mock_call.assert_called_once_with("ak.wwise.core.audio.importTabDelimited", query, {"return": ["id"]}, timeout=300)


@patch("core.pipeline.call")
def test_set_soundbank_inclusions(mock_call):
    mock_call.return_value = {}
    query = {"soundbank": "SoundBank:MyBank", "operation": "add", "inclusions": []}
    set_soundbank_inclusions(query)
    mock_call.assert_called_once_with("ak.wwise.core.soundbank.setInclusions", query)


@patch("core.pipeline.call")
def test_get_soundbank_inclusions(mock_call):
    mock_call.return_value = {"inclusions": [{"object": "{guid}", "filter": ["events"]}]}
    result = get_soundbank_inclusions({"soundbank": "SoundBank:MyBank"})
    assert len(result["inclusions"]) == 1
    mock_call.assert_called_once_with("ak.wwise.core.soundbank.getInclusions", {"soundbank": "SoundBank:MyBank"})


@patch("core.pipeline.call")
def test_generate_soundbanks(mock_call):
    mock_call.return_value = {"logs": []}
    result = generate_soundbanks({"soundbanks": [{"name": "MyBank"}]})
    assert result["logs"] == []
    mock_call.assert_called_once_with("ak.wwise.core.soundbank.generate", {"soundbanks": [{"name": "MyBank"}]}, timeout=600)


@patch("core.pipeline.call")
def test_process_definition_files(mock_call):
    mock_call.return_value = {}
    process_definition_files({"files": ["C:/defs.txt"]})
    mock_call.assert_called_once_with("ak.wwise.core.soundbank.processDefinitionFiles", {"files": ["C:/defs.txt"]})


@patch("core.pipeline.call")
def test_convert_external_sources(mock_call):
    mock_call.return_value = {}
    query = {"sources": [{"input": "C:/VO.wsources", "platform": "Windows"}]}
    convert_external_sources(query)
    mock_call.assert_called_once_with("ak.wwise.core.soundbank.convertExternalSources", query, timeout=300)


@patch("core.pipeline.call")
def test_get_log(mock_call):
    mock_call.return_value = {"items": [{"severity": "Message", "message": "Done"}]}
    result = get_log({"channel": "soundbankGenerate"})
    assert result["items"][0]["severity"] == "Message"
    mock_call.assert_called_once_with("ak.wwise.core.log.get", {"channel": "soundbankGenerate"})
