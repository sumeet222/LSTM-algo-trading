"""Independent P027 panel/peer math, order, identity and causal-graph tests; no fits."""

import copy
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.config import fingerprint, write_json
from lstm_data.controlled_loss import LossPolicy
from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.hf1m_ft16_source import ORDER, ref
from lstm_data.neural_engine import SharedLSTM, seed_all
from lstm_data.objective_screen_attribution import cohort_masks, cohort_table
from lstm_data.objective_screen_run import record_epoch
from lstm_data.peer_screen_authority import (
    RUNS,
    ensure,
    predecessor_gate,
    require_gate,
    required_artifacts,
    validate,
)
from lstm_data.peer_screen_control import evaluate
from lstm_data.peer_screen_data import donor_map, validate_clock, validate_metadata
from lstm_data.peer_screen_metrics import allocation, paired
from lstm_data.peer_screen_models import exact_optimizer, model_for, optimizer, peer_statistics
from lstm_data.peer_screen_spec import ARMS, PARAMETERS
from lstm_data.temporal_screen_rehearsal import SyntheticStudy
from lstm_data.visualization.peer_screen_ui import guard, guard_query


@pytest.fixture(autouse=True, scope="module")
def bounded_threads():
    previous = torch.get_num_threads()
    torch.set_num_threads(4)
    yield
    torch.set_num_threads(previous)


def test_peer_statistics_numpy_loops_self_exclusion_and_population_divisor():
    x = np.random.default_rng(27042).normal(size=(2, 20, 48))
    oracle = np.empty((2, 20, 48, 2))
    for b in range(2):
        for i in range(20):
            peers = np.delete(x[b], i, axis=0)
            oracle[b, i, :, 0] = peers.mean(0)
            oracle[b, i, :, 1] = np.sqrt(((peers - peers.mean(0)) ** 2).sum(0) / 19)
    actual = peer_statistics(torch.from_numpy(x)).numpy()
    np.testing.assert_allclose(actual, oracle, rtol=1e-14, atol=1e-14)
    changed = x.copy()
    changed[:, 3] += 100
    np.testing.assert_array_equal(
        actual[:, 3], peer_statistics(torch.from_numpy(changed)).numpy()[:, 3]
    )
    assert not np.allclose(actual[:, 4], peer_statistics(torch.from_numpy(changed)).numpy()[:, 4])
    assert torch.equal(peer_statistics(torch.ones(1, 20, 48))[..., 1], torch.zeros(1, 20, 48))


@pytest.mark.parametrize("arm", ARMS)
def test_shape_exact_groups_rng_and_input_axes(arm):
    model = model_for(arm)
    groups = exact_optimizer(model, optimizer(model))
    assert groups["parameters"] == PARAMETERS[arm]
    assert model(torch.zeros(2, 20, 48, 16)).shape == (2, 20)
    with pytest.raises(ValueError):
        model(torch.zeros(40, 48, 16))
    with pytest.raises(ValueError):
        model(torch.zeros(2, 19, 48, 16))
    model.eval()
    x = torch.randn(2, 20, 48, 16)
    a = model(x)
    x[1] += 2
    torch.testing.assert_close(a[0], model(x)[0], rtol=0, atol=0)


@pytest.mark.parametrize("arm", ("A5", "A6"))
def test_exact_residual_identity_and_original_rng(arm):
    seed_all(42)
    base = SharedLSTM()
    expected_rng = torch.get_rng_state()
    model = model_for(arm).eval()
    assert torch.equal(torch.get_rng_state(), expected_rng)
    x = torch.randn(2, 20, 48, 16)
    base.eval()
    torch.testing.assert_close(model(x), base(x.reshape(-1, 48, 16)).reshape(2, 20), rtol=0, atol=0)
    h = model.encode(x)
    torch.testing.assert_close(model.exchange(h)["readout"], h, rtol=0, atol=0)


