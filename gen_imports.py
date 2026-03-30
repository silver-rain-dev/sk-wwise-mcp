"""Generate tab-delimited import files for Pokemon RGY Wwise project."""
import os

# ── Pokemon Gen 1 names ──────────────────────────────────────────────
POKEMON = {
    1: "Bulbasaur", 2: "Ivysaur", 3: "Venusaur", 4: "Charmander", 5: "Charmeleon",
    6: "Charizard", 7: "Squirtle", 8: "Wartortle", 9: "Blastoise", 10: "Caterpie",
    11: "Metapod", 12: "Butterfree", 13: "Weedle", 14: "Kakuna", 15: "Beedrill",
    16: "Pidgey", 17: "Pidgeotto", 18: "Pidgeot", 19: "Rattata", 20: "Raticate",
    21: "Spearow", 22: "Fearow", 23: "Ekans", 24: "Arbok", 25: "Pikachu",
    26: "Raichu", 27: "Sandshrew", 28: "Sandslash", 29: "NidoranF", 30: "Nidorina",
    31: "Nidoqueen", 32: "NidoranM", 33: "Nidorino", 34: "Nidoking", 35: "Clefairy",
    36: "Clefable", 37: "Vulpix", 38: "Ninetales", 39: "Jigglypuff", 40: "Wigglytuff",
    41: "Zubat", 42: "Golbat", 43: "Oddish", 44: "Gloom", 45: "Vileplume",
    46: "Paras", 47: "Parasect", 48: "Venonat", 49: "Venomoth", 50: "Diglett",
    51: "Dugtrio", 52: "Meowth", 53: "Persian", 54: "Psyduck", 55: "Golduck",
    56: "Mankey", 57: "Primeape", 58: "Growlithe", 59: "Arcanine", 60: "Poliwag",
    61: "Poliwhirl", 62: "Poliwrath", 63: "Abra", 64: "Kadabra", 65: "Alakazam",
    66: "Machop", 67: "Machoke", 68: "Machamp", 69: "Bellsprout", 70: "Weepinbell",
    71: "Victreebel", 72: "Tentacool", 73: "Tentacruel", 74: "Geodude", 75: "Graveler",
    76: "Golem", 77: "Ponyta", 78: "Rapidash", 79: "Slowpoke", 80: "Slowbro",
    81: "Magnemite", 82: "Magneton", 83: "Farfetchd", 84: "Doduo", 85: "Dodrio",
    86: "Seel", 87: "Dewgong", 88: "Grimer", 89: "Muk", 90: "Shellder",
    91: "Cloyster", 92: "Gastly", 93: "Haunter", 94: "Gengar", 95: "Onix",
    96: "Drowzee", 97: "Hypno", 98: "Krabby", 99: "Kingler", 100: "Voltorb",
    101: "Electrode", 102: "Exeggcute", 103: "Exeggutor", 104: "Cubone", 105: "Marowak",
    106: "Hitmonlee", 107: "Hitmonchan", 108: "Lickitung", 109: "Koffing", 110: "Weezing",
    111: "Rhyhorn", 112: "Rhydon", 113: "Chansey", 114: "Tangela", 115: "Kangaskhan",
    116: "Horsea", 117: "Seadra", 118: "Goldeen", 119: "Seaking", 120: "Staryu",
    121: "Starmie", 122: "MrMime", 123: "Scyther", 124: "Jynx", 125: "Electabuzz",
    126: "Magmar", 127: "Pinsir", 128: "Tauros", 129: "Magikarp", 130: "Gyarados",
    131: "Lapras", 132: "Ditto", 133: "Eevee", 134: "Vaporeon", 135: "Jolteon",
    136: "Flareon", 137: "Porygon", 138: "Omanyte", 139: "Omastar", 140: "Kabuto",
    141: "Kabutops", 142: "Aerodactyl", 143: "Snorlax", 144: "Articuno", 145: "Zapdos",
    146: "Moltres", 147: "Dratini", 148: "Dragonair", 149: "Dragonite", 150: "Mewtwo",
    151: "Mew",
}

CRIES_DIR = "E:\\AudioSamples\\Pokemon\\Pokemon SFX Attack Moves & Sound Effects Collection\\cries-main\\cries-main\\cries\\pokemon\\legacy"
MOVES_DIR = "E:\\AudioSamples\\Pokemon\\Pokemon SFX Attack Moves & Sound Effects Collection\\GEN 1 SFX - Attack Moves - RBY"

