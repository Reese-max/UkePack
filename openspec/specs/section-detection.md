---
id: section-detection
title: Intro Verse Chorus Detection Contract
status: accepted
created: 2026-04-27
description: Detect reusable Intro / Verse / Chorus spans from score chord data and manual chord-sheet headers.
---

## Summary

`app.arrangement.section_detector.detect_sections(score: Score) -> list[ScoreSection]`
is the canonical automatic section detector. It labels score spans as `intro`,
`verse`, or `chorus` so the API, HTMX analysis page, and PDF page 3 can show a
compact section map.

## Contract

### Input sources

1. Imported MusicXML flows through `app.core.musicxml.parse`, which must attach
   detected sections to `Score.sections`.
2. Manual chord input flows through `app.core.chord_sheet.parse_chord_sheet`,
   which preserves explicit headers like `Verse:` / `Chorus:` and only falls
   back to auto-detection when no headers are present.

### Output model

Each section entry is an `app.models.score.ScoreSection` with:

| Field | Contract |
| --- | --- |
| `section` | `intro`, `verse`, or `chorus` |
| `start_measure` | Inclusive 1-based start bar |
| `end_measure` | Inclusive 1-based end bar |
| `source` | `manual` for preserved chord-sheet headers, otherwise `detected` |

### Detection rules

1. Build per-measure chord signatures from `Score.chords`.
2. Search repeated phrases between 2 and 8 measures.
3. Choose the strongest non-overlapping repeated phrase as `chorus`.
4. Label leading unmatched spans of 1-2 measures as `intro`.
5. Label remaining unmatched spans as `verse`.
6. If no repeated phrase exists, return a single `verse` span for the whole
   score, except a 1-2 measure score which returns a single `intro`.

### Manual header rules

1. Supported explicit labels: `Intro`, `Verse`, `Chorus`, `Hook`, `前奏`,
   `主歌`, `副歌`.
2. Unknown headers degrade to `verse`.
3. Section headers define measure ranges; they are not discarded.

## Acceptance Signals

1. Section-detector tests cover repeated-phrase chorus detection and fallback
   verse-only labeling.
2. Manual chord-sheet parsing preserves `Verse:` / `Chorus:` ranges as
   `source="manual"`.
3. MusicXML parse regression tests show repeated chord structure producing
   `intro -> chorus -> verse -> chorus`.
4. API analysis, HTMX analysis page, and PDF page 3 all consume serialized
   `Score.sections`.

## Out of Scope

1. Distinguishing bridge, pre-chorus, outro, or chorus hook as separate labels.
2. Lyric-aware section detection.
3. Melody-only section inference when chord data is absent.

## References

1. `PRD.md` sections 7.2, 8.1, 9.4, and 13.2
2. `app/arrangement/section_detector.py`
3. `app/core/chord_sheet.py`
4. `tests/test_section_detector.py`
