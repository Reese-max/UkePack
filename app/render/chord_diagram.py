"""SVG chord diagram generator for GCEA ukulele (PRD §9.9)."""

from __future__ import annotations

import html as _html
import json as _json
import re as _re

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

_CHORD_FINGERS: dict[str, tuple[int, int, int, int]] = {
    "C":   (0, 0, 0, 3),
    "G":   (0, 1, 3, 2),
    "Am":  (2, 0, 0, 0),
    "F":   (2, 0, 1, 0),
    "G7":  (0, 2, 1, 3),
    "Dm":  (2, 3, 1, 0),
    "D":   (1, 2, 3, 0),
    "A":   (2, 1, 0, 0),
    "A7":  (0, 1, 0, 0),
    "D7":  (1, 1, 1, 2),
    "E7":  (1, 2, 0, 3),
    "Em":  (0, 3, 2, 1),
    "Bb":  (3, 2, 1, 1),
    "B":   (3, 2, 1, 1),
    "Bm":  (3, 1, 1, 1),
    "E":   (3, 3, 3, 1),
    "Eb":  (0, 1, 2, 3),
    "Ab":  (3, 1, 2, 1),
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

_CUSTOM_CHORD_PATTERN = _re.compile(
    r"^([A-Za-z0-9#b/]+)(?:\(([^)]+)\)|\[([^\]]+)\])$"
)

def parse_custom_chord(
    chord_name: str,
) -> tuple[str, tuple[int, int, int, int], tuple[int, int, int, int] | None] | None:
    """Parse custom ukulele chord like 'Dadd9(2202)' or 'G(0232|0132)'.

    Returns (display_name, frets, fingers) or None if not custom.
    """
    match = _CUSTOM_CHORD_PATTERN.match(chord_name.strip())
    if not match:
        return None
    name = match.group(1)
    pattern = match.group(2) or match.group(3)
    if not pattern:
        return None

    parts = pattern.split("|")
    frets_str = parts[0].strip()
    fingers_str = parts[1].strip() if len(parts) > 1 else None

    frets = _parse_string_values(frets_str)
    if frets is None or len(frets) != 4:
        return None

    fingers = None
    if fingers_str:
        fingers = _parse_string_values(fingers_str)
        if fingers is None or len(fingers) != 4:
            fingers = None

    return name, tuple(frets), tuple(fingers) if fingers else None  # type: ignore[return-value]


def _parse_string_values(s: str) -> list[int] | None:
    if "," in s:
        parts = [p.strip() for p in s.split(",")]
    else:
        parts = list(s)

    if len(parts) != 4:
        return None

    values: list[int] = []
    for p in parts:
        if p.upper() in ("X", "P", "-1"):
            values.append(-1)
        else:
            try:
                values.append(int(p))
            except ValueError:
                return None
    return values



def generate_svg(
    chord_name: str,
    *,
    colorable: bool = False,
    left_handed: bool = False,
) -> str:
    """Return an SVG string for the named ukulele chord diagram.

    When ``colorable`` is True, fretted dots are drawn as white-filled outlines so
    a child can colour them in (U4-b kid-friendly variant).
    """
    if chord_name == "N.C.":
        return _nc_svg()

    custom = parse_custom_chord(chord_name)
    if custom is not None:
        display_name, fingering, fingers = custom
        if left_handed:
            fingering = fingering[::-1]
            if fingers is not None:
                fingers = fingers[::-1]
        start_fret, display = _compute_display(fingering)
        return _render_svg(
            display_name, display, start_fret, colorable, fingers, left_handed=left_handed
        )

    fingering = _CHORD_FINGERINGS.get(chord_name)
    if fingering is None:
        return _unknown_svg(chord_name)
    if left_handed:
        fingering = fingering[::-1]
    start_fret, display = _compute_display(fingering)
    fingers = _CHORD_FINGERS.get(chord_name)
    if left_handed and fingers is not None:
        fingers = fingers[::-1]
    return _render_svg(
        chord_name, display, start_fret, colorable, fingers, left_handed=left_handed
    )



def get_fingering(chord_name: str) -> tuple[int, int, int, int] | None:
    """Return (G, C, E, A) fret tuple for the chord, or None if unknown."""
    custom = parse_custom_chord(chord_name)
    if custom is not None:
        return custom[1]
    return _CHORD_FINGERINGS.get(chord_name)


def get_fingerings_json(chord_names: list[str]) -> str:
    """Return a JSON object mapping chord names to their fret tuples.

    Unknown chords are omitted.  Intended for embedding in an HTML page so
    client-side JavaScript can synthesise chord audio via Web Audio API.
    """
    data: dict[str, list[int]] = {}
    for name in chord_names:
        f = get_fingering(name)
        if f is not None:
            data[name] = list(f)
    return _json.dumps(data, separators=(",", ":"))


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
    shifted = [f - start + 1 if f > 0 else f for frets_idx, f in enumerate(frets)]
    return start, shifted


def _fret_dot_y(display_fret: int) -> float:
    return _NUT_Y + (display_fret - 0.5) * _FRET_SPACING


def _render_svg(
    name: str,
    display_frets: list[int],
    start_fret: int,
    colorable: bool = False,
    fingers: tuple[int, int, int, int] | None = None,
    *,
    left_handed: bool = False,
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
    _append_grid(p, start_fret, left_handed=left_handed)
    _append_dots(p, display_frets, colorable, fingers)
    p.append("</svg>")
    return "".join(p)


def _append_grid(p: list[str], start_fret: int, *, left_handed: bool = False) -> None:
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
    labels = _STRING_LABELS[::-1] if left_handed else _STRING_LABELS
    for sx, lbl in zip(_STRING_XS, labels, strict=True):
        p.append(
            f'<text x="{sx}" y="{bottom_y + 12}" text-anchor="middle" '
            f'font-family="Helvetica,Arial,sans-serif" font-size="7">'
            f"{lbl}</text>"
        )


def _append_dots(
    p: list[str],
    display_frets: list[int],
    colorable: bool = False,
    fingers: tuple[int, int, int, int] | None = None,
) -> None:
    for idx, (sx, fret) in enumerate(zip(_STRING_XS, display_frets, strict=False)):
        if fret < 0:
            open_cy = _NUT_Y - 9
            p.append(
                f'<text x="{sx}" y="{open_cy + 3}" text-anchor="middle" '
                f'font-family="Helvetica,Arial,sans-serif" font-size="10" '
                f'font-weight="bold" fill="black">×</text>'
            )
        elif fret == 0:
            open_cy = float(_NUT_Y - 9)
            p.append(
                f'<circle cx="{sx}" cy="{open_cy}" r="{_OPEN_R}" '
                f'fill="white" stroke="black" stroke-width="1.2"/>'
            )
        elif colorable:
            dot_cy = _fret_dot_y(fret)
            p.append(
                f'<circle cx="{sx}" cy="{dot_cy:.1f}" r="{_DOT_R}" '
                f'fill="white" stroke="black" stroke-width="1.2"/>'
            )
            if fingers is not None and idx < len(fingers):
                f_num = fingers[idx]
                if f_num > 0:
                    p.append(
                        f'<text x="{sx}" y="{dot_cy + 2.2:.1f}" text-anchor="middle" '
                        f'font-family="Helvetica,Arial,sans-serif" font-size="7" '
                        f'font-weight="bold" fill="#000000">{f_num}</text>'
                    )
        else:
            dot_cy = _fret_dot_y(fret)
            p.append(
                f'<circle cx="{sx}" cy="{dot_cy:.1f}" r="{_DOT_R}" fill="black"/>'
            )
            if fingers is not None and idx < len(fingers):
                f_num = fingers[idx]
                if f_num > 0:
                    p.append(
                        f'<text x="{sx}" y="{dot_cy + 2.2:.1f}" text-anchor="middle" '
                        f'font-family="Helvetica,Arial,sans-serif" font-size="7" '
                        f'font-weight="bold" fill="white">{f_num}</text>'
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
