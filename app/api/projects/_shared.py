"""Shared helpers for project API route modules."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import Session, SQLModel

from app.core.chord_sheet import parse_chord_sheet
from app.core.db import get_session
from app.models.project import Project, ProjectRead
from app.models.score import Score

SessionDep = Annotated[Session, Depends(get_session)]

MUSICXML_EXTS = {".musicxml", ".xml", ".mxl"}
MIDI_EXTS = {".mid", ".midi"}


class ChordsBody(SQLModel):
    """Body for POST .../chords."""

    text: str


class ArrangeBody(SQLModel):
    """Body for POST .../arrange."""

    level: int = 1


class LicenseBody(SQLModel):
    """Body for POST .../license."""

    confirmed: bool


def get_project_or_404(session: Session, project_id: int) -> Project:
    """Load a project row or raise a 404."""
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def load_score(project: Project) -> Score:
    """Deserialize stored score data or rebuild it from manual chords."""
    if project.score_json is not None:
        return Score.model_validate_json(project.score_json)
    if project.chords_text is not None:
        return parse_chord_sheet(project.title, project.chords_text)
    raise HTTPException(422, "No score data; import a MusicXML file or add chords first")


def to_read(project: Project) -> ProjectRead:
    """Convert a Project row into the read schema."""
    return ProjectRead.model_validate(project.model_dump())
