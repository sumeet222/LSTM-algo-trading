"""Independent scalar real examples and cutoff perturbations for P020 FT16."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_source import publish_json, publish_table
from .hf1m_ft16_fit import native
from .hf1m_ft16_math import build
from .hf1m_ft16_source import COMMON, ORDER, SYMBOLS, checked, configuration, read_hourly


def average(values: list[float], n: int, minimum: int, square: bool = False) -> float:
    if len(values) < n:
        return math.nan
    sample = values[-n:]
    finite = [x for x in sample if math.isfinite(x)]
    gap = 0
    for x in sample:
        gap = 0 if math.isfinite(x) else gap + 1
        if gap > 2:
            return math.nan
    if len(finite) < minimum:
        return math.nan
    value = math.fsum(x * x if square else x for x in finite) / len(finite)
    return math.sqrt(value) if square else value


def manual(frame: pd.DataFrame, stock: str, step: int, o: int, floors: dict) -> tuple[dict, dict]:
    """Scalar formulas from indexed source candles, not saved component values."""
    f = frame.loc[frame.ticker.eq(stock)].sort_values("step").reset_index(drop=True)
    part = f.iloc[: step + 1]
    current = part.iloc[-1]
    close = part.close_input_cap5.to_numpy(float)
    oc = np.log(close / part.open.to_numpy(float))
    h12 = average(oc.tolist(), 12, 12, True)
    h60 = average(oc.tolist(), 60, 57, True)
    groups = f.groupby("session_date_et", sort=True)
    regular = [
        (str(day), p)
        for day, p in groups
        if len(p) == 6 and str(day) < str(current.session_date_et)
    ]
    daily = []
    volumes = []
    returns = []
    regimes = []
    for _, p in regular:
        p = p.sort_values("step")
        daily.append(float(p.close.iloc[-1]))
        regimes.append(str(p.volume_basis_id.iloc[-1]))
        volumes.append(
            float(p.volume_for_feature.sum())
            if p.volume_usable_for_feature.all() and p.volume_basis_id.nunique() == 1
            else math.nan
        )
        returns.append(float(np.log(p.close.iloc[o + 4] / p.close.iloc[o])))
    dr = [math.nan] + [
        math.log(b / a) if math.isfinite(a) and math.isfinite(b) else math.nan
        for a, b in zip(daily[:-1], daily[1:])
    ]
    rms = average(dr, 63, 60, True)
    mean = average(returns, 20, 19)
    rm2 = average(returns, 60, 57, True)
    width = float(current.high - current.low)
    C = float(current.close_input_cap5)
    b2 = (2 * C - float(current.high) - float(current.low)) / width if width != 0 else 0.0
    if not math.isfinite(width) or abs(b2) > 1 + 1e-10:
        b2 = math.nan
    slot = pd.Timestamp(current.hour_end_utc).tz_convert("America/New_York").hour - 10
    matching = part.loc[
        (part.hour_end_utc.dt.tz_convert("America/New_York").dt.hour - 10).eq(slot)
    ].iloc[:-1]
    qmean = average(matching.volume_for_feature.tolist(), 20, 19)
    regime = str(current.volume_basis_id)
    if len(matching) < 20 or matching.volume_basis_id.iloc[-20:].ne(regime).any():
        qmean = math.nan
    q5 = average(volumes, 5, 5)
    q60 = average(volumes, 60, 57)
    if len(regimes) < 60 or any(r != regime for r in regimes[-60:]):
        q60 = math.nan
    if len(regimes) < 5 or any(r != regime for r in regimes[-5:]):
        q5 = math.nan
    p = floors["volume_pseudocounts"].get(regime)
    qh = p["hour"] if p else math.nan
    qd = p["day"] if p else math.nan
    # Independent scalar EMA/Wilder replay, including recovery without a fictitious delta.
    emas = {}
    updates = 0
    previous = None
    changes = []
    gain = loss = None
    wilder = 0
    gap = 0
    prior_basis = None
    for value, basis in zip(close, part.price_basis_id):
        valid = math.isfinite(value)
        gap = 0 if valid else gap + 1
        if basis != prior_basis or gap >= 3:
            emas = {}
            updates = 0
            previous = None
            changes = []
            gain = loss = None
            wilder = 0
        prior_basis = basis
        if not valid:
            previous = None
            if gain is None:
                changes = []
            continue
        if not emas:
            emas = {n: float(value) for n in [6, 18, 24, 72]}
        else:
            for n in emas:
                emas[n] = 2 / (n + 1) * value + (1 - 2 / (n + 1)) * emas[n]
            updates += 1
        if previous is not None:
            change = value - previous
            if gain is None:
                changes.append(change)
                if len(changes) == 14:
                    gain = sum(max(x, 0) for x in changes) / 14
                    loss = sum(max(-x, 0) for x in changes) / 14
            else:
                if loss is None:
                    raise ValueError("WILDER_ORACLE_PAIR")
                gain = (13 * gain + max(change, 0)) / 14
                loss = (13 * loss + max(-change, 0)) / 14
                wilder += 1
        previous = float(value)
    recent = math.isfinite(average(close.tolist(), 72, 69))
    rsi = math.nan
    if recent and math.isfinite(C) and gain is not None and loss is not None and wilder >= 140:
        rsi = (
            0.0
            if gain == loss == 0
            else 1.0
            if loss == 0
            else -1.0
            if gain == 0
            else (100 - 100 / (1 + gain / loss) - 50) / 50
        )
    h = floors["hourly_floor"]
    d = floors["daily_floor"]
    last = daily[-1]
    sma = average(daily, 20, 19)
    v1 = math.log(max(h12, h)) if math.isfinite(h12) else math.nan
    v2 = math.log(max(h60, h)) if math.isfinite(h60) else math.nan
    result = {
        "M1": float(oc[-1]) / max(h60, h),
        "M2": mean / max(rm2, floors["m2_floor"]),
        "M3": math.log(last / daily[-6]) / (math.sqrt(5) * max(rms, d)),
        "M4": math.log(daily[-21] / daily[-126]) / (math.sqrt(105) * max(rms, d)),
        "V1": v1,
        "V2": v2,
        "V3": v1 - v2,
        "B1": float(np.log(current.high / current.low)),
        "B2": b2,
        "Q1": float(np.log((current.volume_for_feature + qh) / (qmean + qh))),
        "Q2": float(np.log((q5 + qd) / (q60 + qd))),
        "T1": math.log(C / sma),
        "T2": average(np.sign(dr).tolist(), 20, 19),
        "T3": (emas[6] - emas[18]) / C if recent and updates >= 360 else math.nan,
        "T4": (emas[24] - emas[72]) / C if recent and updates >= 360 else math.nan,
        "T5": rsi,
    }
    operands = {
        "OC": float(oc[-1]),
        "RMS12": h12,
        "RMS60": h60,
        "RMS63": rms,
        "M2_mean20": mean,
        "M2_RMS60": rm2,
        "daily_close_lag1": last,
        "daily_close_lag6": daily[-6],
        "daily_close_lag21": daily[-21],
        "daily_close_lag126": daily[-126],
        "Q1_previous20_mean": qmean,
        "Q2_mean5": q5,
        "Q2_mean60": q60,
        "SMA20": sma,
        "EMA6": emas[6],
        "EMA18": emas[18],
        "EMA24": emas[24],
        "EMA72": emas[72],
        "RSI_average_gain": gain,
        "RSI_average_loss": loss,
        "Wilder_updates": wilder,
    }
    return result, operands


def run(out: Path) -> None:
    config = configuration()
    d = json.loads((out / "model_input_contract.json").read_text())
    recipe = json.loads(checked(d["fit_recipes"]).read_text())["refit"]
    candles = pd.read_parquet(checked(d["files"]["candles_quality"]))
    grid = pd.read_parquet(checked(d["files"]["grid"]))
    with np.load(checked(d["files"]["components"]), allow_pickle=False) as a:
        common = a["refit_native_common"]
        m2 = a["refit_native_m2"]
    checks = []
    examples = []
    # Choose source-valid native cells, not targets or model outcomes.
    for stock, date in [("AAPL", "2024-06-18"), ("KO", "2021-11-15"), ("MRK", "2015-11-02")]:
        j = SYMBOLS.index(stock)
        floor = recipe["floors"][j]
        candidates = grid.index[grid.session_date_et.eq(date)].tolist()
        i = int(candidates[0])
        expected, operands = manual(candles, stock, i, 0, floor)
        for feature in ORDER:
            actual = (
                float(m2[i, j, 0])
                if feature == "M2"
                else float(common[i, j, COMMON.index(feature)])
            )
            value = float(expected[feature])
            if not np.isclose(actual, value, rtol=1e-10, atol=1e-11, equal_nan=True):
                raise ValueError(
                    f"INDEPENDENT_REAL_ORACLE_FAILED:{stock}:{date}:{feature}:{actual}:{value}"
                )
            checks.append(
                {
                    "ticker": stock,
                    "date": date,
                    "feature": feature,
                    "step": i,
                    "cutoff": str(grid.hour_end_utc.iloc[i]),
                    "actual_native": actual if np.isfinite(actual) else None,
                    "independent_native": value if np.isfinite(value) else None,
                    "native_available": bool(np.isfinite(actual)),
                    "pass": True,
                }
            )
        examples.append(
            {"ticker": stock, "date": date, "cutoff": str(grid.hour_end_utc.iloc[i]), **operands}
        )
    if {r["feature"] for r in checks if r["native_available"]} != set(ORDER):
        raise ValueError("ALL16_REAL_ORACLES_REQUIRED")
    private = Path(d["files"]["components"]["path"]).parent
    example_ref = publish_table(
        private / "P020_independent_real_oracle_operands.parquet", pd.DataFrame(examples)
    )
    hours = read_hourly(config)
    up = Path(config["upstream_packet"])
    fieldref = json.loads((up / "hour_field_mask_manifest.json").read_text())["file"]
    fields = pd.read_parquet(checked(fieldref))
    prefix_checks = []
    for date, slot in [("2011-04-04", 0), ("2012-05-01", 0), ("2020-03-09", 1), ("2024-06-18", 0)]:
        i = int(grid.index[grid.session_date_et.eq(date)][slot])
        cutoff = grid.hour_end_utc.iloc[i]
        past = hours.loc[hours.hour_end_utc.le(cutoff)].copy()
        c = build(past, fields)
        raw, raw_m2 = native(c, recipe["floors"])
        np.testing.assert_allclose(
            raw[-48:], common[i - 47 : i + 1], rtol=1e-11, atol=1e-11, equal_nan=True
        )
        np.testing.assert_allclose(
            raw_m2[-48:], m2[i - 47 : i + 1], rtol=1e-11, atol=1e-11, equal_nan=True
        )
        if c.m2_reference_end[-1] >= len(c.grid) - 1:
            raise ValueError("M2_NOT_PREVIOUS_MATURE_SESSION")
        prefix_checks.append(
            {
                "date": date,
                "cutoff": str(cutoff),
                "48x20x16_both_M2_contexts_equal": True,
                "past_feature_max_source_end": str(c.grid.hour_end_utc.iloc[-1]),
                "m2_last_reference_end": str(c.grid.hour_end_utc.iloc[c.m2_reference_end[-1]]),
                "protected_numeric_read": False,
            }
        )
    # Future multiplicative split units cancel in every pre-origin channel, with fixed fit recipe.
    i = int(grid.index[grid.session_date_et.eq("2024-06-18")][0])
    cutoff = grid.hour_end_utc.iloc[i]
    prefix = hours.loc[hours.hour_end_utc.le(cutoff)].copy()
    for name in ["open", "high", "low", "close", "close_input_cap5"]:
        prefix[name] *= 7.0
    c = build(prefix, fields)
    r, mm = native(c, recipe["floors"])
    np.testing.assert_allclose(
        r[-48:], common[i - 47 : i + 1], rtol=2e-9, atol=2e-9, equal_nan=True
    )
    np.testing.assert_allclose(mm[-48:], m2[i - 47 : i + 1], rtol=2e-9, atol=2e-9, equal_nan=True)
    # Change all permitted post-origin prices and separate closing stubs; no pre-origin effect.
    mutant = hours.copy()
    future = mutant.hour_end_utc.gt(cutoff)
    for name in ["open", "high", "low", "close", "close_input_cap5"]:
        mutant.loc[future, name] *= 11.0
    c = build(mutant, fields)
    r, mm = native(c, recipe["floors"])
    np.testing.assert_allclose(
        r[i - 47 : i + 1], common[i - 47 : i + 1], rtol=1e-11, atol=1e-11, equal_nan=True
    )
    np.testing.assert_allclose(
        mm[i - 47 : i + 1], m2[i - 47 : i + 1], rtol=1e-11, atol=1e-11, equal_nan=True
    )
    protected = hours.iloc[[0]].copy()
    protected["session_date_et"] = "2026-01-01"
    try:
        build(protected, fields)
    except ValueError as exc:
        if "PROTECTED" not in str(exc):
            raise
    else:
        raise ValueError("PROTECTED_SYNTHETIC_PERTURBATION_NOT_REJECTED")
    publish_json(
        out / "independent_oracle_and_causality.json",
        {
            "real_feature_checks": checks,
            "private_hand_calculated_operands": example_ref,
            "causal_prefix_tests": prefix_checks,
            "post_origin_bars_and_stub_perturbation_pass": True,
            "future_split_unit_multiplier7_invariant": True,
            "protected_synthetic_input_rejected_before_computation": True,
            "feature_builder_has_no_target_argument": True,
            "fixed_fit_recipe_scope": (
                "retrospective training transforms held fixed for causal component tests; "
                "no claim fitted historical constants existed before actual fitting"
            ),
            "tolerance": "1e-11prefix and2e-9split-unit ratios; scalar math vs vector arithmetic",
            "result": "PASS",
            "model_fits": 0,
        },
    )
    print("ALL16_INDEPENDENT_REAL_AND_CAUSAL_ORACLES_PASS")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, type=Path)
    run(p.parse_args().out)


if __name__ == "__main__":
    main()
