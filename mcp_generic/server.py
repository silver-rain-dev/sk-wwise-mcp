import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.generic_handling import get_waapi_availiable_functions, get_waapi_schema
from core.waapi_util import call


mcp = FastMCP(name = "SK Wwise MCP Generic")

@mcp.tool
def list_waapi_functions():
    """List all available WAAPI functions."""
    return get_waapi_availiable_functions()

@mcp.tool
def get_waapi_function_schema(function_name: str):
    """Get the argument/option schema for a WAAPI function."""
    return get_waapi_schema(function_name)

@mcp.tool
def  call_waapi(function_name, args: dict = {}, options: dict = {}):
    """Execute any WAAPI function with the given args and options."""
    return call(function_name, args, options)

if __name__ == "__main__":
    mcp.run(transport="stdio")