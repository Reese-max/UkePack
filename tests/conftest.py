import shutil
import textwrap
import zipfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.db import get_session, reset_engine
from app.main import app


@pytest.fixture(scope="session")
def compressed_mxl_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Minimal MXL fixture built with zipfile (not music21.write) — avoids ~14s overhead per session."""
    xml = textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <score-partwise version="3.1">
          <work><work-title>Compressed Score</work-title></work>
          <identification><encoding><software>test</software></encoding></identification>
          <part-list>
            <score-part id="P1"><part-name>Piano</part-name></score-part>
          </part-list>
          <part id="P1">
            <measure number="1">
              <attributes>
                <divisions>1</divisions>
                <key><fifths>0</fifths><mode>major</mode></key>
                <time><beats>4</beats><beat-type>4</beat-type></time>
                <clef><sign>G</sign><line>2</line></clef>
              </attributes>
              <note>
                <pitch><step>C</step><octave>4</octave></pitch>
                <duration>4</duration>
                <type>whole</type>
              </note>
            </measure>
          </part>
        </score-partwise>
    """)
    container = textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
          <rootfiles>
            <rootfile full-path="score.xml"
                      media-type="application/vnd.recordare.musicxml+xml"/>
          </rootfiles>
        </container>
    """)
    tmp = tmp_path_factory.mktemp("mxl")
    path = tmp / "compressed_score.mxl"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("META-INF/container.xml", container)
        zf.writestr("score.xml", xml)
    return path


@pytest.fixture
def mock_ffmpeg_encode(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace ffmpeg MP3 encoding with a WAV copy in integration tests.

    Avoids ~3s ffmpeg subprocess startup per generate_practice_audio call in API/page tests.
    The core practice_audio unit test still runs real ffmpeg.
    """
    def _fake_encode(wav_path: Path, mp3_path: Path) -> None:
        shutil.copy2(wav_path, mp3_path)

    monkeypatch.setattr("app.core.practice_audio._encode_mp3", _fake_encode)


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
