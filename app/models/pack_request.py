"""Practice-pack request model shared across demo, API, and PDF rendering."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.arrangement.level_classifier import PlayabilityResult
from app.arrangement.strum_pattern import StrumPattern
from app.models.score import KeyRecommendation, Score


@dataclass
class PackRequest:
    """Bundle of data needed to render a practice pack PDF."""

    title: str
    source_type: str = "public_domain"
    level: int = 1
    score: Score = field(default_factory=lambda: Score(title="", key="C", measures=0))
    key_recommendation: KeyRecommendation | None = None
    strum_patterns: list[StrumPattern] = field(default_factory=list)
    playability: PlayabilityResult | None = None
