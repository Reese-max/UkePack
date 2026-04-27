---
id: chord-diagram
title: Ukulele Chord Diagram Contract
status: accepted
created: 2026-04-27
description: Define the SVG chord-diagram output used by PDF rendering for beginner ukulele shapes.
---

## Summary

`app.render.chord_diagram.generate_svg(chord_name: str) -> str` is the canonical
Phase 0 chord-chart generator for GCEA ukulele. It renders a compact SVG
diagram for known chords, a dedicated placeholder for `N.C.`, and a labeled
fallback card for unknown symbols.

## Contract

### Supported chord inventory

Known fingerings are stored as `(G, C, E, A)` fret tuples for:

`C`, `G`, `Am`, `F`, `G7`, `Dm`, `D`, `A`, `A7`, `D7`, `E7`, `Em`, `Bb`, `B`,
`Bm`, `E`, `Eb`, `Ab`, and `Bbm`.

`get_fingering(chord_name: str)` returns that tuple for known chords, otherwise
`None`.

### SVG output rules

1. Standard diagrams render at `80x115` with an SVG `viewBox`.
2. The chord name appears centered at the top.
3. The grid contains four vertical string lines and five horizontal fret lines
   (nut plus four frets).
4. String labels are always shown in `G C E A` order below the grid.
5. Open strings render as white circles above the nut.
6. Fretted strings render as filled black dots in the middle of the target fret.

### High-position chord handling

1. If every fretted note is within the first four frets, display the fingering
   directly and use a thick nut line.
2. If any fret is above 4, shift the visible diagram so the minimum non-zero
   fret becomes display fret 1.
3. Shifted diagrams show a thin nut line and a text position indicator
   `<start_fret>fr`.

### Special cases

1. `N.C.` returns a boxed placeholder SVG labeled `N.C.`.
2. Unknown chord names return a boxed fallback SVG containing the chord name and
   the text `no chart`.
3. Chord names are HTML-escaped before being embedded into SVG text nodes.

## Acceptance Signals

1. Known chords return SVG markup and preserve the requested chord label.
2. Open-string chords like `Am` show white open-circle markers.
3. Fretted chords like `C` show filled black dots.
4. Higher-position chords like `Ab` show a fret-position indicator.
5. Unknown chords keep returning a safe fallback SVG instead of failing.

## Out of Scope

1. Finger-number annotations.
2. Left-handed or mirrored diagrams.
3. Large-format child mode or alternate tunings.

## References

1. `PRD.md` section 9.9
2. `app/render/chord_diagram.py`
3. `tests/test_pdf_render.py`
