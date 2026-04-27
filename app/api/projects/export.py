"""Project export routes for PDF and MusicXML downloads."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response

from app.arrangement.key_advisor import suggest_key
from app.arrangement.level_classifier import classify
from app.arrangement.strum_pattern import suggest_for_level
from app.config import get_settings
from app.models.pack_request import PackRequest
from app.render.pdf import render_pdf

from ._shared import SessionDep, get_project_or_404, load_score

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _pdf_filename(title: str) -> str:
    return title[:50].replace(" ", "_") + ".pdf"


@router.get("/{project_id}/export.pdf")
def export_pdf(project_id: int, session: SessionDep) -> Response:
    """Download a practice-pack PDF after license confirmation."""
    project = get_project_or_404(session, project_id)
    if not project.license_confirmed:
        raise HTTPException(
            status_code=403,
            detail="License not confirmed; POST /api/projects/{id}/license first",
        )

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
