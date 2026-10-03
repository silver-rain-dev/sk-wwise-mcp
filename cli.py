"""Unified entry point for all SK Wwise MCP servers.

One executable, dispatched by --server. Used by both `python cli.py` and the
PyInstaller-built `sk-wwise-mcp.exe`.

Omit --server to mount every server's tools on a single FastMCP instance
(the "all-in-one" config); pass --server <name> (or a comma-separated list)
to expose only those, or --profile <name> to mount a profile's servers
(listen, author, build, qa, admin; see core/profiles.py). The shipped .mcp.json registers one entry per server
(better tool-routing accuracy); .mcp.all-in-one.json uses the no-flag form.

Examples:
    python cli.py --server browse
    sk-wwise-mcp.exe --server audition
    sk-wwise-mcp.exe --server browse,objects
    sk-wwise-mcp.exe --profile author      # servers of the author profile
    sk-wwise-mcp.exe                       # all 12 servers on one instance
"""

import argparse
import importlib
import sys

from core.instructions import build_instructions
from core.profiles import PROFILE_NAMES, resolve_profile

SERVERS = {
    "browse":             "mcp_browse.server",
    "audition":           "mcp_audition.server",
    "objects":            "mcp_objects.server",
    "containers":         "mcp_containers.server",
    "pipeline":           "mcp_pipeline.server",
    "generic":            "mcp_generic.server",
    "media-read":         "mcp_media_read.server",
    "profiling":          "mcp_profiling.server",
    "profiling-control":  "mcp_profiling_control.server",
    "command-line":       "mcp_command_line.server",
    "remote":             "mcp_remote.server",
    "ui":                 "mcp_ui.server",
}


def _resolve_servers(spec):
    """Map a --server value (None, one name, or comma list) to server keys."""
    if not spec:
        return list(SERVERS)
    names = [n.strip() for n in spec.split(",") if n.strip()]
    unknown = [n for n in names if n not in SERVERS]
    if unknown:
        raise SystemExit(
            f"unknown server(s): {', '.join(unknown)}. "
            f"valid: {', '.join(sorted(SERVERS))}"
        )
    if not names:
        raise SystemExit("--server was given an empty value")
    return names


def _resolve_selection(server_spec, profile):
    """Map --server / --profile to server keys. The two are mutually exclusive."""
    if profile is not None and server_spec:
        raise SystemExit("--profile and --server cannot be used together")
    if profile is not None:
        try:
            return resolve_profile(profile)
        except ValueError as e:
            raise SystemExit(str(e))
    return _resolve_servers(server_spec)


def main():
    parser = argparse.ArgumentParser(
        prog="sk-wwise-mcp",
        description=(
            "SK Wwise MCP server dispatcher. Omit --server and --profile to "
            "mount every server's tools on one instance; pass --server <name> "
            "(or a comma-separated list) to expose only those, or --profile "
            "<name> to mount a named role's servers."
        ),
    )
    parser.add_argument(
        "--profile",
        help=(
            "Mount the servers of a profile: "
            + ", ".join(PROFILE_NAMES)
            + ". Cannot be combined with --server."
        ),
    )
    parser.add_argument(
        "--server",
        help=(
            "Comma-separated server names from: "
            + ", ".join(sorted(SERVERS))
            + ". Omit to enable all."
        ),
    )
    args = parser.parse_args()
    names = _resolve_selection(args.server, args.profile)

    _build_server(names).run(transport="stdio")


def _build_server(names):
    """Return the FastMCP instance to run for these server keys.

    Both paths send routing guidance (MCP instructions) built from exactly the
    servers mounted; see core/instructions.py.
    """
    instructions = build_instructions(names)

    # Single-server fast path: run the underlying instance directly. Skips the
    # mount layer and keeps the more specific sk-wwise-<name> server identity.
    if len(names) == 1:
        module = importlib.import_module(SERVERS[names[0]])
        module.mcp.instructions = instructions
        return module.mcp

    # All / multi-server path: mount each child into a master instance.
    from fastmcp import FastMCP

    master = FastMCP("sk-wwise", instructions=instructions)
    for name in names:
        module = importlib.import_module(SERVERS[name])
        master.mount(module.mcp)
    return master


if __name__ == "__main__":
    main()
