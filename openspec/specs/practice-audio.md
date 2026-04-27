---
id: practice-audio
title: Slow Practice Audio Contract
status: accepted
created: 2026-04-27
description: Generate deterministic slow-practice MIDI and MP3 assets from uploaded project MIDI files.
---

## Summary

`app.core.practice_audio` is the canonical Beta practice-audio pipeline. It takes an
uploaded project MIDI file, generates deterministic slowed MIDI variants with a
one-bar click-track count-in, renders matching MP3 files, and persists a
`manifest.json` so the API and HTMX pages can reuse existing artifacts.

## Contract

### Input requirements

1. Practice audio requires `Project.midi_path` to exist on disk under
   `DATA_DIR/projects/{id}/original.mid` or `.midi`.
2. Export routes must honor the existing `license_confirmed` gate before
   generating or downloading practice audio.
3. Projects without MIDI fail fast with a `422`-style error instead of silently
   hiding the feature.

### Generated variants

The first implementation always emits exactly three variants:

| Variant | Label | Tempo rule | Filenames |
| --- | --- | --- | --- |
| `50bpm` | `50 BPM` | fixed 50 BPM | `{title}_practice_50bpm.mid` / `.mp3` |
| `70percent` | `70%` | first detected BPM × 0.7 | `{title}_practice_70percent.mid` / `.mp3` |
| `fullspeed` | `100%` | first detected BPM × 1.0 | `{title}_practice_fullspeed.mid` / `.mp3` |

All artifacts live under `DATA_DIR/projects/{id}/practice_audio/`.

### MIDI generation rules

1. Generated MIDI prepends exactly one bar of count-in click track.
2. Count-in click uses the source time signature, defaulting to `4/4` when the
   MIDI omits it.
3. Tempo changes are scaled consistently from the first detected BPM so the song
   structure stays intact after slowing down.
4. The first musical note begins after the count-in bar; setup messages such as
   program changes may remain at time zero.

### MP3 generation rules

1. The service renders MIDI note events into a mono PCM waveform in-process.
2. Rendered WAV data is transcoded to MP3 via the local `ffmpeg` binary.
3. If `ffmpeg` is unavailable or encoding fails, the API surfaces a clear error
   instead of returning a partial success.

### Persistence contract

1. `manifest.json` is stored beside the generated files under the practice-audio
   directory.
2. The persisted manifest is an `app.models.practice_audio.PracticeAudioManifest`
   containing `source_midi_path`, `generated_at`, and three serialized
   `PracticeAudioArtifact` entries.
3. API and page rendering must read `manifest.json` instead of regenerating
   artifacts on every request.

### API and page surfaces

1. `POST /api/projects/{id}/practice-audio` generates the manifest and returns
   its serialized payload.
2. `GET /api/projects/{id}/practice-audio` returns the persisted manifest.
3. `GET /api/projects/{id}/export.practice-audio/{variant}.{format}` downloads a
   generated `.mid` or `.mp3` artifact.
4. `POST /projects/{id}/generate-practice-audio` triggers generation from the
   HTMX pages and redirects back to the analysis page.
5. `analysis.html` and `preview.html` show practice-audio actions when a project
   has uploaded MIDI data.

## Acceptance Signals

1. Practice-audio service tests assert all three variants, count-in note
   placement, manifest persistence, and non-empty MP3 output.
2. API tests cover license gating, missing-MIDI failure, manifest retrieval, and
   `.mid` / `.mp3` downloads.
3. Page tests cover MIDI-only analysis surfaces and preview/analysis actions for
   practice-audio generation.

## Out of Scope

1. Browser streaming preview before the export is generated.
2. Teacher review annotations inside audio artifacts.
3. Alternate soundfonts, waveform editing, or per-track mute/solo controls.

## References

1. `PRD.md` sections 9.11, 11.3, 12.2, and 16.1
2. `openspec/changes/2026-04-27-slow-practice-mp3/proposal.md`
3. `app/core/practice_audio.py`
4. `app/api/projects/export.py`
5. `tests/test_practice_audio.py`
