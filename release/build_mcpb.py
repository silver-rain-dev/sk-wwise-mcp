"""Build sk-wwise-mcp.mcpb: the Bundle that wraps the PyInstaller exe.

An .mcpb is a zip with a `manifest.json` at its root (MCP Bundle spec,
https://github.com/modelcontextprotocol/mcpb). This script generates the
manifest from code, so the profile list always comes from the canonical
Profile table in `core/profiles.py`, then zips it with the exe.

Entry points (for build.ps1, the plugin-zip step and release CI):

    python release/build_mcpb.py [--exe dist/sk-wwise-mcp.exe]
                                 [--out sk-wwise-mcp.mcpb]

    from build_mcpb import build_mcpb, build_manifest
    build_mcpb(exe_path, out_path)      # returns the output Path

Only the standard library is needed to build. Tests validate the manifest
against the vendored schema in `release/schema/` (needs `jsonschema`).

User settings (`user_config`):
  profile        required string, default "author" -> `--profile <value>`
  waapi_url      optional string                   -> env SK_WWISE_WAAPI_URL
  wwise_console  optional file path                -> env SK_WWISE_CONSOLE

MCPB `user_config` has no enum type (types: string, number, boolean,
directory, file), so `profile` is a string whose description lists the valid
names. The exe validates it: an unknown or empty profile exits non-zero and
prints the valid names.
"""

import argparse
import json
import re
import sys
import tomllib
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.profiles import DEFAULT_PROFILE, PROFILE_NAMES  # noqa: E402
from core.waapi_util import DEFAULT_WAAPI_URL, WAAPI_URL_ENV  # noqa: E402

# Schema vendored at release/schema/mcpb-manifest-v0.3.schema.json.
MANIFEST_VERSION = "0.3"
BUNDLE_NAME = "sk-wwise-mcp"
EXE_NAME = "sk-wwise-mcp.exe"
ENTRY_POINT = f"server/{EXE_NAME}"
CONSOLE_ENV = "SK_WWISE_CONSOLE"
DEFAULT_EXE = REPO_ROOT / "dist" / EXE_NAME
DEFAULT_OUT = REPO_ROOT / "sk-wwise-mcp.mcpb"


def _project_version():
    with open(REPO_ROOT / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]["version"]


def build_manifest(version=None):
    """Return the manifest.json content as a dict."""
    names = ", ".join(PROFILE_NAMES)
    return {
        "manifest_version": MANIFEST_VERSION,
        "name": BUNDLE_NAME,
        "display_name": "SK Wwise MCP",
        "version": version or _project_version(),
        "description": (
            "Browse and edit a running Wwise project through the Wwise "
            "Authoring API (WAAPI)."
        ),
        "author": {"name": "silver-rain-dev", "url": "https://github.com/silver-rain-dev"},
        "repository": {
            "type": "git",
            "url": "https://github.com/silver-rain-dev/sk-wwise-mcp",
        },
        "license": "Apache-2.0",
        "keywords": ["wwise", "waapi", "audio", "game-audio"],
        "server": {
            "type": "binary",
            "entry_point": ENTRY_POINT,
            "mcp_config": {
                "command": "${__dirname}/" + ENTRY_POINT,
                "args": ["--profile", "${user_config.profile}"],
                "env": {
                    WAAPI_URL_ENV: "${user_config.waapi_url}",
                    CONSOLE_ENV: "${user_config.wwise_console}",
                },
            },
        },
        "tools_generated": True,
        "compatibility": {"platforms": ["win32"]},
        "user_config": {
            "profile": {
                "type": "string",
                "title": "Profile",
                "description": (
                    "Which Wwise tools to load. One of: "
                    f"{names}. Default: {DEFAULT_PROFILE}."
                ),
                "required": True,
                "default": DEFAULT_PROFILE,
            },
            "waapi_url": {
                "type": "string",
                "title": "WAAPI URL",
                "description": (
                    "WebSocket URL of the Wwise Authoring API. Leave as the "
                    "default unless your studio changed the WAAPI port or host."
                ),
                "required": False,
                "default": DEFAULT_WAAPI_URL,
            },
            "wwise_console": {
                "type": "file",
                "title": "WwiseConsole.exe path",
                "description": (
                    "Optional. Full path to a WwiseConsole.exe, to pin a Wwise "
                    "version for command-line tools when several are installed. "
                    "Leave empty to auto-pick the newest install."
                ),
                "required": False,
            },
        },
    }


def profile_names(manifest):
    """The profile names a manifest offers, read back from its description."""
    description = manifest["user_config"]["profile"]["description"]
    listed = description.split("One of:", 1)[1].split(".", 1)[0]
    return [n.strip() for n in listed.split(",")]


def resolve_mcp_config(manifest, install_dir, user_config):
    """Substitute variables the way an MCPB host does (mirrors mcpb's
    `getMcpConfigForManifest`). Returns None when a required setting is empty.

    `user_config` holds the values the user set; defaults are prefilled, as
    the Claude Desktop settings form does. A variable with no value is left as
    its literal `${user_config.<key>}` text, as the reference host does.
    """
    values = {}
    for key, opt in manifest.get("user_config", {}).items():
        if "default" in opt:
            values[key] = opt["default"]
    values.update(user_config)
    for key, opt in manifest.get("user_config", {}).items():
        if opt.get("required") and values.get(key) in (None, ""):
            return None

    variables = {"__dirname": str(install_dir)}
    for key, value in values.items():
        variables[f"user_config.{key}"] = str(value)

    def sub(value):
        if isinstance(value, str):
            return re.sub(
                r"\$\{([^}]+)\}",
                lambda m: variables.get(m.group(1), m.group(0)),
                value,
            )
        if isinstance(value, list):
            return [sub(v) for v in value]
        if isinstance(value, dict):
            return {k: sub(v) for k, v in value.items()}
        return value

    return sub(manifest["server"]["mcp_config"])


def build_mcpb(exe_path=DEFAULT_EXE, out_path=DEFAULT_OUT, version=None):
    """Pack `exe_path` and a generated manifest into `out_path`. Returns it."""
    exe_path = Path(exe_path)
    out_path = Path(out_path)
    if not exe_path.is_file():
        raise FileNotFoundError(f"exe not found: {exe_path}")
    manifest = build_manifest(version)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        z.write(exe_path, ENTRY_POINT)
        license_file = REPO_ROOT / "LICENSE"
        if license_file.is_file():
            z.write(license_file, "LICENSE")
    return out_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build sk-wwise-mcp.mcpb")
    parser.add_argument("--exe", default=str(DEFAULT_EXE), help="PyInstaller exe to pack")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="output .mcpb path")
    parser.add_argument("--version", default=None, help="override bundle version")
    args = parser.parse_args(argv)
    out = build_mcpb(args.exe, args.out, args.version)
    print(f"Bundle:  {out} ({out.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
