# Spec: Teacher Review Mode

**Status**: Accepted  
**Scope**: `app/core/teacher_review.py`, `app/api/projects/review.py`, `app/api/review_pages.py`, `app/templates/review.html`  
**Implements**: BACKLOG P2-03 / FR-013

---

## 1. Overview

Teacher review mode lets instructors adjust the system suggestion before export. The review state is persisted as a project-scoped JSON manifest under `DATA_DIR/projects/{id}/teacher_review_<created_at>.json` so the feature can ship without a SQLite migration.

---

## 2. Editable Fields

`TeacherReviewDraft` stores:

1. `arrangement_level`
2. `chords_text`
3. `strum_name`
4. `strum_notation`
5. `strum_description`
6. `tab_notes`
7. `practice_notes`

The manifest keeps both `original` (system suggestion) and `current` (teacher-edited) drafts, a `too_hard` flag, a compare list, and named templates.

---

## 3. API Contract

All review endpoints live under `/api/projects/{id}` and require the project to exist plus score data (`score_json` or `chords_text`).

| Method | Path | Behaviour |
|---|---|---|
| `GET` | `/review` | Return persisted review manifest or derived defaults |
| `POST` | `/review` | Validate and persist edited teacher draft |
| `POST` | `/review/downgrade` | Mark `too_hard = true`, lower level by one, refresh default strum |
| `POST` | `/review/restore` | Reset `current` back to `original` |
| `POST` | `/review/template` | Save current draft as named template |
| `POST` | `/review/template/apply` | Replace current draft with named template |

Validation:

- `arrangement_level` must be `1`, `2`, or `3`
- `chords_text` cannot resolve to an empty score
- blank template names are rejected

Errors:

- `404` — project not found
- `422` — project has no score data
- `400` — invalid level, empty review chords, blank template name, missing template

---

## 4. Page Contract

| Method | Path | Behaviour |
|---|---|---|
| `GET` | `/projects/{id}/review` | Render teacher review editor, compare grid, template list |
| `POST` | `/projects/{id}/review/save` | Persist edited form fields, redirect `?saved=1` |
| `POST` | `/projects/{id}/review/downgrade` | Redirect `?downgraded=1` |
| `POST` | `/projects/{id}/review/restore` | Redirect `?restored=1` |
| `POST` | `/projects/{id}/review/save-template` | Redirect `?template_saved=1` |
| `POST` | `/projects/{id}/review/apply-template` | Redirect `?template_applied=1` |

The analysis page and preview page must expose an entry point into review mode when score data exists.

---

## 5. Export Contract

When a persisted review manifest exists, PDF export must:

1. rebuild the score from `current.chords_text`
2. use `current.arrangement_level`
3. show teacher-authored strum text on Page 1 / Page 2
4. show `tab_notes` on Page 3
5. show `practice_notes` on Page 4

If no review manifest exists, export behavior stays unchanged.
