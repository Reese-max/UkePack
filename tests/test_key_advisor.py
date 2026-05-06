import pytest

from app.arrangement import suggest_key
from app.models import ChordEvent, Score


def test_suggest_key_prefers_c_major_for_e_major_progressions() -> None:
    recommendation = suggest_key(
        _build_score("E major", ["E", "B", "C#m", "A", "B"])
    )

    assert recommendation.target_key == "C major"
    assert recommendation.semitone_shift == -4
    assert recommendation.friendly_chords == ["C", "G", "Am", "F"]
    assert "選 C major" in recommendation.reason


def test_suggest_key_prefers_g_major_when_c_major_requires_raising() -> None:
    recommendation = suggest_key(
        _build_score("B major", ["B", "F#", "G#m", "E", "F#"])
    )

    assert recommendation.target_key == "G major"
    assert recommendation.semitone_shift == -4
    assert recommendation.friendly_chords == ["G", "D", "Em", "C"]


def test_suggest_key_prefers_small_downward_move_for_f_sharp_major() -> None:
    recommendation = suggest_key(
        _build_score("F# major", ["F#", "C#", "D#m", "B", "C#"])
    )

    assert recommendation.target_key == "F major"
    assert recommendation.semitone_shift == -1
    assert recommendation.friendly_chords == ["F", "C", "Dm", "Bb"]


def test_suggest_key_skips_omitted_diminished_chords() -> None:
    recommendation = suggest_key(_build_score("C major", ["C", "Bdim", "G"]))

    assert recommendation.target_key == "C major"
    assert recommendation.friendly_chords == ["C", "G"]


def test_suggest_key_handles_scores_without_chords() -> None:
    recommendation = suggest_key(_build_score("E major", []))

    assert recommendation.target_key == "D major"
    assert recommendation.semitone_shift == -2
    assert recommendation.friendly_chords == ["D"]


def test_suggest_key_falls_back_to_c_major_for_unsupported_modes() -> None:
    recommendation = suggest_key(_build_score("D dorian", ["D", "A", "Bm", "G"]))

    assert recommendation.target_key == "C major"
    assert recommendation.semitone_shift == -2
    assert recommendation.friendly_chords == ["C", "G", "Am", "F"]
    assert "改用 C major" in recommendation.reason


def test_suggest_key_raises_for_unsupported_key_format() -> None:
    with pytest.raises(ValueError, match="Unsupported key format: CMajor"):
        suggest_key(_build_score("CMajor", ["C", "G", "Am", "F"]))


def _build_score(key_name: str, chords: list[str]) -> Score:
    return Score(
        title="Suggestion Fixture",
        key=key_name,
        bpm=100,
        time_signature="4/4",
        measures=len(chords),
        chords=[
            ChordEvent(symbol=symbol, measure=index + 1, beat=1.0)
            for index, symbol in enumerate(chords)
        ],
        melody=[],
    )
