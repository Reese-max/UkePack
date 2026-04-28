"""Tests for PDF rendering pipeline (program.md tasks 26-30)."""

import io
from pathlib import Path

import pytest
from reportlab.pdfgen import canvas as rl_canvas

from app.arrangement.key_advisor import suggest_key
from app.arrangement.level_classifier import classify
from app.arrangement.strum_pattern import suggest_for_level
from app.core.musicxml import parse
from app.models.pack_request import PackRequest
from app.models.score import ChordEvent, Score, ScoreSection
from app.models.teacher_review import TeacherReviewDraft
from app.render import _layout as layout_module
from app.render.chord_diagram import generate_svg, get_fingering
from app.render.pages import page1 as page1_module
from app.render.pages import page2 as page2_module
from app.render.pages import page3 as page3_module
from app.render.pdf import render_pdf

_FIXTURE_DIR = Path(__file__).parent / "fixtures"
_SAMPLE_FIXTURES = sorted(_FIXTURE_DIR.glob("*.musicxml"))[:3]


class TestChordDiagram:
    def test_known_chord_returns_svg(self) -> None:
        svg = generate_svg("C")
        assert "<svg" in svg
        assert "C" in svg

    def test_all_known_chords_produce_svg(self) -> None:
        for name in ("C", "G", "Am", "F", "G7", "Dm", "D", "A", "A7", "Em"):
            svg = generate_svg(name)
            assert "<svg" in svg, f"Expected SVG for {name}"

    def test_nc_chord(self) -> None:
        svg = generate_svg("N.C.")
        assert "N.C." in svg
        assert "<svg" in svg

    def test_unknown_chord_returns_fallback_svg(self) -> None:
        svg = generate_svg("Xyz123")
        assert "<svg" in svg
        assert "Xyz123" in svg

    def test_high_fret_chord_shows_position_indicator(self) -> None:
        # Ab has fret 5, should trigger fret position indicator "3fr"
        svg = generate_svg("Ab")
        assert "fr" in svg

    def test_get_fingering_known(self) -> None:
        f = get_fingering("C")
        assert f is not None
        assert len(f) == 4

    def test_get_fingering_unknown_returns_none(self) -> None:
        assert get_fingering("XyzUnknown") is None

    def test_svg_contains_open_circle_for_open_string(self) -> None:
        # Am = (2,0,0,0) — three open strings
        svg = generate_svg("Am")
        assert 'fill="white"' in svg  # open string circles

    def test_svg_contains_filled_dot_for_fretted_string(self) -> None:
        # C = (0,0,0,3) — one fretted string
        svg = generate_svg("C")
        assert 'fill="black"' in svg


