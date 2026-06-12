"""Chord simplification helpers for beginner-friendly ukulele arrangements."""

import re

from app.core.music_theory import split_chord_root

_FULL_WIDTH_SPACE = "\u3000"
_NO_CHORD_MARKERS = {"N.C.", "N.C", "NC"}
_SUFFIX_NORMALIZERS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile("Δ|△"), "maj"),
    (re.compile(r"(?i)maj"), "maj"),
    (re.compile(r"(?i)min"), "min"),
    (re.compile(r"(?i)add"), "add"),
    (re.compile(r"(?i)sus"), "sus"),
    (re.compile(r"(?i)dim"), "dim"),
)
_SUFFIX_RULES: tuple[tuple[str, str], ...] = (
    ("maj9", ""),
    ("maj7", ""),
    ("maj6", ""),
    ("add9", ""),
    ("sus4", ""),
    ("sus2", ""),
    ("dim7", "N.C."),
    ("m7b5", "m"),
    ("dim", "N.C."),
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
    "A7": "A7",
    "A9": "A7",
    "A11": "A7",
    "A13": "A7",
    "Am11": "Am",
    "Am13": "Am",
    "Bbmaj7": "Bb",
    "Bdim": "N.C.",
    "B7": "B7",
    "B9": "B7",
    "B11": "B7",
    "B13": "B7",
    "Bm9": "Bm",
    "Bm11": "Bm",
    "Bm13": "Bm",
    "Bm7b5": "Dm",
    "C7": "C7",
    "C9": "C7",
    "C11": "C7",
    "C13": "C7",
    "Cm7": "Cm",
    "Cm9": "Cm",
    "Cm11": "Cm",
    "Cm13": "Cm",
    "Cdim": "N.C.",
    "Cdim7": "N.C.",
    "C/E": "C",
    "C#m7b5": "Dm",
    "Cadd9": "C",
    "Caug": "C",
    "Cmaj7": "C",
    "Cmaj9": "C",
    "Csus2": "C",
    "D/A": "D",
    "D/F#": "D",
    "Dm7": "Dm",
    "Dm9": "Dm",
    "Dm11": "Dm",
    "Dm13": "Dm",
    "Dm7sus4": "Dm7",
    "Dsus4": "D",
    "Em7": "Em",
    "Em9": "Em",
    "Em11": "Em",
    "Em13": "Em",
    "Eaug": "E",
    "E7sus4": "E7",
    "E/G#": "E",
    "Ebmaj7": "Eb",
    "F7": "F7",
    "F9": "F7",
    "F11": "F7",
    "F13": "F7",
    "Fm7": "Fm",
    "Fm9": "Fm",
    "Fm11": "Fm",
    "Fm13": "Fm",
    "F#m7b5": "Dm",
    "Fadd9": "F",
    "Fmaj7": "F",
    "F/A": "F",
    "G/B": "G",
    "G/D": "G",
    "G7": "G7",
    "G9": "G7",
    "G11": "G7",
    "G13": "G7",
    "Gsus4": "G",
    "A/C": "A",
    "A/E": "A",
    "B/D": "B",
}


def simplify(chord: str) -> str:
    """Reduce a chord symbol to a beginner-friendly ukulele voicing."""
    normalized = _normalize_symbol(chord)
    if not normalized:
        raise ValueError("Chord symbol cannot be empty")
    if normalized == "N.C.":
        return normalized

    direct_match = _EXACT_SIMPLIFICATIONS.get(normalized)
    if direct_match is not None:
        return direct_match

    if "/" in normalized:
        return simplify(normalized.split("/", maxsplit=1)[0])

    return _simplify_suffix(normalized)


def _normalize_symbol(chord: str) -> str:
    """Collapse whitespace and normalize the root note casing."""
    compact = "".join(chord.replace(_FULL_WIDTH_SPACE, " ").split())
    if compact.upper() in _NO_CHORD_MARKERS:
        return "N.C."

    parsed = split_chord_root(compact)
    if parsed is None:
        return compact

    root, suffix = parsed
    for pattern, replacement in _SUFFIX_NORMALIZERS:
        suffix = pattern.sub(replacement, suffix)
    return f"{root}{suffix}"


def _simplify_suffix(chord: str) -> str:
    """Apply stable suffix-based fallback rules when no exact mapping exists."""
    for suffix, replacement in _SUFFIX_RULES:
        if chord.endswith(suffix):
            if replacement == "N.C.":
                return replacement
            return f"{chord.removesuffix(suffix)}{replacement}"
    return chord
