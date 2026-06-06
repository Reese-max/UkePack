"""Practice session log model for progress tracking."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(UTC)


class PracticeLogBase(SQLModel):
    """Fields shared between create / read schemas and the table."""

    project_id: int = Field(foreign_key="project.id", index=True)
    chords_practiced: str = Field(default="")  # comma-separated chord names
    duration_seconds: int = Field(default=0)
    speed_pct: int = Field(default=100)  # 50 / 70 / 100


class PracticeLog(PracticeLogBase, table=True):
    """Persisted practice session row."""

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now)


class PracticeLogCreate(SQLModel):
    """Request body for POST /api/projects/{id}/practice-log."""

    chords_practiced: str = ""
    duration_seconds: int = 0
    speed_pct: int = 100


class PracticeLogRead(SQLModel):
    """Response schema for practice log entries."""

    id: int
    project_id: int
    chords_practiced: str
    duration_seconds: int
    speed_pct: int
    created_at: datetime
