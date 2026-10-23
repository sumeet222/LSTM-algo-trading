"""Independent forecasting-moment and protected-route oracles for P024 postfit work."""

import numpy as np
import pandas as pd

from lstm_data.optimization_screen_supplement import forecast_profile, read_updates


def test_affine_calibration_and_zero_identity_without_row_independence():
    # A day with two origins has the same total weight as a day with one origin.
    prediction = np.tile(np.linspace(-2, 2, 20), 3)
    target = 1.5 + 2.0 * prediction
    f = pd.DataFrame(
        dict(
            TG20=target,
            pred_original_TG20=prediction,
            session_date_et=np.repeat(["2025-07-15", "2025-07-15", "2025-07-16"], 20),
            origin_id=np.repeat([1, 2, 3], 20),
        )
    )
    p = forecast_profile(f)
    assert p["rows"] == 60 and p["origins"] == 3 and p["sessions"] == 2
    np.testing.assert_allclose(p["calibration_slope_y_on_prediction"], 2.0, rtol=0, atol=1e-12)
    np.testing.assert_allclose(p["calibration_intercept"], 1.5, rtol=0, atol=1e-12)
    np.testing.assert_allclose(p["mse_identity_lhs"], p["mse_identity_rhs"], atol=1e-12)
    assert p["top4_recall"] == p["bottom4_recall"] == 1.0


def test_zero_forecast_does_not_invent_a_calibration_slope_or_rank_skill():
    f = pd.DataFrame(
        dict(
            TG20=np.arange(-10, 10),
            pred_original_TG20=np.zeros(20),
            session_date_et=["2025-07-15"] * 20,
            origin_id=[1] * 20,
        )
    )
    p = forecast_profile(f)
    assert p["calibration_slope_y_on_prediction"] is None
    assert np.isnan(p["top4_recall"]) and np.isnan(p["bottom4_recall"])
    assert p["mse_identity_lhs"] == p["mse_identity_rhs"] == 0.0


def test_nested_optimizer_rates_preserve_exact_json_float(tmp_path):
    p = tmp_path / "updates.jsonl"
    p.write_text('{"lr":[0.0003,0.0003],"weight_decay":[0.01,0.0]}\n')
    f = read_updates(p)
    assert f.iloc[0].lr == [0.0003, 0.0003]
    assert float(f.iloc[0].lr[0]).hex() == (0.0003).hex()
    assert f.iloc[0].weight_decay == [0.01, 0.0]


def test_one_ulp_wrong_rate_is_not_hidden_by_tolerance(tmp_path):
    import json

    p = tmp_path / "updates.jsonl"
    wrong = float(np.nextafter(0.0003, np.inf))
    p.write_text(json.dumps(dict(lr=[wrong, wrong], weight_decay=[0.01, 0.0])) + "\n")
    actual = read_updates(p).iloc[0].lr
    assert actual == [wrong, wrong]
    assert actual != [0.0003, 0.0003]


def test_empty_zero_update_log_has_explicit_schema(tmp_path):
    p = tmp_path / "empty.jsonl"
    p.write_text("")
    frame = read_updates(p)
    assert frame.empty and {"lr", "phase", "epoch", "postclip_norm"} <= set(frame.columns)
