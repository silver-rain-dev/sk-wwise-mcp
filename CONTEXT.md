# SK Wwise MCP

Tools that let Claude browse and edit a running Wwise project through WAAPI. They are shipped so a sound designer only needs Claude plus one install.

## Language

### Packaging

**Server**:
One of the `mcp_*` tool groups (browse, audition, objects, …). The single exe can mount any set of servers in one process.
_Avoid_: module, toolset

**Profile**:
A named role that picks which servers get mounted, so the tools a role should not use never load. The profiles are **listen**, **author** (the default), **build**, **qa** and **admin**. Names describe what the role can do, not who the person is.
_Avoid_: role config, permission level, viewer/designer/editor (old names), junior/senior

**Bundle**:
The `sk-wwise-mcp.mcpb` file: the exe, its manifest and its user settings. It is the one server artifact for both install paths.
_Avoid_: extension, dxt

**Plugin**:
The Claude plugin: the bundle plus the skills, installed from the marketplace. It is the main way users install.
_Avoid_: mod (a mod is an optional part a plugin may hold)

### Guidance

**Routing guidance**:
The short notes the server sends as MCP instructions. They are built from the servers actually mounted, so they only name tools that exist.
_Avoid_: system prompt, preamble

**Skill**:
A `wwise-*` SKILL.md with the detailed how-to for one server. Claude loads it on demand; it is not always in context.
