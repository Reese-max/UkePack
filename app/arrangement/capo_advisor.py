"""Capo suggestions and small-hand (kids) fingering helpers (BACKLOG U1-b).

A capo raises every open string, so fretting an easy open-position shape with the
capo on fret *c* sounds *c* semitones higher.  For songs whose written chords are
hard barre shapes (B, E, Bb …) we recommend a capo position that lets a child fret
simple open chords while the music still sounds in the original key — the standard
small-hands strategy taught for beginner ukulele.
"""

from pydantic import BaseModel, Field

from app.arrangement.chord_simplify import simplify
from app.arrangement.key_advisor import BEGINNER_FRIENDLY_CHORDS, CAUTION_CHORDS
from app.core.music_theory import transpose_chord_symbol
from app.models import Score

# Verified beginner substitutions: an easier chord that keeps the same musical
# role and already has a charted ukulele fingering.  Kept intentionally small —
# only swaps endorsed by ukulele teaching practice (E → E7).  Hard chords with no
# charted easy shape (B, Bm, Bb …) return None; the capo is their answer.
_KID_SUBSTITUTIONS: dict[str, str] = {
    "E": "E7",
}

_DEFAULT_MAX_CAPO = 5


class CapoRecommendation(BaseModel):
    """A capo suggestion that turns hard shapes into kid-friendly open chords."""

    capo_fret: int
    played_chords: list[str] = Field(default_factory=list)
    hard_chords: list[str] = Field(default_factory=list)
    reason: str


def suggest_capo(score: Score, max_capo: int = _DEFAULT_MAX_CAPO) -> CapoRecommendation:
    """Recommend a capo position so a child can fret simple open chords."""
    base_chords = _unique_simplified_chords(score)
    if not base_chords:
        return CapoRecommendation(
            capo_fret=0,
            played_chords=[],
            hard_chords=[],
            reason="沒有和弦資料，無法建議 capo。",
        )

    best_fret, best_shapes = _best_capo(base_chords, max_capo)
    hard = [shape for shape in best_shapes if shape in CAUTION_CHORDS]
    reason = _build_reason(score.key, best_fret, best_shapes, hard)
    return CapoRecommendation(
        capo_fret=best_fret,
        played_chords=best_shapes,
        hard_chords=hard,
        reason=reason,
    )


def kid_friendly_substitution(chord: str) -> str | None:
    """Return an easier same-role chord for small hands, or None if none is known."""
    return _KID_SUBSTITUTIONS.get(chord)


def hard_for_small_hands(chord: str) -> bool:
    """Report whether a chord is a known barre/stretch shape kids struggle with."""
    return chord in CAUTION_CHORDS


# ── private helpers ─────────────────────────────────────────────────────────


def _unique_simplified_chords(score: Score) -> list[str]:
    """Simplify the score's chords (in the written key), keeping unique order."""
    unique: list[str] = []
    seen: set[str] = set()
    for event in score.chords:
        shape = simplify(event.symbol)
        if shape == "N.C." or shape in seen:
            continue
        unique.append(shape)
        seen.add(shape)
    return unique


def _best_capo(base_chords: list[str], max_capo: int) -> tuple[int, list[str]]:
    """Pick the capo (0..max_capo) maximizing kid-friendly shapes; lowest wins ties."""
    best_fret = 0
    best_shapes = _shapes_for_capo(base_chords, 0)
    best_score = _friendliness(best_shapes)
    for fret in range(1, max(max_capo, 0) + 1):
        shapes = _shapes_for_capo(base_chords, fret)
        score_value = _friendliness(shapes)
        if score_value > best_score:
            best_fret, best_shapes, best_score = fret, shapes, score_value
    return best_fret, best_shapes


def _shapes_for_capo(base_chords: list[str], capo_fret: int) -> list[str]:
    """Shapes a player frets with the capo on `capo_fret` (sounding key unchanged)."""
    shapes: list[str] = []
    seen: set[str] = set()
    for chord in base_chords:
        shape = simplify(transpose_chord_symbol(chord, -capo_fret, prefer_flats=True))
        if shape in seen:
            continue
        shapes.append(shape)
        seen.add(shape)
    return shapes


def _friendliness(shapes: list[str]) -> int:
    """Score shapes: reward beginner chords, penalize caution (barre) shapes."""
    friendly = sum(shape in BEGINNER_FRIENDLY_CHORDS for shape in shapes)
    caution = sum(shape in CAUTION_CHORDS for shape in shapes)
    return friendly - 2 * caution


def _build_reason(original_key: str, capo_fret: int, shapes: list[str], hard: list[str]) -> str:
    """Explain the capo suggestion in Chinese for the teacher-facing analysis page."""
    preview = "、".join(shapes[:4])
    if capo_fret == 0:
        return f"和弦已經夠簡單，不需要 capo，直接用 {preview} 彈就好。"
    base = (
        f"夾 capo 在第 {capo_fret} 格，改用 {preview} 等開放和弦，"
        f"聽起來還是原本的 {original_key}，小朋友的手比較好按。"
    )
    if hard:
        hard_preview = "、".join(hard)
        base += f"（{hard_preview} 仍偏難，可改用更簡單的替代和弦或請大人幫忙）"
    return base
