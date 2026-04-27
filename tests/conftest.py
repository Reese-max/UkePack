from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.db import get_session, reset_engine
from app.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    reset_engine()
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        reset_engine()


@pytest.fixture
def db_client() -> Iterator[TestClient]:
    """TestClient backed by an in-memory SQLite DB (StaticPool = shared connection)."""
    reset_engine()
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def _override() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
        reset_engine()
