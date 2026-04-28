"""Unit tests for teacher_review core module edge-case branches.

Covers lines that the API integration tests miss:
  - _review_path: project.id is None (line 48)
  - save_teacher_review_template: empty name (line 125)
  - review_score: non-empty chords_text path (line 152)
  - parse_review_chord_sheet: empty lines, empty tokens, empty chords, no-sections path
    (lines 165, 174, 180, 184)
  - _primary_pattern: empty score with no patterns (line 206)
  - _validate_level: invalid level (line 213)
  - _score_to_chord_text: empty chords (219), section with no matching measures (230),
    uncovered measures (236)
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from app.core.teacher_review import (
    _primary_pattern,
    _review_path,
    _score_to_chord_text,
    _validate_level,
    parse_review_chord_sheet,
    review_score,
    save_teacher_review_template,
)
from app.models.project import Project
from app.models.score import ChordEvent, Score, ScoreSection
from app.models.teacher_review import TeacherReviewDraft, TeacherReviewState


def _make_project(*, project_id: int | None = 1, level: int = 1) -> Project:
    return Project(
        id=project_id,
        title="Test Song",
        source_type="public_domain",
        arrangement_level=level,
        created_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
    )


def _make_score(
    *,
    chords: list[ChordEvent] | None = None,
    sections: list[ScoreSection] | None = None,
) -> Score:
    return Score(
        title="Test",
        key="C major",
        measures=4,
        chords=chords or [],
        sections=sections or [],
    )


class TestReviewPath:
    def test_raises_when_project_id_is_none(self) -> None:
        project = _make_project(project_id=None)
        with pytest.raises(ValueError, match="must be saved"):
            _review_path(project)


class TestSaveTeacherReviewTemplate:
    def test_raises_on_empty_template_name(self, tmp_path: pytest.TempPathFactory) -> None:
        # save_teacher_review_template calls load_teacher_review first; we need a project
        # with a review already persisted in tmp data_dir.  Use monkeypatch-free approach:
        # the empty-name guard fires before any I/O, so we can trigger it with a patch.
        project = _make_project()
        score = _make_score()
        draft = TeacherReviewDraft()
        state = TeacherReviewState(original=draft, current=draft.model_copy())

        with (
            patch("app.core.teacher_review.load_teacher_review", return_value=state),
            patch("app.core.teacher_review.save_teacher_review", return_value=state),
            pytest.raises(ValueError, match="Template name is required"),
        ):
            save_teacher_review_template(project, score, "")

    def test_raises_on_whitespace_only_template_name(self) -> None:
        project = _make_project()
        score = _make_score()
        draft = TeacherReviewDraft()
        state = TeacherReviewState(original=draft, current=draft.model_copy())

        with (
            patch("app.core.teacher_review.load_teacher_review", return_value=state),
            patch("app.core.teacher_review.save_teacher_review", return_value=state),
            pytest.raises(ValueError, match="Template name is required"),
        ):
            save_teacher_review_template(project, score, "   ")


class TestReviewScore:
    def test_returns_parsed_score_when_chords_text_present(self) -> None:
        """review_score() line 152: non-empty chords_text triggers parse_review_chord_sheet."""
        project = _make_project()
        draft = TeacherReviewDraft(chords_text="C | G | Am | F")
        state = TeacherReviewState(original=draft, current=draft.model_copy())
        fallback = _make_score()
        result = review_score(project, state, fallback)
        # Should return a parsed score, not the fallback
        assert len(result.chords) == 4

    def test_returns_fallback_when_chords_text_empty(self) -> None:
        project = _make_project()
        draft = TeacherReviewDraft(chords_text="")
        state = TeacherReviewState(original=draft, current=draft.model_copy())
        fallback = _make_score(chords=[ChordEvent(symbol="C", measure=1, beat=1.0)])
        result = review_score(project, state, fallback)
        assert result is fallback


class TestParseReviewChordSheet:
    def test_empty_lines_and_tokens_are_skipped(self) -> None:
        """Lines 165, 174: empty lines and empty pipe tokens are skipped."""
        result = parse_review_chord_sheet("Song", "C | G\n\n| Am |")
        symbols = [ce.symbol for ce in result.chords]
        # "C", "G" from first non-empty line; "Am" from third (empty leading token skipped)
        assert "C" in symbols
        assert "G" in symbols
        assert "Am" in symbols

    def test_raises_on_completely_empty_input(self) -> None:
        """Line 180: empty chords after parsing → ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_review_chord_sheet("Song", "")

    def test_raises_on_whitespace_only_input(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_review_chord_sheet("Song", "   \n\n  ")

    def test_raises_on_pipe_only_input(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_review_chord_sheet("Song", "| | |")

    def test_auto_detects_sections_when_none_provided(self) -> None:
        """Line 184: when no section headers are in text, detect_sections() is called."""
        result = parse_review_chord_sheet("Song", "C | G | C | G | Am | F | Am | F")
        # sections should be auto-detected (not manual)
        assert result.sections  # detect_sections should find something
        for sec in result.sections:
            assert sec.source != "manual"

    def test_manual_section_headers_preserved(self) -> None:
        text = "Verse:\nC | G\nChorus:\nAm | F"
        result = parse_review_chord_sheet("Song", text)
        assert any(s.source == "manual" for s in result.sections)


class TestPrimaryPattern:
    def test_returns_default_when_no_patterns(self) -> None:
        """Line 206: _primary_pattern returns placeholder when suggest_for_level returns []."""
        score = _make_score()
        with patch("app.core.teacher_review.suggest_for_level", return_value=[]):
            _name, _notation, _description = _primary_pattern(score, 1)
        assert _name == "老師自訂刷法"
        assert _notation == ""
        assert _description == ""


class TestValidateLevel:
    def test_raises_on_invalid_level(self) -> None:
        """Line 213: levels outside {1, 2, 3} raise ValueError."""
        with pytest.raises(ValueError, match="must be 1, 2, or 3"):
            _validate_level(0)
        with pytest.raises(ValueError, match="must be 1, 2, or 3"):
            _validate_level(4)

    def test_valid_levels_pass(self) -> None:
        for level in (1, 2, 3):
            _validate_level(level)  # should not raise


class TestScoreToChordText:
    def test_returns_empty_string_when_no_chords(self) -> None:
        """Line 219: empty by_measure → returns ''."""
        score = _make_score(chords=[])
        assert _score_to_chord_text(score) == ""

    def test_section_with_no_matching_measures_is_skipped(self) -> None:
        """Line 230: section whose measures don't appear in by_measure is skipped."""
        chords = [ChordEvent(symbol="C", measure=1, beat=1.0)]
        # Section claims measures 5-8 but only measure 1 has a chord → section_lines is empty
        sections = [ScoreSection(section="chorus", start_measure=5, end_measure=8)]
        score = _make_score(chords=chords, sections=sections)
        text = _score_to_chord_text(score)
        # Measure 1 (not in any section) should still appear without a header
        assert "C" in text
        # "Chorus:" header should be omitted (no matching measures)
        assert "Chorus:" not in text

    def test_uncovered_measures_appended_after_sections(self) -> None:
        """Line 236: measures not covered by any section appear at end."""
        chords = [
            ChordEvent(symbol="C", measure=1, beat=1.0),
            ChordEvent(symbol="G", measure=2, beat=1.0),
            ChordEvent(symbol="Am", measure=3, beat=1.0),
        ]
        sections = [ScoreSection(section="verse", start_measure=1, end_measure=2)]
        score = _make_score(chords=chords, sections=sections)
        text = _score_to_chord_text(score)
        lines = [ln for ln in text.splitlines() if ln.strip()]
        # Should have section header + 2 section lines + 1 uncovered (Am measure 3)
        assert any("Am" in line for line in lines)
