import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from waapi import CannotConnectToWaapiException
from mcp_generic.server import list_waapi_functions, get_waapi_function_schema, call_waapi


@patch("mcp_generic.server.get_waapi_availiable_functions")
def test_list_waapi_functions(mock_fn):
    mock_fn.return_value = {"functions": ["ak.wwise.core.getInfo"]}
    result = list_waapi_functions()
    assert "ak.wwise.core.getInfo" in result["functions"]


@patch("mcp_generic.server.get_waapi_schema")
def test_get_waapi_function_schema(mock_fn):
    mock_fn.return_value = {"uri": "ak.wwise.core.getInfo", "args": {}}
    result = get_waapi_function_schema("ak.wwise.core.getInfo")
    assert result["uri"] == "ak.wwise.core.getInfo"


@patch("mcp_generic.server.call")
def test_call_waapi_success(mock_call):
    mock_call.return_value = {"return": []}
    result = call_waapi("ak.wwise.core.object.get", {"from": {"path": ["\\Events"]}}, {"return": ["name"]})
    assert result == {"return": []}
    mock_call.assert_called_once_with("ak.wwise.core.object.get", {"from": {"path": ["\\Events"]}}, {"return": ["name"]})
