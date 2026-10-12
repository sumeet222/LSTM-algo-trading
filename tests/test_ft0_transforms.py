from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.ft0_transforms import (
    ORDER,
    SCALED,
    FitObservation,
    check_window,
    fit_floors,
    fit_scaler,
    transform_reason,
)
from lstm_data.labels import UNIVERSE, FitWindow, fitting_window


def fit_window():
    return FitWindow(
        "SYNTHETIC:INNER_TRAIN",
        pd.Timestamp("2020-07-01T04:00Z"),
        pd.Timestamp("2020-08-01T04:00Z"),
        pd.Timestamp("2020-08-01T04:00Z"),
        "INNER_TRAIN",
    )


def observation(symbol, kind, value, day, slot=1, origin=None):
    timestamp = pd.Timestamp(day + "T14:30Z")
    return FitObservation(
        symbol,
        timestamp,
        kind,
        (symbol, day, slot),
        value,
        f"{symbol}:{kind}:{day}:{slot}",
        "a" * 64,
        "b" * 64,
        "SYNTHETIC",
        timestamp,
        origin,
    )


def floor_records():
    result = []
    for symbol in UNIVERSE:
        for day, value in zip(("2020-07-01", "2020-07-02", "2020-07-06"), (0.01, 0.02, 0.03)):
            for kind in ("RMS12", "RMS60", "RMS63"):
                result.append(observation(symbol, kind, value, day))
            result.append(observation(symbol, "VOLUME_H", value * 10000, day))
            result.append(observation(symbol, "VOLUME_D", value * 100000, day))
    return tuple(result)


def scaler_records():
    result = []
    for feature in SCALED:
        for day, value in zip(("2020-07-01", "2020-07-02", "2020-07-06"), (1.0, 2.0, 100.0)):
            if feature == "M2":
                for origin in (1, 2):
                    result.append(observation("AAPL", feature, value, day, origin, origin))
            else:
                result.append(observation("AAPL", feature, value, day))
    return tuple(result)


def test_hand_fitted_positive_p05_pseudocounts_dedup_and_validation_extreme_invariance():
    records = floor_records()
    cert = fit_floors(records, fit_window(), "synthetic", allow_synthetic=True)
    for p in cert.values:
        assert p.hourly_floor == pytest.approx(0.01)  # pooled six RMS12/RMS60 values
        assert p.daily_floor == pytest.approx(0.011)
        assert p.hourly_pseudocount == 2.0 and p.daily_pseudocount == 20.0
    heldout = replace(
        records[0],
        timestamp=pd.Timestamp("2023-07-03T14:30Z"),
        available_at=pd.Timestamp("2023-07-03T14:30Z"),
        value=1e12,
        key=("AAPL", "2023-07-03", 1),
    )
    assert (
        fit_floors(records + records + (heldout,), fit_window(), "synthetic", allow_synthetic=True)
        == cert
    )
    with pytest.raises(ValueError, match="PENDING"):
        fit_floors(records, fit_window(), "synthetic")
    with pytest.raises(ValueError, match="CONTRADICTORY"):
        fit_floors(
            records + (replace(records[0], value=999.0),),
            fit_window(),
            "synthetic",
            allow_synthetic=True,
        )


def test_pooled_median_unscaled_mad_native_bounded_no_clipping_and_wrong_lineage():
    cert = fit_scaler(scaler_records(), fit_window(), "synthetic", allow_synthetic=True)
    assert cert.order == ORDER
    assert cert.centers[0] == 2 and cert.scales[0] == 1 and cert.methods[0] == "MAD"
    cutoff = pd.Timestamp("2020-08-03T14:30Z")
    value, _, novel = cert.apply(
        "M1", 1000.0, cutoff, source_binding="a" * 64, action_binding="b" * 64
    )
    assert value == 998 and not novel
    assert cert.apply("B2", 0.5, cutoff, source_binding="a" * 64, action_binding="b" * 64)[0] == 0.5
    with pytest.raises(ValueError, match="MISMATCH"):
        cert.apply("M1", 1.0, cutoff, source_binding="c" * 64, action_binding="b" * 64)
    with pytest.raises(ValueError, match="PROVENANCE"):
        replace(cert, order=tuple(reversed(ORDER)))


