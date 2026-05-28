"""Key recommendation helpers for beginner-friendly ukulele arrangements."""

import re
from dataclasses import dataclass

from app.arrangement.chord_simplify import simplify
from app.core.music_theory import signed_semitone_shift, transpose_chord_symbol
from app.models import KeyRecommendation, Score

_CANDIDATE_KEYS: tuple[str, ...] = (
    "C major",
    "G major",
    "F major",
    "A minor",
    "D major",
)
_KEY_PRIORITY: dict[str, int] = {name: index for index, name in enumerate(_CANDIDATE_KEYS)}
_PREFERRED_CHORDS = {"Am", "C", "F", "G"}
# Public so capo_advisor (U1-b) shares one source of truth for chord difficulty.
BEGINNER_FRIENDLY_CHORDS = {"A7", "Am", "C", "D7", "Dm", "Em", "F", "G", "G7"}
CAUTION_CHORDS = {"Ab", "B", "Bb", "Bm", "E", "Eb", "F#m"}
_KEY_PATTERN = re.compile(r"^([A-G][#b]?)\s+([a-z]+)$")


@dataclass(frozen=True)
class _CandidateEvaluation:
    target_key: str
    semitone_shift: int
    score: int
    preferred_count: int
    friendly_count: int
    friendly_chords: list[str]
    reason: str


def suggest_key(score: Score) -> KeyRecommendation:
    """Recommend a ukulele-friendly key using chord simplicity and light transposition."""
    original_tonic, original_mode = _parse_key_name(score.key)
    if original_mode not in {"major", "minor"}:
        return _build_mode_fallback(score, original_tonic, original_mode)

    evaluations = tuple(
        _evaluate_candidate(score, candidate, original_tonic) for candidate in _CANDIDATE_KEYS
    )
    selected = _select_candidate(evaluations)
    return KeyRecommendation(
        original_key=score.key,
        target_key=selected.target_key,
        semitone_shift=selected.semitone_shift,
        friendly_chords=selected.friendly_chords,
        reason=selected.reason,
    )


def _evaluate_candidate(score: Score, candidate_key: str, original_tonic: str) -> _CandidateEvaluation:
    target_tonic, _ = _parse_key_name(candidate_key)
    semitone_shift = signed_semitone_shift(original_tonic, target_tonic)
    friendly_chords = _transpose_and_simplify_chords(score, semitone_shift, target_tonic)
    preferred_count = sum(chord in _PREFERRED_CHORDS for chord in friendly_chords)
    friendly_count = sum(chord in BEGINNER_FRIENDLY_CHORDS for chord in friendly_chords)
    score_value = _score_candidate(friendly_chords, preferred_count, friendly_count)
    return _CandidateEvaluation(
        target_key=candidate_key,
        semitone_shift=semitone_shift,
        score=score_value,
        preferred_count=preferred_count,
        friendly_count=friendly_count,
        friendly_chords=friendly_chords,
        reason=_build_reason(candidate_key, semitone_shift, friendly_chords),
    )


def _parse_key_name(key_name: str) -> tuple[str, str]:
    """Split a normalized key string into tonic and mode."""
    match = _KEY_PATTERN.match(key_name.strip())
    if match is None:
        raise ValueError(f"Unsupported key format: {key_name}")
    tonic, mode = match.groups()
    return tonic, mode.lower()


def _build_mode_fallback(score: Score, original_tonic: str, original_mode: str) -> KeyRecommendation:
    """Default modal or otherwise unsupported keys back to C major."""
    fallback_key = "C major"
    semitone_shift = signed_semitone_shift(original_tonic, "C")
    friendly_chords = _transpose_and_simplify_chords(score, semitone_shift, "C")
    chord_preview = "、".join(friendly_chords[:4])
    return KeyRecommendation(
        original_key=score.key,
        target_key=fallback_key,
        semitone_shift=semitone_shift,
        friendly_chords=friendly_chords,
        # {original_mode} 調式不支援自動移調, fallback 到 C major
        reason=(
            f"{score.key} 使用 {original_mode} 調式（不支援自動移調），改用 "
            f"{fallback_key} 為基礎，主要和弦為 {chord_preview}。"
        ),
    )


def _transpose_and_simplify_chords(score: Score, semitone_shift: int, target_tonic: str) -> list[str]:
    """Project score chords into a candidate key and keep stable unique shapes."""
    prefer_flats = "b" in target_tonic or target_tonic == "F"
    if not score.chords:
        return [target_tonic]

    unique_chords: list[str] = []
    seen: set[str] = set()
    for chord_event in score.chords:
        transposed = transpose_chord_symbol(chord_event.symbol, semitone_shift, prefer_flats)
        simplified = simplify(transposed)
        if simplified == "N.C.":
            continue
        if simplified not in seen:
            unique_chords.append(simplified)
            seen.add(simplified)
    return unique_chords or [target_tonic]


def _score_candidate(chords: list[str], preferred_count: int, friendly_count: int) -> int:
    """Score candidate keys by how many shapes remain in the beginner set."""
    caution = sum(chord in CAUTION_CHORDS for chord in chords)
    accidentals = sum("#" in chord or "b" in chord for chord in chords)
    return preferred_count + friendly_count - (2 * caution) - accidentals


def _select_candidate(evaluations: tuple[_CandidateEvaluation, ...]) -> _CandidateEvaluation:
    """Prefer close-enough friendly keys, then avoid upward transposition."""
    contenders = [
        candidate
        for candidate in evaluations
        if candidate.friendly_count >= 3 and candidate.preferred_count >= 2
    ]
    if not contenders:
        max_score = max(candidate.score for candidate in evaluations)
        contenders = [candidate for candidate in evaluations if candidate.score >= max_score - 3]

    downward_or_static = [candidate for candidate in contenders if candidate.semitone_shift <= 0]
    if downward_or_static:
        contenders = downward_or_static

    min_distance = min(abs(candidate.semitone_shift) for candidate in contenders)
    distance_matched = [
        candidate for candidate in contenders if abs(candidate.semitone_shift) == min_distance
    ]
    return max(
        distance_matched,
        key=lambda candidate: (candidate.score, -_KEY_PRIORITY[candidate.target_key]),
    )


def _build_reason(candidate_key: str, semitone_shift: int, chords: list[str]) -> str:
    """Explain the recommendation in Chinese for the teacher-facing analysis page."""
    chord_preview = "、".join(chords[:4])
    if semitone_shift == 0:
        movement = "無需移調"
    elif semitone_shift < 0:
        movement = f"往下移 {abs(semitone_shift)} 個半音"
    else:
        movement = f"往上移 {semitone_shift} 個半音"
    return f"選 {candidate_key}：{movement}，主要和弦變成 {chord_preview}，孩子比較容易跟上。"
