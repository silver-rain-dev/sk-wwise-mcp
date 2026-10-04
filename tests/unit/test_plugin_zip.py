"""Tests for the plugin zip (sk-wwise-plugin.zip) and the root marketplace.json.

No network, node or PyInstaller needed: the .mcpb is built from a dummy exe.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "release"))

import build_mcpb  # noqa: E402
import build_plugin  # noqa: E402

SKILLS_SRC = REPO_ROOT / ".claude" / "skills"


@pytest.fixture(scope="module")
def plugin_zip(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("plugin")
    exe = tmp / "sk-wwise-mcp.exe"
    exe.write_bytes(b"MZ fake exe")
    mcpb = build_mcpb.build_mcpb(exe, tmp / "sk-wwise-mcp.mcpb")
    return build_plugin.build_plugin_zip(mcpb, tmp / "sk-wwise-plugin.zip")


def _names(path):
    with zipfile.ZipFile(path) as z:
        return z.namelist()


# --- AC1: layout ---


def test_zip_has_plugin_json_mcpb_and_wwise_skills(plugin_zip):
    names = set(_names(plugin_zip))
    assert ".claude-plugin/plugin.json" in names
    assert "sk-wwise-mcp.mcpb" in names
    expected = {
        f"skills/{d.name}/SKILL.md"
        for d in SKILLS_SRC.iterdir()
        if d.name.startswith("wwise-") and (d / "SKILL.md").is_file()
    }
    assert expected  # the repo has wwise skills
    assert expected <= names


def test_zip_has_nothing_else(plugin_zip):
    for name in _names(plugin_zip):
        assert (
            name == ".claude-plugin/plugin.json"
            or name == "sk-wwise-mcp.mcpb"
            or (name.startswith("skills/wwise-") and name.endswith("/SKILL.md"))
        ), name


def test_embedded_mcpb_is_the_given_bundle(plugin_zip, tmp_path):
    with zipfile.ZipFile(plugin_zip) as z:
        inner = z.read("sk-wwise-mcp.mcpb")
    # it is a real .mcpb: a zip with a manifest at its root
    p = tmp_path / "inner.mcpb"
    p.write_bytes(inner)
    assert "manifest.json" in _names(p)


# --- AC2: plugin.json and marketplace.json validate ---

MARKETPLACE_FILE = REPO_ROOT / ".claude-plugin" / "marketplace.json"


def _plugin_json(plugin_zip):
    with zipfile.ZipFile(plugin_zip) as z:
        return json.loads(z.read(".claude-plugin/plugin.json"))


def test_plugin_json_fields(plugin_zip):
    plugin = _plugin_json(plugin_zip)
    assert plugin["name"] == build_plugin.PLUGIN_NAME
    assert plugin["description"]
    assert plugin["version"] == build_mcpb.build_manifest()["version"]
    assert plugin["mcpServers"] == "./sk-wwise-mcp.mcpb"
    assert build_plugin.validate_plugin_manifest(plugin) == []


def test_plugin_version_follows_the_version_argument(tmp_path):
    exe = tmp_path / "e.exe"
    exe.write_bytes(b"x")
    mcpb = build_mcpb.build_mcpb(exe, tmp_path / "b.mcpb")
    out = build_plugin.build_plugin_zip(mcpb, tmp_path / "p.zip", version="9.8.7")
    assert _plugin_json(out)["version"] == "9.8.7"


def test_marketplace_entry_is_an_archive_source_at_the_release_asset():
    entry = build_plugin.marketplace_entry("1.2.3")
    assert entry["name"] == build_plugin.PLUGIN_NAME
    assert entry["version"] == "1.2.3"
    assert entry["source"] == {
        "source": "archive",
        "url": "https://github.com/silver-rain-dev/sk-wwise-mcp/releases/download/"
        "v1.2.3/sk-wwise-plugin.zip",
    }


def test_marketplace_entry_can_pin_a_sha256():
    digest = "ab" * 32
    entry = build_plugin.marketplace_entry("1.2.3", sha256=digest)
    assert entry["source"]["sha256"] == digest


def test_built_marketplace_validates_and_names_match(plugin_zip):
    marketplace = build_plugin.build_marketplace()
    assert build_plugin.validate_marketplace(marketplace) == []
    assert marketplace["plugins"][0]["name"] == _plugin_json(plugin_zip)["name"]


def test_validators_reject_broken_files():
    plugin = build_plugin.build_plugin_manifest()
    assert build_plugin.validate_plugin_manifest({**plugin, "name": ""})
    assert build_plugin.validate_plugin_manifest({**plugin, "name": "Has Space"})
    assert build_plugin.validate_plugin_manifest({**plugin, "mcpServers": "sk.mcpb"})
    assert build_plugin.validate_plugin_manifest({**plugin, "mcpServers": "./../x.mcpb"})
    assert build_plugin.validate_plugin_manifest({**plugin, "mcpServers": "./x.json.bak"})
    market = build_plugin.build_marketplace()
    assert build_plugin.validate_marketplace({**market, "owner": {}})
    assert build_plugin.validate_marketplace({**market, "plugins": []})
    bad = json.loads(json.dumps(market))
    bad["plugins"][0]["source"]["url"] = "http://example.com/p.zip"
    assert build_plugin.validate_marketplace(bad)
    bad["plugins"][0]["source"] = "./../up"
    assert build_plugin.validate_marketplace(bad)
    bad["plugins"][0]["name"] = "other"
    assert build_plugin.validate_marketplace(bad, plugin_name="sk-wwise-mcp")


def test_committed_marketplace_json_validates_and_is_consistent():
    marketplace = json.loads(MARKETPLACE_FILE.read_text(encoding="utf-8"))
    assert build_plugin.validate_marketplace(marketplace) == []
    entry = marketplace["plugins"][0]
    # URL and version move together; a sha256 is optional and not compared.
    expected = build_plugin.marketplace_entry(entry["version"])
    assert entry["source"]["url"] == expected["source"]["url"]
    assert entry["name"] == build_plugin.PLUGIN_NAME


def test_write_marketplace_round_trips(tmp_path):
    path = build_plugin.write_marketplace("2.0.0", sha256="cd" * 32, path=tmp_path / "m.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == build_plugin.build_marketplace("2.0.0", sha256="cd" * 32)


@pytest.mark.skipif(shutil.which("claude") is None, reason="claude CLI not on PATH")
def test_claude_plugin_validate_accepts_plugin_and_marketplace(plugin_zip, tmp_path):
    root = tmp_path / "unpacked"
    with zipfile.ZipFile(plugin_zip) as z:
        z.extractall(root)
    mkt = tmp_path / "mkt"
    (mkt / ".claude-plugin").mkdir(parents=True)
    # Relative-path source so validate can also read the plugin's plugin.json.
    marketplace = build_plugin.build_marketplace()
    marketplace["plugins"][0]["source"] = "./plugin"
    (mkt / ".claude-plugin" / "marketplace.json").write_text(json.dumps(marketplace))
    shutil.copytree(root, mkt / "plugin")
    env = {**os.environ, "CLAUDE_CONFIG_DIR": str(tmp_path / "cfg")}
    for target in (root, mkt):
        r = subprocess.run(
            ["claude", "plugin", "validate", str(target)],
            capture_output=True, text=True, env=env, timeout=120,
        )
        assert r.returncode == 0, r.stdout + r.stderr


def test_cli_builds_zip_and_can_write_marketplace_with_digest(tmp_path):
    exe = tmp_path / "e.exe"
    exe.write_bytes(b"x")
    mcpb = build_mcpb.build_mcpb(exe, tmp_path / "b.mcpb")
    out = tmp_path / "p.zip"
    market = tmp_path / "m" / "marketplace.json"
    build_plugin.main(
        ["--mcpb", str(mcpb), "--out", str(out), "--version", "3.2.1",
         "--write-marketplace", "--marketplace-out", str(market)]
    )
    data = json.loads(market.read_text(encoding="utf-8"))
    source = data["plugins"][0]["source"]
    assert data["plugins"][0]["version"] == "3.2.1"
    assert "v3.2.1" in source["url"]
    assert source["sha256"] == hashlib.sha256(out.read_bytes()).hexdigest()


def test_cli_fails_on_missing_bundle(tmp_path):
    with pytest.raises(FileNotFoundError):
        build_plugin.main(["--mcpb", str(tmp_path / "none.mcpb"), "--out", str(tmp_path / "p.zip")])


# --- AC3: eval skills are not shipped ---


def test_eval_skills_are_excluded(plugin_zip):
    eval_dirs = [d.name for d in SKILLS_SRC.iterdir() if d.name.startswith("eval-")]
    assert eval_dirs  # the repo has eval skills, so this check means something
    names = _names(plugin_zip)
    assert not [n for n in names if "eval" in n]
    for d in eval_dirs:
        assert not any(n.startswith(f"skills/{d}/") for n in names)
