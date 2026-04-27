"""Teacher review data models for FR-013."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(UTC)


class TeacherReviewDraft(BaseModel):
    """Editable teacher-review payload applied on top of the base project data."""

    arrangement_level: int = 1
    chords_text: str = ""
    strum_name: str = ""
    strum_notation: str = ""
    strum_description: str = ""
    tab_notes: str = ""
    practice_notes: str = ""


class TeacherReviewCompareRow(BaseModel):
    """Human-readable compare row between original and current review drafts."""

    field: str
    label: str
    original: str
    current: str


class TeacherReviewTemplate(BaseModel):
    """Named reusable teacher-review preset."""

    name: str
    saved_at: datetime = Field(default_factory=_utc_now)
    draft: TeacherReviewDraft


class TeacherReviewState(BaseModel):
    """Persisted teacher-review state for a single project."""

    original: TeacherReviewDraft
    current: TeacherReviewDraft
    too_hard: bool = False
    templates: list[TeacherReviewTemplate] = Field(default_factory=list)
    compare: list[TeacherReviewCompareRow] = Field(default_factory=list)
    saved_at: datetime = Field(default_factory=_utc_now)
