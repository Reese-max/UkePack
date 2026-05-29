"""Tests for chord + metronome reference-audio synthesis (BACKLOG U5-a)."""

from pathlib import Path
import wave

import mido

from app.core.practice_audio import build_reference_midi, render_reference_wav


def _note_ons(midi: mido.MidiFile) -> list[mido.Message]:
    return [
        msg
        for track in midi.tracks
        for msg in track
        if msg.type == "note_on" and msg.velocity > 0
    ]


def test_build_reference_midi_has_chord_notes_and_metronome() -> None:
    midi = build_reference_midi(["C", "G"], bpm=100)

    note_ons = _note_ons(midi)
    chord_notes = [m for m in note_ons if m.channel != 9]
    click_notes = [m for m in note_ons if m.channel == 9]
    assert chord_notes, "expected strummed chord notes"
    assert click_notes, "expected metronome clicks"


def test_build_reference_midi_tempo_matches_bpm() -> None:
    midi = build_reference_midi(["C"], bpm=84)

    tempos = [m.tempo for track in midi.tracks for m in track if m.type == "set_tempo"]
    assert tempos == [mido.bpm2tempo(84)]


def test_build_reference_midi_handles_unknown_chord_without_notes() -> None:
    midi = build_reference_midi(["Xyz"], bpm=100)

    note_ons = _note_ons(midi)
    assert [m for m in note_ons if m.channel != 9] == []  # unknown chord → no voicing
    assert any(m.channel == 9 for m in note_ons)  # metronome still present


def test_render_reference_wav_produces_audio(tmp_path: Path) -> None:
    out = render_reference_wav(["C", "G", "Am", "F"], bpm=100, wav_path=tmp_path / "ref.wav")

    assert out.exists()
    with wave.open(str(out), "rb") as handle:
        assert handle.getnframes() > 0
        assert handle.getframerate() == 11025
