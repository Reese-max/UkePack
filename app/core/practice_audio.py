"""Practice-audio generation from uploaded MIDI projects."""

from __future__ import annotations

import re
import shutil
import subprocess
import wave
from array import array
from dataclasses import dataclass
from math import pi, sin
from pathlib import Path

import mido

from app.config import get_settings
from app.models.practice_audio import PracticeAudioArtifact, PracticeAudioManifest
from app.models.project import Project

SAMPLE_RATE = 11025
DEFAULT_BPM = 120
COUNT_IN_BARS = 1
CLICK_CHANNEL = 9
_INVALID_STEM_CHARS = re.compile(r'[<>:"/\\|?*]+')


@dataclass(frozen=True)
class _VariantSpec:
    variant: str
    label: str
    file_suffix: str
    speed_ratio: float
    fixed_bpm: int | None = None


@dataclass(frozen=True)
class _NoteEvent:
    start_seconds: float
    end_seconds: float
    note: int
    velocity: int
    channel: int


_VARIANTS: tuple[_VariantSpec, ...] = (
    _VariantSpec("50bpm", "50 BPM", "50bpm", 50 / DEFAULT_BPM, fixed_bpm=50),
    _VariantSpec("70percent", "70%", "70percent", 0.7),
    _VariantSpec("fullspeed", "100%", "fullspeed", 1.0),
)


def load_practice_audio_manifest(project: Project) -> PracticeAudioManifest | None:
    """Load a project's persisted practice-audio manifest, if one exists."""
    manifest_path = _manifest_path(project)
    if not manifest_path.exists():
        return None
    return PracticeAudioManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))


def generate_practice_audio(project: Project) -> PracticeAudioManifest:
    """Generate slowed MIDI + MP3 practice assets for an uploaded MIDI project."""
    source_path = _source_midi_path(project)
    source_midi = mido.MidiFile(str(source_path))
    output_dir = _output_dir(project)
    output_dir.mkdir(parents=True, exist_ok=True)

    base_bpm = _first_bpm(source_midi)
    time_signature = _first_time_signature(source_midi)
    stem = _safe_stem(project.title)
    variants = [
        _render_variant(project, source_midi, spec, output_dir, stem, base_bpm, time_signature)
        for spec in _VARIANTS
    ]
    manifest = PracticeAudioManifest(source_midi_path=project.midi_path or "", variants=variants)
    _manifest_path(project).write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return manifest


def get_practice_audio_file(project: Project, variant: str, file_format: str) -> Path:
    """Resolve an existing generated practice-audio artifact on disk."""
    manifest = load_practice_audio_manifest(project)
    if manifest is None:
        raise FileNotFoundError("Practice audio has not been generated yet")

    artifact = next((item for item in manifest.variants if item.variant == variant), None)
    if artifact is None:
        raise ValueError(f"Unknown practice-audio variant '{variant}'")

    rel_path = artifact.mp3_path if file_format == "mp3" else artifact.midi_path
    full_path = get_settings().data_dir / rel_path
    if not full_path.exists():
        raise FileNotFoundError(f"Missing generated file: {rel_path}")
    return full_path


def _render_variant(
    project: Project,
    source_midi: mido.MidiFile,
    spec: _VariantSpec,
    output_dir: Path,
    stem: str,
    base_bpm: int,
    time_signature: tuple[int, int],
) -> PracticeAudioArtifact:
    target_bpm = _target_bpm(spec, base_bpm)
    midi_path = output_dir / f"{stem}_practice_{spec.file_suffix}.mid"
    mp3_path = output_dir / f"{stem}_practice_{spec.file_suffix}.mp3"
    wav_path = output_dir / f"{stem}_practice_{spec.file_suffix}.wav"

    practice_midi = _build_practice_midi(source_midi, target_bpm, base_bpm, time_signature)
    practice_midi.save(str(midi_path))
    try:
        _render_wav(practice_midi, wav_path)
        _encode_mp3(wav_path, mp3_path)
    finally:
        wav_path.unlink(missing_ok=True)

    data_dir = get_settings().data_dir
    return PracticeAudioArtifact(
        variant=spec.variant,
        label=spec.label,
        bpm=target_bpm,
        speed_ratio=round(target_bpm / base_bpm, 3),
        midi_path=str(midi_path.relative_to(data_dir)),
        mp3_path=str(mp3_path.relative_to(data_dir)),
    )


