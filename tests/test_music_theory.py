from app.core.music_theory import transpose_chord_symbol


def test_transpose_chord_symbol_transposes_slash_bass() -> None:
    assert transpose_chord_symbol("C/E", 2, prefer_flats=False) == "D/F#"


def test_transpose_chord_symbol_preserves_unparseable_tokens() -> None:
    assert transpose_chord_symbol("N.C.", 3, prefer_flats=False) == "N.C."
