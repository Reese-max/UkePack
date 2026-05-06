from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import mido
import pytest

from app.core.practice_audio import generate_practice_audio, load_practice_audio_manifest
from app.models.project import Project
from tests.helpers import build_test_midi_bytes


def _first_song_note_tick(midi_file: mido.MidiFile) -> int:
    total_ticks = 0
    for msg in mido.merge_tracks(midi_file.tracks):
        total_ticks += int(msg.time)
        if msg.type == "note_on" and msg.velocity > 0 and msg.channel != 9:
            return total_ticks
    raise AssertionError("expected at least one non-click note")


def test_generate_practice_audio_creates_midis_mp3s_and_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_ffmpeg_encode: None,
) -> None:
    project_dir = tmp_path / "projects" / "1"
    project_dir.mkdir(parents=True)
    source_path = project_dir / "original.mid"
    source_path.write_bytes(build_test_midi_bytes(bpm=100))
    monkeypatch.setattr(
        "app.core.practice_audio.get_settings",
        lambda: SimpleNamespace(data_dir=tmp_path),
    )

    project = Project(
        id=1,
        title="Practice Song",
        source_type="public_domain",
        midi_path="projects/1/original.mid",
    )

    manifest = generate_practice_audio(project)

    assert [artifact.variant for artifact in manifest.variants] == [
        "50bpm",
        "70percent",
        "fullspeed",
    ]
    assert manifest.variants[0].bpm == 50
    assert manifest.variants[1].bpm == 70
    assert manifest.variants[2].bpm == 100

    half_speed = mido.MidiFile(str(tmp_path / manifest.variants[0].midi_path))
    first_tempo = next(msg for track in half_speed.tracks for msg in track if msg.type == "set_tempo")
    assert round(mido.tempo2bpm(first_tempo.tempo)) == 50
    assert _first_song_note_tick(half_speed) == half_speed.ticks_per_beat * 4
    assert any(
        msg.type == "note_on" and msg.channel == 9 and msg.velocity > 0
        for msg in half_speed.tracks[0]
    )

    mp3_path = tmp_path / manifest.variants[0].mp3_path
    assert mp3_path.exists()
    assert mp3_path.stat().st_size > 0

    reloaded = load_practice_audio_manifest(project)
    assert reloaded is not None
    assert reloaded.variants[2].variant == "fullspeed"


def test_generate_practice_audio_requires_uploaded_midi(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.core.practice_audio.get_settings",
        lambda: SimpleNamespace(data_dir=tmp_path),
    )
    project = Project(id=1, title="Missing MIDI", source_type="public_domain")

    with pytest.raises(ValueError, match="uploaded MIDI"):
        generate_practice_audio(project)
