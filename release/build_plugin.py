"""Build sk-wwise-plugin.zip: the Claude plugin that embeds the .mcpb Bundle.

ADR 0001: the release zip is the plugin. Layout of the zip (plugin root at
the top of the archive):

    .claude-plugin/plugin.json      name, description, version, mcpServers
    sk-wwise-mcp.mcpb               the Bundle built by release/build_mcpb.py
    skills/wwise-*/SKILL.md         copied from .claude/skills (wwise-* only)

`plugin.json` points `mcpServers` at the embedded bundle
(`"./sk-wwise-mcp.mcpb"`; Claude Code accepts a `.mcpb` or `.dxt` path there).

This module also produces the marketplace entry for `.claude-plugin/
marketplace.json` at the repo root (an `archive` source at the GitHub release
asset URL). Release CI rewrites that file per tag with
`release/bump_marketplace.py` (a thin wrapper over `write_marketplace`):

    from build_plugin import write_marketplace
    write_marketplace(version, sha256=..., repo="owner/name")

Entry points:

    python release/build_plugin.py [--mcpb sk-wwise-mcp.mcpb]
                                   [--out sk-wwise-plugin.zip]
                                   [--version X] [--write-marketplace]

    from build_plugin import (build_plugin_zip, build_plugin_manifest,
                              marketplace_entry, build_marketplace,
                              write_marketplace)

Only the standard library is needed.
"""

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RELEASE_DIR = Path(__file__).resolve().parent
for _p in (str(REPO_ROOT), str(RELEASE_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from build_mcpb import BUNDLE_NAME, DEFAULT_OUT as DEFAULT_MCPB, _project_version  # noqa: E402

PLUGIN_NAME = BUNDLE_NAME  # plugin.json name == marketplace entry name
MCPB_NAME = f"{BUNDLE_NAME}.mcpb"
MARKETPLACE_NAME = "sk-wwise"
PLUGIN_ZIP_NAME = "sk-wwise-plugin.zip"
DEFAULT_PLUGIN_OUT = REPO_ROOT / PLUGIN_ZIP_NAME
SKILLS_SRC = REPO_ROOT / ".claude" / "skills"
MARKETPLACE_PATH = REPO_ROOT / ".claude-plugin" / "marketplace.json"

GITHUB_REPO = "silver-rain-dev/sk-wwise-mcp"
DESCRIPTION = (
    "Browse and edit a running Wwise project through the Wwise Authoring API "
    "(WAAPI). Bundles the MCP server and the wwise-* routing skills."
)


def build_plugin_manifest(version=None):
    """Return the `.claude-plugin/plugin.json` content as a dict."""
    return {
        "name": PLUGIN_NAME,
        "description": DESCRIPTION,
        "version": version or _project_version(),
        "author": {"name": "silver-rain-dev", "url": "https://github.com/silver-rain-dev"},
        "repository": f"https://github.com/{GITHUB_REPO}",
        "license": "Apache-2.0",
        "keywords": ["wwise", "waapi", "audio", "game-audio"],
        "mcpServers": f"./{MCPB_NAME}",
    }


def release_asset_url(version, repo=GITHUB_REPO):
    """GitHub release asset URL of the plugin zip for `version` (tag `v<version>`)."""
    return (
        f"https://github.com/{repo}/releases/download/"
        f"v{version}/{PLUGIN_ZIP_NAME}"
    )


def marketplace_entry(version=None, sha256=None, repo=GITHUB_REPO):
    """The marketplace.json plugin entry for `version` (an `archive` source).

    `version` and `source.url` always move together. `sha256` (the plugin
    zip's digest, 64 hex chars) is optional: Claude Code refuses a download
    that does not match it. Release CI knows it only after building the zip.
    `repo` is `owner/name` of the GitHub repo that hosts the release.
    """
    version = version or _project_version()
    source = {"source": "archive", "url": release_asset_url(version, repo)}
    if sha256:
        source["sha256"] = sha256.lower()
    return {
        "name": PLUGIN_NAME,
        "description": DESCRIPTION,
        "version": version,
        "source": source,
    }


def build_marketplace(version=None, sha256=None, repo=GITHUB_REPO):
    """The whole `.claude-plugin/marketplace.json` content as a dict."""
    return {
        "name": MARKETPLACE_NAME,
        "description": "Claude plugin for browsing and editing Wwise projects.",
        "owner": {"name": "silver-rain-dev", "url": "https://github.com/silver-rain-dev"},
        "plugins": [marketplace_entry(version, sha256, repo)],
    }


def write_marketplace(version=None, sha256=None, path=MARKETPLACE_PATH, repo=GITHUB_REPO):
    """Write marketplace.json (default: the repo root file). Returns the Path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = build_marketplace(version, sha256, repo)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


# --- validation (documented Claude Code fields; `claude plugin validate` is
# the authority and the tests run it when `claude` is on PATH) ---

_PLUGIN_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")  # kebab-case
_ID_PART_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")  # marketplace / entry names
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _check_relative_path(value, label, errors, suffixes=None):
    if not isinstance(value, str):
        errors.append(f"{label}: must be a string")
        return
    if not value.startswith("./"):
        errors.append(f'{label}: must start with "./": {value}')
    if ".." in value.split("/"):
        errors.append(f'{label}: path contains "..": {value}')
    if suffixes and not value.endswith(suffixes):
        errors.append(f"{label}: must end in {' or '.join(suffixes)}: {value}")


def validate_plugin_manifest(manifest):
    """Return a list of problems with a plugin.json dict (empty when valid)."""
    errors = []
    name = manifest.get("name")
    if not isinstance(name, str) or not _PLUGIN_NAME_RE.match(name):
        errors.append(f"name: must be non-empty kebab-case: {name!r}")
    for field in ("description", "version"):
        if not manifest.get(field):
            errors.append(f"{field}: missing")
    if "mcpServers" in manifest:
        _check_relative_path(
            manifest["mcpServers"], "mcpServers", errors, suffixes=(".mcpb", ".dxt")
        )
    return errors


def validate_marketplace(marketplace, plugin_name=PLUGIN_NAME):
    """Return a list of problems with a marketplace.json dict (empty when valid).

    Every entry's `name` must equal `plugin_name` (the plugin.json name), or
    installs by the manifest name fail with "not found in marketplace".
    """
    errors = []
    name = marketplace.get("name")
    if not isinstance(name, str) or not _ID_PART_RE.match(name) or ".." in name:
        errors.append(f"name: invalid marketplace name: {name!r}")
    owner = marketplace.get("owner")
    if not isinstance(owner, dict) or not owner.get("name"):
        errors.append("owner.name: required")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        errors.append("plugins: must be a non-empty array")
        return errors
    for i, entry in enumerate(plugins):
        label = f"plugins[{i}]"
        if entry.get("name") != plugin_name:
            errors.append(
                f"{label}.name: {entry.get('name')!r} must equal the plugin.json "
                f"name {plugin_name!r}"
            )
        source = entry.get("source")
        if isinstance(source, str):
            _check_relative_path(source, f"{label}.source", errors)
        elif isinstance(source, dict) and source.get("source") == "archive":
            url = source.get("url")
            if not isinstance(url, str) or not url.startswith("https://"):
                errors.append(f"{label}.source.url: must be an https:// URL: {url!r}")
            digest = source.get("sha256")
            if digest is not None and not _SHA256_RE.match(str(digest)):
                errors.append(f"{label}.source.sha256: must be 64 hex characters")
        else:
            errors.append(f"{label}.source: must be a ./ path or an archive source")
    return errors


def wwise_skill_files():
    """(skill name, SKILL.md path) for each wwise-* skill, sorted by name."""
    return sorted(
        (d.name, d / "SKILL.md")
        for d in SKILLS_SRC.iterdir()
        if d.is_dir() and d.name.startswith("wwise-") and (d / "SKILL.md").is_file()
    )


def build_plugin_zip(mcpb_path=DEFAULT_MCPB, out_path=DEFAULT_PLUGIN_OUT, version=None):
    """Pack the plugin around `mcpb_path` into `out_path`. Returns it."""
    mcpb_path = Path(mcpb_path)
    out_path = Path(out_path)
    if not mcpb_path.is_file():
        raise FileNotFoundError(f"bundle not found: {mcpb_path}")
    manifest = build_plugin_manifest(version)
    problems = validate_plugin_manifest(manifest)
    if problems:
        raise ValueError("invalid plugin.json: " + "; ".join(problems))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(".claude-plugin/plugin.json", json.dumps(manifest, indent=2) + "\n")
        # The .mcpb is already compressed; store it as-is.
        z.write(mcpb_path, MCPB_NAME, compress_type=zipfile.ZIP_STORED)
        for name, skill_md in wwise_skill_files():
            z.write(skill_md, f"skills/{name}/SKILL.md")
    return out_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build sk-wwise-plugin.zip")
    parser.add_argument("--mcpb", default=str(DEFAULT_MCPB), help=".mcpb Bundle to embed")
    parser.add_argument("--out", default=str(DEFAULT_PLUGIN_OUT), help="output plugin zip path")
    parser.add_argument("--version", default=None, help="override plugin version")
    parser.add_argument(
        "--write-marketplace",
        action="store_true",
        help="also rewrite marketplace.json for this version, pinned to the zip's sha256",
    )
    parser.add_argument(
        "--marketplace-out",
        default=str(MARKETPLACE_PATH),
        help="marketplace.json path for --write-marketplace",
    )
    args = parser.parse_args(argv)
    out = build_plugin_zip(args.mcpb, args.out, args.version)
    print(f"Plugin:  {out} ({out.stat().st_size / 1024 / 1024:.1f} MB)")
    if args.write_marketplace:
        digest = hashlib.sha256(out.read_bytes()).hexdigest()
        market = write_marketplace(args.version, sha256=digest, path=args.marketplace_out)
        print(f"Market:  {market} (sha256 {digest})")


if __name__ == "__main__":
    main()
