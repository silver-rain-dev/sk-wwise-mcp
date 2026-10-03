"""Read optional settings from environment variables.

An MCP Bundle host can leave an unset optional setting as the literal text
`${user_config.<key>}` (or as an empty string). Both mean "not set".
"""

import os


def read_env_setting(name: str) -> str:
    """Return the trimmed value of env var `name`, or "" when it is unset.

    Unset, empty, whitespace-only and an unsubstituted Bundle placeholder
    (`${user_config.<key>}`) all return "".
    """
    value = os.environ.get(name, "").strip()
    if value.startswith("${user_config.") and value.endswith("}"):
        return ""
    return value
