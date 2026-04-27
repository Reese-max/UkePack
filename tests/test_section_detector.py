"""Tests for automatic and manual score section detection."""

from app.arrangement.section_detector import _fallback_sections, detect_sections
from app.core.chord_sheet import parse_chord_sheet
from app.models.score import ChordEvent, Score


def test_detect_sections_marks_repeated_phrase_as_chorus() -> None:
    score = Score(
        title="Section Song",
        key="C major",
        measures=12,
        chords=[
            ChordEvent(symbol=symbol, measure=index, beat=1.0)
            for index, symbol in enumerate(
                [
                    "Dm",
                    "G",
                    "C",
                    "G",
                    "Am",
                    "F",
                    "Em",
                    "F",
                    "C",
                    "G",
                    "Am",
                    "F",
                ],
                start=1,
            )
        ],
    )

    sections = detect_sections(score)

    assert [(section.section, section.start_measure, section.end_measure) for section in sections] == [
        ("intro", 1, 2),
        ("chorus", 3, 6),
        ("verse", 7, 8),
        ("chorus", 9, 12),
    ]


def test_detect_sections_falls_back_to_single_verse_without_repetition() -> None:
    score = Score(
        title="Linear Song",
        key="C major",
        measures=4,
        chords=[
            ChordEvent(symbol="C", measure=1, beat=1.0),
            ChordEvent(symbol="Dm", measure=2, beat=1.0),
            ChordEvent(symbol="Em", measure=3, beat=1.0),
            ChordEvent(symbol="F", measure=4, beat=1.0),
        ],
    )

    sections = detect_sections(score)

    assert [(section.section, section.start_measure, section.end_measure) for section in sections] == [
        ("verse", 1, 4)
    ]


def test_detect_sections_returns_empty_for_zero_measure_score() -> None:
    score = Score(title="Silent Song", key="C major", measures=0, chords=[])

    assert detect_sections(score) == []


def test_detect_sections_skips_empty_phrase_windows() -> None:
    score = Score(title="Blank Song", key="C major", measures=4, chords=[])

    sections = detect_sections(score)

    assert [(section.section, section.start_measure, section.end_measure) for section in sections] == [
        ("verse", 1, 4)
    ]


def test_fallback_sections_returns_empty_for_non_positive_measures() -> None:
    assert _fallback_sections(0) == []


def test_parse_chord_sheet_preserves_manual_section_headers() -> None:
    score = parse_chord_sheet(
        "Manual Song",
        "Verse:\nC | G\nChorus:\nAm | F",
    )

    assert [(section.section, section.start_measure, section.end_measure, section.source) for section in score.sections] == [
        ("verse", 1, 2, "manual"),
        ("chorus", 3, 4, "manual"),
    ]
