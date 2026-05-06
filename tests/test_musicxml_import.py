from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pytest
from music21 import chord, harmony, key, metadata, meter, note, stream

from app.core.musicxml import parse
from app.models.score import Score

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


@dataclass
class _CorpusParseResult:
    score: Score | None
    error: BaseException | None


@pytest.fixture(scope="session")
def corpus_parse_cache() -> dict[str, _CorpusParseResult]:
    """Parse all corpus fixtures once per test session to avoid duplicate work."""
    cache: dict[str, _CorpusParseResult] = {}
    for fixture_path in ALL_FIXTURE_PATHS:
        try:
            score = parse(fixture_path)
            cache[fixture_path.stem] = _CorpusParseResult(score=score, error=None)
        except Exception as exc:
            cache[fixture_path.stem] = _CorpusParseResult(score=None, error=exc)
    return cache


@pytest.fixture(scope="session")
def section_song_parsed(tmp_path_factory: pytest.TempPathFactory) -> Score:
    """Pre-parsed section song score — written+parsed once per session to avoid ~1s overhead."""
    part = _new_part()
    repeated = ["C", "G", "Am", "F"]
    measures = ["Dm", "G", *repeated, "Em", "F", *repeated]
    for number, chord_name in enumerate(measures, start=1):
        measure = cast(Any, stream).Measure(number=number)
        _insert_element(measure, 0, _time_signature("4/4"))
        _insert_element(measure, 0, cast(Any, harmony).ChordSymbol(chord_name))
        _insert_element(measure, 0, cast(Any, note).Note("C4", quarterLength=4.0))
        _append_element(part, measure)
    score_stream = cast(Any, stream).Score()
    score_stream.metadata = cast(Any, metadata).Metadata(title="Section Song")
    _append_element(score_stream, part)
    tmp = tmp_path_factory.mktemp("section_song")
    path = tmp / "section_song.musicxml"
    _write_score_file(score_stream, "musicxml", path)
    return parse(path)


def _new_part() -> stream.Part:
    return cast(stream.Part, cast(Any, stream).Part())


def _time_signature(signature: str) -> Any:
    return cast(Any, meter).TimeSignature(signature)


def _insert_element(container: object, offset: float, element: object) -> None:
    cast(Any, container).insert(offset, element)


def _append_element(container: object, element: object) -> None:
    cast(Any, container).append(element)


def _write_score_file(score_stream: stream.Score, output_format: str, path: Path) -> None:
    cast(Any, score_stream).write(output_format, fp=path)


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
    part = _new_part()
    measure = stream.Measure(number=1)
    _insert_element(measure, 0, _time_signature("4/4"))
    _insert_element(measure, 0, note.Note("C4", quarterLength=1.0))
    _insert_element(measure, 1.0, chord.Chord(["E4", "G4", "C5"], quarterLength=2.0))
    _append_element(part, measure)
    _append_element(score_stream, part)
    _write_score_file(score_stream, "musicxml", chord_melody_path)

    score = parse(chord_melody_path)

    assert [melody_note.pitch for melody_note in score.melody] == ["C4", "C5"]
    assert score.melody[1].quarter_length == pytest.approx(2.0)


def test_parse_detects_sections_from_repeated_chords(section_song_parsed: Score) -> None:
    assert [(section.section, section.start_measure, section.end_measure) for section in section_song_parsed.sections] == [
        ("intro", 1, 2),
        ("chorus", 3, 6),
        ("verse", 7, 8),
        ("chorus", 9, 12),
    ]


def test_parse_supports_compressed_mxl_scores(compressed_mxl_path: Path) -> None:
    # Using a pre-built MXL fixture avoids music21.write("mxl") which takes ~14s on Windows
    score = parse(compressed_mxl_path)

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


def test_parse_rejects_url_style_paths() -> None:
    with pytest.raises(ValueError, match="Network fetch blocked"):
        parse(Path("http://example.com/score.musicxml"))


def test_parse_rejects_https_url_style_paths() -> None:
    with pytest.raises(ValueError, match="Network fetch blocked"):
        parse(Path("https://evil.com/bomb.mxl"))


def test_parse_rejects_files_exceeding_size_limit(tmp_path: Path) -> None:
    from app.core.musicxml import MAX_IMPORT_BYTES

    oversized = tmp_path / "oversized.musicxml"
    oversized.write_bytes(b"x" * (MAX_IMPORT_BYTES + 1))

    with pytest.raises(ValueError, match="exceeds maximum import size"):
        parse(oversized)


def test_parse_rejects_mxl_with_oversized_zip_member(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import zipfile as _zipfile

    import app.core.musicxml as _musicxml

    # Patch limit to 100 bytes so a tiny file triggers the guard without disk overhead
    monkeypatch.setattr(_musicxml, "_MAX_MXL_MEMBER_BYTES", 100)

    bomb_path = tmp_path / "bomb.mxl"
    with _zipfile.ZipFile(bomb_path, "w") as zf:
        zf.writestr("score.xml", b"X" * 200)  # 200 bytes > patched 100-byte limit

    with pytest.raises(ValueError, match="exceeds limit"):
        parse(bomb_path)


@pytest.mark.parametrize("fixture_path", CORPUS_FIXTURE_PARAMS)
def test_parse_fixture_corpus(
    fixture_path: Path,
    corpus_parse_cache: dict[str, _CorpusParseResult],
) -> None:
    result = corpus_parse_cache[fixture_path.stem]
    if result.error is not None:
        raise result.error
    score = result.score
    assert score is not None
    assert score.title
    assert score.key
    assert score.time_signature
    assert score.measures > 0
    assert score.chords
    assert score.melody


def test_fixture_inventory_reaches_thirty_scores() -> None:
    assert len(ALL_FIXTURE_PATHS) == 30


def test_fixture_corpus_success_rate(
    corpus_parse_cache: dict[str, _CorpusParseResult],
) -> None:
    successes = 0
    unexpected_failures: list[str] = []

    for fixture_path in ALL_FIXTURE_PATHS:
        result = corpus_parse_cache[fixture_path.stem]
        if result.error is not None:
            if fixture_path.name not in EXPECTED_XFAIL_FIXTURES:
                unexpected_failures.append(f"{fixture_path.name}: {result.error}")
            continue

        score = result.score
        assert score is not None
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

    part = _new_part()
    measure = stream.Measure(number=1)
    _insert_element(measure, 0, _time_signature("4/4"))
    _insert_element(measure, 0, key.Key(tonic))
    _append_element(measure, note.Note(melody_pitch, quarterLength=4.0))
    _append_element(part, measure)
    _append_element(score_stream, part)

    output_format = "mxl" if path.suffix.lower() == ".mxl" else "musicxml"
    _write_score_file(score_stream, output_format, path)
