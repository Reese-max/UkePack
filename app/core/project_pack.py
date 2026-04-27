"""Shared project-to-PDF rendering helpers."""

from __future__ import annotations

from app.arrangement.key_advisor import suggest_key
from app.arrangement.level_classifier import classify
from app.arrangement.strum_pattern import suggest_for_level
from app.core.chord_sheet import parse_chord_sheet
from app.core.teacher_review import (
    has_teacher_review,
    load_teacher_review,
    review_score,
)
from app.models.pack_request import PackRequest
from app.models.project import Project
from app.models.score import Score
from app.render.pdf import render_pdf


def pdf_filename(title: str) -> str:
    """Return a filesystem-friendly PDF filename stem."""
    return title[:50].replace(" ", "_") + ".pdf"


def render_project_pdf(project: Project) -> bytes:
    """Render a project's current practice-pack PDF bytes."""
    score = _load_score(project)
    review = load_teacher_review(project, score) if has_teacher_review(project) else None
    export_score = review_score(project, review, score) if review is not None else score
    export_level = review.current.arrangement_level if review is not None else project.arrangement_level
    pack = PackRequest(
        title=project.title,
        source_type=project.source_type,
        level=export_level,
        score=export_score,
        key_recommendation=suggest_key(export_score),
        strum_patterns=suggest_for_level(export_score, export_level),
        playability=classify(export_score),
        teacher_review=review.current if review is not None else None,
    )
    return render_pdf(pack)


def _load_score(project: Project) -> Score:
    if project.score_json is not None:
        return Score.model_validate_json(project.score_json)
    if project.chords_text is not None:
        return parse_chord_sheet(project.title, project.chords_text)
    raise ValueError("No score data; import a MusicXML file or add chords first")
