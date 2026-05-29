"""Progressive practice-tempo ladder (BACKLOG U3-b).

A slow→original sequence of practice tempos so a child can ramp up gradually.
Each rung is a ratio of the song's original BPM, deduped and floored so very slow
songs still get distinct, playable steps.
"""

from dataclasses import dataclass

_DEFAULT_BPM = 100
_MIN_BPM = 40
_LADDER_RATIOS: tuple[tuple[str, float], ...] = (
    ("慢速", 0.5),
    ("70%", 0.7),
    ("85%", 0.85),
    ("原速", 1.0),
)


@dataclass(frozen=True)
class TempoStep:
    """One rung of the slow→original practice tempo ladder."""

    label: str
    bpm: int
    ratio: float


def tempo_ladder(bpm: int | None) -> list[TempoStep]:
    """Return progressive practice tempos from slow to the song's original speed."""
    base = bpm if bpm and bpm > 0 else _DEFAULT_BPM
    steps: list[TempoStep] = []
    seen: set[int] = set()
    for label, ratio in _LADDER_RATIOS:
        step_bpm = max(round(base * ratio), _MIN_BPM)
        if step_bpm in seen:
            continue
        seen.add(step_bpm)
        steps.append(TempoStep(label=label, bpm=step_bpm, ratio=ratio))
    return steps
