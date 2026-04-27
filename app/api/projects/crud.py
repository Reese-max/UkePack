"""Project create, read, analysis, and arrange routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, status

from app.arrangement.key_advisor import suggest_key
from app.arrangement.level_classifier import classify
from app.arrangement.strum_pattern import suggest_for_level
from app.core.chord_sheet import parse_chord_sheet
from app.models.project import Project, ProjectCreate, ProjectRead
from app.models.score import Score

from ._shared import (
    ArrangeBody,
    ChordsBody,
    SessionDep,
    get_project_or_404,
    load_score,
    to_read,
    utc_now,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _analysis_response(score: Score) -> dict[str, Any]:
    key_rec = suggest_key(score)
    playability = classify(score)
    return {
        "key": score.key,
        "bpm": score.bpm,
        "time_signature": score.time_signature,
        "measures": score.measures,
        "chords": [chord.model_dump() for chord in score.chords],
        "sections": [section.model_dump() for section in score.sections],
        "key_recommendation": key_rec.model_dump(),
        "playability": {
            "score": playability.playability_score,
            "level": playability.recommended_level,
            "label": playability.label,
        },
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_project(body: ProjectCreate, session: SessionDep) -> ProjectRead:
    """Create a new project."""
    project = Project(**body.model_dump())
    session.add(project)
    session.commit()
    session.refresh(project)
    return to_read(project)


@router.get("/{project_id}")
def get_project(project_id: int, session: SessionDep) -> ProjectRead:
    """Return project metadata."""
    return to_read(get_project_or_404(session, project_id))


@router.post("/{project_id}/chords")
def add_chords(project_id: int, body: ChordsBody, session: SessionDep) -> dict[str, Any]:
    """Store manual chord text and derived score metadata."""
    project = get_project_or_404(session, project_id)
    score = parse_chord_sheet(project.title, body.text)
    project.chords_text = body.text
    project.score_json = score.model_dump_json()
    project.original_key = score.key
    project.updated_at = utc_now()
    session.add(project)
    session.commit()
    return {
        "project_id": project_id,
        "chord_count": len(score.chords),
        "measures": score.measures,
        "section_count": len(score.sections),
    }


@router.get("/{project_id}/analysis")
def get_analysis(project_id: int, session: SessionDep) -> dict[str, Any]:
    """Return key, meter, chord, and difficulty analysis."""
    project = get_project_or_404(session, project_id)
    return _analysis_response(load_score(project))


@router.post("/{project_id}/arrange")
def arrange(project_id: int, body: ArrangeBody, session: SessionDep) -> dict[str, Any]:
    """Store arrangement level and return suggested strum patterns."""
    if body.level not in (1, 2, 3):
        from fastapi import HTTPException

        raise HTTPException(400, "level must be 1, 2, or 3")

    project = get_project_or_404(session, project_id)
    patterns = suggest_for_level(load_score(project), body.level)
    project.arrangement_level = body.level
    project.updated_at = utc_now()
    session.add(project)
    session.commit()
    return {
        "project_id": project_id,
        "level": body.level,
        "strum_patterns": [
            {"name": pattern.name, "notation": pattern.notation(), "description": pattern.description}
            for pattern in patterns
        ],
    }
