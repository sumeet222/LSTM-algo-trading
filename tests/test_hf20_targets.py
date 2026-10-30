"""Five focused target, availability, solver and hierarchical-metric fixtures."""

import numpy as np
import pandas as pd
import pytest

from lstm_data.hf20_ranking import daily_ic, origin_weights, rank_targets, ranks, ridge_solution
from lstm_data.hf20_targets import indicator_scores, past_window, risk_scale, target_standardize
from lstm_data.hf20_targets_report import agreement, signed_metrics


def test_risk_rank_floor_ties_and_tg20():
    r = np.array([[0.01, 0.02, -0.01, -0.02]])
    sigma, valid = risk_scale(np.array([[0.01, 0.1, 0, 0.1]]), np.full(4, 0.005))
    assert valid.all() and sigma[0, 2] == 0.005
    z = r / sigma
    assert ranks(r)[0, 1] > ranks(r)[0, 0] and ranks(z)[0, 1] < ranks(z)[0, 0]
    np.testing.assert_array_equal(np.sign(r), np.sign(z))
    med = np.median(r, axis=1, keepdims=True)
    mad = np.median(abs(r - med), axis=1, keepdims=True)
    np.testing.assert_array_equal(ranks(r), ranks((r - med) / (mad + 1e-4)))
    np.testing.assert_allclose(rank_targets(np.array([[1.0, 1.0, 3.0]])), [[-0.5, -0.5, 1.0]])
    bad, ok = risk_scale(np.array([[0.01, np.nan]]), np.array([0.005, 0.005]))
    assert not ok[0] and np.isnan(bad[0, 1])


def test_immature_history_and_scheduled_gap():
    dates = pd.date_range("2020-01-01", periods=61, freq="B")
    starts = dates.tz_localize("America/New_York") + pd.Timedelta(hours=15, minutes=30)
    ends = starts + pd.Timedelta(hours=21, minutes=30)
    rows = pd.DataFrame(
        dict(
            row_index=np.arange(61),
            regular_session=True,
            context=5,
            session_date_et=dates.strftime("%Y-%m-%d"),
            label_maturity_utc=ends + pd.Timedelta(minutes=2),
        )
    )
    y = np.ones((61, 20)) * 0.02
    past, values, rms, lock = past_window(rows, y, dates[-1].strftime("%Y-%m-%d"), 5)
    assert len(past) == 60 and not np.isfinite(values[-1]).any()
    assert past.label_maturity_utc.iloc[-1] >= lock
    np.testing.assert_allclose(rms, 0.02)
    altered = y.copy()
    altered[-2] = 1e6
    np.testing.assert_array_equal(
        rms, past_window(rows, altered, dates[-1].strftime("%Y-%m-%d"), 5)[2]
    )
    y[-5:-2] = np.nan
    assert np.isnan(past_window(rows, y, dates[-1].strftime("%Y-%m-%d"), 5)[2]).all()


def test_session_weighting_and_hand_origin():
    a = np.tile(np.arange(4), (3, 1))
    s = np.stack([a[0], a[1], -a[2]])
    days = np.array(["a", "a", "b"])
    np.testing.assert_allclose(origin_weights(days), [0.25, 0.25, 0.5])
    assert daily_ic(a, s, days) == pytest.approx(0.0)
    assert daily_ic(a[:1], a[:1], days[:1]) == 1.0
    a20 = np.arange(-10, 10, dtype=float)[None]
    m = signed_metrics(a20, -a20)
    assert m["IC"][0] == -1 and m["pair_concordance"][0] == 0
    assert m["top4"][0] == 0 and m["bottom4"][0] == 0
    assert agreement(a20, -a20)["Kendall_tau_b"][0] == -1
    constant = signed_metrics(a20, np.ones_like(a20))
    assert np.isnan(constant["IC"][0]) and constant["IC_zero"][0] == 0
    assert constant["top4"][0] == pytest.approx(0.2)
    assert constant["pair_concordance"][0] == 0.5


def test_ridge_intercept_penalty_and_target_units():
    # Fit a two-column test in the existing768-input solver, all unused slopes zero.
    x = np.zeros((4, 769))
    x[:, -1] = 1
    x[:, 0] = [-2, -1, 1, 2]
    y = 3 + 2 * x[:, 0]
    w = np.array([0.1, 0.2, 0.3, 0.4])
    gram = x.T @ (w[:, None] * x)
    rhs = x.T @ (w * y)
    coef = ridge_solution(gram, rhs, 1.0)
    centered = x[:, 0] - w @ x[:, 0]
    slope = (w * centered * (y - w @ y)).sum() / ((w * centered**2).sum() + 1.0)
    assert coef[0] == pytest.approx(slope)
    assert coef[-1] == pytest.approx(w @ y - slope * (w @ x[:, 0]))
    targets = np.array([[[0.01, 1.0], [0.02, 2.0]], [[0.03, 3.0], [0.04, 4.0]]])
    standardized, mean, scale = target_standardize(targets, np.array(["a", "b"]))
    np.testing.assert_allclose(standardized * scale + mean, targets)


def test_latest_channel_gather_shape():
    x = np.arange(2 * 20 * 48 * 16).reshape(2, 20, 48, 16)
    latest = x[:, :, -1, [0, 1, 3]]
    assert latest.shape == (2, 20, 3)
    np.testing.assert_array_equal(latest[:, :, 1], x[:, :, -1, 1])
    columns = []
    for first in [(1, 2), (9, 10), (15, 13)]:
        columns.append([*first, *[j for j in range(1, 21) if j not in first]])
    scores, combined = indicator_scores(np.array(columns).T[None])
    assert combined[0, 0] == combined[0, 1]
    np.testing.assert_allclose(combined, scores.mean(axis=-1), atol=1e-15)
