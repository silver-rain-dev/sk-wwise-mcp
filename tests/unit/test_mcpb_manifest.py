"""Tests for the .mcpb Bundle: manifest generation, packing and settings.

No network, node or PyInstaller needed. The packing tests use a dummy exe
file; the real exe is exercised by build.ps1.
"""

import json
import subprocess
import sys
import zipfile
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "release"))

import build_mcpb  # noqa: E402
from core.profiles import DEFAULT_PROFILE, PROFILE_NAMES  # noqa: E402
from core.waapi_util import DEFAULT_WAAPI_URL, resolve_waapi_url  # noqa: E402
from core.wwise_cli import resolve_wwise_cli  # noqa: E402

SCHEMA_PATH = REPO_ROOT / "release" / "schema" / "mcpb-manifest-v0.3.schema.json"


@pytest.fixture(scope="module")
def manifest():
    return build_mcpb.build_manifest()


def _resolve(manifest, user_config=None):
    """Mimic an MCPB host: merge defaults with user values, substitute."""
    return build_mcpb.resolve_mcp_config(
        manifest, install_dir="C:/ext", user_config=user_config or {}
    )


# --- AC2: schema ---


def test_manifest_validates_against_mcpb_schema(manifest):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(manifest, schema)


def test_schema_rejects_a_broken_manifest():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    bad = build_mcpb.build_manifest()
    del bad["server"]["entry_point"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_manifest_version_matches_vendored_schema(manifest):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == schema["properties"]["manifest_version"]["const"]


# --- AC3: profile setting ---


def test_profile_setting_default_is_canonical_default(manifest):
    cfg = manifest["user_config"]["profile"]
    assert cfg["default"] == DEFAULT_PROFILE == "author"
    assert cfg["required"] is True


def test_profile_is_a_plain_string_setting(manifest):
    """MCPB user_config has no enum type, so the names live in the description."""
    cfg = manifest["user_config"]["profile"]
    assert cfg["type"] == "string"
    assert "enum" not in cfg and "choices" not in cfg
    for name in PROFILE_NAMES:
        assert name in cfg["description"]


def test_manifest_profile_enum_equals_profile_table():
    assert build_mcpb.profile_names(build_mcpb.build_manifest()) == PROFILE_NAMES


def test_profile_names_follow_a_changed_table(monkeypatch):
    monkeypatch.setattr(build_mcpb, "PROFILE_NAMES", ["listen", "extra"])
    m = build_mcpb.build_manifest()
    assert build_mcpb.profile_names(m) == ["listen", "extra"]


# --- other settings ---


def test_waapi_url_setting(manifest):
    cfg = manifest["user_config"]["waapi_url"]
    assert cfg["type"] == "string"
    assert not cfg.get("required", False)
    assert cfg["default"] == DEFAULT_WAAPI_URL


def test_wwise_console_setting(manifest):
    cfg = manifest["user_config"]["wwise_console"]
    assert cfg["type"] == "file"
    assert not cfg.get("required", False)
    assert cfg.get("multiple", False) is False


def test_mcp_config_wiring(manifest):
    mc = manifest["server"]["mcp_config"]
    assert manifest["server"]["type"] == "binary"
    assert manifest["server"]["entry_point"] == "server/sk-wwise-mcp.exe"
    assert mc["command"] == "${__dirname}/server/sk-wwise-mcp.exe"
    assert mc["args"] == ["--profile", "${user_config.profile}"]
    assert mc["env"] == {
        "SK_WWISE_WAAPI_URL": "${user_config.waapi_url}",
        "SK_WWISE_CONSOLE": "${user_config.wwise_console}",
    }


def test_env_var_names_match_the_code(manifest):
    from core.waapi_util import WAAPI_URL_ENV

    assert WAAPI_URL_ENV in manifest["server"]["mcp_config"]["env"]


def test_windows_only(manifest):
    assert manifest["compatibility"]["platforms"] == ["win32"]


# --- host substitution ---


def test_default_config_resolves_to_profile_author(manifest):
    cfg = _resolve(manifest)
    assert cfg["command"] == "C:/ext/server/sk-wwise-mcp.exe"
    assert cfg["args"] == ["--profile", "author"]


def test_chosen_profile_is_passed_through(manifest):
    assert _resolve(manifest, {"profile": "qa"})["args"] == ["--profile", "qa"]


def test_default_config_env(manifest):
    env = _resolve(manifest)["env"]
    assert env["SK_WWISE_WAAPI_URL"] == DEFAULT_WAAPI_URL
    # no default for the console path: the host leaves the literal placeholder
    assert env["SK_WWISE_CONSOLE"] in ("", "${user_config.wwise_console}")


def test_user_values_reach_env(manifest):
    env = _resolve(
        manifest,
        {"waapi_url": "ws://10.0.0.5:9090/waapi", "wwise_console": "D:/W/WwiseConsole.exe"},
    )["env"]
    assert env["SK_WWISE_WAAPI_URL"] == "ws://10.0.0.5:9090/waapi"
    assert env["SK_WWISE_CONSOLE"] == "D:/W/WwiseConsole.exe"


def test_missing_required_setting_means_no_config(manifest):
    assert _resolve(manifest, {"profile": ""}) is None


# --- unset optional settings must not reach the exe as junk ---


@pytest.mark.parametrize("raw", ["", "   ", "${user_config.waapi_url}"])
def test_waapi_url_resolver_treats_unset_forms_as_default(monkeypatch, raw):
    monkeypatch.setenv("SK_WWISE_WAAPI_URL", raw)
    assert resolve_waapi_url() == DEFAULT_WAAPI_URL


@pytest.mark.parametrize("raw", ["", "   ", "${user_config.wwise_console}"])
def test_console_resolver_treats_unset_forms_as_unset(monkeypatch, raw):
    monkeypatch.setenv("SK_WWISE_CONSOLE", raw)
    monkeypatch.delenv("WWISEROOT", raising=False)
    assert resolve_wwise_cli()["source"] != "SK_WWISE_CONSOLE"


def test_console_resolver_still_honours_a_real_path(monkeypatch):
    monkeypatch.setenv("SK_WWISE_CONSOLE", "D:/W/WwiseConsole.exe")
    r = resolve_wwise_cli()
    assert r["source"] == "SK_WWISE_CONSOLE"
    assert r["path"] == "D:/W/WwiseConsole.exe"


# --- AC1/AC4: packing and smoke ---


@pytest.fixture
def bundle(tmp_path):
    exe = tmp_path / "sk-wwise-mcp.exe"
    exe.write_bytes(b"MZ-dummy")
    out = tmp_path / "out" / "sk-wwise-mcp.mcpb"
    result = build_mcpb.build_mcpb(exe, out)
    return out, result


def test_build_mcpb_writes_the_output_path(bundle):
    out, result = bundle
    assert out.is_file()
    assert Path(result) == out


def test_mcpb_is_a_zip_with_manifest_and_exe(bundle):
    out, _ = bundle
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
        assert "manifest.json" in names
        assert "server/sk-wwise-mcp.exe" in names
        assert z.read("server/sk-wwise-mcp.exe") == b"MZ-dummy"
        packed = json.loads(z.read("manifest.json"))
    assert packed == build_mcpb.build_manifest()


def test_packed_manifest_validates(bundle):
    out, _ = bundle
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    with zipfile.ZipFile(out) as z:
        jsonschema.validate(json.loads(z.read("manifest.json")), schema)


def test_build_mcpb_missing_exe_is_an_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        build_mcpb.build_mcpb(tmp_path / "nope.exe", tmp_path / "x.mcpb")


def test_unpacked_bundle_default_config_starts_with_profile_author(bundle, tmp_path):
    """Unpack, resolve the command with default config, run it.

    The dummy exe cannot run, so the resolved args are run through cli.py
    with --help: it proves the args are accepted and the entry exists.
    """
    out, _ = bundle
    dest = tmp_path / "unpacked"
    with zipfile.ZipFile(out) as z:
        z.extractall(dest)
    manifest = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))
    cfg = build_mcpb.resolve_mcp_config(manifest, install_dir=str(dest), user_config={})
    assert Path(cfg["command"]).is_file()
    assert cfg["args"] == ["--profile", "author"]

    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "cli.py"), *cfg["args"], "--help"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert "--profile" in proc.stdout


def test_exe_rejects_an_empty_profile():
    """Why the manifest default must always be non-empty."""
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "cli.py"), "--profile", ""],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=60,
    )
    assert proc.returncode != 0
    assert "author" in (proc.stderr + proc.stdout)


# --- AC5: legacy zip untouched ---


def test_build_ps1_still_builds_legacy_zip_and_adds_mcpb():
    text = (REPO_ROOT / "build.ps1").read_text(encoding="utf-8")
    assert "Compress-Archive" in text
    assert "sk-wwise-mcp.zip" in text
    assert "sk-wwise-mcp.mcpb" in text
    assert "build_mcpb.py" in text


def test_mcpb_output_is_gitignored():
    ignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "sk-wwise-mcp.mcpb" in ignore
