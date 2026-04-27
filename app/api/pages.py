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

from app.api.project_uploads import import_musicxml_into_project, save_upload_with_limit
from app.arrangement.key_advisor import suggest_key
from app.arrangement.level_classifier import classify
from app.arrangement.strum_pattern import suggest_for_level
from app.config import get_settings
from app.core.db import get_session
from app.models.project import Project, ProjectCreate
from app.models.score import ChordEvent, Score

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
        if suffix in _MUSICXML_EXTS:
            settings = get_settings()
            save_dir = settings.data_dir / "projects" / str(project.id)
            save_path = save_dir / f"original{suffix}"
            relative_path = str(save_path.relative_to(settings.data_dir))

            await save_upload_with_limit(file, save_path)

            try:
                import_musicxml_into_project(
                    project,
                    save_path,
                    relative_path=relative_path,
                )
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
            "import_error": request.query_params.get("import_error") == "1",
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

    score = _score_from_project(project)
    patterns = suggest_for_level(score, level)
    return _TEMPLATES.TemplateResponse(
        request=request,
        name="partials/strum_patterns.html",
        context={
            "strum_patterns": [
                {"name": p.name, "notation": p.notation(), "description": p.description}
                for p in patterns
            ],
            "level": level,
        },
    )


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
        context={"project": project.model_dump()},
    )


# ── Private helpers ────────────────────────────────────────────────────────


def _score_from_project(project: Project) -> Any:
    """Return a Score object from stored JSON or chords text."""
    if project.score_json:
        return Score.model_validate_json(project.score_json)

    chords: list[ChordEvent] = []
    measure = 1
    for line in (project.chords_text or "").splitlines():
        clean = line.strip()
        if not clean or clean.endswith(":"):
            continue
        for token in clean.split("|"):
            sym = token.strip()
            if sym:
                chords.append(ChordEvent(symbol=sym, measure=measure, beat=1.0))
                measure += 1
    return Score(
        title=project.title,
        key="C major",
        measures=max(measure - 1, 0),
        chords=chords,
    )


def _build_analysis(project: Project) -> dict[str, Any] | None:
    """Build analysis dict for template, or return None if no score data yet."""
    if not project.score_json and not project.chords_text:
        return None

    score = _score_from_project(project)
    key_rec = suggest_key(score)
    playability = classify(score)
    patterns = suggest_for_level(score, project.arrangement_level)

    return {
        "key": score.key,
        "bpm": score.bpm,
        "time_signature": score.time_signature,
        "measures": score.measures,
        "chords": [c.model_dump() for c in score.chords[:24]],
        "key_recommendation": key_rec.model_dump(),
        "playability": {
            "score": playability.playability_score,
            "level": playability.recommended_level,
            "label": playability.label,
        },
        "strum_patterns": [
            {"name": p.name, "notation": p.notation(), "description": p.description}
            for p in patterns
        ],
    }
