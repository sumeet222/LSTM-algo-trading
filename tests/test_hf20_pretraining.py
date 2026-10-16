"""Focused independent HF20 causal, numeric, calendar, identity and lock oracles."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.hf20_features import COMMON, build_components, rolling
from lstm_data.hf20_source import BARRIER, SYMBOLS
from lstm_data.hf20_transforms import fit_recipe, robust, target_decomposition
from lstm_data.hf_hourly_audit import calendar_grid


@pytest.fixture(scope="module")
def candles() -> pd.DataFrame:
    grid, _ = calendar_grid("2022-06-01", "2023-08-31")
    grid = grid.loc[~grid.stub]
    frames = []
    t = np.arange(len(grid), dtype=float)
    for j, symbol in enumerate(SYMBOLS):
        close = 50 + j + t * 0.001 + 0.2 * np.sin(t / (17 + j))
        opening = close / np.exp(0.0005 * np.sin(t / 11 + j))
        frames.append(
            pd.DataFrame(
                dict(
                    symbol=symbol,
                    datetime=pd.DatetimeIndex(grid.start).tz_convert("America/New_York"),
                    UTC=grid.start.to_numpy(),
                    timeframe="1h",
                    open=opening,
                    high=np.maximum(opening, close) * 1.001,
                    low=np.minimum(opening, close) * 0.999,
                    close=close,
                    close_adj=close,
                    volume=100000 + t * 7 + j * 1000,
                )
            )
        )
    return pd.concat(frames, ignore_index=True)


@pytest.fixture(scope="module")
def components(candles: pd.DataFrame):
    return build_components(candles, start="2022-06-01", stop="2023-08-31")


def test_rolling_oracle_and_no_missing_position_compression():
    v = np.arange(1, 81, dtype=float)[:, None]
    v[30] = np.nan
    r = rolling(v, 60, 57, square=True)
    assert r[59, 0] == pytest.approx(math.sqrt(np.nanmean(v[:60] ** 2)))
    assert np.isnan(rolling(v, 12, 12)[35, 0])
    v[30:33] = np.nan
    assert np.isnan(rolling(v, 60, 57)[59, 0])


def test_exact_nonzero_constant_fallback_and_nonconstant_sd():
    p = robust(np.full(1001, 0.1))
    assert p["method"] == "CONSTANT_ZERO" and p["scale"] == 1
    p = robust(np.array([0.0] * 99 + [1.0]))
    assert p["method"] == "POPULATION_SD" and p["scale"] > 0


def test_all_channels_independent_arithmetic_and_unique_fit(components):
    c = components
    recipe, arrays = fit_recipe(c, "2023-05-31")
    i = int(np.flatnonzero(c.grid.session.eq("2023-06-15"))[1])
    j = 0
    v, p = c.values, recipe["floors"][j]
    x = c.source
    assert v["OC"][i, j] == pytest.approx(math.log(x["close"][i, j] / x["open"][i, j]))
    assert v["RMS12"][i, j] == pytest.approx(np.sqrt(np.mean(v["OC"][i - 11 : i + 1, j] ** 2)))
    d = c.days.index("2023-06-15")
    previous = [k for k, day in enumerate(c.regular_days) if day < "2023-06-15"]
    daily = c.daily_close[previous, j]
    dv = c.daily_volume[previous, j]
    drms = math.sqrt(np.mean(np.diff(np.log(daily[-64:])) ** 2))
    slot = int(c.grid.slot.iloc[i])
    before = c.grid.index[(c.grid.slot == slot) & (c.grid.session < "2023-06-15")][-20:]
    qmean = float(np.mean(x["volume"][before, j]))
    # EMA is an independent scalar recurrence, not the production IndicatorState.
    ema = {k: float(x["close"][0, j]) for k in (6, 18, 24, 72)}
    for close in x["close"][1 : i + 1, j]:
        for k in ema:
            ema[k] = 2 / (k + 1) * close + (1 - 2 / (k + 1)) * ema[k]
    changes = np.diff(x["close"][: i + 1, j])
    gain = float(np.maximum(changes[:14], 0).mean())
    loss = float(np.maximum(-changes[:14], 0).mean())
    for delta in changes[14:]:
        gain = (13 * gain + max(delta, 0)) / 14
        loss = (13 * loss + max(-delta, 0)) / 14
    expected = dict(
        M1=v["OC"][i, j] / max(v["RMS60"][i, j], p["hourly_floor"]),
        M3=math.log(daily[-1] / daily[-6]) / (math.sqrt(5) * max(drms, p["daily_floor"])),
        M4=math.log(daily[-21] / daily[-126]) / (math.sqrt(105) * max(drms, p["daily_floor"])),
        V1=math.log(max(v["RMS12"][i, j], p["hourly_floor"])),
        V2=math.log(max(v["RMS60"][i, j], p["hourly_floor"])),
        B1=math.log(x["high"][i, j] / x["low"][i, j]),
        B2=(2 * x["close"][i, j] - x["high"][i, j] - x["low"][i, j])
        / (x["high"][i, j] - x["low"][i, j]),
        Q1=math.log(
            (x["volume"][i, j] + p["hourly_pseudocount"]) / (qmean + p["hourly_pseudocount"])
        ),
        Q2=math.log(
            (dv[-5:].mean() + p["daily_pseudocount"]) / (dv[-60:].mean() + p["daily_pseudocount"])
        ),
        T1=math.log(x["close"][i, j] / daily[-20:].mean()),
        T2=float(np.sign(np.diff(daily[-21:])).mean()),
        T3=(ema[6] - ema[18]) / x["close"][i, j],
        T4=(ema[24] - ema[72]) / x["close"][i, j],
        T5=(100 - 100 / (1 + gain / loss) - 50) / 50,
    )
    expected["V3"] = expected["V1"] - expected["V2"]
    for k, name in enumerate(COMMON):
        assert arrays["raw"][i, j, k] == pytest.approx(expected[name], abs=1e-11)
    normal = [c.days.index(day) for day in c.regular_days if day < "2023-06-15"]
    for o in range(2):
        sample = c.returns[normal, j, o]
        m2 = sample[-20:].mean() / max(np.sqrt(np.mean(sample[-60:] ** 2)), p["m2_floor"])
        assert arrays["raw_m2"][d, j, o] == pytest.approx(m2)
    unique = c.grid.session.between("2022-12-01", "2023-05-31").sum() * 20
    assert recipe["hourly_fit_keys"] == unique
    assert arrays["common"].dtype == np.float32


def test_target_full_cross_section_epsilon_and_extremes(components):
    c = components
    complete, med, mad = target_decomposition(c)
    d = c.days.index("2023-06-15")
    values = c.returns[d, :, 0]
    assert complete[d, 0]
    assert med[d, 0] == np.median(values)
    assert mad[d, 0] == np.median(np.abs(values - np.median(values)))
    before = c.returns[d, 0, 0]
    c.returns[d, 0, 0] = 2.0
    _, arrays = fit_recipe(c, "2023-05-31")
    assert arrays["targets"][d, 0, 0] > 100  # No clipping of genuine idiosyncratic extremes.
    c.returns[d, 0, 0] = np.nan
    assert not target_decomposition(c)[0][d, 0]
    c.returns[d, 0, 0] = before


def test_held_out_guard_precedes_component_construction(candles):
    with pytest.raises(ValueError, match="CONFIRMATION"):
        build_components(candles, start="2022-06-01", stop="2026-01-07")
    future = candles.iloc[[0]].copy()
    future["datetime"] = pd.DatetimeIndex([BARRIER])
    with pytest.raises(ValueError, match="CONFIRMATION"):
        build_components(future, start="2022-06-01", stop="2023-08-31")


def test_future_changes_cannot_reach_earlier_components(candles, components):
    f = candles.copy()
    future = f.datetime >= pd.Timestamp("2023-07-01", tz="America/New_York")
    for col in ("open", "high", "low", "close", "close_adj"):
        f.loc[future, col] *= 2
    changed = build_components(f, start="2022-06-01", stop="2023-08-31")
    before = components.grid.session < "2023-07-01"
    for key in components.values:
        assert np.array_equal(
            components.values[key][before], changed.values[key][before], equal_nan=True
        )
    days = np.asarray(components.days) < "2023-07-01"
    assert np.array_equal(components.m2_mean[days], changed.m2_mean[days], equal_nan=True)


def test_missing_exit_never_changes_forecast_issuance(candles):
    from lstm_data.hf20_transforms import admissions

    f = candles.loc[
        ~(
            candles.symbol.eq(SYMBOLS[0])
            & candles.datetime.eq(pd.Timestamp("2023-06-15 13:30", tz="America/New_York"))
        )
    ].copy()
    c = build_components(f, start="2022-06-01", stop="2023-08-31")
    _, arrays = fit_recipe(c, "2023-05-31")
    table = admissions(c, arrays, fitted_stop="2023-05-31")
    row = table.loc[table.session.eq("2023-06-15") & table.origin.eq(1)].iloc[0]
    assert row.feature_ready and row.forecast_issuable
    assert not row.label_ready and not row.supervised_ready
    d = c.days.index("2023-06-15")
    assert np.isnan(arrays["targets"][d, :, 0]).all()


def test_identity_and_missing_live_approval_deny_before_store_read(tmp_path: Path):
    import hashlib
    import json

    from lstm_data.hf20_loader import check_identity, require_approval

    with pytest.raises(ValueError, match="CONFIRMATION"):
        check_identity({}, mode="CANDIDATE_HOURLY_NATIVE", split="held_out", recipe="refit")
    with pytest.raises(ValueError, match="EXACT_READY"):
        check_identity({}, mode="CANDIDATE_HOURLY_NATIVE", split="refit", recipe="refit")
    receipt = tmp_path / "pending.json"
    receipt.write_text(json.dumps(dict(actor="user", methodology_answer="PENDING")))
    ref = dict(path=receipt.name, sha256=hashlib.sha256(receipt.read_bytes()).hexdigest())
    with pytest.raises(ValueError, match="ACTUAL_METHODOLOGY"):
        require_approval(tmp_path, ref)
    ref["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="BOUND_CONTENT_CHANGED"):
        require_approval(tmp_path, ref)


def test_early_close_has_no_four_hour_origin_but_keeps_genuine_hourly_steps(components):
    c = components
    d = c.days.index("2022-11-25")
    assert (c.origin_indices[d] == -1).all()
    assert c.grid.session.eq("2022-11-25").sum() == 3
    assert "2022-11-25" not in c.regular_days
    before = c.grid.loc[c.grid.session.eq("2022-11-04"), "start"].iloc[0]
    after = c.grid.loc[c.grid.session.eq("2022-11-07"), "start"].iloc[0]
    assert before.hour == 13 and after.hour == 14


def test_v2_uses_observed_last_close_without_manufacturing_daily_volume(candles):
    missing = candles.symbol.eq(SYMBOLS[0]) & candles.datetime.eq(
        pd.Timestamp("2023-06-15 09:30", tz="America/New_York")
    )
    frame = candles.loc[~missing].copy()
    original = build_components(frame, start="2022-06-01", stop="2023-08-31")
    revised = build_components(
        frame, start="2022-06-01", stop="2023-08-31", independent_daily_close=True
    )
    i = revised.regular_days.index("2023-06-15")
    assert np.isnan(original.daily_close[i, 0])
    assert np.isfinite(revised.daily_close[i, 0])
    assert np.isnan(original.daily_volume[i, 0]) and np.isnan(revised.daily_volume[i, 0])
    assert np.array_equal(original.source["close"], revised.source["close"], equal_nan=True)
    assert np.array_equal(original.returns, revised.returns, equal_nan=True)


def test_source_arrow_predicate_materializes_no_protected_numeric_rows(tmp_path: Path):
    from lstm_data.hf20_source import read_source

    frame = pd.DataFrame(
        dict(
            datetime=pd.DatetimeIndex(
                [pd.Timestamp("2026-01-06 09:30", tz="America/New_York"), BARRIER]
            ),
            symbol=[SYMBOLS[0]] * 2,
            timeframe=["1h"] * 2,
            open=[10.0, 999999.0],
            high=[12.0, 999999.0],
            low=[9.0, 999999.0],
            close=[11.0, 999999.0],
            close_adj=[11.0, 999999.0],
            volume=[100, 999999],
        )
    )
    path = tmp_path / "synthetic.parquet"
    frame.to_parquet(path, index=False)
    manifest = dict(files=[dict(path=str(path), sha256="SYNTHETIC_ONLY")])
    numeric = read_source(manifest)
    assert len(numeric) == 1 and numeric.close.iloc[0] == 11
    assert len(read_source(manifest, keys_only=True)) == 2


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_revision", "0" * 40),
        ("symbols", list(reversed(SYMBOLS))),
        ("clock_id", "LEGACY_FIVE_STOCK_CLOCK"),
        ("target_id", "TG0"),
        ("feature_id", "FT0"),
        ("preparation_id", ""),
    ],
)
def test_exact_contract_identity_mutations_fail_closed(field: str, value: object):
    from lstm_data.hf20_features import ORDER
    from lstm_data.hf20_loader import V2_PROPOSAL_SHA, check_identity
    from lstm_data.hf20_source import REVISION

    # Identity-only synthetic mapping grants no authority; no receipt/store is created.
    contract: dict[str, object] = dict(
        source_revision=REVISION,
        symbols=SYMBOLS,
        feature_order=ORDER,
        clock_id="HF20_COMPLETED_VENDOR_HOUR_CLOSE_PROXY_V1",
        feature_id="FT1_HF20_HOURLY_NATIVE_V2",
        target_id="TG20_HF20_CROSS_SECTIONAL_V1",
        proposal_sha256=V2_PROPOSAL_SHA,
        training_authorized=False,
        readiness="HF20_TRAIN_INPUT_READY_CONDITIONAL",
        preparation_id="SYNTHETIC_IDENTITY_ONLY",
        approval={"path": "NO_RECEIPT_EXISTS"},
        config={"sha256": V2_PROPOSAL_SHA},
    )
    check_identity(contract, mode="CANDIDATE_HOURLY_NATIVE", split="refit", recipe="refit")
    contract[field] = value
    with pytest.raises(ValueError):
        check_identity(contract, mode="CANDIDATE_HOURLY_NATIVE", split="refit", recipe="refit")


def test_warmup_has_only_historical_m2_returns_not_tg20_supervision(components):
    c = components
    recipe, arrays = fit_recipe(c, "2023-05-31")
    warmup = np.asarray(c.days) < "2022-12-01"
    complete, median, mad = target_decomposition(c)
    assert not complete[warmup].any()
    assert np.isnan(median[warmup]).all() and np.isnan(mad[warmup]).all()
    assert np.isnan(arrays["targets"][warmup]).all()
    assert np.isfinite(c.returns[warmup]).any()  # Own-stock matured antecedents, not TG20.
    assert recipe["epsilon_origins"] > 0
