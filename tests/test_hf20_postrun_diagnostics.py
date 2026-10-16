"""Focused P016 weighted algebra, authority, strict selection and no-gradient replay tests."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.controlled_loss import LossPolicy
from lstm_data.hf20_diagnostic_math import day_weights, selection_trace, weighted_decomposition
from lstm_data.hf20_postrun_diagnostics import (
    checked_binding,
    discover,
    evaluation_forward,
    guard_scope,
    read_json,
    validate_family,
)
from lstm_data.neural_engine import SharedLSTM

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/data_audit/ta_hf20_first_tm0_t2_2026-10-16_174656"


def test_three_session_unequal_origins_exact_decomposition():
    # Day losses: dayAmean(1,9)=5; dayB=25; dayCmean(49,81)=65; mean95/3.
    rows = []
    for day, values in [("A", [1.0, 3.0]), ("B", [5.0]), ("C", [7.0, 9.0])]:
        for origin, value in enumerate(values, 1):
            for symbol in ("X", "Y"):
                rows.append(
                    dict(session=day, origin=origin, symbol=symbol, y=value, p=0.25 * value + 0.5)
                )
    f = pd.DataFrame(rows)
    w = day_weights(f)
    assert w.sum() == pytest.approx(1)
    assert sum(w[f.session.eq("B")]) == pytest.approx(1 / 3)
    result = weighted_decomposition(f.y.to_numpy(), f.p.to_numpy(), w)
    manual_y2 = (5 + 25 + 65) / 3
    assert result["E_y2"] == pytest.approx(manual_y2)
    assert result["E_y2"] != pytest.approx(float(np.mean(f.y**2)))
    assert result["delta_MSE_vs_ZERO"] == pytest.approx(
        result["E_prediction2"] - 2 * result["E_y_prediction"]
    )
    assert result["delta_MSE_vs_ZERO"] == pytest.approx(
        result["mean_component"] + result["variance_covariance_component"]
    )
    with pytest.raises(ValueError):
        day_weights(pd.concat([f, f.iloc[:1]]))


def test_strict_qualifying_raw_minimum_and_real_t2_oracle():
    trace = selection_trace([1.0, 0.999, 0.9989])
    assert trace.qualifying.tolist() == [True, False, True]
    e = read_json(REPORT / "HF20-TM0-T2-S42-DEV1" / "epoch_records.json")
    trace = selection_trace([r["validation_MSE"] for r in e["calibration"]])
    assert int(trace.iloc[-1].selected_epoch) == 1 and int(trace.iloc[-1].raw_epoch) == 2
    first, second = trace.validation_MSE.iloc[:2]
    assert 0 < (first - second) / first < 0.001
    assert second > 0.999 * first and trace.iloc[-1].stop_reason == "PATIENCE_STOP"


@pytest.mark.parametrize(
    "split,start,end",
    [
        ("held_out", "2025-01-01", "2025-01-01"),
        ("development", "2026-01-07", "2026-01-08"),
        ("refit", "2024-01-01", "2026-10-15"),
        ("TG0", "2024-01-01", "2024-02-01"),
    ],
)
def test_heldout_denied_before_numerical_io(monkeypatch, split, start, end):
    def forbidden(*args, **kwargs):
        raise AssertionError("Numerical I/O before scope denial")

    monkeypatch.setattr(pd, "read_csv", forbidden)
    monkeypatch.setattr(np, "load", forbidden)
    with pytest.raises(ValueError, match="BEFORE_IO"):
        guard_scope(split, start, end)


@pytest.mark.parametrize("kind", ["source", "order", "target", "preparation", "input_id"])
def test_wrong_family_and_input_identity_denied(kind):
    p = read_json(REPORT / "experiment_design.json")
    c = read_json(ROOT / p["input_contract"]["path"])
    if kind == "source":
        c["source_revision"] = "wrong"
    elif kind == "order":
        p["symbols"] = list(reversed(p["symbols"]))
    elif kind == "target":
        c["target_id"] = "TG0"
    elif kind == "preparation":
        c.pop("preparation_id")
    else:
        p["views"]["development"]["preparation_id"] = "WRONG"
    with pytest.raises(ValueError):
        validate_family(p, c)


def test_checkpoint_stage_scale_and_no_aliasing_guard(monkeypatch):
    p = read_json(REPORT / "experiment_design.json")
    c = read_json(ROOT / p["input_contract"]["path"])
    d = REPORT / "HF20-TM0-T2-S42-DEV1"
    r = read_json(d / "run_result.json")
    manifest = read_json(d / "refit_final.manifest.json")
    valid = checked_binding(manifest, p, c, "T2", "REFIT_FINAL", r)
    assert valid["scale"]["scale"] == p["scales"]["refit"]["scale"]
    for field, value in [
        ("stage", "CALIBRATION_SELECTED"),
        ("target_id", "TG0"),
        ("scale", None),
        ("recipe_id", "WRONG"),
    ]:
        forged = deepcopy(manifest)
        forged["binding"][field] = value
        with pytest.raises(ValueError):
            checked_binding(forged, p, c, "T2", "REFIT_FINAL", r)
    assert (d / "refit_final.pt").resolve() != (d / "calibration_selected.pt").resolve()


def test_eval_forward_no_train_backward_step_or_double_inverse(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Training operation in read-only replay")

    monkeypatch.setattr(torch.Tensor, "backward", forbidden)
    monkeypatch.setattr(torch.optim.AdamW, "step", forbidden)
    old = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        model = SharedLSTM()
        x = torch.zeros((20, 48, 16), dtype=torch.float32)
        with pytest.raises(ValueError, match="TRAINING_MODE"):
            evaluation_forward(model, x, LossPolicy("T2", scale=0.9))
        model.eval()
        before = {k: v.clone() for k, v in model.state_dict().items()}
        h, z, y = evaluation_forward(model, x, LossPolicy("T2", scale=0.9))
        assert (
            h.shape == (20, 32)
            and not h.requires_grad
            and not z.requires_grad
            and not y.requires_grad
        )
        assert torch.equal(y, 0.9 * torch.sinh(z))
        assert torch.equal(y, evaluation_forward(model, x, LossPolicy("T2", scale=0.9))[2])
        assert all(torch.equal(v, before[k]) for k, v in model.state_dict().items())
        assert all(p.grad is None for p in model.parameters())
    finally:
        torch.set_num_threads(old)


def test_current_manifest_mask_and_original_metrics_guard_without_replay():
    directory, p, c, h, f, views = discover(None)
    assert directory.resolve() == REPORT.resolve()
    assert len(f) == 7320 and views["development"].summary() == p["views"]["development"]
    assert h["T2_saved_inverse_count"] == 1
    for a in ("C0", "T2", "ZERO"):
        result = weighted_decomposition(f.target.to_numpy(), f[a].to_numpy(), day_weights(f))
        original = pd.read_csv(REPORT / "matched_metrics.csv").set_index("arm").to_dict("index")
        assert result["MSE"] == pytest.approx(original[a]["MSE"], abs=2e-12)


def test_cli_protected_scope_denies_before_discovery(monkeypatch, tmp_path):
    import sys

    import lstm_data.hf20_postrun_diagnostics as module

    def forbidden(*args, **kwargs):
        raise AssertionError("Discovery before protected-scope denial")

    monkeypatch.setattr(module, "discover", forbidden)
    monkeypatch.setattr(
        sys, "argv", ["diagnose", "--out", str(tmp_path / "out"), "--through", "2026-01-07"]
    )
    with pytest.raises(ValueError, match="BEFORE_IO"):
        module.main()
    assert not (tmp_path / "out").exists()


def test_mismatched_actual_mask_never_intersects(monkeypatch):
    from dataclasses import replace

    import lstm_data.hf20_postrun_diagnostics as module

    loader = module.load_views

    def changed(contract):
        views = loader(contract)
        v = views["development"]
        views["development"] = replace(v, source=replace(v.source, rows=v.source.rows.iloc[:-1]))
        return views

    monkeypatch.setattr(module, "load_views", changed)
    with pytest.raises(ValueError, match="MASK_OR_INPUT"):
        module.discover(None)


def test_actual_four_case_visual_walkthrough_no_model_execution():
    from datetime import date

    from streamlit.testing.v1 import AppTest

    from lstm_data.hf20_postrun_diagnostics import choose_examples

    f = pd.read_csv(REPORT / "matched_predictions_development.csv", float_precision="round_trip")
    examples = choose_examples(f)
    guide = (ROOT / "docs/track_a/HOW_TO_VISUALLY_REVIEW_HF20_DIAGNOSIS.md").read_text()
    app = AppTest.from_file(str(ROOT / "apps/track_a_dashboard.py"), default_timeout=60).run()
    assert not app.exception
    app.sidebar.radio[0].set_value("HF20: TM0 vs T2").run()
    assert not app.exception
    for example in examples:
        assert (
            f"{example['symbol']},{example['session']},origin{example['origin']}"
            in guide.replace(" ", "").replace("**", "")
        )
        actual = f.loc[f.source_key.eq(example["source_key"])]
        assert len(actual) == 1 and float(actual.target.iloc[0]) == example["TG20"]
        app.selectbox(key="hf20_stock").set_value(example["symbol"]).run()
        day = date.fromisoformat(example["session"])
        app.date_input(key="hf20_dates").set_value((day, day)).run()
        origin = "1 · 10:32 ET" if example["origin"] == 1 else "2 · 11:32 ET"
        app.selectbox(key="hf20_origin").set_value(origin).run()
        labels = app.selectbox(key="hf20_event").options
        index = next(
            i
            for i, label in enumerate(labels)
            if label.startswith(example["session"] + " / origin" + str(example["origin"]) + " /")
        )
        app.selectbox(key="hf20_event").set_value(index).run()
        app.button(key="hf20_load_features").click().run()
        assert not app.exception
        assert len(app.get("plotly_chart")) >= 14
        assert not any("SOURCE/CHRONOLOGY HOLD" in w.value for w in app.warning)
    app.selectbox(key="hf20_run").set_value("HF20-TM0-T2-S42-DEV1").run()
    assert not app.exception


def test_full_matched_subgroups_and_rank_statistics_need_no_scipy(monkeypatch):
    import builtins

    from lstm_data.hf20_postrun_diagnostics import matched_audit

    original_import = builtins.__import__

    def no_scipy(name, *args, **kwargs):
        if name == "scipy" or name.startswith("scipy."):
            raise AssertionError("Undeclared SciPy dependency in rank diagnostics")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_scipy)
    f = pd.read_csv(REPORT / "matched_predictions_development.csv", float_precision="round_trip")
    result = matched_audit(
        f, REPORT, 6.5
    )  # Arbitrary unit-test subgroup boundary, never a fitted cutoff.
    groups = result["paired_groups"]
    assert isinstance(groups, pd.DataFrame)
    assert len(groups.loc[groups.group_kind.eq("origin")]) == 2
    assert groups.loc[groups.group_kind.eq("origin"), "defined_full_panel_Rank_IC_T2"].notna().all()
    ranks = result["stock_rank"]
    assert isinstance(ranks, pd.DataFrame)
    assert len(ranks) == 40 and ranks.rank_MAE.between(0, 19).all()
    decomposition = result["decomposition"]
    assert isinstance(decomposition, pd.DataFrame)
    assert decomposition.set_index("arm").loc["ZERO", "MSE"] == pytest.approx(3.4745059908061524)


def test_forged_future_view_denied_before_target_array_access():
    from dataclasses import replace

    from lstm_data.hf20_postrun_diagnostics import target_panel
    from lstm_data.hf20_training_data import load_views

    view = load_views()["development"]
    rows = view.source.rows.iloc[:1].copy()
    rows["session"] = "2026-01-07"
    forged = replace(view, source=replace(view.source, rows=rows))

    class ForbiddenLabels(dict):
        def __getitem__(self, key):
            raise AssertionError("Label numeric access before metadata guard")

    with pytest.raises(ValueError, match="BEFORE_IO"):
        target_panel(forged, ForbiddenLabels(), 0.001, "development")
