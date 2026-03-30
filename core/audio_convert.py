import shutil
import subprocess
from pathlib import Path
from typing import Optional


_CONVERTIBLE_EXTENSIONS = {".ogg", ".flac", ".mp3", ".aac", ".m4a", ".wma", ".aiff", ".aif"}

_KNOWN_FFMPEG_PATHS = [
    r"C:\ffmpeg\bin\ffmpeg.exe",
    r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
    r"C:\tools\ffmpeg\bin\ffmpeg.exe",
]


def find_ffmpeg() -> Optional[str]:
    """Find ffmpeg executable. Checks PATH first, then known install locations."""
    path_result = shutil.which("ffmpeg")
    if path_result:
        return path_result
    for known in _KNOWN_FFMPEG_PATHS:
        if Path(known).is_file():
            return known
    return None


def convert_to_wav(
    input_dir: str,
    output_dir: str,
    ffmpeg_path: Optional[str] = None,
) -> dict:
    """Convert all non-WAV audio files in input_dir to WAV in output_dir.

    Args:
        input_dir:   Directory containing audio files to convert.
        output_dir:  Directory to write converted WAV files.
        ffmpeg_path: Optional explicit path to ffmpeg. Auto-detected if omitted.

    Returns dict with:
        output_directory: Path to output directory.
        converted: List of converted WAV file paths.
        skipped: List of skipped files (already WAV or unsupported).
        errors: List of {file, error} dicts for failed conversions.
    """
    ffmpeg = ffmpeg_path or find_ffmpeg()
    if not ffmpeg:
        raise FileNotFoundError(
            "ffmpeg not found. Install ffmpeg and add to PATH, or pass ffmpeg_path explicitly."
        )

    in_path = Path(input_dir)
    if not in_path.is_dir():
        raise NotADirectoryError(f"Input directory does not exist: {input_dir}")

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    converted = []
    skipped = []
    errors = []

    for f in sorted(in_path.iterdir()):
        if not f.is_file():
            continue
        ext = f.suffix.lower()
        if ext == ".wav":
            skipped.append(str(f))
            continue
        if ext not in _CONVERTIBLE_EXTENSIONS:
            skipped.append(str(f))
            continue

        dest = out_path / (f.stem + ".wav")
        try:
            result = subprocess.run(
                [ffmpeg, "-y", "-i", str(f), "-ar", "44100", str(dest)],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                converted.append(str(dest))
            else:
                errors.append({"file": str(f), "error": result.stderr[-500:]})
        except subprocess.TimeoutExpired:
            errors.append({"file": str(f), "error": "Conversion timed out (120s)"})

    return {
        "output_directory": str(out_path),
        "converted": converted,
        "skipped": skipped,
        "errors": errors,
    }


def convert_file_to_wav(src: Path, dest_dir: Path) -> Path:
    """Convert a single audio file to WAV. Returns the path to the converted file.

    Raises FileNotFoundError if ffmpeg is not available.
    Raises RuntimeError if the conversion fails.
    """
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        raise FileNotFoundError(
            f"Cannot import '{src.name}' — it is {src.suffix} format and requires "
            f"ffmpeg to convert to WAV. Install ffmpeg (https://ffmpeg.org) and add "
            f"it to PATH, or convert the file to WAV manually before importing."
        )

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / (src.stem + ".wav")

    result = subprocess.run(
        [ffmpeg, "-y", "-i", str(src), "-ar", "44100", str(dest)],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed to convert '{src.name}': {result.stderr[-500:]}"
        )
    return dest
