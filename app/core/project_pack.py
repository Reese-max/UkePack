"""Shared project-to-PDF rendering helpers."""

from __future__ import annotations

from app.core.chord_sheet import parse_chord_sheet
from app.core.practice_pack import build_pack_request
from app.core.teacher_review import (
    has_teacher_review,
    load_teacher_review,
    review_score,
)
from app.models.project import Project
from app.models.score import Score
from app.render.pdf import render_pdf


def pdf_filename(title: str, level: int | None = None, key: str | None = None) -> str:
    """Return PRD §11.1 compliant filename: {title}_UkePack_Level{N}_{Key}_{date}.pdf."""
    from datetime import UTC, datetime

    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    safe_title = title[:50].replace(" ", "_")
    # Keep only the tonic (e.g. "C major" → "C", "F# minor" → "F#")
    clean_key = key.split()[0].replace("#", "s") if key else None
    parts: list[str] = [safe_title, "UkePack"]
    if level is not None:
        parts.append(f"Level{level}")
    if clean_key:
        parts.append(clean_key)
    parts.append(date_str)
    return "_".join(parts) + ".pdf"


def render_project_pdf(project: Project) -> bytes:
    """Render a project's current practice-pack PDF bytes."""
    score = _load_score(project)
    review = load_teacher_review(project, score) if has_teacher_review(project) else None
    export_score = review_score(project, review, score) if review is not None else score
    export_level = review.current.arrangement_level if review is not None else project.arrangement_level
    pack = build_pack_request(
        title=project.title,
        source_type=project.source_type,
        score=export_score,
        level=export_level,
        teacher_review=review.current if review is not None else None,
    )
    return render_pdf(pack)


def _load_score(project: Project) -> Score:
    if project.score_json is not None:
        return Score.model_validate_json(project.score_json)
    if project.chords_text is not None:
        return parse_chord_sheet(project.title, project.chords_text)
    raise ValueError("No score data; import a MusicXML file or add chords first")
