"""Project persistence model (FR-014)."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def _generate_owner_token() -> str:
    return f"ukp_{secrets.token_urlsafe(32)}"


def _utc_now() -> datetime:
    return datetime.now(UTC)


class ProjectBase(SQLModel):
    """Fields shared between create / read schemas and the table."""

    title: str = Field(max_length=200)
    source_type: str = Field(max_length=50)
    usage_type: str = Field(default="private", max_length=50)
    learner_level: str = Field(default="beginner", max_length=50)
    learner_age: int | None = Field(default=None)
    tuning: str = Field(default="GCEA", max_length=10)


class Project(ProjectBase, table=True):
    """Persisted project row (FR-014 schema)."""

    id: int | None = Field(default=None, primary_key=True)
    license_confirmed: bool = Field(default=False)

    # Analyzed fields — populated after import/chord entry
    original_key: str | None = Field(default=None, max_length=10)
    target_key: str | None = Field(default=None, max_length=10)
    bpm: int | None = Field(default=None)
    arrangement_level: int = Field(default=1)
    semitone_shift: int = Field(default=0)

    # File paths relative to settings.data_dir
    musicxml_path: str | None = Field(default=None)
    midi_path: str | None = Field(default=None)

    # Serialized score data
    chords_text: str | None = Field(default=None)
    score_json: str | None = Field(default=None)

    # Ownership & Capability Security
    owner_token: str = Field(default_factory=_generate_owner_token, index=True)
    owner_id: str | None = Field(default=None, index=True)

    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)


class ProjectCreate(ProjectBase):
    """Request body for POST /api/projects."""


class ProjectRead(SQLModel):
    """Response schema for project endpoints."""

    id: int
    title: str
    source_type: str
    usage_type: str
    learner_level: str
    learner_age: int | None
    tuning: str
    license_confirmed: bool
    original_key: str | None
    target_key: str | None
    bpm: int | None
    arrangement_level: int
    semitone_shift: int
    musicxml_path: str | None
    midi_path: str | None
    owner_token: str | None = None
    owner_id: str | None = None
    created_at: datetime
    updated_at: datetime
