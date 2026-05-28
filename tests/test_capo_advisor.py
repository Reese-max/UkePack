"""Tests for capo suggestions and small-hand (kids) fingering helpers (U1-b)."""

from app.arrangement import (
    CapoRecommendation,
    hard_for_small_hands,
    kid_friendly_substitution,
    suggest_capo,
)
from app.models import ChordEvent, Score


def test_suggest_capo_recommends_third_fret_for_b_flat_major() -> None:
    # Arrange: a I-IV-V in Bb (all barre/caution chords on a ukulele).
    score = _build_score("Bb major", ["Bb", "Eb", "F"])

    # Act
    recommendation = suggest_capo(score)

    # Assert — capo 3 lets a child fret open G / C / D shapes instead.
    assert isinstance(recommendation, CapoRecommendation)
    assert recommendation.capo_fret == 3
    assert recommendation.played_chords == ["G", "C", "D"]
    assert recommendation.hard_chords == []


def test_suggest_capo_reason_keeps_sounding_key_and_names_the_fret() -> None:
    recommendation = suggest_capo(_build_score("Bb major", ["Bb", "Eb", "F"]))

    assert "3" in recommendation.reason
    assert "Bb major" in recommendation.reason


def test_suggest_capo_skips_capo_when_song_is_already_easy() -> None:
    score = _build_score("C major", ["C", "F", "G", "Am"])

    recommendation = suggest_capo(score)

    assert recommendation.capo_fret == 0
    assert recommendation.played_chords == ["C", "F", "G", "Am"]
    assert recommendation.hard_chords == []
    assert "不需要" in recommendation.reason


def test_suggest_capo_handles_score_without_chords() -> None:
    recommendation = suggest_capo(_build_score("E major", []))

    assert recommendation.capo_fret == 0
    assert recommendation.played_chords == []


def test_suggest_capo_never_exceeds_max_capo() -> None:
    score = _build_score("Bb major", ["Bb", "Eb", "F"])

    recommendation = suggest_capo(score, max_capo=2)

    assert 0 <= recommendation.capo_fret <= 2


def test_suggest_capo_deduplicates_repeated_chords() -> None:
    score = _build_score("Bb major", ["Bb", "Eb", "F", "Bb", "F"])

    recommendation = suggest_capo(score)

    assert recommendation.capo_fret == 3
    assert recommendation.played_chords == ["G", "C", "D"]


def test_kid_friendly_substitution_swaps_e_for_e7() -> None:
    assert kid_friendly_substitution("E") == "E7"


def test_kid_friendly_substitution_returns_none_for_easy_chord() -> None:
    assert kid_friendly_substitution("C") is None


def test_kid_friendly_substitution_returns_none_without_known_easier_shape() -> None:
    # No charted small-hand voicing exists for a barre B; capo is the answer.
    assert kid_friendly_substitution("B") is None


def test_hard_for_small_hands_flags_caution_chords() -> None:
    assert hard_for_small_hands("E") is True
    assert hard_for_small_hands("Bm") is True


def test_hard_for_small_hands_allows_beginner_chords() -> None:
    assert hard_for_small_hands("C") is False
    assert hard_for_small_hands("Am") is False


def _build_score(key_name: str, chords: list[str]) -> Score:
    return Score(
        title="Capo Fixture",
        key=key_name,
        bpm=100,
        time_signature="4/4",
        measures=max(len(chords), 1),
        chords=[
            ChordEvent(symbol=symbol, measure=index + 1, beat=1.0)
            for index, symbol in enumerate(chords)
        ],
        melody=[],
    )
