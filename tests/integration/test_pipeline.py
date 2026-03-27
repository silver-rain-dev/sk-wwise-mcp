"""Integration tests for pipeline operations (save, import, soundbanks)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.pipeline import (
    save_project,
    get_log,
)

pytestmark = pytest.mark.integration


def test_save_project(wwise):
    # Note: we call save but this persists whatever state exists.
    # The test project may have been mutated by other tests.
    # This only tests that the WAAPI call succeeds, not the saved state.
    result = save_project()
    assert result is not None  # Returns {} on success


def test_get_log(wwise):
    result = get_log({"channel": "general"})
    assert result is not None
