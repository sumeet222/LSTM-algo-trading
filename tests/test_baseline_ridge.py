"""Analytic weighted equations, exact lag dictionary, chronology and synthetic fits."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from lstm_data.baseline_fit import select_and_refit
from lstm_data.baseline_fixtures import ridge_data
from lstm_data.baseline_ridge import (
    PENALTIES,
    adequacy,
    choose_penalty,
    session_weights,
    solve_weighted,
    windows,
)
from lstm_data.p3_domain import MODE, Permission, UniverseSpec


def test_equal_day_not_equal_pooled_origin_and_unpenalized_intercept():
    names = ("ONE", "TWO", "THREE", "FOUR", "FIVE")
    keys = tuple(
        (day, origin, s) for day, origin in (("d1", 1), ("d2", 1), ("d2", 2)) for s in names
    )
    w = session_weights(keys)
    assert w[:5] == pytest.approx([0.1] * 5)
    assert w[5:] == pytest.approx([0.05] * 10)
    x = np.tile(np.array([-2.0, -1.0, 0.0, 1.0, 2.0]), 3)[:, None]
    y = 10 + 2 * x[:, 0]
    s = solve_weighted(x, y, w, 1.0)
    assert s.intercept == pytest.approx(10)
    assert s.coefficients == pytest.approx((4 / 3,))
    assert s.objective == pytest.approx(8 / 3)
    # Augmented independent normal equation penalizes beta only.
    z = np.column_stack([np.ones(15), x])
    expected = np.linalg.solve(z.T @ np.diag(w) @ z + np.diag([0.0, 1.0]), z.T @ np.diag(w) @ y)
    assert [s.intercept, *s.coefficients] == pytest.approx(expected)
    naive = solve_weighted(x, np.repeat([0.0, 1.0, 3.0], 5), np.full(15, 1 / 15), 1.0)
    weighted = solve_weighted(x, np.repeat([0.0, 1.0, 3.0], 5), w, 1.0)
    assert weighted.intercept == pytest.approx(1.0) and naive.intercept == pytest.approx(4 / 3)


def test_exact_tie_larger_penalty_no_near_tie_and_invalid_system():
    assert choose_penalty(tuple((p, 2.0) for p in PENALTIES)) == 1.0
    assert (
        choose_penalty(tuple((p, 1.0 if p == 0.001 else 1.0 + 1e-12) for p in PENALTIES)) == 0.001
    )
    with pytest.raises(ValueError):
        solve_weighted(np.array([[np.nan]]), np.array([1.0]), np.array([1.0]), 1.0)
    with pytest.raises(ValueError):
        solve_weighted(np.array([[1.0]]), np.array([1.0]), np.array([2.0]), 1.0)
    with pytest.raises(ValueError):
        session_weights((("d", 1, "ONE"),))


@pytest.fixture(scope="module")
def data():
    return ridge_data(UniverseSpec("SYN:RIDGE:v1", ("ONE", "TWO", "THREE", "FOUR", "FIVE")))


def test_frozen_selection_chronology_adequacy_tie_one_refit_and_market(data):
    own = select_and_refit(data, "WF1", Permission(MODE), market=False, allow_synthetic=True)
    market = select_and_refit(data, "WF1", Permission(MODE), market=True, allow_synthetic=True)
    assert own.selected_penalty == market.selected_penalty == 1.0
    assert (
        len(own.model.solution.coefficients) == 112
        and len(market.model.solution.coefficients) == 147
    )
    assert own.evidence["candidate_count"] == 5 and own.evidence["refit_count"] == 1
    assert own.evidence["adequacy"]["sessions"] >= 50
    assert own.evidence["validation_keys"] == market.evidence["validation_keys"]
    assert set(own.evidence["fit_keys"]).isdisjoint(own.evidence["validation_keys"])
    assert own.evidence["candidate_scaler"] != own.evidence["refit_scaler"]
    with pytest.raises(ValueError):
        select_and_refit(data, "WF1", Permission(MODE), market=False)
    with pytest.raises(ValueError):
        select_and_refit(
            replace(data, basis="DOCUMENTED"),
            "WF1",
            Permission(MODE),
            market=False,
            allow_synthetic=True,
        )
    with pytest.raises(ValueError):
        adequacy(data.origins[:10])


def test_duplicate_unknown_maturity_purge_frozen_fold_windows(data):
    from lstm_data.baseline_ridge import fitting_origins

    inner, val, full = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))
    with pytest.raises(ValueError, match="DUPLICATE"):
        fitting_origins((data.origins[0],) * 2, data.universe, inner)
    row = data.origins[0]
    crossing = replace(row, label=replace(row.label, maturity=inner.stop))
    accepted, rejected = fitting_origins((crossing,), data.universe, inner)
    assert not accepted and rejected[0][1] == "PURGED_SPLIT_BOUNDARY"
    immature = replace(inner, fitted_at=row.label.maturity - pd.Timedelta(minutes=1))
    accepted, rejected = fitting_origins((row,), data.universe, immature)
    assert not accepted and rejected[0][1] == "NOT_MATURED_BY_FIT"
    assert len({w.stop for w in windows("WF2", pd.Timestamp("2024-01-01T05:00Z"))}) == 2
    assert val.start == inner.stop and full.stop == val.stop


def test_exact112_147_sentinel_columns_and_neutral_masks():
    from lstm_data.baseline_fixtures import feature_input
    from lstm_data.baseline_ridge import LAGS, lag_vectors
    from lstm_data.ft0_transforms import identity
    from lstm_data.market_features import MarketFitWindow, MarketScaler, MarketWindow

    u = UniverseSpec("SYN:ALT", ("FOX", "ZEN", "MAP", "ORB", "TIN"))
    row = feature_input(u)
    scaler = replace(
        row.stock_scaler, centers=(0.0,) * 13, scales=(1.0,) * 13, methods=("MAD",) * 13
    )
    raw = tuple(
        tuple(tuple((i * 1000 + j * 16 + c) / 10000 for c in range(16)) for j in range(48))
        for i in range(5)
    )
    row = replace(
        row,
        stock_scaler=scaler,
        stock=replace(row.stock, raw_values=raw, values=raw, scaler_ref=scaler.certificate_id),
    )
    mw = MarketFitWindow(
        scaler.window.start, scaler.window.stop, scaler.window.fitted_at, "INNER_TRAIN"
    )
    ms = MarketScaler(
        (0.0, 0.0, 0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0, 1.0, 1.0),
        ("MAD", "MAD", "MAD", "MAD", "MAD"),
        mw,
        (mw.start,),
        "SYN:SENTINEL",
    )
    values = tuple(
        (
            j * 5 / 1000,
            (j * 5 + 1) / 1000,
            (j * 5 + 2) / 1000,
            (j * 5 + 3) / 1000,
            (j * 5 + 4) / 1000,
        )
        for j in range(48)
    )
    market = MarketWindow(
        values,
        (True,) * 48,
        "SYNTHETIC",
        (),
        scheduled_ends=tuple(s.end for s in row.stock.steps),
        source_ids=(("SYN:MARKET",),) * 48,
        floor_ref="SYN:FLOOR",
        scaler_ref=identity(ms),
        application_context="ASOF",
        source_ages_seconds=(0.0,) * 48,
    )
    row = replace(row, market=market, market_scaler=ms)
    own = lag_vectors(row, Permission(MODE), allow_synthetic=True)
    both = lag_vectors(row, Permission(MODE), market=True, allow_synthetic=True)
    for i in range(5):
        expected = tuple(
            (i * 1000 + (47 - lag) * 16 + c) / 10000 for lag in LAGS for c in range(16)
        )
        assert own[i] == expected
        assert both[i] == expected + tuple(
            ((47 - lag) * 5 + c) / 1000 for lag in LAGS for c in range(5)
        )
    invalid = replace(row, market=replace(market, valid_mask=(False,) * 3 + (True,) * 45))
    with pytest.raises(ValueError):
        lag_vectors(invalid, Permission(MODE), market=True, allow_synthetic=True)
    missing = replace(
        market,
        values=((0.0,) * 5,) + values[1:],
        valid_mask=(False,) + (True,) * 47,
        source_ids=((),) + market.source_ids[1:],
        source_ages_seconds=(None,) + (0.0,) * 47,
    )
    allowed = lag_vectors(
        replace(row, market=missing), Permission(MODE), market=True, allow_synthetic=True
    )
    assert allowed[0][-5:] == (0.0,) * 5


def test_validation_outlier_never_changes_candidate_scaler(data):
    from lstm_data.baseline_fit import prepare
    from lstm_data.baseline_ridge import fitting_origins

    inner, _, _ = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))
    inner = replace(inner, fitted_at=inner.stop)
    train, _ = fitting_origins(data.origins, data.universe, inner)
    modified = replace(
        data,
        stock_records=tuple(
            replace(r, value=1e20) if r.timestamp >= inner.stop else r for r in data.stock_records
        ),
    )
    first = prepare(
        data, inner, train, market=True, permission=Permission(MODE), allow_synthetic=True
    )
    altered = prepare(
        modified, inner, train, market=True, permission=Permission(MODE), allow_synthetic=True
    )
    assert first.stock_scaler.certificate_id == altered.stock_scaler.certificate_id
    assert first.tg0_floor.floor_id == altered.tg0_floor.floor_id
    assert first.stock_scaler.window.fitted_at == inner.stop


def test_ill_conditioned_system_and_all_frozen_market_candidate_windows():
    from lstm_data.baseline_fit import RidgeMarketFitWindow
    from lstm_data.baseline_ridge import Stage

    with pytest.raises(ValueError, match="ILL_CONDITIONED"):
        solve_weighted(
            np.array([[1e12, 0.0], [-1e12, 0.0]]),
            np.array([1.0, -1.0]),
            np.array([0.5, 0.5]),
            0.0001,
        )
    cases: tuple[tuple[Stage, str], ...] = (
        ("WF1", "2023-07-01T04:00Z"),
        ("WF2", "2024-01-01T05:00Z"),
        ("PRECONFIRMATION", "2024-07-01T04:00Z"),
    )
    for stage, at in cases:
        inner, validation, full = windows(stage, pd.Timestamp(at))
        market = RidgeMarketFitWindow(
            inner.start, inner.stop, inner.fitted_at, "INNER_TRAIN", inner
        )
        assert market.stop == validation.start and market.stop < full.stop
        with pytest.raises(ValueError):
            RidgeMarketFitWindow(
                inner.start,
                inner.stop + pd.Timedelta(days=1),
                inner.fitted_at,
                "INNER_TRAIN",
                inner,
            )


def test_new_asof_market_history_never_refits_or_replaces_conflicting_source(data):
    from lstm_data.baseline_fit import prepare
    from lstm_data.baseline_ridge import fitting_origins
    from lstm_data.market_features import MarketVector

    inner, _, _ = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))
    inner = replace(inner, fitted_at=inner.stop)
    rows, _ = fitting_origins(data.origins, data.universe, inner)
    prep = prepare(
        data, inner, rows, market=True, permission=Permission(MODE), allow_synthetic=True
    )
    at = pd.Timestamp("2023-07-20T14:30Z")
    added = MarketVector(at, (1.0, 2.0, 3.0, 4.0, 5.0), "VECTOR_VALID", ("SYN:ASOF",), "SYNTHETIC")
    extended = prep.with_market_history((added,), Permission(MODE), allow_synthetic=True)
    assert extended.market_scaler is prep.market_scaler and extended.tg0_floor is prep.tg0_floor
    assert prep.market_vectors != extended.market_vectors
    with pytest.raises(ValueError):
        extended.with_market_history(
            (replace(added, values=(2.0, 2.0, 3.0, 4.0, 5.0)),),
            Permission(MODE),
            allow_synthetic=True,
        )
    with pytest.raises(ValueError):
        prep.with_market_history((added,), Permission(MODE))
