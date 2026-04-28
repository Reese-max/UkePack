"""Teacher review persistence and PDF override helpers (FR-013)."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

from app.arrangement.section_detector import detect_sections
from app.arrangement.strum_pattern import suggest_for_level
from app.config import get_settings
from app.models.project import Project
from app.models.score import ChordEvent, Score, ScoreSection
from app.models.teacher_review import (
    TeacherReviewCompareRow,
    TeacherReviewDraft,
    TeacherReviewState,
    TeacherReviewTemplate,
)

_SECTION_ALIASES = {
    "intro": "intro",
    "前奏": "intro",
    "verse": "verse",
    "主歌": "verse",
    "chorus": "chorus",
    "副歌": "chorus",
    "hook": "chorus",
}
_SECTION_HEADERS = {"intro": "前奏:", "verse": "主歌:", "chorus": "副歌:"}
_COMPARE_LABELS = {
    "arrangement_level": "難度等級",
    "chords_text": "和弦內容",
    "strum_name": "刷法名稱",
    "strum_notation": "刷法箭頭",
    "strum_description": "刷法說明",
    "tab_notes": "TAB 提示",
    "practice_notes": "練習說明",
}


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _review_path(project: Project) -> Path:
    if project.id is None:
        raise ValueError("Project must be saved before review data can be stored")
    stamp = project.created_at.astimezone(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    return get_settings().data_dir / "projects" / str(project.id) / f"teacher_review_{stamp}.json"


def has_teacher_review(project: Project) -> bool:
    """Return True when a persisted teacher-review manifest exists for the project."""
    return _review_path(project).exists()


def load_teacher_review(project: Project, score: Score) -> TeacherReviewState:
    """Load persisted teacher-review state, or derive a default draft from the project."""
    path = _review_path(project)
    if path.exists():
        payload = TeacherReviewState.model_validate_json(path.read_text(encoding="utf-8"))
        return _with_compare(payload)
    return _with_compare(_default_state(project, score))


def save_teacher_review(project: Project, state: TeacherReviewState) -> TeacherReviewState:
    """Persist teacher-review state under the project's data directory."""
    hydrated = _with_compare(state.model_copy(update={"saved_at": _utc_now()}))
    path = _review_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(hydrated.model_dump_json(indent=2), encoding="utf-8")
    return hydrated


def update_teacher_review(project: Project, score: Score, draft: TeacherReviewDraft) -> TeacherReviewState:
    """Validate and persist a teacher-edited review draft."""
    _validate_level(draft.arrangement_level)
    parse_review_chord_sheet(project.title, draft.chords_text)
    state = load_teacher_review(project, score)
    project.arrangement_level = draft.arrangement_level
    project.updated_at = _utc_now()
    return save_teacher_review(
        project,
        state.model_copy(
            update={
                "current": draft,
                "too_hard": state.too_hard or draft.arrangement_level < state.original.arrangement_level,
            }
        ),
    )


def downgrade_teacher_review(project: Project, score: Score) -> TeacherReviewState:
    """Mark the current arrangement as too hard and lower the saved level by one."""
    state = load_teacher_review(project, score)
    next_level = max(1, state.current.arrangement_level - 1)
    name, notation, description = _primary_pattern(score, next_level)
    current = state.current.model_copy(
        update={
            "arrangement_level": next_level,
            "strum_name": name,
            "strum_notation": notation,
            "strum_description": description,
        }
    )
    project.arrangement_level = next_level
    project.updated_at = _utc_now()
    return save_teacher_review(project, state.model_copy(update={"current": current, "too_hard": True}))


def restore_teacher_review(project: Project, score: Score) -> TeacherReviewState:
    """Restore the review draft back to the original system suggestion."""
    state = load_teacher_review(project, score)
    original = state.original.model_copy(deep=True)
    project.arrangement_level = original.arrangement_level
    project.updated_at = _utc_now()
    return save_teacher_review(project, state.model_copy(update={"current": original, "too_hard": False}))


def save_teacher_review_template(project: Project, score: Score, name: str) -> TeacherReviewState:
    """Save the current draft as a named template for later reuse."""
    template_name = name.strip()
    if not template_name:
        raise ValueError("Template name is required")
    state = load_teacher_review(project, score)
    template = TeacherReviewTemplate(name=template_name, draft=state.current.model_copy(deep=True))
    templates = [item for item in state.templates if item.name != template_name]
    templates.append(template)
    return save_teacher_review(project, state.model_copy(update={"templates": templates}))


def apply_teacher_review_template(project: Project, score: Score, name: str) -> TeacherReviewState:
    """Replace the current draft with a previously saved template."""
    state = load_teacher_review(project, score)
    template_name = name.strip()
    template = next((item for item in state.templates if item.name == template_name), None)
    if template is None:
        raise ValueError(f"Teacher review template '{template_name}' not found")
    project.arrangement_level = template.draft.arrangement_level
    project.updated_at = _utc_now()
    return save_teacher_review(
        project,
        state.model_copy(update={"current": template.draft.model_copy(deep=True), "too_hard": False}),
    )


