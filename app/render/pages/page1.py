"""Page 1 — 練習總覽."""

from __future__ import annotations

from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas

from app.arrangement.capo_advisor import suggest_capo
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
    lp = 1.4 if req.large_print else 1.0

    c.setFont("Helvetica-Bold", 24 * lp)
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
    c.setFont(_ZH, 16 * lp)
    c.setFillColor(colors.black)
    c.drawString(_MARGIN, y, "  ".join(unique) if unique else "（無和弦資料）")
    y -= 34

    capo = suggest_capo(req.score)
    if capo.capo_fret > 0:
        section(c, "小手建議：夾 capo", y)
        y -= 22
        c.setFont(_ZH, 13)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(
            _MARGIN, y, f"夾 capo 第 {capo.capo_fret} 格，改彈 {'  '.join(capo.played_chords)}"
        )
        y -= 30

    # competitor-research gap vs Ukulele-Tabs.com (beginner + dedicated strumming focus):
    # kids need explicit "do this now" micro-entry on overview to hit <15min first segment.
    # Level 1 quick-start callout reuses existing strum[0] + first chord (no new data).
    if req.level <= 1 and req.strum_patterns:
        section(c, "15 分鐘起步", y)
        y -= 18
        first_ch = unique[0] if unique else "和弦"
        sp0 = req.strum_patterns[0]
        bpm_hint = f"{sp0.bpm_range[0]}-{sp0.bpm_range[1]}"
        c.setFont(_ZH, 11)
        c.setFillColor(colors.HexColor("#1a5f2a"))
        c.drawString(
            _MARGIN, y,
            f"先彈 {first_ch} + {sp0.notation()}（{bpm_hint} BPM），重複 4 拍即可開始！"
        )
        y -= 20

    if req.teacher_review and req.teacher_review.strum_notation:
        section(c, "建議刷法", y)
        y -= 22
        strum_line = f"{req.teacher_review.strum_name}：{req.teacher_review.strum_notation}"
        c.setFont("Helvetica-Bold" if strum_line.isascii() else _ZH, 12)
        c.setFillColor(colors.black)
        c.drawString(_MARGIN, y, strum_line)
        y -= 20
        if req.teacher_review.strum_description:
            c.setFont(
                "Helvetica" if req.teacher_review.strum_description.isascii() else _ZH,
                11,
            )
            c.setFillColor(colors.HexColor("#555555"))
            c.drawString(_MARGIN, y, req.teacher_review.strum_description[:72])
            y -= 20
        y -= 8
    elif req.strum_patterns:
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

    if req.teacher_review and req.teacher_review.practice_notes:
        section(c, "老師練習說明", y)
        y -= 22
        for note in req.teacher_review.practice_notes.splitlines()[:3]:
            line = note.strip()
            if not line:
                continue
            c.setFont("Helvetica" if line.isascii() else _ZH, 11)
            c.setFillColor(colors.HexColor("#333333"))
            c.drawString(_MARGIN, y, line[:78])
            y -= 18
        y -= 8

    goals = _LEVEL_GOALS.get(req.level, _LEVEL_GOALS[1])
    goal_step = 22 * lp
    box_h = float(18 + len(goals) * goal_step)
    c.setFillColor(colors.HexColor("#F8F5E6"))
    c.setStrokeColor(colors.HexColor("#BBBBBB"))
    c.roundRect(_MARGIN, y - box_h, _CONTENT_W, box_h, 6, fill=1, stroke=1)
    section(c, "今日目標", y - 4, underline=False)
    gy = y - 24
    for goal in goals:
        c.setFont(_ZH, 13 * lp)
        c.setFillColor(colors.black)
        c.drawString(_MARGIN + 14, gy, f"\u2610  {goal}")
        gy -= goal_step

    footer(c, req, 1)
