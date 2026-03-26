import threading
from queue import Queue, Full

from waapi import WaapiClient, CannotConnectToWaapiException


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

    def __init__(self, maxsize=10000):
        self._client: WaapiClient | None = None
        self._queue: Queue = Queue(maxsize=maxsize)
        self._ready = threading.Event()
        self._connect_error: Exception | None = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._ready.wait()
        if self._connect_error:
            raise self._connect_error

    def _run(self):
        """Worker thread: create client, then process call queue forever."""
        try:
            self._client = WaapiClient()
        except Exception as e:
            self._connect_error = e
            self._ready.set()
            return
        self._ready.set()

        while True:
            args, result_event, result_holder = self._queue.get()
            try:
                uri, payload = args
                result_holder["result"] = self._client.call(uri, payload)
            except Exception as e:
                result_holder["error"] = e
            result_event.set()

    def call(self, uri: str, payload: dict):
        result_holder = {}
        event = threading.Event()
        try:
            self._queue.put(((uri, payload), event, result_holder), block=False)
        except Full:
            raise WaapiQueueFullError("WAAPI dispatch queue is full")
        event.wait()
        if "error" in result_holder:
            raise result_holder["error"]
        return result_holder["result"]

    def is_connected(self) -> bool:
        return self._client is not None and self._client.is_connected()

    def disconnect(self):
        if self._client is not None:
            try:
                self._client.disconnect()
            except Exception:
                pass


_dispatcher: WaapiDispatcher | None = None
_lock = threading.Lock()


def get_dispatcher() -> WaapiDispatcher:
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


def ping() -> dict:
    """Check if WAAPI is available. Returns {"isAvailable": bool}."""
    try:
        return get_dispatcher().call("ak.wwise.core.ping", {})
    except Exception:
        return {"isAvailable": False}


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


def call(uri: str, args: dict = {}, options: dict = {}) -> dict:
    args = _normalize_paths(args)
    if options:
        payload = {**args, "options": _normalize_paths(options)}
    else:
        payload = args

    result = get_dispatcher().call(uri, payload)
    if result is None:
        _reconnect()
        result = get_dispatcher().call(uri, payload)
    return result
