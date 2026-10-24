"""Independent P028 panel/peer math, order, identity and causal-graph tests; no fits."""

import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.config import fingerprint, write_json
from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.hf1m_ft16_source import ref
from lstm_data.objective_screen_run import record_epoch
from lstm_data.state_screen_authority import (
    RUNS,
    ensure,
    predecessor_gate,
    require_gate,
    required_artifacts,
    validate,
)
from lstm_data.state_screen_control import evaluate
from lstm_data.state_screen_metrics import allocation, paired
from lstm_data.state_screen_models import exact_optimizer, model_for, optimizer
from lstm_data.state_screen_spec import ARMS, PARAMETERS
from lstm_data.temporal_screen_rehearsal import SyntheticStudy
from lstm_data.visualization.state_screen_ui import guard_query


@pytest.fixture(autouse=True, scope="module")
def bounded_threads():
    previous = torch.get_num_threads()
    torch.set_num_threads(4)
    yield
    torch.set_num_threads(previous)


def test_peer_shift_reweights_both_matched_populations_and_never_updates(tmp_path, monkeypatch):
    from lstm_data.objective_screen_source import ordered_targets
    from lstm_data.state_screen_engine import predict

    monkeypatch.chdir(tmp_path)
    study = SyntheticStudy(Path("source"))
    view = study.mock_view("refit")
    model = model_for("A7").eval()
    recipe = dict(scale=study.recipe("refit")["t2_scale"])
    f = allocation(predict(model, view, "A7", recipe, {}), recipe["scale"])
    out = Path("control")
    out.mkdir()
    with patch.object(
        torch.optim.AdamW, "step", side_effect=AssertionError("UNAUTHORIZED_STEP")
    ) as step:
        result = evaluate(model, study, view, f, ordered_targets(view), recipe, out, rehearsal=True)
        assert step.call_count == 0
    assert result["matched_origins"] == 20 and result["own_history_unchanged"] is True
    for name in ("peer_original_matched", "peer_shifted_matched"):
        subset = pd.read_parquet(out / (name + ".parquet"))
        np.testing.assert_allclose(subset.ordinary_weight.sum(), 1, rtol=0, atol=1e-14)
        assert len(subset) == 400 and subset.origin_id.nunique() == 20
    assert len(f) == 800


def test_injected_scalar_ticker_row_and_float_precision_errors_stop(tmp_path, monkeypatch):
    from lstm_data.hf1m_ft16_source import checked
    from lstm_data.objective_screen_diagnostics import canonical
    from lstm_data.objective_screen_source import ordered_targets

    monkeypatch.chdir(tmp_path)
    study = SyntheticStudy(Path("source"))
    view = study.mock_view("inner_train")
    target = ordered_targets(view)
    f = target.copy()
    f["actual_TG20"] = f.TG20
    for broken in (f.iloc[:-1].copy(), f.assign(ticker=np.roll(f.ticker.to_numpy(), 1))):
        with pytest.raises(AssertionError):
            canonical(broken, target)
    model = model_for("A8")
    opt = optimizer(model)
    opt.param_groups[0]["lr"] = np.nextafter(0.001, np.inf)
    with pytest.raises(ValueError):
        exact_optimizer(model, opt)
    receipt = Path("provenance.json")
    write_json(receipt, {"fixture": "DRY_RUN"})
    reference = ref(receipt)
    receipt.write_text("bad source")
    with pytest.raises(ValueError):
        checked(reference)
    before = view.origin_batch((0,))["x"].copy()
    view.labels *= 100
    np.testing.assert_array_equal(before, view.origin_batch((0,))["x"])


def test_atomic_progress_and_exclusive_receipts(tmp_path):
    epochs = []
    for phase, count in [("calibration", 12), ("refit", 2)]:
        for epoch in range(1, count + 1):
            epochs.append(dict(phase=phase, training=dict(epoch=epoch, lr=0.001)))
            record_epoch(tmp_path, epochs)
    assert json.loads((tmp_path / "epochs_progress.json").read_text()) == epochs
    assert len(list((tmp_path / "epoch_receipts").glob("*.json"))) == 14
    with pytest.raises(FileExistsError):
        record_epoch(tmp_path, epochs)


