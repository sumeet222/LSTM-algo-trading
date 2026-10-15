"""Small G6 regressions; no training or historical artifact regeneration."""

import pytest

from lstm_data.neural_health import g6_summary


def trace(*, warning: bool = False, nonfinite: int = 0) -> tuple[dict, ...]:
    return (
        {
            "epoch": 1,
            "gradients": {
                "nonfinite_count": nonfinite,
                "sustained_clipping_warning": warning,
            },
        },
    )


def test_calibration_only_warning_is_not_lost():
    result = g6_summary(trace(warning=True), trace(), 0.1, "PATIENCE_STOP")
    assert result["status"] == "WARN_INVESTIGATE"
    assert result["warning_epochs"] == {"calibration": [1], "refit": []}


def test_clean_both_passes_pass():
    assert g6_summary(trace(), trace(), 0.1, "PATIENCE_STOP")["status"] == "PASS_PER_RUN_TELEMETRY"


def test_refit_warning_is_preserved():
    result = g6_summary(trace(), trace(warning=True), 0.1, "PATIENCE_STOP")
    assert result["status"] == "WARN_INVESTIGATE"
    assert result["warning_epochs"]["refit"] == [1]


def test_nonfinite_fails_and_missing_pass_is_rejected():
    assert (
        g6_summary(trace(nonfinite=1), trace(), 0.1, "PATIENCE_STOP")["status"]
        == "FAIL_NONFINITE_TELEMETRY"
    )
    with pytest.raises(ValueError, match="BOTH_PASS"):
        g6_summary((), trace(), 0.1, "PATIENCE_STOP")
