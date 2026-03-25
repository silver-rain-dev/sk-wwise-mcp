from core.waapi_util import call


def create_transport(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.transport.create query."""
    return call("ak.wwise.core.transport.create", query)


def prepare_transport(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.transport.prepare query."""
    return call("ak.wwise.core.transport.prepare", query)


def destroy_transport(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.transport.destroy query."""
    return call("ak.wwise.core.transport.destroy", query)


def get_transport_list() -> dict:
    """Execute a WAAPI ak.wwise.core.transport.getList query."""
    return call("ak.wwise.core.transport.getList")


def get_transport_state(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.transport.getState query."""
    return call("ak.wwise.core.transport.getState", query)


def execute_transport_action(query: dict) -> dict:
    """Execute a WAAPI ak.wwise.core.transport.executeAction query."""
    return call("ak.wwise.core.transport.executeAction", query)
