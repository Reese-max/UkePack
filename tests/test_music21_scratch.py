"""Verify music21 scratch directory is isolated per pytest-xdist worker."""

from music21.environment import Environment


def test_music21_scratch_dir_is_worker_isolated() -> None:
    scratch = Environment().getRootTempDir()
    assert "ukepack_music21_" in str(scratch)