"""Routing guidance: the MCP `instructions` the exe sends to the client.

Built from short global guidance plus one short note per *mounted* server, so
the text only names tools that exist in the current Profile. Detailed how-to
stays in the `wwise-*` Skills; these notes are the condensed routing hints.

Rules for editing the notes:
- Write EVERY tool name in single backticks. `core.tool_names` only checks
  backticked names, and tests/unit/test_instructions.py fails when a note names
  a tool that its own server does not expose.
- A note may name only its own server's tools (other servers may not be mounted).
- Keep notes short. ADMIN_BUDGET_CHARS caps the largest case (all 12 servers).

To add a tool hint (e.g. a new browse tool), edit that server's entry in
SERVER_NOTES. To add a server, add its key (a `cli.SERVERS` key) there.
"""

from typing import Iterable

# Size budget for the admin profile (all 12 servers), in characters. Picked in
# issue #5: the size when written was about 4.7k chars, so 5500 leaves room for a
# few new tool hints while keeping the always-in-context cost to about 1.4k
# tokens. If a change goes over, trim the notes; do not raise this casually.
ADMIN_BUDGET_CHARS = 5500

GLOBAL_GUIDANCE = (
    "SK Wwise MCP: browse and edit a Wwise project through the Wwise Authoring API (WAAPI).\n"
    "- Wwise must be running with WAAPI enabled, except for the command-line server.\n"
    "- Use read-only tools for read-only tasks. Query an object before you edit it.\n"
    "- Warn the user before bulk operations (50+ objects).\n"
    "- Prefer the specialized servers below. Use the generic WAAPI server only as a last resort.\n"
    "- If a tool you need is not listed, the active profile "
    "(listen, author, build, qa, admin) excludes it. Tell the user which profile adds it.\n"
    "- Load the matching wwise-* skill for detailed rules."
)

