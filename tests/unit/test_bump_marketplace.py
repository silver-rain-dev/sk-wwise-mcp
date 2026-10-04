"""Tests for release/bump_marketplace.py: tag + repo -> marketplace.json.

Release CI runs this after publishing a release. No network needed.
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "release"))

import build_plugin  # noqa: E402
import bump_marketplace  # noqa: E402


def _entry(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    assert len(data["plugins"]) == 1
    return data["plugins"][0]


def test_tag_and_repo_give_the_expected_marketplace(tmp_path):
    out = tmp_path / "marketplace.json"
    bump_marketplace.bump_marketplace("v0.2.0", "acme/wwise-tools", path=out)
    assert json.loads(out.read_text(encoding="utf-8")) == {
        "name": "sk-wwise",
        "description": "Claude plugin for browsing and editing Wwise projects.",
        "owner": {"name": "silver-rain-dev", "url": "https://github.com/silver-rain-dev"},
        "plugins": [
            {
                "name": "sk-wwise-mcp",
                "description": build_plugin.DESCRIPTION,
                "version": "0.2.0",
                "source": {
                    "source": "archive",
                    "url": "https://github.com/acme/wwise-tools/releases/download/"
                    "v0.2.0/sk-wwise-plugin.zip",
                },
            }
        ],
    }


def test_default_repo_is_the_project_repo(tmp_path):
    out = tmp_path / "marketplace.json"
    bump_marketplace.bump_marketplace("v1.4.2", path=out)
    assert _entry(out)["source"]["url"] == (
        "https://github.com/silver-rain-dev/sk-wwise-mcp/releases/download/"
        "v1.4.2/sk-wwise-plugin.zip"
    )


def test_build_plugin_default_repo_is_unchanged():
    assert build_plugin.marketplace_entry("0.3.0")["source"]["url"] == (
        "https://github.com/silver-rain-dev/sk-wwise-mcp/releases/download/"
        "v0.3.0/sk-wwise-plugin.zip"
    )


def test_zip_pins_its_sha256(tmp_path):
    zip_path = tmp_path / "sk-wwise-plugin.zip"
    zip_path.write_bytes(b"plugin bytes")
    out = tmp_path / "marketplace.json"
    bump_marketplace.bump_marketplace("v0.2.0", path=out, zip_path=zip_path)
    assert _entry(out)["source"]["sha256"] == hashlib.sha256(b"plugin bytes").hexdigest()


def test_rerunning_for_the_same_tag_gives_identical_bytes(tmp_path):
    out = tmp_path / "marketplace.json"
    bump_marketplace.bump_marketplace("v0.2.0", "a/b", path=out)
    first = out.read_bytes()
    bump_marketplace.bump_marketplace("v0.2.0", "a/b", path=out)
    assert out.read_bytes() == first


def test_output_validates_with_the_plugin_validator(tmp_path):
    out = tmp_path / "marketplace.json"
    bump_marketplace.bump_marketplace("v2.0.0-rc.1", "a/b", path=out)
    assert build_plugin.validate_marketplace(json.loads(out.read_text(encoding="utf-8"))) == []
    assert _entry(out)["version"] == "2.0.0-rc.1"


@pytest.mark.parametrize(
    "tag", ["0.2.0", "v0.2", "vx.y.z", "v", "", "v0.2.0 ", "v0.2.0/../x", "latest", "v1.2.3;rm"]
)
def test_bad_tags_are_rejected(tag, tmp_path):
    out = tmp_path / "marketplace.json"
    with pytest.raises(ValueError):
        bump_marketplace.bump_marketplace(tag, path=out)
    assert not out.exists()


@pytest.mark.parametrize("repo", ["", "noslash", "a/b/c", "a b/c", "/b", "a/"])
def test_bad_repos_are_rejected(repo, tmp_path):
    out = tmp_path / "marketplace.json"
    with pytest.raises(ValueError):
        bump_marketplace.bump_marketplace("v0.2.0", repo, path=out)
    assert not out.exists()


def test_cli_writes_the_file(tmp_path, capsys):
    zip_path = tmp_path / "p.zip"
    zip_path.write_bytes(b"z")
    out = tmp_path / "m" / "marketplace.json"
    rc = bump_marketplace.main(
        ["--tag", "v0.9.0", "--repo", "o/r", "--zip", str(zip_path), "--path", str(out)]
    )
    assert rc == 0
    entry = _entry(out)
    assert entry["version"] == "0.9.0"
    assert "o/r/releases/download/v0.9.0/" in entry["source"]["url"]
    assert entry["source"]["sha256"] == hashlib.sha256(b"z").hexdigest()


def test_cli_print_version_writes_nothing(tmp_path, capsys):
    out = tmp_path / "marketplace.json"
    rc = bump_marketplace.main(["--tag", "v0.2.0", "--print-version", "--path", str(out)])
    assert rc == 0
    assert capsys.readouterr().out.strip() == "0.2.0"
    assert not out.exists()


def test_cli_exits_nonzero_on_a_bad_tag(tmp_path, capsys):
    rc = bump_marketplace.main(["--tag", "nope", "--path", str(tmp_path / "m.json")])
    assert rc != 0
    assert "tag" in capsys.readouterr().err.lower()
