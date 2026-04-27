# Spec: HTMX Page Routes

**Status**: Accepted  
**Scope**: `app/api/pages.py`  
**Implements**: BACKLOG P1-12 – P1-15 plus practice-audio page flow for P2-02

---

## 1. Overview

Seven browser-facing HTML paths compose the HTMX-powered UI. All routes render Jinja2 templates; HTMX partials return fragments only. Children-first styling is applied globally via `base.html` (18 px font, 52 px buttons, high contrast).

---

## 2. Routes

### 2.1 GET `/new` — New-project form

Renders `new_project.html`.  
Context: `source_types` list of `(value, label)` pairs.  
No auth required.

---

### 2.2 POST `/projects/create-htmx` — Create project (HTMX form submit)

**Form fields**:

| Field | Required | Notes |
|-------|----------|-------|
| `title` | yes | |
| `source_type` | yes | |
| `usage_type` | no | default `"private"` |
| `learner_age` | no | digit string or empty |
| `file` | no | optional MusicXML upload |

**Behaviour**:
1. Create `Project` row in SQLite.
2. If `file` is present and has `.musicxml` / `.xml` / `.mxl` extension:
   a. Stream-save with 10 MB limit.
   b. Call `import_musicxml_into_project`.
   c. On `ValueError` / `RuntimeError`: log warning, delete partial file, redirect with `?import_error=1`.
3. Redirect `303` → `/projects/{id}`.

**Redirect rules**:

| Outcome | Destination |
|---------|-------------|
| Success (with or without file) | `GET /projects/{id}` |
| MusicXML parse failure | `GET /projects/{id}?import_error=1` |

---

### 2.3 GET `/projects/{id}` — Analysis page

Renders `analysis.html`.  
Context includes `project` dict, `analysis` dict (or `null`), `import_error` bool,
`audio_error` bool, and optional `practice_audio` manifest data.  
If `?import_error=1` in query string: template displays a red error banner.  
`analysis` is `null` when no score data exists (project created without a file).
When score data exists, the template shows:

1. score metadata
2. section map (`analysis.sections`) with manual vs detected badges
3. chord list
4. strum selector
5. license gate card
6. practice-audio actions when a MIDI upload exists

---

### 2.4 GET `/projects/{id}/strum-partial` — HTMX strum fragment

**Query param**: `level` (int, default 1).  
Returns `partials/strum_patterns.html` fragment — **not** a full HTML page.  
Used for read-only fragment fetches and tests.

Context:

```json
{
  "strum_patterns": [{"name": "...", "notation": "...", "description": "..."}],
  "level": 1
}
```

---

### 2.5 POST `/projects/{id}/strum-partial` — Persist arrangement level from the analysis UI

**Form field**: `level` (required, one of `1`, `2`, `3`).  
Updates `Project.arrangement_level`, bumps `updated_at`, then returns the same
`partials/strum_patterns.html` fragment for HTMX swap-in.

The analysis page level tabs must call this route so the saved arrangement level
matches the strum pattern preview and later PDF export.

---

### 2.6 POST `/projects/{id}/confirm-license` — License gate (FR-015)

Sets `license_confirmed = true` on the project.  
Redirects `303` → `/projects/{id}`.  
`404` if project not found.

**HTMX contract**: `analysis.html` submits this route via `hx-post`; on success the license section is replaced with a confirmation message.

---

### 2.7 POST `/projects/{id}/generate-practice-audio` — Practice-audio generate action

Requires an existing project.  
If the project is not license-confirmed or generation fails, redirect `303` to
`/projects/{id}?audio_error=1`.  
On success, redirect `303` back to `/projects/{id}`.

---

### 2.8 GET `/projects/{id}/preview` — PDF preview

Renders `preview.html` with an `<iframe>` pointing to `/api/projects/{id}/export.pdf`.  
If the project has uploaded MIDI data, the page also shows practice-audio
generate/download actions.
`404` if project not found.

---

## 3. Error Display Contract

| Condition | UI behaviour |
|-----------|-------------|
| `?import_error=1` | Red banner: "匯入失敗，請檢查檔案格式" |
| `?audio_error=1` | Red banner: "練習音檔產生失敗，請確認已上傳有效 MIDI 並完成授權確認。" |
| No score data | Analysis section shows placeholder text |
| License not confirmed | Download button is disabled; confirm form is shown |

---

## 4. Styling Constraints (P1-15)

- Base font: 18 px minimum
- Interactive targets: min height 52 px
- Color contrast ratio: ≥ 4.5:1 (WCAG AA)
- Chord diagrams: displayed at ≥ 110 px wide
- HTMX loaded via CDN (`htmx.org/1.9.12`)

---

## 5. Out of Scope

- OAuth / session-based authentication
- Multi-language UI (Chinese only for MVP)
- Real-time collaborative editing
