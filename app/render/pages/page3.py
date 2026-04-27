"""Page 3 — 歌曲練習 (chord progression grid)."""

from __future__ import annotations

from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas

from app.models.pack_request import PackRequest
from app.models.score import ChordEvent, ScoreSection
from app.render._layout import (
    _CONTENT_W,
    _MARGIN,
    _PAGE_H,
    _ZH,
    footer,
    page_title,
)


def render_page3(c: rl_canvas.Canvas, req: PackRequest) -> None:
    """P3 — 歌曲練習."""
    y = _PAGE_H - _MARGIN
    page_title(c, "歌曲練習", y)
    y -= 44

    if req.score.sections:
        y = _section_summary(c, req.score.sections, y)
        y -= 16

    if req.teacher_review and req.teacher_review.tab_notes:
        y = _tab_notes(c, req.teacher_review.tab_notes, y)
        y -= 16

    if not req.score.chords:
        c.setFont(_ZH, 14)
        c.setFillColor(colors.HexColor("#888888"))
        c.drawString(_MARGIN, y - 20, "（無和弦資料）")
    else:
        _chord_progression(c, req.score.chords, y)

    footer(c, req, 3)


def _tab_notes(c: rl_canvas.Canvas, notes: str, y_start: float) -> float:
    """Draw teacher-authored TAB hints above the chord grid."""
    c.setFont(_ZH, 12)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawString(_MARGIN, y_start, "老師 TAB 提示")
    y = y_start - 18
    c.setFillColor(colors.HexColor("#FFF8DC"))
    c.setStrokeColor(colors.HexColor("#CCCCCC"))
    box_height = 18.0 * max(2, min(4, len([line for line in notes.splitlines() if line.strip()])))
    c.roundRect(_MARGIN, y - box_height, _CONTENT_W, box_height, 4, fill=1, stroke=1)
    text_y = y - 14
    for line in notes.splitlines()[:4]:
        content = line.strip()
        if not content:
            continue
        c.setFont(_ZH, 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(_MARGIN + 10, text_y, content[:78])
        text_y -= 16
    return y - box_height


def _section_summary(
    c: rl_canvas.Canvas, sections: list[ScoreSection], y_start: float
) -> float:
    """Draw a compact detected section map above the measure grid."""
    labels = {"intro": "前奏", "verse": "主歌", "chorus": "副歌"}
    c.setFont(_ZH, 12)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawString(_MARGIN, y_start, "段落地圖")
    y = y_start - 18
    c.setFont(_ZH, 11)
    for section in sections[:6]:
        name = labels.get(section.section, "主歌")
        start = section.start_measure
        end = section.end_measure
        source = "手動" if section.source == "manual" else "自動"
        c.drawString(_MARGIN + 8, y, f"{name}｜第 {start}-{end} 小節｜{source}")
        y -= 16
    return y


def _chord_progression(
    c: rl_canvas.Canvas, chords: list[ChordEvent], y_start: float
) -> None:
    """Draw chord symbols grouped by measure in a 4-column grid."""
    cols = 4
    cell_w = _CONTENT_W / cols
    cell_h = 55.0
    y = y_start - 8.0

    by_measure: dict[int, list[str]] = {}
    for ce in chords:
        by_measure.setdefault(ce.measure, []).append(ce.symbol)

    for i, m in enumerate(sorted(by_measure.keys())[:24]):
        col = i % cols
        row = i // cols
        x = _MARGIN + col * cell_w
        cy = y - row * cell_h
        if cy - cell_h < _MARGIN + 20:
            break
        c.setStrokeColor(colors.HexColor("#AAAAAA"))
        c.setFillColor(colors.HexColor("#F9F9F9"))
        c.rect(x, cy - cell_h, cell_w - 4, cell_h, fill=1, stroke=1)
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#888888"))
        c.drawString(x + 4, cy - 13, f"m{m}")
        syms = by_measure[m]
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.black)
        c.drawString(x + 4, cy - 37, " / ".join(syms[:4]))
