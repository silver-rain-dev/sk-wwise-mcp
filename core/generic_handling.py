from core.waapi_util import call

def get_waapi_availiable_functions():
    """List all available WAAPI functions."""
    return call("ak.wwise.waapi.getFunctions")

def get_waapi_schema(function_name: str):
    """Get the argument/option schema for a WAAPI function."""
    return call("ak.wwise.waapi.getSchema", {"uri": function_name})