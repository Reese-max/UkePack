"""Keep the PR #7 research protocol aligned with issue #3's acceptance contract."""

from pathlib import Path


PLAN = Path(__file__).resolve().parent.parent / "docs" / "issue-3-workshop-pack-set.md"


def _section(number: int) -> str:
    text = PLAN.read_text(encoding="utf-8")
    return text.split(f"## {number}.", 1)[1].split("\n## ", 1)[0]


def test_build_requires_all_issue_thresholds_and_a_fallback() -> None:
    decisions = _section(4)
    build = next(line for line in decisions.splitlines() if line.startswith("- ") and "BUILD" in line)
    for requirement in ("median", "≥40%", "4/5", "下一堂課", "child PII", "同時", "≥80%"):
        assert requirement in build, f"BUILD is missing issue #3 requirement: {requirement}"
    for outcome in ("SIMPLIFY", "DO NOT BUILD", "否則"):
        assert outcome in decisions, f"Decision protocol is missing outcome: {outcome}"
    assert "NARROW" not in decisions and "REJECT" not in decisions


def test_protocol_collects_demand_evidence_without_market_extrapolation() -> None:
    methods = _section(3)
    for requirement in ("付費意願", "再次使用", "下一堂課", "原話", "市場規模"):
        assert requirement in methods, f"Missing demand evidence instruction: {requirement}"


def test_protocol_defines_authorization_and_license_boundaries() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    for requirement in (
        "owner_token",
        "唯讀",
        "跨專案",
        "private_research",
        "Private study only. Do not distribute.",
        "Non-commercial practice use",
        "authorization",
        "support",
    ):
        assert requirement in plan, f"Missing research safety boundary: {requirement}"


def test_protocol_observes_each_class_size_level_change_and_errors() -> None:
    methods = _section(3)
    for requirement in ("10、20、30", "臨時換級", "錯配", "漏印", "錯誤數", "三種流程"):
        assert requirement in methods, f"Missing task observation instruction: {requirement}"


def test_protocol_counterbalances_order_and_checks_order_effects_at_the_gate() -> None:
    methods = _section(3)
    rotation = next(line for line in methods.splitlines() if "施測順序" in line)
    for requirement in ("輪替", "每種流程", "首位", "觀察前固定"):
        assert requirement in rotation, f"Order rotation rule is missing: {requirement}"
    observation = next(line for line in methods.splitlines() if "每列觀察記錄" in line)
    assert "順位" in observation, "Observation log must record each task's order position"

    decisions = _section(4)
    assert "≥40% 門檻前必須檢查施測順位" in decisions, (
        "BUILD gate must require an order-effect check before the ≥40% threshold"
    )
    assert "median_current_time - median_pack_set_time" in decisions, (
        "Improvement must be computed from both flow medians"
    )
