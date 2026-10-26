"""Small S3 source/clock/M2 counterfactual oracles; no fitted market model."""

import numpy as np
import pandas as pd
import pytest

from lstm_data.hf20_horizon_math import (
    endpoints,
    historical_m2,
    horizon_roles,
    m2_parameters,
    returns_at,
    scale_m2,
    substitute_m2,
    target_parameters,
    target_support,
)
from lstm_data.hf20_horizon_preflight import proposed_runs
from lstm_data.hf20_ranking import ranks


def fixture(days: int = 90) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    dates = pd.bdate_range("2020-01-02", periods=days)
    records = []
    for date in dates:
        for slot in range(6):
            end = (
                pd.Timestamp(date.date(), tz="America/New_York")
                + pd.Timedelta(hours=10, minutes=30)
                + pd.Timedelta(hours=slot)
            )
            records.append(
                dict(
                    session_date_et=str(date.date()),
                    hour_end_utc=end.tz_convert("UTC"),
                    hour_start_utc=(end - pd.Timedelta(hours=1)).tz_convert("UTC"),
                )
            )
    grid = pd.DataFrame(records)
    rng = np.random.default_rng(42)
    close = np.exp(rng.normal(0, 0.01, size=(len(grid), 20)).cumsum(0)) + 10
    return (
        grid,
        close,
        np.full(close.shape, "SAME_BASIS", dtype=object),
        np.zeros(close.shape, bool),
    )


def test_endpoints_dst_weekend_early_close_and_stub():
    grid, close, basis, _ = fixture()
    entry = np.array([0, 1, 6, 7])
    np.testing.assert_array_equal(endpoints(grid, entry, 4), entry + 4)
    assert target_support(grid, entry, np.ones_like(close, bool), basis, 2).all()
    with pytest.raises(ValueError, match="OVERNIGHT"):
        endpoints(grid, np.array([5]), 1)
    early = grid.iloc[:3].copy()
    with pytest.raises(ValueError, match="OUTSIDE"):
        endpoints(early, np.array([0]), 4)
    stub = grid.copy()
    stub["is_stub"] = False
    stub.loc[2, "is_stub"] = True
    with pytest.raises(ValueError, match="FULL_HOURS"):
        endpoints(stub, np.array([0]), 1)
    # Actual spring DST weekend dates, with one-hour completed bars on both days.
    e = pd.to_datetime(
        ["2020-03-06T15:30Z", "2020-03-06T16:30Z", "2020-03-09T14:30Z", "2020-03-09T15:30Z"]
    )
    g = pd.DataFrame(dict(session_date_et=["2020-03-06"] * 2 + ["2020-03-09"] * 2, hour_end_utc=e))
    np.testing.assert_array_equal(endpoints(g, np.array([0, 2]), 1), [1, 3])
    with pytest.raises(ValueError, match="OVERNIGHT"):
        endpoints(g, np.array([1]), 1)


def test_target_math_and_source_only_support():
    g, c, b, _ = fixture()
    entry = np.array([0, 1])
    ex = endpoints(g, entry, 2)
    r = returns_at(c, entry, ex)
    np.testing.assert_array_equal(r, np.log(c[ex] / c[entry]))
    med = np.median(r, axis=1)
    y = (r - med[:, None]) / (np.median(abs(r - med[:, None]), axis=1)[:, None] + 0.001)
    np.testing.assert_array_equal(ranks(r), ranks(y))
    np.testing.assert_array_equal(ranks(r), ranks(np.arcsinh(y / 0.5)))
    genuine = np.ones_like(c, bool)
    genuine[ex[0], 3] = False
    assert not target_support(g, entry, genuine, b, 2)[0, 3]
    b[ex[1], 5] = "BAD"
    assert not target_support(g, entry, genuine, b, 2)[1, 5]


@pytest.mark.parametrize("horizon", [1, 2, 4])
def test_m2_prior_day_and_independent_mean_rms(horizon: int):
    g, c, b, blocked = fixture()
    mean, rms, ref, past = historical_m2(g, c, b, blocked, horizon)
    day = 75
    step = day * 6
    for slot in (0, 1):
        expected = []
        for d in range(day - 60, day):
            expected.append(np.log(c[d * 6 + slot + horizon, 0] / c[d * 6 + slot, 0]))
        v = np.array(expected)
        assert mean[step, 0, slot] == pytest.approx(v[-20:].mean())
        assert rms[step, 0, slot] == pytest.approx(np.sqrt(np.mean(v * v)))
        assert rms[step, 0, slot] != pytest.approx(np.std(v), rel=1e-8, abs=0)
    assert ref[step] == step - 1
    changed = c.copy()
    changed[step + 1 :] *= 1.7
    after = historical_m2(g, changed, b, blocked, horizon)
    np.testing.assert_array_equal(mean[: step + 6], after[0][: step + 6])
    np.testing.assert_array_equal(rms[: step + 6], after[1][: step + 6])
    assert np.isfinite(past[-1]).all()


