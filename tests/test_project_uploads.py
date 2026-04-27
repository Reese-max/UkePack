"""Tests for shared project upload helpers."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile

from app.api.project_uploads import UPLOAD_CHUNK_BYTES, save_upload_with_limit
from app.core.musicxml import MAX_IMPORT_BYTES


class TrackingBytesIO(io.BytesIO):
    """BytesIO that records requested read sizes."""

    def __init__(self, payload: bytes) -> None:
        super().__init__(payload)
        self.read_sizes: list[int | None] = []

    def read(self, size: int | None = -1) -> bytes:
        self.read_sizes.append(size)
        return super().read(size)


@pytest.mark.asyncio
async def test_save_upload_with_limit_reads_in_fixed_chunks(tmp_path: Path) -> None:
    payload = b"x" * (UPLOAD_CHUNK_BYTES * 3 + 17)
    tracking_file = TrackingBytesIO(payload)
    upload = UploadFile(filename="song.musicxml", file=tracking_file)
    destination = tmp_path / "song.musicxml"

    written = await save_upload_with_limit(upload, destination)

    assert written == len(payload)
    assert destination.read_bytes() == payload
    assert len(tracking_file.read_sizes) > 1
    assert all(size == UPLOAD_CHUNK_BYTES for size in tracking_file.read_sizes)


@pytest.mark.asyncio
async def test_save_upload_with_limit_allows_exact_limit(tmp_path: Path) -> None:
    payload = b"x" * MAX_IMPORT_BYTES
    upload = UploadFile(filename="exact.musicxml", file=io.BytesIO(payload))
    destination = tmp_path / "exact.musicxml"

    written = await save_upload_with_limit(upload, destination)

    assert written == MAX_IMPORT_BYTES
    assert destination.stat().st_size == MAX_IMPORT_BYTES


@pytest.mark.asyncio
async def test_save_upload_with_limit_rejects_oversized_payload(tmp_path: Path) -> None:
    upload = UploadFile(
        filename="too-large.musicxml",
        file=io.BytesIO(b"x" * (MAX_IMPORT_BYTES + 1)),
    )
    destination = tmp_path / "too-large.musicxml"

    with pytest.raises(HTTPException) as exc_info:
        await save_upload_with_limit(upload, destination)

    assert exc_info.value.status_code == 413
    assert exc_info.value.detail == "File too large"
    assert not destination.exists()
