"""P028 source-only preparation math, no fills, source scope and episode support."""

import numpy as np
import pandas as pd
import pytest

from lstm_data.panel_state_audit import CHANNELS, construct, episodes, guard, support


def test_two_exact_inclusive_proxies_and_independent_time_axis():
    x = np.arange(3 * 20 * 2, dtype=np.float32).reshape(3, 20, 2)
    result = construct(x)
    expected = np.array(
        [
            [
                sum(float(v) for v in row[:, 0]) / 20,
                (sorted(row[:, 1])[9] + sorted(row[:, 1])[10]) / 2,
            ]
            for row in x
        ],
        dtype=np.float32,
    )
    np.testing.assert_array_equal(result, expected)
    changed = x.copy()
    changed[1, 0, 0] += 20
    np.testing.assert_array_equal(construct(changed)[[0, 2]], result[[0, 2]])
    assert construct(changed)[1, 0] == result[1, 0] + 1
    np.testing.assert_array_equal(construct(x[:, ::-1]), result)
    assert result.shape == (3, 2) and CHANNELS == ("mean20_scaled_M1", "median20_scaled_V1")


@pytest.mark.parametrize(
    "bad",
    [
        np.zeros((2, 19, 2), dtype=np.float32),
        np.zeros((2, 20, 3), dtype=np.float32),
        np.zeros((2, 20, 2), dtype=np.float64),
        np.full((2, 20, 2), np.nan, dtype=np.float32),
    ],
)
def test_no_dynamic_universe_new_channel_or_fallback(bad):
    with pytest.raises(ValueError):
        construct(bad)


@pytest.mark.parametrize(
    "role,stop",
    [
        ("confirmation", "2025-12-31"),
        ("development", "2026-01-01"),
        ("refit", "2025-13-01"),
        ("", "2025-12-31"),
    ],
)
def test_protected_unknown_malformed_scope_before_file_lookup(role, stop, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("scope validation attempted numeric lookup")

    monkeypatch.setattr(pd, "read_parquet", forbidden)
    with pytest.raises(ValueError):
        guard(role, stop)


def test_one_long_run_is_not_multiple_independent_episodes_and_gaps_break_runs():
    days = [f"2025-01-{i:02}" for i in range(1, 22)]
    runs = episodes(days, np.zeros(21, dtype=bool), days)
    assert len(runs) == 1 and runs[0]["sessions"] == 21
    missing = days[:7] + days[8:]
    runs = episodes(missing, np.zeros(20, dtype=bool), days)
    assert [r["sessions"] for r in runs] == [7, 13]


def test_frozen_threshold_ties_and_insufficient_exposure_are_honest():
    days = [f"2025-01-{i:02}" for i in range(1, 22)]
    daily = pd.DataFrame(dict(session_date_et=days, median20_scaled_V1=np.zeros(21)))
    r = support(daily, 0.0, days, "inner_validation")
    assert r["states"]["LOW"]["sessions"] == 21
    assert r["states"]["HIGH"]["sessions"] == 0
    assert not r["passes_proposed_support_policy"] and not r["policy_is_approved"]
    daily["median20_scaled_V1"] = 10.0
    assert support(daily, 0.0, days, "development")["threshold"] == 0.0
    assert (
        support(daily, 0.0, days, "development")["activation_use"]
        == "DESCRIPTIVE_ONLY_NOT_A12_ACTIVATION"
    )
