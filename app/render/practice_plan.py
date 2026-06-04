"""Song-specific 7-day practice plan for the PDF practice pack.

Replaces the generic 3x7 grid with a concrete daily plan that references
the song's actual chords, tempo, and sections — so a child knows exactly
what to practice each day.
"""

from __future__ import annotations

from dataclasses import dataclass

from reportlab.pdfgen import canvas as rl_canvas

from app.arrangement.tempo import tempo_ladder
from app.models.pack_request import PackRequest
from app.render._layout import _CONTENT_W, _MARGIN, _ZH, section


@dataclass(frozen=True)
class DayPlan:
    """One day's practice focus."""

    day: int
    goal: str
    detail: str


def build_plan(req: PackRequest) -> list[DayPlan]:
    """Build a 7-day practice plan tailored to the song and level."""
    chords = _unique_chords(req)
    chord_str = "、".join(chords[:4]) if chords else "歌曲和弦"
    extra = f"、{chords[4]}" if len(chords) > 4 else ""
    ladder = tempo_ladder(req.score.bpm)
    slow_bpm = ladder[0].bpm if ladder else 60
    mid_bpm = ladder[1].bpm if len(ladder) > 1 else int(slow_bpm * 1.4)
    sections = _section_names(req)

    if req.level == 1:
        return [
            DayPlan(1, "認識和弦", f"手指放對 {chord_str}{extra}，每個按 5 秒"),
            DayPlan(2, "空刷節奏", f"不壓弦，右手練習刷法，跟節拍器 ♩={slow_bpm}"),
            DayPlan(3, "慢速換和弦", f"{chord_str} 兩兩換，每拍換一次 ♩={slow_bpm}"),
            DayPlan(4, "跟著彈第一段", f"用慢速彈完整段，和弦對就好 ♩={slow_bpm}"),
            DayPlan(5, "加速練習", f"從慢速提到中速 ♩={mid_bpm}"),
            DayPlan(6, "完整彈一遍", f"中速完整彈，錯了繼續不要停 ♩={mid_bpm}"),
            DayPlan(7, "表演日！", f"彈給家人聽，原速 ♩={req.score.bpm or '原速'}"),
        ]
    if req.level == 2:
        sec_hint = sections[0] if sections else "主歌"
        sec_hint2 = sections[1] if len(sections) > 1 else "副歌"
        return [
            DayPlan(1, "暖身：複習和弦", f"確認 {chord_str} 換弦乾淨"),
            DayPlan(2, "刷法節奏", f"固定刷法配節拍器 ♩={slow_bpm}"),
            DayPlan(3, f"練{sec_hint}", f"{sec_hint} 段落慢速彈 ♩={slow_bpm}"),
            DayPlan(4, f"練{sec_hint2}", f"{sec_hint2} 段落慢速彈 ♩={slow_bpm}"),
            DayPlan(5, "合併段落", f"把段落接起來 ♩={mid_bpm}"),
            DayPlan(6, "70% 完整彈", f"用 70% 速度完整彈一遍 ♩={mid_bpm}"),
            DayPlan(7, "原速挑戰！", f"試試原速 ♩={req.score.bpm or '原速'}"),
        ]
    # Level 3
    sec_str = "→".join(sections[:3]) if sections else "前奏→主歌→副歌"
    return [
        DayPlan(1, "暖身：原速和弦", f"原速刷 {chord_str} 確認手感"),
        DayPlan(2, "刷法加花", f"練習進階刷法配節拍器 ♩={req.score.bpm or 100}"),
        DayPlan(3, "分段精練", f"依序練 {sec_str}"),
        DayPlan(4, "副歌 TAB", "挑戰副歌旋律或加花"),
        DayPlan(5, "完整慢速", f"完整彈一遍找弱點 ♩={mid_bpm}"),
        DayPlan(6, "完整原速", f"原速彈 ♩={req.score.bpm or '原速'}"),
        DayPlan(7, "錄音檢視！", "錄下來聽，標記要改的地方"),
    ]


def draw_practice_plan(c: rl_canvas.Canvas, req: PackRequest, y: float) -> float:
    """Draw the 7-day practice plan on the PDF canvas.

    Returns the y coordinate after drawing.
    """
    from reportlab.lib import colors

    section(c, "七日練習計畫", y)
    y -= 20

    plans = build_plan(req)
    col_day = 45.0
    col_goal = 100.0
    row_h = 26.0

    # Header
    hx = _MARGIN
    c.setFillColor(colors.HexColor("#E8F0FE"))
    c.setStrokeColor(colors.HexColor("#AAAAAA"))
    c.rect(hx, y - row_h, _CONTENT_W, row_h, fill=1, stroke=1)
    c.setFont(_ZH, 9)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawString(hx + 4, y - row_h + 8, "天")
    c.drawString(hx + col_day + 4, y - row_h + 8, "今日目標")
    c.drawString(hx + col_day + col_goal + 4, y - row_h + 8, "具體做法")
    y -= row_h

    # Rows
    for plan in plans:
        bg = colors.HexColor("#FAFAFA") if plan.day % 2 == 0 else colors.white
        c.setFillColor(bg)
        c.setStrokeColor(colors.HexColor("#DDDDDD"))
        c.rect(_MARGIN, y - row_h, _CONTENT_W, row_h, fill=1, stroke=1)

        c.setFont(_ZH, 9)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(_MARGIN + 4, y - row_h + 8, f"Day {plan.day}")

        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(_MARGIN + col_day + 4, y - row_h + 8, plan.goal[:12])

        c.setFillColor(colors.HexColor("#555555"))
        detail_text = plan.detail[:38]
        c.drawString(_MARGIN + col_day + col_goal + 4, y - row_h + 8, detail_text)
        y -= row_h

    return y


def _unique_chords(req: PackRequest) -> list[str]:
    """Get unique simplified chords from the score."""
    from app.arrangement.chord_simplify import simplify

    seen: set[str] = set()
    result: list[str] = []
    for ce in req.score.chords:
        try:
            sym = simplify(ce.symbol)
        except ValueError:
            sym = ce.symbol
        if sym != "N.C." and sym not in seen:
            seen.add(sym)
            result.append(sym)
    return result


def _section_names(req: PackRequest) -> list[str]:
    """Get section names from the score."""
    return [s.section for s in req.score.sections if s.section]