def _build_practice_midi(
    source_midi: mido.MidiFile,
    target_bpm: int,
    base_bpm: int,
    time_signature: tuple[int, int],
) -> mido.MidiFile:
    output = mido.MidiFile(type=source_midi.type, ticks_per_beat=source_midi.ticks_per_beat)
    count_in_ticks = _count_in_ticks(source_midi.ticks_per_beat, time_signature)
    scale = target_bpm / base_bpm

    output.tracks.append(_build_click_track(source_midi.ticks_per_beat, target_bpm, time_signature))
    for track in source_midi.tracks:
        output.tracks.append(_copy_shifted_track(track, count_in_ticks, scale))
    return output


def _build_click_track(
    ticks_per_beat: int,
    bpm: int,
    time_signature: tuple[int, int],
) -> mido.MidiTrack:
    numerator, denominator = time_signature
    beat_ticks = max(1, round(ticks_per_beat * 4 / denominator))
    click_ticks = max(1, beat_ticks // 8)
    track = mido.MidiTrack()
    track.append(mido.MetaMessage("track_name", name="Count In Click", time=0))
    track.append(mido.MetaMessage("time_signature", numerator=numerator, denominator=denominator, time=0))
    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    for beat in range(numerator * COUNT_IN_BARS):
        delta = 0 if beat == 0 else beat_ticks - click_ticks
        note = 76 if beat % numerator == 0 else 77
        track.append(mido.Message("note_on", channel=CLICK_CHANNEL, note=note, velocity=100, time=delta))
        track.append(mido.Message("note_off", channel=CLICK_CHANNEL, note=note, velocity=0, time=click_ticks))
    track.append(mido.MetaMessage("end_of_track", time=0))
    return track


# GCEA re-entrant ukulele open-string MIDI pitches (high-G tuning): G4 C4 E4 A4.
_UKE_OPEN_MIDI: tuple[int, int, int, int] = (67, 60, 64, 69)
_REF_TICKS_PER_BEAT = 480


def build_reference_midi(chords: list[str], bpm: int, beats_per_bar: int = 4) -> mido.MidiFile:
    """Build a reference-audio MIDI: a metronome click every beat plus the ukulele
    chord voicings down-strummed once per beat (BACKLOG U5-a)."""
    beats_per_bar = max(beats_per_bar, 1)
    midi = mido.MidiFile(type=1, ticks_per_beat=_REF_TICKS_PER_BEAT)
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage("time_signature", numerator=beats_per_bar, denominator=4, time=0))
    meta.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(max(bpm, 1)), time=0))
    meta.append(mido.MetaMessage("end_of_track", time=0))
    midi.tracks.append(meta)

    bars = max(len(chords), 1)
    midi.tracks.append(_reference_click_track(beats_per_bar, bars))
    midi.tracks.append(_reference_chord_track(chords, beats_per_bar))
    return midi


def render_reference_wav(
    chords: list[str], bpm: int, wav_path: Path, beats_per_bar: int = 4
) -> Path:
    """Synthesize a chords + metronome reference WAV to ``wav_path`` (BACKLOG U5-a)."""
    _render_wav(build_reference_midi(chords, bpm, beats_per_bar), wav_path)
    return wav_path


def _reference_click_track(beats_per_bar: int, bars: int) -> mido.MidiTrack:
    track = mido.MidiTrack()
    track.append(mido.MetaMessage("track_name", name="Metronome", time=0))
    for beat in range(beats_per_bar * bars):
        note = 76 if beat % beats_per_bar == 0 else 77
        track.append(mido.Message("note_on", channel=CLICK_CHANNEL, note=note, velocity=90, time=0))
        track.append(
            mido.Message(
                "note_off", channel=CLICK_CHANNEL, note=note, velocity=0, time=_REF_TICKS_PER_BEAT
            )
        )
    track.append(mido.MetaMessage("end_of_track", time=0))
    return track


