import json
from pathlib import Path
from core.waapi_util import call

def execute_object_query(query: dict) -> list[dict]:
    """Execute a WAAPI ak.wwise.core.object.get query and return the results."""
    result = call("ak.wwise.core.object.get", query)
    return result.get("return", [])

# ak.wwise.core.object.diff 
# ak.wwise.core.object.getAttenuationCurve 

def get_installation_info() -> dict:
    """Executes ak.wwise.core.getInfo and return the results"""
    return call("ak.wwise.core.getInfo")

def get_project_info() -> dict:
    """Executes ak.wwise.core.getProjectInfo and return the results"""
    return call("ak.wwise.core.getProjectInfo")


def summarize_and_save(results: list[dict], output_file: str = None) -> dict:
    """Save full query results to a JSON file and return a compact summary."""
    if output_file is None:
        output_file = "wwise_query_output.json"

    output_path = Path(output_file).resolve()
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    type_counts = {}
    for obj in results:
        t = obj.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    return {
        "total_count": len(results),
        "types": type_counts,
        "output_file": str(output_path),
        "preview": results[:10],
    }
