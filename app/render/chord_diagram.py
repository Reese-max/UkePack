"""SVG chord diagram generator for GCEA ukulele (PRD §9.9)."""

import html as _html

# (G_fret, C_fret, E_fret, A_fret) — string order left-to-right on diagram
# -1 would mean muted; all known beginner chords are open-or-fretted here
_CHORD_FINGERINGS: dict[str, tuple[int, int, int, int]] = {
    "C":   (0, 0, 0, 3),
    "G":   (0, 2, 3, 2),
    "Am":  (2, 0, 0, 0),
    "F":   (2, 0, 1, 0),
    "G7":  (0, 2, 1, 2),
    "Dm":  (2, 2, 1, 0),
    "D":   (2, 2, 2, 0),
    "A":   (2, 1, 0, 0),
    "A7":  (0, 1, 0, 0),
    "D7":  (2, 2, 2, 3),
    "E7":  (1, 2, 0, 2),
    "Em":  (0, 4, 3, 2),
    "Bb":  (3, 2, 1, 1),
    "B":   (4, 3, 2, 2),
    "Bm":  (4, 2, 2, 2),
    "E":   (4, 4, 4, 2),
    "Eb":  (0, 3, 3, 3),
    "Ab":  (5, 3, 4, 3),
    "Bbm": (3, 1, 2, 1),
}

_W = 80
_H = 115
_STRING_XS: tuple[int, int, int, int] = (12, 28, 44, 60)
_STRING_LABELS: tuple[str, str, str, str] = ("G", "C", "E", "A")
_NUT_Y = 30
_FRET_SPACING = 16
_FRET_LINES = 5   # nut + 4 fret lines
_DOT_R = 5
_OPEN_R = 4


def generate_svg(chord_name: str) -> str:
    """Return an SVG string for the named ukulele chord diagram."""
    if chord_name == "N.C.":
        return _nc_svg()
    fingering = _CHORD_FINGERINGS.get(chord_name)
    if fingering is None:
        return _unknown_svg(chord_name)
    start_fret, display = _compute_display(fingering)
    return _render_svg(chord_name, display, start_fret)


def get_fingering(chord_name: str) -> tuple[int, int, int, int] | None:
    """Return (G, C, E, A) fret tuple for the chord, or None if unknown."""
    return _CHORD_FINGERINGS.get(chord_name)


# ── private helpers ────────────────────────────────────────────────────────

def _compute_display(
    frets: tuple[int, int, int, int],
) -> tuple[int, list[int]]:
    """Return (start_fret, display_frets).

    When the highest fret > 4, shift so the minimum non-zero fret is
    at position 1 and add a numeric fret indicator.
    """
    non_zero = [f for f in frets if f > 0]
    if not non_zero or max(non_zero) <= 4:
        return 1, list(frets)
    start = min(non_zero)
    shifted = [f - start + 1 if f > 0 else 0 for f in frets]
    return start, shifted


def _fret_dot_y(display_fret: int) -> float:
    return _NUT_Y + (display_fret - 0.5) * _FRET_SPACING


def _render_svg(
    name: str, display_frets: list[int], start_fret: int
) -> str:
    p: list[str] = []
    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {_W} {_H}" width="{_W}" height="{_H}">'
    )
    # chord name title
    safe = _html.escape(name)
    p.append(
        f'<text x="{_W // 2}" y="12" text-anchor="middle" '
        f'font-family="Helvetica,Arial,sans-serif" font-size="11" '
        f'font-weight="bold">{safe}</text>'
    )
    _append_grid(p, start_fret)
    _append_dots(p, display_frets)
    p.append("</svg>")
    return "".join(p)


def _append_grid(p: list[str], start_fret: int) -> None:
    x1, x2 = _STRING_XS[0], _STRING_XS[-1]
    bottom_y = _NUT_Y + (_FRET_LINES - 1) * _FRET_SPACING

    # vertical string lines
    for sx in _STRING_XS:
        p.append(
            f'<line x1="{sx}" y1="{_NUT_Y}" x2="{sx}" y2="{bottom_y}" '
            f'stroke="black" stroke-width="1"/>'
        )

    # nut (thick when starting from fret 1, thin otherwise)
    nut_w = 3 if start_fret == 1 else 1
    p.append(
        f'<line x1="{x1}" y1="{_NUT_Y}" x2="{x2}" y2="{_NUT_Y}" '
        f'stroke="black" stroke-width="{nut_w}"/>'
    )

    # fret lines
    for i in range(1, _FRET_LINES):
        fy = _NUT_Y + i * _FRET_SPACING
        p.append(
            f'<line x1="{x1}" y1="{fy}" x2="{x2}" y2="{fy}" '
            f'stroke="black" stroke-width="1"/>'
        )

    # position indicator for higher-up chords
    if start_fret > 1:
        ind_y = _NUT_Y + 5
        p.append(
            f'<text x="{x2 + 4}" y="{ind_y}" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="8">'
            f"{start_fret}fr</text>"
        )

    # string labels below diagram
    for sx, lbl in zip(_STRING_XS, _STRING_LABELS, strict=True):
        p.append(
            f'<text x="{sx}" y="{bottom_y + 12}" text-anchor="middle" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="7">'
            f"{lbl}</text>"
        )


def _append_dots(p: list[str], display_frets: list[int]) -> None:
    for sx, fret in zip(_STRING_XS, display_frets, strict=False):
        if fret == 0:
            open_cy: float = float(_NUT_Y - 9)
            p.append(
                f'<circle cx="{sx}" cy="{open_cy}" r="{_OPEN_R}" '
                f'fill="white" stroke="black" stroke-width="1.2"/>'
            )
        else:
            dot_cy = _fret_dot_y(fret)
            p.append(
                f'<circle cx="{sx}" cy="{dot_cy:.1f}" r="{_DOT_R}" fill="black"/>'
            )


def _nc_svg() -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {_W} {_H}" width="{_W}" height="{_H}">'
        f'<rect x="4" y="4" width="{_W-8}" height="{_H-8}" '
        f'fill="none" stroke="#ccc" stroke-width="1" rx="4"/>'
        f'<text x="{_W//2}" y="{_H//2+5}" text-anchor="middle" '
        f'font-family="Helvetica,Arial,sans-serif" font-size="13" '
        f'font-weight="bold">N.C.</text>'
        f"</svg>"
    )


def _unknown_svg(name: str) -> str:
    safe = _html.escape(name)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {_W} {_H}" width="{_W}" height="{_H}">'
        f'<rect x="4" y="4" width="{_W-8}" height="{_H-8}" '
        f'fill="none" stroke="#ccc" stroke-width="1" rx="4"/>'
        f'<text x="{_W//2}" y="20" text-anchor="middle" '
        f'font-family="Helvetica,Arial,sans-serif" font-size="11" '
        f'font-weight="bold">{safe}</text>'
        f'<text x="{_W//2}" y="{_H//2+5}" text-anchor="middle" '
        f'font-family="Helvetica,Arial,sans-serif" font-size="9" '
        f'fill="#888">no chart</text>'
        f"</svg>"
    )
