---
id: pdf-render
title: Practice Pack PDF Render Contract
status: accepted
created: 2026-04-27
description: Define the 4-page A4 practice-pack PDF output, footer rules, and chord/strum rendering behavior.
---

## Summary

`app.render.pdf.render_pdf(request: PackRequest) -> bytes` is the canonical
Phase 0 PDF renderer. It returns a four-page A4 practice pack built from parsed
score data, arrangement metadata, and source-type licensing labels.

## Contract

### Input model

The renderer consumes `app.models.pack_request.PackRequest` with these relevant
fields:

| Field | Contract |
| --- | --- |
| `title` | Display title on page 1. |
| `source_type` | Chooses footer licensing text. |
| `level` | Chooses the goals box on page 1. |
| `score` | Provides title, key, BPM, chords, and measures. |
| `key_recommendation` | Optional target key shown on page 1. |
| `strum_patterns` | Optional strum suggestions shown on pages 1 and 2. |
| `playability` | Optional playability score and label shown on page 1. |

### Output shape

1. Always return raw PDF bytes.
2. The PDF always contains four A4 pages in this order:
   1. `練習總覽`
   2. `和弦指法圖`
   3. `歌曲練習`
   4. `老師 / 家長備註`
3. The footer always shows `UkePack AI`, the source-type label, and `Page N / 4`.

### Footer licensing labels

`source_type` maps to these footer labels:

| `source_type` | Footer text |
| --- | --- |
| `self_created` | `Created by user` |
| `suno_free` | `Non-commercial practice use` |
| `suno_paid` | `User-declared commercial rights` |
| `public_domain` | `Public domain declared by user` |
| `licensed` | `Licensed use declared by user` |
| `private_research` | `Private study only. Do not distribute.` |

When `source_type == "private_research"`, the footer also draws the warning
`Private study only. Do not distribute.` in red, centered on the page.

### Page content rules

#### Page 1 — 練習總覽

1. Show title, level, chosen key (recommended key first, otherwise score key),
   BPM when available, and playability score when available.
2. Show unique simplified chords in first-seen order, excluding `N.C.`.
3. Show up to two suggested strum patterns.
4. Show playability label when available.
5. Show a level-specific goals box with exactly three checklist items.

#### Page 2 — 和弦指法圖

1. Show up to eight unique simplified chords in a four-column grid.
2. Each grid cell tries to embed the SVG diagram from
   `app.render.chord_diagram.generate_svg`.
3. If `svglib` is unavailable or SVG conversion fails, fall back to a text box
   containing only the chord name.
4. If strum patterns are present and there is room, show up to three patterns
   with notation and description.

#### Page 3 — 歌曲練習

1. If there are no chord events, show `（無和弦資料）`.
2. If `score.sections` exists, draw a compact `段落地圖` summary above the
   measure grid with section label, measure span, and manual/detected source.
3. Otherwise group chord symbols by measure number.
4. Render up to 24 measures in a four-column grid.
5. Each measure cell shows the measure label and up to four chord symbols joined
    by ` / `.

#### Page 4 — 老師 / 家長備註

1. Show the fixed six-step practice-order list.
2. Show the fixed common-mistakes note box.
3. Show the fixed seven-day practice table with rows `和弦練習`, `節奏練習`,
   and `段落完成`.

## Acceptance Signals

1. Regression tests verify the renderer returns PDF bytes with a `%PDF` header.
2. All six `source_type` values render valid PDFs.
3. Real MusicXML fixtures can flow through parse -> classify -> strum -> render
   without PDF generation failing.
4. The renderer keeps PRD 15.2 footer labels, including the private-research
   warning.

## Out of Scope

1. Editable annotations inside the PDF.
2. Lyric layout or chorus TAB engraving.
3. Streaming or incremental PDF generation.

## References

1. `PRD.md` sections 9.12, 15.2, and 16.2
2. `app/models/pack_request.py`
3. `app/render/pdf.py`
4. `tests/test_pdf_render.py`
