"""Helpers for converting manual chord sheets into normalized Score models."""

from __future__ import annotations

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


def parse_chord_sheet(title: str, text: str) -> Score:
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
    score = Score(
        title=title,
        key="C major",
        measures=max(measure - 1, 0),
        chords=chords,
        sections=sections,
    )
    if score.sections:
        return score
    return score.model_copy(update={"sections": detect_sections(score)})


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
