"""P021 mathematical/authority oracles; no optimizer steps or empirical fitting."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.config import fingerprint
from lstm_data.controlled_loss import LossPolicy
from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.hf1m_ft16_loader import ModelInput, load_model_input
from lstm_data.hf1m_ft16_source import COMMON, read_hourly
from lstm_data.hf1m_training_authority import IDS, ensure, read_rows
from lstm_data.hf1m_training_data import TrainingView
from lstm_data.hf1m_training_run import epoch_pass, predictions
from lstm_data.neural_engine import SharedLSTM, optimizer, seed_all, session_losses
from lstm_data.neural_lifecycle import EarlyStop
from lstm_data.neural_lifecycle import epoch_pass as original_epoch


@pytest.fixture
def view() -> TrainingView:
    rows = pd.DataFrame(
        dict(
            origin_id=["a", "b", "c"],
            session_date_et=["2020-01-02", "2020-01-02", "2020-01-03"],
            entry_index=[47, 48, 53],
            first_step=[0, 1, 6],
            entry_end_utc=["2020-01-02T15:30:00Z", "2020-01-02T16:30:00Z", "2020-01-03T15:30:00Z"],
        )
    )
    common = np.arange(60 * 20 * 15, dtype=np.float32).reshape(60, 20, 15) / 100000
    m2 = np.arange(60 * 20 * 2, dtype=np.float32).reshape(60, 20, 2) / 10000
    records = []
    for k, o in enumerate(rows.origin_id):
        for j, s in enumerate(SYMBOLS):
            records.append(
                dict(origin_id=o, ticker=s, TG20=(j - 10) * (k + 1) / 10, label_eligible=True)
            )
    return TrainingView(
        ModelInput(rows, common, m2, pd.DataFrame(records), "inner", dict(t2_scale=0.9)),
        "inner_train",
    )


def test_vectorized_gather_matches_released_indexed_loader(view: TrainingView) -> None:
    for positions in ((0,), (1, 2), (2, 0, 1)):
        actual = view.origin_batch(positions)
        expected = view.source.batch(positions)
        assert np.array_equal(actual["x"], expected["x"])
        assert np.array_equal(actual["y"], expected["y"])
    b = view.batch((1, 0))
    assert b.origins.tolist() == [[True, False], [True, True]]
    assert torch.equal(b.targets[1, 1], torch.from_numpy(view.labels[1]))
    assert b.inputs.shape == (2, 2, 20, 48, 16)
    assert len(COMMON) == 15


@pytest.mark.parametrize("arm", ["C0", "T2"])
def test_observed_epoch_matches_frozen_engine_without_optimizer(
    view: TrainingView, arm: str
) -> None:
    torch.set_num_threads(2)
    seed_all(42)
    model = SharedLSTM()
    policy = LossPolicy(arm, scale=0.9)
    a = original_epoch(model, view, 1, 42, policy=policy)
    b, steps = epoch_pass(model, view, 1, 42, policy)
    assert b["original_mse"] == pytest.approx(a["mean_session_mse"], abs=1e-7)
    assert b["objective"] == pytest.approx(a["optimizer_objective"], abs=1e-7)
    assert b["optimizer_steps"] == 0 and all(not s["optimizer_step"] for s in steps)
    assert all(p.grad is None for p in model.parameters())


def test_session_weighting_does_not_overweight_two_origin_day() -> None:
    y = torch.zeros((2, 2, 20))
    pred = torch.ones_like(y)
    pred[0] *= 2
    pred[1, 0] *= 4
    mask = torch.tensor([[True, True], [True, False]])
    assert session_losses(pred, y, mask, stock_count=20).mean().item() == 10
    assert float(((pred - y).square()[mask]).mean()) != 10


@pytest.mark.parametrize("arm", ["C0", "T2"])
def test_full_prediction_export_retains_both_named_join_keys(
    view: TrainingView, monkeypatch: pytest.MonkeyPatch, arm: str
) -> None:
    from lstm_data import hf1m_training_run

    monkeypatch.setattr(hf1m_training_run, "COUNTS", {"inner_train": (3, 2)})
    model = SharedLSTM()
    f = predictions(model, view, LossPolicy(arm, scale=0.9), dict(run_id="synthetic-export-oracle"))
    assert len(f) == 60 and set(f.ticker) == set(SYMBOLS)
    assert f.columns[:2].tolist() == ["origin_id", "ticker"]
    assert not f.duplicated(["origin_id", "ticker"]).any()
    assert f.inverse_count.eq(int(arm == "T2")).all()
    assert all(p.grad is None for p in model.parameters())


def test_t2_inverse_and_objective_independent_scalar_oracle() -> None:
    target = torch.tensor([[[-10.0, 0.0, 2.0] + [1.0] * 17, [0.0] * 20]])
    mask = torch.tensor([[True, False]])
    s = 0.906406830018944
    z = torch.asinh(target / s)
    policy = LossPolicy("T2", scale=s)
    assert float(policy.objective(z, target, mask, stock_count=20).sum()) == 0
    assert torch.allclose(policy.canonical(z), target, rtol=1e-6, atol=1e-6)


def test_architecture_adam_groups_and_minimum_epochs_are_not_minimum_selection() -> None:
    seed_all(42)
    model = SharedLSTM()
    opt = optimizer(model)
    assert sum(p.numel() for p in model.parameters()) == 6433
    assert model.dropout.p == 0.1 and model.lstm.dropout == 0
    assert [g["weight_decay"] for g in opt.param_groups] == [0.01, 0]
    assert not opt.state
    stop = EarlyStop()
    for value in (1.0, 0.9995, *([1.0] * 10)):
        stop.observe(value)
    assert stop.selected == 1 and stop.raw_epoch == 2 and stop.epoch == 12


@pytest.mark.parametrize("split", ["confirmation", "heldout", "test", "2026"])
def test_protected_role_rejected_before_contract_read(tmp_path: Path, split: str) -> None:
    with pytest.raises(ValueError, match="PROTECTED"):
        load_model_input(tmp_path / "does_not_exist", split=split, fit_version="refit")
    with pytest.raises(ValueError, match="PROTECTED"):
        read_hourly({}, stop="2026-02-01")


def test_no_live_approval_stops_before_any_numeric_loader(tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    plan.write_text("{}")
    with pytest.raises(ValueError, match="LIVE_APPROVAL_REQUIRED_ZERO_STEPS"):
        ensure(plan, None, IDS[0])


def test_journal_counts_failures_and_blocks_retries(tmp_path: Path) -> None:
    rows = []
    for status in ("STARTED", "FAILED_AFTER_START"):
        rows.append(
            dict(
                sequence=len(rows) + 1,
                previous=fingerprint(rows),
                run_id=IDS[0],
                status=status,
                global_started_pairs=33,
                effective_ceiling=200,
            )
        )
    path = tmp_path / "journal.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert read_rows(path)[-1]["global_started_pairs"] == 33
    rows.append(
        dict(
            sequence=3,
            previous=fingerprint(rows),
            run_id=IDS[0],
            status="STARTED",
            global_started_pairs=34,
            effective_ceiling=200,
        )
    )
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    with pytest.raises(ValueError, match="NO_EXTRA_START"):
        read_rows(path)


def test_recovery_requires_new_live_authority_and_preserves_charged_start(tmp_path: Path) -> None:
    from lstm_data.hf1m_training_recovery import ensure as recovery_ensure
    from lstm_data.hf1m_training_recovery import read_rows as recovery_rows

    plan = tmp_path / "plan.json"
    plan.write_text("{}")
    with pytest.raises(ValueError, match="CONTINUATION_LIVE_APPROVAL_REQUIRED"):
        recovery_ensure(plan, None, IDS[0])
    events = []
    for name in IDS:
        statuses = (
            ("RESUMED_EXISTING_START", "REFITTING", "COMPLETED")
            if name == IDS[0]
            else ("STARTED", "CALIBRATED", "REFITTING", "COMPLETED")
        )
        for status in statuses:
            starts = sum(r["status"] == "STARTED" for r in events) + int(status == "STARTED")
            events.append(
                dict(
                    sequence=len(events) + 1,
                    previous=fingerprint(events),
                    run_id=name,
                    status=status,
                    global_started_pairs=33 + starts,
                    effective_ceiling=200,
                )
            )
    path = tmp_path / "recovery.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in events))
    actual = recovery_rows(path)
    assert actual[0]["global_started_pairs"] == 33 and actual[-1]["global_started_pairs"] == 36
    assert sum(r["status"] == "STARTED" for r in actual) == 3
