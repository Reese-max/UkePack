"""Page 1 — 練習總覽."""

from __future__ import annotations

from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas

from app.models.pack_request import PackRequest
from app.render._layout import (
    _CONTENT_W,
    _EN,
    _LEVEL_GOALS,
    _MARGIN,
    _PAGE_H,
    _ZH,
    divider,
    footer,
    section,
    unique_chords,
)


def render_page1(c: rl_canvas.Canvas, req: PackRequest) -> None:
    """P1 — 練習總覽."""
    y = _PAGE_H - _MARGIN

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.HexColor("#111111"))
    c.drawString(_MARGIN, y - 30, req.title[:50])
    y -= 50

    parts: list[str] = [f"Level {req.level}"]
    if req.key_recommendation:
        parts.append(f"Key: {req.key_recommendation.target_key}")
    elif req.score.key:
        parts.append(f"Key: {req.score.key}")
    if req.score.bpm:
        parts.append(f"BPM: {req.score.bpm}")
    if req.playability:
        parts.append(f"Score: {req.playability.playability_score}/100")
    c.setFont(_EN, 11)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawString(_MARGIN, y, "  |  ".join(parts))
    y -= 22

    divider(c, y)
    y -= 18

    section(c, "今日使用和弦", y)
    y -= 22
    unique = unique_chords(req.score)
    c.setFont(_ZH, 16)
    c.setFillColor(colors.black)
    c.drawString(_MARGIN, y, "  ".join(unique) if unique else "（無和弦資料）")
    y -= 34

    if req.strum_patterns:
        section(c, "建議刷法", y)
        y -= 22
        for sp in req.strum_patterns[:2]:
            c.setFont(_ZH, 12)
            c.setFillColor(colors.black)
            c.drawString(_MARGIN, y, f"{sp.name}：{sp.notation()}  —  {sp.description}")
            y -= 20
        y -= 8

    divider(c, y)
    y -= 18

    if req.playability:
        section(c, "可彈性評估", y)
        y -= 22
        c.setFont(_ZH, 13)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(
            _MARGIN,
            y,
            f"{req.playability.playability_score} / 100  —  {req.playability.label}",
        )
        y -= 30

    goals = _LEVEL_GOALS.get(req.level, _LEVEL_GOALS[1])
    box_h = float(18 + len(goals) * 22)
    c.setFillColor(colors.HexColor("#F8F5E6"))
    c.setStrokeColor(colors.HexColor("#BBBBBB"))
    c.roundRect(_MARGIN, y - box_h, _CONTENT_W, box_h, 6, fill=1, stroke=1)
    section(c, "今日目標", y - 4, underline=False)
    gy = y - 24
    for goal in goals:
        c.setFont(_ZH, 13)
        c.setFillColor(colors.black)
        c.drawString(_MARGIN + 14, gy, f"\u2610  {goal}")
        gy -= 22

    footer(c, req, 1)
