"""Independent once-flag, calendar, preprocessing and matched-fit oracles."""

from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.baseline_fit import prepare
from lstm_data.baseline_ridge import (
    LAGS,
    PENALTIES,
    choose_penalty,
    fitting_origins,
    lag_vectors,
    session_weights,
    solve_weighted,
    windows,
)
from lstm_data.config import write_json
from lstm_data.directed_peers import directed_ridge_fit
from lstm_data.directed_ridge import DECISION_SHA, MatchedDesign, approved_decision, extension
from lstm_data.directed_ridge_audit import column_names, run_case
from lstm_data.directed_ridge_fixture import fixture
from lstm_data.e5_health_diagnosis import diagnose
from lstm_data.ft0_transforms import identity
from lstm_data.m2 import ScheduledCalendar
from lstm_data.p3_domain import Permission, UniverseSpec
from lstm_data.p3_events import json_value
from lstm_data.peer_inputs import peer_lag_vectors

DECISION = Path("docs/track_a/decisions/D8_RIDGE_FLAGS_ONCE_v1_2026-10-13.json")


@pytest.fixture(scope="module")
def prepared():
    data, history, archive, pair, permission = fixture("FORWARD")
    inner, validation, _ = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))
    inner = replace(inner, fitted_at=inner.stop)
    rows, _ = fitting_origins(data.origins, data.universe, inner)
    prep = prepare(data, inner, rows, market=True, permission=permission, allow_synthetic=True)
    calendar = ScheduledCalendar("2020-07-01", "2023-06-30")
    design = MatchedDesign(archive, history, pair, calendar, approved_decision(DECISION))
    return data, history, archive, pair, permission, prep, calendar, design, validation


def test_163_198_exact_161_prefix_flags_once_sentinel_lag_order(prepared):
    data, history, _, _, permission, prep, calendar, design, _ = prepared
    row = data.origins[-2].inputs
    window, sham, _ = design.prepare(row, prep, permission, "ASOF")
    prefix = np.asarray(
        lag_vectors(window.processed, permission, market=True, allow_synthetic=True)
    )
    original161 = np.asarray(peer_lag_vectors(row, prep, history, permission))
    a = extension(window, sham, prep, "ASOF", "LL0_R", DECISION_SHA)
    b = extension(window, sham, prep, "ASOF", "LL1_R", DECISION_SHA)
    shifted = extension(window, sham, prep, "ASOF", "SHAM_LL1_R", DECISION_SHA)
    ll0 = np.concatenate((prefix, np.asarray(a.values)), axis=1)
    ll1 = np.concatenate((prefix, np.asarray(b.values)), axis=1)
    assert ll0.shape == (5, 163) and ll1.shape == (5, 198)
    np.testing.assert_array_equal(ll0[:, :161], original161)
    np.testing.assert_array_equal(ll1[:, :163], ll0)
    np.testing.assert_array_equal(np.asarray(shifted.values)[:, :16], np.asarray(a.values))
    np.testing.assert_array_equal(ll0[:, 161:163], window.flags)
    # Independent ordinal sentinels prove every tail channel and lag-major index.
    sentinel = np.arange(5 * 48 * 5, dtype=float).reshape(5, 48, 5)
    sent = extension(replace(window, signals=sentinel), sham, prep, "ASOF", "LL1_R", DECISION_SHA)
    for i in range(5):
        assert sent.values[i][16:] == tuple(
            sentinel[i, 47 - lag, c] for lag in LAGS for c in range(5)
        )
    assert column_names()[161:163] == ("TARGET_IS_H", "TARGET_IS_L")
    assert len(column_names()) == 198 and len(set(column_names())) == 198
    a.validate(window.processed, prep, "ASOF")
    for invalid in (
        replace(a, content_id="0" * 64),
        replace(a, context="HISTORICAL_TRAINING"),
        replace(a, universe_id="SYN:OTHER"),
        replace(a, values=a.values[:4]),
    ):
        with pytest.raises(ValueError):
            invalid.validate(window.processed, prep, "ASOF")
    assert window.samples[0].step == calendar.steps[calendar.steps.index(row.stock.steps[0]) - 1]


def test_independent_weighted_free_intercept_and_repeated_flag_penalty():
    symbols = ("N", "O", "P", "Q", "R")
    keys = tuple(
        (day, origin, s)
        for day, origins in (("A", (1, 2)), ("B", (1,)))
        for origin in origins
        for s in symbols
    )
    w = session_weights(keys)
    np.testing.assert_allclose(w, [0.05] * 10 + [0.1] * 5, rtol=0, atol=1e-16)
    flag = np.array([s == "N" for _, _, s in keys], dtype=float)
    y = 3.0 + 2.0 * flag
    lam = 0.1
    once = solve_weighted(flag[:, None], y, w, lam)
    repeated = solve_weighted(np.repeat(flag[:, None], 7, axis=1), y, w, lam)
    mx, my = np.sum(w * flag), np.sum(w * y)
    covariance = np.sum(w * (flag - mx) * (y - my))
    variance = np.sum(w * (flag - mx) ** 2)
    expected_once = covariance / (variance + lam)
    expected_repeated_sum = covariance / (variance + lam / 7)
    assert once.coefficients[0] == pytest.approx(expected_once)
    assert sum(repeated.coefficients) == pytest.approx(expected_repeated_sum)
    assert once.intercept == pytest.approx(my - mx * expected_once)
    assert expected_once != pytest.approx(expected_repeated_sum)
    assert PENALTIES == (0.0001, 0.001, 0.01, 0.1, 1)
    assert choose_penalty(tuple((p, 0.0) for p in PENALTIES)) == 1.0


