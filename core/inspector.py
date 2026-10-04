"""Object Inspector MCP App: data for `show_wwise_object`.

Read-only. Uses the same WAAPI object query as the other browse tools.
The HTML for the inspector lives in `core/inspector_html.py`.
"""

from typing import Optional

from core.query import execute_object_query

INSPECTOR_URI = "ui://sk-wwise/object-inspector.html"

# A few properties that most audio objects have. Missing ones are left out.
COMMON_PROPERTIES = ("Volume", "Pitch", "LowPassFilter", "HighPassFilter")

# Children shown in the inspector. The full count is always reported.
MAX_CHILDREN = 100

_BASE_FIELDS = ["id", "name", "type", "path"]


def _from_clause(
    object_path: Optional[str],
    object_guid: Optional[str],
    object_name_with_type: Optional[str],
) -> Optional[dict]:
    if object_path:
        return {"path": [object_path]}
    if object_guid:
        return {"id": [object_guid]}
    if object_name_with_type:
        return {"name": [object_name_with_type]}
    return None


def _brief(obj: dict) -> dict:
    return {key: obj.get(key) for key in _BASE_FIELDS}


def get_object_inspector_data(
    object_path: Optional[str] = None,
    object_guid: Optional[str] = None,
    object_name_with_type: Optional[str] = None,
) -> dict:
    """Return key data for one object: identity, common properties, parent, children."""
    from_clause = _from_clause(object_path, object_guid, object_name_with_type)
    if from_clause is None:
        return {"error": "Must specify object_path, object_guid, or object_name_with_type"}

    return_fields = _BASE_FIELDS + ["notes"] + [f"@{p}" for p in COMMON_PROPERTIES]
    found = execute_object_query({"from": from_clause, "options": {"return": return_fields}})
    if not found:
        return {"error": "Object not found"}
    obj = found[0]

    parents = execute_object_query({
        "from": from_clause,
        "transform": [{"select": ["parent"]}],
        "options": {"return": _BASE_FIELDS},
    })
    children = execute_object_query({
        "from": from_clause,
        "transform": [{"select": ["children"]}],
        "options": {"return": _BASE_FIELDS},
    })

    properties = {
        p: obj[f"@{p}"] for p in COMMON_PROPERTIES if obj.get(f"@{p}") is not None
    }
    return {
        "id": obj.get("id"),
        "name": obj.get("name"),
        "type": obj.get("type"),
        "path": obj.get("path"),
        "notes": obj.get("notes") or "",
        "properties": properties,
        "parent": _brief(parents[0]) if parents else None,
        "children_count": len(children),
        "children": [_brief(c) for c in children[:MAX_CHILDREN]],
    }