class TestRenderPdf:
    def _minimal_request(self, source_type: str = "public_domain") -> PackRequest:
        score = Score(title="Test Song", key="C major", measures=8)
        return PackRequest(title="Test Song", source_type=source_type, level=1, score=score)

    def test_render_returns_pdf_bytes(self) -> None:
        req = self._minimal_request()
        result = render_pdf(req)
        assert isinstance(result, bytes)
        assert result[:4] == b"%PDF"
        assert len(result) > 200

    def test_render_all_source_types(self) -> None:
        for st in (
            "self_created",
            "suno_free",
            "suno_paid",
            "public_domain",
            "licensed",
            "private_research",
        ):
            req = self._minimal_request(source_type=st)
            pdf = render_pdf(req)
            assert pdf[:4] == b"%PDF", f"Invalid PDF for source_type={st}"

    def test_render_all_levels(self) -> None:
        for level in (1, 2, 3):
            score = Score(title="L Test", key="G major", measures=4)
            req = PackRequest(title="Level Test", level=level, score=score)
            pdf = render_pdf(req)
            assert pdf[:4] == b"%PDF"

    @pytest.mark.parametrize("fixture_path", _SAMPLE_FIXTURES)
    def test_render_from_musicxml_fixture(self, fixture_path: Path) -> None:
        """Full pipeline: parse MusicXML → classify → render PDF."""
        score = parse(fixture_path)
        key_rec = suggest_key(score)
        playability = classify(score)
        strum = suggest_for_level(score, playability.recommended_level)
        req = PackRequest(
            title=score.title,
            source_type="public_domain",
            level=playability.recommended_level,
            score=score,
            key_recommendation=key_rec,
            strum_patterns=strum,
            playability=playability,
        )
        pdf_bytes = render_pdf(req)
        assert pdf_bytes[:4] == b"%PDF"
        assert len(pdf_bytes) > 500

    def test_chord_box_falls_back_when_svglib_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        buffer = io.BytesIO()
        canvas = rl_canvas.Canvas(buffer)
        monkeypatch.setattr(layout_module, "_HAS_SVGLIB", False)

        layout_module.chord_box(canvas, "C", 20.0, 20.0, 115.0, 150.0)
        canvas.save()

        assert buffer.getvalue()[:4] == b"%PDF"

    def test_chord_box_falls_back_when_svg_drawing_is_invalid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class EmptyDrawing:
            width = 0
            height = 120

        buffer = io.BytesIO()
        canvas = rl_canvas.Canvas(buffer)
        monkeypatch.setattr(layout_module, "_HAS_SVGLIB", True)
        monkeypatch.setattr(layout_module, "svg2rlg", lambda path: EmptyDrawing(), raising=False)

        layout_module.chord_box(canvas, "G", 20.0, 20.0, 115.0, 150.0)
        canvas.save()

        assert buffer.getvalue()[:4] == b"%PDF"

    def test_chord_progression_stops_at_page_bottom(self) -> None:
        buffer = io.BytesIO()
        canvas = rl_canvas.Canvas(buffer)
        chords = [
            ChordEvent(symbol="C", measure=index + 1, beat=1.0)
            for index in range(32)
        ]

        page3_module._chord_progression(canvas, chords, y_start=110.0)
        canvas.save()

        assert buffer.getvalue()[:4] == b"%PDF"

    def test_render_page3_draws_section_summary_when_sections_exist(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        called: list[int] = []

        def _spy(canvas: rl_canvas.Canvas, sections: list[ScoreSection], y_start: float) -> float:
            called.append(len(sections))
            return y_start

        monkeypatch.setattr(page3_module, "_section_summary", _spy)
        buffer = io.BytesIO()
        canvas = rl_canvas.Canvas(buffer)
        score = Score(
            title="Sections",
            key="C major",
            measures=4,
            chords=[ChordEvent(symbol="C", measure=1, beat=1.0)],
            sections=[
                ScoreSection(section="verse", start_measure=1, end_measure=2),
                ScoreSection(section="chorus", start_measure=3, end_measure=4),
            ],
        )

        page3_module.render_page3(canvas, PackRequest(title="Sections", score=score))
        canvas.save()

        assert called == [2]

    def test_unique_chords_preserves_raw_symbol_when_simplify_fails(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        score = Score(
            title="Fallback",
            key="C major",
            measures=1,
            chords=[ChordEvent(symbol="???", measure=1, beat=1.0)],
        )

        def _boom(symbol: str) -> str:
            raise ValueError(symbol)

        monkeypatch.setattr("app.arrangement.chord_simplify.simplify", _boom)

        assert layout_module.unique_chords(score) == ["???"]


class TestTeacherReviewPdfOverrides:
    """Exercises teacher review override paths in page renderers (page1:57-73/100-110,
    page2:32-46, page3:30-32/46-63).  These paths are used when a teacher has saved
    review overrides before exporting the PDF."""

    def _canvas(self) -> tuple[io.BytesIO, rl_canvas.Canvas]:
        buf = io.BytesIO()
        return buf, rl_canvas.Canvas(buf)

    def _score(self) -> Score:
        return Score(
            title="Test",
            key="C major",
            measures=4,
            chords=[ChordEvent(symbol="C", measure=1, beat=1.0)],
        )

    def test_page1_teacher_strum_with_description(self) -> None:
        """page1.py:57-73 — teacher strum override with strum_description."""
        buf, c = self._canvas()
        review = TeacherReviewDraft(
            strum_name="慢搖",
            strum_notation="D-DU-UDU",
            strum_description="每拍一次，輕鬆掃弦",
        )
        req = PackRequest(
            title="Strum Override", score=self._score(), teacher_review=review
        )
        page1_module.render_page1(c, req)
        c.save()
        assert buf.getvalue()[:4] == b"%PDF"

    def test_page1_teacher_strum_without_description(self) -> None:
        """page1.py:57-64 — teacher strum override, empty strum_description skips that block."""
        buf, c = self._canvas()
        review = TeacherReviewDraft(strum_name="快搖", strum_notation="DUDU")
        req = PackRequest(
            title="Strum No Desc", score=self._score(), teacher_review=review
        )
        page1_module.render_page1(c, req)
        c.save()
        assert buf.getvalue()[:4] == b"%PDF"

    def test_page1_teacher_practice_notes_multiline(self) -> None:
        """page1.py:100-110 — teacher practice notes with blank lines (exercises the skip)."""
        buf, c = self._canvas()
        review = TeacherReviewDraft(
            practice_notes="第一行：先學 C 和弦\n\n第二行：再練 G 和弦\n第三行：最後換弦"
        )
        req = PackRequest(
            title="Practice Notes", score=self._score(), teacher_review=review
        )
        page1_module.render_page1(c, req)
        c.save()
        assert buf.getvalue()[:4] == b"%PDF"

    def test_page2_teacher_strum_with_description(self) -> None:
        """page2.py:32-46 — teacher strum override with strum_description on page 2."""
        buf, c = self._canvas()
        review = TeacherReviewDraft(
            strum_name="標準",
            strum_notation="D-DU",
            strum_description="穩定拍子",
        )
        req = PackRequest(
            title="Page2 Strum", score=self._score(), teacher_review=review
        )
        page2_module.render_page2(c, req)
        c.save()
        assert buf.getvalue()[:4] == b"%PDF"

    def test_page2_teacher_strum_without_description(self) -> None:
        """page2.py:31-37 — teacher strum override, no strum_description."""
        buf, c = self._canvas()
        review = TeacherReviewDraft(strum_name="慢", strum_notation="D--D")
        req = PackRequest(
            title="Page2 No Desc", score=self._score(), teacher_review=review
        )
        page2_module.render_page2(c, req)
        c.save()
        assert buf.getvalue()[:4] == b"%PDF"

    def test_page3_teacher_tab_notes(self) -> None:
        """page3.py:30-32,46-63 — teacher tab_notes triggers _tab_notes render path."""
        buf, c = self._canvas()
        review = TeacherReviewDraft(
            tab_notes="A----|-----\nB----|-----\n\n(空白行測試)"
        )
        req = PackRequest(
            title="Page3 Tabs", score=self._score(), teacher_review=review
        )
        page3_module.render_page3(c, req)
        c.save()
        assert buf.getvalue()[:4] == b"%PDF"

    def test_full_pdf_with_teacher_review_all_fields(self) -> None:
        """Full render_pdf with teacher review overrides covering all 4 pages."""
        review = TeacherReviewDraft(
            arrangement_level=2,
            chords_text="C|G|Am|F",
            strum_name="Calypso",
            strum_notation="D-DU-UDU",
            strum_description="節奏感強",
            tab_notes="0-2-3-2-0",
            practice_notes="注意換弦速度\n保持穩定節拍",
        )
        score = Score(
            title="Review Song",
            key="C major",
            measures=8,
            chords=[
                ChordEvent(symbol="C", measure=1, beat=1.0),
                ChordEvent(symbol="G", measure=2, beat=1.0),
                ChordEvent(symbol="Am", measure=3, beat=1.0),
                ChordEvent(symbol="F", measure=4, beat=1.0),
            ],
            sections=[
                ScoreSection(section="verse", start_measure=1, end_measure=4),
                ScoreSection(section="chorus", start_measure=5, end_measure=8),
            ],
        )
        req = PackRequest(
            title="Review Song",
            source_type="public_domain",
            level=2,
            score=score,
            teacher_review=review,
        )
        pdf = render_pdf(req)
        assert pdf[:4] == b"%PDF"
        assert len(pdf) > 500
