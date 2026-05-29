"""Shared drawing constants, helpers, and the SVG chord-box renderer."""

from __future__ import annotations

import contextlib
import tempfile
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas

from app.models.pack_request import PackRequest
from app.models.score import Score
from app.render.chord_diagram import generate_svg

try:
    from svglib.svglib import svg2rlg

    _HAS_SVGLIB = True
except ImportError:  # pragma: no cover
    _HAS_SVGLIB = False

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

# Level-tailored practice sequence shown on page 4 (U4-a: complete Level 2/3 PDFs).
_LEVEL_PRACTICE_STEPS: dict[int, list[str]] = {
    1: [
        "1. 先認識今日和弦，手指放對位置",
        "2. 空刷（不壓弦）習慣拍子",
        "3. 單小節慢慢換和弦",
        "4. 跟最慢速度彈出第一段",
    ],
    2: [
        "1. 複習和弦，確認換弦乾淨",
        "2. 配合節拍器固定刷法節奏",
        "3. 分段練習主歌與副歌",
        "4. 用 70% 速度完整彈一遍",
    ],
    3: [
        "1. 暖身：原速刷完整首和弦",
        "2. 挑戰副歌 TAB 或加花",
        "3. 原速完整演奏一遍",
        "4. 錄音自我檢視，找可改進處",
    ],
}


# ── typography helpers ─────────────────────────────────────────────────────


def page_title(c: rl_canvas.Canvas, title: str, y: float) -> None:
    """Draw a bold page title with an underline rule."""
    c.setFont(_ZH, 20)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(_MARGIN, y - 28, title)
    c.setStrokeColor(colors.HexColor("#333333"))
    c.setLineWidth(2)
    c.line(_MARGIN, y - 34, _PAGE_W - _MARGIN, y - 34)
    c.setLineWidth(1)


def section(c: rl_canvas.Canvas, title: str, y: float, underline: bool = True) -> None:
    """Draw a section heading, optionally with a light underline."""
    c.setFont(_ZH, 13)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawString(_MARGIN, y, title)
    if underline:
        c.setStrokeColor(colors.HexColor("#CCCCCC"))
        c.line(_MARGIN, y - 3, _PAGE_W - _MARGIN, y - 3)


def divider(c: rl_canvas.Canvas, y: float) -> None:
    """Draw a light horizontal rule."""
    c.setStrokeColor(colors.HexColor("#CCCCCC"))
    c.line(_MARGIN, y, _PAGE_W - _MARGIN, y)


def footer(c: rl_canvas.Canvas, req: PackRequest, page_num: int) -> None:
    """Draw page footer with license label and page number (PRD §15.2)."""
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


# ── chord diagram helpers ─────────────────────────────────────────────────


def chord_box(
    c: rl_canvas.Canvas, chord_sym: str, x: float, y: float, w: float, h: float
) -> None:
    """Embed one SVG chord diagram into the canvas at bottom-left (x, y)."""
    if not _HAS_SVGLIB:
        c.setFont(_EN_B, 12)
        c.setFillColor(colors.black)
        c.drawCentredString(x + w / 2, y + h / 2, chord_sym)
        c.setStrokeColor(colors.HexColor("#AAAAAA"))
        c.rect(x, y, w, h)
        return

    svg_str = generate_svg(chord_sym)
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
        c.drawCentredString(x + w / 2, y + h / 2, chord_sym)
        return

    scale = min(w / drawing.width, h / drawing.height)
    drawing.width = drawing.width * scale
    drawing.height = drawing.height * scale
    drawing.transform = (scale, 0, 0, scale, 0, 0)
    renderPDF.draw(drawing, c, x, y)


def chord_grid(
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
    col_step = dw + 8.0

    for i, ch in enumerate(chords[:8]):
        col = i % cols
        row = i // cols
        dx = x0 + col * col_step
        dy = y0 - (row + 1) * dh
        chord_box(c, ch, dx, dy, dw, dh)

    used_rows = max(1, (min(len(chords), 8) + cols - 1) // cols)
    return y0 - used_rows * dh


# ── practice table ────────────────────────────────────────────────────────


def practice_table(c: rl_canvas.Canvas, y: float) -> None:
    """Draw the 7-day practice plan grid."""
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


def unique_chords(score: Score) -> list[str]:
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
