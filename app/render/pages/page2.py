"""Page 2 — 和弦指法圖 + 刷法練習."""

from __future__ import annotations

from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas

from app.models.pack_request import PackRequest
from app.render._layout import (
    _MARGIN,
    _PAGE_H,
    _ZH,
    chord_grid,
    footer,
    page_title,
    section,
    unique_chords,
)


def render_page2(c: rl_canvas.Canvas, req: PackRequest) -> None:
    """P2 — 和弦指法圖."""
    y = _PAGE_H - _MARGIN
    page_title(c, "和弦指法圖", y)
    y -= 44

    unique = unique_chords(req.score)
    bottom = chord_grid(c, unique, _MARGIN, y, colorable=req.large_print)

    strum_y = bottom - 30.0
    if req.teacher_review and req.teacher_review.strum_notation and strum_y > _MARGIN + 80:
        section(c, "刷法練習", strum_y)
        strum_y -= 22
        strum_line = f"{req.teacher_review.strum_name}：{req.teacher_review.strum_notation}"
        c.setFont("Helvetica-Bold" if strum_line.isascii() else _ZH, 12)
        c.setFillColor(colors.black)
        c.drawString(_MARGIN, strum_y, strum_line)
        strum_y -= 18
        if req.teacher_review.strum_description:
            c.setFont(
                "Helvetica" if req.teacher_review.strum_description.isascii() else _ZH,
                10,
            )
            c.setFillColor(colors.HexColor("#666666"))
            c.drawString(_MARGIN + 20, strum_y, req.teacher_review.strum_description[:76])
            strum_y -= 22
    elif req.strum_patterns and strum_y > _MARGIN + 80:
        section(c, "刷法練習", strum_y)
        strum_y -= 22
        for sp in req.strum_patterns[:3]:
            c.setFont(_ZH, 12)
            c.setFillColor(colors.black)
            bpm_hint = f"  ♩={sp.bpm_range[0]}–{sp.bpm_range[1]} BPM"
            c.drawString(_MARGIN, strum_y, f"{sp.name}（{sp.time_signature}）：{sp.notation()}{bpm_hint}")
            strum_y -= 18
            c.setFont(_ZH, 10)
            c.setFillColor(colors.HexColor("#666666"))
            c.drawString(_MARGIN + 20, strum_y, sp.description)
            strum_y -= 22

    footer(c, req, 2)
