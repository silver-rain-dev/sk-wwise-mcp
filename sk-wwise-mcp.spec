# PyInstaller spec for sk-wwise-mcp.
#
# Build:
#   pip install pyinstaller
#   pyinstaller --clean sk-wwise-mcp.spec
#
# Output: dist/sk-wwise-mcp.exe
#
# All paths are relative to this spec file's directory.

from PyInstaller.utils.hooks import collect_submodules, copy_metadata

# cli.py imports server modules dynamically via importlib, so PyInstaller's
# static analysis can't see them — list them explicitly.
SERVER_MODULES = [
    "mcp_browse.server",
    "mcp_audition.server",
    "mcp_objects.server",
    "mcp_containers.server",
    "mcp_pipeline.server",
    "mcp_generic.server",
    "mcp_media_read.server",
    "mcp_profiling.server",
    "mcp_profiling_control.server",
    "mcp_command_line.server",
    "mcp_remote.server",
    "mcp_ui.server",
]

# fastmcp / mcp / waapi pull submodules dynamically. Sweep the full trees.
hiddenimports = (
    SERVER_MODULES
    + collect_submodules("fastmcp")
    + collect_submodules("mcp")
    + collect_submodules("waapi")
    + collect_submodules("core")
)

# Some libs read their package metadata at runtime (entry points, version).
datas = (
    copy_metadata("fastmcp")
    + copy_metadata("mcp")
    + copy_metadata("waapi-client")
)

a = Analysis(
    ["cli.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="sk-wwise-mcp",
    console=True,
    onefile=True,
    upx=False,
    debug=False,
    strip=False,
)
