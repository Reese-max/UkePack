"""Heuristic section detection for Intro / Verse / Chorus blocks."""

from __future__ import annotations

from dataclasses import dataclass

from app.models import ChordEvent, Score
from app.models.score import ScoreSection


@dataclass(frozen=True)
class _RepeatedPhrase:
    length: int
    starts: tuple[int, ...]


def detect_sections(score: Score) -> list[ScoreSection]:
    """Detect Intro / Verse / Chorus spans from per-measure chord repetition."""
    signatures = _measure_signatures(score.chords, score.measures)
    if not signatures:
        return []
    chorus = _best_repeated_phrase(signatures)
    if chorus is None:
        return _fallback_sections(len(signatures))
    return _merge_adjacent_sections(_build_sections(len(signatures), chorus))


def _measure_signatures(
    chords: list[ChordEvent], measure_count: int
) -> list[tuple[str, ...]]:
    grouped: dict[int, list[str]] = {}
    for chord_event in chords:
        grouped.setdefault(chord_event.measure, []).append(chord_event.symbol)
    return [tuple(grouped.get(measure, [])) for measure in range(1, measure_count + 1)]


def _best_repeated_phrase(
    signatures: list[tuple[str, ...]],
) -> _RepeatedPhrase | None:
    best: _RepeatedPhrase | None = None
    max_length = min(8, len(signatures) // 2)
    for length in range(2, max_length + 1):
        by_window: dict[tuple[tuple[str, ...], ...], list[int]] = {}
        limit = len(signatures) - length + 1
        for offset in range(limit):
            window = tuple(signatures[offset : offset + length])
            if not any(window):
                continue
            by_window.setdefault(window, []).append(offset + 1)
        for starts in by_window.values():
            candidate = _candidate_phrase(starts, length)
            if candidate is not None and _is_better_candidate(candidate, best):
                best = candidate
    return best


def _candidate_phrase(starts: list[int], length: int) -> _RepeatedPhrase | None:
    non_overlapping: list[int] = []
    last_end = 0
    for start in starts:
        if start <= last_end:
            continue
        non_overlapping.append(start)
        last_end = start + length - 1
    if len(non_overlapping) < 2:
        return None
    return _RepeatedPhrase(length=length, starts=tuple(non_overlapping))


def _is_better_candidate(
    candidate: _RepeatedPhrase, current: _RepeatedPhrase | None
) -> bool:
    if current is None:
        return True
    candidate_score = candidate.length * len(candidate.starts)
    current_score = current.length * len(current.starts)
    if candidate_score != current_score:
        return candidate_score > current_score
    if candidate.length != current.length:
        return candidate.length > current.length
    return candidate.starts[0] < current.starts[0]


def _fallback_sections(measure_count: int) -> list[ScoreSection]:
    if measure_count <= 0:
        return []
    label = "intro" if measure_count <= 2 else "verse"
    return [
        ScoreSection(
            section=label,
            start_measure=1,
            end_measure=measure_count,
            source="detected",
        )
    ]


def _build_sections(
    measure_count: int, chorus: _RepeatedPhrase
) -> list[ScoreSection]:
    sections: list[ScoreSection] = []
    chorus_starts = list(chorus.starts)
    cursor = 1
    index = 0
    while cursor <= measure_count:
        next_chorus = chorus_starts[index] if index < len(chorus_starts) else None
        if next_chorus is not None and cursor == next_chorus:
            sections.append(
                ScoreSection(
                    section="chorus",
                    start_measure=cursor,
                    end_measure=min(measure_count, cursor + chorus.length - 1),
                    source="detected",
                )
            )
            cursor += chorus.length
            index += 1
            continue
        boundary = next_chorus if next_chorus is not None else measure_count + 1
        label = "intro" if not sections and boundary - cursor <= 2 else "verse"
        sections.append(
            ScoreSection(
                section=label,
                start_measure=cursor,
                end_measure=boundary - 1,
                source="detected",
            )
        )
        cursor = boundary
    return sections


def _merge_adjacent_sections(sections: list[ScoreSection]) -> list[ScoreSection]:
    merged: list[ScoreSection] = []
    for section in sections:
        if (
            merged
            and merged[-1].section == section.section
            and merged[-1].source == section.source
            and merged[-1].end_measure + 1 == section.start_measure
        ):
            merged[-1] = ScoreSection(
                section=section.section,
                start_measure=merged[-1].start_measure,
                end_measure=section.end_measure,
                source=section.source,
            )
            continue
        merged.append(section)
    return merged
