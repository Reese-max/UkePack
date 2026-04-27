"""Project persistence model (FR-014)."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


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

    # File paths relative to settings.data_dir
    musicxml_path: str | None = Field(default=None)
    midi_path: str | None = Field(default=None)

    # Serialized score data
    chords_text: str | None = Field(default=None)
    score_json: str | None = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


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
    musicxml_path: str | None
    midi_path: str | None
    created_at: datetime
    updated_at: datetime
