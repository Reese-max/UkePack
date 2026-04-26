"""Shared music-theory helpers for chord and key transformations."""

import re

_PITCH_CLASS: dict[str, int] = {
    "C": 0,
    "B#": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "Fb": 4,
    "E#": 5,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
    "Cb": 11,
}
_SHARP_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
_FLAT_NAMES = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B")
_CHORD_ROOT_PATTERN = re.compile(r"^([A-Ga-g])([#b]?)(.*)$")


def split_chord_root(chord_token: str) -> tuple[str, str] | None:
    """Return the normalized chord root plus any remaining suffix."""
    match = _CHORD_ROOT_PATTERN.match(chord_token.strip())
    if match is None:
        return None

    root, accidental, suffix = match.groups()
    return f"{root.upper()}{accidental}", suffix


def signed_semitone_shift(original_tonic: str, target_tonic: str) -> int:
    """Return the shortest signed semitone shift, preferring downward tritones."""
    delta = (pitch_class(target_tonic) - pitch_class(original_tonic)) % 12
    if delta == 6:
        return -6
    return delta - 12 if delta > 6 else delta


def transpose_chord_symbol(chord_symbol: str, semitone_shift: int, prefer_flats: bool) -> str:
    """Transpose a chord symbol while preserving suffixes and slash bass notes."""
    root_part, slash, bass_part = chord_symbol.partition("/")
    transposed_root = _transpose_chord_part(root_part, semitone_shift, prefer_flats)
    if not slash:
        return transposed_root
    transposed_bass = _transpose_chord_part(bass_part, semitone_shift, prefer_flats)
    return f"{transposed_root}/{transposed_bass}"


def pitch_class(note_name: str) -> int:
    """Convert a pitch name into its chromatic pitch class."""
    try:
        return _PITCH_CLASS[note_name]
    except KeyError as error:
        raise ValueError(f"Unsupported note name: {note_name}") from error


def _transpose_chord_part(chord_part: str, semitone_shift: int, prefer_flats: bool) -> str:
    """Transpose the root pitch at the front of a chord token."""
    parsed = split_chord_root(chord_part)
    if parsed is None:
        return chord_part.strip()

    root, suffix = parsed
    names = _FLAT_NAMES if prefer_flats else _SHARP_NAMES
    transposed_root = names[(pitch_class(root) + semitone_shift) % 12]
    return f"{transposed_root}{suffix}"
