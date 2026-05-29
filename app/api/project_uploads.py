"""Shared upload and MusicXML import helpers for project routes."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.arrangement.key_advisor import suggest_key
from app.arrangement.level_classifier import PlayabilityResult, classify
from app.core.musicxml import MAX_IMPORT_BYTES, parse, parse_midi
from app.models import KeyRecommendation
from app.models.project import Project
from app.models.score import Score

UPLOAD_CHUNK_BYTES = 64 * 1024


async def save_upload_with_limit(
    file: UploadFile,
    destination: Path,
    *,
    max_bytes: int = MAX_IMPORT_BYTES,
    chunk_bytes: int = UPLOAD_CHUNK_BYTES,
) -> int:
    """Write an upload to disk while enforcing a streaming byte cap."""
    total_bytes = 0
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        with destination.open("wb") as handle:
            while True:
                chunk = await file.read(chunk_bytes)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise HTTPException(status_code=413, detail="File too large")
                handle.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    return total_bytes


def import_musicxml_into_project(
    project: Project,
    save_path: Path,
    *,
    relative_path: str,
) -> tuple[Score, KeyRecommendation, PlayabilityResult]:
    """Parse a saved MusicXML file and persist its analysis onto the project."""
    try:
        score = parse(save_path)
        key_recommendation = suggest_key(score)
        playability = classify(score)
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"MusicXML parse failed: {exc}") from exc

    project.musicxml_path = relative_path
    _persist_score(project, score, key_recommendation, playability)
    return score, key_recommendation, playability


def import_midi_into_project(
    project: Project,
    save_path: Path,
    *,
    relative_path: str,
) -> tuple[Score, KeyRecommendation, PlayabilityResult]:
    """Parse a saved MIDI file and persist its analysis onto the project (U2-a).

    Also records ``midi_path`` so the same upload can drive practice audio.
    MIDI carries no chord symbols, so the arrangement runs from the melody/key.
    """
    try:
        score = parse_midi(save_path)
        key_recommendation = suggest_key(score)
        playability = classify(score)
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"MIDI parse failed: {exc}") from exc

    project.midi_path = relative_path
    _persist_score(project, score, key_recommendation, playability)
    return score, key_recommendation, playability


def _persist_score(
    project: Project,
    score: Score,
    key_recommendation: KeyRecommendation,
    playability: PlayabilityResult,
) -> None:
    """Write parsed-score analysis fields onto the project row."""
    project.score_json = score.model_dump_json()
    project.original_key = score.key
    project.bpm = score.bpm
    project.target_key = key_recommendation.target_key
    project.arrangement_level = playability.recommended_level
    project.updated_at = datetime.now(UTC)
