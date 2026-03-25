import threading
from queue import Queue, Full

from waapi import WaapiClient, CannotConnectToWaapiException

_client: WaapiClient | None = None


class WaapiQueueFullError(Exception):
    pass


class WaapiDispatcher:
    def __init__(self, client, maxsize=10000):
        self._client = client
        self._queue = Queue(maxsize=maxsize)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while True:
            args, kwargs, result_event, result_holder = self._queue.get()
            try:
                result_holder["result"] = self._client.call(*args, **kwargs)
            except Exception as e:
                result_holder["error"] = e
            result_event.set()

    def call(self, *args, **kwargs):
        result_holder = {}
        event = threading.Event()
        try:
            self._queue.put((args, kwargs, event, result_holder), block=False)
        except Full:
            raise WaapiQueueFullError("WAAPI dispatch queue is full")
        event.wait()
        if "error" in result_holder:
            raise result_holder["error"]
        return result_holder["result"]


_dispatcher: WaapiDispatcher | None = None


def get_client() -> WaapiClient:
    global _client
    if _client is None or not _client.is_connected():
        _client = WaapiClient()
    return _client


def get_dispatcher() -> WaapiDispatcher:
    global _dispatcher, _client
    client = get_client()
    if _dispatcher is None or _dispatcher._client is not client:
        _dispatcher = WaapiDispatcher(client)
    return _dispatcher


def _reconnect():
    """Force a fresh WAAPI connection and dispatcher."""
    global _client, _dispatcher
    if _client is not None:
        try:
            _client.disconnect()
        except Exception:
            pass
    _client = None
    _dispatcher = None


def ping() -> dict:
    """Check if WAAPI is available. Returns {"isAvailable": bool}."""
    try:
        return get_dispatcher().call("ak.wwise.core.ping")
    except Exception:
        return {"isAvailable": False}


def call(uri: str, args: dict = {}, options: dict = {}) -> dict:
    result = get_dispatcher().call(uri, args, options=options)
    if result is None:
        # Stale connection — reconnect and retry once
        _reconnect()
        result = get_dispatcher().call(uri, args, options=options)
    return result
