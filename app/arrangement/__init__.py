"""Arrangement modules."""

from app.arrangement.capo_advisor import (
    CapoRecommendation,
    hard_for_small_hands,
    kid_friendly_substitution,
    suggest_capo,
)
from app.arrangement.chord_simplify import simplify
from app.arrangement.key_advisor import suggest_key
from app.arrangement.level_classifier import PlayabilityResult, classify
from app.arrangement.strum_pattern import StrumPattern, all_patterns, suggest, suggest_for_level

__all__ = [
    "CapoRecommendation",
    "PlayabilityResult",
    "StrumPattern",
    "all_patterns",
    "classify",
    "hard_for_small_hands",
    "kid_friendly_substitution",
    "simplify",
    "suggest",
    "suggest_capo",
    "suggest_for_level",
    "suggest_key",
]
