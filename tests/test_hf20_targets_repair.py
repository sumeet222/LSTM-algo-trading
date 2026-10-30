"""Targeted causal-history and population-separation fixtures for the repair."""

import numpy as np
import pandas as pd

from lstm_data.hf20_targets import risk_scale
from lstm_data.hf20_targets_repair import histories, positions, risk_history, window_bounds


def fixture():
    days = pd.bdate_range("2019-01-01", periods=282, tz="America/New_York")
    records = []
    for k, day in enumerate(days[:-1]):
        for clock, context in [(9.5, 6), (15.5, 5)]:
            start = day + pd.Timedelta(hours=clock)
            end = (
                day + pd.Timedelta(hours=13.5)
                if context == 6
                else days[k + 1] + pd.Timedelta(hours=13)
            )
            records.append(
                dict(
                    origin_id=start.isoformat(),
                    entry_end_utc=start,
                    exit_end_utc=end,
                    issuance_utc=start + pd.Timedelta(minutes=2),
                    label_maturity_utc=end + pd.Timedelta(minutes=2),
                    session_date_et=day.strftime("%Y-%m-%d"),
                    regular_session=True,
                    context=context,
                )
            )
    return pd.DataFrame(records), np.full((len(records), 3), 0.01)


def test_causal_valid_windows_missing_and_252_expiry():
    dates = np.array(["2020-01-01"])
    current = np.array(["2020-01-02"])
    assert window_bounds(dates, np.array([10]), current, np.array([10]), dates)[1][0] == 1
    assert window_bounds(dates, np.array([10]), current, np.array([9]), dates)[1][0] == 0
    rows, r = fixture()
    r[::13, 1] = np.nan
    i = len(rows) - 2  # Morning: previous afternoon endpoint has not matured.
    result = risk_history(rows, r)
    same, pool = histories(rows, r, i, 1)
    assert i - 1 not in pool and i not in pool and len(pool) == 200
    assert len(same) == 60
    expected = np.sqrt((np.sum(r[same, 1] ** 2) + 20 * np.mean(r[pool, 1] ** 2)) / (len(same) + 20))
    np.testing.assert_allclose(result["rms"][i, 1], expected)
    assert result["missing_same_252"][i, 1] > 0
    changed = r.copy()
    changed[i - 1 :] = 10  # Immature prior interval and current/future target cannot enter.
    np.testing.assert_array_equal(risk_history(rows, changed)["rms"][i], result["rms"][i])
    changed[:20] = 10  # Outside252-session lookback; prefix subtraction has roundoff.
    assert min(same.min(), pool.min()) >= 20
    np.testing.assert_allclose(
        risk_history(rows, changed)["rms"][i], result["rms"][i], rtol=0, atol=2e-12
    )
    assert np.isnan(result["rms"][0]).all()  # No fabricated warmup scale.


def test_pool_fallback_floor_and_return_units():
    rows, r = fixture()
    i = len(rows) - 2
    rows.loc[i, "context"] = 0  # Previously unobserved clock: pooled fallback only.
    result = risk_history(rows, r)
    assert (result["n_same"][i] == 0).all() and (result["n_all"][i] == 200).all()
    np.testing.assert_allclose(result["rms"][i], 0.01)
    sigma, valid = risk_scale(result["rms"], np.full(3, 0.02))
    assert valid[i] and (sigma[i] == 0.02).all()
    bigger = risk_history(rows, 100 * r)
    np.testing.assert_allclose(bigger["rms"][i], 100 * result["rms"][i])
    np.testing.assert_allclose(r[i] / result["rms"][i], (100 * r[i]) / bigger["rms"][i])


def test_raw_keys_independent_of_risk_completeness():
    role = np.array([2, 4, 6])
    sigma = np.ones((8, 20))
    sigma[4, 3] = np.nan
    np.testing.assert_array_equal(positions(role), role)
    np.testing.assert_array_equal(positions(role, sigma), [2, 6])
