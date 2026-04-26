from pathlib import Path

import pytest

from app.core.musicxml import parse

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    (
        "fixture_name",
        "expected_title",
        "expected_key",
        "expected_bpm",
        "expected_time_signature",
        "expected_measures",
        "expected_first_chord",
        "expected_first_pitch",
    ),
    [
        pytest.param(
            "are_you_sleeping.musicxml",
            "Are You Sleeping",
            "F major",
            96,
            "4/4",
            8,
            "F",
            "F4",
            id="are-you-sleeping",
        ),
        pytest.param(
            "greensleeves.musicxml",
            "Greensleeves",
            "E minor",
            84,
            "6/8",
            8,
            "Em",
            "E4",
            id="greensleeves",
        ),
        pytest.param(
            "happy_birthday.musicxml",
            "Happy Birthday",
            "G major",
            110,
            "3/4",
            8,
            "G",
            "D4",
            id="happy-birthday",
        ),
        pytest.param(
            "jingle_bells.musicxml",
            "Jingle Bells",
            "G major",
            120,
            "4/4",
            12,
            "G",
            "B4",
            id="jingle-bells",
        ),
        pytest.param(
            "london_bridge.musicxml",
            "London Bridge",
            "C major",
            112,
            "4/4",
            8,
            "C",
            "G4",
            id="london-bridge",
        ),
        pytest.param(
            "mary_had_a_little_lamb.musicxml",
            "Mary Had a Little Lamb",
            "C major",
            96,
            "4/4",
            8,
            "C",
            "E4",
            id="mary-had-a-little-lamb",
        ),
        pytest.param(
            "old_macdonald_had_a_farm.musicxml",
            "Old MacDonald Had a Farm",
            "G major",
            104,
            "4/4",
            8,
            "G",
            "B4",
            id="old-macdonald",
        ),
        pytest.param(
            "row_row_row_your_boat.musicxml",
            "Row Row Row Your Boat",
            "C major",
            92,
            "4/4",
            8,
            "C",
            "C4",
            id="row-row-row-your-boat",
        ),
        pytest.param(
            "this_old_man.musicxml",
            "This Old Man",
            "D major",
            116,
            "2/4",
            8,
            "D",
            "E4",
            id="this-old-man",
        ),
        pytest.param(
            "twinkle_twinkle_little_star.musicxml",
            "Twinkle Twinkle Little Star",
            "C major",
            100,
            "4/4",
            12,
            "C",
            "C4",
            id="twinkle-twinkle",
        ),
    ],
)
def test_parse_public_domain_fixtures(
    fixture_name: str,
    expected_title: str,
    expected_key: str,
    expected_bpm: int,
    expected_time_signature: str,
    expected_measures: int,
    expected_first_chord: str,
    expected_first_pitch: str,
) -> None:
    score = parse(FIXTURES_DIR / fixture_name)

    assert score.title == expected_title
    assert score.key == expected_key
    assert score.bpm == expected_bpm
    assert score.time_signature == expected_time_signature
    assert score.measures == expected_measures
    assert score.chords
    assert score.chords[0].symbol == expected_first_chord
    assert score.melody
    assert score.melody[0].pitch == expected_first_pitch


def test_parse_rejects_unsupported_extensions(tmp_path: Path) -> None:
    invalid_path = tmp_path / "example.mid"
    invalid_path.write_text("not-a-midi", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported score format"):
        parse(invalid_path)


def test_fixture_inventory_reaches_ten_scores() -> None:
    assert len(list(FIXTURES_DIR.glob("*.musicxml"))) == 10
