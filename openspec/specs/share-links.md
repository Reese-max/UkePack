# Spec: Expiring Private Share Links

**Status**: Accepted  
**Scope**: `app/core/share_link.py`, `app/api/projects/share.py`, `app/api/share_pages.py`, `app/templates/partials/share_card.html`, `app/templates/share_preview.html`  
**Implements**: BACKLOG P2-04

---

## 1. Overview

Projects can generate one active private-share link at a time. The link uses an
8-character shortcode, expires automatically, and renders a no-index share page
for PDF preview/download plus any already-generated practice-audio artifacts.

This is a convenience privacy layer, not authenticated access control:
possession of the shortcode is the access mechanism.

---

## 2. Eligibility Rules

Share-link creation is allowed only when all of the following are true:

1. the project already exists in storage
2. `license_confirmed = true`
3. score data exists (`score_json` or `chords_text`)
4. `source_type != "private_research"`

Failures map to:

| Condition | Status |
|---|---|
| invalid expiry value | `400` |
| private research / license not confirmed | `403` |
| project missing score data | `422` |

---

## 3. API Contract

All owner-only share-link endpoints live under `/api/projects/{id}`.

| Method | Path | Behaviour |
|---|---|---|
| `GET` | `/share-link` | Return current share-link metadata (`active`, `expired`, or `revoked`) |
| `POST` | `/share-link` | Create or rotate the active share link |
| `DELETE` | `/share-link` | Revoke the current share link |

`POST /share-link` request body:

```json
{ "expires_in_days": 7 }
```

Allowed expiry presets: `1`, `7`, `30`.

Response payload:

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

---

## 4. Page Contract

| Method | Path | Behaviour |
|---|---|---|
| `POST` | `/projects/{id}/share-link` | Create/rotate from the owner UI, redirect with `?share_created=1` |
| `POST` | `/projects/{id}/share-link/revoke` | Revoke from the owner UI, redirect with `?share_revoked=1` |
| `GET` | `/share/{code}` | Public share page with `noindex` meta, PDF preview, and practice-audio links |
| `GET` | `/share/{code}/pack.pdf` | PDF bytes for an active share code only |
| `GET` | `/share/{code}/practice-audio/{variant}.{format}` | Practice-audio artifact download through the share link |

If a share link is expired or revoked, public routes return `410 Gone`.

---

## 5. Persistence

Two synchronized manifests are written:

1. current project manifest → `DATA_DIR/projects/{id}/share_link.json`
2. shortcode lookup manifest → `DATA_DIR/share_links/{code}.json`

Rotating a link revokes the old shortcode manifest and overwrites the project's
current manifest with the newly active code.

---

## 6. Privacy Constraints

1. Share pages must emit `<meta name="robots" content="noindex, nofollow, noarchive">`
2. Private-research projects cannot generate share links
3. Revoked or expired links must stop resolving immediately
