"""PDF practice pack renderer — dispatcher (PRD §9.12, §15.2).

The rendering logic lives in app/render/pages/ and app/render/_layout.py.
This module's public API (render_pdf) is unchanged.
"""

from __future__ import annotations

import io

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas as rl_canvas

from app.models.pack_request import PackRequest
from app.render.pages.page1 import render_page1
from app.render.pages.page2 import render_page2
from app.render.pages.page3 import render_page3
from app.render.pages.page4 import render_page4

pdfmetrics.registerFont(UnicodeCIDFont("MSung-Light"))


def render_pdf(request: PackRequest) -> bytes:
    """Render a 4-page A4 practice pack PDF and return raw bytes."""
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)
    render_page1(c, request)
    c.showPage()
    render_page2(c, request)
    c.showPage()
    render_page3(c, request)
    c.showPage()
    render_page4(c, request)
    c.showPage()
    c.save()
    return buf.getvalue()
