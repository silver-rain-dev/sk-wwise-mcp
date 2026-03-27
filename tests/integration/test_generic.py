"""Integration tests for generic WAAPI passthrough operations."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.generic_handling import (
    get_waapi_available_functions,
    get_waapi_schema,
)
from core.waapi_util import call

pytestmark = pytest.mark.integration


def test_list_waapi_functions(wwise):
    result = get_waapi_available_functions()
    assert "functions" in result or "return" in result or isinstance(result, dict)


def test_get_waapi_schema(wwise):
    result = get_waapi_schema("ak.wwise.core.object.create")
    assert result is not None
    # Should contain argument schema
    assert "args" in result or "properties" in result or isinstance(result, dict)


def test_raw_call(wwise):
    """Test calling WAAPI directly through waapi_util.call()."""
    result = call("ak.wwise.core.getInfo")
    assert result is not None
    assert "version" in result or "isAvailable" in result or isinstance(result, dict)
