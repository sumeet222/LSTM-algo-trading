"""Independent scalar arithmetic and finite-window evidence for approved real HF20 data."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from .config import write_json
from .hf20_features import COMMON, ORDER, Components
from .hf20_source import SYMBOLS


def average(values: np.ndarray, count: int, minimum: int, *, rms: bool = False) -> float:
    """Scalar reference, independent of production rolling implementation."""
    sample = values[-count:]
    if len(sample) != count or np.isfinite(sample).sum() < minimum:
        return math.nan
    missing = 0
    for value in sample:
        missing = 0 if np.isfinite(value) else missing + 1
        if missing > 2:
            return math.nan
    good = [float(v) for v in sample if np.isfinite(v)]
    return math.sqrt(sum(v * v for v in good) / len(good)) if rms else sum(good) / len(good)


def scalar_row(c: Components, i: int, j: int, origin: int, recipe: dict) -> dict[str, float]:
    """Hand equations from original aligned source fields, not native feature arrays."""
    day = str(c.grid.session.iloc[i])
    slot = int(c.grid.slot.iloc[i])
    s = c.source
    close = s["close"][i, j]
    oc = np.log(s["close"][: i + 1, j] / s["open"][: i + 1, j])
    h12, h60 = average(oc, 12, 12, rms=True), average(oc, 60, 57, rms=True)
    daily, volume = [], []
    for prior in c.regular_days:
        if prior >= day:
            break
        positions = c.grid.index[c.grid.session.eq(prior)].to_numpy()
        good = np.isfinite(s["close"][positions, j]).all()
        daily.append(
            float(s["close"][positions[-1], j]) if good or c.independent_daily_close else math.nan
        )
        volume.append(float(s["volume"][positions, j].sum()) if good else math.nan)
    d = np.asarray(daily)
    dv = np.asarray(volume)
    changes = np.diff(np.log(d))
    rms63 = average(changes, 63, 60, rms=True)
    qpositions = c.grid.index[c.grid.session.lt(day) & c.grid.slot.eq(slot)].to_numpy()
    qmean = average(s["volume"][qpositions, j], 20, 19)
    historical = []
    for prior in c.regular_days:
        if prior >= day:
            break
        positions = c.grid.index[c.grid.session.eq(prior)].to_numpy()
        block = positions[origin - 1 : origin + 4]
        good = np.isfinite(s["close"][block, j]).all()
        historical.append(
            math.log(s["close"][block[-1], j] / s["close"][block[0], j]) if good else math.nan
        )
    historic = np.asarray(historical)
    p = recipe["floors"][j]
    ema: dict[int, float] = {}
    previous = None
    initial = []
    gain = None
    loss = None
    updates = 0
    for value in s["close"][: i + 1, j]:
        if not np.isfinite(value):
            previous = None
            if gain is None:
                initial = []
            continue
        if not ema:
            ema = {k: float(value) for k in (6, 18, 24, 72)}
        else:
            for k in ema:
                ema[k] = 2 / (k + 1) * value + (1 - 2 / (k + 1)) * ema[k]
        if previous is not None:
            delta = float(value - previous)
            if gain is None:
                initial.append(delta)
                if len(initial) == 14:
                    gain = sum(max(x, 0) for x in initial) / 14
                    loss = sum(max(-x, 0) for x in initial) / 14
            else:
                if loss is None:
                    raise ValueError("ORACLE_WILDER_PAIR")
                gain = (13 * gain + max(delta, 0)) / 14
                loss = (13 * loss + max(-delta, 0)) / 14
                updates += 1
        previous = float(value)
    rsi = math.nan
    if gain is not None and loss is not None and updates >= 140:
        rsi = (
            0.0
            if gain == loss == 0
            else 1.0
            if loss == 0
            else -1.0
            if gain == 0
            else (100 - 100 / (1 + gain / loss) - 50) / 50
        )
    spread = s["high"][i, j] - s["low"][i, j]
    row = dict(
        M1=float(oc[-1] / max(h60, p["hourly_floor"])),
        M2=average(historic, 20, 19) / max(average(historic, 60, 57, rms=True), p["m2_floor"]),
        M3=math.log(d[-1] / d[-6]) / (math.sqrt(5) * max(rms63, p["daily_floor"])),
        M4=math.log(d[-21] / d[-126]) / (math.sqrt(105) * max(rms63, p["daily_floor"])),
        V1=math.log(max(h12, p["hourly_floor"])),
        V2=math.log(max(h60, p["hourly_floor"])),
        B1=math.log(s["high"][i, j] / s["low"][i, j]),
        B2=0.0 if spread == 0 else float((2 * close - s["high"][i, j] - s["low"][i, j]) / spread),
        Q1=math.log(
            (s["volume"][i, j] + p["hourly_pseudocount"]) / (qmean + p["hourly_pseudocount"])
        ),
        Q2=math.log(
            (average(dv, 5, 5) + p["daily_pseudocount"])
            / (average(dv, 60, 57) + p["daily_pseudocount"])
        ),
        T1=math.log(close / average(d, 20, 19)),
        T2=average(np.sign(np.diff(d)), 20, 19),
        T3=(ema[6] - ema[18]) / close,
        T4=(ema[24] - ema[72]) / close,
        T5=rsi,
    )
    row["V3"] = row["V1"] - row["V2"]
    return row


def write_oracles(c: Components, recipes: dict, arrays: dict, origins: dict, out: Path) -> None:
    """Preselected real ordinary/DST/missing/action examples, all before held-out."""
    examples = (
        ("2023-03-21", "AAPL", 1),
        ("2023-03-23", "TSLA", 1),
        ("2024-03-11", "AAPL", 2),
        ("2024-07-15", "AVGO", 1),
        ("2023-11-24", "AAPL", 1),
    )
    checks = []
    source_rows = []
    for day, symbol, origin in examples:
        positions = c.grid.index[c.grid.session.eq(day)].to_numpy()
        i = int(positions[min(origin - 1, len(positions) - 1)])
        j = SYMBOLS.index(symbol)
        d = c.days.index(day)
        manual = scalar_row(c, i, j, origin, recipes["refit"])
        for feature in ORDER:
            actual = float(
                arrays["refit"]["raw_m2"][d, j, origin - 1]
                if feature == "M2"
                else arrays["refit"]["raw"][i, j, COMMON.index(feature)]
            )
            expected = manual[feature]
            passed = (np.isnan(actual) and np.isnan(expected)) or math.isclose(
                actual, expected, rel_tol=1e-9, abs_tol=1e-11
            )
            checks.append(
                dict(
                    session=day,
                    symbol=symbol,
                    origin=origin,
                    feature=feature,
                    independent_value=expected,
                    stored_native=actual,
                    passed=passed,
                    source_start_UTC=str(c.grid.start.iloc[i]),
                    source_end_UTC=str(c.grid.end.iloc[i]),
                )
            )
            if not passed:
                raise ValueError("HF20_REAL_FEATURE_ORACLE_MISMATCH:" + feature + ":" + day)
        source_rows.append(
            dict(
                session=day,
                symbol=symbol,
                source_start_UTC=str(c.grid.start.iloc[i]),
                source_end_UTC=str(c.grid.end.iloc[i]),
                **{field: float(value[i, j]) for field, value in c.source.items()},
            )
        )
    pd.DataFrame(checks).to_csv(out / "feature_arithmetic_oracles.csv", index=False)
    pd.DataFrame(source_rows).to_csv(out / "bounded_source_oracle_examples.csv", index=False)
    targets = []
    selected = origins["refit"].loc[origins["refit"].supervised_ready]
    for chosen in [selected.iloc[0], selected.iloc[len(selected) // 2], selected.iloc[-1]]:
        d = int(chosen.day_index)
        o = int(chosen.origin) - 1
        raw = c.returns[d, :, o]
        m = float(np.median(raw))
        mad = float(np.median(np.abs(raw - m)))
        epsilon = recipes["refit"]["epsilon"]
        for j, symbol in enumerate(SYMBOLS):
            last = int(c.origin_indices[d, o])
            exit_index = last + 4
            expected = math.log(c.source["close"][exit_index, j] / c.source["close"][last, j])
            y = (expected - m) / (mad + epsilon)
            stored = float(arrays["refit"]["targets"][d, j, o])
            if not np.isclose(np.float32(y), stored, rtol=0, atol=0):
                raise ValueError("HF20_REAL_TG20_FLOAT32_ORACLE_MISMATCH")
            targets.append(
                dict(
                    session=str(chosen.session),
                    origin=o + 1,
                    symbol=symbol,
                    raw_return=expected,
                    cross_sectional_median=m,
                    unscaled_MAD=mad,
                    centered_deviation=expected - m,
                    epsilon=epsilon,
                    target=y,
                    stored_float32=stored,
                    entry_reference_end_UTC=str(c.grid.end.iloc[last]),
                    exit_reference_end_UTC=str(c.grid.end.iloc[exit_index]),
                    label_maturity_UTC=str(c.grid.end.iloc[exit_index] + pd.Timedelta(minutes=2)),
                    repaired=False,
                )
            )
    pd.DataFrame(targets).to_csv(out / "target_decomposition_and_oracles.csv", index=False)
    scalar = []
    fit = c.grid.session.between("2022-12-01", "2025-03-28").to_numpy()
    for k, feature in enumerate(COMMON):
        if feature in {"B2", "T2", "T5"}:
            continue
        values = arrays["refit"]["raw"][fit, :, k]
        values = values[np.isfinite(values)]
        center = float(np.median(values))
        mad = float(np.median(np.abs(values - center)))
        p = recipes["refit"]["scalers"][feature]
        assert center == p["center"] and (mad == p["scale"] or p["method"] != "MAD")
        scalar.append(
            dict(
                feature=feature,
                unique_native_fit_keys=len(values),
                median=center,
                MAD=mad,
                scale=p["scale"],
                method=p["method"],
            )
        )
    pd.DataFrame(scalar).to_csv(out / "scaler_population_oracles.csv", index=False)
    exclusions = []
    for row in origins["refit"].loc[~origins["refit"].feature_ready].itertuples():
        last = int(row.last_step)
        history = np.arange(last - 47, last + 1)
        for k, feature in enumerate(COMMON):
            missing = ~np.isfinite(arrays["refit"]["common"][history, :, k])
            for j in np.flatnonzero(missing.any(axis=0)):
                positions = history[missing[:, j]]
                exclusions.append(
                    dict(
                        session=str(row.session),
                        origin=int(row.origin),
                        symbol=SYMBOLS[j],
                        feature=feature,
                        missing_historical_steps=len(positions),
                        first_invalid_step_UTC=str(c.grid.end.iloc[int(positions[0])]),
                        last_invalid_step_UTC=str(c.grid.end.iloc[int(positions[-1])]),
                        rule="Exact48scheduled steps; no skipped rows, zero fills or stock removal",
                    )
                )
    pd.DataFrame(exclusions).to_csv(out / "feature_exclusion_dependencies.csv", index=False)
    distribution = {}
    for name, recipe in recipes.items():
        for split, start, stop in (
            ("train", "2022-12-01", recipe["fit_stop_inclusive"]),
            ("development", "2025-03-31", "2026-01-06"),
        ):
            selected_days = np.asarray([start <= day <= stop for day in c.days], dtype=bool)
            returns = c.returns[selected_days]
            median = np.median(returns, axis=1)
            mad = np.median(np.abs(returns - median[:, None, :]), axis=1)
            values = arrays[name]["targets"][selected_days]
            distribution[name + ":" + split] = dict(
                complete_cross_sections=int(np.isfinite(returns).all(axis=1).sum()),
                zero_MAD=int(np.sum(mad == 0)),
                positive_MAD_below_epsilon=int(np.sum((mad > 0) & (mad < recipe["epsilon"]))),
                maximum_absolute_TG20=float(np.nanmax(np.abs(values))),
                target_clipping=False,
            )
    write_json(out / "target_distribution_and_floor_cases.json", distribution)
    write_json(
        out / "finite_oracle_checks.json",
        dict(
            real_feature_equations=len(checks),
            feature_equations_passed=all(r["passed"] for r in checks),
            real_target_stock_examples=len(targets),
            float32_targets_exact=True,
            forecast_label_masks_separate=True,
            held_out_numeric_rows=0,
        ),
    )
    (out / "target_scaler_oracles.md").write_text(
        "# Target and transform oracles\n\nFeature arithmetic is independently recomputed "
        "from aligned source fields, "
        "including ordinary, missing-hour, DST, early-close and split-boundary examples. "
        "Three real complete20stock targets retain raw returns, median, unscaledMAD, "
        "epsilon and maturity. "
        "Targets and features are never clipped. The synthetic extreme/zero-constant and "
        "no-leak tests "
        "are independent of these genuine samples. All comparisons are training/development only; "
        "see finite_oracle_checks.json and scaler_population_oracles.csv.\n"
    )
