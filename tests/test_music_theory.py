from app.core.music_theory import transpose_chord_symbol, transpose_pitch_string, transpose_score
from app.models.score import Score, ChordEvent, MelodyNote


def test_transpose_chord_symbol_transposes_slash_bass() -> None:
    assert transpose_chord_symbol("C/E", 2, prefer_flats=False) == "D/F#"


def test_transpose_chord_symbol_preserves_unparseable_tokens() -> None:
    assert transpose_chord_symbol("N.C.", 3, prefer_flats=False) == "N.C."


def test_transpose_pitch_string() -> None:
    assert transpose_pitch_string("C4", 2, prefer_flats=False) == "D4"
    assert transpose_pitch_string("B3", 1, prefer_flats=False) == "C4"
    assert transpose_pitch_string("C4", -1, prefer_flats=False) == "B3"
    assert transpose_pitch_string("F#3", -2, prefer_flats=True) == "E3"
    assert transpose_pitch_string("N.C.", 3, prefer_flats=False) == "N.C."


def test_transpose_score() -> None:
    score = Score(
        title="Test Song",
        key="C major",
        measures=2,
        chords=[
            ChordEvent(symbol="C", measure=1, beat=1.0),
            ChordEvent(symbol="G", measure=2, beat=1.0),
        ],
        melody=[
            MelodyNote(pitch="E4", measure=1, beat=1.0, quarter_length=1.0),
            MelodyNote(pitch="G4", measure=2, beat=1.0, quarter_length=1.0),
        ],
    )
    transposed = transpose_score(score, 2)
    assert transposed.key == "D major"
    assert transposed.chords[0].symbol == "D"
    assert transposed.chords[1].symbol == "A"
    assert transposed.melody[0].pitch == "F#4"
    assert transposed.melody[1].pitch == "A4"
