"""Tests for practice progress tracking (API + page)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
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


def _make_client(session: Session):
    def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    return TestClient(app)


# ── API: POST /api/projects/{id}/practice-log ──


def test_record_practice_session(session: Session, project: Project):
    client = _make_client(session)
    resp = client.post(
        f"/api/projects/{project.id}/practice-log",
        json={"chords_practiced": "C,G,Am", "duration_seconds": 120, "speed_pct": 70},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["project_id"] == project.id
    assert data["chords_practiced"] == "C,G,Am"
    assert data["duration_seconds"] == 120
    assert data["speed_pct"] == 70
    assert "id" in data
    assert "created_at" in data


def test_record_practice_session_defaults(session: Session, project: Project):
    client = _make_client(session)
    resp = client.post(
        f"/api/projects/{project.id}/practice-log",
        json={},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["chords_practiced"] == ""
    assert data["duration_seconds"] == 0
    assert data["speed_pct"] == 100


def test_record_practice_session_negative_duration_clamped(session: Session, project: Project):
    client = _make_client(session)
    resp = client.post(
        f"/api/projects/{project.id}/practice-log",
        json={"duration_seconds": -10},
    )
    assert resp.status_code == 201
    assert resp.json()["duration_seconds"] == 0


def test_record_practice_session_project_not_found(session: Session):
    client = _make_client(session)
    resp = client.post("/api/projects/9999/practice-log", json={})
    assert resp.status_code == 404


# ── API: GET /api/projects/{id}/practice-progress ──


def test_progress_empty(session: Session, project: Project):
    client = _make_client(session)
    resp = client.get(f"/api/projects/{project.id}/practice-progress")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_sessions"] == 0
    assert data["total_seconds"] == 0
    assert data["streak_days"] == 0
    assert data["longest_streak"] == 0
    assert data["chord_counts"] == {}
    assert data["recent_sessions"] == []
    assert data["last_practice"] is None


def test_progress_with_sessions(session: Session, project: Project):
    client = _make_client(session)
    # Record 3 sessions
    for i in range(3):
        resp = client.post(
            f"/api/projects/{project.id}/practice-log",
            json={"chords_practiced": "C,G", "duration_seconds": 60 + i * 10},
        )
        assert resp.status_code == 201

    resp = client.get(f"/api/projects/{project.id}/practice-progress")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_sessions"] == 3
    assert data["total_seconds"] == 60 + 70 + 80  # 210
    assert data["chord_counts"]["C"] == 3
    assert data["chord_counts"]["G"] == 3
    assert len(data["recent_sessions"]) == 3
    assert data["last_practice"] is not None


def test_progress_daily_chord_trend(session: Session, project: Project):
    """Verify daily_chord_trend groups chords by date."""
    client = _make_client(session)
    # Record 2 sessions with different chords
    client.post(
        f"/api/projects/{project.id}/practice-log",
        json={"chords_practiced": "C,G,Am", "duration_seconds": 60},
    )
    client.post(
        f"/api/projects/{project.id}/practice-log",
        json={"chords_practiced": "C,F", "duration_seconds": 45},
    )

    resp = client.get(f"/api/projects/{project.id}/practice-progress")
    assert resp.status_code == 200
    data = resp.json()
    trend = data["daily_chord_trend"]
    assert isinstance(trend, dict)
    # All sessions are same day → 1 entry
    assert len(trend) == 1
    day_data = next(iter(trend.values()))
    # C appeared twice, G once, Am once, F once
    assert day_data["C"] == 2
    assert day_data["G"] == 1
    assert day_data["Am"] == 1
    assert day_data["F"] == 1


def test_progress_project_not_found(session: Session):
    client = _make_client(session)
    resp = client.get("/api/projects/9999/practice-progress")
    assert resp.status_code == 404


# ── Page: GET /projects/{id}/progress ──


def test_progress_page_empty(session: Session, project: Project):
    client = _make_client(session)
    resp = client.get(f"/projects/{project.id}/progress")
    assert resp.status_code == 200
    html = resp.text
    assert "練習進度" in html
    assert "還沒有練習紀錄" in html
    assert "開始練習" in html


def test_progress_page_with_data(session: Session, project: Project):
    client = _make_client(session)
    # Record a session via API
    client.post(
        f"/api/projects/{project.id}/practice-log",
        json={"chords_practiced": "C,G,Am", "duration_seconds": 90},
    )
    resp = client.get(f"/projects/{project.id}/progress")
    assert resp.status_code == 200
    html = resp.text
    assert "streak" in html.lower() or "連續" in html  # streak or 連續
    assert "mastery" in html.lower() or "和弦掌握" in html  # mastery or 和弦掌握
    assert "C" in html
    assert "Am" in html
    assert "1.5" in html  # 90 seconds = 1.5 minutes


def test_progress_page_has_back_link(session: Session, project: Project):
    client = _make_client(session)
    resp = client.get(f"/projects/{project.id}/progress")
    assert resp.status_code == 200
    assert f"/projects/{project.id}/practice" in resp.text


def test_progress_page_project_not_found(session: Session):
    client = _make_client(session)
    resp = client.get("/projects/9999/progress")
    assert resp.status_code == 404


# ── Practice page has progress link ──


def test_practice_page_has_progress_link(session: Session, project: Project):
    """Verify practice page links to progress dashboard."""
    from app.models.score import Score

    project.score_json = Score(
        title="Test Song",
        key="C major",
        bpm=100,
        time_signature="4/4",
        measures=8,
        chords=[],
        melody=[],
        sections=[],
    ).model_dump_json()
    session.add(project)
    session.commit()
    session.refresh(project)

    client = _make_client(session)
    resp = client.get(f"/projects/{project.id}/practice")
    assert resp.status_code == 200
    assert f"/projects/{project.id}/progress" in resp.text
