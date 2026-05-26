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
        pytest.param("Cdim", "N.C.", id="cdim"),
        pytest.param("Cdim7", "N.C.", id="cdim7"),
        pytest.param("F#m7b5", "Dm", id="fsharp-half-diminished"),
        pytest.param("C#m7b5", "Dm", id="csharp-half-diminished"),
        pytest.param("Gdim7", "N.C.", id="dim7"),
        pytest.param("A7", "A7", id="a7"),
        pytest.param("A9", "A7", id="a9"),
        pytest.param("A11", "A7", id="a11"),
        pytest.param("A13", "A7", id="a13"),
        pytest.param("Am11", "Am", id="am11"),
        pytest.param("Am13", "Am", id="am13"),
        pytest.param("B7", "B7", id="b7"),
        pytest.param("B9", "B7", id="b9"),
        pytest.param("B11", "B7", id="b11"),
        pytest.param("B13", "B7", id="b13"),
        pytest.param("Bm9", "Bm", id="bm9"),
        pytest.param("Bm11", "Bm", id="bm11"),
        pytest.param("Bm13", "Bm", id="bm13"),
        pytest.param("C7", "C7", id="c7"),
        pytest.param("C9", "C7", id="c9"),
        pytest.param("C11", "C7", id="c11"),
        pytest.param("C13", "C7", id="c13"),
        pytest.param("Cm7", "Cm", id="cm7"),
        pytest.param("Cm9", "Cm", id="cm9"),
        pytest.param("Cm11", "Cm", id="cm11"),
        pytest.param("Cm13", "Cm", id="cm13"),
        pytest.param("Cadd9", "C", id="cadd9"),
        pytest.param("Csus2", "C", id="csus2"),
        pytest.param("Dsus4", "D", id="dsus4"),
        pytest.param("Dm9", "Dm", id="dm9"),
        pytest.param("Dm11", "Dm", id="dm11"),
        pytest.param("Dm13", "Dm", id="dm13"),
        pytest.param("Dm7sus4", "Dm7", id="dm7sus4"),
        pytest.param("Am9", "Am", id="am9"),
        pytest.param("Bbmaj7", "Bb", id="bbmaj7"),
        pytest.param("Ebmaj7", "Eb", id="ebmaj7"),
        pytest.param("F7", "F7", id="f7"),
        pytest.param("F9", "F7", id="f9"),
        pytest.param("F11", "F7", id="f11"),
        pytest.param("F13", "F7", id="f13"),
        pytest.param("Fm7", "Fm", id="fm7"),
        pytest.param("Fm9", "Fm", id="fm9"),
        pytest.param("Fm11", "Fm", id="fm11"),
        pytest.param("Fm13", "Fm", id="fm13"),
        pytest.param("A/C#", "A", id="a-over-csharp"),
        pytest.param("Am/C", "Am", id="am-over-c"),
        pytest.param("D/F#", "D", id="d-over-fsharp"),
        pytest.param("D/A", "D", id="d-over-a"),
        pytest.param("F/A", "F", id="f-over-a"),
        pytest.param("G/D", "G", id="g-over-d"),
        pytest.param("A/C", "A", id="a-over-c"),
        pytest.param("A/E", "A", id="a-over-e"),
        pytest.param("B/D", "B", id="b-over-d"),
        pytest.param("E/G#", "E", id="e-over-gsharp"),
        pytest.param("C/E", "C", id="c-over-e"),
        pytest.param("Eaug", "E", id="eaug"),
        pytest.param("Em7", "Em", id="em7"),
        pytest.param("Em9", "Em", id="em9"),
        pytest.param("Em11", "Em", id="em11"),
        pytest.param("Em13", "Em", id="em13"),
        pytest.param("G13", "G7", id="g13"),
        pytest.param("G7", "G7", id="g7"),
        pytest.param("G9", "G7", id="g9"),
        pytest.param("G11", "G7", id="g11"),
        pytest.param("Gsus2", "G", id="gsus2"),
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


def test_simplify_slash_chord_uses_recursive_suffix_fallback() -> None:
    assert simplify("C9/E") == "C7"


def test_simplify_rejects_empty_symbols() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        simplify(" \t ")
