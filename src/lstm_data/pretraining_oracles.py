"""Independent finite-precision real-row oracles for candidate preparation only."""
from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from .config import write_json
from .pretraining_policy import verify_ref
from .pretraining_source import ConditionalHistory
from .pretraining_tables import BaseTables, proxy_panel, tg0
from .pretraining_transforms import CandidatePreparation, raw_features


def recompute_row(history: ConditionalHistory, day: str, slot: int, origin: int,
                  preparation: CandidatePreparation, symbol: str) -> dict:
    """Re-derive each family from immutable aggregate inputs, not cached Components."""
    cal = history.calendar
    pos = cal._positions[day, slot]
    hours = [history.bars[symbol, s.session, s.slot] for s in cal.steps[:pos + 1]]
    row = hours[-1]
    source_manifest = json.loads(verify_ref(
        history.authority.root, history.authority.policy["source_manifest"]
    ).read_text())
    native = []
    for ref in source_manifest["source_by_stock"][symbol]:
        params = ref["params"]
        if not (row.start >= pd.Timestamp(params["start"])
                and row.end <= pd.Timestamp(params["end"])):
            continue
        path = verify_ref(history.authority.root,
                          {"path": ref["data"], "sha256": ref["sha256"]})
        frame = pq.read_table(path, columns=["timestamp", "open", "high", "low", "close", "volume"],
                              filters=[("symbol", "==", symbol),
                                       ("timestamp", ">=", row.start.to_pydatetime()),
                                       ("timestamp", "<", row.end.to_pydatetime())]).to_pandas()
        native.extend(frame.sort_values("timestamp").to_dict("records"))
    if len(native) != 2:
        raise ValueError("ORACLE_EXACT_TWO_NATIVE_ROWS_REQUIRED")
    native_aggregate = (native[0]["open"], max(r["high"] for r in native),
                        min(r["low"] for r in native), native[1]["close"],
                        sum(r["volume"] for r in native))
    aggregate = (row.open, row.high, row.low, row.close, row.volume)
    if native_aggregate != aggregate:
        raise ValueError("INDEPENDENT_NATIVE_AGGREGATION_MISMATCH")
    oc = np.asarray([math.log(r.close / r.open) for r in hours])
    closes = np.asarray([r.close for r in hours])
    daily = [history.daily[symbol, d] for d in cal.days if d < day]
    prices = [r.close for r in daily]
    if any(x is None for x in prices) or len(prices) < 126:
        raise ValueError("ORACLE_COMPLETE_DAILY_HISTORY_REQUIRED")
    dc = np.asarray(prices, dtype=float)
    dv = np.asarray([r.volume for r in daily], dtype=float)
    h12 = float(np.sqrt(np.mean(oc[-12:] ** 2)))
    h60 = float(np.sqrt(np.mean(oc[-60:] ** 2)))
    daily_returns = np.log(dc[-63:] / dc[-64:-1])
    d63 = float(np.sqrt(np.mean(daily_returns ** 2)))
    floor = preparation.floors[history.universe.index(symbol)]
    prior = cal.prior[day, origin][-60:]
    past = np.asarray([math.log(history.bars[symbol, d, origin + 4].close
                                / history.bars[symbol, d, origin].close) for d in prior])
    if len(past) != 60:
        raise ValueError("ORACLE_M2_60_PRIOR_REQUIRED")
    m2mean = float(np.mean(past[-20:]))
    m2rms = float(np.sqrt(np.mean(past ** 2)))
    q1 = float(np.mean([history.bars[symbol, d, slot].volume
                        for d in cal.matching[day, slot]]))
    emas = {p: float(closes[0]) for p in (6, 18, 24, 72)}
    for close in closes[1:]:
        for p in emas:
            alpha = 2 / (p + 1)
            emas[p] = alpha * float(close) + (1 - alpha) * emas[p]
    changes = np.diff(closes)
    gain = float(np.mean(np.maximum(changes[:14], 0)))
    loss = float(np.mean(np.maximum(-changes[:14], 0)))
    for change in changes[14:]:
        gain = (13 * gain + max(float(change), 0)) / 14
        loss = (13 * loss + max(-float(change), 0)) / 14
    rsi = 50. if gain == loss == 0 else (100. if loss == 0 else 100 - 100 / (1 + gain / loss))
    values = (
        float(oc[-1]) / max(h60, floor.hourly_floor),
        m2mean / max(m2rms, floor.m2_floor),
        math.log(dc[-1] / dc[-6]) / (math.sqrt(5) * max(d63, floor.daily_floor)),
        math.log(dc[-21] / dc[-126]) / (math.sqrt(105) * max(d63, floor.daily_floor)),
        math.log(max(h12, floor.hourly_floor)), math.log(max(h60, floor.hourly_floor)),
        math.log(max(h12, floor.hourly_floor)) - math.log(max(h60, floor.hourly_floor)),
        math.log(row.high / row.low),
        0. if row.high == row.low else (2 * row.close - row.high - row.low) / (row.high - row.low),
        math.log((row.volume + floor.hourly_pseudocount) / (q1 + floor.hourly_pseudocount)),
        math.log((float(np.mean(dv[-5:])) + floor.daily_pseudocount)
                 / (float(np.mean(dv[-60:])) + floor.daily_pseudocount)),
        math.log(row.close / float(np.mean(dc[-20:]))),
        float(np.mean(np.sign(np.diff(dc[-21:])))),
        (emas[6] - emas[18]) / row.close, (emas[24] - emas[72]) / row.close, (rsi - 50) / 50,
    )
    return {"symbol": symbol, "day": day, "slot": slot, "origin": origin,
            "independent_values": values, "hourly_RMS12": h12, "hourly_RMS60": h60,
            "daily_RMS63": d63, "M2_mean20": m2mean, "M2_RMS60": m2rms,
            "prior_M2_days": prior, "floors": asdict(floor),
            "last_hourly_close": row.close, "previous_hourly_close": hours[-2].close,
            "previous_daily_close": float(dc[-1]),
            "native_half_hours": [dict(r, timestamp=str(r["timestamp"])) for r in native],
            "independent_hourly_aggregate_OHLCV": native_aggregate,
            "hourly_aggregation_exact_match": True,
            "next_day_or_future_values_used": False}


