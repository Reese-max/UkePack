"""Legacy-migration custody tests (issue #5).

Covers the operator-mediated handoff that keeps pre-remediation projects
accessible after capability tokens are introduced:
1. Migration writes an operator-only manifest binding each new token to its row.
2. A manifest claim URL restores owner access; wrong/missing tokens are denied.
3. The admin recovery endpoint is fail-closed without an operator secret and
   rejects wrong credentials when configured.
4. Re-running the migration is idempotent and never regenerates assigned tokens.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.config import get_settings
from app.core.db import get_session, migrate_project_schema
from app.main import app
from app.models.project import Project

from collections.abc import Iterator


def _override(session):
    def _dep() -> Iterator:
        yield session

    return _dep

LEGACY_SCHEMA = """
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


def _legacy_db(tmp_path: Path) -> Path:
    db_file = tmp_path / "legacy.db"
    conn = sqlite3.connect(db_file)
    conn.execute(LEGACY_SCHEMA)
    conn.execute("INSERT INTO project (title, source_type) VALUES ('Legacy A', 'public_domain')")
    conn.execute("INSERT INTO project (title, source_type) VALUES ('Legacy B', 'public_domain')")
    conn.commit()
    conn.close()
    return db_file


def _tokens(db_file: Path) -> dict[int, str]:
    conn = sqlite3.connect(db_file)
    rows = dict(conn.execute("SELECT id, owner_token FROM project").fetchall())
    conn.close()
    return rows


def _manifests(data_dir: Path) -> list[Path]:
    return sorted((data_dir / "legacy-recovery").glob("manifest-*.json"))


def test_migration_writes_operator_manifest(tmp_path):
    db_file = _legacy_db(tmp_path)
    data_dir = tmp_path / "data"
    migrate_project_schema(create_engine(f"sqlite:///{db_file}"), data_dir=data_dir)

    manifests = _manifests(data_dir)
    assert len(manifests) == 1
    payload = json.loads(manifests[0].read_text(encoding="utf-8"))
    assert len(payload["projects"]) == 2

    db_tokens = _tokens(db_file)
    for entry in payload["projects"]:
        assert db_tokens[entry["id"]] == entry["owner_token"]
        assert entry["owner_token"].startswith("ukp_legacy_")
        assert entry["claim_url"] == f"/projects/{entry['id']}?token={entry['owner_token']}"


def _migrated_session(tmp_path: Path) -> Session:
    """Full-schema DB whose rows lack owner_token, then migrated to legacy tokens."""
    from sqlalchemy import text

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as seed:
        seed.add(Project(title="Legacy A", source_type="public_domain"))
        seed.add(Project(title="Legacy B", source_type="public_domain"))
        seed.commit()
    # Simulate pre-capability rows: ORM always mints a token and the column is
    # NOT NULL, so strip to '' — the state the migration treats as legacy.
    with engine.begin() as conn:
        conn.execute(text("UPDATE project SET owner_token = ''"))
    migrate_project_schema(engine, data_dir=tmp_path / "data")
    return Session(engine)


def test_claim_url_restores_owner_access(tmp_path):
    session = _migrated_session(tmp_path)
    tokens = {p.id: p.owner_token for p in session.exec(select(Project)).all()}
    app.dependency_overrides[get_session] = _override(session)
    try:
        client = TestClient(app)
        for pid, token in tokens.items():
            assert client.get(f"/projects/{pid}", params={"token": token}).status_code == 200
            assert client.get(f"/projects/{pid}").status_code == 401
            assert client.get(f"/projects/{pid}", params={"token": "ukp_wrong"}).status_code == 403
    finally:
        app.dependency_overrides.clear()
        session.close()


def test_admin_endpoint_requires_operator_secret(tmp_path, monkeypatch):
    session = _migrated_session(tmp_path)
    app.dependency_overrides[get_session] = _override(session)
    monkeypatch.setenv("UKEPACK_AUTH_SECRET", "")
    get_settings.cache_clear()
    try:
        client = TestClient(app)
        assert client.get("/api/admin/legacy-recovery").status_code == 403

        monkeypatch.setenv("UKEPACK_AUTH_SECRET", "s3cr3t-operator-key")
        get_settings.cache_clear()
        assert client.get("/api/admin/legacy-recovery").status_code == 401
        assert (
            client.get(
                "/api/admin/legacy-recovery", headers={"Authorization": "Bearer wrong"}
            ).status_code
            == 401
        )
        resp = client.get(
            "/api/admin/legacy-recovery",
            headers={"Authorization": "Bearer s3cr3t-operator-key"},
        )
        assert resp.status_code == 200
        projects = resp.json()["projects"]
        assert len(projects) == 2
        assert all(p["owner_token"].startswith("ukp_legacy_") for p in projects)
    finally:
        app.dependency_overrides.clear()
        session.close()
        get_settings.cache_clear()


def test_migration_idempotent_no_regeneration(tmp_path):
    db_file = _legacy_db(tmp_path)
    data_dir = tmp_path / "data"
    engine = create_engine(f"sqlite:///{db_file}")

    migrate_project_schema(engine, data_dir=data_dir)
    first = _tokens(db_file)
    migrate_project_schema(engine, data_dir=data_dir)
    assert _tokens(db_file) == first
    assert len(_manifests(data_dir)) == 1


def test_non_legacy_tokens_not_listed(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    session = Session(engine)
    session.add(Project(title="Modern", source_type="public_domain", owner_token="ukp_normal123"))
    session.commit()
    app.dependency_overrides[get_session] = _override(session)
    monkeypatch.setenv("UKEPACK_AUTH_SECRET", "s3cr3t-operator-key")
    get_settings.cache_clear()
    try:
        client = TestClient(app)
        resp = client.get(
            "/api/admin/legacy-recovery",
            headers={"Authorization": "Bearer s3cr3t-operator-key"},
        )
        assert resp.status_code == 200
        assert resp.json()["projects"] == []
    finally:
        app.dependency_overrides.clear()
        session.close()
        get_settings.cache_clear()
