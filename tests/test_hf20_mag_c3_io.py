"""Decisive arithmetic/key fixtures; no neural construction, training or inference."""

import numpy as np
import pandas as pd
import pytest

from lstm_data import hf20_mag_designa as saved
from lstm_data.hf20_mag_c3_io import (
    clock_group,
    decode,
    effective_sessions,
    fit_categories,
    residual_exp,
    validate_panel,
)


def calibration() -> pd.DataFrame:
    return pd.DataFrame(
        dict(
            origin_id=["i0", "i1", "o0", "o1", "o2"],
            session_date_et=["a", "b", "a", "b", "c"],
            category=["INTRADAY", "INTRADAY", "OVERNIGHT", "OVERNIGHT", "OVERNIGHT"],
            weight=[0.1, 0.2, 0.15, 0.25, 0.3],
            A=[0.2, 0.6, 0.8, 1.0, 1.4],
            Mhat=np.zeros(5),
        )
    )


def test_weighted_moments_and_session_pooling() -> None:
    cal = calibration()
    fit = fit_categories(cal, 1.0)
    global_c = float(np.array([0.1, 0.2, 0.15, 0.25, 0.3]) @ np.array([1.2, 1.6, 1.8, 2.0, 2.4]))
    assert fit[0]["c0"] == pytest.approx(global_c)
    assert fit[0]["c_raw"] == pytest.approx((0.1 * 1.2 + 0.2 * 1.6) / 0.3)
    assert fit[0]["n_eff"] == pytest.approx(1.8)
    assert fit[1]["n_eff"] == pytest.approx(2.8)
    for f in fit:
        assert f["rho"] == pytest.approx(f["n_eff"] / (f["n_eff"] + 25))
        assert f["c_star"] == pytest.approx(global_c + f["rho"] * (f["c_raw"] - global_c))
        assert min(global_c, f["c_raw"]) <= f["c_star"] <= max(global_c, f["c_raw"])


def test_stock_row_duplication_does_not_inflate_effective_sessions() -> None:
    cal = calibration()
    original = fit_categories(cal, 1.0)
    doubled = pd.concat([cal, cal], ignore_index=True)
    doubled["weight"] /= 2
    repeated = fit_categories(doubled, 1.0)
    for a, b in zip(original, repeated, strict=True):
        for key in ["c0", "c_raw", "n_eff", "rho", "c_star"]:
            assert a[key] == pytest.approx(b[key])


def test_empty_nonfinite_and_invalid_inputs_block() -> None:
    cal = calibration()
    with pytest.raises(ValueError, match="EMPTY"):
        fit_categories(cal.loc[cal.category.eq("INTRADAY")], 1.0)
    bad = cal.copy()
    bad.loc[0, "Mhat"] = np.inf
    with pytest.raises(ValueError):
        fit_categories(bad, 1.0)
    bad = cal.copy()
    bad.loc[0, "weight"] = 0
    with pytest.raises(ValueError, match="WEIGHTS"):
        fit_categories(bad, 1.0)
    with pytest.raises(ValueError):
        effective_sessions(cal.iloc[:0])
    with pytest.raises(ValueError):
        decode(np.array([1.0]), 0.0, 1.0)


def test_unconstrained_residual_and_single_decode_preserve_ranks() -> None:
    raw = np.array([-0.1, 0.2])
    cal = pd.DataFrame(dict(A=[0.2, 0.4], Mhat=raw))
    np.testing.assert_allclose(residual_exp(cal, 1.0), np.exp(np.log1p([0.2, 0.4]) - raw))
    np.testing.assert_allclose(decode(raw, 1.0, 1.2), np.maximum(0, np.exp(raw) * 1.2 - 1))
    z = np.tile(np.linspace(0.1, 2, 20), (2, 1))
    factor = np.array([1.1, 1.5])[:, None]
    old = np.expm1(z)
    new = decode(z, 0.01, factor)
    np.testing.assert_array_equal(pd.DataFrame(old).rank(axis=1), pd.DataFrame(new).rank(axis=1))
    assert (decode(np.array([0.0, 0.01, 0.02, 1.0]), 1.0, 0.5)[:3] == 0).all()


def test_exact_panel_stock_order_and_fixed_category_map() -> None:
    records = []
    for n, slot in enumerate(saved.SLOTS):
        group = clock_group(slot)
        for ticker in saved.SYMBOLS:
            records.append(
                dict(
                    origin_id=f"origin{n}",
                    ticker=ticker,
                    slot=slot,
                    category=group,
                    session_date_et="2001-01-02",
                    weight=1 / (7 * 20),
                    exit_end_utc=pd.Timestamp("2001-01-02T20:00Z")
                    if group == "INTRADAY"
                    else pd.Timestamp("2001-01-03T20:00Z"),
                )
            )
    f = pd.DataFrame(records)
    validate_panel(f)
    assert [clock_group(s) for s in saved.SLOTS] == ["INTRADAY"] * 3 + ["OVERNIGHT"] * 4
    with pytest.raises(ValueError):
        clock_group("16:30")
    bad = f.copy()
    bad.loc[0, "ticker"] = bad.loc[1, "ticker"]
    with pytest.raises(AssertionError):
        validate_panel(bad)
    early = f.iloc[:20].copy()
    early["category"] = "OVERNIGHT"
    early["exit_end_utc"] = pd.Timestamp("2001-01-03T20:00Z")
    # Normalize weights to this standalone fixture's single admitted origin.
    early["weight"] = 1 / 20
    with pytest.raises(AssertionError):
        validate_panel(early)
    validate_panel(early, {"2001-01-02"})
    bad = f.copy()
    bad.loc[0, "category"] = "OVERNIGHT"
    with pytest.raises(AssertionError):
        validate_panel(bad)
