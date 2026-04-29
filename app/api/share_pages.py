"""HTML and public routes for expiring private-share links."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.core.db import get_session
from app.core.practice_audio import get_practice_audio_file, load_practice_audio_manifest
from app.core.project_pack import pdf_filename, render_project_pdf
from app.core.share_link import (
    ShareLinkError,
    create_share_link,
    load_share_link_by_code,
    revoke_share_link,
    share_link_status,
)
from app.core.teacher_review import has_teacher_review
from app.models.project import Project
from app.models.share_link import ShareLinkManifest

router = APIRouter(tags=["share-pages"])
_TEMPLATES = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)
SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/projects/{project_id}/share-link")
def create_share_link_page(
    project_id: int,
    session: SessionDep,
    expires_in_days: int = Form(7),
    return_to: str = Form("analysis"),
) -> RedirectResponse:
    """Create or rotate a share link, then redirect back to the requested owner page."""
    project = _get_project_or_404(session, project_id)
    try:
        create_share_link(project, expires_in_days=expires_in_days)
    except ShareLinkError:
        return _redirect(project_id, return_to, "share_error")
    return _redirect(project_id, return_to, "share_created")


@router.post("/projects/{project_id}/share-link/revoke")
def revoke_share_link_page(
    project_id: int,
    session: SessionDep,
    return_to: str = Form("analysis"),
) -> RedirectResponse:
    """Revoke a share link, then redirect back to the requested owner page."""
    project = _get_project_or_404(session, project_id)
    try:
        revoke_share_link(project)
    except ShareLinkError:
        return _redirect(project_id, return_to, "share_error")
    return _redirect(project_id, return_to, "share_revoked")


@router.get("/share/{code}", response_class=HTMLResponse, name="shared_project_page")
def shared_project_page(request: Request, code: str, session: SessionDep) -> HTMLResponse:
    """Render the public private-share page for a still-active shortcode."""
    project, manifest = _resolve_shared_project(session, code)
    practice_audio = load_practice_audio_manifest(project)
    share_path = f"/share/{manifest.code}"
    return _TEMPLATES.TemplateResponse(
        request=request,
        name="share_preview.html",
        context={
            "project": project.model_dump(),
            "share_link": manifest.model_dump(mode="json")
            | {
                "path": share_path,
                "url": f"{str(request.base_url).rstrip('/')}{share_path}",
                "status": "active",
                "status_label": "有效",
                "expires_label": manifest.expires_at.strftime("%Y-%m-%d %H:%M UTC"),
            },
            "practice_audio": practice_audio.model_dump(mode="json") if practice_audio is not None else None,
            "review_saved": has_teacher_review(project),
        },
    )


@router.get("/share/{code}/pack.pdf")
def shared_project_pdf(code: str, session: SessionDep) -> Response:
    """Return PDF bytes for a currently active share-link shortcode."""
    project, _manifest = _resolve_shared_project(session, code)
    try:
        pdf_bytes = render_project_pdf(project)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{pdf_filename(project.title, project.arrangement_level, project.target_key or project.original_key)}"'},
    )


@router.get("/share/{code}/practice-audio/{variant}.{file_format}")
def shared_practice_audio(
    code: str,
    variant: str,
    file_format: str,
    session: SessionDep,
) -> FileResponse:
    """Download one generated practice-audio artifact through a share link."""
    project, _manifest = _resolve_shared_project(session, code)
    if file_format not in {"mid", "mp3"}:
        raise HTTPException(404, "Unsupported practice-audio format")
    try:
        full_path = get_practice_audio_file(project, variant, file_format)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    media_type = "audio/midi" if file_format == "mid" else "audio/mpeg"
    return FileResponse(str(full_path), media_type=media_type, filename=full_path.name)


def _resolve_shared_project(session: Session, code: str) -> tuple[Project, ShareLinkManifest]:
    manifest = load_share_link_by_code(code)
    if manifest is None:
        raise HTTPException(404, "Share link not found")
    status = share_link_status(manifest)
    if status == "expired":
        raise HTTPException(410, "Share link expired")
    if status == "revoked":
        raise HTTPException(410, "Share link revoked")
    project = session.get(Project, manifest.project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    if not project.license_confirmed:
        raise HTTPException(403, "License not confirmed")
    return project, manifest


def _get_project_or_404(session: Session, project_id: int) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    return project


def _redirect(project_id: int, return_to: str, flag: str) -> RedirectResponse:
    base = f"/projects/{project_id}/preview" if return_to == "preview" else f"/projects/{project_id}"
    return RedirectResponse(url=f"{base}?{flag}=1", status_code=303)