def review_score(project: Project, review: TeacherReviewState, fallback: Score) -> Score:
    """Build the score used for export after teacher-review overrides."""
    if review.current.chords_text.strip():
        return parse_review_chord_sheet(project.title, review.current.chords_text)
    return fallback


def parse_review_chord_sheet(title: str, text: str) -> Score:
    """Parse review-mode chord text with section headers and per-measure slash splits."""
    chords: list[ChordEvent] = []
    sections: list[ScoreSection] = []
    measure = 1
    active_label: str | None = None
    active_start = 1
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith(":"):
            _close_manual_section(sections, active_label, active_start, measure)
            active_label = _normalize_section_name(line[:-1])
            active_start = measure
            continue
        for token in line.split("|"):
            symbol = token.strip()
            if not symbol:
                continue
            for beat_index, chord_symbol in enumerate(_split_measure_chords(symbol), start=1):
                chords.append(ChordEvent(symbol=chord_symbol, measure=measure, beat=float(beat_index)))
            measure += 1
    _close_manual_section(sections, active_label, active_start, measure)
    if not chords:
        raise ValueError("Teacher review chords cannot be empty")
    score = Score(title=title, key="C major", measures=measure - 1, chords=chords, sections=sections)
    if score.sections:
        return score
    return score.model_copy(update={"sections": detect_sections(score)})


def _default_state(project: Project, score: Score) -> TeacherReviewState:
    original = _default_draft(project, score)
    return TeacherReviewState(original=original, current=original.model_copy(deep=True))


def _default_draft(project: Project, score: Score) -> TeacherReviewDraft:
    name, notation, description = _primary_pattern(score, project.arrangement_level)
    return TeacherReviewDraft(
        arrangement_level=project.arrangement_level,
        chords_text=_score_to_chord_text(score),
        strum_name=name,
        strum_notation=notation,
        strum_description=description,
    )


def _primary_pattern(score: Score, level: int) -> tuple[str, str, str]:
    patterns = suggest_for_level(score, level)
    if not patterns:
        return "老師自訂刷法", "", ""
    pattern = patterns[0]
    return pattern.name, pattern.notation(), pattern.description


def _validate_level(level: int) -> None:
    if level not in {1, 2, 3}:
        raise ValueError("Teacher review level must be 1, 2, or 3")


def _score_to_chord_text(score: Score) -> str:
    by_measure = _group_measure_chords(score.chords)
    if not by_measure:
        return ""

    lines: list[str] = []
    covered: set[int] = set()
    for section in score.sections:
        section_lines = [
            " / ".join(by_measure[measure])
            for measure in range(section.start_measure, section.end_measure + 1)
            if measure in by_measure
        ]
        if not section_lines:
            continue
        lines.append(_SECTION_HEADERS.get(section.section, "Verse:"))
        lines.extend(section_lines)
        covered.update(range(section.start_measure, section.end_measure + 1))

    for measure in sorted(measure for measure in by_measure if measure not in covered):
        lines.append(" / ".join(by_measure[measure]))
    return "\n".join(lines)


def _group_measure_chords(chords: list[ChordEvent]) -> dict[int, list[str]]:
    grouped: dict[int, list[str]] = {}
    for chord in chords:
        grouped.setdefault(chord.measure, []).append(chord.symbol)
    return grouped


def _split_measure_chords(symbols: str) -> list[str]:
    return [item.strip() for item in re.split(r"\s+/\s+", symbols) if item.strip()]


def _close_manual_section(
    sections: list[ScoreSection],
    label: str | None,
    start_measure: int,
    next_measure: int,
) -> None:
    if label is None or next_measure <= start_measure:
        return
    sections.append(
        ScoreSection(
            section=label,
            start_measure=start_measure,
            end_measure=next_measure - 1,
            source="manual",
        )
    )


def _normalize_section_name(raw_name: str) -> str:
    normalized = raw_name.strip().strip("[]()").replace(" ", "").lower()
    return _SECTION_ALIASES.get(normalized, "verse")


def _with_compare(state: TeacherReviewState) -> TeacherReviewState:
    return state.model_copy(update={"compare": _build_compare(state.original, state.current)})


def _build_compare(
    original: TeacherReviewDraft,
    current: TeacherReviewDraft,
) -> list[TeacherReviewCompareRow]:
    rows: list[TeacherReviewCompareRow] = []
    for field, label in _COMPARE_LABELS.items():
        before = _format_compare_value(original, field)
        after = _format_compare_value(current, field)
        if before == after:
            continue
        rows.append(TeacherReviewCompareRow(field=field, label=label, original=before, current=after))
    return rows


def _format_compare_value(draft: TeacherReviewDraft, field: str) -> str:
    value = getattr(draft, field)
    if field == "arrangement_level":
        return f"Level {value}"
    return value.strip() or "（空白）"
