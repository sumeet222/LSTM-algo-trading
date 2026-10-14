"""E5 architecture/peer route conservation and final-only checkpoint boundaries."""

from dataclasses import replace

import pandas as pd
import pytest
import torch

from lstm_data.e5_audit import audit
from lstm_data.neural_artifacts import PairIdentity, load_checkpoint, save_checkpoint
from lstm_data.neural_engine import batch_prediction, optimizer, seed_all, session_losses
from lstm_data.neural_models import architecture_of, create_model
from lstm_data.peer_neural import make_e5_view, trace_e5
from lstm_data.regime_peer_audit import fabricated_case


@pytest.fixture(scope="module")
def case():
    return fabricated_case()


def test_named_inventory_7329_zero_state_determinism_and_dropout():
    seed_all(42)
    first = create_model("E5")
    assert dict((n, p.numel()) for n, p in first.named_parameters()) == {
        "lstm.weight_ih_l0": 2944,
        "lstm.weight_hh_l0": 4096,
        "lstm.bias_ih_l0": 128,
        "lstm.bias_hh_l0": 128,
        "head.weight": 32,
        "head.bias": 1,
    }
    assert sum(p.numel() for p in first.parameters()) == 7329 == 4 * 32 * (23 + 32 + 2) + 33
    seed_all(42)
    second = create_model("E5")
    assert all(torch.equal(a, b) for a, b in zip(first.parameters(), second.parameters()))
    x = torch.ones(5, 48, 23)
    first.eval()
    a = first(x)
    assert torch.equal(a, first(x))
    first(torch.zeros_like(x))
    assert torch.equal(a, first(x))  # no recurrent memory across calls
    first.train()
    assert not torch.equal(first(x), first(x))
    for dims in (16, 21, 25, 30):
        with pytest.raises(ValueError):
            first(torch.zeros(5, 48, dims))
    for architecture in ("LL0", "LL1", "MC2", "SP3", "SP1"):
        with pytest.raises(ValueError):
            create_model(architecture)


def test_typed_peer_prefix_market_masks_step_clocks_gradient_and_loss(case):
    data, history, prep, val, permission = case
    small = replace(data, origins=data.origins[-2:])
    view = make_e5_view(small, val, prep, permission, history, allow_synthetic=True)
    peer = view.peer.batch((0,))
    batch = view.batch((0,))
    assert batch.inputs.shape == (1, 2, 5, 48, 23)
    assert torch.equal(batch.inputs[..., :21], peer.base.inputs)
    assert batch.ids == peer.base.ids
    assert torch.equal(batch.origins, peer.base.origins)
    assert view.rows == view.peer.market.stock.rows
    assert tuple(row.inputs.stock.steps for row in small.origins)
    forged = batch.inputs.clone()
    forged[0, 0, 0, 0, 21] += 1
    with pytest.raises(ValueError, match="CANONICAL_E5"):
        replace(batch, inputs=forged).validate()
    batch.inputs.requires_grad_()
    model = create_model("E5")
    prediction = batch_prediction(model, batch)
    loss = session_losses(prediction, batch.targets, batch.origins).mean()
    loss.backward()
    assert batch.inputs.grad is not None
    assert float(batch.inputs.grad[..., 21:].norm()) > 0
    opt = optimizer(model)
    assert [g["weight_decay"] for g in opt.param_groups] == [0.01, 0]
    assert all(g["lr"] == 0.001 for g in opt.param_groups)
    assert set(map(id, model.parameters())) == {
        id(p) for g in opt.param_groups for p in g["params"]
    }
    trace = trace_e5(model, batch.inputs[0, 0], "SYN:E5_TRACE")
    assert trace["parameters"] == 7329 and len(trace["scores"]) == 5
    with pytest.raises(ValueError):
        trace_e5(model, batch.inputs[0, 0], "ENG:PROVISIONAL_CORE5")


