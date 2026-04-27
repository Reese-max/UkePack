---
id: musicxml-import
title: MusicXML Import Contract
status: accepted
created: 2026-04-27
description: Normalize supported MusicXML inputs into the Score payload consumed by arrangement flows.
---

## Summary

`app.core.musicxml.parse(path: Path) -> Score` is the canonical entry point for
MusicXML import in Phase 0. It converts `.musicxml`, `.xml`, and `.mxl` files
into a normalized `Score` model so downstream arrangement code can reason about
title, key, tempo, measures, chord symbols, and melody without touching
`music21` internals.

## Contract

### Inputs

1. The caller passes an existing local `Path`.
2. Accepted suffixes are `.musicxml`, `.xml`, and `.mxl`.
3. Any other suffix raises `ValueError("Unsupported score format: ...")`.
4. A missing file raises `FileNotFoundError`.

### Output model

The parser returns `app.models.score.Score` with these populated fields:

| Field | Contract |
| --- | --- |
| `title` | Prefer embedded metadata title or movement name; ignore `Music21 Fragment`; otherwise title-case the filename stem. |
| `key` | Prefer explicit `music21.key.Key`; then `KeySignature.asKey()`; otherwise use `parsed_score.analyze("key")`. Format is `<Tonic> <mode>`. |
| `bpm` | First numeric metronome mark, rounded to `int`; `None` if absent. |
| `time_signature` | First time signature found on the melody part; `None` if absent. |
| `measures` | Count of `Measure` objects on the melody part. |
| `chords` | Ordered list of `ChordEvent(symbol, measure, beat)` from `harmony.ChordSymbol` events across the score. |
| `melody` | Ordered list of `MelodyNote(pitch, measure, beat, quarter_length)` from the melody part. |

### Melody extraction rules

1. Use the first notated part when the score has parts; otherwise inspect the
   whole parsed score.
2. Keep `note.Note` events as-is.
3. Treat `chord.Chord` events as melody carriers and keep the highest pitch.
4. Never emit `harmony.ChordSymbol` objects into the melody list.
5. Preserve pickup measure `0`; coerce missing measure numbers to `0`.

### Security constraints

1. **Network-fetch blocking**: A `Path` argument whose string representation starts
   with `http://`, `https://`, `ftp://`, or `ftps://` raises `ValueError`
   immediately, before any filesystem or `music21` call.
2. **File-size cap**: Any file whose `stat().st_size` exceeds `MAX_IMPORT_BYTES`
   (10 MB) raises `ValueError` before parsing begins.
3. **Zip-bomb protection**: For `.mxl` inputs, every ZIP member's declared
   uncompressed `file_size` is checked against `_MAX_MXL_MEMBER_BYTES` (50 MB).
   Any member that exceeds this limit raises `ValueError` before decompression.
4. The URL-path check runs before `path.exists()` so a network-fetch cannot
   masquerade as a missing-file error.

### Empty or partial data

1. Missing tempo or time signature is valid and returns `None`.
2. Missing chord symbols is valid and returns `[]`; the caller is responsible
   for prompting manual chord entry or external preprocessing per PRD 9.2.
3. The parser does not mutate or overwrite the source file.

## Acceptance Signals

1. Public-domain fixture coverage stays green across all checked-in
   `tests/fixtures/*.musicxml` songs.
2. `.mxl` import, metadata fallback, and chord-melody extraction have dedicated
   regression tests.
3. Import behavior supports PRD 9.2 visibility needs: title, key, BPM,
   time signature, measures, chords, and melody are all available from one
   `Score` payload.

## Out of Scope

1. MIDI import.
2. Preserving raw source files for download or version replacement workflows.

## References

1. `PRD.md` sections 9.2 and 16.2
2. `app/core/musicxml.py`
3. `tests/test_musicxml_import.py`
