---
id: 2026-04-28-discord-bot-initial
title: Discord Bot Initial PDF Export
status: accepted
created: 2026-04-28
description: Add the first Discord slash-command surface so users can upload MusicXML and receive a practice-pack PDF without opening the web UI.
---

## Problem

- PRD scene 3 and BACKLOG `P2-05` promise a Discord bot, but the product still requires the user to switch to the web UI or local CLI.
- The current pipeline already supports transient MusicXML → PDF generation, yet there is no bot-facing contract for attachment validation, license confirmation, or Discord response formatting.
- Beta sharing flow now exists (`P2-04`), so Discord is the next shortest path to the Mission KPI: reduce the time from "I have a score file" to "I can start practicing."

## Proposed Change

1. Add a thin Discord bot entrypoint that reuses the existing MusicXML parse, analysis, and PDF rendering pipeline instead of creating a Discord-only arrangement path.
2. Expose one slash command, `/ukepack`, that accepts:
   - one MusicXML / XML / MXL attachment;
   - `source_type` for the required footer label;
   - `confirm_license` as an explicit legal gate;
   - `level` (`1`–`3`);
   - optional title override.
3. Keep the first version transient and local-only:
   - no database persistence;
   - no share-link generation;
   - no MIDI / practice-audio flow;
   - no public channel spam by default.
4. Make the bot return the rendered PDF plus a compact summary of key, BPM, and level so the Discord path stays useful even without a full interactive review UI.

## Impact

### Product / UX

- Users who already work inside Discord can go from uploaded score to PDF in one slash command.
- The license gate remains explicit instead of letting the bot bypass the PDF compliance rules already enforced elsewhere.

### Code

- Add a bot entrypoint module plus a reusable transient helper under `app/core/`.
- Reuse the shared `PackRequest` pipeline so CLI, API, and Discord stay behaviorally aligned.
- Add regression tests for validation and PDF generation.

### Dependency / Runtime

- Requires `discord.py` in the project environment.
- Needs `DISCORD_BOT_TOKEN`; `DISCORD_BOT_GUILD_ID` is optional for faster guild-scoped sync during development.

## Out of Scope

1. Klangio conversion inside Discord.
2. Multi-step Discord components for key switching or review-mode editing.
3. Persisting Discord jobs or storing uploaded files beyond the transient render step.
4. Sending practice audio, share links, or teacher-review artifacts from the first bot version.

## References

1. `PRD.md` sections 6 (scene 3), 7.2, and 14
2. `BACKLOG.md` item `P2-05`
3. `app/demo.py`
4. `app/render/pdf.py`
