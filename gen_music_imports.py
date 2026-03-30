"""Generate import JSON for music and jingle audio files."""
import os
import json

d1 = "E:/AudioSamples/Pokemon/Pokemon SFX Attack Moves & Sound Effects Collection/pkmn-rgby-soundtrack/wav/Disc 1"
d2 = "E:/AudioSamples/Pokemon/Pokemon SFX Attack Moves & Sound Effects Collection/pkmn-rgby-soundtrack/wav/Disc 2 (Yellow)"

# Build lookup by track number
d1_by_num = {}
for f in sorted(os.listdir(d1)):
    num = f.split(" - ")[0].strip()
    d1_by_num[num] = os.path.join(d1, f).replace("\\", "/")

d2_by_num = {}
for f in sorted(os.listdir(d2)):
    num = f.split(" - ")[0].strip()
    d2_by_num[num] = os.path.join(d2, f).replace("\\", "/")

B = "\\Containers\\Default Work Unit"

mappings = [
    # MX_Towns
    (f"{B}\\Music\\MX_Towns\\MX_Pallet_Town", d1_by_num["03"]),
    (f"{B}\\Music\\MX_Towns\\MX_Viridian_Pewter", d1_by_num["16"]),
    (f"{B}\\Music\\MX_Towns\\MX_Cerulean", d1_by_num["30"]),
    (f"{B}\\Music\\MX_Towns\\MX_Vermilion", d1_by_num["35"]),
    (f"{B}\\Music\\MX_Towns\\MX_Lavender_Town", d1_by_num["39"]),
    (f"{B}\\Music\\MX_Towns\\MX_Celadon", d1_by_num["41"]),
    (f"{B}\\Music\\MX_Towns\\MX_Fuchsia_Saffron_Cinnabar", d1_by_num["47"]),
    (f"{B}\\Music\\MX_Towns\\MX_Indigo_Plateau", d1_by_num["46"]),
    # MX_Routes
    (f"{B}\\Music\\MX_Routes\\MX_Route_01", d1_by_num["11"]),
    (f"{B}\\Music\\MX_Routes\\MX_Route_03", d1_by_num["27"]),
    (f"{B}\\Music\\MX_Routes\\MX_Route_11", d1_by_num["38"]),
    (f"{B}\\Music\\MX_Routes\\MX_Route_24", d1_by_num["31"]),
    (f"{B}\\Music\\MX_Routes\\MX_Cycling", d1_by_num["37"]),
    # MX_Dungeons
    (f"{B}\\Music\\MX_Dungeons\\MX_Viridian_Forest", d1_by_num["19"]),
    (f"{B}\\Music\\MX_Dungeons\\MX_Mt_Moon", d1_by_num["29"]),
    (f"{B}\\Music\\MX_Dungeons\\MX_Pokemon_Tower", d1_by_num["40"]),
    (f"{B}\\Music\\MX_Dungeons\\MX_Rocket_Hideout", d1_by_num["43"]),
    (f"{B}\\Music\\MX_Dungeons\\MX_Silph_Co", d1_by_num["45"]),
    (f"{B}\\Music\\MX_Dungeons\\MX_Victory_Road", d1_by_num["49"]),
    # MX_Buildings
    (f"{B}\\Music\\MX_Buildings\\MX_Pokemon_Center", d1_by_num["17"]),
    (f"{B}\\Music\\MX_Buildings\\MX_Gym", d1_by_num["23"]),
    (f"{B}\\Music\\MX_Buildings\\MX_Oak_Lab", d1_by_num["05"]),
    (f"{B}\\Music\\MX_Buildings\\MX_SS_Anne", d1_by_num["36"]),
    (f"{B}\\Music\\MX_Buildings\\MX_Game_Corner", d1_by_num["42"]),
    # MX_Battle
    (f"{B}\\Music\\MX_Battle\\MX_Battle_Wild", d1_by_num["13"]),
    (f"{B}\\Music\\MX_Battle\\MX_Battle_Trainer", d1_by_num["08"]),
    (f"{B}\\Music\\MX_Battle\\MX_Battle_Gym_Leader", d1_by_num["25"]),
    (f"{B}\\Music\\MX_Battle\\MX_Battle_Champion", d1_by_num["50"]),
    # MX_Victory
    (f"{B}\\Music\\MX_Victory\\MX_Victory_Wild", d1_by_num["14"]),
    (f"{B}\\Music\\MX_Victory\\MX_Victory_Trainer", d1_by_num["09"]),
    (f"{B}\\Music\\MX_Victory\\MX_Victory_Gym_Leader", d1_by_num["26"]),
    # MX_Story
    (f"{B}\\Music\\MX_Story\\MX_Opening", d1_by_num["01"]),
    (f"{B}\\Music\\MX_Story\\MX_Title_Screen", d1_by_num["02"]),
    (f"{B}\\Music\\MX_Story\\MX_Oak_Theme", d1_by_num["04"]),
    (f"{B}\\Music\\MX_Story\\MX_Rival_Theme", d1_by_num["07"]),
    (f"{B}\\Music\\MX_Story\\MX_Hurry_Along", d1_by_num["21"]),
    (f"{B}\\Music\\MX_Story\\MX_Evolution", d1_by_num["32"]),
    (f"{B}\\Music\\MX_Story\\MX_Credits", d1_by_num["52"]),
    (f"{B}\\Music\\MX_Story\\MX_Hall_of_Fame", d1_by_num["51"]),
    # MX_Yellow_Exclusive
    (f"{B}\\Music\\MX_Yellow_Exclusive\\MX_Opening_Yellow", d2_by_num["01"]),
    (f"{B}\\Music\\MX_Yellow_Exclusive\\MX_Title_Screen_Yellow", d2_by_num["02"]),
    (f"{B}\\Music\\MX_Yellow_Exclusive\\MX_Jessie_James", d2_by_num["03"]),
    (f"{B}\\Music\\MX_Yellow_Exclusive\\MX_Pikachu_Beach", d2_by_num["04"]),
    (f"{B}\\Music\\MX_Yellow_Exclusive\\MX_Giovanni", d2_by_num["05"]),
    # Jingles
    (f"{B}\\SFX\\SFX_Jingles\\Pokemon_Caught", d1_by_num["15"]),
    (f"{B}\\SFX\\SFX_Jingles\\Pokemon_Evolved", d1_by_num["33"]),
    (f"{B}\\SFX\\SFX_Jingles\\Key_Item_Obtained", d1_by_num["06"]),
    (f"{B}\\SFX\\SFX_Jingles\\Item_Obtained", d1_by_num["12"]),
    (f"{B}\\SFX\\SFX_Jingles\\Pokemon_Healed", d1_by_num["18"]),
    (f"{B}\\SFX\\SFX_Jingles\\Jingle_Level_Up", d1_by_num["10"]),
    (f"{B}\\SFX\\SFX_Jingles\\Pokedex_Rated", d1_by_num["34"]),
    (f"{B}\\SFX\\SFX_Jingles\\Trainer_Spotted_Boy", d1_by_num["20"]),
    (f"{B}\\SFX\\SFX_Jingles\\Trainer_Spotted_Girl", d1_by_num["28"]),
    (f"{B}\\SFX\\SFX_Jingles\\Jigglypuff_Song", d1_by_num["22"]),
]

imports = [{"objectPath": p, "audioFile": f} for p, f in mappings]

with open("G:/repos/MCP/sk-wwise-mcp/sk-wwise-mcp/music_imports.json", "w", encoding="utf-8") as out:
    json.dump(imports, out, indent=2, ensure_ascii=False)

print(f"Generated {len(imports)} import entries")
print(f"Sample: {imports[0]['objectPath']} -> {os.path.basename(imports[0]['audioFile'])}")