@pytest.mark.parametrize("arm", ARMS)
def test_coordinate_permutations_and_own_fixed_shift_control(arm):
    model = model_for(arm).double().eval()
    gen = torch.Generator().manual_seed(2707)
    with torch.no_grad():
        if arm == "A5":
            model.M2.copy_(torch.randn(20, 4, generator=gen, dtype=torch.float64) * 0.1)
        if arm == "A6":
            model.WO.copy_(torch.randn(16, 32, generator=gen, dtype=torch.float64) * 0.1)
    x = torch.randn(2, 20, 48, 16, dtype=torch.float64, generator=gen)
    permutation = torch.randperm(20, generator=gen)
    equivalent = copy.deepcopy(model)
    if arm == "A5":
        with torch.no_grad():
            equivalent.M1.copy_(model.M1[:, permutation])
            equivalent.M2.copy_(model.M2[permutation])
    torch.testing.assert_close(
        equivalent(x[:, permutation]), model(x)[:, permutation], rtol=1e-12, atol=1e-13
    )
    donor = x.clone()
    donor[:, 2, :, 0] += 1
    shifted = model.shifted(x, donor)
    for focal in (1, 2, 17):
        mixed = donor.clone()
        mixed[:, focal] = x[:, focal]
        torch.testing.assert_close(
            shifted[:, focal], model(mixed)[:, focal], rtol=1e-12, atol=1e-13
        )


@pytest.mark.parametrize("arm", ARMS)
def test_planted_peer_signal_graph_and_no_cross_origin_transfer(arm):
    model = model_for(arm).double().eval()
    gen = torch.Generator().manual_seed(2708)
    x = torch.randn(2, 20, 48, 16, dtype=torch.float64, generator=gen, requires_grad=True)
    with torch.no_grad():
        if arm == "A5":
            model.M2.fill_(0.1)
        if arm == "A6":
            model.WO.fill_(0.1)
    # Planted target for stock1 depends on peer0's completed M1, never a future return.
    planted = x[:, 0, -1, 0]
    assert not torch.equal(planted, torch.zeros_like(planted))
    z = model(x)
    gradient = torch.autograd.grad(z[0, 1], x, retain_graph=True)[0]
    assert gradient[0, 0].abs().sum() > 0
    assert gradient[1].abs().sum() == 0
    z[0, 1].backward()
    for name, p in model.named_parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all(), name
    for name in (
        ("M1", "M2")
        if arm == "A5"
        else ("WQ", "WK", "WV", "WO")
        if arm == "A6"
        else ("recurrent.weight_ih_l0",)
    ):
        gradient = dict(model.named_parameters())[name].grad
        assert gradient is not None
        assert gradient.abs().sum() > 0, name


def test_attention_axes_uniform_rows_and_no_t2_peer_sensitivity():
    model = model_for("A6").eval()
    h = torch.ones(3, 20, 32)
    a = model.exchange(h)["attention"]
    torch.testing.assert_close(a, torch.full_like(a, 0.05), rtol=0, atol=0)
    torch.testing.assert_close(a.sum(-1), torch.ones(3, 20), rtol=1e-6, atol=1e-7)
    base = SharedLSTM().eval()
    x = torch.randn(2, 20, 48, 16)
    changed = x.clone()
    changed[:, 0] += 5
    torch.testing.assert_close(base(x[:, 1]), base(changed[:, 1]), rtol=0, atol=0)


