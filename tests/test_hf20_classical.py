"""Deterministic causality, conversion, weighting and minute-RV fixtures."""

import math

import numpy as np
import pandas as pd
import pytest

from lstm_data import hf20_classical as run
from lstm_data import hf20_mag_rank_report as ranking
from lstm_data.hf20_classical_math import (
    deoverlap,
    ewma,
    folded_normal,
    har_features,
    multiplier,
    ridge_fit,
    ridge_predict,
    rv_value,
)


def test_folded_normal_and_ewma() -> None:
    np.testing.assert_allclose(
        folded_normal(np.zeros(3), np.array([0, 1, 4.0])),
        [0, math.sqrt(2 / math.pi), 2 * math.sqrt(2 / math.pi)],
    )
    np.testing.assert_array_equal(folded_normal(np.array([-2, 0, 3.0]), np.zeros(3)), [2, 0, 3])
    np.testing.assert_allclose(
        folded_normal(np.array([-1.0]), np.array([4.0])),
        folded_normal(np.array([1.0]), np.array([4.0])),
    )
    np.testing.assert_allclose(ewma(np.array([1.0]), np.array([4.0])), [1.18])
    with pytest.raises(ValueError):
        folded_normal(np.array([0.0]), np.array([-1.0]))


def test_deoverlap_and_strict_maturity() -> None:
    start = np.array([0, 3, 5, 9, 10])
    end = np.array([5, 4, 8, 12, 13])
    keep = deoverlap(start, end)
    np.testing.assert_array_equal(keep, [True, False, True, True, False])
    assert (end[keep][:-1] <= start[keep][1:]).all()
    np.testing.assert_array_equal(deoverlap(start[:3], end[:3]), keep[:3])
    matured = np.array([5, 8, 12]) + 2
    assert np.searchsorted(matured, 10, side="left") == 1
    assert np.searchsorted(matured, 11, side="left") == 2


def test_rv_adjacency_coverage_and_no_early_close() -> None:
    close = np.exp(np.arange(390) * 0.001)[None, :]
    rv, n = rv_value(close)
    np.testing.assert_allclose(rv, [389e-6], atol=1e-14)
    assert n[0] == 389
    close[0, 100] = np.nan
    rv, n = rv_value(close)
    assert n[0] == 387
    np.testing.assert_allclose(rv, [389e-6], atol=1e-14)
    close[0, 100:140] = np.nan
    assert np.isnan(rv_value(close)[0][0])
    with pytest.raises(ValueError):
        rv_value(close[:, :210])


def test_har_previous_days_fallback_and_ridge() -> None:
    dates = np.array([f"{n:03d}" for n in range(30)])
    rv = np.full((30, 2), 0.01)
    rv[20, 0] = np.nan
    rv[25:] = 1000
    x, missing = har_features(
        rv, dates, np.array(["025"]), np.array([0.02, 0.02]), np.array([1e-12, 1e-12])
    )
    assert x.shape == (1, 2, 6)
    np.testing.assert_allclose(x[0, 1, :3], math.log(0.01))
    np.testing.assert_allclose(x[0, 0, 4], 0.2)
    assert missing[0, 0] == 1 / 22
    rng = np.random.default_rng(2)
    train = rng.normal(size=(40, 3))
    y = 1 + train[:, 0]
    fit = ridge_fit(train, y, np.ones(40))
    z = (train - np.array(fit["center"])) / np.array(fit["scale"])
    beta = np.array(fit["beta"])
    err = beta[0] + z @ beta[1:] - y
    np.testing.assert_allclose(err.mean(), 0, atol=1e-12)
    np.testing.assert_allclose(z.T @ err / 40 + 0.01 * beta[1:], 0, atol=1e-12)
    assert (ridge_predict(train, fit, 0.01) >= 0).all()


def test_calibration_weights_and_ties() -> None:
    # One session with one origin, another with two: not a flat row mean.
    w = run.b.origin_weights(np.array(["a", "b", "b"]))
    np.testing.assert_array_equal(w, [0.5, 0.25, 0.25])
    assert w @ np.array([1.0, 3.0, 5.0]) == 2.5
    a = np.array([1.0, 4.0, 2.0])
    p = np.array([1.0, 2.0, 1.0])
    c = multiplier(a, p, w)
    assert c["k"] == pytest.approx((w * a * p).sum() / (w * p * p).sum())
    with pytest.raises(ValueError):
        multiplier(a, np.zeros(3), w)
    true = np.arange(20, dtype=float)[None, :]
    const = np.ones((1, 20))
    result = ranking.origin_metrics(true, const)
    assert result["IC"][0] == 0 and result["top4"][0] == pytest.approx(0.2)
    assert result["pair_concordance"][0] == 0.5
    np.testing.assert_array_equal(
        pd.DataFrame(true).rank(axis=1), pd.DataFrame(c["k"] * true).rank(axis=1)
    )


def test_dynamic_forecasts_ignore_unmatured_labels() -> None:
    records = []
    for day in pd.date_range("2019-01-01", periods=100, tz="UTC"):
        for slot in run.b.SLOTS:
            hour = int(slot[:2])
            start = day + pd.Timedelta(hours=hour, minutes=30)
            records.append(
                dict(
                    origin_id=str(start),
                    slot=slot,
                    session_date_et=str(day.date()),
                    eligible=True,
                    entry_end_utc=start,
                    exit_end_utc=start + pd.Timedelta(hours=4),
                    issuance_utc=start + pd.Timedelta(minutes=2),
                    label_maturity_utc=start + pd.Timedelta(hours=4, minutes=2),
                )
            )
    rows = pd.DataFrame(records)
    r = np.random.default_rng(4).normal(0, 0.01, (len(rows), 20))
    fit = np.arange(70 * 7)
    q = np.arange(80 * 7, 85 * 7)
    first, _, audit = run.dynamic_forecasts(rows, r, fit, q)
    altered = r.copy()
    altered[85 * 7 :] = 99
    second, _, _ = run.dynamic_forecasts(rows, altered, fit, q)
    for arm in first:
        np.testing.assert_array_equal(first[arm], second[arm])
    assert all(pd.Timestamp(x["latest_maturity"]) < pd.Timestamp(x["issue"]) for x in audit)
    # Independently calculate a first-origin rolling forecast from only mature history.
    n = q[0]
    eligible = rows.slot.eq(rows.iloc[n].slot) & rows.label_maturity_utc.lt(
        rows.iloc[n].issuance_utc
    )
    ix = np.flatnonzero(eligible)
    np.testing.assert_allclose(first["ROLL20"][0], abs(r[ix[-20:]]).mean(0), atol=1e-15)