def test_controller_rejects_absent_partial_rehearsal_or_tampered_gate(tmp_path):
    with pytest.raises(ValueError):
        ensure(tmp_path / "missing", None, RUNS[0])
    for run in RUNS[1:]:
        with pytest.raises(ValueError):
            predecessor_gate(tmp_path / "plan.json", run, [])
    gate = dict(status="PASS_P028_A7", scope="REHEARSAL_ONLY", all_roles=4)
    path = tmp_path / "gate.json"
    write_json(path, gate)
    with pytest.raises(ValueError):
        require_gate(path, "A7")
    with pytest.raises(ValueError):
        require_gate(path, "A7", rehearsal=True)
    start = dict(
        sequence=1,
        previous=fingerprint([]),
        run_id=RUNS[0],
        status="STARTED",
        global_started_pairs=60,
        effective_ceiling=200,
    )
    assert validate([start]) == [start]
    repeated = dict(start, sequence=2, previous=fingerprint([start]), global_started_pairs=61)
    with pytest.raises(ValueError):
        validate([start, repeated])


def test_paired_ic_and_mse_bootstrap_matches_complete_panel_resampling():
    from lstm_data.branch_replication_metrics import paired_month_blocks
    from lstm_data.objective_screen_metrics import regression

    y = np.tile(np.linspace(-1, 1, 20), 4)
    days = np.repeat(["2025-07-01", "2025-07-02", "2025-08-01", "2025-09-01"], 20)
    f = pd.DataFrame(
        dict(
            origin_id=np.repeat(np.arange(4), 20),
            ticker=np.tile([str(i) for i in range(20)], 4),
            TG20=y,
            session_date_et=days,
            pred_original_TG20=np.r_[y[:20], -y[:20], np.roll(y[:20], 5), y[:20] * 0.3],
        )
    )
    b = f.copy()
    b["pred_original_TG20"] = np.tile(np.roll(y[:20], 3), 4)
    output, _ = paired(f, b)
    for metric, field in [("mse", "mse"), ("ic", "daily_ic")]:
        original = paired_month_blocks(
            days,
            lambda indices, pseudo: (
                regression(y[indices], f.pred_original_TG20.to_numpy()[indices], pseudo)[field]
                - regression(y[indices], b.pred_original_TG20.to_numpy()[indices], pseudo)[field]
            ),
        )
        for expected in original:
            actual = next(
                x
                for x in output["intervals"]
                if x["metric"] == metric and x["block_months"] == expected["block_months"]
            )
            np.testing.assert_allclose(actual["interval"], expected["interval"], rtol=0, atol=1e-14)


