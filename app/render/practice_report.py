"""Practice session report PDF — single-page A4 summary.

Competitor-research(UkePack): vs Yousician practice session reports.
Generates a printable summary from PracticeLog data for teachers/parents
to track student progress.
"""

from __future__ import annotations

import io
from datetime import UTC, datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas as rl_canvas

from app.render._layout import _CONTENT_W, _MARGIN, _ZH, section

pdfmetrics.registerFont(UnicodeCIDFont("MSung-Light"))

_PAGE_W, _PAGE_H = A4
_EN = "Helvetica"
_EN_B = "Helvetica-Bold"


def render_practice_report(
    project_title: str,
    stats: dict[str, Any],
) -> bytes:
    """Render a single-page practice report PDF and return raw bytes.

    *stats* is the dict returned by the practice-progress API endpoint.
    """
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)
    y = _PAGE_H - _MARGIN

    # ── title ──────────────────────────────────────────────────────────────
    c.setFont(_ZH, 20)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(_MARGIN, y - 28, "練習報告")
    c.setFont(_ZH, 12)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawString(_MARGIN, y - 48, f"曲目：{project_title[:40]}")
    c.setFont(_EN, 9)
    c.setFillColor(colors.HexColor("#888888"))
    c.drawRightString(
        _PAGE_W - _MARGIN,
        y - 48,
        f"Generated {datetime.now(UTC).strftime('%Y-%m-%d')}",
    )
    c.setStrokeColor(colors.HexColor("#333333"))
    c.setLineWidth(2)
    c.line(_MARGIN, y - 56, _PAGE_W - _MARGIN, y - 56)
    c.setLineWidth(1)
    y -= 72

    # ── stats cards ────────────────────────────────────────────────────────
    y = _draw_stat_cards(c, stats, y)
    y -= 16

    # ── top chords ─────────────────────────────────────────────────────────
    y = _draw_top_chords(c, stats, y)
    y -= 16

    # ── recent sessions ────────────────────────────────────────────────────
    y = _draw_recent_sessions(c, stats, y)
    y -= 16

    # ── recommendations ────────────────────────────────────────────────────
    _draw_recommendations(c, stats, y)

    # ── footer ─────────────────────────────────────────────────────────────
    c.setFont(_EN, 8)
    c.setFillColor(colors.HexColor("#888888"))
    c.drawString(_MARGIN, _MARGIN - 14, "UkePack AI  •  Practice Report")
    c.drawRightString(_PAGE_W - _MARGIN, _MARGIN - 14, "Page 1 / 1")
    c.setStrokeColor(colors.HexColor("#CCCCCC"))
    c.line(_MARGIN, _MARGIN, _PAGE_W - _MARGIN, _MARGIN)

    c.showPage()
    c.save()
    return buf.getvalue()


# ── drawing helpers ────────────────────────────────────────────────────────


def _draw_stat_cards(c: rl_canvas.Canvas, stats: dict[str, Any], y: float) -> float:
    """Draw a row of summary stat cards."""
    total_sessions = stats.get("total_sessions", 0)
    total_seconds = stats.get("total_seconds", 0)
    total_minutes = total_seconds // 60
    streak = stats.get("streak_days", 0)
    longest = stats.get("longest_streak", 0)
    last_practice = stats.get("last_practice")

    cards = [
        ("總練習次數", str(total_sessions)),
        ("總練習時間", f"{total_minutes} 分鐘"),
        ("連續天數", f"{streak} 天"),
        ("最長連續", f"{longest} 天"),
    ]

    if last_practice:
        try:
            lp = datetime.fromisoformat(last_practice)
            cards.append(("上次練習", lp.strftime("%m/%d %H:%M")))
        except (ValueError, TypeError):
            pass

    card_w = _CONTENT_W / len(cards)
    card_h = 52.0

    for i, (label, value) in enumerate(cards):
        x = _MARGIN + i * card_w
        # background
        c.setFillColor(colors.HexColor("#F5F8FF"))
        c.setStrokeColor(colors.HexColor("#D0D8E8"))
        c.roundRect(x + 2, y - card_h, card_w - 4, card_h, 4, fill=1, stroke=1)
        # value
        c.setFont(_ZH, 16)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawCentredString(x + card_w / 2, y - card_h + 28, value)
        # label
        c.setFont(_ZH, 9)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawCentredString(x + card_w / 2, y - card_h + 10, label)

    return y - card_h


