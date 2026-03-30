import json
import os
import subprocess
import time
import threading
from pathlib import Path
from queue import Queue, Full

from waapi import WaapiClient, CannotConnectToWaapiException

_LOCKFILE = Path(__file__).parent.parent / ".waapi_server.lock"


class WaapiQueueFullError(Exception):
    pass


class WaapiDispatcher:
    """Thread-safe WAAPI dispatcher.

    All WaapiClient interactions (construction + calls) happen on a single
    dedicated thread. This avoids asyncio event loop conflicts:

    - fastmcp/anyio runs its own event loop on the main thread
    - WaapiClient creates a ProactorEventLoop internally
    - WaapiClient.call() binds asyncio.Future to the thread's current loop
    - If called from different AnyIO worker threads, the Future gets attached
      to the wrong loop → "Future attached to a different loop" error

    By pinning all WAAPI work to one persistent thread, the event loop context
    stays consistent across calls.
    """

    def __init__(self, client=None, maxsize=10000):
        self._client = client
        self._queue: Queue = Queue(maxsize=maxsize)
        self._ready = threading.Event()
        self._connect_error: Exception | None = None
        self._abandoned = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        if not self._ready.wait(timeout=15):
            raise CannotConnectToWaapiException(
                "Timed out waiting for WAAPI client to initialize"
            )
        if self._connect_error:
            raise self._connect_error

    def _run(self):
        """Worker thread: create client (if not injected), then process queue."""
        if self._client is None:
            try:
                self._client = WaapiClient()
            except Exception as e:
                self._connect_error = e
                self._ready.set()
                return
        self._ready.set()

        while True:
            args, result_event, result_holder = self._queue.get()
            if args is None:
                # Poison pill — shut down the worker
                result_event.set()
                break
            try:
                uri, payload = args
                result_holder["result"] = self._client.call(uri, payload)
            except Exception as e:
                result_holder["error"] = e
            result_event.set()

    def call(self, uri: str, payload: dict, timeout: float = 30):
        if self._abandoned:
            raise CannotConnectToWaapiException(
                "Dispatcher was abandoned after a timed-out call"
            )
        result_holder = {}
        event = threading.Event()
        try:
            self._queue.put(((uri, payload), event, result_holder), block=False)
        except Full:
            raise WaapiQueueFullError("WAAPI dispatch queue is full")
        if not event.wait(timeout=timeout):
            # The worker thread is stuck on a hung WaapiClient.call().
            # WaapiClient.disconnect() does NOT unblock a hung call, so
            # we mark this dispatcher as abandoned.  The module-level
            # _reconnect() will create a fresh dispatcher with a new
            # client and thread.  The old daemon thread will leak but
            # won't block process exit.
            self._abandoned = True
            try:
                self._client.disconnect()
            except Exception:
                pass
            raise TimeoutError(f"WAAPI call timed out after {timeout} seconds")
        if "error" in result_holder:
            raise result_holder["error"]
        return result_holder["result"]

    def is_connected(self) -> bool:
        if self._abandoned:
            return False
        return self._client is not None and self._client.is_connected()

    def disconnect(self):
        if self._client is not None:
            try:
                self._client.disconnect()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------

_dispatcher: WaapiDispatcher | None = None
_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Headless server management (file-based, cross-process)
# ---------------------------------------------------------------------------

def write_server_lockfile(pid: int, project_path: str):
    """Write a lockfile so any MCP server process can auto-restart the WAAPI server.

    Called by cli_start_waapi_server after starting a headless server.
    """
    _LOCKFILE.write_text(json.dumps({
        "pid": pid,
        "project_path": project_path,
    }), encoding="utf-8")


