"""Score data models used by the import pipeline."""

from pydantic import BaseModel, Field


class ChordEvent(BaseModel):
    """A chord symbol anchored to a score position."""

    symbol: str
    measure: int
    beat: float


class MelodyNote(BaseModel):
    """A single melodic note event."""

    pitch: str
    measure: int
    beat: float
    quarter_length: float


class Score(BaseModel):
    """Normalized score payload extracted from MusicXML."""

    title: str
    key: str
    bpm: int | None = None
    time_signature: str | None = None
    measures: int
    chords: list[ChordEvent] = Field(default_factory=list)
    melody: list[MelodyNote] = Field(default_factory=list)


class KeyRecommendation(BaseModel):
    """Recommended beginner-friendly key for a parsed score."""

    original_key: str
    target_key: str
    semitone_shift: int
    friendly_chords: list[str] = Field(default_factory=list)
    reason: str
