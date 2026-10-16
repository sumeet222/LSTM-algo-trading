"""Independent bounded-example FT0 replay from genuine sources; no scaler fitting."""

from __future__ import annotations

import math
from collections.abc import Sequence
from datetime import timedelta

import numpy as np
import pandas as pd

from .ft0_transforms import ORDER, SCALED
from .pretraining_policy import CANDIDATE
from .pretraining_source import BARRIER, FIRST
from .pretraining_store import read_preparation
from .pretraining_tables import BaseTables
from .pretraining_transforms import (
    CandidateFloors,
    CandidateView,
    canonical_population,
    raw_features,
)
from .visualization.loaders import ET, Catalog, ViewUnavailable, predictions, source_bars


def source_replay(catalog: Catalog, base: BaseTables, symbol: str, stop: str) -> dict:
    """One temporary genuine source stream per stock, through last requested example only."""
    if pd.Timestamp(stop, tz=ET).tz_convert("UTC") >= BARRIER:
        raise ViewUnavailable("Confirmation source oracle forbidden before I/O.")
    frames = []
    start = pd.Timestamp(FIRST).date()
    end = pd.Timestamp(stop).date()
    while start <= end:
        last = min(start + timedelta(days=90), end)
        frame, _ = source_bars(catalog, symbol, start.isoformat(), last.isoformat())
        frames.append(frame)
        start = last + timedelta(days=1)
    native = pd.concat(frames, ignore_index=True)
    if native.duplicated("timestamp").any() or native.timestamp.ge(BARRIER).any():
        raise ViewUnavailable("Oracle source identity/boundary failed.")
    by_time = {r.timestamp: r for r in native.itertuples()}
    days = native.groupby("session").agg(close=("close", "last"), volume=("volume", "sum"))
    hours, values = {}, {}
    ema: dict[int, float] = {}
    updates = wilder = 0
    previous: float | None = None
    gain: float | None = None
    loss: float | None = None
    initial: list[float] = []
    returns: list[float | None] = []
    for pos, step in enumerate(base.history.calendar.steps):
        if step.session > stop:
            break
        pair = [by_time.get(step.start), by_time.get(step.start + pd.Timedelta(minutes=30))]
        if any(v is None for v in pair):
            returns.append(None)
            previous = None
            continue
        a, b = pair
        if a is None or b is None:
            raise ValueError("Oracle pair invariant")
        opening, closing = float(a.open), float(b.close)
        high, low = max(a.high, b.high), min(a.low, b.low)
        volume = float(a.volume + b.volume)
        oc = math.log(closing / opening)
        returns.append(oc)
        hours[step.session, step.slot] = dict(
            close=closing, open=opening, high=high, low=low, volume=volume, end=step.end
        )
        if not ema:
            ema = {n: closing for n in (6, 18, 24, 72)}
        else:
            ema = {n: 2 / (n + 1) * closing + (1 - 2 / (n + 1)) * v for n, v in ema.items()}
            updates += 1
        if previous is not None:
            change = closing - previous
            if gain is None:
                initial.append(change)
                if len(initial) == 14:
                    gain = math.fsum(max(v, 0) for v in initial) / 14
                    loss = math.fsum(max(-v, 0) for v in initial) / 14
            else:
                assert loss is not None
                gain, loss = (13 * gain + max(change, 0)) / 14, (13 * loss + max(-change, 0)) / 14
                wilder += 1
        previous = closing
        rsi = None
        if gain is not None and loss is not None and wilder >= 140:
            rsi = (
                0.0
                if gain == loss == 0
                else 1.0
                if loss == 0
                else -1.0
                if gain == 0
                else (100 - 100 / (1 + gain / loss) - 50) / 50
            )
        values[pos] = dict(
            OC=oc,
            RMS12=rms(returns[-12:], 12, 12),
            RMS60=rms(returns[-60:], 60, 57),
            B1=math.log(high / low),
            B2=(2 * closing - high - low) / (high - low) if high > low else 0.0,
            T3=(ema[6] - ema[18]) / closing if updates >= 360 else None,
            T4=(ema[24] - ema[72]) / closing if updates >= 360 else None,
            T5=rsi,
        )
    return dict(
        hours=hours,
        days=days,
        values=values,
        rows=len(native),
        oracle="Independent OHLC aggregation / EMA / Wilder recursion",
    )


