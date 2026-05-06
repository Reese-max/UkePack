"""Tests for the strum pattern suggestion module (PRD §9.10)."""

from app.arrangement.strum_pattern import (
    StrumPattern,
    all_patterns,
    suggest,
    suggest_for_level,
)
from app.models import Score


def _score_with_time_sig(time_sig: str | None) -> Score:
    return Score(title="Test", key="C major", time_signature=time_sig, measures=4)


class TestAllPatterns:
    def test_returns_exactly_five_patterns(self) -> None:
        assert len(all_patterns()) == 5

    def test_covers_all_required_time_signatures(self) -> None:
        time_sigs = {p.time_signature for p in all_patterns()}
        assert "4/4" in time_sigs
        assert "3/4" in time_sigs
        assert "6/8" in time_sigs

    def test_each_stroke_is_valid(self) -> None:
        valid = {"D", "U", "-"}
        for pattern in all_patterns():
            for stroke in pattern.strokes:
                assert stroke in valid, f"Invalid stroke '{stroke}' in {pattern.name}"

    def test_each_pattern_has_nonempty_strokes(self) -> None:
        for pattern in all_patterns():
            assert len(pattern.strokes) > 0

    def test_min_level_is_1_or_2(self) -> None:
        for pattern in all_patterns():
            assert pattern.min_level in {1, 2}

    def test_pattern_names_are_unique(self) -> None:
        names = [p.name for p in all_patterns()]
        assert len(names) == len(set(names))


class TestNotation:
    def test_down_up_notation(self) -> None:
        pattern = StrumPattern(
            name="test", time_signature="4/4", strokes=("D", "U"), min_level=1, description=""
        )
        assert pattern.notation() == "↓ ↑"

    def test_rest_renders_as_space(self) -> None:
        pattern = StrumPattern(
            name="test",
            time_signature="6/8",
            strokes=("D", "-", "U"),
            min_level=2,
            description="",
        )
        assert "↓" in pattern.notation()
        assert "↑" in pattern.notation()
        assert " " in pattern.notation()

    def test_four_down_strums(self) -> None:
        pattern = StrumPattern(
            name="入門單刷",
            time_signature="4/4",
            strokes=("D", "D", "D", "D"),
            min_level=1,
            description="",
        )
        assert pattern.notation() == "↓ ↓ ↓ ↓"


class TestSuggest:
    def test_four_four_returns_three_patterns(self) -> None:
        patterns = suggest(_score_with_time_sig("4/4"))
        assert len(patterns) == 3
        assert all(p.time_signature == "4/4" for p in patterns)

    def test_three_four_returns_waltz(self) -> None:
        patterns = suggest(_score_with_time_sig("3/4"))
        assert len(patterns) == 1
        assert patterns[0].name == "華爾滋"

    def test_six_eight_returns_slow_rock(self) -> None:
        patterns = suggest(_score_with_time_sig("6/8"))
        assert len(patterns) == 1
        assert patterns[0].name == "慢搖"

    def test_none_time_sig_falls_back_to_four_four(self) -> None:
        patterns = suggest(_score_with_time_sig(None))
        assert len(patterns) == 3
        assert all(p.time_signature == "4/4" for p in patterns)

    def test_unknown_time_sig_falls_back_to_four_four(self) -> None:
        patterns = suggest(_score_with_time_sig("5/4"))
        assert all(p.time_signature == "4/4" for p in patterns)

    def test_six_eight_slow_rock_has_rests(self) -> None:
        patterns = suggest(_score_with_time_sig("6/8"))
        assert "-" in patterns[0].strokes

    def test_popular_pattern_has_six_strokes(self) -> None:
        patterns = suggest(_score_with_time_sig("4/4"))
        popular = next(p for p in patterns if p.name == "常見流行刷法")
        assert len(popular.strokes) == 6


class TestBpmRange:
    def test_all_patterns_have_bpm_range(self) -> None:
        for pattern in all_patterns():
            assert hasattr(pattern, "bpm_range")
            lo, hi = pattern.bpm_range
            assert isinstance(lo, int) and isinstance(hi, int)
            assert 0 < lo < hi, f"{pattern.name}: bpm_range {pattern.bpm_range} invalid"

    def test_bpm_range_within_reasonable_bounds(self) -> None:
        for pattern in all_patterns():
            lo, hi = pattern.bpm_range
            assert 30 <= lo <= 300, f"{pattern.name}: lo={lo} out of range"
            assert 30 <= hi <= 300, f"{pattern.name}: hi={hi} out of range"


class TestSuggestForLevel:
    def test_level_1_four_four_returns_only_intro_strum(self) -> None:
        patterns = suggest_for_level(_score_with_time_sig("4/4"), 1)
        assert len(patterns) == 1
        assert patterns[0].name == "入門單刷"

    def test_level_2_four_four_returns_all_three(self) -> None:
        patterns = suggest_for_level(_score_with_time_sig("4/4"), 2)
        assert len(patterns) == 3

    def test_level_1_three_four_returns_waltz(self) -> None:
        patterns = suggest_for_level(_score_with_time_sig("3/4"), 1)
        assert len(patterns) == 1
        assert patterns[0].name == "華爾滋"

    def test_level_1_six_eight_returns_empty(self) -> None:
        patterns = suggest_for_level(_score_with_time_sig("6/8"), 1)
        assert patterns == []

    def test_level_2_six_eight_returns_slow_rock(self) -> None:
        patterns = suggest_for_level(_score_with_time_sig("6/8"), 2)
        assert len(patterns) == 1
        assert patterns[0].name == "慢搖"
