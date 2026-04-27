from __future__ import annotations

from typing import Any

import pytest

from app.core import db as db_module


def test_reset_engine_disposes_cached_engine() -> None:
    class FakeEngine:
        def __init__(self) -> None:
            self.disposed = False

        def dispose(self) -> None:
            self.disposed = True

    engine = FakeEngine()
    db_module._cache["engine"] = engine

    db_module.reset_engine()

    assert engine.disposed is True
    assert "engine" not in db_module._cache


def test_get_session_closes_context(monkeypatch: pytest.MonkeyPatch) -> None:
    events: list[str] = []

    class FakeSession:
        closed = False

    class FakeSessionContext:
        def __enter__(self) -> FakeSession:
            events.append("enter")
            return FakeSession()

        def __exit__(self, *args: Any) -> None:
            events.append("exit")

    monkeypatch.setattr(db_module, "get_engine", lambda: object())
    monkeypatch.setattr(db_module, "Session", lambda engine: FakeSessionContext())

    session_generator = db_module.get_session()
    session = next(session_generator)

    assert isinstance(session, FakeSession)
    assert events == ["enter"]

    with pytest.raises(StopIteration):
        next(session_generator)

    assert events == ["enter", "exit"]
