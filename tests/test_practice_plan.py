"""Tests for app/render/practice_plan.py — 7-day practice plan builder + PDF drawer."""

from __future__ import annotations

import io

from reportlab.pdfgen import canvas as rl_canvas

from app.models.pack_request import PackRequest
from app.models.score import ChordEvent, Score, ScoreSection
from app.render.practice_plan import DayPlan, build_plan, draw_practice_plan


def _req(
    level: int = 1,
    bpm: int | None = 100,
    chords: list[str] | None = None,
    sections: list[tuple[str, int, int]] | None = None,
) -> PackRequest:
    """Build a minimal PackRequest for testing."""
    chord_events = [
        ChordEvent(symbol=s, measure=i + 1, beat=1.0)
        for i, s in enumerate(chords if chords is not None else ["C", "G", "Am", "F"])
    ]
    score_sections = [
        ScoreSection(section=s, start_measure=a, end_measure=b)
        for s, a, b in (sections if sections is not None else [])
    ]
    score = Score(
        title="Test Song",
        key="C",
        bpm=bpm,
        measures=16,
        chords=chord_events,
        sections=score_sections,
    )
    return PackRequest(title="Test Song", level=level, score=score)


class TestBuildPlan:
    """Unit tests for build_plan()."""

    def test_returns_7_days_for_level_1(self) -> None:
        plans = build_plan(_req(level=1))
        assert len(plans) == 7
        assert all(isinstance(p, DayPlan) for p in plans)
        assert [p.day for p in plans] == [1, 2, 3, 4, 5, 6, 7]

    def test_returns_7_days_for_level_2(self) -> None:
        plans = build_plan(_req(level=2))
        assert len(plans) == 7

    def test_returns_7_days_for_level_3(self) -> None:
        plans = build_plan(_req(level=3))
        assert len(plans) == 7

    def test_level_1_day_1_mentions_chords(self) -> None:
        plans = build_plan(_req(level=1, chords=["C", "G", "Am", "F"]))
        assert "C" in plans[0].detail
        assert "G" in plans[0].detail

    def test_level_1_uses_slow_bpm_in_details(self) -> None:
        plans = build_plan(_req(level=1, bpm=120))
        # 50% of 120 = 60
        assert "60" in plans[2].detail

    def test_level_2_mentions_sections_when_available(self) -> None:
        sections = [("verse", 1, 8), ("chorus", 9, 16)]
        plans = build_plan(_req(level=2, sections=sections))
        # build_plan uses raw section names from _section_names (no translation)
        day3_detail = plans[2].detail
        day4_detail = plans[3].detail
        assert "verse" in day3_detail
        assert "chorus" in day4_detail

    def test_level_3_mentions_section_chain(self) -> None:
        sections = [("intro", 1, 4), ("verse", 5, 12), ("chorus", 13, 16)]
        plans = build_plan(_req(level=3, sections=sections))
        chain_detail = plans[2].detail
        assert "前奏" in chain_detail or "intro" in chain_detail

    def test_no_bpm_defaults_to_safe_value(self) -> None:
        plans = build_plan(_req(level=1, bpm=None))
        assert len(plans) == 7
        # Should not crash, and detail strings should still be populated
        assert all(p.detail for p in plans)

    def test_no_chords_still_produces_plan(self) -> None:
        plans = build_plan(_req(level=1, chords=[]))
        assert len(plans) == 7
        # Empty chords triggers fallback text, not specific chord names
        assert "歌曲和弦" in plans[0].detail

    def test_many_chords_truncated_at_4_in_summary(self) -> None:
        chords = ["C", "G", "Am", "F", "Dm", "Em"]
        plans = build_plan(_req(level=1, chords=chords))
        # Day 1 detail should mention first 4 chords + a 5th with "、"
        assert "C" in plans[0].detail
        assert "Dm" in plans[0].detail

    def test_frozen_dataclass(self) -> None:
        plan = DayPlan(day=1, goal="test", detail="test")
        try:
            plan.day = 2  # type: ignore[misc]
            raise AssertionError("should be frozen")
        except AttributeError:
            pass


class TestDrawPracticePlan:
    """Smoke tests for draw_practice_plan() — verifies PDF rendering doesn't crash."""

    def test_draw_returns_y_coordinate(self) -> None:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf)
        y = draw_practice_plan(c, _req(level=1), y=700.0)
        assert y < 700.0, "y should decrease after drawing"
        c.save()

    def test_draw_level_1(self) -> None:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf)
        y = draw_practice_plan(c, _req(level=1), y=700.0)
        assert isinstance(y, float)
        c.save()

    def test_draw_level_2(self) -> None:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf)
        y = draw_practice_plan(c, _req(level=2), y=700.0)
        assert isinstance(y, float)
        c.save()

    def test_draw_level_3(self) -> None:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf)
        y = draw_practice_plan(c, _req(level=3), y=700.0)
        assert isinstance(y, float)
        c.save()

    def test_draw_with_no_bpm(self) -> None:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf)
        y = draw_practice_plan(c, _req(level=1, bpm=None), y=700.0)
        assert isinstance(y, float)
        c.save()

    def test_draw_with_no_chords(self) -> None:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf)
        y = draw_practice_plan(c, _req(level=1, chords=[]), y=700.0)
        assert isinstance(y, float)
        c.save()