def _reference_chord_track(chords: list[str], beats_per_bar: int) -> mido.MidiTrack:
    track = mido.MidiTrack()
    track.append(mido.MetaMessage("track_name", name="Chords", time=0))
    pending = 0
    for chord in chords:
        pitches = _chord_pitches(chord)
        for _beat in range(beats_per_bar):
            if not pitches:
                pending += _REF_TICKS_PER_BEAT
                continue
            for index, pitch in enumerate(pitches):
                track.append(
                    mido.Message("note_on", note=pitch, velocity=80, time=pending if index == 0 else 0)
                )
                pending = 0
            for index, pitch in enumerate(pitches):
                track.append(
                    mido.Message(
                        "note_off",
                        note=pitch,
                        velocity=0,
                        time=_REF_TICKS_PER_BEAT if index == 0 else 0,
                    )
                )
    track.append(mido.MetaMessage("end_of_track", time=0))
    return track


def _chord_pitches(chord: str) -> list[int]:
    """Map a chord symbol to its ukulele voicing as MIDI pitches (empty if unknown)."""
    from app.arrangement.chord_simplify import simplify
    from app.render.chord_diagram import get_fingering

    try:
        simplified = simplify(chord)
    except ValueError:
        return []
    fingering = get_fingering(simplified)
    if fingering is None:
        return []
    return [
        open_midi + fret
        for open_midi, fret in zip(_UKE_OPEN_MIDI, fingering, strict=True)
        if fret >= 0
    ]


def _copy_shifted_track(track: mido.MidiTrack, shift_ticks: int, scale: float) -> mido.MidiTrack:
    copied = mido.MidiTrack()
    pending_shift = shift_ticks
    for msg in track:
        clone = _scaled_message(msg, scale)
        if pending_shift and _starts_after_count_in(clone):
            clone.time += pending_shift
            pending_shift = 0
        copied.append(clone)
    return copied


def _scaled_message(msg: mido.Message, scale: float) -> mido.Message:
    if msg.type != "set_tempo":
        return msg.copy()
    tempo = max(1, round(msg.tempo / scale))
    return msg.copy(tempo=tempo)


def _starts_after_count_in(msg: mido.Message) -> bool:
    if not msg.is_meta:
        return True
    return msg.time > 0 or msg.type in {"lyrics", "text", "marker", "cue_marker"}


