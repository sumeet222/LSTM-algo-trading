"""P020 source isolation, component mathematics, causality and preprocessing oracles."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.hf1m_ft16_fit import robust, target_values
from lstm_data.hf1m_ft16_loader import inverse_t2, load_model_input
from lstm_data.hf1m_ft16_math import regime_rolling, rolling, volume_fields
from lstm_data.hf1m_ft16_source import configuration, read_hourly


def volume_fixture(missing: int, conflict: int = 0, quarantine: int = 0) -> pd.DataFrame:
    observed = 60 - missing - conflict - quarantine
    return pd.DataFrame(
        {
            "hour_id": ["SYNTHETIC"],
            "ticker": ["AAPL"],
            "session_date_et": ["2020-11-02"],
            "observed_volume": [float(observed * 10)],
            "missing_count": [missing],
            "conflict_count": [conflict],
            "quarantine_count": [quarantine],
            "invalid_minutes": [0],
            "genuine_count": [observed],
            "expected_minutes": [60],
            "longest_gap_minutes": [missing + conflict + quarantine],
            "observed_volume_complete": [observed == 60],
        }
    )


@pytest.mark.parametrize("missing", [0, 1, 2, 5, 6, 60])
def test_absent_volume_zero_is_feature_only_lower_bound(missing):
    frame = volume_fixture(missing)
    before = frame.copy(deep=True)
    result = volume_fields(frame)
    pd.testing.assert_frame_equal(frame, before)
    assert result.assumed_zero_missing_count.iloc[0] == missing
    assert bool(result.volume_usable_for_feature.iloc[0]) == (missing <= 5)
    assert bool(result.volume_missing_assumed_zero.iloc[0]) == (missing > 0)
    assert result.observed_volume_sum.iloc[0] == (60 - missing) * 10
    if missing > 5:
        assert np.isnan(result.volume_for_feature.iloc[0])


@pytest.mark.parametrize("conflict,quarantine", [(1, 0), (0, 1), (2, 3)])
def test_conflicts_and_quarantines_never_become_zero_volume(conflict, quarantine):
    r = volume_fields(volume_fixture(0, conflict, quarantine))
    assert not r.volume_usable_for_feature.iloc[0]
    assert not r.volume_missing_assumed_zero.iloc[0]
    assert r.quarantine_volume_unknown_count.iloc[0] == conflict + quarantine


def test_real_observed_zero_is_not_absent_placeholder():
    f = volume_fixture(0)
    f["observed_volume"] = 0.0
    r = volume_fields(f)
    assert r.source_volume_observed.iloc[0] and r.volume_for_feature.iloc[0] == 0
    assert not r.volume_missing_assumed_zero.iloc[0]


def test_rolling_does_not_compress_missing_positions():
    x = np.arange(1.0, 66.0)[:, None]
    x[30:33] = np.nan
    assert np.isnan(rolling(x, 60, 57)[-1, 0])
    x[31] = 32.0
    assert np.isfinite(rolling(x, 60, 57)[-1, 0])
    assert np.isnan(rolling(x[:10], 12, 12)[-1, 0])


def test_volume_regime_history_reset():
    values = np.ones((80, 1))
    basis = np.array([["pre"]] * 40 + [["post"]] * 40)
    result = regime_rolling(values, basis, 20, 19)
    assert np.isnan(result[40:59]).all()
    assert result[59, 0] == 1


def test_20_stock_target_exact_median_unscaled_mad():
    r = np.arange(-10, 10, dtype=float)[None, :] / 1000
    y, mad_center, mad = target_values(r, 1e-4)
    assert mad_center[0] == pytest.approx(-0.0005)
    assert mad[0] == pytest.approx(0.005)
    np.testing.assert_allclose(y, (r + 0.0005) / 0.0051)
    r[0, 19] = np.nan
    assert np.isnan(target_values(r, 1e-4)[0]).all()
    with pytest.raises(ValueError, match="EXACT20"):
        target_values(np.ones((2, 19)), 1e-4)


def test_genuine_target_tail_not_clipped_and_t2_inverse_once():
    r = np.zeros((1, 20))
    r[0, -1] = 0.4
    y, _, _ = target_values(r, 1e-4)
    assert y[0, -1] == 4000
    for s in [1e-6, 0.8, 2.0]:
        np.testing.assert_allclose(inverse_t2(np.arcsinh(y / s), s), y, rtol=1e-12, atol=1e-12)


def test_train_robust_scale_constant_and_unscaled_mad():
    assert robust(np.array([1.0, 2.0, 3.0, 4.0, 100.0]))["scale"] == 1
    assert robust(np.ones(10))["scale"] == 1
    assert robust(np.ones(10))["method"] == "EXACT_CONSTANT_SCALE1"


def test_protected_read_and_unknown_split_fail_before_file_access():
    with pytest.raises(ValueError, match="PROTECTED"):
        read_hourly(configuration(), stop="2026-01-01")
    for name in ["confirmation", "heldout", "test", "all", "2026"]:
        with pytest.raises(ValueError, match="DENIED"):
            load_model_input(Path("nonexistent"), split=name, fit_version="refit")
    with pytest.raises(ValueError, match="FIT_MISMATCH"):
        load_model_input(Path("nonexistent"), split="development", fit_version="inner")


@pytest.mark.parametrize(
    "old",
    [
        {"revision": "ad48edaf3828ec855ab4a5bb1b8336fa0b68cdec"},
        {"feature_id": "FT0", "symbols": ["AAPL", "JPM", "JNJ", "WMT", "CAT"]},
        {"feature_id": "FT1_HF20_HOURLY_NATIVE_V1"},
        {"parent_namespace": "HF20_HF1M_LONG_v1"},
    ],
)
def test_old_source_contract_rejection(tmp_path, old):
    import json

    p = tmp_path / "old.json"
    p.write_text(json.dumps(old))
    with pytest.raises(ValueError, match="IDENTITY"):
        load_model_input(p, split="refit", fit_version="refit")


def one_hour_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    from lstm_data.hf1m_action_audit import SYMBOLS

    rows = []
    for stock in SYMBOLS:
        rows.append(
            {
                "ticker": stock,
                "hour_id": stock + ":SYNTHETIC:0",
                "session_date_et": "2020-11-02",
                "hour_start_utc": pd.Timestamp("2020-11-02T14:30Z"),
                "hour_end_utc": pd.Timestamp("2020-11-02T15:30Z"),
                "is_stub": False,
                "open": 100.0,
                "high": 100.0,
                "low": 100.0,
                "close": 100.0,
                "close_input_cap5": 100.0,
                "observed_volume": 0.0,
                "missing_count": 0,
                "quarantine_count": 0,
                "conflict_count": 0,
                "invalid_minutes": 0,
                "genuine_count": 60,
                "expected_minutes": 60,
                "longest_gap_minutes": 0,
                "observed_volume_complete": True,
                "proxy_count": 0,
                "price_basis_id": "SYNTHETIC",
            }
        )
    frame = pd.DataFrame(rows)
    fields = frame[["hour_id"]].assign(
        volume_basis_id="SYNTHETIC", hour_feature_dependency_action_crossing=False
    )
    return frame, fields


def test_zero_range_and_observed_zero_volume_are_preserved_in_components():
    from lstm_data.hf1m_ft16_math import build

    frame, fields = one_hour_panel()
    c = build(frame, fields)
    assert (c.values["B1"] == 0).all() and (c.values["B2"] == 0).all()
    assert c.volume.source_volume_observed.all()
    assert not c.volume.volume_missing_assumed_zero.any()
    assert (c.source["volume_for_feature"] == 0).all()


def test_missing_extrema_cannot_replace_genuine_endpoint_or_become_observed_zero():
    from lstm_data.hf1m_ft16_math import build

    frame, fields = one_hour_panel()
    frame.loc[0, ["high", "low"]] = np.nan
    frame.loc[0, "quarantine_count"] = 1
    frame.loc[0, "genuine_count"] = 59
    frame.loc[0, "observed_volume_complete"] = False
    c = build(frame, fields)
    j = 4  # canonical AAPL position; the altered synthetic source row is VZ at index0.
    assert np.isnan(c.values["B1"][0, 0]) and np.isnan(c.values["B2"][0, 0])
    assert c.source["close"][0, 0] == 100.0
    assert np.isnan(c.source["volume_for_feature"][0, 0])
    assert c.source["close"][0, j] == 100.0