def _read_server_lockfile() -> dict | None:
    """Read the headless server lockfile. Returns None if absent or invalid."""
    try:
        if _LOCKFILE.exists():
            return json.loads(_LOCKFILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def _is_process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def _kill_process(pid: int):
    try:
        if os.name == "nt":
            subprocess.call(
                ["taskkill", "/PID", str(int(pid)), "/F"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        else:
            os.kill(int(pid), 9)  # SIGKILL
    except Exception:
        pass


def _restart_headless_server() -> bool:
    """Restart the headless WAAPI server using info from the lockfile.

    Returns True if server was restarted successfully.
    """
    lock = _read_server_lockfile()
    if lock is None:
        return False

    project_path = lock.get("project_path")
    old_pid = lock.get("pid")
    if not project_path:
        return False

    # Kill the old process if still alive
    if old_pid and _is_process_alive(old_pid):
        _kill_process(old_pid)
        time.sleep(2)

    # Start a new one
    try:
        from core.wwise_cli import start_waapi_server
        result = start_waapi_server(
            project_path=project_path,
            allow_migration=True,
        )
        if result.get("success"):
            write_server_lockfile(pid=result["pid"], project_path=project_path)
            time.sleep(5)  # Give the server time to initialize
            return True
    except Exception:
        pass
    return False


# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------

def _get_dispatcher() -> WaapiDispatcher:
    global _dispatcher
    with _lock:
        if _dispatcher is None or not _dispatcher.is_connected():
            if _dispatcher is not None:
                _dispatcher.disconnect()
            _dispatcher = WaapiDispatcher()
    return _dispatcher


def _reconnect():
    """Force a fresh WAAPI connection and dispatcher."""
    global _dispatcher
    with _lock:
        if _dispatcher is not None:
            _dispatcher.disconnect()
        _dispatcher = None


def _ensure_connection(max_retries: int = 3, base_delay: float = 1.0) -> WaapiDispatcher:
    """Get a working dispatcher, reconnecting or restarting server if needed.

    Strategy:
    1. Get dispatcher — if connected, ping to verify it's alive
    2. If ping fails, close stale connection and reconnect with backoff
    3. If reconnect fails and we started the headless server, restart it
    4. If nothing works, raise CannotConnectToWaapiException

    Args:
        max_retries: Number of reconnect attempts before giving up.
        base_delay: Initial delay in seconds between retries (doubles each attempt).
    """
    # Step 1: try existing connection
    try:
        dispatcher = _get_dispatcher()
        result = dispatcher.call("ak.wwise.core.ping", {})
        if result and result.get("isAvailable"):
            return dispatcher
    except Exception:
        pass

    # Step 2: close stale connection and reconnect with backoff retries
    for attempt in range(max_retries):
        delay = base_delay * (2 ** attempt)
        _reconnect()
        time.sleep(delay)
        try:
            dispatcher = _get_dispatcher()
            result = dispatcher.call("ak.wwise.core.ping", {})
            if result and result.get("isAvailable"):
                return dispatcher
        except Exception:
            pass

    # Step 3: restart headless server if we have a lockfile
    if _read_server_lockfile() is not None:
        _reconnect()
        if _restart_headless_server():
            try:
                dispatcher = _get_dispatcher()
                result = dispatcher.call("ak.wwise.core.ping", {})
                if result and result.get("isAvailable"):
                    return dispatcher
            except Exception:
                pass

    raise CannotConnectToWaapiException(
        "Could not connect to WAAPI. Is Wwise running with the Authoring API enabled?"
    )


# ---------------------------------------------------------------------------
# Path normalization
# ---------------------------------------------------------------------------

def _normalize_paths(d: dict) -> dict:
    """Normalize double-backslash paths to single-backslash for WAAPI.

    MCP clients may send Wwise paths with escaped backslashes (e.g.
    '\\\\Containers\\\\Default Work Unit') which WAAPI rejects. This
    normalizes them to single backslashes.
    """
    result = {}
    for k, v in d.items():
        if isinstance(v, str) and "\\\\" in v:
            v = v.replace("\\\\", "\\")
        elif isinstance(v, dict):
            v = _normalize_paths(v)
        elif isinstance(v, list):
            v = [_normalize_paths(i) if isinstance(i, dict) else
                 i.replace("\\\\", "\\") if isinstance(i, str) and "\\\\" in i else i
                 for i in v]
        result[k] = v
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ping() -> dict:
    """Check if WAAPI is available. Returns {"isAvailable": bool}."""
    try:
        dispatcher = _get_dispatcher()
        return dispatcher.call("ak.wwise.core.ping", {})
    except Exception:
        return {"isAvailable": False}


def call(uri: str, args: dict = None, options: dict = None, timeout: float = 30) -> dict:
    """Execute a WAAPI call with automatic connection recovery.

    Pings WAAPI before calling. If the connection is dead, attempts to
    reconnect the client. If that fails and a headless server was
    registered, restarts the server automatically.

    Args:
        timeout: Max seconds to wait for the WAAPI call to complete.
                 Use higher values for long operations (import, soundbank gen).
    """
    args = _normalize_paths(args or {})
    options = options or {}
    if options:
        payload = {**args, "options": _normalize_paths(options)}
    else:
        payload = args

    dispatcher = _ensure_connection()
    try:
        return dispatcher.call(uri, payload, timeout=timeout)
    except TimeoutError:
        # The worker thread is stuck on the hung call — tear down the
        # dispatcher so the next call gets a fresh connection instead
        # of queuing behind a blocked worker.
        _reconnect()
        raise
    except WaapiQueueFullError:
        raise
    except Exception:
        # Connection may have died between the ping and the actual call.
        # Reconnect and retry once before giving up.
        _reconnect()
        dispatcher = _ensure_connection()
        return dispatcher.call(uri, payload, timeout=timeout)
