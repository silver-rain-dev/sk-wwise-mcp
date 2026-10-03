"""Check that tool names written in guidance text exist in the tool registry.

Guidance (the wwise-* SKILL.md files, and later the generated server
instructions) names tools by hand. A renamed or invented name sends the model
to a tool that does not exist. This module finds those names.

Registry
    ``known_tool_names()`` asks each real FastMCP server object (the 12
    ``mcp_*.server`` modules) for its tool list. Nothing is hard-coded.

Extraction convention
    Only text inside single backticks is looked at. A backticked token counts
    as a tool name when ALL of these hold:

    1. It is lowercase snake_case with at least one underscore
       (``get_wwise_object_info``). This drops WAAPI URIs (``ak.wwise.core...``),
       properties (``@Volume``), paths, camelCase args (``importLanguage``) and
       single words (``parent``).
    2. It looks like a tool, by either:
       a. its first segment is a verb that real tools start with
          (``get``, ``set``, ``import``, ``cli`` ...; built from the registry), or
       b. it contains a Wwise domain segment (``wwise``, ``waapi``,
          ``profiler``, ``remote``).
       Rule (b) catches invented names with a new verb (``find_wwise_object``).
       Rule (a) catches reused verbs (``query_wwise_objects``).

    Arguments that happen to share a tool verb are skipped through
    ``IGNORED_TOKENS`` (kept small, each one justified there).

    Server names (``mcp_browse``) are not tool names; rule 2 does not match them.
"""

import asyncio
import concurrent.futures
import importlib
import re
import sys
from pathlib import Path
from typing import Iterable, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent

# The 12 servers. Each module exposes a FastMCP object named ``mcp``.
SERVER_MODULES = (
    "mcp_audition",
    "mcp_browse",
    "mcp_command_line",
    "mcp_containers",
    "mcp_generic",
    "mcp_media_read",
    "mcp_objects",
    "mcp_pipeline",
    "mcp_profiling",
    "mcp_profiling_control",
    "mcp_remote",
    "mcp_ui",
)

# Backticked tokens that look like tool names but are not.
IGNORED_TOKENS = frozenset({
    "list_name",  # create_wwise_objects argument; "list" is also a tool verb (list_waapi_functions)
})

# Segments that mark a token as Wwise-tool-shaped even with an unknown verb.
DOMAIN_SEGMENTS = frozenset({"wwise", "waapi", "profiler", "remote"})

_BACKTICKED = re.compile(r"`([^`\n]+)`")
_CALL_SUFFIX = re.compile(r"\(.*\)$")
_SNAKE_CASE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)+$")

_known_cache: Optional[frozenset] = None


def _run_sync(coro_factory):
    """Run an async call from sync code, even if an event loop is already running."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro_factory())
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(lambda: asyncio.run(coro_factory())).result()


def known_tool_names() -> set:
    """Names of every tool registered on the 12 servers."""
    global _known_cache
    if _known_cache is None:
        if str(_REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(_REPO_ROOT))
        names = set()
        for module_name in SERVER_MODULES:
            server = importlib.import_module(f"{module_name}.server")
            tools = _run_sync(server.mcp.list_tools)
            names.update(tool.name for tool in tools)
        _known_cache = frozenset(names)
    return set(_known_cache)


def _verbs(known: Iterable[str]) -> set:
    return {name.split("_")[0] for name in known}


def extract_tool_names(text: str, known: Optional[Iterable[str]] = None) -> set:
    """Backticked tool-shaped names in ``text`` (see module docstring).

    ``known`` supplies the verb list; it defaults to the real registry.
    """
    known = known_tool_names() if known is None else set(known)
    verbs = _verbs(known)
    found = set()
    for raw in _BACKTICKED.findall(text):
        token = _CALL_SUFFIX.sub("", raw)
        if not _SNAKE_CASE.match(token) or token in IGNORED_TOKENS:
            continue
        segments = token.split("_")
        if segments[0] in verbs or DOMAIN_SEGMENTS.intersection(segments):
            found.add(token)
    return found


def unknown_tool_names(text: str, known: Optional[Iterable[str]] = None) -> list:
    """Sorted tool-shaped names in ``text`` that are not in the registry.

    Takes plain text so the instructions builder can call it on generated output.
    """
    known = known_tool_names() if known is None else set(known)
    return sorted(extract_tool_names(text, known) - known)


def unknown_tool_names_in_files(paths: Iterable[Path], known: Optional[Iterable[str]] = None) -> dict:
    """Map ``path -> sorted unknown names`` for each file that has any."""
    known = known_tool_names() if known is None else set(known)
    result = {}
    for path in paths:
        unknown = unknown_tool_names(Path(path).read_text(encoding="utf-8"), known)
        if unknown:
            result[Path(path)] = unknown
    return result
