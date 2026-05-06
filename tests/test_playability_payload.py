"""Tests for shared playability presentation payloads."""

from app.api.playability import build_playability_payload
from app.arrangement.level_classifier import classify
from app.models import ChordEvent, Score


def test_build_playability_payload_includes_summary_and_factors() -> None:
    score = Score(
        title="Visual Song",
        key="C major",
        bpm=88,
        time_signature="4/4",
        measures=4,
        chords=[
            ChordEvent(symbol="Cmaj7", measure=1, beat=1.0),
            ChordEvent(symbol="G", measure=2, beat=1.0),
            ChordEvent(symbol="Am7", measure=3, beat=1.0),
            ChordEvent(symbol="F", measure=4, beat=1.0),
        ],
    )

    payload = build_playability_payload(score, classify(score))

    assert payload["summary"] == {
        "distinct_chord_count": 4,
        "total_chord_events": 4,
        "highest_fret": 3,
    }
    assert payload["factors"][0]["label"] == "和弦難度"
    assert payload["factors"][-1]["weight"] == 5
    # Each factor now carries a Chinese description (PRD §10.4)
    for factor in payload["factors"]:
        assert "description" in factor
        assert isinstance(factor["description"], str)
    assert "初學" in payload["factors"][0]["description"]  # chord_difficulty is high → friendly msg
    assert "BPM" in payload["factors"][4]["description"]   # bpm factor references the BPM value
    assert payload["chord_hints"][0]["symbol"] == "Cmaj7"
    assert payload["chord_hints"][0]["category"] == "simplify"
    assert payload["chord_hints"][0]["suggested_symbol"] == "C"
    assert payload["chord_hints"][1]["symbol"] == "G"
    assert payload["chord_hints"][1]["category"] == "friendly"


def test_build_playability_payload_handles_unknown_chord_shapes() -> None:
    score = Score(
        title="Unknown Shapes",
        key="C major",
        bpm=72,
        time_signature="4/4",
        measures=2,
        chords=[
            ChordEvent(symbol="C(add9)", measure=1, beat=1.0),
            ChordEvent(symbol="N.C.", measure=2, beat=1.0),
        ],
    )

    payload = build_playability_payload(score, classify(score))

    assert payload["summary"]["distinct_chord_count"] == 1
    assert payload["summary"]["highest_fret"] is None
    assert payload["chord_hints"][0]["symbol"] == "C(add9)"
    assert payload["chord_hints"][0]["category"] == "watch"
