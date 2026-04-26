"""Strum pattern suggestions for ukulele arrangements (PRD §9.10)."""

from dataclasses import dataclass

from app.models import Score

_FALLBACK_TIME_SIG = "4/4"


@dataclass(frozen=True)
class StrumPattern:
    """A named strum pattern for a specific time signature and difficulty level."""

    name: str
    time_signature: str
    # Each element: "D" = down-strum, "U" = up-strum, "-" = rest/pause beat
    strokes: tuple[str, ...]
    min_level: int
    description: str

    def notation(self) -> str:
        """Return a printable arrow notation string for the pattern."""
        _arrow = {"D": "↓", "U": "↑", "-": " "}
        return " ".join(_arrow.get(s, s) for s in self.strokes)


# Five canonical patterns from PRD §9.10
_ALL_PATTERNS: tuple[StrumPattern, ...] = (
    StrumPattern(
        name="入門單刷",
        time_signature="4/4",
        strokes=("D", "D", "D", "D"),
        min_level=1,
        description="每拍一下，適合 6-10 歲初學者",
    ),
    StrumPattern(
        name="輕快刷法",
        time_signature="4/4",
        strokes=("D", "U", "D", "U"),
        min_level=2,
        description="每半拍一下，輕快流暢",
    ),
    StrumPattern(
        name="常見流行刷法",
        time_signature="4/4",
        strokes=("D", "D", "U", "U", "D", "U"),
        min_level=2,
        description="常見流行歌伴奏節奏",
    ),
    StrumPattern(
        name="華爾滋",
        time_signature="3/4",
        strokes=("D", "D", "D"),
        min_level=1,
        description="3/4 拍圓舞曲節奏",
    ),
    StrumPattern(
        name="慢搖",
        time_signature="6/8",
        strokes=("D", "-", "U", "D", "-", "U"),
        min_level=2,
        description="6/8 搖擺感刷法",
    ),
)


def all_patterns() -> tuple[StrumPattern, ...]:
    """Return all registered strum patterns."""
    return _ALL_PATTERNS


def suggest(score: Score) -> list[StrumPattern]:
    """Return all strum patterns suitable for the score's time signature.

    Falls back to 4/4 patterns when no match exists for the given time signature.
    """
    time_sig = score.time_signature or _FALLBACK_TIME_SIG
    matched = [p for p in _ALL_PATTERNS if p.time_signature == time_sig]
    if not matched:
        matched = [p for p in _ALL_PATTERNS if p.time_signature == _FALLBACK_TIME_SIG]
    return matched


def suggest_for_level(score: Score, level: int) -> list[StrumPattern]:
    """Return patterns whose complexity is at or below the given arrangement level."""
    return [p for p in suggest(score) if p.min_level <= level]
