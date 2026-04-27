# Spec: Projects REST API

**Status**: Accepted  
**Scope**: `app/api/projects/*`  
**Implements**: FR-001 – FR-015 plus Beta practice-audio export, teacher review mode, and expiring private share links (BACKLOG P1-01 – P1-10, P2-02, P2-03, P2-04)

---

## 1. Overview

REST endpoints expose the UkePack pipeline over HTTP. All endpoints are prefixed `/api/projects` and tagged `projects`.

---

## 2. Endpoints

### 2.1 POST `/api/projects` — Create project (FR-001)

**Request body** (`ProjectCreate`):

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | `str` | yes | 1–200 chars |
| `source_type` | `str` | yes | enum: `self_created / suno_free / suno_paid / public_domain / licensed / private_research` |
| `usage_type` | `str` | no | default `"private"` |
| `learner_age` | `int \| null` | no | |

**Response** `201 Created` → `ProjectRead`:

| Field | Type | Notes |
|-------|------|-------|
| `id` | `int` | auto-assigned |
| `title` | `str` | |
| `source_type` | `str` | |
| `created_at` | `datetime` | UTC |
| `updated_at` | `datetime` | UTC |
| `license_confirmed` | `bool` | defaults `false` |

---

### 2.2 POST `/api/projects/{id}/import` — MusicXML upload (FR-002)

**Constraints**:
- Accepts `.musicxml` / `.xml` / `.mxl` only → `400` otherwise
- File size limit 10 MB enforced by streaming chunked read → `413` if exceeded
- `.mxl` zip-bomb protection: single entry ≤ 50 MB
- Network URL paths rejected → `400 "Not a local path"`

**Response** `200 OK`:

```json
{
  "project_id": 1,
  "key": "C major",
  "bpm": 120,
  "time_signature": "4/4",
  "measures": 32,
  "chord_count": 12,
  "recommended_level": 1,
  "playability_score": 72,
  "target_key": "C major"
}
```

**Error codes**:
- `400` — wrong extension
- `413` — file too large
- `422` — parse error (malformed MusicXML)
- `404` — project not found

---

### 2.3 POST `/api/projects/{id}/midi` — MIDI upload (FR-003)

Accepts `.mid` / `.midi` only → `400` otherwise. 10 MB streaming limit.  
Saves file and records `midi_path`; full MIDI parsing deferred to Phase 2.

**Response** `200 OK`:

```json
{ "project_id": 1, "midi_path": "projects/1/original.mid", "status": "saved" }
```

---

### 2.4 POST `/api/projects/{id}/chords` — Manual chord input (FR-004)

**Request body**: `{ "text": "C | G | Am | F" }`  
Pipe-delimited symbols, multi-line, and optional section headers such as
`Verse:` / `Chorus:`. Manual headers are normalized to intro / verse / chorus
and preserved in `Score.sections`.

**Response** `200 OK`:

```json
{ "project_id": 1, "chord_count": 4, "measures": 4, "section_count": 2 }
```

---

### 2.5 GET `/api/projects/{id}/analysis` — Key/BPM/chords/difficulty (FR-005)

Requires `score_json` or `chords_text` to be set → `422` otherwise.

**Response** `200 OK`:

Response includes:

1. Raw score metadata: `key`, `bpm`, `time_signature`, `measures`
2. Serialized chord events under `chords`
3. Serialized section spans under `sections`
4. Nested `key_recommendation`
5. Nested `playability` with `score`, `level`, and `label`

---

### 2.6 POST `/api/projects/{id}/arrange` — Generate arrangement (FR-006)

**Request body**: `{ "level": 1 }` (1 / 2 / 3)  
Runs `suggest_key → classify → suggest_for_level`, stores result in `arrangement_json`.

**Response** `200 OK`:

```json
{
  "project_id": 1,
  "level": 1,
  "strum_patterns": ["D DU UDU"],
  "target_key": "C major"
}
```

---

### 2.7 GET `/api/projects/{id}/export.pdf` — Download PDF (FR-007)

Requires `license_confirmed = true` → `403 "License not confirmed"` otherwise.  
Requires `score_json` or `chords_text` → `422` otherwise.  
Runs full pipeline, streams PDF bytes.

**Response**: `200 OK`, `Content-Type: application/pdf`, `Content-Disposition: attachment; filename="<title>.pdf"`

---

### 2.8 GET `/api/projects/{id}/export.musicxml` — Download edited MusicXML (FR-008)

Returns original uploaded MusicXML from disk.  
→ `404` if no MusicXML has been imported.

**Response**: `200 OK`, `Content-Type: application/xml`

---

### 2.9 POST `/api/projects/{id}/practice-audio` — Generate practice audio

Requires `license_confirmed = true` and `midi_path` to exist.  
Generates deterministic `50bpm`, `70percent`, and `fullspeed` practice variants,
each with matching `.mid` and `.mp3` files plus a persisted `manifest.json`.

**Response** `200 OK`:

```json
{
  "source_midi_path": "projects/1/original.mid",
  "generated_at": "2026-04-27T19:00:00Z",
  "variants": [
    {
      "variant": "50bpm",
      "label": "50 BPM",
      "bpm": 50,
      "speed_ratio": 0.5,
      "count_in_bars": 1,
      "click_enabled": true,
      "midi_path": "projects/1/practice_audio/song_practice_50bpm.mid",
      "mp3_path": "projects/1/practice_audio/song_practice_50bpm.mp3"
    }
  ]
}
```