def test_order_scale_and_future_donors_rejected_without_numeric_source():
    validate_metadata(SYMBOLS, ORDER, 0.9, 0.9)
    for symbols, channels, scale in (
        (SYMBOLS[::-1], ORDER, 0.9),
        (SYMBOLS, ORDER[::-1], 0.9),
        (SYMBOLS, ORDER, 0.8),
    ):
        with pytest.raises(ValueError):
            validate_metadata(symbols, channels, scale, 0.9)
    rows = []
    for d, date in enumerate(pd.bdate_range("2024-02-01", periods=14)):
        for slot in (0, 1):
            if d == 1 and slot == 1:
                continue
            clock = pd.Timestamp(date.date()).tz_localize("America/New_York") + pd.Timedelta(
                hours=10 + slot, minutes=30
            )
            rows.append(
                dict(
                    origin_id=f"{d}:{slot}",
                    session_date_et=str(date.date()),
                    entry_index=100 + d * 6 + slot,
                    first_step=53 + d * 6 + slot,
                    entry_end_utc=clock.tz_convert("UTC"),
                    issuance_utc=(clock + pd.Timedelta(minutes=2)).tz_convert("UTC"),
                )
            )
    pool = pd.DataFrame(rows)
    mapping = donor_map(pool, pool)
    assert mapping.loc[mapping.origin_id.eq("10:0"), "donor_origin_id"].item() == "0:0"
    assert (
        mapping.loc[mapping.origin_id.eq("11:1"), "status"].item()
        == "SAME_SLOT_MISSING_ON_EXACT_DONOR_SESSION"
    )
    own = pool.iloc[-1].to_dict()
    donor = pool.iloc[0].to_dict()
    donor["entry_end_utc"] = own["entry_end_utc"] + pd.Timedelta(days=1)
    with pytest.raises(ValueError):
        validate_clock(own, donor)


def test_peer_shift_reweights_both_matched_populations_and_never_updates(tmp_path, monkeypatch):
    from lstm_data.objective_screen_source import ordered_targets
    from lstm_data.peer_screen_engine import predict

    monkeypatch.chdir(tmp_path)
    study = SyntheticStudy(Path("source"))
    view = study.mock_view("refit")
    model = model_for("A4").eval()
    recipe = dict(scale=study.recipe("refit")["t2_scale"])
    f = allocation(predict(model, view, "A4", recipe, {}), recipe["scale"])
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
    model = model_for("A5")
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


