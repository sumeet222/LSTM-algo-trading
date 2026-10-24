"""P026 independent causal/model/math/authority regressions; no optimizer updates."""

import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.config import fingerprint, write_json
from lstm_data.controlled_loss import LossPolicy
from lstm_data.hf1m_ft16_source import ref
from lstm_data.neural_engine import SharedLSTM, seed_all
from lstm_data.neural_lifecycle import EarlyStop
from lstm_data.objective_screen_attribution import cohort_masks, cohort_table
from lstm_data.objective_screen_run import record_epoch
from lstm_data.temporal_screen_authority import ensure, predecessor_gate, require_gate, validate
from lstm_data.temporal_screen_engine import save_checkpoint
from lstm_data.temporal_screen_metrics import allocation, paired
from lstm_data.temporal_screen_models import causal_means, exact_optimizer, model_for, optimizer
from lstm_data.temporal_screen_rehearsal import SyntheticStudy
from lstm_data.temporal_screen_spec import ARMS, PARAMETERS, RUNS
from lstm_data.visualization.temporal_screen_ui import guard, guard_query


@pytest.fixture(autouse=True)
def cpu_threads():
    torch.set_num_threads(4)


@pytest.mark.parametrize("arm", ARMS)
def test_model_exact_dimensions_rng_checkpoint_gradients(tmp_path, arm, monkeypatch):
    monkeypatch.chdir(tmp_path)
    model = model_for(arm).eval()
    assert sum(p.numel() for p in model.parameters()) == PARAMETERS[arm]
    settings = exact_optimizer(model, optimizer(model))
    assert settings["groups"][0]["lr"] == json.loads(json.dumps(0.001))
    x = torch.randn(4, 48, 16, requires_grad=True)
    y = model(x)
    assert y.shape == (4,) and y.dtype == torch.float32
    assert torch.equal(y, model(x))
    changed = x.detach().clone()
    changed[1:] += 100
    assert torch.equal(y[:1], model(changed)[:1])
    y.sum().backward()
    assert x.grad is not None and torch.isfinite(x.grad).all()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    rng = torch.get_rng_state().clone()
    reference, loaded = save_checkpoint(Path("model.pt"), model, arm, dict(scope="REHEARSAL_ONLY"))
    assert torch.equal(rng, torch.get_rng_state())
    loaded.eval()
    assert torch.equal(y, loaded(x))
    with pytest.raises(FileExistsError):
        save_checkpoint(Path("model.pt"), model, arm, {})
    path = Path(reference["path"])
    path.write_bytes(path.read_bytes() + b"fault")
    from lstm_data.hf1m_ft16_source import checked

    with pytest.raises(ValueError):
        checked(reference)
    with pytest.raises(ValueError):
        model(torch.zeros(4, 47, 16))
    with pytest.raises(ValueError):
        model(torch.full((1, 48, 16), float("nan")))


@pytest.mark.parametrize("arm", ("A1", "A2"))
def test_exact_reference_identity_and_no_rng_consumption(arm):
    seed_all(42)
    base = SharedLSTM().eval()
    expected_rng = torch.get_rng_state().clone()
    model = model_for(arm).eval()
    assert torch.equal(expected_rng, torch.get_rng_state())
    x = torch.linspace(-1, 1, 5 * 48 * 16).reshape(5, 48, 16)
    assert torch.equal(model(x), base(x))
    assert torch.equal(
        model.recurrent.state_dict()["weight_ih_l0"], base.lstm.state_dict()["weight_ih_l0"]
    )


def test_attention_exact_formula_gamma_and_query_flow():
    model = model_for("A1").eval()
    x = torch.randn(4, 48, 16)
    model(x).square().sum().backward()
    assert model.query.grad is not None and torch.count_nonzero(model.query.grad) == 0
    assert model.gamma.grad is not None and abs(float(model.gamma.grad)) > 0
    with torch.no_grad():
        model.gamma.fill_(0.25)
    model.zero_grad(set_to_none=True)
    d = model.details(x)
    oracle = (model.norm(d["sequence"]) @ model.query / np.sqrt(32)).softmax(1)
    assert torch.equal(oracle, d["attention"])
    torch.testing.assert_close(oracle.sum(1), torch.ones(4))
    model(x).square().sum().backward()
    assert model.query.grad is not None and model.query.grad.norm() > 0
    changed = x.clone()
    changed[:, 0] += 5
    assert not torch.equal(model.details(changed)["attention"], oracle)


def test_multiscale_scalar_prefix_oracle_causality_branch_gradients():
    x = torch.arange(48 * 16, dtype=torch.float32).reshape(1, 48, 16) / 100
    m = causal_means(x)
    for s in (0, 1, 3, 4, 10, 11, 12, 47):
        for j, width in enumerate((1, 4, 12)):
            torch.testing.assert_close(
                m[:, s, j * 16 : (j + 1) * 16],
                x[:, max(0, s - width + 1) : s + 1].mean(1),
                rtol=0,
                atol=0,
            )
    changed = x.clone()
    changed[:, 24:] += 100
    assert torch.equal(m[:, :24], causal_means(changed)[:, :24])
    model = model_for("A2")
    model(x).square().sum().backward()
    assert model.mixer.weight.grad is not None
    assert all(model.mixer.weight.grad[:, j * 16 : (j + 1) * 16].norm() > 0 for j in range(3))


