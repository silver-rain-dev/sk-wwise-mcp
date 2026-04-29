"""Unified entry point for all SK Wwise MCP servers.

One executable, dispatched by --server. Used by both `python cli.py` and the
PyInstaller-built `sk-wwise-mcp.exe`.

Example:
    python cli.py --server browse
    sk-wwise-mcp.exe --server audition
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


def main():
    parser = argparse.ArgumentParser(
        prog="sk-wwise-mcp",
        description="SK Wwise MCP server dispatcher.",
    )
    parser.add_argument(
        "--server",
        required=True,
        choices=sorted(SERVERS),
        help="Which MCP server to launch on stdio.",
    )
    args = parser.parse_args()

    module = importlib.import_module(SERVERS[args.server])
    module.mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