def test_production_controller_requires_complete_integrity_science_and_resource_gate(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    # Bind the current reviewed code without creating a real ledger or optimizer.
    with patch("lstm_data.state_screen_authority.code_binding", return_value={"fixture": "bound"}):
        plan = Path("plan.json")
        write_json(plan, dict(scientific_definitions=dict(sha256="science")))
        evidence = Path("evidence.json")
        write_json(evidence, dict(mock=True))
        result = ref(evidence)
        history = [dict(run_id=RUNS[0], status="COMPLETED", detail=dict(result=result))]
        gate: dict[str, object] = dict(
            status="PASS_P028_A7",
            scope="RESEARCH_CANDIDATE",
            all_roles=4,
            cases=dict(cases=22),
            proposal_sha256=ref(plan)["sha256"],
            execution_sha256=fingerprint({"fixture": "bound"}),
            scientific_sha256="science",
            result_sha256=result["sha256"],
            evidence=[result],
            evidence_fingerprint=fingerprint([result]),
        )
        fields = (
            "objective_reconciled",
            "reload_reconciled",
            "mechanisms_verified",
            "resources_verified",
            "source_verified",
            "uncertainty_verified",
            "tests_verified",
            "peer_control_verified",
            "case_peer_evidence_verified",
            "ui_verified",
            "order_and_clock_verified",
        )
        gate.update({key: True for key in fields})
        # Isolated UNIT-TEST provenance fixtures; ensure/append cannot authorize them.
        root = Path("UNIT_TEST_DELIVERABLES")
        for name in required_artifacts("A7"):
            q = root / name
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_text(json.dumps({"fixture": True}))
        manifest = dict(files={"fixture": result}, execution_sha256=gate["execution_sha256"])
        (root / "ui_payload/manifest.json").write_text(json.dumps(manifest))
        (root / "ui_payload/component_receipt.json").write_text(
            json.dumps(
                dict(
                    fixture=True,
                    status="PASS_P028_ARM_COMPONENTS",
                    arm="A7",
                    scope="RESEARCH_CANDIDATE",
                    role_view_pairs=36,
                    case_choices=22,
                    stock_histories=20,
                    feature_channels=16,
                    optimizer_step_calls=0,
                    manifest=ref(root / "ui_payload/manifest.json"),
                    execution_sha256=gate["execution_sha256"],
                    files_fingerprint=fingerprint(manifest["files"]),
                )
            )
        )
        gate["diagnostics_root"] = str(root)
        deliverables = {name: ref(root / name) for name in required_artifacts("A7")}
        gate["deliverables"] = deliverables
        path = Path("A7_immediate_gate.json")
        path.write_text(json.dumps(gate))
        predecessor_gate(plan, RUNS[1], history)
        for name in (
            "cohorts.parquet",
            "ui_payload/component_receipt.json",
            "refit/case_state_history.parquet",
        ):
            missing = dict(gate, deliverables={k: v for k, v in deliverables.items() if k != name})
            path.write_text(json.dumps(missing))
            with pytest.raises(ValueError):
                predecessor_gate(plan, RUNS[1], history)
        for field in fields:
            broken = dict(gate, **{field: False})
            path.write_text(json.dumps(broken))
            with pytest.raises(ValueError):
                predecessor_gate(plan, RUNS[1], history)
        path.write_text(json.dumps(dict(gate, all_roles=3)))
        with pytest.raises(ValueError):
            predecessor_gate(plan, RUNS[1], history)
        path.write_text(json.dumps(gate))
        evidence.write_text("corruption")
        with pytest.raises(ValueError):
            predecessor_gate(plan, RUNS[1], history)


def test_failure_remains_charged_even_when_the_original_plan_was_changed(tmp_path, monkeypatch):
    import lstm_data.state_screen_authority as authority

    monkeypatch.chdir(tmp_path)
    journal = Path("UNIT_TEST_JOURNAL.jsonl")
    monkeypatch.setattr(authority, "JOURNAL", journal)
    plan = Path("plan.json")
    approval = Path("approval.json")
    prior = Path("prior.json")
    for p in (plan, approval, prior):
        write_json(p, dict(fixture=True))
    start = dict(
        sequence=1,
        previous=fingerprint([]),
        run_id=RUNS[0],
        status="STARTED",
        global_started_pairs=60,
        effective_ceiling=200,
        plan=ref(plan),
        authority=ref(approval),
        previous_journal=ref(prior),
    )
    journal.write_text(json.dumps(start) + "\n")
    plan.write_text("CHANGED_BINDING")
    authority.append_failure(plan, approval, RUNS[0], ValueError("EXACT_BINDING_CHANGED"))
    history = authority.rows()
    assert history[-1]["status"] == "FAILED" and history[-1]["global_started_pairs"] == 60
    assert (
        history[-1]["plan"] == start["plan"]
        and history[-1]["detail"]["new_fit_permission"] is False
    )
    with pytest.raises(ValueError):
        authority.append_failure(plan, approval, RUNS[0], ValueError("NO_RETRY"))


def test_origin_weighted_block_intervals_with_single_and_dual_origin_days():
    from lstm_data.branch_replication_followup import month_counts
    from lstm_data.objective_screen_audit import origin_ic

    days = np.repeat(
        ["2025-07-01", "2025-07-01", "2025-07-02", "2025-08-01", "2025-08-01", "2025-09-01"], 20
    )
    y = np.tile(np.linspace(-1, 1, 20), 6)
    predictions = np.concatenate([np.roll(y[:20], k) for k in (0, 3, 8, 1, 6, 2)])
    f = pd.DataFrame(
        dict(
            origin_id=np.repeat(range(6), 20),
            ticker=np.tile(SYMBOLS, 6),
            TG20=y,
            session_date_et=days,
            pred_original_TG20=predictions,
        )
    )
    baseline = f.assign(pred_original_TG20=np.tile(np.roll(y[:20], 4), 6))
    output, _ = paired(f, baseline)
    delta = origin_ic(predictions, y) - origin_ic(baseline.pred_original_TG20.to_numpy(), y)
    per_origin = pd.DataFrame(dict(day=days[::20], delta=delta))
    g = per_origin.groupby("day").delta.agg(["sum", "count"])
    for size in (1, 2):
        counts = month_counts(g.index.to_numpy(), size)
        draws = (counts @ g["sum"].to_numpy()) / (counts @ g["count"].to_numpy())
        actual = next(
            x
            for x in output["intervals"]
            if x["metric"] == "origin_ic" and x["block_months"] == size
        )
        np.testing.assert_allclose(
            actual["interval"], np.quantile(draws, [0.025, 0.975]), rtol=0, atol=1e-14
        )
        np.testing.assert_allclose(actual["delta"], delta.mean(), rtol=0, atol=1e-14)


def test_undefined_origin_IC_is_not_imputed_or_given_an_origin_weight():
    from lstm_data.objective_screen_audit import origin_ic

    y = np.tile(np.linspace(-1, 1, 20), 3)
    f = pd.DataFrame(
        dict(
            origin_id=np.repeat(range(3), 20),
            ticker=np.tile(SYMBOLS, 3),
            TG20=y,
            session_date_et=np.repeat(["2025-07-01", "2025-07-01", "2025-08-01"], 20),
            pred_original_TG20=np.r_[np.zeros(20), y[20:40], -y[40:]],
        )
    )
    baseline = f.assign(pred_original_TG20=np.r_[y[:20], np.zeros(20), np.roll(y[40:], 3)])
    result, _ = paired(f, baseline)
    expected = (
        origin_ic(f.pred_original_TG20.to_numpy(), y)
        - origin_ic(baseline.pred_original_TG20.to_numpy(), y)
    )[2]
    assert result["defined_origin_pairs"] == 1
    for interval in result["intervals"]:
        if interval["metric"] == "origin_ic":
            np.testing.assert_allclose(interval["delta"], expected, rtol=0, atol=1e-14)


@pytest.mark.parametrize("arm", ARMS)
def test_exact_architecture_parameter_settings_and_finite_output(arm):
    model = model_for(arm).eval()
    assert sum(p.numel() for p in model.parameters()) == PARAMETERS[arm]
    exact_optimizer(model, optimizer(model))
    x = torch.randn(2, 20, 48, 16)
    assert model(x).shape == (2, 20) and torch.isfinite(model(x)).all()


def test_structural_identity_null_rank_and_backward_without_steps():
    from lstm_data.state_screen_mechanisms import prove

    with patch.object(torch.optim.AdamW, "step", side_effect=AssertionError("FORBIDDEN")) as step:
        assert prove()["status"] == "PASS_P028_MECHANISM_PROOFS"
        assert step.call_count == 0


def test_state_constructor_exact_float64_and_own_fixed_shift():
    from lstm_data.state_screen_models import panel_state

    x = torch.randn(3, 20, 48, 16)
    m = panel_state(x).numpy()
    a = x.numpy().astype(float)
    expected = np.stack((a[:, :, :, 0].mean(1), np.median(a[:, :, :, 4], axis=1)), -1).astype(
        np.float32
    )
    np.testing.assert_array_equal(m, expected)
    model = model_for("A8").eval()
    torch.testing.assert_close(model.shifted(x, torch.randn_like(x)), model(x), rtol=0, atol=0)


@pytest.mark.parametrize(
    "query",
    [
        dict(role="confirmation"),
        dict(date="2026-01-01"),
        dict(date=""),
        dict(arm="A4"),
        dict(ticker="INVALID"),
        dict(unrecognized="bad"),
    ],
)
def test_protected_routes_fail_before_io(query):
    with patch.object(Path, "open", side_effect=AssertionError("IO_BEFORE_GUARD")):
        with pytest.raises(ValueError):
            guard_query(query)


def test_a7_endpoint_gate_and_direct_historical_state_are_distinct():
    model = model_for("A7").eval()
    x = torch.randn(2, 20, 48, 16)
    from lstm_data.state_screen_models import panel_state

    m = panel_state(x)
    alternate = m.clone()
    alternate[:, 0] += 1
    torch.testing.assert_close(
        model.details(x, m)["alpha"], model.details(x, alternate)["alpha"], rtol=0, atol=0
    )
    assert not torch.equal(model(x, m), model(x, alternate))


def test_a12_common_dropout_once_and_cloned_identity():
    model = model_for("A12")
    x = torch.randn(2, 20, 48, 16)
    calls = []
    hook = model.dropout.register_forward_hook(lambda *a: calls.append(1))
    model(x)
    hook.remove()
    assert len(calls) == 1
    torch.testing.assert_close(model.head.weight, model.expert1.weight, rtol=0, atol=0)


def test_d6g_strict_tie_and_selected_vs_raw():
    from lstm_data.neural_lifecycle import EarlyStop

    selector = EarlyStop()
    assert selector.observe(1.0)
    assert not selector.observe(0.999)
    assert selector.selected == 1 and selector.raw_epoch == 2
    for _ in range(10):
        selector.observe(1.1)
    assert selector.epoch == 12 and selector.status != "CALIBRATING"


def test_engine_synthetic_backward_clips_without_any_optimizer_step(tmp_path, monkeypatch):
    from lstm_data.state_screen_engine import epoch_pass, state_hash

    monkeypatch.chdir(tmp_path)
    study = SyntheticStudy(Path("source"))
    model = model_for("A7")
    before = state_hash(model)
    opt = optimizer(model)
    with patch.object(
        torch.optim.AdamW, "step", side_effect=AssertionError("FORBIDDEN")
    ) as blocked:
        result = epoch_pass(
            model,
            study.mock_view("inner_train"),
            "A7",
            dict(scale=0.7),
            1,
            opt,
            Path("backward.jsonl"),
            update=False,
        )
        assert blocked.call_count == 0
    assert result["backward_batches"] > 0 and result["optimizer_steps"] == 0
    assert before == state_hash(model) and not opt.state
    assert result["postclip"]["norm_max"] <= 1.00001


@pytest.mark.parametrize("arm", ARMS)
def test_causal_state_prefix_and_nonnull_rank_change(arm):
    from lstm_data.state_screen_models import panel_state

    model = model_for(arm).eval()
    x = torch.randn(3, 20, 48, 16)
    m = panel_state(x)
    with torch.no_grad():
        if arm == "A7":
            model.gate.weight[0, 0] = 3
        elif arm == "A8":
            model.local_cell.weight_ih[:, 16:24].fill_(0.5)
        else:
            model.expert1.weight.add_(0.5)
        original = model(x, m)
        changed = model(x, m + 5)
    assert torch.any(torch.argsort(original, dim=1) != torch.argsort(changed, dim=1))


def test_deterministic_cases_never_consult_predictions(tmp_path, monkeypatch):
    from lstm_data.objective_screen_source import ordered_targets
    from lstm_data.state_screen_cases import select

    monkeypatch.chdir(tmp_path)
    study = SyntheticStudy(Path("source"))
    f = ordered_targets(study.mock_view("refit"))
    f["panel_state2"] = np.linspace(-1, 1, len(f))
    f["pred_original_TG20"] = np.arange(len(f))
    first, coverage = select(dict(refit=f, development=f), dict(refit=0.0))
    f["pred_original_TG20"] = -f.pred_original_TG20
    second, _ = select(dict(refit=f, development=f), dict(refit=0.0))
    pd.testing.assert_frame_equal(first, second, check_exact=True)
    assert len(first) == 22 and len(coverage) == 22


def test_extreme_decomposition_uses_same_float64_metrics_and_strict_reference():
    from decimal import Decimal, localcontext

    from lstm_data.objective_screen_metrics import equal_weights
    from lstm_data.state_screen_metrics import regression

    y = np.tile(np.linspace(-2, 2, 20), 40)
    y[0] = 9000.0
    y[4] = 8100.0
    pred = np.linspace(-0.01, 0.01, len(y))
    days = np.repeat([f"2024-04-{i + 1:02d}" for i in range(20)], 40)
    result = regression(y, pred, days)
    w = equal_weights(days)
    assert result["mse"] == float(w @ ((pred - y) ** 2))
    with localcontext() as context:
        context.prec = 50
        reference = sum(
            Decimal.from_float(float(a))
            * (Decimal.from_float(float(b)) - Decimal.from_float(float(c))) ** 2
            for a, b, c in zip(w, pred, y)
        )
    np.testing.assert_allclose(result["mse"], float(reference), rtol=1e-10, atol=1e-11)


def test_global_then_local_order_and_strict_prefix_causality():
    from lstm_data.state_screen_models import panel_state

    model = model_for("A8").eval()
    x = torch.randn(2, 20, 48, 16)
    m = panel_state(x)
    calls = []
    a = model.global_cell.register_forward_hook(lambda *args: calls.append("global"))
    b = model.local_cell.register_forward_hook(lambda *args: calls.append("local"))
    first = model.details(x, m)
    a.remove()
    b.remove()
    assert calls == ["global", "local"] * 48
    changed = m.clone()
    changed[:, 24:] += 5
    second = model.details(x, changed)
    torch.testing.assert_close(
        first["global_hidden"][:, :24], second["global_hidden"][:, :24], rtol=0, atol=0
    )
    torch.testing.assert_close(
        first["local_hidden"][:, :, :24], second["local_hidden"][:, :, :24], rtol=0, atol=0
    )
