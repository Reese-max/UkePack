"""Practice progress API endpoints."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, date, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, select

from app.core.db import get_session
from app.models.practice_log import PracticeLog, PracticeLogCreate, PracticeLogRead
from app.models.project import Project

router = APIRouter(prefix="/api/projects", tags=["practice"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.post(
    "/{project_id}/practice-log",
    response_model=PracticeLogRead,
    status_code=201,
)
def record_practice_session(
    project_id: int,
    body: PracticeLogCreate,
    session: SessionDep,
) -> PracticeLog:
    """Record a completed practice session."""
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")

    log = PracticeLog(
        project_id=project_id,
        chords_practiced=body.chords_practiced,
        duration_seconds=max(0, body.duration_seconds),
        speed_pct=body.speed_pct,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


@router.get("/{project_id}/practice-progress")
def get_practice_progress(
    project_id: int,
    session: SessionDep,
) -> dict[str, Any]:
    """Return aggregated practice progress stats."""
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")

    logs = list(
        session.exec(
            select(PracticeLog)
            .where(PracticeLog.project_id == project_id)
            .order_by(col(PracticeLog.created_at))
        ).all()
    )

    if not logs:
        return {
            "total_sessions": 0,
            "total_seconds": 0,
            "streak_days": 0,
            "longest_streak": 0,
            "chord_counts": {},
            "recent_sessions": [],
            "last_practice": None,
        }

    # Aggregate stats
    total_seconds = sum(lg.duration_seconds for lg in logs)

    # Chord frequency
    chord_counter: Counter[str] = Counter()
    for lg in logs:
        for ch in lg.chords_practiced.split(","):
            ch = ch.strip()
            if ch:
                chord_counter[ch] += 1

    # Streak calculation (consecutive days with at least one session)
    practice_dates: set[str] = set()
    for lg in logs:
        practice_dates.add(lg.created_at.astimezone(UTC).strftime("%Y-%m-%d"))

    today = datetime.now(UTC).date()
    streak = 0
    check = today
    while check.strftime("%Y-%m-%d") in practice_dates:
        streak += 1
        check -= timedelta(days=1)

    # If no practice today, check from yesterday
    if streak == 0:
        check = today - timedelta(days=1)
        while check.strftime("%Y-%m-%d") in practice_dates:
            streak += 1
            check -= timedelta(days=1)

    # Longest streak
    sorted_dates = sorted(practice_dates)
    longest = 0
    current = 0
    prev_date: date | None = None
    for d in sorted(sorted_dates):
        dt = datetime.strptime(d, "%Y-%m-%d").date()
        if prev_date and (dt - prev_date).days == 1:
            current += 1
        else:
            current = 1
        longest = max(longest, current)
        prev_date = dt

    # Recent 5 sessions
    recent = [
        {
            "id": lg.id,
            "chords_practiced": lg.chords_practiced,
            "duration_seconds": lg.duration_seconds,
            "speed_pct": lg.speed_pct,
            "created_at": lg.created_at.isoformat(),
        }
        for lg in logs[-5:]
    ]

    return {
        "total_sessions": len(logs),
        "total_seconds": total_seconds,
        "streak_days": streak,
        "longest_streak": max(longest, streak),
        "chord_counts": dict(chord_counter.most_common()),
        "recent_sessions": recent,
        "last_practice": logs[-1].created_at.isoformat(),
    }
