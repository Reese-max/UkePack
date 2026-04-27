"""Tests for PDF rendering pipeline (program.md tasks 26-30)."""

from pathlib import Path

import pytest

from app.arrangement.key_advisor import suggest_key
from app.arrangement.level_classifier import classify
from app.arrangement.strum_pattern import suggest_for_level
from app.core.musicxml import parse
from app.models.pack_request import PackRequest
from app.models.score import Score
from app.render.chord_diagram import generate_svg, get_fingering
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
