"""Small fabricated Package011 scientific oracles; no genuine optimizer work."""

from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.baseline_ridge import windows
from lstm_data.batch_telemetry import BatchTelemetry
from lstm_data.config import digest, fingerprint
from lstm_data.controlled_authority import (
    JOURNAL,
    QUEUE,
    SEAL,
    ControlledAuthority,
    approval_scope,
    contract,
    journal_rows,
    run_id,
)
from lstm_data.controlled_loss import LossPolicy, fit_policy
from lstm_data.ft0_transforms import identity
from lstm_data.neural_data import IndexedOrigin
from lstm_data.neural_engine import (
    SharedLSTM,
    batch_prediction,
    clip,
    optimizer,
    seed_all,
    session_losses,
)
from lstm_data.neural_lifecycle import EarlyStop
from lstm_data.pretraining_policy import PreparationAuthority
from lstm_data.real_bridge_authority import BridgeReview, require_training
from lstm_data.real_bridge_data import RealInputView, tensor_hash


def fixture_view() -> RealInputView:
    window = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))[0]
    values = torch.arange(240 * 16, dtype=torch.float32).reshape(240, 16) / 1000
    indices = tuple(tuple(range(i * 48, (i + 1) * 48)) for i in range(5))
    rows = (
        IndexedOrigin("2023-01-03", 1, indices, (-82.0, -2.0, 0.0, 2.0, 82.0)),
        IndexedOrigin("2023-01-03", 2, indices, (1.0, 2.0, 3.0, 4.0, 5.0)),
        IndexedOrigin("2023-01-04", 1, indices, (0.0, 0.0, 0.0, 0.0, 0.0)),
    )
    days = ("2023-01-03", "2023-01-04")
    return RealInputView(
        "SYN:R",
        "SYN:P",
        window,
        values,
        rows,
        days,
        tensor_hash(values),
        identity(["SYN:R", "SYN:P", window, rows, days, ()]),
        (),
    )


def test_huber_values_derivative_and_unequal_session_weighting():
    p = torch.tensor([[[0.0] * 5, [0.0] * 5], [[0.0] * 5, [0.0] * 5]], requires_grad=True)
    t = torch.tensor([[[1.0] * 5, [3.0] * 5], [[4.0] * 5, [0.0] * 5]])
    origins = torch.tensor([[True, True], [True, False]])
    losses = LossPolicy("H1").objective(p, t, origins)
    assert losses.tolist() == [2.25, 6.0]
    losses.mean().backward()
    assert p.grad is not None
    assert p.grad[0, 0, 0].item() == pytest.approx(-0.05)
    assert p.grad[1, 0, 0].item() == pytest.approx(-0.2)
    assert p.grad[1, 1, 0].item() == 0
    smooth = torch.nn.functional.smooth_l1_loss(p, t, reduction="none", beta=2.0)
    huber = torch.nn.functional.huber_loss(p, t, reduction="none", delta=2.0)
    assert torch.equal(huber, 2 * smooth)


def test_tail_fit_prefix_identity_cap_and_raw_immutability():
    v = fixture_view()
    before = [r.targets for r in v.rows]
    a = fit_policy(v, "T1")
    assert a == fit_policy(v, "T1")
    assert a["policy"]["cap"] == np.quantile(
        np.abs(np.array(before).flatten()), 0.99, method="linear"
    )
    full = replace(v, preparation_id="SYN:FULL", window=replace(v.window, phase="REFIT"))
    assert fit_policy(full, "T1")["parameter_id"] != a["parameter_id"]
    with pytest.raises(ValueError, match="TRAINING_PREFIX"):
        fit_policy(replace(v, window=replace(v.window, phase="INNER_VALIDATION")), "T1")
    batch = v.batch((0, 1))
    raw = batch.targets.clone()
    p = torch.zeros_like(raw)
    loss = LossPolicy("T1", cap=2.0).objective(p, raw, batch.origins)
    assert torch.equal(raw, batch.targets) and before == [r.targets for r in v.rows]
    assert loss[0] < session_losses(p, raw, batch.origins)[0]


def test_asinh_roundtrip_floor_gradient_and_overflow_fail_closed():
    raw = torch.tensor([-82.0, -2.0, 0.0, 2.0, 82.0])
    for s in (1e-6, 0.7, 1.0):
        policy = LossPolicy("T2", scale=s)
        z = torch.asinh(raw / s).requires_grad_()
        restored = policy.canonical(z)
        assert torch.allclose(restored, raw, rtol=3e-6, atol=1e-6)
        restored.sum().backward()
        assert z.grad is not None and torch.isfinite(z.grad).all()
    v = fixture_view()
    zeros = replace(v, rows=tuple(replace(r, targets=(0.0,) * 5) for r in v.rows))
    assert fit_policy(zeros, "T2")["policy"]["scale"] == 1e-6
    with pytest.raises(ValueError, match="NONFINITE"):
        LossPolicy("T2").canonical(torch.tensor([100.0]))


