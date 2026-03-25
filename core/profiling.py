from core.waapi_util import call


def get_available_consoles() -> dict:
    """Execute a WAAPI ak.wwise.core.remote.getAvailableConsoles query."""
    return call("ak.wwise.core.remote.getAvailableConsoles")


def connect_remote(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.remote.connect query."""
    return call("ak.wwise.core.remote.connect", query)


def get_connection_status() -> dict:
    """Execute a WAAPI ak.wwise.core.remote.getConnectionStatus query."""
    return call("ak.wwise.core.remote.getConnectionStatus")


def get_loaded_media(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.getLoadedMedia query."""
    return call("ak.wwise.core.profiler.getLoadedMedia", query)


def get_game_objects(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.getGameObjects query."""
    return call("ak.wwise.core.profiler.getGameObjects", query)


def get_cursor_time(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.getCursorTime query."""
    return call("ak.wwise.core.profiler.getCursorTime", query)


def stop_capture() -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.stopCapture query."""
    return call("ak.wwise.core.profiler.stopCapture")


def start_capture() -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.startCapture query."""
    return call("ak.wwise.core.profiler.startCapture")


def save_capture(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.saveCapture query."""
    return call("ak.wwise.core.profiler.saveCapture", query)


def register_meter(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.registerMeter query."""
    return call("ak.wwise.core.profiler.registerMeter", query)


def unregister_meter(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.unregisterMeter query."""
    return call("ak.wwise.core.profiler.unregisterMeter", query)


def move_cursor(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.moveCursor query."""
    return call("ak.wwise.core.profiler.moveCursor", query)


def set_cursor_time(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.setCursorTime query."""
    return call("ak.wwise.core.profiler.setCursorTime", query)


def get_voices(query: dict, options: dict = {}) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.getVoices query."""
    return call("ak.wwise.core.profiler.getVoices", query, options)


def get_voice_contributions(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.getVoiceContributions query."""
    return call("ak.wwise.core.profiler.getVoiceContributions", query)


def get_streamed_media(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.getStreamedMedia query."""
    return call("ak.wwise.core.profiler.getStreamedMedia", query)


def get_rtpcs(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.getRTPCs query."""
    return call("ak.wwise.core.profiler.getRTPCs", query)


def get_performance_monitor(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.getPerformanceMonitor query."""
    return call("ak.wwise.core.profiler.getPerformanceMonitor", query)


def get_meters(query: dict, options: dict = {}) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.getMeters query."""
    return call("ak.wwise.core.profiler.getMeters", query, options)


def get_cpu_usage(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.getCpuUsage query."""
    return call("ak.wwise.core.profiler.getCpuUsage", query)


def get_busses(query: dict, options: dict = {}) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.getBusses query."""
    return call("ak.wwise.core.profiler.getBusses", query, options)


def get_audio_objects(query: dict, options: dict = {}) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.getAudioObjects query."""
    return call("ak.wwise.core.profiler.getAudioObjects", query, options)


def enable_profiler_data(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.profiler.enableProfilerData query."""
    return call("ak.wwise.core.profiler.enableProfilerData", query)


def disconnect_remote() -> dict:
    """Execute a WAAPI ak.wwise.core.remote.disconnect query."""
    return call("ak.wwise.core.remote.disconnect")
