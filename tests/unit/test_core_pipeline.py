import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from core.pipeline import (
    import_audio,
    import_tab_delimited,
    set_soundbank_inclusions,
    get_soundbank_inclusions,
    generate_soundbanks,
    process_definition_files,
    convert_external_sources,
    get_log,
    _convert_non_wav_imports,
    _match_wavs_to_objects,
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


# --- Non-WAV auto-conversion ---


def test_convert_non_wav_imports_skips_wav():
    imports = [{"audioFile": "C:/audio/sound.wav"}]
    _convert_non_wav_imports(imports)
    assert imports[0]["audioFile"] == "C:/audio/sound.wav"


def test_convert_non_wav_imports_skips_no_audio():
    imports = [{"objectPath": "\\path\\Sound"}]
    _convert_non_wav_imports(imports)
    assert "audioFile" not in imports[0]


@patch("core.pipeline.convert_file_to_wav")
def test_convert_non_wav_imports_converts_ogg(mock_convert):
    mock_convert.return_value = Path("C:/tmp/cry.wav")
    imports = [{"audioFile": "C:/audio/cry.ogg"}]
    _convert_non_wav_imports(imports)
    assert Path(imports[0]["audioFile"]) == Path("C:/tmp/cry.wav")
    mock_convert.assert_called_once()


@patch("core.pipeline.convert_file_to_wav")
def test_convert_non_wav_imports_converts_mixed(mock_convert):
    mock_convert.return_value = Path("C:/tmp/bad.wav")
    imports = [
        {"audioFile": "C:/audio/good.wav"},
        {"audioFile": "C:/audio/bad.flac"},
    ]
    _convert_non_wav_imports(imports)
    assert imports[0]["audioFile"] == "C:/audio/good.wav"
    assert Path(imports[1]["audioFile"]) == Path("C:/tmp/bad.wav")


def test_convert_non_wav_imports_rejects_unsupported():
    with pytest.raises(ValueError, match="Unsupported audio format"):
        _convert_non_wav_imports([{"audioFile": "C:/audio/sound.mid"}])


# --- WAV-to-object matching ---


def test_match_exact_sound():
    wavs = [Path("C:/audio/Acid.wav")]
    children = [{"name": "Acid", "type": "Sound", "path": "\\AM\\SFX\\Acid"}]
    imports, unmatched_f, unmatched_o = _match_wavs_to_objects(wavs, children)
    assert len(imports) == 1
    assert imports[0]["objectPath"] == "\\AM\\SFX\\Acid"
    assert not unmatched_f
    assert not unmatched_o


def test_match_rsc_variants():
    wavs = [Path("C:/audio/Absorb.wav"), Path("C:/audio/Absorb1.wav"), Path("C:/audio/Absorb2.wav")]
    children = [{"name": "Absorb", "type": "RandomSequenceContainer", "path": "\\AM\\SFX\\Absorb"}]
    imports, unmatched_f, unmatched_o = _match_wavs_to_objects(wavs, children)
    assert len(imports) == 3
    assert all("Absorb" in i["objectPath"] for i in imports)
    assert not unmatched_f
    assert not unmatched_o


def test_match_unmatched_files_and_objects():
    wavs = [Path("C:/audio/Unknown.wav")]
    children = [{"name": "Missing", "type": "Sound", "path": "\\AM\\SFX\\Missing"}]
    imports, unmatched_f, unmatched_o = _match_wavs_to_objects(wavs, children)
    assert len(imports) == 0
    assert len(unmatched_f) == 1
    assert len(unmatched_o) == 1
