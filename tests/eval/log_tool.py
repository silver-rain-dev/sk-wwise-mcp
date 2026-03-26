"""PostToolUse hook script that logs MCP tool calls to tool_log.jsonl.

Called by Claude Code after every MCP tool use. Reads hook event JSON
from stdin, extracts tool name and input, appends to log file.
"""

import json
import sys
from pathlib import Path

LOG_FILE = Path(__file__).parent / "tool_log.jsonl"


def main():
    try:
        event = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = event.get("tool_name", "")

    # Only log MCP tool calls (prefixed with mcp__)
    if not tool_name.startswith("mcp__"):
        sys.exit(0)

    entry = {
        "tool": tool_name,
        "input": event.get("tool_input", {}),
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
