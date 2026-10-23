"""Independent P024 design, selector, transform and zero-update safety oracles."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest
import torch

from lstm_data.config import fingerprint
from lstm_data.controlled_loss import LossPolicy
from lstm_data.neural_engine import SharedLSTM, seed_all
from lstm_data.neural_lifecycle import EarlyStop, state_hash
from lstm_data.optimization_screen import (
    REFERENCE,
    RUNS,
    VARIANTS,
    ScreenStop,
    make_model,
    make_optimizer,
    parameter_audit,
)
from lstm_data.optimization_screen_authority import ensure, validate
from lstm_data.optimization_screen_run import persist, save_reload
from lstm_data.visualization.hf1m_long import dates, role


@pytest.mark.parametrize("v", VARIANTS)
def test_single_delta_groups_and_shapes(v):
    audit = parameter_audit(v)
    assert len(audit["delta"]) == 1
    expected = 21057 if v.arm == "H64" else 14881 if v.arm == "L2H32" else 6433
    assert audit["parameters"] == expected
    model = make_model(v)
    assert model.lstm.num_layers == v.layers and model.lstm.hidden_size == v.hidden
    assert model.lstm.dropout == 0 and model.dropout.p == v.head_dropout
    opt = make_optimizer(model, v)
    names = dict(model.named_parameters())
    assert {id(p) for g in opt.param_groups for p in g["params"]} == {id(p) for p in names.values()}
    for g in opt.param_groups:
        assert g["lr"] == v.learning_rate and g["betas"] == (0.9, 0.999)
        assert g["eps"] == 1e-8 and not g["amsgrad"]
        for p in g["params"]:
            assert g["weight_decay"] == (v.matrix_decay if p.ndim == 2 else 0)
    x = torch.randn(3, 48, 16)
    model.eval()
    a = model(x)
    model(torch.randn(2, 48, 16))
    torch.testing.assert_close(model(x), a, rtol=0, atol=0)
    _, (h, c) = model.lstm(x)
    assert h.shape == c.shape == (v.layers, 3, v.hidden)
    assert a.shape == (3,)


def test_reference_initialization_and_dropout():
    seed_all(42)
    baseline = SharedLSTM()
    m = make_model(REFERENCE)
    assert state_hash(m) == state_hash(baseline)
    x = torch.ones(3, 48, 16)
    m.eval()
    fixed = m(x)
    m.train()
    assert not torch.equal(m(x), fixed)
    no = make_model(VARIANTS[1])
    no.train()
    a = no(x)
    no.eval()
    torch.testing.assert_close(no(x), a, rtol=0, atol=0)
    # Same initial weights, with dropout setting as the sole change.
    assert state_hash(no) == state_hash(baseline)


def test_selector_exact_boundary_and_historical_parity():
    for t in (0.001, 0.00025):
        s = ScreenStop(improvement=t)
        assert s.observe(4.0)
        boundary = (1 - t) * 4
        assert not s.observe(boundary)
        assert s.observe(math.nextafter(boundary, -math.inf))
    a, b = EarlyStop(), ScreenStop()
    for value in [4, 3.999, 3.99] + [3.99] * 11:
        if a.status != "CALIBRATING":
            break
        assert a.observe(value) == b.observe(value)
        assert vars(a) == {k: v for k, v in vars(b).items() if k != "improvement"}
    assert a.status == "PATIENCE_STOP"
    s = ScreenStop()
    for _ in range(12):
        s.observe(1.0)
    assert s.epoch == 12 and s.selected == 1 and s.patience == 11
    with pytest.raises(ValueError):
        s.observe(1.0)
    s = ScreenStop()
    for e in range(60):
        s.observe(0.99**e)
    assert s.status == "MAX_EPOCHS_REACHED" and s.selected == 60


def test_seed123_curve_qualifies_against_last_qualified_best():
    curve = [
        3.6556651155933055,
        3.65351354374605,
        3.6544769485531807,
        3.6546921296317074,
        3.654483893208514,
        3.655634775920112,
        3.654918109279832,
        3.655528259692888,
        3.653926606791212,
        3.656258753571895,
        3.654920311664964,
        3.653055626192903,
    ]
    old, new = ScreenStop(), ScreenStop(improvement=0.00025)
    for value in curve:
        old.observe(value)
        new.observe(value)
    assert (old.selected, new.selected, old.raw_epoch, new.raw_epoch) == (1, 2, 12, 12)
    assert old.status == new.status == "PATIENCE_STOP"


def test_transformed_loss_and_equal_session_scalar_oracle():
    # One session has two origins and another only one: equal row loss is incorrect.
    y = torch.tensor([[[1.0] * 20, [4.0] * 20], [[2.0] * 20, [0.0] * 20]])
    mask = torch.tensor([[True, True], [True, False]])
    raw = torch.zeros_like(y)
    policy = LossPolicy("T2", scale=0.9)
    loss = policy.objective(raw, y, mask, stock_count=20)
    expected = np.array(
        [(np.arcsinh(1 / 0.9) ** 2 + np.arcsinh(4 / 0.9) ** 2) / 2, np.arcsinh(2 / 0.9) ** 2]
    )
    np.testing.assert_allclose(loss, expected, rtol=2e-7)
    z = torch.tensor([-4.0, 0.0, 3.0])
    torch.testing.assert_close(policy.canonical(z), 0.9 * torch.sinh(z), rtol=0, atol=0)
    assert not np.isclose(float(loss.mean()), float((torch.asinh(y / 0.9)[mask] ** 2).mean()))


def test_progress_reload_fresh_init_and_rng(tmp_path: Path):
    epochs = []
    for phase, count in [("calibration", 12), ("refit", 2)]:
        for e in range(1, count + 1):
            r = dict(phase=phase, training=dict(epoch=e))
            epochs.append(r)
            persist(tmp_path, r, epochs)
    assert json.loads((tmp_path / "epochs_progress.json").read_text()) == dict(epochs=epochs)
    assert len(list((tmp_path / "epoch_receipts").glob("*.json"))) == 14
    with pytest.raises(FileExistsError):
        persist(tmp_path, epochs[-1], epochs)
    v = VARIANTS[4]
    m = make_model(v)
    rng = torch.get_rng_state().clone()
    _, loaded = save_reload(tmp_path / "test.pt", m, v, dict(test=True))
    assert torch.equal(rng, torch.get_rng_state())
    assert state_hash(m) == state_hash(loaded) == state_hash(make_model(v))
    assert not make_optimizer(make_model(v), v).state


def test_unapproved_and_protected_queries_fail_before_reads(tmp_path: Path):
    with pytest.raises(ValueError, match="LIVE_APPROVAL"):
        ensure(tmp_path / "absent.json", None, RUNS[0])
    with pytest.raises(ValueError, match="protected"):
        dates("2025-12-31", "2026-01-01")
    with pytest.raises(ValueError, match="protected"):
        role("confirmation")


def test_journal_failed_start_is_charged_and_terminal():
    history = []

    def event(status, name=RUNS[0], count=45):
        return dict(
            sequence=len(history) + 1,
            previous=fingerprint(history),
            run_id=name,
            status=status,
            global_started_pairs=count,
            effective_ceiling=200,
        )

    history.append(event("STARTED"))
    history.append(event("FAILED"))
    assert validate(history) == history
    with pytest.raises(ValueError):
        validate(history + [event("STARTED")])
    with pytest.raises(ValueError):
        validate(history + [event("STARTED", RUNS[1], 46)])
    with pytest.raises(ValueError):
        validate([dict(history[0], global_started_pairs=44)])
