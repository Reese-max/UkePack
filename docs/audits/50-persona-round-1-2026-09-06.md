# 50-Persona Audit — Round 1

Date: 2026-09-06
Protocol: `Reese-max/autodev-ng/docs/portfolio-audit/2026-09-06-50-persona-audit.md`

> Fixed 50-persona model simulation plus repository evidence review; not 50 human participants.

## Round 1 result

Status: **P0 OPEN — NOT CLEAN**

### P0 — public deployment has no project authorization boundary

The README documents one-click public deployment. Current project persistence uses an auto-increment integer primary key and the API/HTMX routes operate on those IDs without authentication or ownership checks.

Examples on the current default branch:
- `GET /api/projects/{project_id}` reads project metadata.
- `POST /api/projects/{project_id}/chords` overwrites project chord/score state.
- `GET /api/projects/{project_id}/analysis` reads derived content.
- `POST /api/projects/{project_id}/arrange` modifies arrangement state.

Projects even carry a `usage_type` default of `private`, but that label does not enforce access control. Adjacent integer IDs are enumerable.

Actionable issue: #1 — `[P0][50-persona audit] Add project authorization before public deployment`.

## Positive evidence

- Upload sizes and license-confirmation flows are documented.
- Private share links are separate, revocable and expiring by design.
- The project has a large documented test suite and clear teacher-review/product workflows.

Those controls do not substitute for owner authorization on project APIs.

## Regression gates

1. Add authenticated owner/tenant or strong per-project capability authorization.
2. Enforce it on every read/write/import/export/review/practice/share-management route and HTMX page.
3. Keep public share capability separate from edit/owner authority.
4. Test adjacent-ID enumeration and cross-user access comprehensively.
5. Make public production deployment fail closed if auth is not configured.
6. Run the same fixed personas against a non-production public deployment and require two consecutive rounds without new P0/P1/P2 after remediation.

## Runtime status

**Pending.** The broken authorization is reproducible from default-branch route/model code and the documented public deployment path, but this round did not attack a live deployment.