# Files that belong to SFX_Status, not SFX_Moves
STATUS_FILES = {"Poisoned.wav", "Sleeping.wav", "Confused.wav", "Confused2.wav"}

# Special container types (default is Random Container for multi-file)
BLEND_MOVES = {"HyperBeam"}      # Layered: beam + laser
SEQUENCE_MOVES = {"SolarBeam", "Substitute"}  # Multi-phase

# ── Generate Cries import ────────────────────────────────────────────
def gen_cries_import(out_path):
    lines = ["Audio File\tObject Path"]
    base = "\\Actor-Mixer Hierarchy\\Default Work Unit\\SFX\\SFX_Pokemon_Cries"
    for num in range(1, 152):
        name = POKEMON[num]
        audio = os.path.join(CRIES_DIR, f"{num}.ogg")
        obj_name = f"{num:03d}_{name}"
        obj_path = f"{base}\\<Sound SFX>{obj_name}"
        lines.append(f"{audio}\t{obj_path}")
    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote {len(lines)-1} cries to {out_path}")


# ── Group move files by base move name ───────────────────────────────
def group_move_files():
    """Group wav files by their base move name."""
    import re
    files = sorted(f for f in os.listdir(MOVES_DIR) if f.endswith(".wav"))

    # Exclude status files and readme
    files = [f for f in files if f not in STATUS_FILES]

    groups = {}
    for fname in files:
        base = fname[:-4]  # strip .wav

        # Find the base move name by stripping numeric suffixes,
        # "Direct", "Single", "Delay", "Full", "Shield", "WHit", "(LOOP)"
        # Pattern: BaseName followed by optional variant suffix
        # e.g., "Absorb1" -> "Absorb", "AuroraBeamDirect" -> "AuroraBeam"
        # "SolarBeam2+3Direct" -> "SolarBeam", "Waterfall23" -> "Waterfall"

        # Special cases first
        if base.startswith("IMHIT"):
            # IMHIT_Damage, IMHITSUPER_Super_Effective, IMHITWEAK_Not_Very_Effective
            if "SUPER" in base:
                move_name = "IMHITSUPER"
            elif "WEAK" in base:
                move_name = "IMHITWEAK"
            else:
                move_name = "IMHIT"
            groups.setdefault(move_name, []).append(fname)
            continue

        # Strip known suffixes repeatedly until stable
        move_name = base
        while True:
            prev = move_name
            move_name = re.sub(
                r'(\d+\+?\d*|Direct|Single|Delay|Full|Shield|WHit|Laser|\(LOOP\))$',
                '', move_name
            )
            if move_name == prev or not move_name:
                break
        # If stripping left nothing, use original
        if not move_name:
            move_name = base

        groups.setdefault(move_name, []).append(fname)

    return groups


def gen_moves_import(out_path):
    lines = ["Audio File\tObject Path"]
    base_path = "\\Actor-Mixer Hierarchy\\Default Work Unit\\SFX\\SFX_Moves"

    groups = group_move_files()

    for move_name, files in sorted(groups.items()):
        if len(files) == 1:
            # Single file → Sound directly under SFX_Moves
            audio = os.path.join(MOVES_DIR, files[0])
            obj_path = f"{base_path}\\<Sound SFX>{move_name}"
            lines.append(f"{audio}\t{obj_path}")
        else:
            # Multi-file → container with Sound children
            if move_name in BLEND_MOVES:
                container_type = "Blend Container"
            elif move_name in SEQUENCE_MOVES:
                container_type = "Sequence Container"
            else:
                container_type = "Random Container"

            for fname in files:
                sound_name = fname[:-4]  # strip .wav
                audio = os.path.join(MOVES_DIR, fname)
                obj_path = f"{base_path}\\<{container_type}>{move_name}\\<Sound SFX>{sound_name}"
                lines.append(f"{audio}\t{obj_path}")

    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote {len(lines)-1} move sounds to {out_path}")

    # Print summary
    single = sum(1 for f in groups.values() if len(f) == 1)
    multi = sum(1 for f in groups.values() if len(f) > 1)
    print(f"  {single} single-file moves, {multi} multi-file moves ({len(groups)} total)")


if __name__ == "__main__":
    gen_cries_import("pokemon_cries_import.txt")
    gen_moves_import("pokemon_moves_import.txt")
