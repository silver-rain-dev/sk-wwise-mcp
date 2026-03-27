#!/usr/bin/env python3
"""Setup script for SK Wwise MCP servers.

Detects paths, installs dependencies, and generates MCP configuration.
Works on Windows, macOS, and Linux.
"""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.resolve()
VENV_DIR = PROJECT_DIR / ".venv"

SERVERS = {
    "sk-wwise-browse": "mcp_browse/server.py",
    "sk-wwise-objects": "mcp_objects/server.py",
    "sk-wwise-containers": "mcp_containers/server.py",
    "sk-wwise-pipeline": "mcp_pipeline/server.py",
    "sk-wwise-audition": "mcp_audition/server.py",
    "sk-wwise-media-read": "mcp_media_read/server.py",
    "sk-wwise-ui": "mcp_ui/server.py",
    "sk-wwise-profiling": "mcp_profiling/server.py",
    "sk-wwise-profiling-control": "mcp_profiling_control/server.py",
    "sk-wwise-remote": "mcp_remote/server.py",
    "sk-wwise-command-line": "mcp_command_line/server.py",
    "sk-wwise-generic": "mcp_generic/server.py",
}


def get_python_path() -> str:
    """Get the venv Python executable path."""
    if platform.system() == "Windows":
        return str(VENV_DIR / "Scripts" / "python.exe")
    else:
        return str(VENV_DIR / "bin" / "python")


def check_uv() -> bool:
    """Check if uv is installed."""
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def install_dependencies():
    """Install project dependencies."""
    print("\n[2/4] Installing dependencies...")
    if check_uv():
        subprocess.run(["uv", "sync"], cwd=str(PROJECT_DIR), check=True)
    else:
        print("  uv not found, falling back to pip...")
        if not VENV_DIR.exists():
            subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        pip = str(VENV_DIR / ("Scripts" if platform.system() == "Windows" else "bin") / "pip")
        subprocess.run([pip, "install", "-e", "."], cwd=str(PROJECT_DIR), check=True)
    print("  Done.")


def select_servers() -> dict:
    """Let user choose which servers to enable."""
    print("\n[3/4] Select servers to enable:\n")
    print("  0) ALL servers (recommended)")
    for i, (name, _) in enumerate(SERVERS.items(), 1):
        print(f"  {i}) {name}")

    choice = input("\nEnter numbers separated by commas (e.g. 1,2,3) or 0 for all: ").strip()

    if choice == "0" or choice == "":
        return SERVERS

    selected = {}
    for num in choice.split(","):
        num = num.strip()
        if num.isdigit():
            idx = int(num)
            if 1 <= idx <= len(SERVERS):
                name = list(SERVERS.keys())[idx - 1]
                selected[name] = SERVERS[name]

    if not selected:
        print("  No valid selection, enabling all servers.")
        return SERVERS

    return selected


def generate_config(selected_servers: dict) -> dict:
    """Generate MCP server configuration."""
    python_path = get_python_path().replace("\\", "/")
    config = {"mcpServers": {}}

    for name, script in selected_servers.items():
        script_path = str(PROJECT_DIR / script).replace("\\", "/")
        config["mcpServers"][name] = {
            "command": python_path,
            "args": [script_path],
        }

    return config


def save_config(config: dict):
    """Save configuration to chosen location."""
    print("\n[4/4] Where to save the MCP configuration?\n")
    print("  1) .mcp.json in current working directory (project-scoped)")
    print("  2) .mcp.json in the sk-wwise-mcp repo (for development)")
    print("  3) Print to console (copy manually)")

    choice = input("\nChoice [1]: ").strip() or "1"

    if choice == "1":
        out_path = Path.cwd() / ".mcp.json"
    elif choice == "2":
        out_path = PROJECT_DIR.parent / ".mcp.json"
    elif choice == "3":
        print("\n--- Copy this into your .mcp.json ---\n")
        print(json.dumps(config, indent=2))
        print("\n--- End ---")
        return
    else:
        out_path = Path.cwd() / ".mcp.json"

    # Merge with existing config if present
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text(encoding="utf-8"))
            if "mcpServers" in existing:
                existing["mcpServers"].update(config["mcpServers"])
                config = existing
        except (json.JSONDecodeError, KeyError):
            pass

    out_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"\n  Saved to: {out_path}")


def main():
    print("=" * 50)
    print("  SK Wwise MCP — Setup")
    print("=" * 50)

    print(f"\n[1/4] Project directory: {PROJECT_DIR}")
    print(f"  Platform: {platform.system()}")
    print(f"  Python: {sys.version.split()[0]}")

    install_dependencies()
    selected = select_servers()
    config = generate_config(selected)
    save_config(config)

    print("\n" + "=" * 50)
    print("  Setup complete!")
    print("=" * 50)
    print(f"\n  Enabled {len(config['mcpServers'])} MCP server(s).")
    print("  Restart Claude Code / your agent to connect.\n")


if __name__ == "__main__":
    main()
