"""Import music and jingle audio files into Wwise via WAAPI."""
import json
from waapi import WaapiClient

client = WaapiClient()

for label, path in [
    ("music", "G:/repos/MCP/sk-wwise-mcp/sk-wwise-mcp/music_imports_final.json"),
    ("jingles", "G:/repos/MCP/sk-wwise-mcp/sk-wwise-mcp/jingle_imports_final.json"),
]:
    with open(path, encoding="utf-8") as f:
        imports = json.load(f)

    print(f"Importing {len(imports)} {label} files...")

    # Add <Sound SFX> type prefix and fix path for WAAPI
    for entry in imports:
        entry["objectPath"] = entry["objectPath"].replace(
            "\\Containers\\", "\\Actor-Mixer Hierarchy\\"
        )
        parts = entry["objectPath"].rsplit("\\", 1)
        if len(parts) == 2 and not parts[1].startswith("<"):
            entry["objectPath"] = parts[0] + "\\<Sound SFX>" + parts[1]
        if "\\Music\\" in entry["objectPath"]:
            entry["originalsSubFolder"] = "Music"
        else:
            entry["originalsSubFolder"] = "Jingles"

    result = client.call("ak.wwise.core.audio.import", {
        "importOperation": "useExisting",
        "default": {"importLanguage": "SFX"},
        "imports": imports,
    })

    if result:
        files = result.get("files", [])
        objs = result.get("objects", [])
        print(f"  Objects: {len(objs)}, Files copied: {len(files)}")
        for f in files[:3]:
            print(f"    {f}")
        if len(files) > 3:
            print(f"    ... and {len(files) - 3} more")
    else:
        print("  Import returned None")

client.disconnect()
print("Done!")
