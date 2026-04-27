"""Project CRUD and pipeline endpoints (Stage 7, P1-01 - P1-10)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, Response
from sqlmodel import Session, SQLModel

from app.config import get_settings
from app.core.db import get_session
from app.models.project import Project, ProjectCreate, ProjectRead
from app.models.score import ChordEvent, Score

router = APIRouter(prefix="/api/projects", tags=["projects"])

SessionDep = Annotated[Session, Depends(get_session)]

_MUSICXML_EXTS = {".musicxml", ".xml", ".mxl"}
_MIDI_EXTS = {".mid", ".midi"}


# ── Request bodies ─────────────────────────────────────────────────────────


class ChordsBody(SQLModel):
    """Body for POST …/chords (FR-004)."""

    text: str


class ArrangeBody(SQLModel):
    """Body for POST …/arrange."""

    level: int = 1


class LicenseBody(SQLModel):
    """Body for POST …/license (P1-10)."""

    confirmed: bool


# ── Helpers ────────────────────────────────────────────────────────────────


def _get_or_404(session: Session, project_id: int) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _parse_chords_text(text: str, title: str) -> Score:
    """Build a minimal Score from pipe-delimited chord text (FR-004)."""
    chords: list[ChordEvent] = []
    measure = 1
    for line in text.splitlines():
        clean = line.strip()
        if not clean or clean.endswith(":"):
            continue
        for token in clean.split("|"):
            symbol = token.strip()
            if symbol:
                chords.append(ChordEvent(symbol=symbol, measure=measure, beat=1.0))
                measure += 1
    return Score(title=title, key="C major", measures=max(measure - 1, 0), chords=chords)


def _load_score(project: Project) -> Score:
    """Deserialize stored Score, or build from chords_text."""
    if project.score_json is not None:
        return Score.model_validate_json(project.score_json)
    if project.chords_text is not None:
        return _parse_chords_text(project.chords_text, project.title)
    raise HTTPException(422, "No score data; import a MusicXML file or add chords first")


def _to_read(project: Project) -> ProjectRead:
    return ProjectRead.model_validate(project.model_dump())


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.post("", status_code=status.HTTP_201_CREATED)
def create_project(body: ProjectCreate, session: SessionDep) -> ProjectRead:
    """FR-001: Create a new project."""
    project = Project(**body.model_dump())
    session.add(project)
    session.commit()
    session.refresh(project)
    return _to_read(project)


@router.get("/{project_id}")
def get_project(project_id: int, session: SessionDep) -> ProjectRead:
    """Get project metadata."""
    return _to_read(_get_or_404(session, project_id))


@router.post("/{project_id}/import")
async def import_musicxml(
    project_id: int,
    file: Annotated[UploadFile, File()],
    session: SessionDep,
) -> dict[str, Any]:
    """FR-002: Upload and parse a MusicXML / MXL file."""
    project = _get_or_404(session, project_id)

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _MUSICXML_EXTS:
        raise HTTPException(400, f"Unsupported file type '{suffix}'. Use .musicxml / .mxl")

    settings = get_settings()
    save_dir = settings.data_dir / "projects" / str(project_id)
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / f"original{suffix}"

    content = await file.read()
    save_path.write_bytes(content)

    from app.arrangement.key_advisor import suggest_key
    from app.arrangement.level_classifier import classify
    from app.core.musicxml import parse

    try:
        score = parse(save_path)
    except (ValueError, Exception) as exc:
        save_path.unlink(missing_ok=True)
        raise HTTPException(422, f"MusicXML parse failed: {exc}") from exc

    key_rec = suggest_key(score)
    playability = classify(score)

    project.musicxml_path = str(save_path.relative_to(settings.data_dir))
    project.score_json = score.model_dump_json()
    project.original_key = score.key
    project.bpm = score.bpm
    project.target_key = key_rec.target_key
    project.arrangement_level = playability.recommended_level
    project.updated_at = datetime.utcnow()
    session.add(project)
    session.commit()

    return {
        "project_id": project_id,
        "key": score.key,
        "bpm": score.bpm,
        "time_signature": score.time_signature,
        "measures": score.measures,
        "chord_count": len(score.chords),
        "recommended_level": playability.recommended_level,
        "playability_score": playability.playability_score,
        "target_key": key_rec.target_key,
    }


@router.post("/{project_id}/midi")
async def import_midi(
    project_id: int,
    file: Annotated[UploadFile, File()],
    session: SessionDep,
) -> dict[str, Any]:
    """FR-003: Upload a MIDI file (save + basic metadata; full parsing in Phase 2)."""
    project = _get_or_404(session, project_id)

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _MIDI_EXTS:
        raise HTTPException(400, f"Unsupported MIDI extension '{suffix}'. Use .mid / .midi")

    settings = get_settings()
    save_dir = settings.data_dir / "projects" / str(project_id)
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / f"original{suffix}"

    content = await file.read()
    save_path.write_bytes(content)

    project.midi_path = str(save_path.relative_to(settings.data_dir))
    project.updated_at = datetime.utcnow()
    session.add(project)
    session.commit()

    return {"project_id": project_id, "midi_path": project.midi_path, "status": "saved"}


@router.post("/{project_id}/chords")
def add_chords(
    project_id: int,
    body: ChordsBody,
    session: SessionDep,
) -> dict[str, Any]:
    """FR-004: Set manual pipe-delimited chord input."""
    project = _get_or_404(session, project_id)
    score = _parse_chords_text(body.text, project.title)
    project.chords_text = body.text
    project.score_json = score.model_dump_json()
    project.original_key = score.key
    project.updated_at = datetime.utcnow()
    session.add(project)
    session.commit()
    return {"project_id": project_id, "chord_count": len(score.chords)}


@router.get("/{project_id}/analysis")
def get_analysis(project_id: int, session: SessionDep) -> dict[str, Any]:
    """P1-05: Return Key / BPM / chord list / difficulty analysis."""
    project = _get_or_404(session, project_id)
    score = _load_score(project)

    from app.arrangement.key_advisor import suggest_key
    from app.arrangement.level_classifier import classify

    key_rec = suggest_key(score)
    playability = classify(score)

    return {
        "key": score.key,
        "bpm": score.bpm,
        "time_signature": score.time_signature,
        "measures": score.measures,
        "chords": [c.model_dump() for c in score.chords],
        "key_recommendation": key_rec.model_dump(),
        "playability": {
            "score": playability.playability_score,
            "level": playability.recommended_level,
            "label": playability.label,
        },
    }


@router.post("/{project_id}/arrange")
def arrange(project_id: int, body: ArrangeBody, session: SessionDep) -> dict[str, Any]:
    """P1-06: Store arrangement level and return suggested strum patterns."""
    if body.level not in (1, 2, 3):
        raise HTTPException(400, "level must be 1, 2, or 3")
    project = _get_or_404(session, project_id)
    score = _load_score(project)

    from app.arrangement.strum_pattern import suggest_for_level

    patterns = suggest_for_level(score, body.level)
    project.arrangement_level = body.level
    project.updated_at = datetime.utcnow()
    session.add(project)
    session.commit()

    return {
        "project_id": project_id,
        "level": body.level,
        "strum_patterns": [
            {"name": p.name, "notation": p.notation(), "description": p.description}
            for p in patterns
        ],
    }


@router.post("/{project_id}/license")
def confirm_license(
    project_id: int, body: LicenseBody, session: SessionDep
) -> dict[str, Any]:
    """P1-10: Record user's license acknowledgment (required before PDF export)."""
    project = _get_or_404(session, project_id)
    project.license_confirmed = body.confirmed
    project.updated_at = datetime.utcnow()
    session.add(project)
    session.commit()
    return {"project_id": project_id, "license_confirmed": project.license_confirmed}


