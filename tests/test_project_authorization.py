"""Comprehensive security regression tests for project capability authorization.

Covers:
1. Multi-tenant project isolation (Tenant A cannot access/modify Tenant B).
2. Unauthorized access rejection (401 Unauthorized for missing/invalid capability token).
3. Sequential ID enumeration defense.
4. Public share link capability containment (read-only, cannot invoke owner actions).
5. CSRF defense on state-changing requests with hostile Origin/Referer.
6. Fail-closed deployment guard (refuse startup in production without UKEPACK_AUTH_SECRET).
7. Database migration for legacy project rows without owner_token.
"""

from __future__ import annotations

import os
import sqlite3
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.config import get_settings
from app.core.auth import validate_deployment_security
from app.core.db import get_session, migrate_project_schema
from app.main import app
from app.models.project import Project


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:

        def _override():
            yield session

        app.dependency_overrides[get_session] = _override
        yield session
        app.dependency_overrides.clear()


@pytest.fixture(name="client")
def client_fixture(session: Session) -> TestClient:
    def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    return TestClient(app)


def test_multi_tenant_isolation(client: TestClient):
    """Verify that User A cannot read, update, or export User B's project."""
    # User A creates Project A
    resp_a = client.post(
        "/api/projects",
        json={"title": "Song A", "source_type": "public_domain"},
    )
    assert resp_a.status_code == 201
    proj_a = resp_a.json()
    token_a = proj_a["owner_token"]
    assert token_a.startswith("ukp_")

    # User B creates Project B
    resp_b = client.post(
        "/api/projects",
        json={"title": "Song B", "source_type": "public_domain"},
    )
    assert resp_b.status_code == 201
    proj_b = resp_b.json()
    proj_b_id = proj_b["id"]
    token_b = proj_b["owner_token"]
    assert token_b.startswith("ukp_")
    assert token_a != token_b

    # Confirm license for Project B so export endpoint can proceed past license check
    auth_client_b = TestClient(app)
    auth_client_b.headers["X-Project-Token"] = token_b
    lic_res = auth_client_b.post(f"/api/projects/{proj_b_id}/license", json={"confirmed": True})
    assert lic_res.status_code == 200

    # Client with Token A attempting to read/modify/export Project B
    unauth_client = TestClient(app)
    unauth_client.headers["Authorization"] = f"Bearer {token_a}"

    # Read Project B -> 403 Forbidden
    get_res = unauth_client.get(f"/api/projects/{proj_b_id}")
    assert get_res.status_code == 403

    # Update chords of Project B -> 403 Forbidden
    post_res = unauth_client.post(
        f"/api/projects/{proj_b_id}/chords",
        json={"text": "E B C#m A"},
    )
    assert post_res.status_code == 403

    # Attempt export of Project B -> 403 Forbidden
    pdf_res = unauth_client.get(f"/api/projects/{proj_b_id}/export.pdf")
    assert pdf_res.status_code == 403

    # Attempt practice progress of Project B -> 403 Forbidden
    practice_res = unauth_client.get(f"/api/projects/{proj_b_id}/practice-progress")
    assert practice_res.status_code == 403

    # Owner B can access Project B without issue
    ok_res = auth_client_b.get(f"/api/projects/{proj_b_id}")
    assert ok_res.status_code == 200
    assert ok_res.json()["title"] == "Song B"


def test_unauthorized_rejection(client: TestClient, session: Session):
    """Requests with no capability token or cookie must be rejected with 401."""
    p = Project(
        title="Protected Song",
        source_type="public_domain",
        chords_text="C G",
        license_confirmed=True,
    )
    session.add(p)
    session.commit()
    session.refresh(p)

    bare_client = TestClient(app)

    # API endpoints
    assert bare_client.get(f"/api/projects/{p.id}").status_code == 401
    assert bare_client.post(f"/api/projects/{p.id}/chords", json={"text": "C"}).status_code == 401
    assert bare_client.post(f"/api/projects/{p.id}/practice-log", json={}).status_code == 401
    assert bare_client.get(f"/api/projects/{p.id}/practice-progress").status_code == 401
    assert bare_client.get(f"/api/projects/{p.id}/export.pdf").status_code == 401

    # Page HTML endpoints
    assert bare_client.get(f"/projects/{p.id}").status_code == 401
    assert bare_client.get(f"/projects/{p.id}/preview").status_code == 401
    assert bare_client.get(f"/projects/{p.id}/practice").status_code == 401
    assert bare_client.get(f"/projects/{p.id}/review").status_code == 401
    assert bare_client.get(f"/projects/{p.id}/progress").status_code == 401


def test_id_enumeration_defense(client: TestClient, session: Session):
    """An attacker enumerating integer IDs without tokens is blocked across all IDs."""
    for i in range(1, 4):
        p = Project(title=f"Song {i}", source_type="public_domain", chords_text="C")
        session.add(p)
    session.commit()

    attacker = TestClient(app)
    for target_id in [1, 2, 3]:
        resp = attacker.get(f"/api/projects/{target_id}")
        assert resp.status_code == 401


