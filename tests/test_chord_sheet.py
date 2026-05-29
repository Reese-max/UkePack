"""Tests for chord-sheet / ChordPro parsing (BACKLOG U2-b)."""

from app.core.chord_sheet import parse_chord_sheet
from app.models import Score


# ── pipe-delimited (existing behavior — regression guard for the refactor) ───


def test_pipe_delimited_sheet_still_parses() -> None:
    score = parse_chord_sheet("Song", "C | G | Am | F")

    assert isinstance(score, Score)
    assert [c.symbol for c in score.chords] == ["C", "G", "Am", "F"]
    assert score.measures == 4
    assert score.key == "C major"


def test_pipe_section_headers_create_manual_sections() -> None:
    score = parse_chord_sheet("Song", "Verse:\nC | G\nChorus:\nAm | F")

    labels = [s.section for s in score.sections]
    assert "verse" in labels
    assert "chorus" in labels


def test_plain_pipe_text_is_not_treated_as_chordpro() -> None:
    score = parse_chord_sheet("s", "C | F | G")

    assert score.key == "C major"
    assert [c.symbol for c in score.chords] == ["C", "F", "G"]


# ── ChordPro ─────────────────────────────────────────────────────────────────


def test_chordpro_inline_chords_extracted_in_order() -> None:
    score = parse_chord_sheet("X", "[C]Amazing [F]grace how [C]sweet the [G]sound")

    assert [c.symbol for c in score.chords] == ["C", "F", "C", "G"]


def test_chordpro_title_directive_overrides_fallback_title() -> None:
    score = parse_chord_sheet("fallback", "{title: Amazing Grace}\n[C]Amazing [F]grace")

    assert score.title == "Amazing Grace"


def test_chordpro_key_directive_major() -> None:
    assert parse_chord_sheet("s", "{key: G}\n[G]x").key == "G major"


def test_chordpro_key_directive_minor() -> None:
    assert parse_chord_sheet("s", "{key: Am}\n[Am]x").key == "A minor"


def test_chordpro_chorus_directive_creates_section() -> None:
    text = "{start_of_chorus}\n[C]la [G]la\n{end_of_chorus}\n[Am]verse [F]bit"
    score = parse_chord_sheet("s", text)

    assert any(s.section == "chorus" for s in score.sections)


def test_chordpro_short_directives_soc_eoc() -> None:
    score = parse_chord_sheet("s", "{soc}\n[C]x [G]y\n{eoc}")

    assert any(s.section == "chorus" for s in score.sections)


def test_chordpro_directive_lines_do_not_add_chords() -> None:
    score = parse_chord_sheet("s", "{title: T}\n{key: C}\n[C]only [G]two chords")

    assert [c.symbol for c in score.chords] == ["C", "G"]


def test_chordpro_preserves_extended_chord_symbols() -> None:
    score = parse_chord_sheet("s", "[Cmaj7]a [F#m7b5]b [G7]c")

    assert [c.symbol for c in score.chords] == ["Cmaj7", "F#m7b5", "G7"]