@router.get("/{project_id}/export.pdf")
def export_pdf(project_id: int, session: SessionDep) -> Response:
    """P1-07: Download practice pack PDF (requires license_confirmed=True, FR-015)."""
    project = _get_or_404(session, project_id)
    if not project.license_confirmed:
        raise HTTPException(
            status_code=403,
            detail="License not confirmed; POST /api/projects/{id}/license first",
        )
    score = _load_score(project)

    from app.arrangement.key_advisor import suggest_key
    from app.arrangement.level_classifier import classify
    from app.arrangement.strum_pattern import suggest_for_level
    from app.models.pack_request import PackRequest
    from app.render.pdf import render_pdf

    pack = PackRequest(
        title=project.title,
        source_type=project.source_type,
        level=project.arrangement_level,
        score=score,
        key_recommendation=suggest_key(score),
        strum_patterns=suggest_for_level(score, project.arrangement_level),
        playability=classify(score),
    )
    pdf_bytes = render_pdf(pack)
    fname = project.title[:50].replace(" ", "_") + ".pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@router.get("/{project_id}/export.musicxml")
def export_musicxml(project_id: int, session: SessionDep) -> FileResponse:
    """P1-08: Download the original imported MusicXML file."""
    project = _get_or_404(session, project_id)
    if project.musicxml_path is None:
        raise HTTPException(404, "No MusicXML file imported for this project")
    settings = get_settings()
    full_path = settings.data_dir / project.musicxml_path
    if not full_path.exists():
        raise HTTPException(404, "MusicXML file not found on disk")
    return FileResponse(
        str(full_path),
        media_type="application/xml",
        filename=f"{project.title[:50]}.musicxml",
    )