def test_weighted_m2_two_origins_50_50_without_window_appearance_copies():
    records = tuple(r for r in scaler_records() if r.kind != "M2")
    m2 = tuple(observation("AAPL", "M2", 0.0, f"2020-07-{day:02}", 1, 1) for day in (1, 2, 6, 7, 8))
    m2 += (observation("AAPL", "M2", 10.0, "2020-07-01", 2, 2),)
    cert = fit_scaler(records + m2 + m2, fit_window(), "weighted", allow_synthetic=True)
    assert cert.centers[SCALED.index("M2")] == 5
    assert cert.scales[SCALED.index("M2")] == 5
    totals = {1: 0.0, 2: 0.0}
    for (feature, key), weight in zip(cert.keys, cert.weights):
        if feature == "M2":
            totals[key[2]] += weight
    assert totals[1] == pytest.approx(0.5) and totals[2] == pytest.approx(0.5)


@pytest.mark.parametrize(
    "values,method",
    [
        ((0.0, 0.0, 0.0, 1.0, 2.0), "IQR_1.349"),
        ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0), "AUDITED_POPULATION_SD"),
        ((2.0, 2.0, 2.0), "CONSTANT"),
    ],
)
def test_exact_fallbacks_and_constant_novel_variation(values, method):
    records = tuple(r for r in scaler_records() if r.kind != "M1")
    records += tuple(
        observation("AAPL", "M1", value, f"2020-07-{i + 1:02}") for i, value in enumerate(values)
    )
    cert = fit_scaler(records, fit_window(), method, allow_synthetic=True)
    assert cert.methods[0] == method
    if method == "CONSTANT":
        value, _, novel = cert.apply(
            "M1",
            999.0,
            pd.Timestamp("2020-08-03T14:30Z"),
            source_binding="a" * 64,
            action_binding="b" * 64,
        )
        assert value == 0 and novel


def test_factual_fit_time_historical_training_application_and_held_out_prohibition():
    window = fit_window()
    step = pd.Timestamp("2020-07-10T14:30Z")
    assert transform_reason(window, step, "ASOF") == "FIT_AFTER_STEP_CUTOFF"
    assert (
        transform_reason(window, step, "HISTORICAL_TRAINING", pd.Timestamp("2020-07-15T14:30Z"))
        == "HISTORICAL_TRAINING_TRANSFORM_ONLY"
    )
    assert (
        transform_reason(window, step, "HISTORICAL_TRAINING", pd.Timestamp("2023-07-03T14:30Z"))
        == "TRAINING_ORIGIN_OUTSIDE_CERTIFIED_PREFIX"
    )
    for stage in ("WF1", "WF2", "PRECONFIRMATION"):
        # Explicit branch narrowing in implementation; fixture strings are accepted at runtime.
        actual = fitting_window(stage, "INNER_TRAIN", fitted_at="2024-07-01T04:00Z")
        check_window(actual)
        with pytest.raises(ValueError, match="BOUNDARY"):
            check_window(replace(actual, stop=actual.stop - pd.Timedelta(days=1)))
    with pytest.raises(ValueError, match="PREFIX"):
        check_window(replace(window, phase="INNER_VALIDATION"))


def test_no_real_empirical_fitting_even_documented_caller_assertion():
    records = tuple(replace(r, basis="DOCUMENTED") for r in floor_records())
    with pytest.raises(ValueError, match="PENDING"):
        fit_floors(records, fit_window(), "assertion", allow_synthetic=True)
    assert np.isfinite(
        fit_floors(floor_records(), fit_window(), "synthetic", allow_synthetic=True)
        .values[0]
        .hourly_floor
    )
    assert Path("docs/track_a/decisions/TA_P2_FT0_Q_VOLUME_001_v1.json").is_file()
