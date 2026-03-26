import sys
import json
import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.generic_handling import get_waapi_availiable_functions, get_waapi_schema
from core.waapi_util import call

LOG_FILE = Path(__file__).parent.parent / "generic_usage.log"

mcp = FastMCP(name = "SK Wwise MCP Generic")


def _log_generic_usage(tool_name: str, **kwargs):
    """Log every generic server tool call for analysis."""
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tool": tool_name,
        **kwargs,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


@mcp.tool
def list_waapi_functions():
    """List all available WAAPI functions."""
    _log_generic_usage("list_waapi_functions")
    return get_waapi_availiable_functions()

@mcp.tool
def get_waapi_function_schema(function_name: str):
    """Get the argument/option schema for a WAAPI function."""
    _log_generic_usage("get_waapi_function_schema", function_name=function_name)
    return get_waapi_schema(function_name)

@mcp.tool
def call_waapi(function_name, args: dict = {}, options: dict = {}):
    """Execute any WAAPI function with the given args and options."""
    _log_generic_usage("call_waapi", function_name=function_name, args=args, options=options)
    return call(function_name, args, options)

if __name__ == "__main__":
    mcp.run(transport="stdio")