def _render_wav(practice_midi: mido.MidiFile, wav_path: Path) -> None:
    samples = _mixdown(_extract_note_events(practice_midi))
    with wave.open(str(wav_path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(samples.tobytes())


def _extract_note_events(practice_midi: mido.MidiFile) -> list[_NoteEvent]:
    current_tempo = mido.bpm2tempo(DEFAULT_BPM)
    current_time = 0.0
    active: dict[tuple[int, int], list[tuple[float, int]]] = {}
    finished: list[_NoteEvent] = []
    for msg in mido.merge_tracks(practice_midi.tracks):
        current_time += mido.tick2second(msg.time, practice_midi.ticks_per_beat, current_tempo)
        if msg.type == "set_tempo":
            current_tempo = msg.tempo
        elif msg.type == "note_on" and msg.velocity > 0:
            active.setdefault((msg.channel, msg.note), []).append((current_time, msg.velocity))
        elif _is_note_off(msg):
            _close_note(active, finished, current_time, msg.channel, msg.note)
    _flush_active_notes(active, finished, current_time)
    return finished


def _is_note_off(msg: mido.Message) -> bool:
    velocity = int(getattr(msg, "velocity", -1))
    return msg.type == "note_off" or (msg.type == "note_on" and velocity == 0)


def _close_note(
    active: dict[tuple[int, int], list[tuple[float, int]]],
    finished: list[_NoteEvent],
    current_time: float,
    channel: int,
    note: int,
) -> None:
    key = (channel, note)
    if key not in active or not active[key]:
        return
    start_time, velocity = active[key].pop()
    finished.append(
        _NoteEvent(
            start_seconds=start_time,
            end_seconds=max(current_time, start_time + 0.05),
            note=note,
            velocity=velocity,
            channel=channel,
        )
    )
    if not active[key]:
        del active[key]


def _flush_active_notes(
    active: dict[tuple[int, int], list[tuple[float, int]]],
    finished: list[_NoteEvent],
    current_time: float,
) -> None:
    for (channel, note), starts in active.items():
        for start_time, velocity in starts:
            finished.append(
                _NoteEvent(
                    start_seconds=start_time,
                    end_seconds=max(current_time, start_time + 0.05),
                    note=note,
                    velocity=velocity,
                    channel=channel,
                )
            )


def _mixdown(events: list[_NoteEvent]) -> array[int]:
    total_seconds = max((event.end_seconds for event in events), default=0.5) + 0.2
    total_samples = max(1, int(total_seconds * SAMPLE_RATE))
    # Keep exports fast; practice audio only needs clear timing, not studio fidelity.
    mix = array("f", [0.0]) * total_samples
    for event in events:
        _add_note_wave(mix, event)
    return _to_pcm16(mix)


def _add_note_wave(mix: array[float], event: _NoteEvent) -> None:
    start = max(0, int(event.start_seconds * SAMPLE_RATE))
    end = min(len(mix), max(start + 1, int(event.end_seconds * SAMPLE_RATE)))
    length = end - start
    if length <= 0:
        return

    step = 2 * pi * _note_frequency(event.note, event.channel) / SAMPLE_RATE
    fade = max(8, min(length // 6, SAMPLE_RATE // 40))
    amplitude = 0.22 if event.channel == CLICK_CHANNEL else 0.08 + (event.velocity / 1270)
    for offset in range(length):
        envelope = _envelope(offset, length, fade)
        mix[start + offset] += amplitude * envelope * sin(step * offset)


def _envelope(offset: int, length: int, fade: int) -> float:
    if offset < fade:
        return offset / fade
    if offset >= length - fade:
        return max(0.0, (length - offset) / fade)
    return 1.0


def _note_frequency(note: int, channel: int) -> float:
    if channel == CLICK_CHANNEL:
        return 1760.0 if note == 76 else 1320.0
    return 440.0 * (2 ** ((note - 69) / 12))


def _to_pcm16(mix: array[float]) -> array[int]:
    peak = max((abs(sample) for sample in mix), default=1.0)
    scale = 0.95 / peak if peak > 0.95 else 1.0
    pcm = array("h")
    for sample in mix:
        clipped = max(-1.0, min(1.0, sample * scale))
        pcm.append(int(clipped * 32767))
    return pcm


def _encode_mp3(wav_path: Path, mp3_path: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg is required to render practice-audio MP3 files")

    result = subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-i", str(wav_path), str(mp3_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg mp3 render failed: {result.stderr.strip()}")


def _source_midi_path(project: Project) -> Path:
    if project.id is None:
        raise ValueError("Project must be saved before generating practice audio")
    if project.midi_path is None:
        raise ValueError("Practice audio requires an uploaded MIDI file")
    full_path = get_settings().data_dir / project.midi_path
    if not full_path.exists():
        raise ValueError("Uploaded MIDI file is missing from disk")
    return full_path


def _manifest_path(project: Project) -> Path:
    return _output_dir(project) / "manifest.json"


def _output_dir(project: Project) -> Path:
    if project.id is None:
        raise ValueError("Project must be saved before generating practice audio")
    return get_settings().data_dir / "projects" / str(project.id) / "practice_audio"


def _safe_stem(title: str) -> str:
    normalized = _INVALID_STEM_CHARS.sub("_", title.strip())
    compact = re.sub(r"\s+", "_", normalized)
    return compact[:60].strip("._") or "project"


def _first_bpm(source_midi: mido.MidiFile) -> int:
    for track in source_midi.tracks:
        for msg in track:
            if msg.type == "set_tempo":
                return max(1, round(float(mido.tempo2bpm(msg.tempo))))
    return DEFAULT_BPM


def _first_time_signature(source_midi: mido.MidiFile) -> tuple[int, int]:
    for track in source_midi.tracks:
        for msg in track:
            if msg.type == "time_signature":
                return msg.numerator, msg.denominator
    return 4, 4


def _count_in_ticks(ticks_per_beat: int, time_signature: tuple[int, int]) -> int:
    numerator, denominator = time_signature
    beat_ticks = max(1, round(ticks_per_beat * 4 / denominator))
    return numerator * beat_ticks * COUNT_IN_BARS


def _target_bpm(spec: _VariantSpec, base_bpm: int) -> int:
    if spec.fixed_bpm is not None:
        return spec.fixed_bpm
    return max(1, round(base_bpm * spec.speed_ratio))
