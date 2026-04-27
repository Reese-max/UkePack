"""Helpers for presenting playability analysis in API and HTML payloads."""

from __future__ import annotations

from typing import Any

from app.arrangement.chord_simplify import simplify as simplify_chord
from app.arrangement.level_classifier import PlayabilityResult
from app.models.score import Score
from app.render.chord_diagram import get_fingering

_PLAYABILITY_FACTORS: tuple[tuple[str, str, int], ...] = (
    ("chord_difficulty", "和弦難度", 30),
    ("chord_change_freq", "換和弦頻率", 20),
    ("melody_position", "旋律把位", 20),
    ("rhythm_complexity", "節奏複雜度", 15),
    ("bpm", "速度", 10),
    ("layout_readability", "版面可讀性", 5),
)


def build_playability_payload(score: Score, result: PlayabilityResult) -> dict[str, Any]:
    """Serialize playability analysis for API and template consumers."""
    distinct_chords = _distinct_simplified_chords(score)
    return {
        "score": result.playability_score,
        "level": result.recommended_level,
        "label": result.label,
        "summary": {
            "distinct_chord_count": len(distinct_chords),
            "total_chord_events": len(score.chords),
            "highest_fret": _highest_fret(distinct_chords),
        },
        "factors": [
            {
                "key": key,
                "label": label,
                "weight": weight,
                "score": round(result.factors[key], 1),
            }
            for key, label, weight in _PLAYABILITY_FACTORS
        ],
    }


def _distinct_simplified_chords(score: Score) -> list[str]:
    """Return ordered, simplified chord names used by the score."""
    distinct: list[str] = []
    for chord_event in score.chords:
        try:
            simplified = simplify_chord(chord_event.symbol)
        except ValueError:
            simplified = chord_event.symbol.strip() or chord_event.symbol
        if simplified == "N.C." or simplified in distinct:
            continue
        distinct.append(simplified)
    return distinct


def _highest_fret(chords: list[str]) -> int | None:
    """Return the highest fret required by known chord diagrams."""
    highest: int | None = None
    for chord_name in chords:
        fingering = get_fingering(chord_name)
        if fingering is None:
            continue
        chord_highest = max(fret for fret in fingering if fret >= 0)
        highest = chord_highest if highest is None else max(highest, chord_highest)
    return highest
