"""Unified entry point for all SK Wwise MCP servers.

One executable, dispatched by --server. Used by both `python cli.py` and the
PyInstaller-built `sk-wwise-mcp.exe`.

Omit --server to mount every server's tools on a single FastMCP instance
(the "all-in-one" config); pass --server <name> (or a comma-separated list)
to expose only those. The shipped .mcp.json registers one entry per server
(better tool-routing accuracy); .mcp.all-in-one.json uses the no-flag form.

Examples:
    python cli.py --server browse
    sk-wwise-mcp.exe --server audition
    sk-wwise-mcp.exe --server browse,objects
    sk-wwise-mcp.exe                       # all 12 servers on one instance
"""

import argparse
import importlib
import sys

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


def main():
    parser = argparse.ArgumentParser(
        prog="sk-wwise-mcp",
        description=(
            "SK Wwise MCP server dispatcher. Omit --server to mount every "
            "server's tools on one instance; pass --server <name> (or a "
            "comma-separated list) to expose only those."
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
    names = _resolve_servers(args.server)

    # Single-server fast path: run the underlying instance directly. Skips the
    # mount layer and keeps the more specific sk-wwise-<name> server identity.
    if len(names) == 1:
        module = importlib.import_module(SERVERS[names[0]])
        module.mcp.run(transport="stdio")
        return

    # All / multi-server path: mount each child into a master instance.
    from fastmcp import FastMCP

    master = FastMCP("sk-wwise")
    for name in names:
        module = importlib.import_module(SERVERS[name])
        master.mount(module.mcp)
    master.run(transport="stdio")


if __name__ == "__main__":
    main()
