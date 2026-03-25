from core.waapi_util import call


def get_min_max_peaks(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.audioSourcePeaks.getMinMaxPeaksInRegion query."""
    return call("ak.wwise.core.audioSourcePeaks.getMinMaxPeaksInRegion", query)


def get_min_max_peaks_trimmed(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.audioSourcePeaks.getMinMaxPeaksInTrimmedRegion query."""
    return call("ak.wwise.core.audioSourcePeaks.getMinMaxPeaksInTrimmedRegion", query)


def get_media_pool(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.mediaPool.get query."""
    return call("ak.wwise.core.mediaPool.get", query)


def get_media_pool_fields() -> dict:
    """Execute a WAAPI ak.wwise.core.mediaPool.getFields query."""
    return call("ak.wwise.core.mediaPool.getFields")
