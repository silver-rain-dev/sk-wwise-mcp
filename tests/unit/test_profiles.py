import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.profiles import PROFILE_NAMES, mcp_config, resolve_profile

LISTEN = ["browse", "audition", "media-read"]
AUTHOR = LISTEN + ["objects", "containers", "pipeline", "ui"]
BUILD = AUTHOR + ["command-line"]
QA = ["browse", "audition", "profiling", "profiling-control", "remote"]


@pytest.mark.parametrize(
    "name, expected",
    [("listen", LISTEN), ("author", AUTHOR), ("build", BUILD), ("qa", QA)],
)
def test_profile_resolves_to_exact_servers(name, expected):
    assert resolve_profile(name) == expected


def test_admin_is_all_twelve_servers():
    servers = resolve_profile("admin")
    assert len(servers) == 12
    assert len(set(servers)) == 12


# --- drift checks: files and docs must match the code table -----------------

ROOT = Path(__file__).parent.parent.parent


def test_profile_files_are_exactly_the_profiles_and_match_the_table():
    files = sorted(p.name for p in (ROOT / "profiles").glob("*.mcp.json"))
    assert files == sorted(f"{n}.mcp.json" for n in PROFILE_NAMES)
    for name in PROFILE_NAMES:
        actual = json.loads((ROOT / "profiles" / f"{name}.mcp.json").read_text())
        assert actual == mcp_config(name), f"profiles/{name}.mcp.json drifted"
        entries = list(actual["mcpServers"])
        assert entries == [f"sk-wwise-{s}" for s in resolve_profile(name)]


def _role_table(path):
    """Parse markdown table rows whose first cell is a profile name."""
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        first = cells[0].strip("`")
        if line.lstrip().startswith("|") and first in PROFILE_NAMES:
            rows[first] = [s.strip().strip("`") for s in cells[1].split(",")]
    return rows


@pytest.mark.parametrize("doc", ["release/README.md", "README.md"])
def test_readme_role_table_matches_the_table(doc):
    rows = _role_table(ROOT / doc)
    assert sorted(rows) == sorted(PROFILE_NAMES), f"{doc} role table is missing profiles"
    for name in PROFILE_NAMES:
        assert rows[name] == resolve_profile(name), f"{doc} row {name} drifted"
