"""Teacher review API routes for FR-013."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlmodel import SQLModel

from app.core.teacher_review import (
    apply_teacher_review_template,
    downgrade_teacher_review,
    load_teacher_review,
    restore_teacher_review,
    save_teacher_review_template,
    update_teacher_review,
)
from app.models.teacher_review import TeacherReviewDraft

from ._shared import SessionDep, get_project_or_404, load_score

router = APIRouter(prefix="/api/projects", tags=["projects"])


class ReviewUpdateBody(SQLModel):
    """Body for saving teacher-review edits."""

    arrangement_level: int = 1
    chords_text: str
    strum_name: str
    strum_notation: str
    strum_description: str = ""
    tab_notes: str = ""
    practice_notes: str = ""


class ReviewTemplateBody(SQLModel):
    """Body for save/apply teacher-review template actions."""

    name: str


@router.get("/{project_id}/review")
def get_teacher_review(project_id: int, session: SessionDep) -> dict[str, object]:
    """Return the current teacher-review state for a project."""
    project = get_project_or_404(session, project_id)
    review = load_teacher_review(project, load_score(project))
    return review.model_dump(mode="json")


@router.post("/{project_id}/review")
def save_teacher_review_api(
    project_id: int,
    body: ReviewUpdateBody,
    session: SessionDep,
) -> dict[str, object]:
    """Validate and persist teacher-review edits."""
    project = get_project_or_404(session, project_id)
    try:
        review = update_teacher_review(project, load_score(project), TeacherReviewDraft(**body.model_dump()))
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    session.add(project)
    session.commit()
    return review.model_dump(mode="json")


@router.post("/{project_id}/review/downgrade")
def downgrade_teacher_review_api(project_id: int, session: SessionDep) -> dict[str, object]:
    """Mark the arrangement as too hard and lower the active level by one."""
    project = get_project_or_404(session, project_id)
    review = downgrade_teacher_review(project, load_score(project))
    session.add(project)
    session.commit()
    return review.model_dump(mode="json")


@router.post("/{project_id}/review/restore")
def restore_teacher_review_api(project_id: int, session: SessionDep) -> dict[str, object]:
    """Restore teacher-review edits back to the system's original suggestion."""
    project = get_project_or_404(session, project_id)
    review = restore_teacher_review(project, load_score(project))
    session.add(project)
    session.commit()
    return review.model_dump(mode="json")


@router.post("/{project_id}/review/template")
def save_teacher_review_template_api(
    project_id: int,
    body: ReviewTemplateBody,
    session: SessionDep,
) -> dict[str, object]:
    """Save the current review draft as a reusable named template."""
    project = get_project_or_404(session, project_id)
    try:
        review = save_teacher_review_template(project, load_score(project), body.name)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return review.model_dump(mode="json")


@router.post("/{project_id}/review/template/apply")
def apply_teacher_review_template_api(
    project_id: int,
    body: ReviewTemplateBody,
    session: SessionDep,
) -> dict[str, object]:
    """Apply a previously saved teacher-review template to the current project."""
    project = get_project_or_404(session, project_id)
    try:
        review = apply_teacher_review_template(project, load_score(project), body.name)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    session.add(project)
    session.commit()
    return review.model_dump(mode="json")
