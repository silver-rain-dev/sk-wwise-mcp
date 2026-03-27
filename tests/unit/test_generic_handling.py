import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.generic_handling import get_waapi_available_functions, get_waapi_schema


@patch("core.generic_handling.call")
def test_get_functions(mock_call):
    mock_call.return_value = {"functions": ["ak.wwise.core.getInfo", "ak.wwise.core.object.get"]}
    result = get_waapi_available_functions()
    assert "ak.wwise.core.getInfo" in result["functions"]
    mock_call.assert_called_once_with("ak.wwise.waapi.getFunctions")


@patch("core.generic_handling.call")
def test_get_schema(mock_call):
    mock_call.return_value = {"uri": "ak.wwise.core.getInfo", "args": {}, "options": {}}
    result = get_waapi_schema("ak.wwise.core.getInfo")
    assert result["uri"] == "ak.wwise.core.getInfo"
    mock_call.assert_called_once_with("ak.wwise.waapi.getSchema", {"uri": "ak.wwise.core.getInfo"})