def test_public_share_containment(client: TestClient, session: Session):
    """Share links grant read-only view access, strictly barring modifications."""
    # Create project
    resp = client.post(
        "/api/projects",
        json={"title": "Shared Song", "source_type": "public_domain"},
    )
    proj = resp.json()
    proj_id = proj["id"]
    token = proj["owner_token"]

    owner_client = TestClient(app)
    owner_client.headers["X-Project-Token"] = token

    # Add chords
    chord_res = owner_client.post(
        f"/api/projects/{proj_id}/chords",
        json={"text": "C G Am F"},
    )
    assert chord_res.status_code == 200

    # License confirmation is required before sharing
    lic_res = owner_client.post(f"/api/projects/{proj_id}/license", json={"confirmed": True})
    assert lic_res.status_code == 200

    # Owner creates a share link via POST /api/projects/{id}/share-link
    share_res = owner_client.post(f"/api/projects/{proj_id}/share-link", json={"expires_in_days": 7})
    assert share_res.status_code == 200
    code = share_res.json()["code"]

    # Public visitor accesses via public share route
    visitor = TestClient(app)
    pub_res = visitor.get(f"/share/{code}")
    assert pub_res.status_code == 200
    assert "Shared Song" in pub_res.text

    pub_pdf_res = visitor.get(f"/share/{code}/pack.pdf")
    assert pub_pdf_res.status_code == 200
    assert pub_pdf_res.headers["content-type"] == "application/pdf"

    # Public visitor CANNOT use share code to modify project chords or access owner actions
    visitor.headers["X-Project-Token"] = code
    mod_res = visitor.post(
        f"/api/projects/{proj_id}/chords",
        json={"text": "F G C Am"},
    )
    assert mod_res.status_code in (401, 403)


def test_csrf_defense_with_cross_origin(session: Session):
    """State-changing requests carrying hostile Origin/Referer with cookies are rejected."""
    p = Project(title="CSRF Guard Song", source_type="public_domain", chords_text="C G")
    session.add(p)
    session.commit()
    session.refresh(p)

    cookie_client = TestClient(app)
    cookie_client.cookies.set(f"ukepack_project_{p.id}", p.owner_token)
    cookie_client.cookies.set("ukepack_owner_token", p.owner_token)

    # Hostile Origin on state-changing POST
    resp = cookie_client.post(
        f"/api/projects/{p.id}/chords",
        headers={"Origin": "https://attacker.evil.com"},
        json={"text": "A B C"},
    )
    assert resp.status_code == 403
    assert "CSRF" in resp.json()["detail"]


def test_fail_closed_production_guard():
    """Application startup MUST fail closed if UKEPACK_AUTH_SECRET is unset in production."""
    with patch.dict(os.environ, {"ENVIRONMENT": "production", "UKEPACK_AUTH_SECRET": ""}, clear=False):
        get_settings.cache_clear()
        with pytest.raises(RuntimeError, match="UKEPACK_AUTH_SECRET is missing"):
            validate_deployment_security()

    with patch.dict(os.environ, {"RENDER": "true", "UKEPACK_AUTH_SECRET": ""}, clear=False):
        get_settings.cache_clear()
        with pytest.raises(RuntimeError, match="UKEPACK_AUTH_SECRET is missing"):
            validate_deployment_security()

    # Valid secret allows startup
    with patch.dict(os.environ, {"ENVIRONMENT": "production", "UKEPACK_AUTH_SECRET": "a" * 32}, clear=False):
        get_settings.cache_clear()
        validate_deployment_security()

    get_settings.cache_clear()


def test_database_migration_legacy_projects(tmp_path):
    """migrate_project_schema automatically populates owner_token for legacy rows."""
    db_file = tmp_path / "legacy.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    # Create legacy table without owner_token column
    cursor.execute(
        """
        CREATE TABLE project (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR NOT NULL,
            source_type VARCHAR NOT NULL,
            bpm INTEGER NOT NULL DEFAULT 100,
            time_signature VARCHAR NOT NULL DEFAULT '4/4',
            key VARCHAR NOT NULL DEFAULT 'C',
            chords_text VARCHAR NOT NULL DEFAULT '',
            melody_notes VARCHAR NOT NULL DEFAULT '',
            arrangement_style VARCHAR NOT NULL DEFAULT 'four_finger',
            style VARCHAR NOT NULL DEFAULT '',
            strum_pattern VARCHAR NOT NULL DEFAULT '',
            score_json VARCHAR,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        "INSERT INTO project (title, source_type, chords_text) VALUES ('Legacy Song 1', 'public_domain', 'C G')"
    )
    cursor.execute(
        "INSERT INTO project (title, source_type, chords_text) VALUES ('Legacy Song 2', 'public_domain', 'Am F')"
    )
    conn.commit()
    conn.close()

    engine = create_engine(f"sqlite:///{db_file}")
    # Run migration
    migrate_project_schema(engine)

    # Verify columns and generated tokens
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, owner_token FROM project")
    rows = cursor.fetchall()
    conn.close()

    assert len(rows) == 2
    for _proj_id, _title, owner_token in rows:
        assert owner_token is not None
        assert owner_token.startswith("ukp_")
        assert len(owner_token) > 20