def rms(values: Sequence[float | None], count: int, minimum: int) -> float | None:
    if len(values) != count:
        return None
    present = [v for v in values if v is not None]
    if len(present) < minimum:
        return None
    run = 0
    for v in values:
        run = run + 1 if v is None else 0
        if run > 2:
            return None
    return math.sqrt(math.fsum(v * v for v in present) / len(present))


def native_oracle(
    replay: dict, base: BaseTables, symbol: str, pos: int, origin: int, floors: CandidateFloors
) -> dict[str, float | None]:
    """Recover all sixteen equations from the independent stream and scheduled past only."""
    step = base.history.calendar.steps[pos]
    v = replay["values"][pos]
    current = replay["hours"][step.session, step.slot]
    days = base.history.calendar.days
    index = days.index(step.session)
    prior = list(days[max(0, index - 126) : index])
    prices = [float(replay["days"].at[day, "close"]) for day in prior]
    volumes = [float(replay["days"].at[day, "volume"]) for day in prior]
    daily_returns = [math.log(b / a) for a, b in zip(prices[-64:], prices[-64:][1:])]
    daily_rms = rms(daily_returns, 63, 60)
    matched = base.history.calendar.matching[step.session, step.slot]
    hourly_volumes = [replay["hours"][day, step.slot]["volume"] for day in matched]
    m2returns = []
    for day in base.history.calendar.previous_origins(step, origin)[-60:]:
        entry = replay["hours"].get((day, origin))
        exit_bar = replay["hours"].get((day, origin + 4))
        if (
            entry is None
            or exit_bar is None
            or exit_bar["end"] + pd.Timedelta(minutes=3) > step.end
        ):
            m2returns.append(None)
        else:
            m2returns.append(math.log(exit_bar["close"] / entry["close"]))
    m2rms = rms(m2returns, 60, 57)
    good20 = [v for v in m2returns[-20:] if v is not None]
    h12, h60 = v["RMS12"], v["RMS60"]
    log12 = math.log(max(h12, floors.hourly_floor)) if h12 is not None else None
    log60 = math.log(max(h60, floors.hourly_floor)) if h60 is not None else None
    out = dict(
        M1=v["OC"] / max(h60, floors.hourly_floor) if h60 is not None else None,
        M2=math.fsum(good20) / len(good20) / max(m2rms, floors.m2_floor)
        if m2rms is not None and len(good20) >= 19
        else None,
        M3=math.log(prices[-1] / prices[-6]) / (math.sqrt(5) * max(daily_rms, floors.daily_floor))
        if len(prices) >= 6 and daily_rms is not None
        else None,
        M4=math.log(prices[-21] / prices[-126])
        / (math.sqrt(105) * max(daily_rms, floors.daily_floor))
        if len(prices) >= 126 and daily_rms is not None
        else None,
        V1=log12,
        V2=log60,
        V3=log12 - log60 if log12 is not None and log60 is not None else None,
        B1=v["B1"],
        B2=v["B2"],
        Q1=math.log(
            (current["volume"] + floors.hourly_pseudocount)
            / (np.mean(hourly_volumes) + floors.hourly_pseudocount)
        )
        if len(hourly_volumes) >= 19
        else None,
        Q2=math.log(
            (np.mean(volumes[-5:]) + floors.daily_pseudocount)
            / (np.mean(volumes[-60:]) + floors.daily_pseudocount)
        )
        if len(volumes) >= 60
        else None,
        T1=math.log(current["close"] / np.mean(prices[-20:])) if len(prices) >= 20 else None,
        T2=float(np.mean(np.sign(np.diff(prices[-21:])))) if len(prices) >= 21 else None,
        T3=v["T3"],
        T4=v["T4"],
        T5=v["T5"],
    )
    return out


