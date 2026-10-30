"""Price-only newest-hour invariants; synthetic fixtures, no research starts."""

import numpy as np
import pytest
import torch

from lstm_data.hf20_s3c_priceonly import five_channels, model_for_price, price_channels


def test_no_bridged_return_and_no_first_position_return():
    prices = np.ones((1, 20, 60, 4)) * 10
    prices[:, :, 3:, :] = 20
    observed = np.ones((1, 20, 60), bool)
    observed[:, :, 2] = False
    prices[:, :, 2] = np.nan
    native = price_channels(prices, observed)
    x = five_channels(native, observed, np.full(20, 0.1))
    np.testing.assert_array_equal(x[..., [0, 2, 3], 0], 0)
    np.testing.assert_array_equal(x[..., [0, 2, 3], 3], 0)
    assert x.shape == (1, 20, 60, 5) and np.isfinite(x).all()
    np.testing.assert_array_equal(
        x[..., 4], np.broadcast_to(np.arange(60, dtype=np.float32) / 59, (1, 20, 60))
    )


def test_native_and_model_hidden_missing_payload_invariance_and_gradients():
    prices = np.ones((1, 20, 60, 4)) * 10
    observed = np.ones((1, 20, 60), bool)
    observed[:, :, 12] = False
    altered = prices.copy()
    altered[:, :, 12] = np.nan
    np.testing.assert_array_equal(
        price_channels(prices, observed), price_channels(altered, observed)
    )
    x = five_channels(price_channels(prices, observed), observed, np.full(20, 0.1)).reshape(
        20, 60, 5
    )
    a = torch.tensor(x, requires_grad=True)
    changed = x.copy()
    changed[:, 12, :2] = 1e30
    changed[:, 13, 0] = -1e30
    z = torch.tensor(changed, requires_grad=True)
    model = model_for_price().eval()
    y = model(torch.zeros(20, 48, 16), torch.zeros(20, 10), a)
    yy = model(torch.zeros(20, 48, 16), torch.zeros(20, 10), z)
    torch.testing.assert_close(y, yy, rtol=0, atol=0)
    y.sum().backward()
    yy.sum().backward()
    assert a.grad is not None and z.grad is not None
    torch.testing.assert_close(a.grad, z.grad, rtol=0, atol=0)
    torch.testing.assert_close(a.grad[:, 12, :2], torch.zeros(20, 2), rtol=0, atol=0)
    torch.testing.assert_close(a.grad[:, 13, 0], torch.zeros(20), rtol=0, atol=0)
    assert all(p.grad is None or bool(torch.isfinite(p.grad).all()) for p in model.parameters())


def test_all_missing_embedding_is_exact_zero_despite_position_and_biases():
    minute = torch.zeros(3, 60, 5)
    minute[..., 4] = torch.arange(60) / 59
    minute[..., :2] = float("nan")
    model = model_for_price().eval()
    with torch.no_grad():
        for name, parameter in model.minute_lstm.named_parameters():
            if name.startswith("bias"):
                parameter.fill_(0.9 if "ih" in name else 0.7)
    embedding = model.minute_embedding(minute)
    torch.testing.assert_close(embedding, torch.zeros(3, 8), rtol=0, atol=0)
    embedding.sum().backward()
    for p in model.minute_lstm.parameters():
        assert p.grad is not None
        torch.testing.assert_close(p.grad, torch.zeros_like(p), rtol=0, atol=0)


def test_count_shape_full_history_scale_and_reload():
    observed = np.ones((1, 20, 60), bool)
    p = np.repeat((np.exp(np.arange(60) * 0.001) * 10)[None, None, :, None], 20, axis=1)
    prices = np.repeat(p, 4, axis=-1)
    native = price_channels(prices, observed)
    x = five_channels(native, observed, np.full(20, 0.1))
    np.testing.assert_allclose(x[:, :, 1:, 0], 0.01, rtol=1e-6)
    np.testing.assert_array_equal(x[:, :, :, 1], 0)
    model = model_for_price().eval()
    other = model_for_price().eval()
    other.load_state_dict(model.state_dict())
    with torch.inference_mode():
        y = model(
            torch.ones(20, 48, 16), torch.zeros(20, 10), torch.from_numpy(x.reshape(20, 60, 5))
        )
        z = other(
            torch.ones(20, 48, 16), torch.zeros(20, 10), torch.from_numpy(x.reshape(20, 60, 5))
        )
    assert y.shape == (20,) and bool(torch.isfinite(y).all())
    torch.testing.assert_close(y, z, rtol=0, atol=0)
    assert sum(p.numel() for p in model.parameters()) == 6931
    assert model.dropout.p == 0.10 and model.minute_lstm.dropout == 0
    opt = torch.optim.AdamW(model.parameters(), lr=0.001)
    assert not opt.state


def test_illegal_floor_and_observed_bad_price_fail_closed():
    flags = np.ones((1, 20, 60), bool)
    with pytest.raises(ValueError, match="FLOORS"):
        five_channels(np.zeros((1, 20, 60, 2)), flags, np.zeros(20))
    with pytest.raises(ValueError, match="PRICE"):
        price_channels(np.zeros((1, 20, 60, 4)), flags)


def test_original_optimizer_groups_and_four_year_reaggregation():
    import pandas as pd

    from lstm_data.hf20_mag_designa import optimizer
    from lstm_data.hf20_s3c_price_report import equal_year

    model = model_for_price()
    opt = optimizer(model)
    assert not opt.state and [g["weight_decay"] for g in opt.param_groups] == [0.01, 0.0]
    assert all(
        g["lr"] == 0.001 and g["eps"] == 1e-8 and g["betas"] == (0.9, 0.999)
        for g in opt.param_groups
    )
    assert sum(p.numel() for g in opt.param_groups for p in g["params"]) == 6931
    frame = pd.DataFrame(
        dict(
            year=["2021", "2022", "2023", "2024"],
            arm=["X"] * 4,
            scope=["FULL"] * 4,
            predicted=[1.0, 2.0, 3.0, 4.0],
            observed=[2.0, 2.0, 2.0, 2.0],
            raw_MSE=[1.0, 2.0, 3.0, 4.0],
            rows=[20] * 4,
            origins=[1] * 4,
            sessions=[1] * 4,
            ratio=[0.5, 1.0, 1.5, 2.0],
        )
    )
    eq = equal_year(frame, ["scope", "arm"]).iloc[-1]
    assert eq["raw_MSE"] == 2.5 and eq["ratio"] == 1.25 and eq["rows"] == 80