def test_sham_old_publication_current_transform_49th_missing_masks(prepared):
    data, _, archive, pair, permission, prep, calendar, design, validation = prepared
    row = data.origins[-2].inputs
    window, sham, _ = design.prepare(row, prep, permission, "ASOF")
    assert sham.matched and len(sham.timestamp_pairs) == 49
    for now, old in sham.timestamp_pairs:
        n, o = pd.Timestamp(now), pd.Timestamp(old)
        nd, od = n.tz_convert("America/New_York"), o.tz_convert("America/New_York")
        assert nd.time() == od.time()
        assert design.sessions.index(str(nd.date())) - design.sessions.index(str(od.date())) == 10
        assert o < n
    # Earliest adequate window may use older raw evidence from before the fit;
    # its transform is applied at the current step using that existing fit.
    boundary = next(
        r.inputs
        for r in data.origins
        if r.inputs.stock.steps[0].end >= prep.window.fitted_at
        and r.inputs.plan.cutoff is not None
        and r.inputs.plan.cutoff >= validation.start
    )
    shifted_window, shifted, _ = design.prepare(boundary, prep, permission, "ASOF")
    assert pd.Timestamp(shifted.timestamp_pairs[0][1]) < prep.window.fitted_at
    assert shifted_window.samples[0].step.end >= prep.window.fitted_at
    missing_at = pd.Timestamp(sham.timestamp_pairs[0][1])
    broken = replace(archive, rows=tuple(r for r in archive.rows if r.step.end != missing_at))
    other = MatchedDesign(broken, design.history, pair, calendar, DECISION_SHA)
    for arm in ("LL0_R", "LL1_R", "SHAM_LL1_R"):
        with pytest.raises(ValueError, match="SAME_SLOT_SOURCE_ABSENT"):
            other.adapter(arm)(row, prep, permission, "ASOF")
    corrupt = replace(row, stock=replace(row.stock, action_binding="SYN:CHANGED"))
    with pytest.raises(ValueError):
        design.adapter("LL0_R")(corrupt, prep, permission, "ASOF")
    with pytest.raises(ValueError):
        design.adapter("LL0_R")(row, prep, Permission("SCIENTIFIC_REAL"), "ASOF")
    with pytest.raises(ValueError):
        directed_ridge_fit(data=data, allow_synthetic=True)


def test_alternate_order_identity_is_not_a_live_universe_default():
    u = UniverseSpec("SYN:ALTERNATE_D8", ("RUNE", "QUARK", "PULSE", "ORBIT", "NOVA"))
    data, _, archive, pair, _ = fixture("NULL", u)
    assert data.universe == archive.universe == pair.universe == u
    assert pair.highest == "NOVA" and pair.lowest == "RUNE"
    assert identity(u) != identity(replace(u, symbols=u.symbols[::-1]))
    assert all(
        ref.row is not None
        and ref.row.source_version == "SYN:D8_LABEL_SOURCE:NULL"
        and ref.row.row_id.startswith("SYN:D8:NULL:")
        for origin in data.origins
        for ref in origin.label.references
    )


def test_original_failed_health_reconstruction_no_new_optimization():
    from lstm_data.baseline_authority import replay_permission
    from lstm_data.p3_domain import MODE

    result = diagnose(
        Path("reports/data_audit/ta_p4_e5_e5l_2026-10-13_225047/failed_health_proof.json"),
        replay_permission(Permission(MODE)),
    )
    assert result["parameter_count"] == 7329
    assert result["new_optimizer_steps"] == result["new_health_runs"] == 0
    assert result["unchanged_gate"]["both_failed"]
    assert result["peer_linear_projection_MSE"] < 1e-20
    assert result["own_linear_projection_MSE"] > 0.1
    assert result["two_pass_fit"] == "NOT_RUN"


@pytest.mark.parametrize("case", ["FORWARD", "REVERSE", "NULL"])
def test_actual_matched_three_arm_candidate_and_fresh_refit(case, tmp_path):
    result = run_case(case, DECISION)
    write_json(tmp_path / "ridge_case.json", json_value(result))
    for name, width in (("LL0_R", 163), ("LL1_R", 198), ("SHAM_LL1_R", 198)):
        arm = result["arms"][name]
        assert len(arm["full_prefix_coefficients"]) == width
        assert arm["cohort"]["candidate_count"] == 5
        assert arm["cohort"]["refit_count"] == 1
        assert arm["cohort"]["adequacy"]["sessions"] >= 50
        assert len(arm["illustrative_five_scores"]) == 5
