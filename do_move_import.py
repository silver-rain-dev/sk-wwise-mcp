"""Import move SFX WAVs into Wwise via WAAPI."""
import json
import sys
sys.path.insert(0, ".")
from core.waapi_util import call

with open("move_imports.json") as f:
    imports = json.load(f)

# Split into batches of 50
batch_size = 50
total_created = 0
errors = []

for i in range(0, len(imports), batch_size):
    batch = imports[i:i + batch_size]
    try:
        result = call(
            "ak.wwise.core.audio.import",
            {
                "importOperation": "useExisting",
                "default": {"importLanguage": "SFX"},
                "imports": batch,
            },
            timeout=120,
        )
        created = len(result.get("objects", []))
        total_created += created
        print(f"Batch {i // batch_size}: {created} objects from {len(batch)} imports")
    except Exception as e:
        errors.append(f"Batch {i // batch_size}: {e}")
        print(f"Batch {i // batch_size}: ERROR - {e}")

print(f"\nTotal created/linked: {total_created}")
if errors:
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  {e}")