def test_canonical_selector_not_transformed_loss():
    selector = EarlyStop()
    for mse in (8.0, 7.0, 7.001, 6.999):
        selector.observe(mse)
    assert selector.selected == 2 and selector.raw_epoch == 4
    policy = LossPolicy("T2", scale=0.5)
    z = torch.tensor([[[1.0] * 5, [0.0] * 5]])
    truth = torch.ones_like(z)
    origins = torch.tensor([[True, False]])
    assert not torch.equal(
        policy.objective(z, truth, origins), session_losses(policy.canonical(z), truth, origins)
    )


@pytest.mark.parametrize("cap", [1.0, 5.0])
def test_clip_hand_oracle_and_true_norm(cap: float):
    parameter = torch.nn.Parameter(torch.zeros(2))
    parameter.grad = torch.tensor([3.0, 4.0])
    norm = torch.nn.utils.clip_grad_norm_([parameter], cap, error_if_nonfinite=True)
    assert float(norm) == 5.0
    assert torch.allclose(parameter.grad, torch.tensor([3.0, 4.0]) * min(1.0, cap / (5.0 + 1e-6)))


def test_c0_numerical_update_observer_rng_and_initial_state(tmp_path: Path):
    torch.set_num_threads(1)
    view = fixture_view()
    batch = view.batch((0, 1))
    states = []
    rngs = []
    opts = []
    initials = []
    for controlled in (False, True):
        seed_all(123)
        model = SharedLSTM()
        opt = optimizer(model)
        initials.append(identity({k: v.tolist() for k, v in model.state_dict().items()}))
        pred = batch_prediction(model, batch)
        by_day = session_losses(pred, batch.targets, batch.origins)
        objective = (
            LossPolicy("C0").objective(pred, batch.targets, batch.origins) if controlled else by_day
        )
        opt.zero_grad(set_to_none=True)
        objective.mean().backward()
        norm = (
            float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True))
            if controlled
            else clip(model)
        )
        opt.step()
        if controlled:
            BatchTelemetry(
                tmp_path / "batch.csv", "SYN:C0", "TM0", "CALIBRATION", seed=123, arm="C0"
            ).record(1, 1, batch, by_day.detach(), norm)
        states.append({k: v.detach().clone() for k, v in model.state_dict().items()})
        rngs.append(torch.get_rng_state().clone())
        opts.append(opt.state_dict())
    assert initials[0] == initials[1]
    assert all(torch.equal(v, states[1][k]) for k, v in states[0].items())
    assert torch.equal(rngs[0], rngs[1]) and opts[0]["param_groups"] == opts[1]["param_groups"]
    for k, state in opts[0]["state"].items():
        assert all(torch.equal(v, opts[1]["state"][k][n]) for n, v in state.items())
    for arm in ("H1", "T1", "T2", "O1"):
        seed_all(123)
        m = SharedLSTM()
        assert identity({k: v.tolist() for k, v in m.state_dict().items()}) == initials[0]
        assert contract(arm, "WF1", 123)["parameters"] == 6433


def test_approval_required_before_any_real_step():
    assert len(QUEUE) == 18 and QUEUE[8:10] == (("C0", "WF1", 123), ("C0", "WF2", 123))
    with pytest.raises(ValueError):
        require_training(object.__new__(ControlledAuthority), "START_PAIR", "SYN:I")
    with pytest.raises(ValueError, match="HUMAN_BATCH_APPROVAL"):
        approval_scope({"sha256": "SYN:PLAN"}, {}, {"runs": []})


def test_failed_started_identity_spends_and_cannot_retry(tmp_path: Path, monkeypatch):
    (tmp_path / "configs").mkdir()
    (tmp_path / "reports/audit").mkdir(parents=True)
    pointer = tmp_path / "configs/CURRENT_EXPERIMENT_REGISTRY.json"
    pointer.write_text("{}")
    review = BridgeReview(
        tmp_path, {}, {}, {}, PreparationAuthority(tmp_path, {}, {}, {}, {}), object()
    )
    arm, fold, seed = QUEUE[0]
    descriptor = dict(
        run_id=run_id(arm, fold, seed), contract=contract(arm, fold, seed), input_id="SYN:I"
    )
    plan = dict(
        runs=[descriptor],
        registry_definition={},
        prior_pointer_snapshot=dict(sha256=digest(pointer)),
    )
    token = ControlledAuthority(review, {}, plan, {}, {}, run_id(arm, fold, seed), SEAL)
    monkeypatch.setattr(ControlledAuthority, "ensure", lambda *args: None)
    token.append("STARTED", dict(synthetic=True))
    token.append("FAILED", dict(synthetic=True))
    assert journal_rows(tmp_path / JOURNAL)[-1]["global_started_pairs"] == 7
    with pytest.raises(ValueError, match="NO_RETRY"):
        token.append("STARTED", {})
    rows = journal_rows(tmp_path / JOURNAL)
    rows[-1]["global_started_pairs"] = 6
    (tmp_path / JOURNAL).write_text("\n".join(__import__("json").dumps(r) for r in rows) + "\n")
    with pytest.raises(ValueError, match="GLOBAL_BUDGET"):
        journal_rows(tmp_path / JOURNAL)
    assert rows[0]["previous"] == fingerprint([])


