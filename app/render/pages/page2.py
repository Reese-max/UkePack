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
    bottom = chord_grid(c, unique, _MARGIN, y)

    strum_y = bottom - 30.0
    if req.strum_patterns and strum_y > _MARGIN + 80:
        section(c, "刷法練習", strum_y)
        strum_y -= 22
        for sp in req.strum_patterns[:3]:
            c.setFont(_ZH, 12)
            c.setFillColor(colors.black)
            c.drawString(_MARGIN, strum_y, f"{sp.name}（{sp.time_signature}）：{sp.notation()}")
            strum_y -= 18
            c.setFont(_ZH, 10)
            c.setFillColor(colors.HexColor("#666666"))
            c.drawString(_MARGIN + 20, strum_y, sp.description)
            strum_y -= 22

    footer(c, req, 2)
