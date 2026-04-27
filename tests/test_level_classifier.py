"""Tests for the playability level classifier (PRD §10.4)."""

import pytest

from app.arrangement.level_classifier import (
    PlayabilityResult,
    _derive_label,
    _derive_level,
    _pitch_to_midi,
    classify,
)
from app.models import ChordEvent, MelodyNote, Score


def _make_score(
    key: str = "C major",
    bpm: int | None = 80,
    time_signature: str | None = "4/4",
    measures: int = 8,
    chords: list[ChordEvent] | None = None,
    melody: list[MelodyNote] | None = None,
) -> Score:
    if chords is None:
        chords = [
            ChordEvent(symbol="C", measure=1, beat=1.0),
            ChordEvent(symbol="G", measure=2, beat=1.0),
            ChordEvent(symbol="Am", measure=3, beat=1.0),
            ChordEvent(symbol="F", measure=4, beat=1.0),
        ]
    if melody is None:
        melody = [
            MelodyNote(pitch="C4", measure=1, beat=1.0, quarter_length=1.0),
            MelodyNote(pitch="G4", measure=2, beat=1.0, quarter_length=1.0),
        ]
    return Score(
        title="Test Song",
        key=key,
        bpm=bpm,
        time_signature=time_signature,
        measures=measures,
        chords=chords,
        melody=melody,
    )


class TestPitchToMidi:
    def test_middle_c(self) -> None:
        assert _pitch_to_midi("C4") == 60

    def test_a4(self) -> None:
        assert _pitch_to_midi("A4") == 69

    def test_g4(self) -> None:
        assert _pitch_to_midi("G4") == 67

    def test_c_sharp_4(self) -> None:
        assert _pitch_to_midi("C#4") == 61

    def test_flat_music21_notation(self) -> None:
        # music21 uses "-" for flats: B-4 = Bb4 = MIDI 70
        assert _pitch_to_midi("B-4") == 70

    def test_c5(self) -> None:
        assert _pitch_to_midi("C5") == 72

    def test_g5(self) -> None:
        assert _pitch_to_midi("G5") == 79

    def test_invalid_note_name(self) -> None:
        assert _pitch_to_midi("X4") is None

    def test_empty_string(self) -> None:
        assert _pitch_to_midi("") is None

    def test_non_standard_accidental_string(self) -> None:
        assert _pitch_to_midi("Cbb4") is None


class TestDeriveLevel:
    def test_high_score_is_level_1(self) -> None:
        assert _derive_level(100) == 1
        assert _derive_level(90) == 1
        assert _derive_level(75) == 1

    def test_mid_score_is_level_2(self) -> None:
        assert _derive_level(74) == 2
        assert _derive_level(60) == 2
        assert _derive_level(50) == 2

    def test_low_score_is_level_3(self) -> None:
        assert _derive_level(49) == 3
        assert _derive_level(0) == 3


class TestDeriveLabel:
    def test_label_very_easy(self) -> None:
        assert _derive_label(95) == "非常適合初學"
        assert _derive_label(90) == "非常適合初學"

    def test_label_easy_slow_practice(self) -> None:
        assert _derive_label(80) == "適合初學，但需慢練"
        assert _derive_label(75) == "適合初學，但需慢練"

    def test_label_needs_teacher(self) -> None:
        assert _derive_label(65) == "需要老師協助"
        assert _derive_label(60) == "需要老師協助"

    def test_label_simplify(self) -> None:
        assert _derive_label(50) == "建議大幅簡化"
        assert _derive_label(40) == "建議大幅簡化"

    def test_label_not_recommended(self) -> None:
        assert _derive_label(20) == "不建議作為兒童入門教材"
        assert _derive_label(0) == "不建議作為兒童入門教材"