def test_actual_epoch_c0_matches_legacy_branch_and_t2_is_inverted_once(monkeypatch, tmp_path: Path):
    import time

    from lstm_data.real_bridge_authority import TrainingAuthority
    from lstm_data.real_bridge_run import epoch_pass

    view = fixture_view()
    params = {s: fit_policy(view, "C0") for s in ("inner", "refit")}
    desc: dict = dict(
        run_id="SYN:PAIR", contract={**contract("C0", "WF1", 123)}, target_parameters=params
    )
    token = ControlledAuthority(
        object.__new__(BridgeReview), {}, dict(runs=[desc]), {}, {}, "SYN:PAIR", SEAL
    )
    monkeypatch.setattr("lstm_data.real_bridge_run.require_training", lambda *args: None)
    states = []
    rngs = []
    for permit in (object.__new__(TrainingAuthority), token):
        # Compare seed42 sampler to legacy, with identical starting weights and RNG.
        desc["contract"]["seed"] = 42
        seed_all(42)
        model = SharedLSTM()
        opt = optimizer(model)
        epoch_pass(permit, "SYN:I", model, view, 1, opt, time.monotonic() + 30)
        states.append({k: v.detach().clone() for k, v in model.state_dict().items()})
        rngs.append(torch.get_rng_state().clone())
    assert all(torch.equal(v, states[1][k]) for k, v in states[0].items())
    assert torch.equal(rngs[0], rngs[1])
    params = {
        s: {"preparation_id": view.preparation_id, "policy": dict(arm="T2", cap=1.0, scale=0.5)}
        for s in ("inner", "refit")
    }
    desc["target_parameters"] = params
    desc["contract"] = contract("T2", "WF1", 42)
    monkeypatch.setattr(
        "lstm_data.real_bridge_run.batch_prediction", lambda m, b: torch.ones_like(b.targets)
    )
    result = epoch_pass(token, "SYN:I", SharedLSTM(), view, 1, None, time.monotonic() + 30)
    expected = 0.5 * torch.sinh(torch.tensor(1.0)).item()
    assert all(v == pytest.approx(expected) for r in result["origin_records"] for v in r["scores"])
    assert all(
        r["targets"] == list(view.batch((0, 1)).targets[j, o - 1].tolist())
        for r in result["origin_records"]
        for j, day in enumerate(view.sessions)
        if r["session"] == day
        for o in (r["origin"],)
    )


def test_raw_guard_excludes_only_finder_metadata(tmp_path: Path, monkeypatch):
    import csv
    import json

    from lstm_data.real_bridge_authority import producer_snapshot

    folder = tmp_path / "packet"
    folder.mkdir()
    protected = {
        p: dict(sha256="SYN:HASH")
        for p in (
            "data/raw/.DS_Store",
            "data/raw/vendor/bars.parquet",
            "data/raw/vendor/manifest.json",
            "data/raw/vendor/.other_metadata",
        )
    }
    pre = folder / "preflight.json"
    pre.write_text(json.dumps(dict(protected=protected)))
    inventory = folder / "inventory.csv"
    with inventory.open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=["path", "sha256"])
        writer.writeheader()
        writer.writerow(dict(path="packet/preflight.json", sha256=digest(pre)))
    monkeypatch.setattr("lstm_data.real_bridge_authority.verify_ref", lambda root, ref: inventory)
    _, raw = producer_snapshot(tmp_path, dict(inventory={}))
    assert "data/raw/.DS_Store" not in raw
    assert set(raw) == set(protected) - {"data/raw/.DS_Store"}


def test_cli_missing_approval_cannot_call_worker_or_spend(tmp_path: Path, monkeypatch):
    import sys

    from lstm_data import controlled_batch

    folder = tmp_path / "packet"
    folder.mkdir()
    (folder / "predeclared_experiment_matrix.json").write_text("{}")
    monkeypatch.setattr(controlled_batch, "load_plan", lambda *args: ({"runs": []}, None))
    called = []
    monkeypatch.setattr("lstm_data.real_bridge_run.run_worker", lambda *args: called.append(True))
    monkeypatch.setattr(sys, "argv", ["controlled_batch", "--output", str(folder)])
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="NO_HUMAN_APPROVAL"):
        controlled_batch.main()
    assert not called and not (tmp_path / JOURNAL).exists()
