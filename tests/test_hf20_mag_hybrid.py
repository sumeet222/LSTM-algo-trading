"""Frozen hybrid arithmetic, phase hierarchy, pair gradients and inherited decoder."""

import math

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data import hf20_mag_hybrid as h


def test_phase_moments_and_hierarchy():
    a = np.tile(np.arange(1, 21, dtype=float), (3, 1)) * np.array([1, 2, 4])[:, None]
    days = np.array(["d1", "d2", "d2"])
    s = 10.0
    c = h.phase_constants(a, days, s)
    m = np.log1p(a / s)
    w = np.array([0.5, 0.25, 0.25])
    mu = (w[:, None] * m / 20).sum()
    v = (w[:, None] * (m - mu) ** 2 / 20).sum()
    assert c["mu"] == pytest.approx(mu) and c["variance"] == pytest.approx(v)
    assert c["tau"] == pytest.approx(math.sqrt(v))
    # No selector argument exists; calling on a different legal role gives own moments.
    assert h.phase_constants(a * 2, days, s)["variance"] != c["variance"]
    with pytest.raises(ValueError, match="VARIANCE"):
        h.phase_constants(np.zeros((3, 20)), days, s)
    z = torch.from_numpy(m + 0.2)
    parts = h.reduced(z, a, days, c)
    assert float(parts[0]) == pytest.approx(0.04)
    assert float(parts[2]) == pytest.approx(0.04 / v + 0.25 * float(parts[1]) / math.log(2))
    for k in range(3):
        torch.testing.assert_close(
            parts[k],
            (h.reduced(z[:1], a[:1], days[:1], c)[k] + h.reduced(z[1:], a[1:], days[1:], c)[k]) / 2,
        )


def test_pairs_zero_all_ties_permutation_margin_and_gradient():
    a = np.tile(np.arange(20, dtype=float), (2, 1))
    a[1] = 0
    y = torch.from_numpy(h.preferences(a))
    assert int((y[0] != 0).sum()) == 190 and y[1].count_nonzero() == 0
    z = torch.zeros((2, 20), requires_grad=True)
    m = torch.log1p(torch.from_numpy(a).float())
    mag, pair, total = h.components(z, m, y, 2.0, math.sqrt(2))
    torch.testing.assert_close(pair, torch.tensor([math.log(2), 0.0]))
    torch.testing.assert_close(total, mag / 2 + 0.25 * pair / math.log(2))
    grad = torch.autograd.grad(pair.sum(), z, retain_graph=True)[0]
    assert grad[0, 0] > 0 and grad[0, -1] < 0 and grad[1].count_nonzero() == 0
    torch.testing.assert_close(h.components(z + 17, m, y, 2.0, math.sqrt(2))[1], pair)
    p = np.random.default_rng(4).permutation(20)
    torch.testing.assert_close(
        h.components(z[:, p], m[:, p], torch.from_numpy(h.preferences(a[:, p])), 2.0, math.sqrt(2))[
            2
        ],
        total,
    )
    total.sum().backward()
    assert z.grad is not None and torch.isfinite(z.grad).all()
    # Exact A equality before float32 conversion.
    a[0, :2] = [1.0, 1.0 + 1e-12]
    assert h.preferences(a)[0, 0] == -1


def test_one_head_pair_backprop_clock_cancellation():
    model = h.clock.model_for_clock().eval()
    assert sum(p.numel() for p in model.parameters()) == 6443
    x = torch.randn(20, 48, 16)
    clock = torch.randn(1, 10).repeat(20, 1)
    z = model(x, clock).reshape(1, 20)
    y = torch.from_numpy(h.preferences(np.arange(20, dtype=float)[None, :]))
    mag, pair, total = h.components(z, torch.ones_like(z), y, 1.0, 1.0)
    pair.sum().backward(retain_graph=True)
    trunk_grad = dict(model.named_parameters())["lstm.weight_ih_l0"].grad
    assert trunk_grad is not None and torch.linalg.vector_norm(trunk_grad) > 0
    assert model.head.weight.grad is not None
    torch.testing.assert_close(
        model.head.weight.grad[:, 32:], torch.zeros((1, 10)), atol=1e-6, rtol=0
    )
    model.zero_grad()
    total.sum().backward()
    assert model.head.weight.grad is not None and model.head.weight.grad[:, 32:].norm() > 0
    shifted = model(x, clock + 1).reshape(1, 20)
    torch.testing.assert_close(
        h.components(shifted, torch.ones_like(z), y, 1.0, 1.0)[1], pair, atol=1e-6, rtol=0
    )
    assert not torch.allclose(h.components(shifted, torch.ones_like(z), y, 1.0, 1.0)[0], mag)


def test_own_scale_transform_and_unclamped_calibrator():
    # Same source prices give signed log ratio, absolute target, monotone M.
    r = np.log(np.array([0.5, 1.0, 2.0]) / 1.0)
    a = abs(r)
    assert np.all(a >= 0) and a[0] == a[2]
    np.testing.assert_allclose(0.01 * np.expm1(np.log1p(a / 0.01)), a)
    f = pd.DataFrame(
        dict(
            A=[0.01, 0.02, 0.03, 0.04],
            Mhat=[-0.2, 0.1, 0.3, 0.4],
            weight=[0.25] * 4,
            session_date_et=["a", "a", "b", "b"],
            category=["INTRADAY", "OVERNIGHT"] * 2,
            origin_id=[0, 1, 2, 3],
        )
    )
    coeff = h.c3.fit_categories(f, 0.01)
    q = np.exp(np.log1p(f.A / 0.01) - f.Mhat)
    assert coeff[0]["c0"] == pytest.approx(q.mean())
    for row in coeff:
        group = f[f.category == row["group"]]
        n = 2.0
        rho = n / (n + 25)
        raw = np.exp(np.log1p(group.A / 0.01) - group.Mhat).mean()
        assert row["c_star"] == pytest.approx(q.mean() + rho * (raw - q.mean()))
    decoded = h.c3.decode(f.Mhat.to_numpy(), 0.01, 1.2)
    np.testing.assert_allclose(decoded, 0.01 * np.maximum(0, np.exp(f.Mhat) * 1.2 - 1))
    assert np.isfinite(decoded).all() and (decoded >= 0).all()


def test_report_equal_year_and_conservative_rank_reducer():
    from lstm_data import hf20_mag_hybrid_report as report

    a = np.tile(np.arange(20, dtype=float), (3, 1))
    z = a.copy()
    z[0] = 0
    result = report.rank_summary(a, z, np.array(["d1", "d2", "d2"]))
    assert result["IC"] == pytest.approx(0.5)
    assert result["historical_IC"] == pytest.approx(1.0)
    assert result["undefined_IC_origins"] == 1
    f = pd.DataFrame(
        dict(
            year=["2021", "2022", "2023", "2024"],
            arm=["x"] * 4,
            observed=[1.0, 2.0, 3.0, 4.0],
            predicted=[2.0, 2.0, 3.0, 5.0],
            ratio=[2.0, 1.0, 1.0, 1.25],
            raw_MSE=[1.0, 2.0, 3.0, 4.0],
            rows=[20] * 4,
        )
    )
    eq = report.equal_year(f, ["arm"]).iloc[-1]
    assert eq.raw_MSE == pytest.approx(2.5) and eq.ratio == pytest.approx(1.2)
    assert eq.rows == 80