def test_weighted_objective_label_inverse_cohorts_and_cases(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    study = SyntheticStudy(Path("source"))
    from lstm_data.dm_quantile_cases import exact_cases
    from lstm_data.objective_screen_source import ordered_targets
    from lstm_data.optimization_screen_diagnostics import original_identity

    view = study.mock_view("refit")
    f = ordered_targets(view)
    original_identity(study, view, f)
    scale = study.recipe("refit")["t2_scale"]
    f["raw_net_output"] = np.linspace(-0.1, 0.1, len(f)).astype(np.float32)
    f["pred_original_TG20"] = scale * np.sinh(f.raw_net_output)
    f = allocation(f, scale)
    masks, cuts = cohort_masks(f, f)
    table = cohort_table(f, masks, cuts)
    assert table.loc[table.cohort.eq("ALL"), "rows"].iloc[0] == 800
    assert all(
        (
            np.stack([masks[k + "_5"] for k in ("BOTH", "NUM_ONLY", "MAD_ONLY", "NEITHER")]).sum(0)
            == 1
        )
    )
    destination = tmp_path / "cases"
    destination.mkdir()
    # Independent source exporter: controlled candle prices and observed volume schema.
    summary = exact_cases(study, view, f, pd.DataFrame(), "A4", dict(scale=scale), destination)
    assert summary["cases"] == 20 and summary["candles"] == 1040
    candles = pd.read_parquet(destination / "case_candles.parquet")
    assert {"observed_volume_sum", "volume_quality_tier"} <= set(candles)
    assert (candles.groupby("case_id").size() == 52).all()
    batch = view.batch((0, 1))
    raw = torch.zeros_like(batch.targets)
    policy = LossPolicy("T2", scale=scale)
    loss = policy.objective(raw, batch.targets, batch.origins, stock_count=20)
    oracle = np.mean(np.arcsinh(batch.targets.numpy() / scale) ** 2, axis=(1, 2))
    np.testing.assert_allclose(loss.numpy(), oracle, rtol=1e-7, atol=1e-7)
    torch.testing.assert_close(
        policy.canonical(torch.asinh(batch.targets / scale)), batch.targets, rtol=7e-7, atol=1e-7
    )


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


@pytest.mark.parametrize(
    "query",
    [
        dict(role="confirmation"),
        dict(date="2026-01-01"),
        dict(start=""),
        dict(arm=""),
        dict(ticker="INVALID"),
        dict(view="unknown"),
        dict(unrecognized="2026"),
    ],
)
def test_protected_routes_before_any_path_lookup(query):
    with patch.object(Path, "open", side_effect=AssertionError("IO before guard")):
        with pytest.raises(ValueError):
            guard_query(query)
    with pytest.raises(ValueError):
        guard("A4", "development", "AAPL", "2025-01-01", "2026-01-01")


def test_controller_rejects_absent_partial_rehearsal_or_tampered_gate(tmp_path):
    with pytest.raises(ValueError):
        ensure(tmp_path / "missing", None, RUNS[0])
    for run in RUNS[1:]:
        with pytest.raises(ValueError):
            predecessor_gate(tmp_path / "plan.json", run, [])
    gate = dict(status="PASS_P027_A4", scope="REHEARSAL_ONLY", all_roles=4)
    path = tmp_path / "gate.json"
    write_json(path, gate)
    with pytest.raises(ValueError):
        require_gate(path, "A4")
    with pytest.raises(ValueError):
        require_gate(path, "A4", rehearsal=True)
    start = dict(
        sequence=1,
        previous=fingerprint([]),
        run_id=RUNS[0],
        status="STARTED",
        global_started_pairs=57,
        effective_ceiling=200,
    )
    assert validate([start]) == [start]
    repeated = dict(start, sequence=2, previous=fingerprint([start]), global_started_pairs=58)
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
    with patch("lstm_data.peer_screen_authority.code_binding", return_value={"fixture": "bound"}):
        plan = Path("plan.json")
        write_json(plan, dict(scientific_definitions=dict(sha256="science")))
        evidence = Path("evidence.json")
        write_json(evidence, dict(mock=True))
        result = ref(evidence)
        history = [dict(run_id=RUNS[0], status="COMPLETED", detail=dict(result=result))]
        gate: dict[str, object] = dict(
            status="PASS_P027_A4",
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
        for name in required_artifacts("A4"):
            q = root / name
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_text(json.dumps({"fixture": True}))
        manifest = dict(files={"fixture": result}, execution_sha256=gate["execution_sha256"])
        (root / "ui_payload/manifest.json").write_text(json.dumps(manifest))
        (root / "ui_payload/component_receipt.json").write_text(
            json.dumps(
                dict(
                    fixture=True,
                    status="PASS_P027_ARM_COMPONENTS",
                    arm="A4",
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
        deliverables = {name: ref(root / name) for name in required_artifacts("A4")}
        gate["deliverables"] = deliverables
        path = Path("A4_immediate_gate.json")
        path.write_text(json.dumps(gate))
        predecessor_gate(plan, RUNS[1], history)
        for name in (
            "cohorts.parquet",
            "ui_payload/component_receipt.json",
            "refit/case_peer_M1_operands.parquet",
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
    import lstm_data.peer_screen_authority as authority

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
        global_started_pairs=57,
        effective_ceiling=200,
        plan=ref(plan),
        authority=ref(approval),
        previous_journal=ref(prior),
    )
    journal.write_text(json.dumps(start) + "\n")
    plan.write_text("CHANGED_BINDING")
    authority.append_failure(plan, approval, RUNS[0], ValueError("EXACT_BINDING_CHANGED"))
    history = authority.rows()
    assert history[-1]["status"] == "FAILED" and history[-1]["global_started_pairs"] == 57
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


@pytest.mark.parametrize("arm", ("A5", "A6"))
def test_zero_exchange_has_exactly_zero_peer_control_response(arm):
    model = model_for(arm).eval()
    x = torch.randn(3, 20, 48, 16)
    donor = torch.randn_like(x)
    with torch.inference_mode():
        torch.testing.assert_close(model.shifted(x, donor), model.shifted(x, x), rtol=0, atol=0)


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
