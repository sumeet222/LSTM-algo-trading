"""Read-only normalization software checks; no estimator fitting or confirmation numbers."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.ft0_transforms import ORDER, SCALED
from lstm_data.normalization_audit import run, scaler_records
from lstm_data.normalization_population import (
    BOUNDED,
    audit_guard,
    fit_records,
    population,
    preparations,
    verify_fit_binding,
)
from lstm_data.normalization_stats import (
    clipping_collisions,
    distribution,
    independent_scaler_check,
)
from lstm_data.pretraining_transforms import CandidateFloors
from lstm_data.stock_features import apply_component_floors
from lstm_data.visualization.controlled import Study
from lstm_data.visualization.loaders import Catalog, ViewUnavailable, component_base


def test_distributions_signed_absolute_missing_and_bounded():
    result = distribution(np.array([-1.0, 0.0, 0.0, 1.0, np.nan, np.inf]), True)
    assert result["observed"] == 6 and result["valid"] == 4
    assert result["missing"] == result["nonfinite"] == 1
    assert result["constant_rate"] == 0.5 and result["near_zero_rate"] == 0.5
    assert result["median"] == 0 and result["abs_median"] == 0.5
    assert result["bound_violations"] == 0
    assert distribution(np.array([1.1]), True)["bound_violations"] == 1


@pytest.mark.parametrize(
    "values,center,scale,method",
    [
        ([0.0, 0.0, 1.0, 2.0, 3.0], 1.0, 1.0, "MAD"),
        ([0.0, 0.0, 0.0, 1.0], 0.0, 0.25 / 1.349, "IQR_1.349"),
        ([0.0, 0.0, 0.0, 0.0, 1.0], 0.0, 0.4, "AUDITED_POPULATION_SD"),
        ([0.0, 0.0, 0.0], 0.0, 1.0, "CONSTANT"),
    ],
)
def test_recorded_scaler_fallback_algebra(values, center, scale, method):
    check = independent_scaler_check(np.array(values), None, center, scale, method)
    assert check["passed"]


def test_weighted_m2_quantile_and_clipping_collisions():
    x = np.array([-9.0, -6.0, 0.0, 6.0, 9.0])
    keys = pd.DataFrame(
        dict(symbol=["A", "B", "C", "D", "E"], timestamp=["SYN:T"] * 5, origin=[1] * 5)
    )
    before = x.copy()
    result = clipping_collisions(x, keys, 3)
    assert result["unique_lost"] == 2 and result["cross_stock_pairs_lost"] == 2
    assert result["lost_pair_rate"] == 0.2 and result["ordering_reversals"] == 0
    np.testing.assert_array_equal(x, before)
    check = independent_scaler_check(
        np.array([0.0, 2.0, 10.0, 12.0]), np.array([1, 1, 2, 2]), 6.0, 5.0, "MAD"
    )
    assert check["passed"]  # Weighted CDF midpoint convention, unscaled MAD.


def test_nonzero_constant_roundoff_discrepancy_is_disclosed():
    from lstm_data.ft0_transforms import robust_parameters

    # Preserve the actual historical kernel; disclose the gap from D4's constant contract.
    center, scale, method = robust_parameters(np.array([7.0, 7.0, 7.0]))
    assert center == 7.0 and 0 < scale < 1e-14 and method == "AUDITED_POPULATION_SD"
    desired_contract = independent_scaler_check(
        np.array([7.0, 7.0, 7.0]), None, 7.0, 1.0, "CONSTANT"
    )
    assert not desired_contract["passed"]


def test_floor_and_pseudocount_arithmetic_only():
    floors = CandidateFloors("AAPL", 0.1, 0.2, 1.0, 10.0, 0.3)
    values: dict[str, float | None] = dict(
        RMS12=0.0,
        RMS60=0.05,
        RMS63=0.0,
        OC=0.02,
        MOM5=0.2,
        MOM105=-0.1,
        Q1_MEAN=20.0,
        VOLUME_H=10.0,
        Q2_5=50.0,
        Q2_60=100.0,
    )
    result = apply_component_floors(values, floors)
    assert result["M1"] == pytest.approx(0.2)
    assert result["V1"] == result["V2"] == pytest.approx(np.log(0.1))
    assert result["Q1"] == pytest.approx(np.log(11 / 21))
    assert result["Q2"] == pytest.approx(np.log(60 / 110))


def test_confirmation_guard_before_discovery_output_or_numeric_io(monkeypatch, tmp_path):
    def forbidden(*args, **kwargs):
        raise AssertionError("Must fail before source discovery")

    monkeypatch.setattr(Catalog, "discover", forbidden)
    out = tmp_path / "reports/data_audit/ta012a_ft0_normalization_PROTECTED_TEST"
    with pytest.raises(ViewUnavailable, match="protected I/O"):
        run(tmp_path, out, "2024-07-01")
    assert not out.exists()
    with pytest.raises(ViewUnavailable):
        audit_guard("2025-06-30")


@pytest.fixture(scope="module")
def actual():
    root = Path(__file__).resolve().parents[1]
    catalog = Catalog.discover(root)
    if not (root / catalog.config["baseline"]["path"]).is_file():
        pytest.skip("Provision legitimate original candidate sources")
    base = component_base(catalog)
    return catalog, base, Study.discover(catalog), preparations(catalog, base)


def test_actual_fit_population_hash_13_plus3_no_refit(actual, monkeypatch):
    from lstm_data import pretraining_transforms

    def forbidden(*args, **kwargs):
        raise AssertionError("An audit cannot call a fitting routine")

    monkeypatch.setattr(pretraining_transforms, "fit_preparation", forbidden)
    monkeypatch.setattr(pretraining_transforms, "derive_floors", forbidden)
    catalog, base, study, views = actual
    pop = population(catalog, base, study, "WF1", "Inner training", views["WF1", "inner"])
    assert len(SCALED) == 13 and set(ORDER) - set(SCALED) == set(BOUNDED)
    assert pop.metadata["origins"] == 1376 and pop.metadata["unique_tensor_rows"] == 41820
    assert verify_fit_binding(pop, base)["passed"]
    # Includes four additional early-close sessions represented in legal input histories;
    # M2 fit keys are not the 6,880 stock/forecast labels of the target population.
    assert len(fit_records(pop, "M2")) == 6920
    assert len(pop.channel("M1")) == len(pop.frame) // 2
    assert len(pop.channel("M2")) == len(pop.frame)
    checks, _ = scaler_records(pop, base)
    assert all(v["passed"] for v in checks)
    for feature in BOUNDED:
        part = pop.channel(feature)
        np.testing.assert_array_equal(
            part[feature + "_scaled"], part[feature].to_numpy().astype(np.float32)
        )
        assert part[feature + "_scaled"].abs().le(1).all()
    assert pop.frame.timestamp.lt(pop.preparation.window.stop).all()
    assert pop.frame.timestamp.ge(pop.preparation.window.start).all()


def test_actual_validation_scope_and_mask_not_intersected(actual):
    catalog, base, study, views = actual
    pop = population(catalog, base, study, "WF2", "Inner validation", views["WF2", "inner"])
    assert pop.metadata["origins"] == 108 and pop.metadata["unique_tensor_rows"] == 3690
    assert pop.frame.timestamp.ge(pop.preparation.window.stop).all()
    assert pop.metadata["exclusions"] == {"SCALER_NOT_AVAILABLE_AT_EVERY_HISTORICAL_STEP": 16}
    with pytest.raises(ViewUnavailable, match="Wrong preparation"):
        population(catalog, base, study, "WF2", "Development", views["WF2", "inner"])


def test_existing_output_never_overwritten(tmp_path):
    out = tmp_path / "reports/data_audit/ta012a_ft0_normalization_EXISTING"
    out.mkdir(parents=True)
    with pytest.raises(FileExistsError):
        run(tmp_path, out)


def test_registered_packet_complete_distributions_and_tail_identities(actual):
    from lstm_data.normalization_report import AuditPacket
    from lstm_data.visualization.loaders import verified

    catalog, *_ = actual
    if "normalization_audit" not in catalog.config:
        pytest.skip("Register the completed audit packet before the UI verification")
    packet = AuditPacket.discover(catalog)
    frame = packet.table("ft0_normalization_distribution.csv")
    assert len(frame) == 2 * 4 * 16 * 2 * 6 and set(frame.feature) == set(ORDER)
    assert frame.nonfinite.eq(0).all() and frame.missing.eq(0).all()
    assert frame.ever_model_input_count.le(frame.observed).all()
    hist = packet.json("histograms.json")["histograms"]
    assert all(sum(h["counts"]) == h["unique_observations"] for h in hist)
    identities = json.loads(
        gzip.decompress(
            verified(
                catalog.root, packet.manifest["artifacts"]["tail_identity_sets.json.gz"]
            ).read_bytes()
        )
    )
    indexed = {
        (str(r["fold"]), str(r["partition"]), str(r["feature"]), str(r["symbol"])): r
        for r in frame.loc[frame.representation.eq("scaled")].to_dict("records")
    }
    for group in identities:
        keys = group["identities"]
        row = indexed[group["fold"], group["partition"], group["feature"], group["symbol"]]
        assert len(keys) == row[f"abs_gt_{group['abs_gt']}_count"]
        assert len(keys) == len(set(keys))
    with pytest.raises(ViewUnavailable):
        packet.table("unregistered.csv")


def test_actual_normalization_ui_example_and_48_step_context(actual):
    from streamlit.testing.v1 import AppTest

    catalog, *_ = actual
    if "normalization_audit" not in catalog.config:
        pytest.skip("Register the completed packet before UI verification")
    app = AppTest.from_file(
        str(catalog.root / "apps/track_a_dashboard.py"), default_timeout=90
    ).run()

    def widget(kind, label):
        return next(v for v in getattr(app, kind) if v.label == label)

    widget("button", "Package012A normalization audit").click().run()
    assert not app.exception and not app.error
    widget("selectbox", "Audit fold").set_value("WF2").run()
    widget("selectbox", "Audit FT0 channel").set_value("B1").run()
    widget("selectbox", "Audit population").set_value("Development").run()
    widget("selectbox", "Audit stock or pooled").set_value("CMCSA").run()
    assert not app.exception and not app.error
    widget("button", "Open normalization example").click().run()
    assert not app.exception and not app.error
    assert app.session_state["full_stock"] == "CMCSA"
    assert app.session_state["full_recipe"] == "WF2 / refit"
    assert app.session_state["full_jump"].isoformat() == "2024-01-25"
    widget("checkbox", "Show normalization example's actual 48-step input context").check().run()
    assert not app.exception and not app.error
    assert len(app.get("plotly_chart")) == 3
