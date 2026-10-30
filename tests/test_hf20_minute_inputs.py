"""Small source/path fixtures, no research fits or outside-data readers."""

import numpy as np
import pandas as pd

from lstm_data.hf20_minute_inputs import path_features


def test_exact_path_summaries_and_genuine_zero_volume():
    prices = np.ones((2, 60, 4)) * 100
    prices[0, :, :] = np.exp(np.arange(60)[:, None] * 0.001) * 100
    observed = np.ones((2, 60), bool)
    volume = np.ones((2, 60))
    volume[1] = 0
    result = path_features(prices, volume, observed)
    np.testing.assert_allclose(result[0, 0], 59e-6, atol=1e-15)
    np.testing.assert_allclose(result[0, [1, 3, 4, 5, 6]], [1, 1, 0.25, 1, 1])
    np.testing.assert_allclose(result[0, 2], 0, atol=1e-12)
    np.testing.assert_array_equal(result[1], [0, 0, 0, 0, 0.25, 1, 1])


def test_missing_payload_never_becomes_observed_path_or_zero_volume():
    observed = np.ones((2, 60), bool)
    observed[0, 3] = False
    a = np.ones((2, 60, 4)) * 10
    b = a.copy()
    a[0, 3] = np.nan
    b[0, 3] = 1e100
    volume = np.ones((2, 60))
    np.testing.assert_array_equal(
        path_features(a, volume, observed), path_features(b, volume, observed)
    )
    np.testing.assert_array_equal(path_features(a, volume, observed)[0], [0, 0, 0, 0, 0.25, 0, 0])


def test_energy_halves_omit_crossing_transition_only():
    close = np.ones(60)
    close[30:] = 2
    prices = np.repeat(close[:, None], 4, axis=1)[None]
    result = path_features(prices, np.ones((1, 60)), np.ones((1, 60), bool))[0]
    np.testing.assert_allclose(result[[0, 1, 2, 3]], [np.log(2) ** 2, 1, 0, 1])


def test_utc_minute_template_keeps_sixty_unique_completed_intervals():
    for text in ["2024-03-08 14:30Z", "2024-03-11 13:30Z", "2024-12-24 16:30Z"]:
        start = pd.Timestamp(text)
        stamps = pd.date_range(start, periods=60, freq="min")
        assert stamps.nunique() == 60
        assert stamps[-1] + pd.Timedelta(minutes=1) == start + pd.Timedelta(hours=1)
        values = stamps.to_numpy(dtype="datetime64[ns]").view(np.int64)
        assert np.diff(values).tolist() == [60_000_000_000] * 59


def test_summary_network_shape_parameter_count_and_reload():
    import torch

    from lstm_data.hf20_minute_bc import model_for_summary

    model = model_for_summary().eval()
    x = torch.zeros(20, 48, 23)
    clocks = torch.zeros(20, 10)
    z = model(x, clocks)
    assert z.shape == (20,) and bool(torch.isfinite(z).all())
    reload = model_for_summary().eval()
    reload.load_state_dict(model.state_dict())
    torch.testing.assert_close(z, reload(x, clocks), rtol=0, atol=0)
    assert sum(p.numel() for p in model.parameters()) == 7339
    assert not model.training and model.dropout.p == 0.10


def test_summary_prefix_normalization_and_masked_placeholders():
    from lstm_data.hf20_minute_bc import normalized_features

    raw = np.zeros((2, 20, 7))
    raw[1, :, 5:] = 1
    raw[1, :, 0] = 0.04
    raw[:, :, 4] = 0.25
    hidden = raw.copy()
    hidden[0, :, :5] = 1e20
    a = normalized_features(raw, np.full(20, 0.1), dict(center=1, scale=2))
    b = normalized_features(hidden, np.full(20, 0.1), dict(center=1, scale=2))
    np.testing.assert_array_equal(a, b)
    np.testing.assert_array_equal(a[0, :, 0], np.zeros(20))
    np.testing.assert_allclose(a[1, :, 0], (np.log1p(4) - 1) / 2)


def test_same_original_session_hierarchy_one_and_two_origin_days():
    import torch

    from lstm_data.hf20_mag_designa import origin_weights
    from lstm_data.hf20_overnight_specialist import weighted_loss

    pred = torch.zeros(3, 20, requires_grad=True)
    # M targets1 on the one-origin day and3 on each two-origin day.
    signed = torch.tensor([np.expm1(1), np.expm1(3), np.expm1(3)], dtype=torch.float32)
    signed = signed[:, None].repeat(1, 20)
    weights = origin_weights(np.asarray(["2020-01-02", "2020-01-03", "2020-01-03"]))
    loss = weighted_loss(pred, signed, 1.0, weights)
    torch.testing.assert_close(loss, torch.tensor(5.0))
    loss.backward()
    assert pred.grad is not None and bool(torch.isfinite(pred.grad).all())