def test_m2_fixed_scheduled_windows_missing_run_and_block():
    g, c, b, blocked = fixture()
    c[30 * 6 : 33 * 6] = np.nan
    mean, rms, _, _ = historical_m2(g, c, b, blocked, 1)
    assert np.isfinite(mean[80 * 6, 0]).all()
    assert np.isnan(rms[80 * 6, 0]).all()  # 57/60 alone is insufficient: three consecutive misses.
    blocked[81 * 6, 0] = True
    mean, rms, _, _ = historical_m2(g, c, b, blocked, 1)
    assert np.isnan(mean[81 * 6, 0]).all() and np.isnan(rms[81 * 6, 0]).all()


def test_synthetic_only_normalizers_and_other15_identity():
    rng = np.random.default_rng(42)
    mean = rng.normal(size=(80, 20, 2))
    rms = abs(rng.normal(size=(80, 20, 2))) + 0.1
    floor, scale, scaled = m2_parameters(mean, rms, np.arange(60))
    np.testing.assert_array_equal(scaled, scale_m2(mean, rms, floor, scale))
    assert np.isfinite(scaled).all() and floor.shape == (20,)
    rows = pd.DataFrame(
        dict(
            first_step=[0, 1],
            entry_end_utc=pd.to_datetime(["2020-01-02T15:30Z", "2020-01-02T16:30Z"]),
        )
    )
    x = rng.normal(size=(2, 20, 48, 16)).astype(np.float32)
    result = substitute_m2(x, rows, scaled)
    np.testing.assert_array_equal(
        result[..., [j for j in range(16) if j != 1]], x[..., [j for j in range(16) if j != 1]]
    )
    r = rng.normal(size=(80, 20))
    mask = np.arange(80) < 60
    p = target_parameters(r, mask, mask)
    r[60:] *= 100
    assert p == target_parameters(r, mask, mask)


def test_budget_and_protected_or_unknown_horizon_fail_closed():
    runs = proposed_runs()
    assert len(runs) == len(set(runs)) == 32
    assert all("S3A" in r for r in runs[:16]) and all("S3B" in r for r in runs[16:])
    g, _, _, _ = fixture()
    with pytest.raises(ValueError, match="ONLY_DECLARED"):
        endpoints(g, np.array([0]), 3)
    g["session_date_et"] = "2026-01-02"
    with pytest.raises(ValueError, match="POST2024"):
        endpoints(g, np.array([0]), 1)


def test_amended_horizon_membership_does_not_require_four_hour_prices():
    grid = pd.DataFrame(dict(session_date_et=["2020-06-01", "2020-07-01", "2021-01-04"]))
    rows = pd.DataFrame(
        dict(
            session_date_et=["2020-06-30", "2020-07-20", "2021-01-20"],
            first_step=[0, 1, 2],
            source_input_eligible=True,
            label_maturity_utc=pd.to_datetime(
                ["2020-06-30T19:32Z", "2020-07-20T19:32Z", "2021-01-20T20:32Z"]
            ),
        )
    )
    plan = dict(
        year=2021, inner_stop="2020-06-30", selection_start="2020-07-01", refit_stop="2020-12-31"
    )
    h1 = horizon_roles(rows, grid, plan, np.array([True, True, True]))
    h4 = horizon_roles(rows, grid, plan, np.array([False, True, True]))
    assert h1["inner_train"][0] and not h4["inner_train"][0]
    assert h1["inner_validation"][1] and h1["oos"][2]
    assert not (h1["inner_train"] & h1["inner_validation"]).any()
    assert not (h1["refit"] & h1["oos"]).any()
    b = horizon_roles(rows.copy(), grid, plan, np.ones(3, bool))
    for role in h1:
        np.testing.assert_array_equal(h1[role], b[role])
    rows.loc[0, "label_maturity_utc"] = pd.Timestamp("2020-07-01T04:00Z")
    with pytest.raises(ValueError, match="CONSERVATIVE"):
        horizon_roles(rows, grid, plan, np.ones(3, bool))
