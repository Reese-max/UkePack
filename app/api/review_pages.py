"""HTML routes for teacher review mode (FR-013)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.api.projects._shared import load_score
from app.core.db import get_session
from app.core.teacher_review import (
    apply_teacher_review_template,
    downgrade_teacher_review,
    load_teacher_review,
    restore_teacher_review,
    save_teacher_review_template,
    update_teacher_review,
)
from app.models.project import Project
from app.models.teacher_review import TeacherReviewDraft

router = APIRouter(tags=["review-pages"])
_TEMPLATES = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)
SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/projects/{project_id}/review", response_class=HTMLResponse)
def teacher_review_page(
    request: Request,
    project_id: int,
    session: SessionDep,
) -> HTMLResponse:
    """Render the teacher-review editor for a scored project."""
    project = _get_project_or_404(session, project_id, request=request)
    review = load_teacher_review(project, load_score(project))
    return _TEMPLATES.TemplateResponse(
        request=request,
        name="review.html",
        context={
            "project": project.model_dump(),
            "project_token": project.owner_token,
            "csrf_token": request.cookies.get("ukepack_csrf") or "",
            "review": review.model_dump(mode="json"),
            "saved": request.query_params.get("saved") == "1",
            "downgraded": request.query_params.get("downgraded") == "1",
            "restored": request.query_params.get("restored") == "1",
            "template_saved": request.query_params.get("template_saved") == "1",
            "template_applied": request.query_params.get("template_applied") == "1",
        },
    )


@router.post("/projects/{project_id}/review/save")
def save_teacher_review_page(
    project_id: int,
    session: SessionDep,
    request: Request,
    arrangement_level: int = Form(...),
    chords_text: str = Form(...),
    strum_name: str = Form(...),
    strum_notation: str = Form(...),
    strum_description: str = Form(""),
    tab_notes: str = Form(""),
    practice_notes: str = Form(""),
) -> RedirectResponse:
    """Persist teacher-review edits from the HTML form."""
    project = _get_project_or_404(session, project_id, request=request)
    update_teacher_review(
        project,
        load_score(project),
        TeacherReviewDraft(
            arrangement_level=arrangement_level,
            chords_text=chords_text,
            strum_name=strum_name,
            strum_notation=strum_notation,
            strum_description=strum_description,
            tab_notes=tab_notes,
            practice_notes=practice_notes,
        ),
    )
    session.add(project)
    session.commit()
    return _redirect(project_id, "saved")


@router.post("/projects/{project_id}/review/downgrade")
def downgrade_teacher_review_page(
    project_id: int,
    session: SessionDep,
    request: Request,
) -> RedirectResponse:
    """Mark the arrangement too hard and redirect back to the review page."""
    project = _get_project_or_404(session, project_id, request=request)
    downgrade_teacher_review(project, load_score(project))
    session.add(project)
    session.commit()
    return _redirect(project_id, "downgraded")


@router.post("/projects/{project_id}/review/restore")
def restore_teacher_review_page(
    project_id: int,
    session: SessionDep,
    request: Request,
) -> RedirectResponse:
    """Restore the teacher review draft back to the system default."""
    project = _get_project_or_404(session, project_id, request=request)
    restore_teacher_review(project, load_score(project))
    session.add(project)
    session.commit()
    return _redirect(project_id, "restored")


@router.post("/projects/{project_id}/review/save-template")
def save_teacher_review_template_page(
    project_id: int,
    session: SessionDep,
    request: Request,
    template_name: str = Form(...),
) -> RedirectResponse:
    """Save the current review draft as a named template."""
    project = _get_project_or_404(session, project_id, request=request)
    save_teacher_review_template(project, load_score(project), template_name)
    return _redirect(project_id, "template_saved")


@router.post("/projects/{project_id}/review/apply-template")
def apply_teacher_review_template_page(
    project_id: int,
    session: SessionDep,
    request: Request,
    template_name: str = Form(...),
) -> RedirectResponse:
    """Apply a saved teacher-review template and redirect back to the editor."""
    project = _get_project_or_404(session, project_id, request=request)
    apply_teacher_review_template(project, load_score(project), template_name)
    session.add(project)
    session.commit()
    return _redirect(project_id, "template_applied")


def _get_project_or_404(
    session: Session,
    project_id: int,
    request: Request | None = None,
) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    if request is not None:
        from app.core.auth import verify_project_access

        verify_project_access(project, request)
    return project


def _redirect(project_id: int, flag: str) -> RedirectResponse:
    return RedirectResponse(url=f"/projects/{project_id}/review?{flag}=1", status_code=303)