**Error codes**:
- `403` — license not confirmed
- `422` — MIDI missing
- `503` — MP3 rendering failed / local transcoder unavailable

---

### 2.10 GET `/api/projects/{id}/practice-audio` — Read practice-audio manifest

Requires `license_confirmed = true`.  
Returns the persisted manifest without regenerating files.

---

### 2.11 GET `/api/projects/{id}/export.practice-audio/{variant}.{format}` — Download practice audio

Requires `license_confirmed = true`.

**Supported variants**: `50bpm`, `70percent`, `fullspeed`  
**Supported formats**: `.mid`, `.mp3`

Returns `404` when the manifest or requested artifact is missing.

---

### 2.12 POST `/api/projects/{id}/license` — Confirm license gate (FR-015)

**Request body**: `{ "confirmed": true }`  
→ `400` if `confirmed` is `false`.

Sets `license_confirmed = true` on the project.

**Response** `200 OK`:

```json
{ "project_id": 1, "license_confirmed": true }
```

---

### 2.13 GET `/api/projects/{id}/share-link` — Read private-share link metadata

Returns the project's current share-link manifest, including `status`, `share_path`,
and `share_url`. `404` if no link has been created yet.

---

### 2.14 POST `/api/projects/{id}/share-link` — Create or rotate a private-share link

**Request body**: `{ "expires_in_days": 7 }`  
Allowed expiry values: `1`, `7`, `30`.

Requires:

1. `license_confirmed = true`
2. score data to exist
3. `source_type != private_research`

**Response** `200 OK`:

```json
{
  "project_id": 1,
  "code": "8H4Q7K2M",
  "created_at": "2026-04-27T23:10:00Z",
  "expires_at": "2026-05-04T23:10:00Z",
  "revoked_at": null,
  "status": "active",
  "share_path": "/share/8H4Q7K2M",
  "share_url": "http://localhost:8000/share/8H4Q7K2M"
}
```

**Error codes**:
- `400` — invalid expiry preset
- `403` — license not confirmed / private research project
- `422` — no score data

---

### 2.15 DELETE `/api/projects/{id}/share-link` — Revoke the active private-share link

Marks the current share code as revoked.  
Returns the revoked manifest with `status = "revoked"`.

---

### 2.16 GET `/api/projects/{id}/review` — Read teacher review state (FR-013)

Requires score data. Returns persisted review manifest or a default draft derived from
the current project score plus arrangement level.

---

### 2.17 POST `/api/projects/{id}/review` — Save teacher review edits (FR-013)

**Request body**:

```json
{
  "arrangement_level": 2,
  "chords_text": "Verse:\nC | G\nChorus:\nAm | F",
  "strum_name": "老師慢刷",
  "strum_notation": "↓ ↓ ↑",
  "strum_description": "先慢練再加速",
  "tab_notes": "副歌先彈第一弦",
  "practice_notes": "每天 5 分鐘，只練前四小節"
}
```

Validates the chord text, updates `Project.arrangement_level`, and persists a review
manifest under the project data directory.

---

### 2.18 POST `/api/projects/{id}/review/downgrade` — Mark too hard

Requires score data. Lowers the active level by one step (minimum Level 1), sets
`too_hard = true`, and refreshes the default strum suggestion for the downgraded level.

---

### 2.19 POST `/api/projects/{id}/review/restore` — Restore original suggestion

Requires score data. Replaces the current review draft with the original
system-generated suggestion.

---

### 2.20 POST `/api/projects/{id}/review/template` — Save review template

**Request body**: `{ "name": "一年級慢版" }`  
Stores the current review draft as a named template inside the project review manifest.

---

### 2.21 POST `/api/projects/{id}/review/template/apply` — Apply review template

**Request body**: `{ "name": "一年級慢版" }`  
Loads the named template, replaces the current draft, and updates the project's
saved arrangement level.

---

## 3. Common Error Codes

| Code | Meaning |
|------|---------|
| `400` | Bad request (wrong file type, `confirmed: false`, invalid share expiry) |
| `403` | License not confirmed / share disallowed for the project |
| `404` | Project not found |
| `413` | File too large (> 10 MB) |
| `422` | No score data / parse failure / missing MIDI |
| `410` | Share link expired or revoked |
| `503` | Practice-audio rendering dependency failed |

---

## 4. Data Persistence

All projects stored in SQLite via SQLModel (`Project` table).  
Uploaded files written to `DATA_DIR/projects/{id}/original{ext}`.  
`score_json` holds a serialised `Score` pydantic model.  
Generated practice-audio assets and `manifest.json` are written to
`DATA_DIR/projects/{id}/practice_audio/`.
Current share-link metadata lives at `DATA_DIR/projects/{id}/share_link.json`,
with shortcode lookup manifests mirrored under `DATA_DIR/share_links/{code}.json`.

---

## 5. Out of Scope (Phase 2+)

- Full MIDI parsing and chord extraction
- Alternate soundfonts or browser-streamed audio previews
- Collaborative editing / multi-user access
