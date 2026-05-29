"""Convert manual chord sheets (pipe-delimited or ChordPro) into Score models."""

from __future__ import annotations

import re

from app.arrangement.section_detector import detect_sections
from app.models import ChordEvent, Score
from app.models.score import ScoreSection

_SECTION_ALIASES = {
    "intro": "intro",
    "前奏": "intro",
    "verse": "verse",
    "主歌": "verse",
    "chorus": "chorus",
    "副歌": "chorus",
    "hook": "chorus",
}

# ChordPro tokens: inline [C] chords and {directive: value} metadata.
_CHORDPRO_CHORD = re.compile(r"\[([^\]]+)\]")
_CHORDPRO_DIRECTIVE = re.compile(r"\{\s*([a-zA-Z_]+)\s*:?\s*([^}]*)\}")
_CHORDPRO_TITLE_KEYS = {"title", "t"}
_CHORDPRO_KEY_KEYS = {"key", "k"}
_CHORDPRO_SECTION_START = {
    "start_of_chorus": "chorus",
    "soc": "chorus",
    "start_of_verse": "verse",
    "sov": "verse",
    "start_of_bridge": "bridge",
    "sob": "bridge",
}
_CHORDPRO_SECTION_END = {"end_of_chorus", "eoc", "end_of_verse", "eov", "end_of_bridge", "eob"}
_KEY_TOKEN = re.compile(r"^([A-G][#b]?)(m|min|minor)?$")


def parse_chord_sheet(title: str, text: str) -> Score:
    """Parse a chord sheet into a normalized Score (ChordPro or pipe-delimited)."""
    if _is_chordpro(text):
        return _parse_chordpro(title, text)
    return _parse_pipe_sheet(title, text)


def _is_chordpro(text: str) -> bool:
    """Detect ChordPro by the presence of inline [chords] or {directives}."""
    return bool(_CHORDPRO_CHORD.search(text) or _CHORDPRO_DIRECTIVE.search(text))


def _parse_pipe_sheet(title: str, text: str) -> Score:
    """Parse pipe-delimited chord text and preserve manual section headers."""
    chords: list[ChordEvent] = []
    sections: list[ScoreSection] = []
    measure = 1
    active_label: str | None = None
    active_start = 1
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith(":"):
            _close_manual_section(sections, active_label, active_start, measure)
            active_label = _normalize_section_name(line[:-1])
            active_start = measure
            continue
        for token in line.split("|"):
            symbol = token.strip()
            if symbol:
                chords.append(ChordEvent(symbol=symbol, measure=measure, beat=1.0))
                measure += 1
    _close_manual_section(sections, active_label, active_start, measure)
    return _finalize(title, "C major", chords, sections, measure)


def _parse_chordpro(title: str, text: str) -> Score:
    """Parse ChordPro: inline [chords], {title}/{key} meta, and section directives."""
    chords: list[ChordEvent] = []
    sections: list[ScoreSection] = []
    measure = 1
    active_label: str | None = None
    active_start = 1
    resolved_title = title
    resolved_key = "C major"

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        for name, value in _CHORDPRO_DIRECTIVE.findall(line):
            directive = name.strip().lower()
            stripped_value = value.strip()
            if directive in _CHORDPRO_TITLE_KEYS and stripped_value:
                resolved_title = stripped_value
            elif directive in _CHORDPRO_KEY_KEYS and stripped_value:
                resolved_key = _normalize_key(stripped_value)
            elif directive in _CHORDPRO_SECTION_START:
                _close_manual_section(sections, active_label, active_start, measure)
                active_label = _CHORDPRO_SECTION_START[directive]
                active_start = measure
            elif directive in _CHORDPRO_SECTION_END:
                _close_manual_section(sections, active_label, active_start, measure)
                active_label = None
                active_start = measure
        for raw_symbol in _CHORDPRO_CHORD.findall(_CHORDPRO_DIRECTIVE.sub("", line)):
            symbol = raw_symbol.strip()
            if symbol:
                chords.append(ChordEvent(symbol=symbol, measure=measure, beat=1.0))
                measure += 1
    _close_manual_section(sections, active_label, active_start, measure)
    return _finalize(resolved_title, resolved_key, chords, sections, measure)


def _finalize(
    title: str,
    key: str,
    chords: list[ChordEvent],
    sections: list[ScoreSection],
    measure: int,
) -> Score:
    """Assemble the Score, falling back to auto section detection when none are manual."""
    score = Score(
        title=title,
        key=key,
        measures=max(measure - 1, 0),
        chords=chords,
        sections=sections,
    )
    if score.sections:
        return score
    return score.model_copy(update={"sections": detect_sections(score)})


def _normalize_key(value: str) -> str:
    """Map a ChordPro key (e.g. 'G', 'Am') to the app's 'tonic mode' format."""
    cleaned = value.strip()
    if " " in cleaned:
        return cleaned
    match = _KEY_TOKEN.match(cleaned)
    if match is None:
        return "C major"
    tonic, minor = match.group(1), match.group(2)
    return f"{tonic} minor" if minor else f"{tonic} major"


def _close_manual_section(
    sections: list[ScoreSection],
    label: str | None,
    start_measure: int,
    next_measure: int,
) -> None:
    if label is None or next_measure <= start_measure:
        return
    sections.append(
        ScoreSection(
            section=label,
            start_measure=start_measure,
            end_measure=next_measure - 1,
            source="manual",
        )
    )


def _normalize_section_name(raw_name: str) -> str:
    normalized = raw_name.strip().strip("[]()").replace(" ", "").lower()
    return _SECTION_ALIASES.get(normalized, "verse")
