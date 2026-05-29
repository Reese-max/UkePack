"""Tests for MIDI import → Score (BACKLOG U2-a).

The corpus is generated deterministically from public-domain children's melodies
(no committed binaries), mirroring the existing ``build_test_midi_bytes`` helper.
"""

from __future__ import annotations

from pathlib import Path

import mido
import pytest

from app.core.musicxml import parse_midi
from app.models import Score

# Public-domain children's melodies as quarter-note MIDI pitch sequences.
_PUBLIC_DOMAIN_MELODIES: dict[str, list[int]] = {
    "twinkle_twinkle": [60, 60, 67, 67, 69, 69, 67, 65, 65, 64, 64, 62, 62, 60],
    "mary_had_a_little_lamb": [64, 62, 60, 62, 64, 64, 64, 62, 62, 62, 64, 67, 67],
    "london_bridge": [67, 69, 67, 65, 64, 65, 67, 62, 64, 65, 64, 65, 67],
    "row_row_row_your_boat": [60, 60, 60, 62, 64, 64, 62, 64, 65, 67],
    "hot_cross_buns": [64, 62, 60, 64, 62, 60, 60, 60, 60, 60, 62, 62, 62, 62, 64, 62, 60],
    "jingle_bells": [64, 64, 64, 64, 64, 64, 64, 67, 60, 62, 64],
}


def _write_midi(
    path: Path, notes: list[int], *, bpm: int = 100, numerator: int = 4, denominator: int = 4
) -> Path:
    """Write a monophonic quarter-note melody to a .mid file."""
    mid = mido.MidiFile(type=1)
    meta = mido.MidiTrack()
    track = mido.MidiTrack()
    mid.tracks.extend([meta, track])
    meta.append(
        mido.MetaMessage("time_signature", numerator=numerator, denominator=denominator, time=0)
    )
    meta.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    meta.append(mido.MetaMessage("end_of_track", time=0))
    track.append(mido.Message("program_change", program=0, time=0))
    for pitch in notes:
        track.append(mido.Message("note_on", note=pitch, velocity=80, time=0))
        track.append(mido.Message("note_off", note=pitch, velocity=0, time=mid.ticks_per_beat))
    track.append(mido.MetaMessage("end_of_track", time=0))
    mid.save(str(path))
    return path


@pytest.fixture
def midi_corpus(tmp_path: Path) -> list[Path]:
    """Materialize the public-domain melody corpus as .mid files."""
    return [
        _write_midi(tmp_path / f"{name}.mid", notes)
        for name, notes in _PUBLIC_DOMAIN_MELODIES.items()
    ]


def test_corpus_has_at_least_five_fixtures(midi_corpus: list[Path]) -> None:
    assert len(midi_corpus) >= 5


def test_midi_corpus_parse_success_rate_at_least_90_percent(midi_corpus: list[Path]) -> None:
    parsed_ok = 0
    for path in midi_corpus:
        try:
            score = parse_midi(path)
        except Exception:  # measuring parse robustness across the whole corpus
            continue
        if score.melody:
            parsed_ok += 1
    rate = parsed_ok / len(midi_corpus)
    assert rate >= 0.9, f"MIDI parse success rate {rate:.0%} < 90% ({parsed_ok}/{len(midi_corpus)})"


def test_parse_midi_extracts_tempo_timesig_and_melody(tmp_path: Path) -> None:
    notes = _PUBLIC_DOMAIN_MELODIES["twinkle_twinkle"]
    path = _write_midi(tmp_path / "twinkle.mid", notes, bpm=96)

    score = parse_midi(path)

    assert isinstance(score, Score)
    assert score.bpm == 96
    assert score.time_signature == "4/4"
    assert len(score.melody) == len(notes)
    assert score.title  # derived from filename when MIDI has no metadata


def test_parse_midi_accepts_dot_midi_extension(tmp_path: Path) -> None:
    path = _write_midi(tmp_path / "song.midi", [60, 62, 64])

    score = parse_midi(path)

    assert len(score.melody) == 3


def test_parse_midi_rejects_non_midi_extension(tmp_path: Path) -> None:
    bogus = tmp_path / "song.musicxml"
    bogus.write_text("not midi")
    with pytest.raises(ValueError, match="Unsupported MIDI format"):
        parse_midi(bogus)


def test_parse_midi_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        parse_midi(tmp_path / "missing.mid")


def test_parse_midi_blocks_network_fetch_path() -> None:
    with pytest.raises(ValueError, match="Network fetch blocked"):
        parse_midi(Path("https://evil.example/song.mid"))
