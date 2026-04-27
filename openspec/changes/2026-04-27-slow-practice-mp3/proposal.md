---
id: 2026-04-27-slow-practice-mp3
title: Slow Practice Audio Export
status: accepted
created: 2026-04-27
description: Define the spec-first Beta contract for exporting local slow-practice MIDI and MP3 assets from uploaded project MIDI.
---

## Problem

- PRD section 9.11 and Beta scope promise practice audio at 50% / 70% / 100% speed with click support and a one-bar count-in, but the repo currently stops at `POST /api/projects/{id}/midi`.
- `Project` rows store `midi_path`, yet there is no agreed contract for derived audio assets, metadata, filenames, or download routes.
- `openspec/changes/` has never been used for a real change-first workflow, so P2-02 risks becoming another code-first feature with the spec written after the fact.
- `mido` can generate tempo-shifted MIDI, but it cannot emit MP3 on its own. The implementation must make the local transcoding step explicit before code lands.

## Proposed Change

1. Treat P2-02 as a local-only export pipeline rooted in the uploaded project MIDI (`Project.midi_path`).
2. Add a practice-audio service inside the existing locked app structure, likely `app/core/practice_audio.py`, that:
   - validates a project has an uploaded MIDI file;
   - generates three deterministic practice variants for 50% / 70% / 100% speed;
   - prepends a one-bar count-in click track;
   - keeps an optional click-enabled render for guided practice;
   - writes canonical `.mid` artifacts first, then transcodes matching `.mp3` artifacts.
3. Extend the projects export surface with a dedicated practice-audio contract that returns artifact metadata and allows downloading generated `.mid` / `.mp3` files per speed variant.
4. Persist per-project audio artifact metadata so the UI can render download actions without regenerating assets blindly on every page load.
5. Keep naming deterministic and close to PRD section 11.3, using one shared stem per variant for both formats:
   - `{title}_practice_50bpm.mid` and `.mp3`
   - `{title}_practice_70percent.mid` and `.mp3`
   - `{title}_practice_fullspeed.mid` and `.mp3`
6. Keep the first implementation intentionally narrow: tempo scaling, click/count-in, export metadata, API wiring, and regression coverage. No waveform editor, no sharing flow, no teacher annotations.

## Impact

### Product / UX

- Analysis and preview surfaces will gain explicit practice-audio actions once a project has MIDI data.
- Projects without MIDI must fail fast with a clear 422-style response instead of silently hiding audio features.

### Code

- Likely touched areas:
  - `app/models/project.py` for audio artifact metadata;
  - `app/api/projects/export.py` or a sibling route module for generation/download endpoints;
  - `app/core/` for MIDI tempo scaling, click-track injection, and artifact naming;
  - `tests/` for service-level and API-level regression coverage.

### Dependency / Runtime

- The MP3 step needs an explicit local transcoder plan because `mido` alone is insufficient.
- If a new dependency or binary bridge is approved, it must be added in the same implementation PR together with docs and tests.
- If local MP3 transcoding cannot be provisioned safely, MIDI export can still be the canonical intermediate artifact, but P2-02 must remain open until MP3 is satisfied.

### Performance / Operations

- PRD section 16.1 sets the audio export target to under 60 seconds per song.
- Generated artifacts should live under the existing project data directory so cleanup and export behavior stay aligned with current PDF / MusicXML storage rules.

## Out of Scope

1. Source separation, vocal removal, or backing-track remixing.
2. Streaming audio previews in the browser before the file is generated.
3. Waveform editing, loop-region authoring, or teacher review annotations.
4. External APIs or cloud audio rendering services.

## References

1. `PRD.md` sections 7.2, 9.11, 11.3, 12.2, and 16.1
2. `program.md` item 37d
3. `app/models/project.py`
4. `app/api/projects/import_.py`
