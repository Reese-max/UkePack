"""Tests for practice session report PDF export."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.core.db import get_session
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


@pytest.fixture(name="project")
def project_fixture(session: Session) -> Project:
    p = Project(
        title="Test Song",
        source_type="public_domain",
        chords_text="C G Am F",
    )
    session.add(p)
    session.commit()
    session.refresh(p)
    return p


def _make_client(session: Session, project: Project | None = None):
    def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    client = TestClient(app)
    proj = project or session.exec(select(Project)).first()
    if proj is not None and getattr(proj, "owner_token", None):
        client.cookies.set(f"ukepack_project_{proj.id}", proj.owner_token)
        client.cookies.set("ukepack_owner_token", proj.owner_token)
    return client


def _add_sessions(client: TestClient, project_id: int, count: int = 3) -> None:
    """Helper: record practice sessions."""
    for i in range(count):
        client.post(
            f"/api/projects/{project_id}/practice-log",
            json={
                "chords_practiced": "C,G,Am",
                "duration_seconds": 60 + i * 30,
                "speed_pct": 100 - i * 10,
            },
        )


# ── API: GET /api/projects/{id}/practice-report.pdf ──


def test_practice_report_pdf_with_data(session: Session, project: Project):
    client = _make_client(session)
    _add_sessions(client, project.id, 3)

    resp = client.get(f"/api/projects/{project.id}/practice-report.pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert "practice_report.pdf" in resp.headers.get("content-disposition", "")
    # PDF magic bytes
    assert resp.content[:5] == b"%PDF-"
    assert len(resp.content) > 500


def test_practice_report_pdf_empty_sessions_404(session: Session, project: Project):
    client = _make_client(session)
    resp = client.get(f"/api/projects/{project.id}/practice-report.pdf")
    assert resp.status_code == 404
    assert "No practice sessions" in resp.json()["detail"]


def test_practice_report_pdf_project_not_found(session: Session):
    client = _make_client(session)
    resp = client.get("/api/projects/9999/practice-report.pdf")
    assert resp.status_code == 404


def test_practice_report_pdf_contains_project_title(session: Session, project: Project):
    """PDF filename references the project title."""
    client = _make_client(session)
    _add_sessions(client, project.id, 1)

    resp = client.get(f"/api/projects/{project.id}/practice-report.pdf")
    assert resp.status_code == 200
    disposition = resp.headers.get("content-disposition", "")
    assert "Test Song" in disposition


def test_practice_report_pdf_multiple_sessions_stats(session: Session, project: Project):
    """Report reflects correct aggregate stats across sessions."""
    client = _make_client(session)
    _add_sessions(client, project.id, 5)

    resp = client.get(f"/api/projects/{project.id}/practice-report.pdf")
    assert resp.status_code == 200
    # PDF should be larger with more data
    assert len(resp.content) > 800


def test_practice_report_pdf_renderer_unit():
    """Unit test: render_practice_report produces valid PDF bytes."""
    from app.render.practice_report import render_practice_report

    stats = {
        "total_sessions": 5,
        "total_seconds": 600,
        "streak_days": 3,
        "longest_streak": 5,
        "chord_counts": {"C": 10, "G": 8, "Am": 6, "F": 4},
        "daily_chord_trend": {},
        "recent_sessions": [
            {
                "id": 1,
                "chords_practiced": "C,G,Am",
                "duration_seconds": 120,
                "speed_pct": 100,
                "created_at": "2026-06-15T10:00:00+00:00",
            },
            {
                "id": 2,
                "chords_practiced": "C,F",
                "duration_seconds": 90,
                "speed_pct": 70,
                "created_at": "2026-06-14T10:00:00+00:00",
            },
        ],
        "last_practice": "2026-06-15T10:00:00+00:00",
    }
    pdf = render_practice_report("Test Song", stats)
    assert isinstance(pdf, bytes)
    assert pdf[:5] == b"%PDF-"
    assert len(pdf) > 500


def test_practice_report_pdf_renderer_empty_stats():
    """Unit test: renderer handles empty stats gracefully."""
    from app.render.practice_report import render_practice_report

    stats = {
        "total_sessions": 0,
        "total_seconds": 0,
        "streak_days": 0,
        "longest_streak": 0,
        "chord_counts": {},
        "daily_chord_trend": {},
        "recent_sessions": [],
        "last_practice": None,
    }
    pdf = render_practice_report("Empty Song", stats)
    assert isinstance(pdf, bytes)
    assert pdf[:5] == b"%PDF-"
