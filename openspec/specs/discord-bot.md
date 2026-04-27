# Spec: Discord Bot Initial PDF Export

**Status**: Accepted  
**Scope**: `app/discord_bot.py`, `app/core/discord_pack.py`, `app/core/practice_pack.py`  
**Implements**: BACKLOG P2-05

---

## 1. Overview

The Discord bot provides a transient slash-command path for the core UkePack flow:
upload one MusicXML-family file, choose a level, confirm license rights, and receive
one rendered practice-pack PDF back in Discord.

This first version is intentionally narrow. It does **not** persist a `Project` row,
does **not** expose review mode, and does **not** generate practice audio.

---

## 2. Slash Command Contract

### 2.1 Command

`/ukepack`

### 2.2 Inputs

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `score_file` | attachment | yes | `.musicxml` / `.xml` / `.mxl` only |
| `source_type` | string choice | yes | `self_created / suno_free / suno_paid / public_domain / licensed / private_research` |
| `confirm_license` | bool | yes | must be `true` before any PDF is returned |
| `level` | integer | no | default `1`, allowed `1`–`3` |
| `title` | string | no | optional PDF title override |

### 2.3 Validation Rules

1. Attachment size limit is the same 10 MB cap used by the web import flow.
2. Unsupported file extensions fail before parsing.
3. `confirm_license=false` blocks PDF export.
4. Parse errors surface an explicit failure message instead of returning an empty success.

---

## 3. Response Contract

On success, the bot replies with:

1. one PDF attachment
2. a compact summary message containing:
   - title
   - selected level
   - recommended level
   - original key
   - target key
   - BPM
   - chord count

The PDF must reuse the same render pipeline and footer rules as CLI/API output,
including:

1. source-type footer labels from PRD §15.2
2. `private_research` warning text: `Private study only. Do not distribute.`
3. Level-specific strum-pattern suggestions and chord diagrams

Bot responses are ephemeral so the initial Discord surface does not spray PDFs into
public channels by default.

---

## 4. Runtime Contract

1. The bot runs via `python -m app.discord_bot`.
2. `DISCORD_BOT_TOKEN` is required.
3. `DISCORD_BOT_GUILD_ID` is optional; when present, command sync is guild-scoped for faster development feedback.

---

## 5. Non-Persistence Rules

1. Uploaded files are handled transiently in a temporary directory.
2. No SQLite `Project` row is created.
3. No share-link, review, or practice-audio artifact is produced.

---

## 6. Acceptance Signals

1. Regression tests cover:
   - successful PDF generation from a real MusicXML fixture;
   - title override handling;
   - missing license confirmation rejection;
   - bad extension rejection;
   - oversized payload rejection.
2. `ruff`, `mypy`, and `pytest` remain green after adding the bot surface.

---

## 7. References

1. `PRD.md` sections 6, 7.2, and 14
2. `openspec/changes/2026-04-28-discord-bot-initial/proposal.md`
3. `tests/test_discord_pack.py`
