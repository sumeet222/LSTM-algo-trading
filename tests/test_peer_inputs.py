"""Independent leave-one-out, causal adapter and matched regression integration tests."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.baseline_fit import prepare
from lstm_data.baseline_ridge import LAGS, PENALTIES, fitting_origins, lag_vectors
from lstm_data.ft0_transforms import identity
from lstm_data.neural_market import market_input
from lstm_data.p3_domain import Permission
from lstm_data.peer_inputs import (
    M1_INDEX,
    make_peer_view,
    peer_input,
    peer_lag_vectors,
    peer_summaries,
)
from lstm_data.peer_ridge import matched_peer_ridge
from lstm_data.regime_diagnostics import classify, diagnostic_window, training_threshold


def direct(values):
    output = []
    for target in range(5):
        pairs = []
        for step in range(48):
            z = [float(values[i, step, M1_INDEX]) for i in range(5) if i != target]
            mean = sum(z) / 4
            pairs.append((mean, (sum((v - mean) ** 2 for v in z) / 4) ** 0.5))
        output.append(pairs)
    return np.asarray(output)


def sentinel():
    values = np.zeros((5, 48, 16))
    for i in range(5):
        values[i, :, M1_INDEX] = i + 1
    return values


def test_all_five_arithmetic_population_divisor_and_all_equal():
    values = sentinel()
    pairs = peer_summaries(values)
    np.testing.assert_allclose(pairs, direct(values), rtol=0, atol=0)
    np.testing.assert_allclose(
        pairs[[0, 2, 4], 0], [(3.5, 1.25**0.5), (3.0, 2.5**0.5), (2.5, 1.25**0.5)]
    )
    assert np.array_equal(peer_summaries(np.ones((5, 48, 16)))[..., 1], np.zeros((5, 48)))
    # Centered differences remain stable even with a large common offset.
    np.testing.assert_allclose(peer_summaries(values + 1e12)[..., 1], pairs[..., 1])


def test_permutation_and_own_exclusion_perturbation_and_common_rank_counterexample():
    values = sentinel()
    base = peer_summaries(values)
    order = [4, 0, 3, 1, 2]
    np.testing.assert_allclose(peer_summaries(values[order]), base[order])
    changed = values.copy()
    changed[2, :, M1_INDEX] += 10
    output = peer_summaries(changed)
    assert np.array_equal(output[2], base[2])
    assert all(not np.array_equal(output[i], base[i]) for i in (0, 1, 3, 4))
    z = values[:, 0, M1_INDEX]
    # Common sum term leaves ranks alone, despite apparent added peer access.
    assert np.array_equal(np.argsort(z), np.argsort(z + sum(z) / 4))
    assert base[0, 0, 1] != base[2, 0, 1]  # dispersion isn't a shared additive constant.
    for bad in (values[:4], np.full_like(values, np.nan), values[:, :47]):
        with pytest.raises(ValueError):
            peer_summaries(bad)


@pytest.fixture(scope="module")
def case():
    from lstm_data.regime_peer_audit import fabricated_case

    return fabricated_case()


def test_canonical_clock_source_fit_provenance_and_regime_threshold(case):
    data, history, prep, _, permission = case
    row = data.origins[-1].inputs
    processed, peers, trace = peer_input(row, prep, history, permission)
    expected = np.asarray(processed.stock.values, dtype=float)
    np.testing.assert_allclose(peers, direct(expected))
    assert trace and processed.stock.scaler_ref == prep.stock_scaler.certificate_id
    assert prep.market_scaler is not None
    threshold = training_threshold(history, prep.market_scaler, permission)
    assert threshold.value == 0
    diagnostic = diagnostic_window(row, prep, history, permission, phase="TRAINING")
    state = classify(diagnostic, threshold)
    assert state.trend == "NEUTRAL" and state.volatility == "LOW"
    mutated = replace(
        history, stamps=(replace(history.stamps[0], available_at=pd.NaT),) + history.stamps[1:]
    )
    with pytest.raises(ValueError):
        peer_input(row, prep, mutated, permission)
    with pytest.raises(ValueError):
        training_threshold(history, prep.market_scaler, Permission("SCIENTIFIC_REAL"))


@pytest.mark.parametrize(
    "fault", ["order", "unknown", "nat", "future", "mask", "source", "scaler", "market", "grid"]
)
def test_required_peer_and_source_negatives(case, fault):
    data, history, prep, _, permission = case
    row = data.origins[-1].inputs
    if fault in {"unknown", "nat", "future"}:
        at = (
            None
            if fault == "unknown"
            else pd.NaT
            if fault == "nat"
            else row.stock.steps[0].end + pd.Timedelta(nanoseconds=1)
        )
        clocks = list(row.available_at)
        stock = list(clocks[1])
        cell = list(stock[0])
        cell[M1_INDEX] = at
        stock[0] = tuple(cell)
        clocks[1] = tuple(stock)
        row = replace(row, available_at=tuple(clocks))
    elif fault == "order":
        row = replace(row, universe=replace(row.universe, symbols=row.universe.symbols[::-1]))
    elif fault == "mask":
        masks = list(row.stock.mask)
        stock = list(masks[2])
        cell = list(stock[0])
        cell[M1_INDEX] = False
        stock[0] = tuple(cell)
        masks[2] = tuple(stock)
        row = replace(row, stock=replace(row.stock, mask=tuple(masks)))
    elif fault == "source":
        row = replace(row, stock=replace(row.stock, source_binding="SYN:OTHER"))
    elif fault == "scaler":
        prep = replace(prep, stock_scaler=replace(prep.stock_scaler, source_binding="f" * 64))
    elif fault == "market":
        t = row.stock.steps[-1].end
        vectors = tuple(
            replace(v, values=None, reason="MISSING_SPY_SOURCE", evidence_ids=())
            if v.timestamp == t
            else v
            for v in history.vectors
        )
        stamps = tuple(
            replace(s, available_at=None, period_end=None, evidence_ids=())
            if s.timestamp == t
            else s
            for s in history.stamps
        )
        history = replace(history, vectors=vectors, stamps=stamps)
        prep = replace(prep, market_vectors=vectors)
    else:
        steps = (
            replace(row.stock.steps[0], end=row.stock.steps[0].end + pd.Timedelta(hours=1)),
        ) + row.stock.steps[1:]
        row = replace(row, stock=replace(row.stock, steps=steps))
    with pytest.raises(ValueError):
        peer_input(row, prep, history, permission)


def test_all_seven_147_prefix_161_peer_sentinel_columns(case):
    data, history, prep, _, permission = case
    row = data.origins[-1].inputs
    # vary M1 by scheduled position; regenerate canonical values through P2 prep.
    raw = tuple(
        tuple(
            tuple((i + 1) * 100 + s if c == M1_INDEX else v for c, v in enumerate(step))
            for s, step in enumerate(stock)
        )
        for i, stock in enumerate(row.stock.raw_values)
    )
    row = replace(row, stock=replace(row.stock, raw_values=raw))
    processed, _ = market_input(row, prep, history, permission)
    baseline = np.asarray(lag_vectors(processed, permission, market=True, allow_synthetic=True))
    joined = np.asarray(peer_lag_vectors(row, prep, history, permission))
    assert joined.shape == (5, 161) and np.array_equal(joined[:, :147], baseline)
    expected = direct(np.asarray(processed.stock.values, dtype=float))
    for slot, lag in enumerate(LAGS):
        for stock in range(5):
            assert joined[stock, 147 + 2 * slot : 149 + 2 * slot] == pytest.approx(
                expected[stock, 47 - lag]
            )
    assert [47 - lag for lag in LAGS] == [47, 46, 45, 42, 36, 24, 0]


def test_ephemeral23_indexed_view_mutation_order_no_model(case):
    data, history, prep, val, permission = case
    small = replace(data, origins=data.origins[-2:])
    view = make_peer_view(small, val, prep, permission, history, allow_synthetic=True)
    batch = view.batch((0,))
    assert batch.inputs.shape == (1, 2, 5, 48, 23)
    assert torch.equal(batch.inputs[..., :21], batch.base.inputs)
    for origin in range(2):
        peers = direct(batch.base.inputs[0, origin, :, :, :16].numpy())
        np.testing.assert_allclose(batch.inputs[0, origin, :, :, 21:].numpy(), peers, rtol=1e-6)
    with pytest.raises(ValueError):
        replace(view, universe=replace(view.universe, symbols=view.universe.symbols[::-1])).batch(
            (0,)
        )
    forged = batch.inputs.clone()
    forged[0, 0, 0, 0, 21] += 1
    with pytest.raises(ValueError, match="CANONICAL_FOUR_PEER"):
        replace(batch, inputs=forged)
    from lstm_data.neural_models import create_model

    # P4.8 now explicitly authorizes the 23-channel synthetic model; LL neural stays closed.
    assert create_model("E5").input_dim == 23
    with pytest.raises(ValueError):
        create_model("LL1")
    view.market.values[0, 0] += 1
    with pytest.raises(ValueError, match="MUTATED"):
        view.batch((0,))


def test_validation_outlier_cannot_change_inner_training_fit(case):
    data, _, prep, val, permission = case
    outlier = replace(
        data,
        stock_records=tuple(
            replace(r, value=1e9) if r.timestamp >= val.start else r for r in data.stock_records
        ),
    )
    train, _ = fitting_origins(data.origins, data.universe, prep.window)
    fresh = prepare(
        outlier, prep.window, train, market=True, permission=permission, allow_synthetic=True
    )
    assert identity(fresh.stock_scaler) == identity(prep.stock_scaler)
    assert identity(fresh.tg0_floor) == identity(prep.tg0_floor)


def test_matched_fabricated_ridge_uses_original_selection_and_one_refit(case):
    data, history, _, _, permission = case
    control, peer, evidence = matched_peer_ridge(
        data, "WF1", history, permission, allow_synthetic=True
    )
    assert len(control.solution.coefficients) == 147 and len(peer.solution.coefficients) == 161
    for fit in (control, peer):
        assert tuple(c["penalty"] for c in fit.candidates) == PENALTIES
        assert fit.evidence["candidate_count"] == 5 and fit.evidence["refit_count"] == 1
        assert fit.evidence["adequacy"]["sessions"] >= 50
        assert fit.evidence["candidate_scaler"] != fit.evidence["refit_scaler"]
        assert set(fit.evidence["fit_keys"]).isdisjoint(fit.evidence["validation_keys"])
    assert control.evidence["validation_keys"] == peer.evidence["validation_keys"]
    assert control.evidence["effective_train_weights"] == peer.evidence["effective_train_weights"]
    assert (
        evidence["neural_pairs"] == 0 and evidence["scientific_status"] == "NOT_ASSESSED_SCIENTIFIC"
    )
    with pytest.raises(ValueError):
        matched_peer_ridge(data, "WF1", history, permission)


def test_consistently_reordered_typed_source_is_equivariant(case):
    data, history, prep, _, permission = case
    row = data.origins[-1].inputs
    _, expected, old = peer_input(row, prep, history, permission)
    order = (4, 0, 3, 1, 2)
    universe = replace(row.universe, symbols=tuple(row.universe.symbols[i] for i in order))
    fields = {
        name: tuple(getattr(row.stock, name)[i] for i in order)
        for name in ("values", "raw_values", "mask", "lineage")
    }
    swapped = replace(
        row,
        universe=universe,
        stock=replace(row.stock, symbols=universe.symbols, **fields),
        available_at=tuple(row.available_at[i] for i in order),
    )
    _, observed, new = peer_input(swapped, replace(prep, universe=universe), history, permission)
    np.testing.assert_allclose(observed, expected[list(order)])
    assert new != old


def test_source_value_clock_and_version_change_invalidates_peer_evidence(case):
    data, history, prep, _, permission = case
    row = data.origins[-1].inputs
    _, _, before = peer_input(row, prep, history, permission)
    clocks = list(row.available_at)
    stock = list(clocks[0])
    cell = list(stock[0])
    # A past daily-state dependency can legitimately have an earlier publication.
    from lstm_data.ft0_transforms import ORDER

    index = ORDER.index("T3")
    assert cell[index] is not None
    cell[index] -= pd.Timedelta(minutes=1)
    stock[0] = tuple(cell)
    clocks[0] = tuple(stock)
    _, _, clock_id = peer_input(replace(row, available_at=tuple(clocks)), prep, history, permission)
    raw = list(row.stock.raw_values)
    stock = list(raw[0])
    cell = list(stock[0])
    assert cell[M1_INDEX] is not None
    cell[M1_INDEX] += 0.01
    stock[0] = tuple(cell)
    raw[0] = tuple(stock)
    _, _, value_id = peer_input(
        replace(row, stock=replace(row.stock, raw_values=tuple(raw))), prep, history, permission
    )
    _, _, version_id = peer_input(
        row, prep, replace(history, version="SYN:NEW_VERSION"), permission
    )
    assert len({before, clock_id, value_id, version_id}) == 4


def test_regime_code_identity_and_optional_existing_gate_summary(case, monkeypatch):
    import lstm_data.regime_diagnostics as diagnostics
    from lstm_data.regime_diagnostics import PairedRecord, paired_report

    data, history, prep, _, permission = case
    row = data.origins[-1].inputs
    assert prep.market_scaler is not None
    threshold = training_threshold(history, prep.market_scaler, permission)
    window = diagnostic_window(row, prep, history, permission, phase="TRAINING")
    state = classify(window, threshold)
    assert state.cutoff is not None
    t = state.cutoff
    a = PairedRecord(
        "MC0",
        state,
        (0.0,) * 5,
        (1.0,) * 5,
        "SYN:S",
        "SYN:Y",
        "SYN:F",
        t - pd.Timedelta(days=1),
        t,
        t + pd.Timedelta(minutes=2),
        t + pd.Timedelta(hours=4),
        t + pd.Timedelta(hours=5),
    )
    b = replace(a, architecture="MC1", scores=(1.0,) * 5, gate_weights=(1.0,) * 16)
    result = paired_report((a, b))
    assert result["gate_summary"]["sum16_max_error"] == 0
    assert result["gate_summary"]["constant_gate_warning"]
    old_window, old_threshold = window.window_id, threshold.threshold_id
    monkeypatch.setattr(diagnostics, "diagnostic_code_identity", lambda: "SYN:CHANGED_CODE")
    assert window.window_id != old_window and threshold.threshold_id != old_threshold
