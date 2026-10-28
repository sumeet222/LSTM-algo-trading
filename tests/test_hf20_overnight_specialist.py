"""Small fixtures for the new loss, selector, router and weighted month blocks."""

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data import hf20_mag_designa as b
from lstm_data import hf20_overnight_specialist as s


def test_separate_group_means_and_no_intraday_gradient() -> None:
    days = np.array(["a", "a", "b", "b", "c"])
    cat = np.array([s.NIGHT, "INTRADAY", s.NIGHT, s.NIGHT, "INTRADAY"])
    weights = s.loss_weights(days, cat, 0.25)
    np.testing.assert_allclose(weights, [0.5, 0.125, 0.25, 0.25, 0.125])
    targets = np.array([1, 2, 3, 5, 4.0])
    returns = torch.tensor(np.repeat(np.expm1(targets)[:, None], 20, axis=1))
    raw = torch.zeros_like(returns, requires_grad=True)
    assert float(s.weighted_loss(raw, returns, 1.0, weights).detach()) == pytest.approx(11.5)
    loss = s.weighted_loss(raw, returns, 1.0, s.loss_weights(days, cat, 0.0))
    loss.backward()
    assert raw.grad is not None
    assert torch.count_nonzero(raw.grad[[1, 4]]) == 0
    assert torch.count_nonzero(raw.grad[[0, 2, 3]]) == 60
    assert float(loss.detach()) == pytest.approx(9.0)


def test_batch_denominators_preserve_declared_loss_with_missing_group() -> None:
    days = np.array(["a", "a", "b", "b", "c"])
    cat = np.array([s.NIGHT, "INTRADAY", s.NIGHT, s.NIGHT, "INTRADAY"])
    w = s.loss_weights(days, cat, 0.1)
    raw = torch.zeros((5, 20), dtype=torch.float64)
    returns = torch.tensor(np.repeat(np.expm1(np.array([1, 2, 3, 5, 4.0]))[:, None], 20, axis=1))
    full = s.weighted_loss(raw, returns, 1.0, w)
    aggregate = torch.tensor(0.0, dtype=torch.float64)
    for batch in [np.array([0, 1, 2, 3]), np.array([4])]:
        number = len(np.unique(days[batch]))
        batch_loss = s.weighted_loss(raw[batch], returns[batch], 1.0, w[batch] * 3 / number)
        aggregate += batch_loss * number / 3
    assert float(aggregate) == pytest.approx(float(full))
    assert float(full) == pytest.approx(10.0)
    with pytest.raises(ValueError):
        s.loss_weights(days, cat, 0.75)


def test_lambda_selection_ties_and_invalid_scores() -> None:
    records = [{"lambda": v, "selector_raw_MSE": 1.0} for v in s.LAMBDAS]
    assert s.choose_candidate(records)["lambda"] == 0.5
    records[1]["selector_raw_MSE"] = 0.9
    assert s.choose_candidate(records)["lambda"] == 0.1
    records[0]["selector_raw_MSE"] = np.nan
    with pytest.raises(ValueError):
        s.choose_candidate(records)


def test_router_uses_saved_category_including_early_close_and_decode() -> None:
    # A saved early-close morning crossing must route overnight despite09:30.
    f = pd.DataFrame(
        dict(slot=["09:30", "09:30", "15:30"], category=["INTRADAY", s.NIGHT, s.NIGHT])
    )
    cat = np.repeat(f.category.to_numpy(), 20)
    old = np.linspace(0.001, 0.01, 60)
    new = old * 2
    routed = s.route(old, new, cat)
    np.testing.assert_array_equal(routed[:20], old[:20])
    np.testing.assert_array_equal(routed[20:], new[20:])
    np.testing.assert_allclose(
        s.raw_decode(np.array([-0.1, 0.0, 1.0]), 0.01), [0, 0, 0.01 * np.expm1(1)]
    )
    z = np.array([-0.1, 0.1, 1.0])
    scale = 0.01
    a = np.array([0.02, 0.01, 0.1])
    q = np.exp(np.log1p(a / scale) - z)
    c = float(np.mean(q))
    np.testing.assert_allclose(s.c3.decode(z, scale, c), scale * np.maximum(0, np.exp(z) * c - 1))


def test_month_bootstrap_preserves_conditional_mass_and_historical_full_case() -> None:
    index = pd.Index(["2021-01-04", "2021-01-05", "2021-02-01", "2021-02-02"])
    delta = pd.Series([1.0, 2.0, 3.0, 4.0], index=index)
    full = pd.DataFrame(dict(numerator=delta, mass=np.ones(4)), index=index)
    result = s.paired_months({2021: full})[0]
    old = b.block_interval(delta)
    for key in ["low", "high"]:
        assert result[key] == pytest.approx(old[key])
    assert result["delta"] == pytest.approx(old["mean"])
    weighted = pd.DataFrame(
        dict(numerator=[1.0, 6.0, 1.0, 6.0], mass=[1.0, 3.0, 1.0, 3.0]), index=index
    )
    answer = s.paired_months({2021: weighted})[0]
    assert answer["delta"] == pytest.approx(1.75)
    assert answer["low"] == pytest.approx(1.75)
    assert answer["high"] == pytest.approx(1.75)
