"""PDF practice pack renderer for ukulele arrangements (PRD §9.12, §15.2)."""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas as rl_canvas

from app.models.pack_request import PackRequest
from app.models.score import ChordEvent, Score
from app.render.chord_diagram import generate_svg

try:
    from svglib.svglib import svg2rlg

    _HAS_SVGLIB = True
except ImportError:  # pragma: no cover
    _HAS_SVGLIB = False

pdfmetrics.registerFont(UnicodeCIDFont("MSung-Light"))

_PAGE_W, _PAGE_H = A4
_MARGIN = 40.0
_CONTENT_W = _PAGE_W - 2 * _MARGIN

_ZH = "MSung-Light"
_EN = "Helvetica"
_EN_B = "Helvetica-Bold"

# PRD §15.2 — footer label per source_type
_LICENSE_LABELS: dict[str, str] = {
    "self_created": "Created by user",
    "suno_free": "Non-commercial practice use",
    "suno_paid": "User-declared commercial rights",
    "public_domain": "Public domain declared by user",
    "licensed": "Licensed use declared by user",
    "private_research": "Private study only. Do not distribute.",
}

_LEVEL_GOALS: dict[int, list[str]] = {
    1: ["認識今日和弦", "慢速空刷節奏", "彈出第一段落"],
    2: ["練習刷法節奏", "配合節拍器完整彈一遍", "嘗試副歌"],
    3: ["挑戰副歌 TAB", "完整演奏一遍", "自我錄音檢視"],
}

def render_pdf(request: PackRequest) -> bytes:
    """Render a 4-page A4 practice pack PDF and return raw bytes."""
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)
    _page1(c, request)
    c.showPage()
    _page2(c, request)
    c.showPage()
    _page3(c, request)
    c.showPage()
    _page4(c, request)
    c.showPage()
    c.save()
    return buf.getvalue()


# ── page builders ─────────────────────────────────────────────────────────

def _page1(c: rl_canvas.Canvas, req: PackRequest) -> None:
    """P1 - 練習總覽."""
    y = _PAGE_H - _MARGIN

    # Large title
    c.setFont(_EN_B, 24)
    c.setFillColor(colors.HexColor("#111111"))
    c.drawString(_MARGIN, y - 30, req.title[:50])
    y -= 50

    # Info row
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

    _divider(c, y)
    y -= 18

    # Chord list
    _section(c, "今日使用和弦", y)
    y -= 22
    unique = _unique_chords(req.score)
    c.setFont(_ZH, 16)
    c.setFillColor(colors.black)
    c.drawString(_MARGIN, y, "  ".join(unique) if unique else "（無和弦資料）")
    y -= 34

    # Strum patterns
    if req.strum_patterns:
        _section(c, "建議刷法", y)
        y -= 22
        for sp in req.strum_patterns[:2]:
            c.setFont(_ZH, 12)
            c.setFillColor(colors.black)
            c.drawString(_MARGIN, y, f"{sp.name}：{sp.notation()}  —  {sp.description}")
            y -= 20
        y -= 8

    _divider(c, y)
    y -= 18

    # Playability label
    if req.playability:
        _section(c, "可彈性評估", y)
        y -= 22
        c.setFont(_ZH, 13)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(
            _MARGIN, y,
            f"{req.playability.playability_score} / 100  —  {req.playability.label}",
        )
        y -= 30

    # Today's goal box
    goals = _LEVEL_GOALS.get(req.level, _LEVEL_GOALS[1])
    box_h = float(18 + len(goals) * 22)
    c.setFillColor(colors.HexColor("#F8F5E6"))
    c.setStrokeColor(colors.HexColor("#BBBBBB"))
    c.roundRect(_MARGIN, y - box_h, _CONTENT_W, box_h, 6, fill=1, stroke=1)
    _section(c, "今日目標", y - 4, underline=False)
    gy = y - 24
    for goal in goals:
        c.setFont(_ZH, 13)
        c.setFillColor(colors.black)
        c.drawString(_MARGIN + 14, gy, f"\u2610  {goal}")
        gy -= 22

    _footer(c, req, 1)


