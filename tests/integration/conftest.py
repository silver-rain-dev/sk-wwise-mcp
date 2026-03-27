"""Integration test fixtures.

Starts a headless WwiseConsole WAAPI server with the test project,
waits for connectivity, and tears down after all tests complete.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from waapi import WaapiClient, CannotConnectToWaapiException

# Resolve paths relative to this file
_TESTS_DIR = Path(__file__).parent.parent
_PROJECT_DIR = _TESTS_DIR / "test_project" / "TestProject"
_PROJECT_FILE = _PROJECT_DIR / "TestProject.wproj"


def _find_wwise_console() -> str:
    """Find the WwiseConsole executable."""
    # Check WWISEROOT env var first
    wwiseroot = os.environ.get("WWISEROOT")
    if wwiseroot:
        candidate = Path(wwiseroot) / "Authoring" / "x64" / "Release" / "bin" / "WwiseConsole.exe"
        if candidate.exists():
            return str(candidate)

    # Common install paths on Windows
    base = Path(r"C:\Program Files (x86)\Audiokinetic")
    if base.exists():
        # Find newest Wwise version
        versions = sorted(base.glob("Wwise*/"), reverse=True)
        for v in versions:
            candidate = v / "Authoring" / "x64" / "Release" / "bin" / "WwiseConsole.exe"
            if candidate.exists():
                return str(candidate)

    pytest.skip("WwiseConsole not found. Set WWISEROOT or install Wwise.")


@pytest.fixture(scope="session")
def waapi_server():
    """Start a headless WAAPI server for the test project.

    Yields the subprocess.Popen process. Kills on teardown.
    Skips all tests if WwiseConsole is not available or the test project is missing.
    """
    if not _PROJECT_FILE.exists():
        pytest.skip(f"Test project not found at {_PROJECT_FILE}. Run the test project setup first.")

    # Kill any existing WwiseConsole to free port 8080
    if sys.platform == "win32":
        subprocess.call(["taskkill", "/IM", "WwiseConsole.exe", "/F"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    cli = _find_wwise_console()
    proc = subprocess.Popen(
        [cli, "waapi-server", str(_PROJECT_FILE), "--allow-migration"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for WAAPI to become available
    for attempt in range(10):
        time.sleep(2)
        try:
            client = WaapiClient()
            result = client.call("ak.wwise.core.ping")
            client.disconnect()
            if result and result.get("isAvailable"):
                break
        except (CannotConnectToWaapiException, Exception):
            pass
    else:
        proc.terminate()
        proc.wait(timeout=5)
        pytest.skip("WAAPI server failed to start within 20 seconds.")

    yield proc

    # Teardown
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(scope="session")
def wwise(waapi_server):
    """Provide a connected WaapiClient for the test session.

    Depends on waapi_server to ensure the server is running.
    Cleans up any leftover IntTest* objects before yielding.
    """
    client = WaapiClient()

    # Delete any leftover objects from previous failed test runs
    leftovers = client.call("ak.wwise.core.object.get", {
        "from": {"path": ["\\Containers\\Default Work Unit"]},
        "transform": [
            {"select": ["children"]},
            {"where": ["name:matches", "^IntTest"]},
        ],
    }, options={"return": ["id", "name"]})
    for obj in (leftovers or {}).get("return", []):
        client.call("ak.wwise.core.object.delete", {"object": obj["id"]})

    yield client
    client.disconnect()
