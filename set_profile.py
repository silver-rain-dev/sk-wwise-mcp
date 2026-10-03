"""Switch MCP server access profile.

Usage:
    python set_profile.py <profile>
    python set_profile.py --regenerate    # rewrite profiles/*.mcp.json from the table

Profiles (defined in core/profiles.py):
    listen - browse, audition, media-read
    author - listen + objects, containers, pipeline, ui
    build  - author + command-line
    qa     - browse, audition, profiling, profiling-control, remote
    admin  - all 12 servers

Old names: viewer -> listen, designer -> listen, editor -> author.
"""

import json
import shutil
import sys
from pathlib import Path

from core.profiles import PROFILE_NAMES, mcp_config

PROFILES_DIR = Path(__file__).parent / "profiles"
TARGET = Path(__file__).parent / ".mcp.json"
VALID_PROFILES = PROFILE_NAMES
RENAMED = {"viewer": "listen", "designer": "listen", "editor": "author"}


def regenerate():
    PROFILES_DIR.mkdir(exist_ok=True)
    for name in PROFILE_NAMES:
        path = PROFILES_DIR / f"{name}.mcp.json"
        text = json.dumps(mcp_config(name), indent=2) + "\n"
        path.write_bytes(text.encode("utf-8"))  # LF on every platform
        print(f"Wrote {path}")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--regenerate":
        regenerate()
        return

    if len(sys.argv) != 2 or sys.argv[1] not in VALID_PROFILES:
        if len(sys.argv) == 2 and sys.argv[1] in RENAMED:
            print(
                f"'{sys.argv[1]}' was renamed. Use '{RENAMED[sys.argv[1]]}' "
                f"(valid: {', '.join(VALID_PROFILES)})."
            )
        else:
            print(f"Usage: python set_profile.py <{'|'.join(VALID_PROFILES)}>")
        sys.exit(1)

    profile = sys.argv[1]
    source = PROFILES_DIR / f"{profile}.mcp.json"

    if not source.exists():
        print(f"Error: Profile '{profile}' not found at {source}")
        sys.exit(1)

    shutil.copy2(source, TARGET)
    print(f"Switched to '{profile}' profile -> {TARGET}")


if __name__ == "__main__":
    main()
