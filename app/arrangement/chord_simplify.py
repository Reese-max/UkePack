"""Chord simplification helpers for beginner-friendly ukulele arrangements."""

import re

_ROOT_PATTERN = re.compile(r"^([A-Ga-g])([#b]?)(.*)$")
_SUFFIX_RULES: tuple[tuple[str, str], ...] = (
    ("maj9", ""),
    ("maj7", ""),
    ("maj6", ""),
    ("add9", ""),
    ("sus4", ""),
    ("sus2", ""),
    ("m11", "m"),
    ("m9", "m"),
    ("m7", "m"),
    ("m6", "m"),
    ("min11", "m"),
    ("min9", "m"),
    ("min7", "m"),
    ("min6", "m"),
    ("13", "7"),
    ("11", "7"),
    ("9", "7"),
    ("aug", ""),
    ("+", ""),
)
_EXACT_SIMPLIFICATIONS: dict[str, str] = {
    "A/C#": "A",
    "Am/C": "Am",
    "Am7": "Am",
    "Am9": "Am",
    "Bbmaj7": "Bb",
    "Bdim": "G7",
    "Bm7b5": "Dm",
    "Cadd9": "C",
    "Caug": "C",
    "Cmaj7": "C",
    "Cmaj9": "C",
    "Csus2": "C",
    "D/F#": "D",
    "Dm7": "Dm",
    "Dsus4": "D",
    "Eaug": "E",
    "E7sus4": "E7",
    "Ebmaj7": "Eb",
    "F#m7b5": "Am",
    "Fadd9": "F",
    "Fmaj7": "F",
    "G/B": "G",
    "G13": "G7",
    "Gsus4": "G",
}


def simplify(chord: str) -> str:
    """Reduce a chord symbol to a beginner-friendly ukulele voicing."""
    normalized = _normalize_symbol(chord)
    if not normalized:
        raise ValueError("Chord symbol cannot be empty")

    direct_match = _EXACT_SIMPLIFICATIONS.get(normalized)
    if direct_match is not None:
        return direct_match

    if "/" in normalized:
        return simplify(normalized.split("/", maxsplit=1)[0])

    return _simplify_suffix(normalized)


def _normalize_symbol(chord: str) -> str:
    """Collapse whitespace and normalize the root note casing."""
    compact = "".join(chord.split())
    match = _ROOT_PATTERN.match(compact)
    if match is None:
        return compact

    root, accidental, suffix = match.groups()
    return f"{root.upper()}{accidental}{suffix}"


def _simplify_suffix(chord: str) -> str:
    """Apply stable suffix-based fallback rules when no exact mapping exists."""
    for suffix, replacement in _SUFFIX_RULES:
        if chord.endswith(suffix):
            return f"{chord.removesuffix(suffix)}{replacement}"
    return chord
