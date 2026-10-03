"""Canonical Profile table: which Servers each Profile mounts.

One place defines the roles. The exe (`--profile`), the legacy
`profiles/*.mcp.json` files and the release README role table all follow it;
tests fail if they drift.

Server names are the keys of `cli.SERVERS` (e.g. "media-read").
"""

_LISTEN = ["browse", "audition", "media-read"]
_AUTHOR = _LISTEN + ["objects", "containers", "pipeline", "ui"]
_BUILD = _AUTHOR + ["command-line"]
_QA = ["browse", "audition", "profiling", "profiling-control", "remote"]
_ADMIN = _BUILD + ["generic", "profiling", "profiling-control", "remote"]

PROFILES = {
    "listen": _LISTEN,
    "author": _AUTHOR,
    "build": _BUILD,
    "qa": _QA,
    "admin": _ADMIN,
}

PROFILE_NAMES = list(PROFILES)
DEFAULT_PROFILE = "author"


def resolve_profile(name):
    """Return the server names for a profile. Unknown name raises ValueError."""
    if name not in PROFILES:
        raise ValueError(
            f"unknown profile: {name!r}. valid: {', '.join(PROFILE_NAMES)}"
        )
    return list(PROFILES[name])


def mcp_config(name):
    """Per-server .mcp.json content for a profile (run from the repo root)."""
    return {
        "mcpServers": {
            f"sk-wwise-{server}": {
                "command": "uv",
                "args": ["run", "python", "cli.py", "--server", server],
            }
            for server in resolve_profile(name)
        }
    }
