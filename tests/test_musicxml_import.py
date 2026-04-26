from pathlib import Path

import pytest
from music21 import chord, key, metadata, meter, note, stream

from app.core.musicxml import parse

FIXTURES_DIR = Path(__file__).parent / "fixtures"
EXPECTED_XFAIL_FIXTURES: dict[str, str] = {}
ALL_FIXTURE_PATHS = sorted(FIXTURES_DIR.glob("*.musicxml"))
CORPUS_FIXTURE_PARAMS = [
    pytest.param(
        fixture_path,
        id=fixture_path.stem,
        marks=[
            pytest.mark.xfail(
                reason=EXPECTED_XFAIL_FIXTURES[fixture_path.name],
                strict=True,
            )
        ]
        if fixture_path.name in EXPECTED_XFAIL_FIXTURES
        else [],
    )
    for fixture_path in ALL_FIXTURE_PATHS
]


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


def test_parse_extracts_highest_pitch_from_chord_melody(tmp_path: Path) -> None:
    chord_melody_path = tmp_path / "chord_melody.musicxml"
    score_stream = stream.Score()
    score_stream.metadata = metadata.Metadata(title="Chord Melody")
    part = stream.Part()
    measure = stream.Measure(number=1)
    measure.insert(0, meter.TimeSignature("4/4"))
    measure.insert(0, note.Note("C4", quarterLength=1.0))
    measure.insert(1.0, chord.Chord(["E4", "G4", "C5"], quarterLength=2.0))
    part.append(measure)
    score_stream.append(part)
    score_stream.write("musicxml", fp=chord_melody_path)

    score = parse(chord_melody_path)

    assert [melody_note.pitch for melody_note in score.melody] == ["C4", "C5"]
    assert score.melody[1].quarter_length == pytest.approx(2.0)


def test_parse_supports_compressed_mxl_scores(tmp_path: Path) -> None:
    compressed_path = tmp_path / "compressed_score.mxl"
    _write_single_part_score(compressed_path, title="Compressed Score", tonic="C", melody_pitch="C4")

    score = parse(compressed_path)

    assert score.title == "Compressed Score"
    assert score.key == "C major"
    assert score.time_signature == "4/4"
    assert score.melody[0].pitch == "C4"


def test_parse_falls_back_to_filename_when_metadata_missing(tmp_path: Path) -> None:
    untitled_path = tmp_path / "missing_metadata.musicxml"
    _write_single_part_score(untitled_path, title=None, tonic="G", melody_pitch="G4")

    score = parse(untitled_path)

    assert score.title == "Missing Metadata"
    assert score.key == "G major"
    assert score.time_signature == "4/4"
    assert score.melody[0].pitch == "G4"


@pytest.mark.parametrize("fixture_path", CORPUS_FIXTURE_PARAMS)
def test_parse_fixture_corpus(fixture_path: Path) -> None:
    score = parse(fixture_path)

    assert score.title
    assert score.key
    assert score.time_signature
    assert score.measures > 0
    assert score.chords
    assert score.melody


def test_fixture_inventory_reaches_thirty_scores() -> None:
    assert len(ALL_FIXTURE_PATHS) == 30


def test_fixture_corpus_success_rate() -> None:
    successes = 0
    unexpected_failures: list[str] = []

    for fixture_path in ALL_FIXTURE_PATHS:
        try:
            score = parse(fixture_path)
        except Exception as exc:
            if fixture_path.name not in EXPECTED_XFAIL_FIXTURES:
                unexpected_failures.append(f"{fixture_path.name}: {exc}")
            continue

        assert score.title
        assert score.key
        successes += 1

    assert not unexpected_failures
    assert successes / len(ALL_FIXTURE_PATHS) >= 0.9


def _write_single_part_score(
    path: Path,
    *,
    title: str | None,
    tonic: str,
    melody_pitch: str,
) -> None:
    score_stream = stream.Score()
    if title is not None:
        score_stream.metadata = metadata.Metadata(title=title)

    part = stream.Part()
    measure = stream.Measure(number=1)
    measure.insert(0, meter.TimeSignature("4/4"))
    measure.insert(0, key.Key(tonic))
    measure.append(note.Note(melody_pitch, quarterLength=4.0))
    part.append(measure)
    score_stream.append(part)

    output_format = "mxl" if path.suffix.lower() == ".mxl" else "musicxml"
    score_stream.write(output_format, fp=path)
