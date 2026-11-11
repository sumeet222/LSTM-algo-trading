"""Independent published-output checks; never invoke a funded rerun."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.trading.track2.rapid_final_diag.provenance import registry, verify
from lstm_data.trading.track2.rapid_final_diag_analysis import verify_funded
from lstm_data.trading.track2.rapid_v1.paths import digest

ROOT = Path("trading/track2/rapid_final_diag_v1")
BASE = ROOT / "runs/final-diag-20261110-r1/funded"


def test_untouched_archive_and_bound_code():
    verify()
    assert registry()["status"] == "SEALED_BEFORE_NEW_FUNDED_OUTCOMES"
    assert verify_funded()["status"] == "COMPLETE"


def test_thirteen_finite_accounts_and_exact_identity():
    d = pd.read_csv(BASE / "FUNDED_TARGETED_RESULTS.csv")
    assert len(d) == 13 and set(d.status) == {"COMPLETE"}
    assert d.sessions.eq(1005).all()
    assert np.isfinite(d.final_NAV_USD).all() and (d.final_NAV_USD > 0).all()
    assert abs(d.arithmetic_residual_USD).max() <= 1e-7
    x = d[d.strategy_id == "M01"]
    for key in (
        "net_PnL_USD",
        "gross_signed_price_PnL_USD",
        "external_orders",
        "commission_USD",
        "risk_closed_cohorts",
    ):
        assert len(set(x[key])) == 1
    p = json.loads((BASE / "CONTROL_PARITY.json").read_text())
    assert p["controls"] == 7 and p["daily_rows"] == 7035


def test_complete_cohort_bridge_not_first_entry_reconstruction():
    x = pd.read_csv(ROOT / "analysis_01/COHORT_ACCOUNT_RECONCILIATION.csv")
    assert len(x) == 39 and abs(x.residual).max() <= 1e-7
    d = pd.read_parquet(BASE / "COMPLETED_COHORTS.parquet")
    assert not d.key.duplicated().any()
    assert (d.entry_at <= d.exit_at).all()
    assert d.entry_at.notna().all()


def test_special_order_supplement_exact_and_never_replayed():
    r = ROOT / "supplement_01"
    m = json.loads((r / "SUPPLEMENT_MANIFEST.json").read_text())
    assert m["recovered_rows"] == 3 and not m["funded_replay_performed"]
    assert not m["funded_performance_changed"]
    for key, sha in m["files"].items():
        assert digest(r / key) == sha
    x = pd.read_csv(r / "PHYSICAL_ORDERS_RECONCILIATION.csv")
    assert len(x) == 52 and abs(x.residual).max() <= 1e-7
    q = pd.read_parquet(r / "RECOVERED_OGN_PHYSICAL_ROWS.parquet")
    assert list(q.shares) == [12.0, 12.0, 6.0]
    assert q.commission.eq(1).all()
    assert np.allclose(
        q.shares * q.external_price, q.shares * q.raw_open + q.print_slippage + q.impact
    )


def test_stress_before_rounding_and_existing_reservations():
    d = pd.read_csv(BASE / "R01_ENTRY_RESERVES.csv")
    assert len(d) == 538
    assert d.t.between(0, 1).all() and (d.new_commitment <= d.old_commitment).all()
    assert np.allclose(d.new_commitment, d.old_commitment * d.t)
    x = pd.read_csv(ROOT / "supplement_01/R01_STRESS_INEQUALITY_CHECKS.csv")
    assert x.residual.max() <= 1e-7
    assert set(d.A) == {0} and set(d.L) == {0}  # Actual same-vintage state, not fabricated support.


def test_no_earlier_execution_and_actual_source_hashes():
    x = pd.read_parquet(BASE / "PHYSICAL_FILLS.parquet")
    assert (x.effective > x.decision).all()
    assert (x.posted >= x.effective + 3).all()
    assert x.source.notna().all()
    assert x.raw_open.gt(0).all()
    assert x.effective.max() <= 28928159  # 2024-12-31T23:59Z, calendar metadata only after.


def test_causal_opportunity_alignment_and_unshared_selection():
    d = pd.read_csv(ROOT / "analysis_01/PAIRED_OPPORTUNITY_AND_EXIT_DIVERGENCE.csv")
    rows = d[d.category != "NEITHER_FUNDED_AGGREGATE"]
    assert rows.raw_causal_key_verified.eq(True).all()
    assert set(d.strategy_id) == {"M01", "M03", "M04", "M05", "R01", "R07"}
    assert {"BOTH_ENTERED", "CONTROL_ONLY", "TREATMENT_ONLY"}.issubset(set(rows.category))
    assert d[d.strategy_id == "M01"].exit_changed.sum() == 0


def test_small_offline_only_sample_is_not_portfolio_value():
    d = pd.read_parquet(ROOT / "analysis_01/OFFLINE_CHANGED_EXIT_SAMPLE.parquet")
    assert len(d) == 1347 and len(d) <= 6 * 100 * 3
    assert (d.reference_at >= d.target_at).all()
    assert d.lag.le(5).all()
    assert (d.available_at == d.reference_at + 3).all()
    assert set(d.feasibility) == {"INFEASIBLE_UNDER_REALIZED_RISK", "UNFUNDED_NONFORCED"}
    assert np.allclose(d.price_raw_to_raw, d.quantity * (d.share_factor * d.later_raw - d.raw))
    before = (BASE / "FUNDED_MANIFEST.json").read_bytes()
    changed_future = d.later_raw + 1
    assert not np.allclose(
        d.price_raw_to_raw, d.quantity * (d.share_factor * changed_future - d.raw)
    )
    assert (BASE / "FUNDED_MANIFEST.json").read_bytes() == before


def test_all18_retained_and_storage_bounded():
    d = pd.read_csv(ROOT / "analysis_01/ALL18_CONTEXT_AND_FINAL_DIAGNOSTIC_MATRIX.csv")
    assert len(d) == 18 and d.strategy_id.nunique() == 18 and d.retained.all()
    assert len(d[d.final_variant_status == "NO_NEW_FUNDED_VARIANT"]) == 12
    assert d[d.strategy_id == "M06"].role.iloc[0] == "COMPACT_NONFUNDED_CONTEXT"
    assert sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file()) < 100_000_000


@pytest.mark.parametrize("name", ["INPUTS_BEFORE.json", "REGISTRY_SEAL.json", "PILOT_GATE.json"])
def test_mandatory_immutable_receipts(name):
    assert (ROOT / name).is_file()