# server name (a cli.SERVERS key) -> routing note. Tool names in single backticks.
SERVER_NOTES = {
    "browse": (
        "browse (read-only): `ping_wwise` checks the connection. "
        "Query objects with `build_object_info_query` first, then `get_wwise_object_info` "
        "(only a 10-item preview is returned; read the `output_file` for all results). "
        "Never use the absolute root `\\` as `from_path` (WAAPI returns 0 results); start from "
        "`\\Actor-Mixer Hierarchy`, `\\Events`, `\\Master-Mixer Hierarchy`, `\\SoundBanks` etc. "
        "`@OutputBus` is the local value, not the effective one: use `get_effective_output_bus`. "
        "To show one object with its children, use `show_wwise_object` (interactive inspector where supported). "
        "Compare objects with `diff_wwise_objects`; discover properties with "
        "`get_property_and_reference_names`; project info with `get_wwise_project_info`."
    ),
    "audition": (
        "audition (playback): `create_wwise_transport` for an object, then "
        "`execute_wwise_transport_action` (play, stop, pause). "
        "Leaving out the transport id applies the action to ALL transports. "
        "`list_wwise_transports` lists them; `destroy_wwise_transport` cleans up."
    ),
    "media-read": (
        "media-read (read-only): `query_media_pool` searches media files, "
        "`get_media_pool_fields` lists the fields you can filter on, "
        "`get_audio_source_peaks` returns waveform peaks."
    ),
    "objects": (
        "objects (editing): `create_wwise_objects`, `delete_wwise_objects`, `move_wwise_objects`, "
        "`copy_wwise_object`, `set_wwise_object_name`, `set_wwise_object_notes`, and "
        "`set_wwise_object_properties` (properties AND references, e.g. OutputBus). "
        "Batch tools take lists; use a single-entry list for one object. "
        "Event Actions: `create_wwise_objects` with type Action under the Event, then set the "
        "Target reference with `set_wwise_object_properties`; the target must be playable "
        "(not a virtual folder or Work Unit). "
        "Container-specific setup belongs to the containers server."
    ),
    "containers": (
        "containers (type-specific editing): `add_wwise_switch_assignments` / "
        "`remove_wwise_switch_assignments`, `add_wwise_blend_assignment` / "
        "`remove_wwise_blend_assignment`, `set_wwise_randomizer`, `set_wwise_attenuation_curve`, "
        "`set_wwise_game_parameter_range`. "
        "`set_wwise_state_groups` and `set_wwise_state_properties` REPLACE all existing values: "
        "include the current values to keep them."
    ),
    "pipeline": (
        "pipeline (import, build, save): import WAV only. Convert OGG/FLAC/MP3 first with "
        "`convert_audio_to_wav`. Pick the import tool by scale: `import_audio_directory` "
        "(a folder of WAVs matching existing objects), `import_audio_files` (under 50 files), "
        "`generate_tab_delimited_file` then `import_tab_delimited_file` (50+ files). "
        "Import object paths start with `\\Actor-Mixer Hierarchy`, not `\\Containers`. "
        "Import does not report per-file failures: check `get_wwise_log`. "
        "SoundBanks: `set_wwise_soundbank_inclusions`, `get_wwise_soundbank_inclusions`, "
        "`generate_wwise_soundbanks`. Save with `save_wwise_project`."
    ),
    "ui": (
        "ui (Wwise window): `open_project` / `close_project`, `get_selected_objects`, "
        "`execute_command` (find commands with `get_commands`), `switch_layout`, "
        "`capture_screen`, `bring_to_foreground`."
    ),
    "profiling": (
        "profiling (read-only profiler data): `get_profiler_voices`, `get_profiler_busses`, "
        "`get_profiler_cpu_usage`, `get_profiler_performance_monitor`, `get_profiler_meters`, "
        "`get_profiler_rtpcs`, `get_profiler_game_objects`, `get_profiler_loaded_media`, "
        "`get_profiler_streamed_media`, `get_profiler_cursor_time`. "
        "Most data needs the profiler data types enabled first (profiling-control server)."
    ),
    "profiling-control": (
        "profiling-control: call `enable_wwise_profiler_data` first, then `start_profiler_capture` "
        "and `stop_profiler_capture`; `save_profiler_capture` writes a .prof file; "
        "`set_profiler_cursor` moves the timeline. Every `register_profiler_meter` needs a "
        "matching `unregister_profiler_meter`."
    ),
    "remote": (
        "remote (connection): `get_available_remote_consoles`, then `connect_to_remote`; "
        "`get_remote_connection_status` checks it; `disconnect_from_remote` when done. "
        "Connect before profiling a running game."
    ),
    "command-line": (
        "command-line (WwiseConsole, no WAAPI needed): `cli_create_new_project`, "
        "`cli_verify_project`, `cli_migrate_project`, `cli_tab_delimited_import`, "
        "`cli_convert_external_sources`, `cli_start_waapi_server`. "
        "Run `cli_diagnostics` first if the console is not found."
    ),
    "generic": (
        "generic (last resort): `list_waapi_functions`, then `get_waapi_function_schema`, "
        "then `call_waapi`. Use only when no specialized server has the tool."
    ),
}


def build_instructions(servers: Iterable[str]) -> str:
    """Instructions text for the given mounted server names.

    Order follows ``servers``; duplicates are dropped. An unknown name raises
    ``ValueError`` so a typo cannot silently drop a note.
    """
    ordered = list(dict.fromkeys(servers))
    unknown = [name for name in ordered if name not in SERVER_NOTES]
    if unknown:
        raise ValueError(
            f"no routing note for server(s): {', '.join(unknown)}. "
            f"valid: {', '.join(sorted(SERVER_NOTES))}"
        )
    parts = [GLOBAL_GUIDANCE]
    if ordered:
        parts.append("Mounted servers:")
        parts.extend(f"- {SERVER_NOTES[name]}" for name in ordered)
    return "\n".join(parts)
