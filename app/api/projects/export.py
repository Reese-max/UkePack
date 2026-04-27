"""Project export routes for PDF, MusicXML, and practice-audio downloads."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response

from app.arrangement.key_advisor import suggest_key
from app.arrangement.level_classifier import classify
from app.arrangement.strum_pattern import suggest_for_level
from app.config import get_settings
from app.core.practice_audio import (
    generate_practice_audio,
    get_practice_audio_file,
    load_practice_audio_manifest,
)
from app.models.pack_request import PackRequest
from app.render.pdf import render_pdf

from ._shared import SessionDep, get_project_or_404, load_score

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _pdf_filename(title: str) -> str:
    return title[:50].replace(" ", "_") + ".pdf"


def _require_license_confirmation(license_confirmed: bool) -> None:
    if not license_confirmed:
        raise HTTPException(
            status_code=403,
            detail="License not confirmed; POST /api/projects/{id}/license first",
        )


@router.get("/{project_id}/export.pdf")
def export_pdf(project_id: int, session: SessionDep) -> Response:
    """Download a practice-pack PDF after license confirmation."""
    project = get_project_or_404(session, project_id)
    _require_license_confirmation(project.license_confirmed)

    score = load_score(project)
    pack = PackRequest(
        title=project.title,
        source_type=project.source_type,
        level=project.arrangement_level,
        score=score,
        key_recommendation=suggest_key(score),
        strum_patterns=suggest_for_level(score, project.arrangement_level),
        playability=classify(score),
    )
    return Response(
        content=render_pdf(pack),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{_pdf_filename(project.title)}"'},
    )


@router.get("/{project_id}/export.musicxml")
def export_musicxml(project_id: int, session: SessionDep) -> FileResponse:
    """Download the original imported MusicXML file."""
    project = get_project_or_404(session, project_id)
    if project.musicxml_path is None:
        raise HTTPException(404, "No MusicXML file imported for this project")

    full_path = get_settings().data_dir / project.musicxml_path
    if not full_path.exists():
        raise HTTPException(404, "MusicXML file not found on disk")

    return FileResponse(
        str(full_path),
        media_type="application/xml",
        filename=f"{project.title[:50]}.musicxml",
    )


@router.get("/{project_id}/practice-audio")
def get_practice_audio_manifest(project_id: int, session: SessionDep) -> dict[str, object]:
    """Return persisted practice-audio metadata for a project."""
    project = get_project_or_404(session, project_id)
    _require_license_confirmation(project.license_confirmed)
    manifest = load_practice_audio_manifest(project)
    if manifest is None:
        raise HTTPException(404, "Practice audio has not been generated yet")
    return manifest.model_dump(mode="json")


@router.post("/{project_id}/practice-audio")
def create_practice_audio(project_id: int, session: SessionDep) -> dict[str, object]:
    """Generate slowed practice MIDI/MP3 assets from the uploaded project MIDI."""
    project = get_project_or_404(session, project_id)
    _require_license_confirmation(project.license_confirmed)
    try:
        manifest = generate_practice_audio(project)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    return manifest.model_dump(mode="json")


@router.get("/{project_id}/export.practice-audio/{variant}.{file_format}")
def export_practice_audio(
    project_id: int,
    variant: str,
    file_format: str,
    session: SessionDep,
) -> FileResponse:
    """Download one generated practice-audio artifact."""
    project = get_project_or_404(session, project_id)
    _require_license_confirmation(project.license_confirmed)
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
