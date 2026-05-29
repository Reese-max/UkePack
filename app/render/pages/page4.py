"""Page 4 — 老師 / 家長備註 + 七日練習計畫."""

from __future__ import annotations

from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas

from app.arrangement.tempo import tempo_ladder
from app.models.pack_request import PackRequest
from app.render._layout import (
    _CONTENT_W,
    _LEVEL_PRACTICE_STEPS,
    _MARGIN,
    _PAGE_H,
    _ZH,
    footer,
    page_title,
    practice_table,
    section,
)


def render_page4(c: rl_canvas.Canvas, req: PackRequest) -> None:
    """P4 — 老師 / 家長備註."""
    y = _PAGE_H - _MARGIN
    page_title(c, "老師 / 家長備註", y)
    y -= 44

    section(c, f"練習順序建議（Level {req.level}）", y)
    y -= 22
    steps = _LEVEL_PRACTICE_STEPS.get(req.level, _LEVEL_PRACTICE_STEPS[1])
    for step in steps:
        c.setFont(_ZH, 12)
        c.setFillColor(colors.black)
        c.drawString(_MARGIN + 8, y, step)
        y -= 18
    y -= 10

    section(c, "漸進速度練習（慢→原速）", y)
    y -= 22
    for tempo_step in tempo_ladder(req.score.bpm):
        c.setFont(_ZH, 12)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(_MARGIN + 8, y, f"☐  {tempo_step.label}  ♩= {tempo_step.bpm} BPM")
        y -= 18
    y -= 10

    note_title = "老師練習說明" if req.teacher_review and req.teacher_review.practice_notes else "常見問題"
    section(c, note_title, y)
    y -= 22
    box_h = 70.0
    c.setFillColor(colors.HexColor("#FFF8DC"))
    c.setStrokeColor(colors.HexColor("#CCCCCC"))
    c.roundRect(_MARGIN, y - box_h, _CONTENT_W, box_h, 4, fill=1, stroke=1)
    ny = y - 16
    notes = (
        [line.strip() for line in req.teacher_review.practice_notes.splitlines() if line.strip()][:3]
        if req.teacher_review and req.teacher_review.practice_notes
        else [
            "・換和弦時先看下一個和弦",
            "・右手不要停，即使換和弦也保持節奏",
            "・速度慢才能彈正確，正確後再加快",
        ]
    )
    for note in notes:
        c.setFont(_ZH, 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(_MARGIN + 10, ny, note[:76])
        ny -= 20
    y -= box_h + 16

    section(c, "家長指引", y)
    y -= 22
    for tip in [
        "・每天 10 分鐘，固定時間最有效",
        "・先稱讚有彈出聲音，再慢慢要求準確",
        "・卡住時用 capo 或更慢的速度，不要硬撐",
    ]:
        c.setFont(_ZH, 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(_MARGIN + 8, y, tip)
        y -= 18
    y -= 10

    section(c, "七日練習計畫", y)
    y -= 24
    practice_table(c, y)

    footer(c, req, 4)