@pytest.mark.parametrize("family", ["TM0", "MC0", "MC1"])
def test_architecture_checkpoint_denial_both_directions_and_old_numerics(tmp_path, family):
    seed_all(42)
    model = create_model(family)
    inputs = torch.ones(5, 48, 16 if family == "TM0" else 21)
    model.eval()
    old = model(inputs).detach().clone()
    info = "FT0" if family == "TM0" else "FT0_D7_" + family
    pair = PairIdentity(
        "SYN:" + family, "SYN:U", info, "SYN:Y", "SYN:T", "SYN:S", "SYN:P", "SYN:C", "SYN:CODE"
    )
    path = tmp_path / (family + ".pt")
    save_checkpoint(path, model, pair, "REFIT_FINAL", 1)
    with pytest.raises(ValueError):
        load_checkpoint(path, create_model("E5"), pair, "REFIT_FINAL")
    e5 = create_model("E5")
    assert architecture_of(e5) == "E5"
    peer_pair = replace(pair, information="FT0_D7_E5", experiment="SYN:E5")
    e5path = tmp_path / "e5.pt"
    save_checkpoint(e5path, e5, peer_pair, "REFIT_FINAL", 1)
    with pytest.raises(ValueError):
        load_checkpoint(e5path, model, peer_pair, "REFIT_FINAL")
    for field in (
        "universe",
        "source_features_data",
        "target",
        "preprocess",
        "code",
        "calendar_split_cutoff",
        "model_optimizer_selection",
    ):
        with pytest.raises(ValueError):
            load_checkpoint(e5path, e5, replace(peer_pair, **{field: "SYN:STALE"}), "REFIT_FINAL")
    load_checkpoint(path, model, pair, "REFIT_FINAL")
    assert torch.equal(old, model(inputs))
    selected = tmp_path / "selected.pt"
    save_checkpoint(selected, e5, peer_pair, "CALIBRATION_SELECTED", 1)
    with pytest.raises(ValueError):
        load_checkpoint(selected, e5, peer_pair, "REFIT_FINAL")


def test_same_cpu_completed_epoch_resume_e5(tmp_path):
    seed_all(42)
    model = create_model("E5")
    opt = optimizer(model)
    x = torch.ones(5, 48, 23)
    model.train()
    model(x).square().mean().backward()
    opt.step()
    pair = PairIdentity(
        "SYN:E5:RESUME",
        "SYN:U",
        "FT0_D7_E5",
        "SYN:Y",
        "SYN:T",
        "SYN:S",
        "SYN:P",
        "SYN:C",
        "SYN:CODE",
    )
    path = tmp_path / "boundary.pt"
    save_checkpoint(path, model, pair, "REFIT_BOUNDARY", 1, optimizer=opt)
    rng = torch.get_rng_state().clone()
    fresh = create_model("E5")
    fresh_opt = optimizer(fresh)
    epoch, _ = load_checkpoint(path, fresh, pair, "REFIT_BOUNDARY", optimizer=fresh_opt)
    assert epoch == 1 and torch.equal(rng, torch.get_rng_state())
    assert fresh_opt.state and all(
        torch.equal(a, b) for a, b in zip(model.parameters(), fresh.parameters())
    )
    torch.set_rng_state(rng)
    model.train()
    opt.zero_grad(set_to_none=True)
    model(x).square().mean().backward()
    opt.step()
    torch.set_rng_state(rng)
    fresh.train()
    fresh_opt.zero_grad(set_to_none=True)
    fresh(x).square().mean().backward()
    fresh_opt.step()
    assert all(torch.equal(a, b) for a, b in zip(model.parameters(), fresh.parameters()))


def test_no_real_activation_or_unreviewed_inputs(case, tmp_path):
    data, history, prep, val, permission = case
    with pytest.raises(ValueError):
        audit(tmp_path / "real", "SCIENTIFIC_REAL")
    assert not (tmp_path / "real").exists()
    with pytest.raises(ValueError):
        make_e5_view(
            replace(data, basis="DOCUMENTED"), val, prep, permission, history, allow_synthetic=True
        )
    with pytest.raises(ValueError):
        make_e5_view(data, val, prep, permission, history)
    bad = replace(
        history, stamps=(replace(history.stamps[0], available_at=pd.NaT),) + history.stamps[1:]
    )
    with pytest.raises(ValueError):
        make_e5_view(data, val, prep, permission, bad, allow_synthetic=True)
