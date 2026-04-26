import pytest

from app.arrangement import simplify


@pytest.mark.parametrize(
    ("original", "expected"),
    [
        pytest.param("Cmaj7", "C", id="cmaj7"),
        pytest.param("CMaj7", "C", id="capital-maj"),
        pytest.param("CΔ7", "C", id="delta"),
        pytest.param("Gsus4", "G", id="gsus4"),
        pytest.param("Am7", "Am", id="am7"),
        pytest.param("Fmaj7", "F", id="fmaj7"),
        pytest.param("Dm7", "Dm", id="dm7"),
        pytest.param("G/B", "G", id="g-over-b"),
        pytest.param("Bdim", "N.C.", id="bdim"),
        pytest.param("F#m7b5", "Dm", id="fsharp-half-diminished"),
        pytest.param("Gdim7", "N.C.", id="dim7"),
        pytest.param("Cadd9", "C", id="cadd9"),
        pytest.param("Csus2", "C", id="csus2"),
        pytest.param("Dsus4", "D", id="dsus4"),
        pytest.param("Am9", "Am", id="am9"),
        pytest.param("Bbmaj7", "Bb", id="bbmaj7"),
        pytest.param("Ebmaj7", "Eb", id="ebmaj7"),
        pytest.param("A/C#", "A", id="a-over-csharp"),
        pytest.param("Am/C", "Am", id="am-over-c"),
        pytest.param("D/F#", "D", id="d-over-fsharp"),
        pytest.param("Eaug", "E", id="eaug"),
        pytest.param("G13", "G7", id="g13"),
        pytest.param(" E7sus4 ", "E7", id="whitespace"),
        pytest.param("C　Maj7", "C", id="full-width-space"),
        pytest.param("n.c.", "N.C.", id="no-chord"),
    ],
)
def test_simplify_maps_extended_chords_to_beginner_friendly_shapes(
    original: str, expected: str
) -> None:
    assert simplify(original) == expected


def test_simplify_keeps_unknown_chords_when_no_rule_matches() -> None:
    assert simplify("Em") == "Em"


def test_simplify_rejects_empty_symbols() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        simplify(" \t ")
