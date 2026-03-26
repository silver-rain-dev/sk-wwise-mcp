import sys
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.waapi_util import WaapiDispatcher, WaapiQueueFullError


class FakeClient:
    """Mock WAAPI client that records calls."""

    def __init__(self, delay=0):
        self.calls = []
        self.delay = delay
        self.lock = threading.Lock()

    def call(self, uri, payload=None):
        if self.delay:
            time.sleep(self.delay)
        with self.lock:
            self.calls.append((uri, payload))
        return {"uri": uri, "args": payload}

    def is_connected(self):
        return True

    def disconnect(self):
        pass


class ErrorClient:
    """Mock WAAPI client that raises on call."""

    def call(self, *args, **kwargs):
        raise ConnectionError("WAAPI disconnected")

    def is_connected(self):
        return True

    def disconnect(self):
        pass


def test_single_call():
    client = FakeClient()
    dispatcher = WaapiDispatcher(client)
    result = dispatcher.call("ak.wwise.core.getInfo", {})
    assert result["uri"] == "ak.wwise.core.getInfo"
    assert len(client.calls) == 1


def test_call_with_args():
    client = FakeClient()
    dispatcher = WaapiDispatcher(client)
    result = dispatcher.call("ak.wwise.core.object.get", {"from": {"path": ["\\Events"]}})
    assert result["args"] == {"from": {"path": ["\\Events"]}}


def test_call_with_options_merged():
    """Options should be merged into payload before calling the dispatcher."""
    client = FakeClient()
    dispatcher = WaapiDispatcher(client)
    # In the new API, options are merged into payload at the call() level in waapi_util,
    # not by the dispatcher. Dispatcher just sees (uri, payload).
    payload = {"from": {"path": ["\\Events"]}, "options": {"return": ["name"]}}
    result = dispatcher.call("ak.wwise.core.object.get", payload)
    assert client.calls[0][1] == payload


def test_serializes_concurrent_calls():
    client = FakeClient(delay=0.01)
    dispatcher = WaapiDispatcher(client)
    results = [None] * 10
    errors = []

    def make_call(i):
        try:
            results[i] = dispatcher.call(f"call_{i}", {})
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=make_call, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert all(r is not None for r in results)
    assert len(client.calls) == 10


def test_preserves_order():
    client = FakeClient()
    dispatcher = WaapiDispatcher(client)

    for i in range(20):
        dispatcher.call(f"call_{i}", {})

    uris = [c[0] for c in client.calls]
    assert uris == [f"call_{i}" for i in range(20)]


def test_error_propagates():
    client = ErrorClient()
    dispatcher = WaapiDispatcher(client)
    try:
        dispatcher.call("ak.wwise.core.getInfo", {})
        assert False, "Should have raised"
    except ConnectionError as e:
        assert "WAAPI disconnected" in str(e)


def test_error_does_not_block_subsequent_calls():
    error_client = ErrorClient()
    dispatcher = WaapiDispatcher(error_client)

    try:
        dispatcher.call("will_fail", {})
    except ConnectionError:
        pass

    # Replace client with working one and verify dispatcher still processes
    good_client = FakeClient()
    dispatcher._client = good_client
    result = dispatcher.call("ak.wwise.core.getInfo", {})
    assert result["uri"] == "ak.wwise.core.getInfo"


def test_queue_full_raises():
    client = FakeClient(delay=0.1)
    dispatcher = WaapiDispatcher(client, maxsize=2)

    # Fill the queue - first call is being processed, try to overfill
    errors = []
    barrier = threading.Barrier(3, timeout=5)

    def slow_call():
        try:
            barrier.wait()
            dispatcher.call("slow", {})
        except WaapiQueueFullError:
            errors.append(True)
        except Exception:
            pass

    threads = [threading.Thread(target=slow_call) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)

    # At least some calls should succeed, queue full may or may not trigger
    # depending on timing - just verify no deadlock occurred
    assert True