def _draw_top_chords(c: rl_canvas.Canvas, stats: dict[str, Any], y: float) -> float:
    """Draw top practiced chords as a horizontal bar chart."""
    chord_counts: dict[str, int] = stats.get("chord_counts", {})
    if not chord_counts:
        return y

    section(c, "和弦練習排行", y)
    y -= 18

    top = sorted(chord_counts.items(), key=lambda kv: kv[1], reverse=True)[:8]
    max_count = top[0][1] if top else 1
    bar_max_w = _CONTENT_W - 100  # leave room for label + count
    row_h = 20.0

    for i, (chord, count) in enumerate(top):
        ry = y - (i + 1) * row_h
        # alternating bg
        if i % 2 == 0:
            c.setFillColor(colors.HexColor("#FAFAFA"))
            c.rect(_MARGIN, ry, _CONTENT_W, row_h, fill=1, stroke=0)

        # chord label
        c.setFont(_ZH, 9)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(_MARGIN + 4, ry + 5, chord[:10])

        # bar
        bar_w = (count / max_count) * bar_max_w if max_count > 0 else 0
        c.setFillColor(colors.HexColor("#4A90D9"))
        c.rect(_MARGIN + 70, ry + 3, bar_w, row_h - 6, fill=1, stroke=0)

        # count
        c.setFont(_EN, 8)
        c.setFillColor(colors.HexColor("#555555"))
        c.drawString(_MARGIN + 70 + bar_w + 4, ry + 5, str(count))

    return y - len(top) * row_h


def _draw_recent_sessions(c: rl_canvas.Canvas, stats: dict[str, Any], y: float) -> float:
    """Draw recent practice sessions table."""
    sessions: list[dict[str, Any]] = stats.get("recent_sessions", [])
    if not sessions:
        return y

    section(c, "最近練習紀錄", y)
    y -= 18

    # header
    row_h = 18.0
    cols = [(_MARGIN, "時間"), (_MARGIN + 130, "和弦"), (_MARGIN + 340, "時長"), (_MARGIN + 420, "速度")]
    c.setFillColor(colors.HexColor("#E8F0FE"))
    c.rect(_MARGIN, y - row_h, _CONTENT_W, row_h, fill=1, stroke=0)
    c.setFont(_ZH, 9)
    c.setFillColor(colors.HexColor("#333333"))
    for x, label in cols:
        c.drawString(x + 4, y - row_h + 5, label)
    y -= row_h

    for i, s in enumerate(sessions):
        ry = y - (i + 1) * row_h
        if i % 2 == 0:
            c.setFillColor(colors.HexColor("#FAFAFA"))
            c.rect(_MARGIN, ry, _CONTENT_W, row_h, fill=1, stroke=0)

        c.setFont(_EN, 8)
        c.setFillColor(colors.HexColor("#333333"))
        # time
        try:
            dt = datetime.fromisoformat(s["created_at"])
            time_str = dt.strftime("%m/%d %H:%M")
        except (KeyError, ValueError):
            time_str = "?"
        c.drawString(_MARGIN + 4, ry + 4, time_str)

        # chords
        c.setFont(_ZH, 8)
        c.setFillColor(colors.HexColor("#555555"))
        chords = s.get("chords_practiced", "")[:25]
        c.drawString(_MARGIN + 134, ry + 4, chords)

        # duration
        dur = s.get("duration_seconds", 0)
        c.drawString(_MARGIN + 344, ry + 4, f"{dur // 60}m{dur % 60}s")

        # speed
        c.drawString(_MARGIN + 424, ry + 4, f"{s.get('speed_pct', 100)}%")

    return y - len(sessions) * row_h


def _draw_recommendations(c: rl_canvas.Canvas, stats: dict[str, Any], y: float) -> float:
    """Draw practice recommendations based on stats."""
    section(c, "下一步建議", y)
    y -= 18

    tips: list[str] = []
    total_sessions = stats.get("total_sessions", 0)
    streak = stats.get("streak_days", 0)
    chord_counts: dict[str, int] = stats.get("chord_counts", {})

    if total_sessions == 0:
        tips.append("開始第一次練習吧！每天 15 分鐘就能看到進步。")
    else:
        if streak >= 3:
            tips.append(f"太棒了！已連續練習 {streak} 天，保持下去！")
        elif streak == 0:
            tips.append("今天還沒有練習紀錄，花 15 分鐘彈一下吧！")

        # find weak chords (least practiced)
        if chord_counts:
            sorted_chords = sorted(chord_counts.items(), key=lambda kv: kv[1])
            weak = [ch for ch, _ in sorted_chords[:2]]
            if weak:
                tips.append(f"加強練習：{'、'.join(weak)}（練習次數較少的和弦）")

        if total_sessions >= 10:
            tips.append("已累積 10+ 次練習，試試提高速度挑戰自己！")

    if not tips:
        tips.append("持續練習，每天進步一點點！")

    c.setFont(_ZH, 10)
    c.setFillColor(colors.HexColor("#333333"))
    for i, tip in enumerate(tips[:4]):
        c.drawString(_MARGIN + 8, y - (i * 18), f"• {tip[:50]}")

    return y - len(tips[:4]) * 18
