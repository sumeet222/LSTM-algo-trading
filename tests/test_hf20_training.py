"""Independent HF20 panel, transform, authority and safe-checkpoint oracles."""

import json
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.config import fingerprint
from lstm_data.controlled_loss import LossPolicy
from lstm_data.hf20_loader import HF20View
from lstm_data.hf20_training_authority import IDS, read_rows, validate_approval
from lstm_data.hf20_training_data import TrainingView, fit_scale
from lstm_data.hf20_training_run import checkpoint, reload_checkpoint
from lstm_data.neural_engine import SharedLSTM, batch_prediction, session_losses
from lstm_data.neural_lifecycle import EarlyStop, epoch_pass, state_hash


@pytest.fixture(autouse=True)
def threads():
    old = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(old)


def view() -> TrainingView:
    rows = pd.DataFrame(
        [
            dict(session="2025-01-08", origin=1, last_step=47, day_index=0, label_ready=True),
            dict(session="2025-01-08", origin=2, last_step=48, day_index=0, label_ready=True),
            dict(session="2025-01-09", origin=1, last_step=49, day_index=1, label_ready=True),
        ]
    )
    targets = np.arange(80, dtype=np.float32).reshape(2, 20, 2) / 10
    return TrainingView(
        HF20View(
            np.ones((50, 20, 15), np.float32),
            np.ones((2, 20, 2), np.float32),
            targets,
            np.zeros(50, dtype=int),
            rows,
            "PREP",
            "RECIPE",
        )
    )


def test_whole20_and_unequal_origin_day_weighting():
    batch = view().batch((0, 1))
    assert batch.inputs.shape == (2, 2, 20, 48, 16)
    assert batch.origins.tolist() == [[True, True], [True, False]]
    p = torch.tensor([[[2.0] * 20, [4.0] * 20], [[6.0] * 20, [0.0] * 20]])
    loss = session_losses(p, torch.zeros_like(p), batch.origins, stock_count=20)
    assert loss.tolist() == [10, 36] and float(loss.mean()) == 23
    with pytest.raises(ValueError):
        session_losses(p, torch.zeros_like(p), batch.origins)
    model = SharedLSTM()
    assert sum(p.numel() for p in model.parameters()) == 6433
    assert batch_prediction(model, batch).shape == (2, 2, 20)
    with pytest.raises(ValueError):
        replace(batch, stock_count=5).validate()


def test_t2_unique_train_scale_and_extreme_once_inverse():
    v = view()
    y = np.stack([v.source.targets[0, :, 0], v.source.targets[0, :, 1], v.source.targets[1, :, 0]])
    fitted = fit_scale(v, "inner_train")
    assert fitted["observations"] == 60
    assert fitted["scale"] == float(np.median(np.abs(y.astype(np.float64))))
    with pytest.raises(ValueError):
        fit_scale(v, "development")
    policy = LossPolicy("T2", scale=fitted["scale"])
    for dtype in (torch.float32, torch.float64):
        truth = torch.tensor([-1e8, -20.0, -1.0, 0.0, 1.0, 20.0, 1e8], dtype=dtype)
        assert torch.allclose(policy.canonical(torch.asinh(truth / policy.scale)), truth, rtol=3e-6)
    with pytest.raises(ValueError):
        policy.canonical(torch.tensor([1000.0]))
    zero = replace(v.source, targets=np.zeros_like(v.source.targets))
    assert fit_scale(TrainingView(zero), "refit")["scale"] == 1e-6


def test_shared_epoch_canonical_monitor_and_telemetry():
    v = view()
    model = SharedLSTM()
    policy = LossPolicy("T2", scale=0.01)
    telemetry = []
    r = epoch_pass(model, v, 1, 42, policy=policy, batch_sink=telemetry.append)
    model.eval()
    with torch.no_grad():
        b = v.batch((0, 1))
        logits = batch_prediction(model, b)
        canonical = policy.canonical(logits)
        expected = session_losses(canonical, b.targets, b.origins, stock_count=20).mean()
    assert r["mean_session_mse"] == pytest.approx(float(expected), rel=1e-7)
    assert r["optimizer_objective"] != pytest.approx(r["mean_session_mse"])
    assert r["optimizer_steps"] == 0 and telemetry[0]["optimizer_step"] is False
    selector = EarlyStop()
    assert selector.observe(1.0)
    assert not selector.observe(0.999)
    assert selector.selected == 1


def test_safe_checkpoint_order_stage_and_scale_guard(tmp_path):
    model = SharedLSTM()
    binding = dict(target="TG20", symbols=list(range(20)), stage="REFIT_FINAL", scale=0.8)
    path = tmp_path / "model.pt"
    manifest = checkpoint(path, model, binding)
    assert state_hash(reload_checkpoint(path, binding, manifest)) == state_hash(model)
    for wrong in (
        dict(binding, target="TG0"),
        dict(binding, symbols=list(reversed(range(20)))),
        dict(binding, stage="CALIBRATION_SELECTED"),
        dict(binding, scale=0.9),
    ):
        with pytest.raises(ValueError):
            reload_checkpoint(path, wrong, manifest)


def test_no_approval_and_forged_receipt(tmp_path):
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps(dict(scope="ONLY_TWO_PAIRS")))
    with pytest.raises(ValueError, match="NO_LIVE_APPROVAL"):
        validate_approval(plan, None)
    receipt = tmp_path / "receipt.json"
    receipt.write_text(
        json.dumps(dict(status="APPROVED", actor_type="agent", approved_runs=list(IDS)))
    )
    with pytest.raises(ValueError, match="LIVE_TWO_PAIR"):
        validate_approval(plan, receipt)


def test_journal_chain_duplicate_order_and_ceiling(tmp_path):
    path = tmp_path / "journal.jsonl"
    rows = []

    def event(name, status):
        starts = sum(r["status"] == "STARTED" for r in rows) + int(status == "STARTED")
        rows.append(
            dict(
                sequence=len(rows) + 1,
                previous=fingerprint(rows),
                run_id=name,
                status=status,
                global_started_pairs=28 + starts,
                effective_ceiling=200,
            )
        )
        path.write_text("".join(json.dumps(r) + "\n" for r in rows))

    event(IDS[0], "STARTED")
    assert len(read_rows(path)) == 1
    event(IDS[0], "STARTED")
    with pytest.raises(ValueError):
        read_rows(path)
    rows.clear()
    event(IDS[1], "STARTED")
    with pytest.raises(ValueError):
        read_rows(path)
    rows.clear()
    event(IDS[0], "STARTED")
    rows[0]["effective_ceiling"] = 201
    path.write_text(json.dumps(rows[0]) + "\n")
    with pytest.raises(ValueError):
        read_rows(path)


def test_dryrun_without_plan_or_authority_has_no_optimizer(tmp_path):
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "lstm_data.hf20_training_run",
            "--plan",
            str(tmp_path / "absent"),
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout)["optimizer_steps"] == 0
    assert not (tmp_path / "absent").exists()