class TestClassify:
    def test_returns_playability_result(self) -> None:
        result = classify(_make_score())
        assert isinstance(result, PlayabilityResult)
        assert 0 <= result.playability_score <= 100
        assert result.recommended_level in {1, 2, 3}
        assert result.label
        assert set(result.factors.keys()) == {
            "chord_difficulty",
            "chord_change_freq",
            "melody_position",
            "rhythm_complexity",
            "bpm",
            "layout_readability",
        }

    def test_preferred_chords_yield_full_chord_difficulty(self) -> None:
        score = _make_score(
            chords=[
                ChordEvent(symbol="C", measure=1, beat=1.0),
                ChordEvent(symbol="G", measure=2, beat=1.0),
                ChordEvent(symbol="Am", measure=3, beat=1.0),
                ChordEvent(symbol="F", measure=4, beat=1.0),
            ]
        )
        result = classify(score)
        assert result.factors["chord_difficulty"] == 100.0

    def test_hard_chords_lower_chord_difficulty(self) -> None:
        hard = _make_score(
            chords=[
                ChordEvent(symbol="Bb", measure=1, beat=1.0),
                ChordEvent(symbol="F#m", measure=2, beat=1.0),
            ]
        )
        easy = _make_score()
        assert classify(hard).factors["chord_difficulty"] < classify(easy).factors["chord_difficulty"]

    def test_no_chords_gives_full_chord_difficulty(self) -> None:
        score = _make_score(chords=[])
        assert classify(score).factors["chord_difficulty"] == 100.0

    def test_no_chords_gives_full_change_frequency(self) -> None:
        score = _make_score(chords=[])
        assert classify(score).factors["chord_change_freq"] == 100.0

    def test_chord_simplify_failure_falls_back_to_raw_symbol(self) -> None:
        score = _make_score(chords=[ChordEvent(symbol="   ", measure=1, beat=1.0)])
        result = classify(score)
        assert result.factors["chord_difficulty"] == 55.0
        assert result.factors["layout_readability"] == 100.0

    @pytest.mark.parametrize(
        ("bpm", "expected"),
        [(59, 70.0), (100, 80.0), (150, 55.0), (161, 25.0)],
    )
    def test_bpm_brackets(self, bpm: int, expected: float) -> None:
        assert classify(_make_score(bpm=bpm)).factors["bpm"] == expected

    def test_none_bpm_uses_neutral_score(self) -> None:
        score = _make_score(bpm=None)
        assert classify(score).factors["bpm"] == 75.0

    def test_six_eight_lowers_rhythm_score(self) -> None:
        six_eight = _make_score(time_signature="6/8")
        four_four = _make_score(time_signature="4/4")
        assert (
            classify(six_eight).factors["rhythm_complexity"]
            < classify(four_four).factors["rhythm_complexity"]
        )

    def test_high_melody_pitch_lowers_position_score(self) -> None:
        high_melody = _make_score(
            melody=[MelodyNote(pitch="A5", measure=1, beat=1.0, quarter_length=1.0)]
        )
        low_melody = _make_score(
            melody=[MelodyNote(pitch="C4", measure=1, beat=1.0, quarter_length=1.0)]
        )
        assert (
            classify(high_melody).factors["melody_position"]
            < classify(low_melody).factors["melody_position"]
        )

    def test_upper_comfort_melody_range_scores_seventy(self) -> None:
        score = _make_score(
            melody=[
                MelodyNote(pitch="C5", measure=1, beat=1.0, quarter_length=1.0),
                MelodyNote(pitch="E5", measure=2, beat=1.0, quarter_length=1.0),
            ]
        )
        assert classify(score).factors["melody_position"] == 70.0

    def test_non_standard_melody_pitches_use_neutral_position_score(self) -> None:
        score = _make_score(
            melody=[MelodyNote(pitch="Cbb4", measure=1, beat=1.0, quarter_length=1.0)]
        )
        assert classify(score).factors["melody_position"] == 80.0

    @pytest.mark.parametrize(
        ("chord_count", "measures", "expected"),
        [(12, 4, 55.0), (21, 4, 30.0)],
    )
    def test_chord_change_frequency_brackets(
        self, chord_count: int, measures: int, expected: float
    ) -> None:
        chords = [
            ChordEvent(symbol="C", measure=(index % measures) + 1, beat=1.0)
            for index in range(chord_count)
        ]
        assert (
            classify(_make_score(measures=measures, chords=chords)).factors["chord_change_freq"]
            == expected
        )

    def test_many_chords_lower_layout_score(self) -> None:
        many_chords = _make_score(
            chords=[
                ChordEvent(symbol=sym, measure=i + 1, beat=1.0)
                for i, sym in enumerate(["C", "G", "Am", "F", "Dm", "Em", "A7", "D7", "G7"])
            ]
        )
        few_chords = _make_score()
        assert (
            classify(many_chords).factors["layout_readability"]
            < classify(few_chords).factors["layout_readability"]
        )

    def test_easy_song_recommended_level_1(self) -> None:
        score = _make_score(
            bpm=80,
            chords=[ChordEvent(symbol="C", measure=i, beat=1.0) for i in range(1, 9)],
            melody=[
                MelodyNote(pitch="C4", measure=i, beat=1.0, quarter_length=1.0)
                for i in range(1, 9)
            ],
        )
        result = classify(score)
        assert result.recommended_level == 1

    def test_complex_song_may_suggest_higher_level(self) -> None:
        """Hard chords + fast tempo + high pitch + 6/8 → level ≥ 2."""
        score = Score(
            title="Complex Song",
            key="Ab major",
            bpm=200,
            time_signature="6/8",
            measures=4,
            chords=[
                ChordEvent(symbol="Bbm", measure=1, beat=1.0),
                ChordEvent(symbol="Eb", measure=1, beat=4.0),
                ChordEvent(symbol="Ab", measure=2, beat=1.0),
                ChordEvent(symbol="Db", measure=2, beat=4.0),
                ChordEvent(symbol="Bbm", measure=3, beat=1.0),
                ChordEvent(symbol="Eb", measure=3, beat=4.0),
                ChordEvent(symbol="Ab", measure=4, beat=1.0),
                ChordEvent(symbol="F#m7b5", measure=4, beat=4.0),
            ],
            melody=[
                MelodyNote(pitch="G5", measure=i, beat=1.0, quarter_length=0.5)
                for i in range(1, 5)
            ],
        )
        result = classify(score)
        assert result.recommended_level >= 2

    def test_hard_song_has_lower_score_than_easy_song(self) -> None:
        hard = Score(
            title="Hard",
            key="Ab major",
            bpm=200,
            time_signature="6/8",
            measures=4,
            chords=[ChordEvent(symbol="Bb", measure=i, beat=1.0) for i in range(1, 5)],
            melody=[
                MelodyNote(pitch="A5", measure=i, beat=1.0, quarter_length=1.0)
                for i in range(1, 5)
            ],
        )
        easy = Score(
            title="Easy",
            key="C major",
            bpm=80,
            time_signature="4/4",
            measures=4,
            chords=[ChordEvent(symbol="C", measure=i, beat=1.0) for i in range(1, 5)],
            melody=[
                MelodyNote(pitch="C4", measure=i, beat=1.0, quarter_length=1.0)
                for i in range(1, 5)
            ],
        )
        assert classify(hard).playability_score < classify(easy).playability_score