def test_gru_reference_and_early_event_witness():
    model = model_for("A3").eval()
    x = torch.randn(4, 48, 16, requires_grad=True)
    _, state = model.recurrent(x)
    expected = model.head(state[-1]).squeeze(-1)
    assert torch.equal(model(x), expected)
    assert model.recurrent.dropout == 0 and model.recurrent.num_layers == 1
    for arm in ARMS:
        m = model_for(arm).eval()
        early = torch.zeros(2, 48, 16)
        early[1, 8:12, 0] = 10
        assert m(early)[0] != m(early)[1]


def test_original_selector_strict_boundary_raw_best_patience_maximum():
    s = EarlyStop()
    assert s.observe(10)
    assert not s.observe(9.99)  # equality is NOT qualifying in original T2
    assert s.raw_epoch == 2 and s.selected == 1
    while s.status == "CALIBRATING":
        s.observe(9.995)
    assert s.epoch == 12 and s.selected == 1 and s.status == "PATIENCE_STOP"
    cap = EarlyStop()
    for e in range(60):
        cap.observe(10 * 0.99**e)
    assert cap.status == "MAX_EPOCHS_REACHED" and cap.selected == 60
    for invalid in (None, float("nan"), float("inf"), -1):
        with pytest.raises(ValueError):
            EarlyStop().observe(invalid)


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
    summary = exact_cases(study, view, f, pd.DataFrame(), "A1", dict(scale=scale), destination)
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
        guard("A1", "development", "AAPL", "2025-01-01", "2026-01-01")


def test_controller_rejects_absent_partial_rehearsal_or_tampered_gate(tmp_path):
    with pytest.raises(ValueError):
        ensure(tmp_path / "missing", None, RUNS[0])
    for run in RUNS[1:]:
        with pytest.raises(ValueError):
            predecessor_gate(tmp_path / "plan.json", run, [])
    gate = dict(status="PASS_P026_A1", scope="REHEARSAL_ONLY", all_roles=4)
    path = tmp_path / "gate.json"
    write_json(path, gate)
    with pytest.raises(ValueError):
        require_gate(path, "A1")
    with pytest.raises(ValueError):
        require_gate(path, "A1", rehearsal=True)
    start = dict(
        sequence=1,
        previous=fingerprint([]),
        run_id=RUNS[0],
        status="STARTED",
        global_started_pairs=54,
        effective_ceiling=200,
    )
    assert validate([start]) == [start]
    repeated = dict(start, sequence=2, previous=fingerprint([start]), global_started_pairs=55)
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
    with patch(
        "lstm_data.temporal_screen_authority.code_binding", return_value={"fixture": "bound"}
    ):
        plan = Path("plan.json")
        write_json(plan, dict(scientific_definitions=dict(sha256="science")))
        evidence = Path("evidence.json")
        write_json(evidence, dict(mock=True))
        result = ref(evidence)
        history = [dict(run_id=RUNS[0], status="COMPLETED", detail=dict(result=result))]
        gate = dict(
            status="PASS_P026_A1",
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
        )
        gate.update({key: True for key in fields})
        path = Path("A1_immediate_gate.json")
        path.write_text(json.dumps(gate))
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


@pytest.mark.skipif(
    not Path("configs/track_a_hf1m_long_visualization_v1.json").exists(),
    reason="pinned private P020/P021 context required",
)
def test_saved_t2_checkpoints_are_exact_attention_and_mixer_identities():
    from lstm_data.config import digest
    from lstm_data.objective_screen_source import scoped_view
    from lstm_data.temporal_screen_spec import P021
    from lstm_data.visualization.hf1m_long import LongStudy

    study = LongStudy.discover(Path.cwd())
    result = json.loads((P021 / "HF1M-LONG-TM0-T2-S42-DEV1/run_result.json").read_text())
    for role in ("inner_train", "inner_validation", "refit", "development"):
        checkpoint = result["calibration" if role.startswith("inner") else "refit"]["checkpoint"]
        path = Path(checkpoint["path"])
        assert digest(path) == checkpoint["sha256"]
        state = torch.load(path, weights_only=True, map_location="cpu")["model"]
        reference = SharedLSTM().eval()
        reference.load_state_dict(state)
        view = scoped_view(study, role, stage=7)
        x = torch.from_numpy(
            view.origin_batch((0, len(view.source.rows) - 1))["x"].reshape(-1, 48, 16)
        )
        with torch.inference_mode():
            expected = reference(x)
            for arm in ("A1", "A2"):
                model = model_for(arm).eval()
                model.recurrent.load_state_dict(reference.lstm.state_dict())
                model.head.load_state_dict(reference.head.state_dict())
                assert torch.equal(model(x), expected), (arm, role)
