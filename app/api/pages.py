"""HTML page routes for HTMX-powered UI (P1-12 to P1-15)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.api.playability import build_playability_payload
from app.api.project_uploads import (
    import_midi_into_project,
    import_musicxml_into_project,
    save_upload_with_limit,
)
from app.arrangement.key_advisor import suggest_key
from app.arrangement.level_classifier import classify
from app.arrangement.strum_pattern import suggest_for_level
from app.config import get_settings
from app.core.chord_sheet import parse_chord_sheet
from app.core.db import get_session
from app.core.practice_audio import generate_practice_audio, load_practice_audio_manifest
from app.core.share_link import SHARE_TTL_OPTIONS, load_share_link, share_link_status
from app.core.teacher_review import has_teacher_review
from app.models.project import Project, ProjectCreate
from app.models.score import Score

router = APIRouter(tags=["pages"])
logger = logging.getLogger(__name__)

_TEMPLATES = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)

SessionDep = Annotated[Session, Depends(get_session)]

_SOURCE_TYPE_OPTIONS = [
    ("public_domain", "公版（Public Domain）"),
    ("suno_free", "Suno Free 生成"),
    ("private_research", "私人研究"),
]

_MUSICXML_EXTS = {".musicxml", ".xml", ".mxl"}
_MIDI_EXTS = {".mid", ".midi"}
_VALID_LEVELS = {1, 2, 3}


# ── Page routes ────────────────────────────────────────────────────────────


@router.get("/new", response_class=HTMLResponse)
def new_project_page(request: Request) -> HTMLResponse:
    """Render new-project creation form (P1-12)."""
    return _TEMPLATES.TemplateResponse(
        request=request,
        name="new_project.html",
        context={"source_types": _SOURCE_TYPE_OPTIONS},
    )


@router.post("/projects/create-htmx")
async def create_project_htmx(
    session: SessionDep,
    title: str = Form(...),
    source_type: str = Form(...),
    usage_type: str = Form("private"),
    learner_age: str = Form(""),
    file: Annotated[UploadFile | None, File()] = None,
) -> RedirectResponse:
    """Create project (and optionally import a MusicXML file), then redirect to analysis."""
    age: int | None = int(learner_age) if learner_age.strip().isdigit() else None
    project = Project(
        **ProjectCreate(
            title=title,
            source_type=source_type,
            usage_type=usage_type,
            learner_age=age,
        ).model_dump()
    )
    session.add(project)
    session.commit()
    session.refresh(project)

    if file and file.filename:
        suffix = Path(file.filename).suffix.lower()
        if suffix in _MUSICXML_EXTS | _MIDI_EXTS:
            settings = get_settings()
            save_dir = settings.data_dir / "projects" / str(project.id)
            save_path = save_dir / f"original{suffix}"
            relative_path = str(save_path.relative_to(settings.data_dir))

            await save_upload_with_limit(file, save_path)

            importer = (
                import_midi_into_project if suffix in _MIDI_EXTS else import_musicxml_into_project
            )
            try:
                importer(project, save_path, relative_path=relative_path)
                session.add(project)
                session.commit()
            except (ValueError, RuntimeError) as exc:
                logger.warning("htmx import failed: %s", exc, exc_info=True)
                save_path.unlink(missing_ok=True)
                return RedirectResponse(
                    url=f"/projects/{project.id}?import_error=1",
                    status_code=303,
                )

    return RedirectResponse(url=f"/projects/{project.id}", status_code=303)


@router.get("/projects/{project_id}", response_class=HTMLResponse)
def project_analysis_page(
    request: Request,
    project_id: int,
    session: SessionDep,
) -> HTMLResponse:
    """Full analysis page for a project (P1-13)."""
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")

    analysis: dict[str, Any] | None = _build_analysis(project)
    return _TEMPLATES.TemplateResponse(
        request=request,
        name="analysis.html",
        context={
            "project": project.model_dump(),
            "analysis": analysis,
            "selected_level": project.arrangement_level,
            "import_error": request.query_params.get("import_error") == "1",
            "audio_error": request.query_params.get("audio_error") == "1",
            "practice_audio": _practice_audio_payload(project),
            "review_saved": has_teacher_review(project),
            "has_score_data": analysis is not None,
            "share_link": _share_payload(project, request),
            "share_ttl_options": SHARE_TTL_OPTIONS,
            "share_return_to": "analysis",
            "share_created": request.query_params.get("share_created") == "1",
            "share_revoked": request.query_params.get("share_revoked") == "1",
            "share_error": request.query_params.get("share_error") == "1",
        },
    )


@router.get("/projects/{project_id}/strum-partial", response_class=HTMLResponse)
def strum_partial(
    request: Request,
    project_id: int,
    session: SessionDep,
    level: int = 1,
) -> HTMLResponse:
    """HTMX partial: strum-pattern fragment for selected level (P1-13)."""
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    return _render_strum_partial(request, project, level)


@router.post("/projects/{project_id}/strum-partial", response_class=HTMLResponse)
def persist_strum_partial(
    request: Request,
    project_id: int,
    session: SessionDep,
    level: int = Form(...),
) -> HTMLResponse:
    """Persist arrangement level, then return the matching strum fragment."""
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    _validate_level(level)
    project.arrangement_level = level
    project.updated_at = datetime.now(UTC)
    session.add(project)
    session.commit()
    return _render_strum_partial(request, project, level)


@router.post("/projects/{project_id}/confirm-license")
def confirm_license_page(project_id: int, session: SessionDep) -> RedirectResponse:
    """Confirm license, then redirect back to analysis page."""
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    project.license_confirmed = True
    project.updated_at = datetime.now(UTC)
    session.add(project)
    session.commit()
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)


@router.post("/projects/{project_id}/save-chords")
def save_chords_page(
    project_id: int,
    session: SessionDep,
    chords_text: str = Form(...),
) -> RedirectResponse:
    """Save manual chord text and redirect to analysis page (P1-04 UI)."""
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    score = parse_chord_sheet(project.title, chords_text)
    project.chords_text = chords_text
    project.score_json = score.model_dump_json()
    project.original_key = score.key
    project.updated_at = datetime.now(UTC)
    session.add(project)
    session.commit()
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)


@router.post("/projects/{project_id}/import")
async def import_musicxml_page(
    project_id: int,
    session: SessionDep,
    file: Annotated[UploadFile, File()],
) -> RedirectResponse:
    """Upload MusicXML from analysis page and redirect back (browser-friendly wrapper)."""
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _MUSICXML_EXTS | _MIDI_EXTS:
        return RedirectResponse(url=f"/projects/{project_id}?import_error=1", status_code=303)

    settings = get_settings()
    save_path = settings.data_dir / "projects" / str(project_id) / f"original{suffix}"
    relative_path = str(save_path.relative_to(settings.data_dir))

    await save_upload_with_limit(file, save_path)

    importer = import_midi_into_project if suffix in _MIDI_EXTS else import_musicxml_into_project
    try:
        importer(project, save_path, relative_path=relative_path)
        session.add(project)
        session.commit()
    except (ValueError, RuntimeError) as exc:
        logger.warning("page import failed: %s", exc, exc_info=True)
        save_path.unlink(missing_ok=True)
        return RedirectResponse(url=f"/projects/{project_id}?import_error=1", status_code=303)

    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)


@router.post("/projects/{project_id}/generate-practice-audio")
def generate_practice_audio_page(project_id: int, session: SessionDep) -> RedirectResponse:
    """Generate practice audio, then redirect back to analysis page."""
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    if not project.license_confirmed:
        return RedirectResponse(url=f"/projects/{project_id}?audio_error=1", status_code=303)
    try:
        generate_practice_audio(project)
    except (ValueError, RuntimeError) as exc:
        logger.warning("practice audio generation failed: %s", exc, exc_info=True)
        return RedirectResponse(url=f"/projects/{project_id}?audio_error=1", status_code=303)
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)


@router.get("/projects/{project_id}/preview", response_class=HTMLResponse)
def project_preview_page(
    request: Request,
    project_id: int,
    session: SessionDep,
) -> HTMLResponse:
    """PDF preview page with iframe (P1-14)."""
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    return _TEMPLATES.TemplateResponse(
        request=request,
        name="preview.html",
        context={
            "project": project.model_dump(),
            "practice_audio": _practice_audio_payload(project),
            "review_available": bool(project.score_json or project.chords_text),
            "review_saved": has_teacher_review(project),
            "has_score_data": bool(project.score_json or project.chords_text),
            "share_link": _share_payload(project, request),
            "share_ttl_options": SHARE_TTL_OPTIONS,
            "share_return_to": "preview",
            "share_created": request.query_params.get("share_created") == "1",
            "share_revoked": request.query_params.get("share_revoked") == "1",
            "share_error": request.query_params.get("share_error") == "1",
        },
    )


# ── Private helpers ────────────────────────────────────────────────────────


def _score_from_project(project: Project) -> Score:
    """Return a Score object from stored JSON or chords text."""
    if project.score_json:
        return Score.model_validate_json(project.score_json)
    return parse_chord_sheet(project.title, project.chords_text or "")


def _build_analysis(project: Project) -> dict[str, Any] | None:
    """Build analysis dict for template, or return None if no score data yet."""
    if not project.score_json and not project.chords_text:
        return None

    score = _score_from_project(project)
    key_rec = suggest_key(score)
    playability = classify(score)
    patterns = suggest_for_level(score, project.arrangement_level)

    # Derive suggested practice speeds (50% / 70% / 100% of BPM) per PRD §8.2 Step 4
    practice_speeds: list[dict[str, object]] | None = None
    if score.bpm:
        slow = max(1, round(score.bpm * 0.5))
        mid = max(1, round(score.bpm * 0.7))
        practice_speeds = [
            {"label": "慢速（50%）", "bpm": slow},
            {"label": "中速（70%）", "bpm": mid},
            {"label": "全速（100%）", "bpm": score.bpm},
        ]

    return {
        "key": score.key,
        "bpm": score.bpm,
        "practice_speeds": practice_speeds,
        "time_signature": score.time_signature,
        "measures": score.measures,
        "chords": [c.model_dump() for c in score.chords[:24]],
        "sections": [section.model_dump() for section in score.sections],
        "key_recommendation": key_rec.model_dump(),
        "playability": build_playability_payload(score, playability),
        "strum_patterns": [
            {
                "name": p.name,
                "notation": p.notation(),
                "description": p.description,
                "bpm_range": p.bpm_range,
            }
            for p in patterns
        ],
    }


def _validate_level(level: int) -> None:
    """Reject levels outside the supported arrangement range."""
    if level not in _VALID_LEVELS:
        raise HTTPException(400, "level must be 1, 2, or 3")


def _render_strum_partial(request: Request, project: Project, level: int) -> HTMLResponse:
    """Render the strum partial for a validated arrangement level."""
    _validate_level(level)
    patterns = suggest_for_level(_score_from_project(project), level)
    return _TEMPLATES.TemplateResponse(
        request=request,
        name="partials/strum_patterns.html",
        context={
            "strum_patterns": [
                {
                    "name": p.name,
                    "notation": p.notation(),
                    "description": p.description,
                    "bpm_range": p.bpm_range,
                }
                for p in patterns
            ],
            "level": level,
        },
    )


def _practice_audio_payload(project: Project) -> dict[str, Any] | None:
    """Return persisted practice-audio metadata for template rendering."""
    manifest = load_practice_audio_manifest(project)
    if manifest is None:
        return None
    return manifest.model_dump(mode="json")


def _share_payload(project: Project, request: Request) -> dict[str, Any] | None:
    """Return private-share metadata for owner pages."""
    manifest = load_share_link(project)
    if manifest is None:
        return None
    status = share_link_status(manifest)
    path = f"/share/{manifest.code}"
    status_labels = {
        "active": "有效",
        "expired": "已過期",
        "revoked": "已撤銷",
    }
    return manifest.model_dump(mode="json") | {
        "status": status,
        "status_label": status_labels[status],
        "path": path,
        "url": f"{str(request.base_url).rstrip('/')}{path}",
        "expires_label": manifest.expires_at.strftime("%Y-%m-%d %H:%M UTC"),
    }
