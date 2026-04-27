# Spec: Projects REST API

**Status**: Accepted  
**Scope**: `app/api/projects.py`  
**Implements**: FR-001 – FR-015 (BACKLOG P1-01 – P1-10)

---

## 1. Overview

Nine REST endpoints that expose the full UkePack pipeline over HTTP. All endpoints are prefixed `/api/projects` and tagged `projects`.

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
Pipe-delimited symbols, multi-line, section headers (lines ending `:`) ignored.  
Builds a minimal `Score` from the parsed symbols.

**Response** `200 OK`:

```json
{ "project_id": 1, "chord_count": 4, "measures": 4 }
```

---

### 2.5 GET `/api/projects/{id}/analysis` — Key/BPM/chords/difficulty (FR-005)

Requires `score_json` or `chords_text` to be set → `422` otherwise.

**Response** `200 OK`:

```json
{
  "key": "C major",
  "target_key": "C major",
  "transposition_steps": 0,
  "bpm": 120,
  "time_signature": "4/4",
  "measures": 32,
  "chord_count": 12,
  "unique_chords": ["C", "G", "Am", "F"],
  "playability_score": 72,
  "recommended_level": 1,
  "label": "Beginner"
}
```

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

### 2.9 POST `/api/projects/{id}/license` — Confirm license gate (FR-015)

**Request body**: `{ "confirmed": true }`  
→ `400` if `confirmed` is `false`.

Sets `license_confirmed = true` on the project.

**Response** `200 OK`:

```json
{ "project_id": 1, "license_confirmed": true }
```

---

## 3. Common Error Codes

| Code | Meaning |
|------|---------|
| `400` | Bad request (wrong file type, `confirmed: false`) |
| `403` | License not confirmed |
| `404` | Project not found |
| `413` | File too large (> 10 MB) |
| `422` | No score data / parse failure |

---

## 4. Data Persistence

All projects stored in SQLite via SQLModel (`Project` table).  
Uploaded files written to `DATA_DIR/projects/{id}/original{ext}`.  
`score_json` holds a serialised `Score` pydantic model.

---

## 5. Out of Scope (Phase 2+)

- Full MIDI parsing and chord extraction
- Collaborative editing / multi-user access
- Expiring share links