def replay_oracles(catalog: Catalog, base: BaseTables, examples: list[dict]) -> list[dict]:
    fixed = (
        "2020-08-28",
        "2020-08-31",
        "2020-12-09",
        "2021-03-12",
        "2021-03-15",
        "2023-11-24",
        "2024-06-28",
    )
    output = []
    consumers: dict[tuple[str, str], dict[tuple[int, int], tuple[str, tuple[int, ...]]]] = {}
    for fold in ("WF1", "WF2"):
        for prefix in ("inner", "refit"):
            prep = read_preparation(catalog.root, catalog.config["recipes"][fold][prefix])
            keys, _ = canonical_population(base, prep.window)
            partition = "Inner validation" if prefix == "inner" else "Development"
            saved = predictions(catalog, fold, "TM0", partition)
            members = [(d, o, "training") for d, o in keys] + [
                (d, o, partition) for d, o in sorted(set(zip(saved.session, saved.origin)))
            ]
            mapping = consumers[fold, prefix] = {}
            for day, origin, kind in members:
                positions = base.origin_steps[day, origin]
                for pos in positions:
                    mapping.setdefault((pos, origin), (kind, positions))
    for symbol in CANDIDATE:
        replay = source_replay(catalog, base, symbol, fixed[-1])
        samples = [(day, 1, 1, "fixed split/DST/early-close/archive sample") for day in fixed]
        # Five family examples selected by feature magnitude alone, never by target correlation.
        for family in (
            ("M1", "M2", "M3", "M4"),
            ("V1", "V2", "V3"),
            ("B1", "B2"),
            ("Q1", "Q2"),
            ("T1", "T2", "T3", "T4", "T5"),
        ):
            candidates = [v for v in examples if v["symbol"] == symbol and v["feature"] in family]
            r = max(candidates, key=lambda v: abs(v["scaled"]))
            samples.append((r["session"], r["slot"], r["origin"], "family scaled outlier"))
        for day, slot, origin, kind in samples:
            pos = base.history.calendar._positions[day, slot]
            for fold, prefix in (
                ("WF1", "inner"),
                ("WF1", "refit"),
                ("WF2", "inner"),
                ("WF2", "refit"),
            ):
                prep = read_preparation(catalog.root, catalog.config["recipes"][fold][prefix])
                consumer = consumers[fold, prefix].get((pos, origin))
                if consumer is None:
                    continue
                floors = prep.floors[CANDIDATE.index(symbol)]
                independent = native_oracle(replay, base, symbol, pos, origin, floors)
                native, _ = raw_features(base, symbol, pos, origin, floors)
                view = CandidateView(base, prep)
                actual_partition, positions = consumer
                # Only a bounded 48-step trace, converted exactly as real_bridge_data.build_view.
                actual = np.asarray(
                    [view.row(symbol, p, origin) for p in positions], dtype=np.float32
                )
                selected_index = positions.index(pos)
                for j, feature in enumerate(ORDER):
                    a, b = independent[feature], native[j]
                    index = SCALED.index(feature) if feature in SCALED else None
                    if a is None or b is None:
                        passed = a is None and b is None
                        expected = None
                    else:
                        scale = prep.scaler.scales[index] if index is not None else 1.0
                        center = prep.scaler.centers[index] if index is not None else 0.0
                        method = prep.scaler.methods[index] if index is not None else "IDENTITY"
                        expected = float(
                            np.float32(0.0 if method == "CONSTANT" else (b - center) / scale)
                        )
                        passed = bool(
                            math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10)
                            and float(actual[selected_index, j]) == expected
                        )
                    output.append(
                        dict(
                            fold=fold,
                            partition=actual_partition,
                            recipe_id=prep.preparation_id,
                            symbol=symbol,
                            feature=feature,
                            label=feature + " independent source replay",
                            representation="native + actual scaled float32",
                            units="dimensionless",
                            timestamp=str(base.history.calendar.steps[pos].end),
                            session=day,
                            origin=origin,
                            slot=slot,
                            selection=kind,
                            native=a,
                            registered_native=b,
                            scaled=float(actual[selected_index, j]),
                            independent_scaled=expected,
                            passed=passed,
                            source_binding=prep.source_binding,
                            source_lineage=base.components[symbol, day, slot].lineage_id,
                            clock="completed-hour END; prior data only",
                            ever_model_input=True,
                            actual_window_cutoff=str(
                                base.history.calendar.steps[positions[-1]].end
                            ),
                            model_input_status="frozen constructor, not historical batch capture",
                            limitation="No saved tensor; bitwise float32 constructor replay",
                        )
                    )
    return output
