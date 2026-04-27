"""Reusable score-to-practice-pack helpers for CLI, API, and bot surfaces."""

from __future__ import annotations

from app.arrangement.key_advisor import suggest_key
from app.arrangement.level_classifier import classify
from app.arrangement.strum_pattern import suggest_for_level
from app.models.pack_request import PackRequest
from app.models.score import Score
from app.models.teacher_review import TeacherReviewDraft

SUPPORTED_SOURCE_TYPES: tuple[str, ...] = (
    "self_created",
    "suno_free",
    "suno_paid",
    "public_domain",
    "licensed",
    "private_research",
)


def build_pack_request(
    *,
    title: str,
    source_type: str,
    score: Score,
    level: int,
    teacher_review: TeacherReviewDraft | None = None,
) -> PackRequest:
    """Assemble the canonical PackRequest for a rendered score."""
    if source_type not in SUPPORTED_SOURCE_TYPES:
        raise ValueError(f"Unsupported source_type '{source_type}'")
    if level not in {1, 2, 3}:
        raise ValueError("level must be 1, 2, or 3")

    return PackRequest(
        title=title,
        source_type=source_type,
        level=level,
        score=score,
        key_recommendation=suggest_key(score),
        strum_patterns=suggest_for_level(score, level),
        playability=classify(score),
        teacher_review=teacher_review,
    )
