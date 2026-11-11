"""Original magnitude/controls retain their causal frontier without the legacy sign."""

from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.trading.track2.final_directional_slate.common import ROOT, load
from lstm_data.trading.track2.final_directional_slate.risk_inputs import RiskInputs, control, factor
from lstm_data.trading.track2.rapid_exit_audit.io import as_rows
from lstm_data.trading.track2.rapid_v1.shared_features import FeatureCache
from lstm_data.trading.track2.rapid_v1.strategies import evaluate


def test_references_units_clip_and_first_square_ewma():
    sample = np.arange(1, 61, dtype=float)[:, None] / 10000
    med, rms, count = control(sample)
    variance = sample[0, 0] ** 2
    for x in sample[1:, 0]:
        variance = 0.94 * variance + 0.06 * x * x
    assert med[0] == np.median(sample)
    assert rms[0] == np.sqrt(variance) and count[0] == 60
    a = sample.copy()
    a[0] = np.nan
    assert np.isnan(control(a)[0]).all()
    assert np.isnan(control(sample[:39])[0]).all()
    assert np.array_equal(
        factor(np.ones(3), np.full(3, 0.25), np.array([0.1, 1.0, 10.0])), [1.5, 1.0, 0.5]
    )


def test_cache_has_original_models_and_no_five_day_mask():
    r = load(ROOT / "RISK_INPUT_READINESS.json")
    assert r["original_forecasts"] == 131111 and r["rows"] == 140280
    assert r["counts"]["EQUAL"] == 140280 and not r["sign_mask_used"]
    risk = RiskInputs()
    old = Path("trading/track2/stage35/completion_v2/audits/signals/F21/2021-01-05.parquet")
    frame = pd.read_parquet(old)
    assert frame.g_EQUAL.isna().all()  # Legacy missing-sign day, not neural input failure.
    for row in as_rows(frame):
        t = int(pd.Timestamp(row.origin).value // 60_000_000_000)
        g = risk.values(t, t + 3)
        assert g[:, 0].tolist() == [1.0] * 20
        if row.input_eligible:
            assert np.isfinite(g[list(frame.ticker.unique()).index(row.ticker), 3])


def test_timestamp_units_and_future_mutation_separation():
    ns = pd.DatetimeIndex(["2021-01-04T15:30:00Z"]).as_unit("ns")
    us = ns.as_unit("us")
    assert ns.as_unit("ns").astype("int64").tolist() == us.as_unit("ns").astype("int64").tolist()
    before = np.arange(60 * 20, dtype=float).reshape(60, 20) / 1e5
    future = np.ones((10, 20))
    full = np.r_[before, future]
    x = control(full[:60])
    full[60:] = 1e9
    y = control(full[:60])
    for a, b in zip(x, y, strict=True):
        assert np.array_equal(a, b)


def test_risk_input_frontier_and_common_vs_attainable():
    risk = RiskInputs()
    t = int(risk.data["origin"][100])
    too_early = risk.values(t, t)
    assert np.isnan(too_early[:, 3]).all()
    assert np.array_equal(too_early[:, 0], np.ones(20))
    for at in (0, 100, 1000):
        t = int(risk.data["origin"][at])
        d = t + 3
        allg = risk.values(t, d)
        for j in range(20):
            x = risk.multiplier(t, d, j, "EQUAL", "MATCHED")
            assert (x == Decimal(1)) == bool(np.isfinite(allg[j]).all())


def test_direction_functions_never_receive_risk_or_future_outcomes():
    cache = FeatureCache(
        Path(
            "trading/track2/rapid_v1/cache/49a590a7d44f5900b67cf2faf37584b584a942807cca2fbab262250b80ea1f93"
        )
    )
    f = cache.frames("2021-01-04")[1]
    before = {s: evaluate(s, f) for s in ("R01", "R07", "M04")}
    risk = RiskInputs()
    risk.data["g"][-1] *= 1000
    assert before == {s: evaluate(s, f) for s in before}
