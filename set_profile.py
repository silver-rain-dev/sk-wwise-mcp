"""Switch MCP server access profile.

Usage:
    python set_profile.py <profile>

Profiles:
    viewer   - Browse only (read-only access)
    designer - Browse + audition (playback)
    editor   - Browse + audition + object modification
    admin    - Full access to all servers
"""

import shutil
import sys
from pathlib import Path

PROFILES_DIR = Path(__file__).parent / "profiles"
TARGET = Path(__file__).parent / ".mcp.json"
VALID_PROFILES = ["viewer", "designer", "editor", "admin"]


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in VALID_PROFILES:
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
