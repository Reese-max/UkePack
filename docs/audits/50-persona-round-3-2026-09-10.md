# 50-Persona Audit — Round 3

Date: 2026-09-10
Protocol: `Reese-max/autodev-ng/docs/portfolio-audit/2026-09-06-50-persona-audit.md`
Default branch: `master`
Audited default-branch SHA: `20e6ec5d09379afdcfff496a610e3b37f97c360e`
Product/security remediation code reviewed: `436db728300f6679c193eb886af7a2fd672d7fb2` (current default branch contains this code plus later audit documentation)

> Fixed 50-persona model simulation plus current repository/CI evidence. This is not a 50-human study. No browser, deployed service, or live migration behavior is claimed without execution evidence.

## Result

Status: **NOT CLEAN — new P1 #5; existing P1 #2 remains open.**

The Round-1 P0 cross-project authorization flaw is materially improved in current source: project-scoped reads/writes use a cryptographically random per-project capability, protected routes call the shared authorization check, public share codes are separated from owner capabilities, and production startup has a fail-closed configuration guard. This round does not reopen the original predictable-ID authorization finding.

However, the fixed personas uncovered a post-remediation upgrade/recovery problem: the legacy SQLite migration generates a brand-new random capability for every pre-auth project row but provides no mechanism that hands that newly generated capability to the legitimate pre-upgrade user/operator. Once the new authorization boundary is active, the same legitimate user cannot already possess the random token and is rejected with 401. The persisted project remains in SQLite, so this is classified P1 rather than P0 data loss.

Issue: #5 — `[P1][50-persona audit] Preserve access to legacy projects when capability tokens are introduced`.

## Fixed-persona regression

Relevant fixed personas: C04, D03, D05, E03, H04, I02, I05, J04.

Scenario:
1. Start from a database created before `owner_token` existed.
2. Upgrade/start the remediated application.
3. `migrate_project_schema()` adds/populates `owner_token` with a fresh `ukp_legacy_...` value.
4. The prior user resumes from the same browser/workflow, which cannot contain that newly generated token.
5. `/projects/<id>` or `/api/projects/<id>` reaches `verify_project_access()` and returns 401 because no matching capability is available.
6. Current default source has no authenticated owner mapping, one-time claim flow, recovery/export handoff, or other custody transfer for these generated legacy capabilities.

This is deterministic from current source semantics; no live upgrade was executed in this round.

## Evidence

- `app/core/db.py::migrate_project_schema()` selects rows with null/empty `owner_token` and writes a freshly generated `ukp_legacy_<random>` token directly into SQLite.
- `app/core/auth.py::verify_project_access()` requires an exact matching project capability and returns 401 when absent.
- `tests/test_project_authorization.py::test_database_migration_legacy_projects()` verifies only that migrated rows receive tokens; it does not test legitimate pre-upgrade owner resume or token custody transfer.
- `docs/security/PROJECT_AUTHORIZATION_AND_ISOLATION.md` states that legacy migration keeps existing data usable without interruption, but no corresponding recovery/claim path was found on current default source.
- Search found no `ukp_legacy_` consumer outside the migration.

## Existing blocker

Issue #2 remains open: current CI is still red because the governance-history parser crashes on a legal subject-only commit record. Current default SHA `20e6ec5d09379afdcfff496a610e3b37f97c360e` has GitHub Actions run `34158518182` with conclusion `failure`. Therefore this round does not claim a green current-SHA test gate.

## Runtime evidence boundary

No live/public UkePack deployment, two-user authorization matrix, browser cookie/CSRF flow, legacy database upgrade, PDF/mobile flow, or real share-link recipient flow was executed in this audit round. Static source evidence and GitHub Actions metadata are reported separately from runtime validation.

## CLEAN gate

`UkePack` remains **NOT CLEAN**. New P1 #5 resets the consecutive no-new-P0/P1/P2 count. Before CLEAN:

1. #5 must provide a secure, auditable legacy-project custody/recovery path and upgrade regression tests.
2. Existing P1 #2 must be resolved with a green full CI run.
3. Required non-production two-user authorization/share containment and upgrade-resume runtime evidence must be recorded.
4. The same fixed 50 personas must then complete two consecutive current/recent-code rounds without new P0/P1/P2 findings.
