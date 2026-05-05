"""Regression tests for corpus E2E artifact update policy."""

from __future__ import annotations

import pytest

from tests.test_corpus_e2e_pdf import UPDATE_ARTIFACTS_ENV, _should_update_e2e_artifacts


def test_e2e_artifact_updates_default_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(UPDATE_ARTIFACTS_ENV, raising=False)

    assert _should_update_e2e_artifacts() is False


@pytest.mark.parametrize("value", ["1", "true", "TRUE", " yes ", "On"])
def test_e2e_artifact_updates_accept_truthy_values(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setenv(UPDATE_ARTIFACTS_ENV, value)

    assert _should_update_e2e_artifacts() is True
