"""Magnitude-only targets, pair symmetry/coupling and original session weighting."""

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data import hf20_mag_rank as r


def test_midranks_magnitude_scale_permutation_and_exact_ties():
    a = np.arange(20, dtype=float)[None, :]
    np.testing.assert_allclose(r.targets(a), np.linspace(-1, 1, 20)[None, :])
    a[0, :3] = 0
    q = r.targets(a)
    assert np.all(q[0, :3] == 2 / 19 - 1)
    p = np.random.default_rng(2).permutation(20)
    np.testing.assert_array_equal(r.targets(a[:, p]), q[:, p])
    np.testing.assert_array_equal(r.targets(10 * a), q)
    assert (
        len(r.PAIR_I) == 190
        and len(set(zip(r.PAIR_I, r.PAIR_J))) == 190
        and (r.PAIR_I < r.PAIR_J).all()
    )
    assert np.count_nonzero(r.preferences(a)) == 187
    with pytest.raises(ValueError, match="NO_UNEQUAL"):
        r.preferences(np.zeros((1, 20)))
    with pytest.raises(ValueError):
        r.targets(-np.ones((1, 20)))
    # Do not accidentally turn distinct float64 returns into equal float32 labels.
    a = np.arange(20, dtype=float)[None, :]
    a[0, 0] = 1.0
    a[0, 1] = 1.0 + 1e-12
    assert r.preferences(a)[0, 0] == -1


def test_pair_permutation_offset_extremes_and_coupled_gradients():
    a = np.arange(20, dtype=float)[None, :]
    a[0, 1] = a[0, 0]
    z = torch.linspace(-1, 1, 20, dtype=torch.float64)[None, :].requires_grad_()
    y = torch.as_tensor(r.preferences(a), dtype=z.dtype)
    pair_loss = r.origin_loss(z, y, "S5B")
    assert float(pair_loss.detach()) < np.log(2)
    torch.testing.assert_close(pair_loss, r.origin_loss(z + 17, y, "S5B"))
    p = np.random.default_rng(4).permutation(20)
    torch.testing.assert_close(
        pair_loss,
        r.origin_loss(z[:, p], torch.as_tensor(r.preferences(a[:, p]), dtype=z.dtype), "S5B"),
    )
    grad = torch.autograd.grad(pair_loss.sum(), z, create_graph=True)[0]
    torch.testing.assert_close(grad.sum(), torch.tensor(0.0, dtype=z.dtype), atol=1e-14, rtol=0)
    cross = torch.autograd.grad(grad[0, 0], z)[0]
    assert cross[0, 2] != 0
    extreme = torch.linspace(1e5, -1e5, 20)[None, :].requires_grad_()
    v = r.origin_loss(extreme, y.float(), "S5B")
    v.sum().backward()
    assert extreme.grad is not None
    assert torch.isfinite(v).all() and torch.isfinite(extreme.grad).all()
    zero = torch.zeros((1, 20), requires_grad=True)
    v = r.origin_loss(zero, y.float(), "S5B")
    assert float(v.detach()) == pytest.approx(np.log(2))
    v.backward()
    assert zero.grad is not None
    assert torch.isfinite(zero.grad).all()
    # One known unequal pair: no contribution/gradient from invented equal labels.
    sparse = torch.zeros((1, 190))
    sparse[0, 0] = 1
    z2 = torch.zeros((1, 20), requires_grad=True)
    r.origin_loss(z2, sparse, "S5B").sum().backward()
    assert z2.grad is not None
    np.testing.assert_allclose(z2.grad.numpy()[0, :2], [-0.5, 0.5])
    assert torch.count_nonzero(z2.grad[0, 2:]) == 0


def test_hierarchy_batch_equivalence_and_zero_mean_target():
    a = np.tile(np.arange(20), (3, 1)).astype(float)
    q = torch.as_tensor(r.targets(a), dtype=torch.float64)
    z = q + torch.tensor([1.0, 2.0, 4.0], dtype=torch.float64)[:, None]
    days = np.array(["a", "b", "b"])
    assert float(r.loss(z, q, days, "S5A")) == pytest.approx((1 + (4 + 16) / 2) / 2)
    torch.testing.assert_close(
        r.loss(z, q, days, "S5A"),
        (r.loss(z[:1], q[:1], days[:1], "S5A") + r.loss(z[1:], q[1:], days[1:], "S5A")) / 2,
    )
    np.testing.assert_allclose(r.targets(a).mean(1), 0, atol=1e-16)
    y = torch.from_numpy(r.preferences(a))
    whole = r.loss(z, y, days, "S5B")
    torch.testing.assert_close(
        whole, (r.loss(z[:1], y[:1], days[:1], "S5B") + r.loss(z[1:], y[1:], days[1:], "S5B")) / 2
    )
    assert float(whole) > 0  # ordinal logistic is not rank-MSE or a 20-way classification loss


