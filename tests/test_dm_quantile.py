"""Independent P023 objective and sampling-risk oracles; no optimizer steps."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.dm_quantile_authority import ensure
from lstm_data.dm_quantile_loss import draws, fitting_recipe, model_for, outputs, terms


@pytest.mark.parametrize("arm", ["DM1", "QR1", "SS1"])
def test_numpy_objective_and_head_gradients(arm: str) -> None:
    y = torch.linspace(-4, 4, 80).reshape(2, 2, 20)
    mask = torch.tensor([[True, False], [True, True]])
    raw = (
        torch.linspace(-1, 1, 240 if arm != "SS1" else 80).reshape(2, 2, 20, 3)
        if arm != "SS1"
        else torch.linspace(-1, 1, 80).reshape(2, 2, 20)
    )
    raw.requires_grad_()
    r = terms(raw, y, mask, arm, 1.0)
    z = np.arcsinh(y.numpy())
    a = raw.detach().numpy()
    if arm == "DM1":
        c = z >= 0
        pos = np.logaddexp(0, a[..., 1])
        neg = np.logaddexp(0, a[..., 2])
        expected = (
            np.logaddexp(0, a[..., 0]) - c * a[..., 0] + (np.where(c, pos, neg) - abs(z)) ** 2
        )
        out = outputs(raw, arm, 1.0)
        np.testing.assert_allclose(
            out["z_hat"].detach(),
            (1 / (1 + np.exp(-a[..., 0]))) * pos - (1 - 1 / (1 + np.exp(-a[..., 0]))) * neg,
            atol=2e-7,
        )
    elif arm == "QR1":
        q = np.stack(
            [
                a[..., 0] - np.logaddexp(0, a[..., 1]),
                a[..., 0],
                a[..., 0] + np.logaddexp(0, a[..., 2]),
            ],
            axis=-1,
        )
        e = z[..., None] - q
        tau = np.array([0.05, 0.5, 0.95])
        expected = np.maximum(tau * e, (tau - 1) * e).mean(axis=-1)
        out = outputs(raw, arm, 1.0)
        assert bool((out["quantiles_y"][..., 1:] >= out["quantiles_y"][..., :-1]).all())
    else:
        expected = (z - a) ** 2
    oracle = [expected[i, mask[i].numpy()].mean() for i in range(2)]
    np.testing.assert_allclose(r["session_loss"].detach(), oracle, rtol=1e-6)
    r["session_loss"].mean().backward()
    assert raw.grad is not None and bool(torch.isfinite(raw.grad).all())
    assert not bool(raw.grad[0, 1].any())


def test_zero_convention_weighted_constants_and_quantiles() -> None:
    y = np.tile(np.linspace(-2, 2, 20), 10)
    y[0] = 0
    f = pd.DataFrame(
        dict(
            TG20=y,
            origin_id=np.repeat(np.arange(10), 20),
            session_date_et=np.repeat([f"2020-01-{i + 1:02}" for i in range(10)], 20),
        )
    )
    r = fitting_recipe(f, 1.0, tuple(sorted(set(f.session_date_et))))
    assert r["exact_zero_rows"] == 1
    assert r["sign_prior"] == pytest.approx((y >= 0).mean())
    q = np.sort(np.arcsinh(y))[[9, 99, 189]]
    np.testing.assert_allclose(r["quantiles_z"], q)
    raw = torch.zeros((1, 1, 20, 3))
    target = torch.zeros((1, 1, 20))
    mask = torch.ones((1, 1), dtype=torch.bool)
    loss = terms(raw, target, mask, "DM1", 1.0)
    assert float(loss["session_loss"][0]) == pytest.approx(np.log(2) + np.log(2) ** 2)


def test_sampler_monte_carlo_risk_step_parity_and_replacement() -> None:
    recipe = dict(
        session_count=101,
        tail_natural_share=3 / 101,
        tail_positions=[0, 1, 2],
        ordinary_positions=list(range(3, 101)),
    )
    losses = np.r_[np.full(3, 100.0), np.ones(98)]
    estimates = []
    for e in range(1, 1001):
        batches = draws(recipe, e)
        assert len(batches) == 7 and sum(len(ids) for ids, _ in batches) == 101
        estimates.append(np.mean(np.concatenate([losses[list(ids)] * w for ids, w in batches])))
        for ids, w in batches[:-1]:
            assert sum(i < 3 for i in ids) == 8
    assert np.mean(estimates) == pytest.approx(losses.mean(), rel=0.003)
    ids, weights = draws(recipe, 1)[0]
    assert len(set(ids)) < len(ids)
    # Self normalization is not used: expected weights are not the realized denominator.
    assert float(draws(recipe, 1)[-1][1].mean()) != pytest.approx(1, abs=1e-7)
    with pytest.raises(ValueError):
        ensure(Path("not-read"), None, "no-run")


def test_head_counts_initial_backbone_and_duplicate_safe_batch() -> None:
    models = {a: model_for(a) for a in ["DM1", "QR1", "SS1"]}
    assert [sum(p.numel() for p in m.parameters()) for m in models.values()] == [6499, 6499, 6433]
    for m in models.values():
        for k, v in m.lstm.state_dict().items():
            torch.testing.assert_close(v, models["SS1"].lstm.state_dict()[k])
    # The duplicate-safe real batch path is exercised by preparation on a permitted source batch.


def test_three_start_journal_and_no_refund() -> None:
    from lstm_data.config import fingerprint
    from lstm_data.dm_quantile_authority import validate_history
    from lstm_data.dm_quantile_loss import RUNS

    records = []
    for i, run in enumerate(RUNS):
        for status in ["STARTED", "CALIBRATED", "REFITTING", "COMPLETED"]:
            records.append(
                dict(
                    sequence=len(records) + 1,
                    previous=fingerprint(records),
                    run_id=run,
                    status=status,
                    global_started_pairs=42 + i,
                    effective_ceiling=200,
                )
            )
    assert validate_history(records) == records
    with pytest.raises(ValueError):
        validate_history(
            records
            + [
                dict(
                    sequence=13,
                    previous=fingerprint(records),
                    run_id=RUNS[0],
                    status="STARTED",
                    global_started_pairs=45,
                    effective_ceiling=200,
                )
            ]
        )


def test_pinball_derivative_away_from_knots() -> None:
    raw = torch.zeros((1, 1, 20, 3), requires_grad=True)
    y = torch.full((1, 1, 20), 5.0)
    m = torch.ones((1, 1), dtype=torch.bool)
    r = terms(raw, y, m, "QR1", 1.0)
    r["session_loss"].sum().backward()
    assert raw.grad is not None
    # z exceeds all three quantiles: dL/dq=-tau, shared median aggregates all three.
    np.testing.assert_allclose(
        raw.grad[..., 0].numpy(), -np.mean([0.05, 0.5, 0.95]) / 20, rtol=1e-6
    )
    np.testing.assert_allclose(raw.grad[..., 1].numpy(), 0.05 * 0.5 / (3 * 20), rtol=1e-6)
    np.testing.assert_allclose(raw.grad[..., 2].numpy(), -0.95 * 0.5 / (3 * 20), rtol=1e-6)
