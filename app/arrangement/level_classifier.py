"""Playability scoring for ukulele arrangements (PRD §10.4)."""

import re
from dataclasses import dataclass

from app.arrangement.chord_simplify import simplify as chord_simplify
from app.core.music_theory import pitch_class
from app.models import Score

# Ukulele beginner chord tiers (PRD §10.1)
_VERY_EASY_CHORDS = frozenset({"C", "G", "F", "Am"})
_EASY_CHORDS = frozenset({"G7", "Dm", "Em", "A7", "D7", "D", "A", "E7"})
# "降低" list from PRD §10.1
_HARD_CHORDS = frozenset({"Bb", "Bm", "F#m", "B", "E", "Eb", "Ab", "Bbm"})

# PRD §10.4 factor weights (must sum to 1.0)
_WEIGHTS: dict[str, float] = {
    "chord_difficulty": 0.30,
    "chord_change_freq": 0.20,
    "melody_position": 0.20,
    "rhythm_complexity": 0.15,
    "bpm": 0.10,
    "layout_readability": 0.05,
}

_PITCH_NAME_PATTERN = re.compile(r"^([A-Ga-g](?:[#b\-]{0,2}))(\d+)$")


@dataclass
class PlayabilityResult:
    """Playability assessment for a parsed score."""

    playability_score: int
    recommended_level: int
    label: str
    factors: dict[str, float]


def classify(score: Score) -> PlayabilityResult:
    """Compute a playability score (0-100) and recommend an arrangement level.

    Higher scores mean more beginner-friendly.  Recommended level maps:
    >=75 -> Level 1, 50-74 -> Level 2, <50 -> Level 3.
    """
    factors = {
        "chord_difficulty": _score_chord_difficulty(score),
        "chord_change_freq": _score_chord_change_frequency(score),
        "melody_position": _score_melody_position(score),
        "rhythm_complexity": _score_rhythm_complexity(score),
        "bpm": _score_bpm(score),
        "layout_readability": _score_layout_readability(score),
    }
    raw = sum(factors[k] * _WEIGHTS[k] for k in factors)
    score_int = max(0, min(100, round(raw)))
    return PlayabilityResult(
        playability_score=score_int,
        recommended_level=_derive_level(score_int),
        label=_derive_label(score_int),
        factors=factors,
    )


def _score_chord_difficulty(score: Score) -> float:
    """Score 0-100; higher means easier chords after simplification."""
    if not score.chords:
        return 100.0
    total = 0.0
    for chord_event in score.chords:
        try:
            simplified = chord_simplify(chord_event.symbol)
        except ValueError:
            simplified = chord_event.symbol
        if simplified == "N.C." or simplified in _VERY_EASY_CHORDS:
            total += 100.0
        elif simplified in _EASY_CHORDS:
            total += 75.0
        elif simplified in _HARD_CHORDS:
            total += 30.0
        elif "#" in simplified or "b" in simplified:
            # Remaining chords with accidentals are generally harder
            total += 25.0
        else:
            total += 55.0
    return total / len(score.chords)


def _score_chord_change_frequency(score: Score) -> float:
    """Score 0-100; fewer chord changes per measure is easier."""
    if score.measures == 0 or not score.chords:
        return 100.0
    cpm = len(score.chords) / score.measures
    if cpm <= 1.0:
        return 100.0
    if cpm <= 2.0:
        return 80.0
    if cpm <= 4.0:
        return 55.0
    return 30.0


def _score_melody_position(score: Score) -> float:
    """Score 0-100; lower average MIDI pitch -> easier ukulele fret position.

    Comfortable beginner range on GCEA: roughly C4 (MIDI 60) - C5 (MIDI 72).
    """
    midi_values = [m for n in score.melody if (m := _pitch_to_midi(n.pitch)) is not None]
    if not midi_values:
        return 80.0  # no melody data — assume moderate
    avg_midi = sum(midi_values) / len(midi_values)
    if avg_midi <= 72:
        return 100.0
    if avg_midi <= 76:
        return 70.0
    if avg_midi <= 80:
        return 45.0
    return 20.0


def _score_rhythm_complexity(score: Score) -> float:
    """Score 0-100 based on time signature."""
    return {
        "4/4": 100.0,
        "2/4": 90.0,
        "3/4": 80.0,
        "6/8": 65.0,
    }.get(score.time_signature or "", 75.0)


def _score_bpm(score: Score) -> float:
    """Score 0-100; moderate tempo (60-90 BPM) is easiest for beginners."""
    if score.bpm is None:
        return 75.0
    bpm = score.bpm
    if bpm < 60:
        return 70.0  # very slow tempos are harder to feel
    if bpm <= 90:
        return 100.0
    if bpm <= 120:
        return 80.0
    if bpm <= 160:
        return 55.0
    return 25.0


def _score_layout_readability(score: Score) -> float:
    """Score 0-100 based on distinct simplified chord count."""
    if not score.chords:
        return 100.0
    distinct: set[str] = set()
    for c in score.chords:
        try:
            simplified = chord_simplify(c.symbol)
        except ValueError:
            simplified = c.symbol
        if simplified != "N.C.":
            distinct.add(simplified)
    count = len(distinct)
    if count <= 4:
        return 100.0
    if count <= 8:
        return 70.0
    return 40.0


def _derive_level(playability_score: int) -> int:
    """Map a playability score to a recommended arrangement level (1/2/3)."""
    if playability_score >= 75:
        return 1
    if playability_score >= 50:
        return 2
    return 3


def _derive_label(playability_score: int) -> str:
    """Return a human-readable playability label (PRD §10.4)."""
    if playability_score >= 90:
        return "非常適合初學"
    if playability_score >= 75:
        return "適合初學，但需慢練"
    if playability_score >= 60:
        return "需要老師協助"
    if playability_score >= 40:
        return "建議大幅簡化"
    return "不建議作為兒童入門教材"


def _pitch_to_midi(pitch_name: str) -> int | None:
    """Convert a music21-style nameWithOctave string to a MIDI number.

    music21 uses "-" for flats (e.g. "B-4" means Bb4).
    """
    match = _PITCH_NAME_PATTERN.match(pitch_name)
    if match is None:
        return None
    note_part, octave_str = match.groups()
    # Normalize music21's dash-flat notation to standard "b" accidental
    normalized = note_part.replace("-", "b")
    normalized = normalized[0].upper() + normalized[1:]
    try:
        pc = pitch_class(normalized)
    except ValueError:
        return None
    return (int(octave_str) + 1) * 12 + pc