def test_constant_ic_historical_parity_and_clock_model_reload(tmp_path):
    a = np.tile(np.arange(20), (3, 1))
    z = a.copy().astype(float)
    z[1] = 1
    np.testing.assert_allclose(r.conservative_ic(a, z), [1, 0, 1])
    np.testing.assert_allclose(r.conservative_ic(a, z)[[0, 2]], r.b.origin_ic(a, z)[[0, 2]])
    model = r.clock.model_for_clock().eval()
    assert sum(x.numel() for x in model.parameters()) == 6443
    x = torch.zeros((40, 48, 16))
    c = torch.zeros((40, 10))
    v = model(x, c)
    assert v.shape == (40,)
    path = tmp_path / "model.pt"
    torch.save(model.state_dict(), path)
    new = r.clock.model_for_clock().eval()
    new.load_state_dict(torch.load(path, weights_only=True))
    torch.testing.assert_close(v, new(x, c), rtol=0, atol=0)
    assert not r.b.optimizer(new).state
    assert model.dropout.p == 0.10
    # Clock terms are common additive scores and cancel in a linear-head pair loss.
    with torch.no_grad():
        c[:, 0] = 1
        shifted = model(x, c).reshape(2, 20) - v.reshape(2, 20)
    torch.testing.assert_close(shifted, shifted[:, :1].expand_as(shifted))


def test_selector_qualification_and_ridge_normal_equations():
    s = r.b.Selector()
    assert s.observe(1.0)
    assert not s.observe(0.9995)
    assert s.observe(0.999)
    for _ in range(10):
        s.observe(1.0)
    assert s.status == "PATIENCE_STOP" and s.selected == 3 and s.epoch == 13
    rng = np.random.default_rng(7)
    x = np.column_stack([np.ones(30), rng.normal(size=(30, 4))])
    q = rng.normal(size=30)
    w = np.linspace(1, 2, 30)
    w /= w.sum()
    gram = x.T @ (w[:, None] * x)
    rhs = x.T @ (w * q)
    beta = r.solve(gram, rhs, 0.01)
    reg = np.eye(5) * 0.01
    reg[0, 0] = 0
    np.testing.assert_allclose((gram + reg) @ beta, rhs, atol=1e-14)
    grams = sum(x[k : k + 6].T @ (w[k : k + 6, None] * x[k : k + 6]) for k in range(0, 30, 6))
    np.testing.assert_allclose(gram, grams)


def test_fractional_retrieval_constant_and_signed_label_distinction():
    signed = np.linspace(-0.1, 0.09, 20)[None, :]
    a = abs(signed)
    assert not np.array_equal(
        r.targets(a), 2 * (pd.DataFrame(signed).rank(axis=1).to_numpy() - 1) / 19 - 1
    )
    f = pd.DataFrame(
        {"A": a.ravel(), "score": np.zeros(20), "session_date_et": ["2021-01-04"] * 20}
    )
    d = r.b.rank_metrics(f, "score")
    assert d["top4"] == pytest.approx(0.2)
    assert d["bottom4"] == pytest.approx(0.2)
    assert d["pair_concordance"] == 0.5


def test_report_origin_reducer_and_normalized_rank_error():
    from lstm_data import hf20_mag_rank_report as report

    a = np.tile(np.arange(20), (3, 1)).astype(float)
    z = a.copy()
    z[1] = 0
    d = pd.DataFrame(report.origin_metrics(a, z))
    d["day"] = ["a", "b", "b"]
    v = report.reduce(d)
    assert v["IC"] == pytest.approx(0.75)
    assert v["historical_IC"] == pytest.approx(1.0)
    assert v["constant_rate"] == pytest.approx(0.25)
    np.testing.assert_allclose(report.membership(z).sum(1), 4)
    q = r.targets(a)
    assert np.isfinite(q).all() and q.shape == (3, 20)
