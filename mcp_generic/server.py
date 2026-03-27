import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from core.generic_handling import get_waapi_available_functions, get_waapi_schema
from core.waapi_util import call
from waapi import CannotConnectToWaapiException


mcp = FastMCP(name="SK Wwise MCP Generic")


@mcp.tool()
def list_waapi_functions():
    """List all available WAAPI functions."""
    try:
        return get_waapi_available_functions()
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def get_waapi_function_schema(function_name: str):
    """Get the argument/option schema for a WAAPI function."""
    try:
        return get_waapi_schema(function_name)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


@mcp.tool()
def call_waapi(function_name, args: dict = None, options: dict = None):
    """Execute any WAAPI function with the given args and options."""
    try:
        return call(function_name, args, options)
    except CannotConnectToWaapiException:
        return {"error": "Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
