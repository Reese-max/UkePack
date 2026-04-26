"""MusicXML parsing helpers built on top of music21."""

from pathlib import Path
from typing import Any

from music21 import chord, converter, harmony, key, note, tempo

from app.models import ChordEvent, MelodyNote, Score

SUPPORTED_EXTENSIONS = {".musicxml", ".mxl", ".xml"}
_PLACEHOLDER_TITLES = {"Music21 Fragment"}


def parse(path: Path) -> Score:
    """Parse a MusicXML file into the normalized score model."""
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported score format: {path.suffix}")

    parsed_score = converter.parse(str(path))
    melody_part = _get_melody_part(parsed_score)
    return Score(
        title=_extract_title(parsed_score, path),
        key=_extract_key(parsed_score),
        bpm=_extract_bpm(parsed_score),
        time_signature=_extract_time_signature(melody_part),
        measures=_count_measures(melody_part),
        chords=_extract_chords(parsed_score),
        melody=_extract_melody(melody_part),
    )


def _get_melody_part(parsed_score: Any) -> Any:
    """Return the first notated part or the score itself for monophonic files."""
    parts = list(parsed_score.parts)
    return parts[0] if parts else parsed_score


def _extract_title(parsed_score: Any, path: Path) -> str:
    """Prefer embedded metadata, then fall back to the filename."""
    metadata = parsed_score.metadata
    if metadata is not None:
        title = metadata.title or metadata.movementName
        if title and str(title) not in _PLACEHOLDER_TITLES:
            return str(title)
    return path.stem.replace("_", " ").title()


def _extract_key(parsed_score: Any) -> str:
    """Read an explicit key first, then fall back to music21 analysis."""
    embedded_keys = parsed_score.recurse().getElementsByClass(key.Key)
    if embedded_keys:
        return _format_key(embedded_keys[0])

    key_signatures = parsed_score.recurse().getElementsByClass(key.KeySignature)
    if key_signatures:
        return _format_key(key_signatures[0].asKey())

    return _format_key(parsed_score.analyze("key"))


def _format_key(parsed_key: Any) -> str:
    """Format keys as tonic plus mode for stable downstream assertions."""
    return f"{parsed_key.tonic.name} {parsed_key.mode}"


def _extract_bpm(parsed_score: Any) -> int | None:
    """Return the first numeric tempo mark if one is present."""
    tempo_marks = parsed_score.recurse().getElementsByClass(tempo.MetronomeMark)
    for tempo_mark in tempo_marks:
        if tempo_mark.number is not None:
            return round(float(tempo_mark.number))
    return None


def _extract_time_signature(parsed_stream: Any) -> str | None:
    """Return the first encountered time signature."""
    signatures = parsed_stream.recurse().getElementsByClass("TimeSignature")
    return signatures[0].ratioString if signatures else None


def _count_measures(parsed_stream: Any) -> int:
    """Count notated measures in the lead part."""
    measures = parsed_stream.recurse().getElementsByClass("Measure")
    return len(measures)


def _extract_chords(parsed_score: Any) -> list[ChordEvent]:
    """Collect chord symbols across the score."""
    chords: list[ChordEvent] = []
    for chord_symbol in parsed_score.recurse().getElementsByClass(harmony.ChordSymbol):
        chords.append(
            ChordEvent(
                symbol=chord_symbol.figure,
                measure=_normalize_measure(chord_symbol.measureNumber),
                beat=float(chord_symbol.beat),
            )
        )
    return chords


def _extract_melody(parsed_stream: Any) -> list[MelodyNote]:
    """Collect pitched notes from the melody part."""
    melody: list[MelodyNote] = []
    for event in parsed_stream.recurse().notes:
        pitch = _extract_melody_pitch(event)
        if pitch is None:
            continue
        melody.append(
            MelodyNote(
                pitch=pitch,
                measure=_normalize_measure(event.measureNumber),
                beat=float(event.beat),
                quarter_length=float(event.quarterLength),
            )
        )
    return melody


def _extract_melody_pitch(event: Any) -> str | None:
    """Treat chord voicings as melody by keeping their highest pitch."""
    if isinstance(event, note.Note):
        return event.nameWithOctave
    if isinstance(event, harmony.ChordSymbol):
        return None
    if isinstance(event, chord.Chord) and event.pitches:
        highest_pitch = max(event.pitches, key=lambda candidate: candidate.midi)
        return highest_pitch.nameWithOctave
    return None


def _normalize_measure(measure_number: int | None) -> int:
    """Preserve pickup measure zero while normalizing missing values."""
    return 0 if measure_number is None else int(measure_number)