def audit_rows(base: BaseTables, preparation: CandidatePreparation) -> list[dict]:
    """Small deterministic split/overnight/DST examples; never confirmation selection."""
    history = base.history
    if not isinstance(history, ConditionalHistory):
        raise ValueError("ORACLE_REQUIRES_VERIFIED_NATIVE_BUILD_CONTEXT")
    output = []
    for day in ("2020-07-01", "2020-08-28", "2020-08-31", "2021-03-15"):
        oracle = recompute_row(history, day, 1, 1, preparation, "AAPL")
        pos = history.calendar._positions[day, 1]
        values, reasons = raw_features(base, "AAPL", pos, 1, preparation.floors[0])
        if any(x is None for x in values):
            raise ValueError("REAL_ORACLE_FEATURE_INVALID")
        delta = np.asarray(values, dtype=float) - np.asarray(oracle["independent_values"])
        if not np.allclose(delta, 0, atol=1e-10, rtol=0):
            raise ValueError("REAL_INDEPENDENT_FT0_ORACLE_MISMATCH")
        panel = proxy_panel(history, day, 1)
        r = tuple(math.log(float(x) / float(a)) for a, x in
                  zip(panel.entry_prices, panel.exit_prices) if a is not None and x is not None)
        median = sorted(r)[2]
        mad = sorted(abs(x - median) for x in r)[2]
        expected = tuple((x - median) / (mad + preparation.target_epsilon) for x in r)
        if not np.allclose(expected, tg0(r, preparation.target_epsilon), atol=1e-12, rtol=0):
            raise ValueError("REAL_INDEPENDENT_TG0_ORACLE_MISMATCH")
        oracle.update({"calculated_values": values, "reasons": reasons,
                       "absolute_differences": np.abs(delta).tolist(),
                       "max_absolute_difference": float(np.max(np.abs(delta))),
                       "scaled_values": preparation.scaler.apply(tuple(x for x in values
                                                                          if x is not None)),
                       "target_prices_entry": panel.entry_prices,
                       "target_prices_exit": panel.exit_prices, "target_raw_returns": r,
                       "target_median": median, "target_unscaled_MAD": mad,
                       "target_epsilon_TRAIN_ONLY": preparation.target_epsilon,
                       "target_TG0": expected, "maturity": str(panel.maturity),
                       "designation": "ASSUMPTION_CONDITIONAL_NOT_OBSERVED_PUBLICATION"})
        output.append(oracle)
    return output


def publish_oracles(base: BaseTables, preparation: CandidatePreparation, report: Path) -> None:
    write_json(report / "independent_real_oracles.json", audit_rows(base, preparation))
