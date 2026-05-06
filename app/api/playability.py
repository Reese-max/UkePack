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
_BEGINNER_FRIENDLY_CHORDS = frozenset({"C", "Dm", "Em", "F", "G", "Am", "A7", "D7", "G7"})


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
        "chord_hints": _build_chord_hints(score),
    }


def _distinct_simplified_chords(score: Score) -> list[str]:
    """Return ordered, simplified chord names used by the score."""
    distinct: list[str] = []
    for chord_event in score.chords:
        simplified = _safe_simplify(chord_event.symbol)
        if simplified == "N.C." or simplified in distinct:
            continue
        distinct.append(simplified)
    return distinct


def _build_chord_hints(score: Score) -> list[dict[str, Any]]:
    """Group unique chords into teacher-facing teaching hints for the analysis page."""
    hints: list[dict[str, Any]] = []
    seen: set[str] = set()
    for chord_event in score.chords:
        symbol = chord_event.symbol.strip()
        if not symbol or symbol in seen or symbol.upper() in {"N.C.", "N.C", "NC"}:
            continue
        seen.add(symbol)
        hints.append(_serialize_chord_hint(symbol, _safe_simplify(symbol)))
    return hints


def _safe_simplify(symbol: str) -> str:
    """Return a simplified symbol, falling back to the original text on parse errors."""
    try:
        return simplify_chord(symbol)
    except ValueError:
        return symbol.strip() or symbol


def _serialize_chord_hint(symbol: str, simplified: str) -> dict[str, Any]:
    """Convert a chord into a template-friendly teaching hint payload."""
    category, label, detail, suggestion = _classify_chord_hint(symbol, simplified)
    return {
        "symbol": symbol,
        "category": category,
        "label": label,
        "detail": detail,
        "suggested_symbol": suggestion,
    }


def _classify_chord_hint(symbol: str, simplified: str) -> tuple[str, str, str, str | None]:
    """Map a chord to a traffic-light style teaching hint."""
    if simplified == "N.C.":
        return (
            "simplify",
            "先省略",
            "這個和弦可先省略，等孩子手感穩了再加回來。",
            None,
        )
    if simplified != symbol:
        return (
            "simplify",
            "先簡化",
            f"原和弦先改成 {simplified}，孩子比較容易跟上。",
            simplified,
        )
    if simplified in _BEGINNER_FRIENDLY_CHORDS:
        return (
            "friendly",
            "可直接教",
            "這是常見入門和弦，可以直接帶孩子練。",
            None,
        )
    return (
        "watch",
        "先慢練",
        "不是常見入門和弦，先慢速換和弦，必要時再降階。",
        None,
    )


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