def _page2(c: rl_canvas.Canvas, req: PackRequest) -> None:
    """P2 - 和弦指法圖."""
    y = _PAGE_H - _MARGIN
    _page_title(c, "和弦指法圖", y)
    y -= 44

    unique = _unique_chords(req.score)
    bottom = _chord_grid(c, unique, _MARGIN, y)

    strum_y = bottom - 30.0
    if req.strum_patterns and strum_y > _MARGIN + 80:
        _section(c, "刷法練習", strum_y)
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

    _footer(c, req, 2)


def _page3(c: rl_canvas.Canvas, req: PackRequest) -> None:
    """P3 - 歌曲練習."""
    y = _PAGE_H - _MARGIN
    _page_title(c, "歌曲練習", y)
    y -= 44

    if not req.score.chords:
        c.setFont(_ZH, 14)
        c.setFillColor(colors.HexColor("#888888"))
        c.drawString(_MARGIN, y - 20, "（無和弦資料）")
    else:
        _chord_progression(c, req.score.chords, y)

    _footer(c, req, 3)


def _page4(c: rl_canvas.Canvas, req: PackRequest) -> None:
    """P4 - 老師 / 家長備註."""
    y = _PAGE_H - _MARGIN
    _page_title(c, "老師 / 家長備註", y)
    y -= 44

    _section(c, "練習順序建議", y)
    y -= 22
    for step in [
        "1. 先認識和弦，手指放對位置",
        "2. 空刷節奏，習慣拍子",
        "3. 單小節換和弦練習",
        "4. 慢速配合節拍器",
        "5. 加入歌曲段落",
        "6. 完整演奏一遍",
    ]:
        c.setFont(_ZH, 12)
        c.setFillColor(colors.black)
        c.drawString(_MARGIN + 8, y, step)
        y -= 18
    y -= 10

    _section(c, "常見問題", y)
    y -= 22
    box_h = 70.0
    c.setFillColor(colors.HexColor("#FFF8DC"))
    c.setStrokeColor(colors.HexColor("#CCCCCC"))
    c.roundRect(_MARGIN, y - box_h, _CONTENT_W, box_h, 4, fill=1, stroke=1)
    ny = y - 16
    for note in [
        "・換和弦時先看下一個和弦",
        "・右手不要停，即使換和弦也保持節奏",
        "・速度慢才能彈正確，正確後再加快",
    ]:
        c.setFont(_ZH, 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(_MARGIN + 10, ny, note)
        ny -= 20
    y -= box_h + 16

    _section(c, "七日練習計畫", y)
    y -= 24
    _practice_table(c, y)

    _footer(c, req, 4)


# ── drawing helpers ────────────────────────────────────────────────────────

def _page_title(c: rl_canvas.Canvas, title: str, y: float) -> None:
    c.setFont(_ZH, 20)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(_MARGIN, y - 28, title)
    c.setStrokeColor(colors.HexColor("#333333"))
    c.setLineWidth(2)
    c.line(_MARGIN, y - 34, _PAGE_W - _MARGIN, y - 34)
    c.setLineWidth(1)


def _section(
    c: rl_canvas.Canvas, title: str, y: float, underline: bool = True
) -> None:
    c.setFont(_ZH, 13)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawString(_MARGIN, y, title)
    if underline:
        c.setStrokeColor(colors.HexColor("#CCCCCC"))
        c.line(_MARGIN, y - 3, _PAGE_W - _MARGIN, y - 3)


def _divider(c: rl_canvas.Canvas, y: float) -> None:
    c.setStrokeColor(colors.HexColor("#CCCCCC"))
    c.line(_MARGIN, y, _PAGE_W - _MARGIN, y)


def _footer(c: rl_canvas.Canvas, req: PackRequest, page_num: int) -> None:
    label = _LICENSE_LABELS.get(req.source_type, "")
    c.setFont(_EN, 8)
    c.setFillColor(colors.HexColor("#888888"))
    c.drawString(_MARGIN, _MARGIN - 14, f"UkePack AI  \u2022  {label}")
    c.drawRightString(_PAGE_W - _MARGIN, _MARGIN - 14, f"Page {page_num} / 4")
    c.setStrokeColor(colors.HexColor("#CCCCCC"))
    c.line(_MARGIN, _MARGIN, _PAGE_W - _MARGIN, _MARGIN)
    # PRD §15.2 / AGENTS.md §5: private_research must show warning
    if req.source_type == "private_research":
        c.setFont(_EN_B, 9)
        c.setFillColor(colors.HexColor("#CC0000"))
        c.drawCentredString(
            _PAGE_W / 2,
            _MARGIN - 14,
            "Private study only. Do not distribute.",
        )


def _chord_grid(
    c: rl_canvas.Canvas,
    chords: list[str],
    x0: float,
    y0: float,
) -> float:
    """Draw up to 8 chord diagrams in a 4-column grid.

    Returns the y coordinate of the bottom of the last row.
    """
    dw, dh = 115.0, 150.0
    cols = 4
    col_step = (dw + 8.0)

    for i, chord in enumerate(chords[:8]):
        col = i % cols
        row = i // cols
        dx = x0 + col * col_step
        dy = y0 - (row + 1) * dh
        _chord_box(c, chord, dx, dy, dw, dh)

    used_rows = max(1, (min(len(chords), 8) + cols - 1) // cols)
    return y0 - used_rows * dh


def _chord_box(
    c: rl_canvas.Canvas, chord: str, x: float, y: float, w: float, h: float
) -> None:
    """Embed one SVG chord diagram into the canvas at bottom-left (x, y)."""
    if not _HAS_SVGLIB:
        c.setFont(_EN_B, 12)
        c.setFillColor(colors.black)
        c.drawCentredString(x + w / 2, y + h / 2, chord)
        c.setStrokeColor(colors.HexColor("#AAAAAA"))
        c.rect(x, y, w, h)
        return

    import contextlib

    svg_str = generate_svg(chord)
    drawing = None
    with contextlib.suppress(Exception):
        with tempfile.NamedTemporaryFile(
            suffix=".svg", delete=False, mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write(svg_str)
            tmp_path = Path(tmp.name)
        drawing = svg2rlg(str(tmp_path))
        tmp_path.unlink(missing_ok=True)

    if drawing is None or drawing.width == 0 or drawing.height == 0:
        c.setFont(_EN_B, 12)
        c.drawCentredString(x + w / 2, y + h / 2, chord)
        return

    scale = min(w / drawing.width, h / drawing.height)
    drawing.width = drawing.width * scale
    drawing.height = drawing.height * scale
    drawing.transform = (scale, 0, 0, scale, 0, 0)
    renderPDF.draw(drawing, c, x, y)


def _chord_progression(
    c: rl_canvas.Canvas, chords: list[ChordEvent], y_start: float
) -> None:
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
        c.setFont(_EN, 8)
        c.setFillColor(colors.HexColor("#888888"))
        c.drawString(x + 4, cy - 13, f"m{m}")
        syms = by_measure[m]
        c.setFont(_EN_B, 16)
        c.setFillColor(colors.black)
        c.drawString(x + 4, cy - 37, " / ".join(syms[:4]))


def _practice_table(c: rl_canvas.Canvas, y: float) -> None:
    days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
    tasks_zh = ["和弦練習", "節奏練習", "段落完成"]
    col_w = _CONTENT_W / len(days)
    row_h = 30.0

    for j, day in enumerate(days):
        x = _MARGIN + j * col_w
        c.setFillColor(colors.HexColor("#EEEEEE"))
        c.setStrokeColor(colors.HexColor("#AAAAAA"))
        c.rect(x, y - row_h, col_w, row_h, fill=1, stroke=1)
        c.setFont(_EN, 9)
        c.setFillColor(colors.black)
        c.drawCentredString(x + col_w / 2, y - row_h + 9, day)

    for i, task in enumerate(tasks_zh):
        ry = y - row_h * (i + 2)
        for j in range(len(days)):
            x = _MARGIN + j * col_w
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.HexColor("#CCCCCC"))
            c.rect(x, ry, col_w, row_h, fill=1, stroke=1)
        c.setFont(_ZH, 9)
        c.setFillColor(colors.HexColor("#555555"))
        c.drawString(_MARGIN + 3, ry + row_h / 2 - 5, f"{task} \u25a1")


# ── utilities ─────────────────────────────────────────────────────────────

def _unique_chords(score: Score) -> list[str]:
    """Return simplified unique chord list in first-seen order."""
    from app.arrangement.chord_simplify import simplify

    seen: set[str] = set()
    result: list[str] = []
    for ce in score.chords:
        try:
            sym = simplify(ce.symbol)
        except ValueError:
            sym = ce.symbol
        if sym != "N.C." and sym not in seen:
            seen.add(sym)
            result.append(sym)
    return result
