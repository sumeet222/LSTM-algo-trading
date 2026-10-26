"""Scientific invariants for the one authorized recent36 alternative."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.hf20_ranking import (
    origin_ic,
    origin_weights,
    rank_targets,
    ridge_solution,
    ridge_system,
)
from lstm_data.hf20_recent_analysis import cohorts, monthly, oracle_ic, origin_panel
from lstm_data.hf20_recent_linear import Attempts, lower_bound


def frame() -> pd.DataFrame:
    r = np.tile(np.arange(20, dtype=float), (3, 1))
    s = r / 20
    days = np.array(["2021-01-04", "2021-01-04", "2021-01-05"])
    return pd.DataFrame(
        dict(
            origin_id=np.repeat(["a", "b", "c"], 20),
            ticker=np.tile([f"S{i}" for i in range(20)], 3),
            session_date_et=np.repeat(days, 20),
            year=2021,
            model="LR",
            role="oos",
            entry_end_utc=np.repeat(
                pd.to_datetime(["2021-01-04T15:30Z", "2021-01-04T16:30Z", "2021-01-05T15:30Z"]), 20
            ),
            return_4h=r.reshape(-1),
            score=s.reshape(-1),
            numerator=(r - 9.5).reshape(-1),
            TG20=((r - 9.5) / 5).reshape(-1),
            mad=5.0,
            epsilon=0.1,
            actual_row_allocation=((s - rank_targets(r)) ** 2 / 20).reshape(-1),
        )
    )


def test_calendar36_and_leap_days():
    assert lower_bound("2020-06-30") == "2017-07-01"
    assert lower_bound("2020-12-31") == "2018-01-01"
    assert lower_bound("2023-12-29") == "2020-12-30"
    assert lower_bound("2024-02-28") == "2021-02-28"


def test_independent_midrank_constants_and_reversal():
    r = np.array([[1, 1, 3, 4], [2, 3, 4, 5], [1, 2, 3, 4]], float)
    s = np.array([[4, 4, 2, 1], [1, 1, 1, 1], [1, 2, 3, 4]], float)
    np.testing.assert_allclose(oracle_ic(r, s), [-1, np.nan, 1], atol=1e-14, equal_nan=True)
    np.testing.assert_allclose(oracle_ic(r, s), origin_ic(r, s), atol=1e-14, equal_nan=True)


def test_months_use_equal_sessions_not_origins():
    p = origin_panel(frame())
    p["ic"] = [1, 1, -1]
    m, _ = monthly(p)
    row = m.loc[m.month.eq("2021-01")].iloc[0]
    assert row.daily_ic == 0
    assert row.origin_ic == pytest.approx(1 / 3)
    assert row.sessions == 2 and row.origins == 3 and row.stock_rows == 60


def test_cohort_point_loss_and_pair_mass_conserve():
    f = frame()
    th = dict(abs_y95=1.5, abs_y99=1.8, num95=8, mad05=4)
    c = cohorts(f, th)
    a = c.loc[c.cohort.eq("ALL")].iloc[0]
    w = np.repeat(origin_weights(f.session_date_et.to_numpy()[::20]) / 20, 20)
    q = rank_targets(f.return_4h.to_numpy().reshape(-1, 20)).reshape(-1)
    assert a.actual_rank_loss_contribution == pytest.approx(w @ ((f.score.to_numpy() - q) ** 2))
    assert a.pair_endpoint_mass == pytest.approx(1)
    assert a.conditional_pair_concordance == pytest.approx(1)
    assert a.normalized_rank_error_contribution == 0


def test_weighted_ridge_penalty_intercept_and_normal_equation():
    rng = np.random.default_rng(42)
    x = np.zeros((3, 20, 768))
    x[:, :, :3] = rng.normal(size=(3, 20, 3))
    r = x[:, :, 0] - x[:, :, 1]
    w = origin_weights(np.array(["a", "a", "b"]))
    gram, rhs = ridge_system(lambda: iter([(x, r, w)]))
    coef = ridge_solution(gram, rhs, 0.1)
    a = np.column_stack([x.reshape(-1, 768), np.ones(60)])
    q = rank_targets(r).reshape(-1)
    gradient = 2 * a.T @ (np.repeat(w / 20, 20) * (a @ coef - q)) + 2 * 0.1 * np.r_[coef[:-1], 0]
    np.testing.assert_allclose(gradient, 0, atol=1e-13)
    shifted = ridge_solution(gram, rhs + gram[:, -1] * 2, 0.1)
    np.testing.assert_allclose(shifted[:-1], coef[:-1], atol=1e-13)
    assert shifted[-1] == pytest.approx(coef[-1] + 2)


def test_attempts_count_failures_and_forbid_retry(tmp_path: Path):
    log = Attempts(tmp_path)
    log.event("a", "STARTED", {})
    log.event("a", "FAILED", {})
    with pytest.raises(ValueError, match="RETRY"):
        log.event("a", "STARTED", {})
    assert len([json.loads(s) for s in log.path.read_text().splitlines()]) == 2
    with pytest.raises(ValueError, match="NO_RESTART"):
        Attempts(tmp_path)
