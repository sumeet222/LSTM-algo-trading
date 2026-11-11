"""Completed-book, rank, source and reporting acceptance; no financial replay."""

import ast
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.trading.track2.final_directional_slate.common import ROOT, load, verify_inputs
from lstm_data.trading.track2.final_directional_slate.run import ready
from lstm_data.trading.track2.final_directional_slate_analysis import merge_results, verify_run
from lstm_data.trading.track2.rapid_v1.paths import canonical, digest


def test_frozen_spec_and_selection_before_overlay():
    verify_inputs()
    ready()
    selection = load(ROOT / "SELECTION_RECEIPT.json")
    assert selection["selected"] == ["F1", "F4", "F3"]
    assert selection["status"] == "NO_ROBUST_POSITIVE_DIRECTIONAL_BASELINE"
    spec = load(ROOT / "FIVE_ALGORITHM_REGISTRY.json")
    identity = spec.pop("identity")
    assert canonical(spec) == identity
    assert (
        digest(ROOT / "FIVE_ALGORITHM_REGISTRY.json") == load(ROOT / "REGISTRY_SEAL.json")["sha256"]
    )
    assert (ROOT / "SELECTION_SCORE_AUDIT.csv").stat().st_mtime_ns < (
        ROOT / "OVERLAY_RUN_REGISTRY.json"
    ).stat().st_mtime_ns


def test_all24_views_and_account_bridges():
    d = pd.read_csv(ROOT / "FOUR_ARM_S2C_SIZING_RESULTS.csv")
    assert len(d) == 24 and set(d.status) == {"COMPLETE"}
    sizes = d.groupby(["candidate", "population"]).size()
    assert isinstance(sizes, pd.Series) and np.all(sizes.to_numpy() == 4)
    assert np.isfinite(d.final_NAV_USD).all() and d.final_NAV_USD.gt(0).all()
    x = d.gross_signed_price_PnL_USD + d.gross_action_value_USD - d.total_cost_USD - d.net_PnL_USD
    assert abs(x).max() < 1e-7
    assert d.terminal_pending.eq(0).all() and d.terminal_stock_symbols.eq(0).all()
    assert verify_run("MATCHED")["output"]["accounts"] == 12
    assert verify_run("ATTAINABLE")["output"]["accounts"] == 9


def test_cohort_and_physical_row_scope_normalization():
    s, days, t, p = merge_results()
    assert set(t.population) == {"MATCHED", "ATTAINABLE"}
    assert set(t.arm) == {"EQUAL", "ROLLING_RISK", "EWMA_RISK", "S2C_RISK"}
    assert set(t.economic_mode) == {"MICRO_PRO", "RETAIL_CONSERVATIVE"}
    for row in s.itertuples(index=False, name=None):
        assert row is not None
    check = pd.read_csv(ROOT / "analysis_03/RECONCILIATION.csv")
    assert set(check.status) == {"PASS"} and abs(check.residual).max() <= 1e-7
    sizes = days.groupby(["candidate", "population", "arm"]).size()
    assert isinstance(sizes, pd.Series) and np.all(sizes.to_numpy() == 1005)


def test_opportunities_common_but_funded_paths_endogenous():
    d = pd.read_csv(ROOT / "S2C_MATCHED_VS_ATTAINABLE.csv")
    m = d[d.population == "MATCHED"]
    assert m.groupby("candidate").risk_ready_original_alpha_keys.nunique().eq(1).all()
    a = d[d.population == "ATTAINABLE"]
    assert a.groupby("candidate").risk_ready_original_alpha_keys.nunique().gt(1).all()
    p = pd.read_csv(ROOT / "analysis_03/PAIRED_FUNDED_PATH_DIVERGENCE.csv")
    assert len(p) == 9 and p.source_opportunity_base_identical.all()
    assert p.shared_entry_notional_changed.gt(0).all()


def test_no_new_neural_activity_or_future_analysis_import():
    root = Path("src/lstm_data/trading/track2/final_directional_slate")
    for name in ("allocation.py", "engines.py", "risk_inputs.py"):
        for node in ast.walk(ast.parse((root / name).read_text())):
            if isinstance(node, ast.ImportFrom):
                assert not any(
                    k in (node.module or "") for k in ("phase2", "torch", "slate_analysis")
                )
    risk = load(ROOT / "RISK_INPUT_READINESS.json")
    assert risk["original_forecasts"] == 131111 and not risk["sign_mask_used"]
    assert not risk["future_endpoint_eligibility_filter"]
    labels = pd.read_csv(ROOT / "analysis_03/POSTHOC_MAGNITUDE_DECILES.csv")
    assert labels.never_entry_eligibility.all()
    assert (labels.future_label_observed + labels.censored_future_label == labels.forecasts).all()


def test_output_budget_and_original_context():
    assert sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file()) < 200_000_000
    d = pd.read_csv(ROOT / "ALL18_HISTORICAL_CONTEXT.csv")
    assert len(d) == 18 and d.still_registered.all()
    assert load(ROOT / "OVERLAY_PILOT_GATE.json")["restart"] == "EXACT_FULL_STATE_EQUAL"
    for pop in ("MATCHED", "ATTAINABLE"):
        assert len(verify_run(pop)["source_reads"]) == 48


def test_code_drift_gate_fails_without_rewriting_any_source(monkeypatch):
    from lstm_data.trading.track2.final_directional_slate import run

    monkeypatch.setattr(run, "overlay_hashes", lambda: {"tampered": "0"})
    with pytest.raises(ValueError, match="DRIFT"):
        run.ready()


def test_rank_audit_literal_weights_and_family_limit():
    d = pd.read_csv(ROOT / "SELECTION_SCORE_AUDIT.csv")
    assert len(d) == 30 and d.groupby("candidate").weight.sum().eq(1).all()
    assert np.allclose(d.weight * d.percentile, d.weighted_score)
    assert len({"R01", "R07", "M04"}) == len(load(ROOT / "SELECTION_RECEIPT.json")["families"])
