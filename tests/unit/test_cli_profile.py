import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import cli
from core.profiles import PROFILE_NAMES, resolve_profile


def test_admin_profile_matches_server_registry():
    assert set(resolve_profile("admin")) == set(cli.SERVERS)


def test_unknown_profile_exits_listing_valid_names(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["sk-wwise-mcp", "--profile", "viewer"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    message = str(exc.value)
    assert "viewer" in message
    for name in PROFILE_NAMES:
        assert name in message


def test_profile_and_server_together_is_an_error(monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["sk-wwise-mcp", "--profile", "author", "--server", "browse"]
    )
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code != 0


def _run_main(monkeypatch, argv):
    """Run cli.main() with fake server modules; return (imported names, mounted fakes)."""
    imported = []
    fakes = {}

    def fake_import(path):
        imported.append(path)
        fake = MagicMock(name=path)
        fakes[path] = fake
        return fake

    master = MagicMock(name="master")
    fake_fastmcp = MagicMock()
    fake_fastmcp.FastMCP.return_value = master
    monkeypatch.setitem(sys.modules, "fastmcp", fake_fastmcp)
    monkeypatch.setattr(cli.importlib, "import_module", fake_import)
    monkeypatch.setattr(sys, "argv", argv)
    cli.main()
    return imported, fakes, master


def test_profile_author_mounts_only_author_servers(monkeypatch):
    imported, fakes, master = _run_main(
        monkeypatch, ["sk-wwise-mcp", "--profile", "author"]
    )
    expected = [cli.SERVERS[n] for n in resolve_profile("author")]
    assert sorted(imported) == sorted(expected)
    mounted = [c.args[0] for c in master.mount.call_args_list]
    assert mounted == [fakes[p].mcp for p in expected]
    master.run.assert_called_once_with(transport="stdio")


def test_server_comma_list_still_works(monkeypatch):
    imported, _, _ = _run_main(
        monkeypatch, ["sk-wwise-mcp", "--server", "browse,objects"]
    )
    assert imported == [cli.SERVERS["browse"], cli.SERVERS["objects"]]


@pytest.mark.parametrize("blank", ["", " ", "   ", "\t"])
def test_blank_profile_exits_listing_valid_names(monkeypatch, blank):
    # Fail closed: an empty/blank --profile must never fall through to "mount all".
    monkeypatch.setattr(sys, "argv", ["sk-wwise-mcp", "--profile", blank])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code != 0
    message = str(exc.value)
    for name in PROFILE_NAMES:
        assert name in message


@pytest.mark.parametrize("blank", ["", " "])
def test_blank_profile_with_server_is_a_conflict_error(monkeypatch, blank):
    monkeypatch.setattr(
        sys, "argv", ["sk-wwise-mcp", "--profile", blank, "--server", "browse"]
    )
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert "cannot be used together" in str(exc.value)


def test_profile_name_is_not_stripped(monkeypatch):
    # Same strictness as core.profiles.resolve_profile: " author" is unknown.
    monkeypatch.setattr(sys, "argv", ["sk-wwise-mcp", "--profile", " author"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert "unknown profile" in str(exc.value)
