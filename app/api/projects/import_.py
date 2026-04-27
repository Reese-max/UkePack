"""Project import routes for MusicXML and MIDI uploads."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.project_uploads import import_musicxml_into_project, save_upload_with_limit
from app.config import get_settings

from ._shared import MIDI_EXTS, MUSICXML_EXTS, SessionDep, get_project_or_404, utc_now

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _upload_paths(project_id: int, suffix: str) -> tuple[Path, str]:
    settings = get_settings()
    save_path = settings.data_dir / "projects" / str(project_id) / f"original{suffix}"
    return save_path, str(save_path.relative_to(settings.data_dir))


@router.post("/{project_id}/import")
async def import_musicxml(
    project_id: int,
    file: Annotated[UploadFile, File()],
    session: SessionDep,
) -> dict[str, Any]:
    """Upload and parse a MusicXML or MXL file."""
    project = get_project_or_404(session, project_id)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in MUSICXML_EXTS:
        raise HTTPException(400, f"Unsupported file type '{suffix}'. Use .musicxml / .mxl")

    save_path, relative_path = _upload_paths(project_id, suffix)
    await save_upload_with_limit(file, save_path)

    try:
        score, key_rec, playability = import_musicxml_into_project(
            project,
            save_path,
            relative_path=relative_path,
        )
    except Exception as exc:
        save_path.unlink(missing_ok=True)
        raise HTTPException(422, f"MusicXML parse failed: {exc}") from exc

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
    """Upload a MIDI file and store its saved path."""
    project = get_project_or_404(session, project_id)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in MIDI_EXTS:
        raise HTTPException(400, f"Unsupported MIDI extension '{suffix}'. Use .mid / .midi")

    save_path, relative_path = _upload_paths(project_id, suffix)
    await save_upload_with_limit(file, save_path)
    project.midi_path = relative_path
    project.updated_at = utc_now()
    session.add(project)
    session.commit()
    return {"project_id": project_id, "midi_path": project.midi_path, "status": "saved"}
