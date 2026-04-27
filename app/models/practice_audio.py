"""Practice-audio metadata models."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(UTC)


class PracticeAudioArtifact(BaseModel):
    """One generated practice-audio variant."""

    variant: str
    label: str
    bpm: int
    speed_ratio: float
    count_in_bars: int = 1
    click_enabled: bool = True
    midi_path: str
    mp3_path: str


class PracticeAudioManifest(BaseModel):
    """Persisted practice-audio manifest for a project."""

    source_midi_path: str
    generated_at: datetime = Field(default_factory=_utc_now)
    variants: list[PracticeAudioArtifact]
