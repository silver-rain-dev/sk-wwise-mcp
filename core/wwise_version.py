"""Wwise version parsing and minimum-supported-version checks.

Centralizes the one knob that everything version-related branches on:
MIN_WWISE_YEAR. The MCP supports Wwise releases from this year onward.

Two surfaces care about version (see CLAUDE.md):
  - Runtime WAAPI: the version is whatever Wwise is *running*. We can't pick
    it, only check it (see core.query.get_wwise_version).
  - WwiseConsole.exe: the version is whichever install we *invoke*. We pick it
    (see core.wwise_cli.resolve_wwise_cli).
"""

import re

# Minimum supported Wwise major release (year). Wwise versions are
# YEAR.MAJOR.MINOR.BUILD, e.g. 2023.1.3.8471.
MIN_WWISE_YEAR = 2022

# Matches a Wwise version anywhere in a string: "2023.1.3", "2023.1.3.8471",
# "v2023.1 Build 8471", "...\Wwise 2022.1.0.7929\...".
_VERSION_RE = re.compile(r"(?<!\d)(\d{4})\.(\d+)(?:\.(\d+))?(?:\.(\d+))?")


def parse_version(text) -> dict | None:
    """Extract a Wwise version dict from any string (path, banner, displayName).

    Returns {"year", "major", "minor", "build", "display"} or None if no
    version-looking token is found.
    """
    if not text:
        return None
    match = _VERSION_RE.search(str(text))
    if not match:
        return None
    year = int(match.group(1))
    major = int(match.group(2))
    minor = int(match.group(3)) if match.group(3) else 0
    build = int(match.group(4)) if match.group(4) else None
    display = f"{year}.{major}.{minor}" + (f".{build}" if build is not None else "")
    return {"year": year, "major": major, "minor": minor, "build": build, "display": display}


def version_sort_key(version: dict | None) -> tuple:
    """Sort key for newest-first ordering. Unknown versions sort lowest."""
    if not version:
        return (0, 0, 0, 0)
    return (version.get("year") or 0, version.get("major") or 0,
            version.get("minor") or 0, version.get("build") or 0)


def support_status(version: dict | None) -> dict:
    """Describe whether a parsed version meets MIN_WWISE_YEAR.

    Returns {"supported": True|False|None, "message": str}. None means the
    version couldn't be determined (treated as "proceed, but unverified").
    """
    if not version or not version.get("year"):
        return {
            "supported": None,
            "message": (
                f"Could not determine the Wwise version. This MCP supports "
                f"Wwise {MIN_WWISE_YEAR} and later."
            ),
        }
    display = version.get("display") or str(version.get("year"))
    if version["year"] >= MIN_WWISE_YEAR:
        return {
            "supported": True,
            "message": f"Wwise {display} is supported (minimum {MIN_WWISE_YEAR}).",
        }
    return {
        "supported": False,
        "message": (
            f"Wwise {display} is below the minimum supported version "
            f"{MIN_WWISE_YEAR}. Some tools may not work as expected."
        ),
    }
