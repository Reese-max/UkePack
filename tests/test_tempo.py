"""Tests for the progressive practice-tempo ladder (BACKLOG U3-b)."""

from app.arrangement.tempo import TempoStep, tempo_ladder


def test_tempo_ladder_progresses_slow_to_full() -> None:
    steps = tempo_ladder(100)

    bpms = [s.bpm for s in steps]
    assert all(isinstance(s, TempoStep) for s in steps)
    assert bpms == sorted(bpms)  # monotonic non-decreasing (slow → fast)
    assert bpms[0] < 100  # starts slower than the song
    assert bpms[-1] == 100  # ends at the original speed


def test_tempo_ladder_final_step_is_original_speed() -> None:
    last = tempo_ladder(96)[-1]
    assert last.bpm == 96
    assert last.ratio == 1.0


def test_tempo_ladder_defaults_when_bpm_missing() -> None:
    assert tempo_ladder(None)[-1].bpm == 100


def test_tempo_ladder_applies_floor_for_slow_songs() -> None:
    assert all(step.bpm >= 40 for step in tempo_ladder(60))


def test_tempo_ladder_dedupes_collapsed_tempos() -> None:
    bpms = [s.bpm for s in tempo_ladder(10)]
    assert len(bpms) == len(set(bpms))  # no duplicate rungs after flooring
