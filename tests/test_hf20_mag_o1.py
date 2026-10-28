"""Four bounded synthetic correctness fixtures; no historical research fitting."""

import math
from pathlib import Path

import numpy as np
import pytest
import torch

from lstm_data import hf20_mag_designa as base
from lstm_data.hf20_mag_o1 import check_recipe, decoded, positive, top_membership, weighted_loss
from lstm_data.hf20_s5s9_metrics import auc, average_precision


def test_stable_softplus_units_and_gradients() -> None:
    z = torch.tensor([-1000.0, -100.0, 0.0, 100.0, 1000.0], dtype=torch.float64, requires_grad=True)
    p = positive(z, 0.01)
    assert bool(torch.isfinite(p).all()) and bool((p >= 0).all())
    assert bool((p[1:] > 0).all())
    assert float(p[2].detach()) == pytest.approx(0.01 * math.log(2))
    assert float(p[-1].detach()) == pytest.approx(10.0)
    p.sum().backward()
    assert z.grad is not None and bool(torch.isfinite(z.grad).all())
    np.testing.assert_array_equal(decoded(z.detach().numpy(), 0.01), p.detach().numpy())
    with pytest.raises(ValueError):
        positive(z, 0.0)


def test_scaled_raw_loss_hierarchy_and_return_sign_invariance() -> None:
    z = torch.full((3, 20), math.log(math.expm1(2)), dtype=torch.float64, requires_grad=True)
    r = torch.tensor([0.01, -0.02, 0.04], dtype=torch.float64)[:, None].repeat(1, 20)
    days = np.array(["2000-01-03", "2000-01-04", "2000-01-04"])
    loss = weighted_loss(z, r, 0.01, days)
    assert float(loss.detach()) == pytest.approx(1.5)
    assert float(loss.detach()) != pytest.approx(5 / 3)
    assert float(weighted_loss(z, -r, 0.01, days).detach()) == pytest.approx(1.5)
    loss.backward()
    assert z.grad is not None
    # A one-origin day has twice the per-origin weight of the two-origin day.
    expected = torch.tensor([1 / 40, 1 / 80, 1 / 80], dtype=torch.float64)[:, None].repeat(1, 20)
    errors = (positive(z.detach(), 0.01) - r.abs()) / 0.01
    np.testing.assert_allclose(z.grad, 2 * errors * torch.sigmoid(z.detach()) * expected)


def test_tiny_planted_signal_fresh_optimizer_and_reload(tmp_path: Path) -> None:
    torch.set_num_threads(1)
    model = base.model_for("MAG")
    initial = base.initial_hash(model)
    assert sum(p.numel() for p in model.parameters()) == 6433
    x = torch.zeros(20, 48, 16)
    x[:, :, 0] = torch.linspace(-1, 1, 20)[:, None]
    target = 0.01 * torch.nn.functional.softplus(1.5 * x[:, -1, 0] + 0.3)
    days = np.array(["2000-01-03"])
    opt = base.optimizer(model)
    assert not opt.state
    model.eval()
    before = float(
        weighted_loss(model(x).reshape(1, 20), target.reshape(1, 20), 0.01, days).detach()
    )
    for _ in range(120):
        model.train()
        opt.zero_grad()
        loss = weighted_loss(model(x).reshape(1, 20), target.reshape(1, 20), 0.01, days)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        opt.step()
    model.eval()
    with torch.inference_mode():
        predicted = model(x)
        after = float(weighted_loss(predicted.reshape(1, 20), target.reshape(1, 20), 0.01, days))
    assert predicted.shape == (20,) and after < 0.25 * before
    path = tmp_path / "synthetic.pt"
    torch.save(model.state_dict(), path)
    fresh = base.model_for("MAG")
    assert base.initial_hash(fresh) == initial and not base.optimizer(fresh).state
    fresh.load_state_dict(torch.load(path, weights_only=True))
    fresh.eval()
    with torch.inference_mode():
        torch.testing.assert_close(fresh(x), predicted, rtol=0, atol=0)


def test_existing_event_ties_and_top_four_convention() -> None:
    score = np.ones(20)
    event = np.array([True] * 4 + [False] * 16)
    w = np.full(20, 1 / 20)
    np.testing.assert_allclose(top_membership(score), 0.2)
    assert average_precision(event, score, w) == pytest.approx(0.2)
    assert auc(event, score, w) == pytest.approx(0.5)


def test_recipe_parity_keeps_every_FT16_field_exact() -> None:
    recipe = dict(scalers=dict(V2=dict(center=1.0, scale=2.0)), fit_hour_indices=[1, 2, 3])
    extra = dict(epsilon=0.001, t2_scale=0.9, s4_contexts=7, task="S4A", target_minutes=240)
    original = dict(recipe, **extra)
    assert check_recipe(recipe, original, s4_metadata=True) == sorted(extra)
    with pytest.raises(AssertionError, match="SCHEMA"):
        check_recipe(recipe, original, s4_metadata=False)
    changed = dict(recipe, scalers=dict(V2=dict(center=1.0, scale=3.0)))
    with pytest.raises(AssertionError, match="FIELD"):
        check_recipe(changed, original, s4_metadata=True)
