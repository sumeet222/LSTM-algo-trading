"""Future reference marks kept separate from the immutable executed portfolios."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import numpy as np
import pandas as pd

from ..rapid_v1.costs import CostReference
from ..rapid_v1.shared_features import FeatureCache
from ..rapid_v1.sources import RawMarket
from ..rapid_v3_dynamic.offline import action_frontiers, targets
from ..rapid_v3_dynamic.policy import HoldingClock
from ..stage012.calendar_schedule import MarketClock
from ..stage012.model_registry import SYMBOLS
from ..stage35.completion_v3.tapes import load_actions, midnight
from ..stage35.final_backtest_v4.execution_calendar import ExecutionCalendar
from ..stage35.final_backtest_v4.market import minute
from ..stage35.final_backtest_v5.special import EX

D = Decimal
HORIZONS = ("T60", "T240", "NEXT_FULL_SESSION")
LIMIT = 5


@dataclass(frozen=True)
class EconomicEvent:
    ticker: int
    at: int
    kind: str
    value: float
    payable: int
    truth: str
    event_id: str


def event_tape() -> tuple[EconomicEvent, ...]:
    result = []
    for a in load_actions():
        when = a.ex_date or a.effective_date
        if (
            a.symbol not in SYMBOLS
            or not when
            or not date(2021, 1, 1) <= when <= date(2024, 12, 31)
        ):
            continue
        j, at = SYMBOLS.index(a.symbol), minute(midnight(when))
        if a.action_type == "CASH_DIVIDEND":
            if a.amount is None or a.payable_date is None or a.special:
                kind, amount = "UNSUPPORTED", 0.0
            else:
                kind, amount = "CASH", float(a.amount)
            paid = minute(midnight(a.payable_date)) if a.payable_date else 2**60
        elif a.action_type == "SPLIT" and a.split_ratio_new_old is not None:
            kind, amount, paid = "SPLIT", float(a.split_ratio_new_old), at
        elif a.action_type == "SPINOFF" or "HOLD" in a.effect_on_books:
            kind, amount, paid = "UNSUPPORTED", 0.0, at
        else:
            continue
        result.append(EconomicEvent(j, at, kind, amount, paid, a.status.value, a.event_id))
    # Use the already implemented regular-way ex-distribution transition.
    result = [
        e for e in result if not (e.ticker == SYMBOLS.index("MRK") and e.kind == "UNSUPPORTED")
    ]
    result.append(
        EconomicEvent(
            SYMBOLS.index("MRK"),
            minute(EX),
            "UNSUPPORTED",
            0.0,
            0,
            "VERIFIED_TERMS_UNMODELED_OFFLINE_ASSET",
            "MRK_OGN",
        )
    )
    return tuple(sorted(result, key=lambda e: (e.at, e.kind != "SPLIT", e.event_id)))


def clock() -> HoldingClock:
    return HoldingClock(ExecutionCalendar(MarketClock("2020-01-01", "2025-02-01")))


def economic_units(
    stock: np.ndarray,
    effective: np.ndarray,
    reference: np.ndarray,
    events: tuple[EconomicEvent, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Signed cash values are per original share. Future events never affect eligibility."""
    factor = np.ones(len(stock))
    cash = np.zeros(len(stock))
    claims = np.zeros(len(stock))
    unsupported = np.zeros(len(stock), dtype=bool)
    touched = np.zeros(len(stock), dtype=np.int32)
    for event in events:
        active = (stock == event.ticker) & (effective < event.at) & (event.at <= reference)
        if not active.any():
            continue
        touched[active] += 1
        if event.kind == "SPLIT":
            factor[active] *= event.value
        elif event.kind == "CASH":
            value = factor * event.value
            cash[active & (event.payable <= reference)] += value[
                active & (event.payable <= reference)
            ]
            claims[active & (event.payable > reference)] += value[
                active & (event.payable > reference)
            ]
        else:
            unsupported[active] = True
    return factor, cash, claims, unsupported, touched


def lookup(
    stock: np.ndarray,
    target: np.ndarray,
    cache: FeatureCache,
    c: HoldingClock,
    selected_months: set[str] | None = None,
) -> tuple[dict, list[dict]]:
    unique, inverse = np.unique(np.column_stack([target, stock]), axis=0, return_inverse=True)
    at, symbol = unique[:, 0], unique[:, 1]
    day_index = np.searchsorted(c.cal.closes, at, side="right")
    bounded = at < int(c.cal.closes[c.session(minute("2024-12-31T14:30:00Z"))])
    raw = np.full(len(at), np.nan)
    found = np.full(len(at), -1, dtype=np.int64)
    ratio = np.full(len(at), np.nan)
    adv = np.full(len(at), np.nan)
    market = RawMarket("2021-01-01", "2024-12-31")
    if selected_months is not None:
        market.parts = {k: v for k, v in market.parts.items() if k in selected_months}
    ordered = np.argsort(day_index, kind="stable")
    ordered_day = day_index[ordered]
    for day in market.days():
        session = c.session(int(day.starts[0]))
        lo, hi = np.searchsorted(ordered_day, [session, session + 1], side="left")
        block = ordered[lo:hi]
        if not len(block):
            continue
        f = cache.frames(day.date)[0]
        for j in range(20):
            b = block[(symbol[block] == j) & bounded[block]]
            if not len(b):
                continue
            valid_starts = day.starts[day.valid[:, j]]
            k = np.searchsorted(valid_starts, at[b])
            good = k < len(valid_starts)
            b, k = b[good], k[good]
            found[b] = valid_starts[k]
            raw[b] = day.opens[np.searchsorted(day.starts, found[b]), j]
            v20, v60 = f.values["v20"][j], f.values["v60"][j]
            ratio[b] = v20 / v60 if np.isfinite(v20) and np.isfinite(v60) and v60 > 0 else np.nan
            adv[b] = f.values["adv20"][j]
    return {
        "price": raw[inverse],
        "found": found[inverse],
        "ratio": ratio[inverse],
        "adv": adv[inverse],
        "bounded": bounded[inverse],
        "unique_requests": len(unique),
        "shared_requests": len(stock),
    }, market.reads


def cost_scenarios(sample: pd.DataFrame, ratio: np.ndarray, adv: np.ndarray) -> dict:
    q = sample["quantity"].to_numpy(float)
    q_new = q * sample["share_factor"].to_numpy(float)
    ref = sample["later_raw"].to_numpy(float)
    old_raw, actual = (sample[k].to_numpy(float) for k in ("raw", "fill"))
    at = sample["reference_at"].to_numpy(np.int64)
    later_concession = np.full(len(sample), np.nan)
    fee_delta = np.full(len(sample), np.nan)
    qcache = {}
    for n, (sid, size, old_q, price, vr, volume) in enumerate(
        zip(
            sample["strategy_id"],
            q_new,
            q,
            ref,
            ratio,
            adv,
            strict=True,
        )
    ):
        if not np.isfinite(price):
            continue
        mode = "MICRO_PRO" if sid.startswith("M") else "RETAIL_CONSERVATIVE"
        if mode == "MICRO_PRO" and (not np.isfinite(vr) or not np.isfinite(volume)):
            continue
        key = (
            mode,
            float(size),
            float(old_q),
            price,
            vr if mode == "MICRO_PRO" else 1.0,
            volume if mode == "MICRO_PRO" else 1.0,
        )
        if key not in qcache:
            reference = CostReference(mode, key[4], key[5], int(at[n]))
            fill, fee, *_ = reference.quote(D(str(price)), -D(str(size)), D(0), D(0), int(at[n]))
            old_fee = (
                D(".002") * abs(D(str(old_q)))
                if mode == "MICRO_PRO"
                else max(D(1), (D(".005") * abs(D(str(old_q)))).quantize(D(".01")))
            )
            qcache[key] = float(D(str(size)) * (D(str(price)) - fill)), float(fee - old_fee)
        later_concession[n], fee_delta[n] = qcache[key]
    recovery = q * (old_raw - actual)
    calendar_years = (at - sample["effective"].to_numpy(np.int64)) / (365 * 1440)
    carry = np.where(q < 0, abs(q) * old_raw * 0.02 * calendar_years, 0.0)
    return {
        "original_exit_concession_recovery": recovery,
        "assumed_later_exit_concession": later_concession,
        "standalone_fee_difference": fee_delta,
        "frozen_mark_short_carry": carry,
    }


def reference_status(
    bounded: np.ndarray,
    found: np.ndarray,
    target: np.ndarray,
    unsupported: np.ndarray,
) -> np.ndarray:
    why = np.full(len(found), "VALID", dtype="<U45")
    why[~bounded] = "CENSORED_EVALUATION_CUTOFF"
    why[(found < 0) & bounded] = "CENSORED_NO_VALID_MARK"
    why[(found >= 0) & (found - target > LIMIT) & bounded] = "CENSORED_FORWARD_LIMIT"
    why[(why == "VALID") & unsupported] = "CENSORED_UNSUPPORTED_DISTRIBUTION"
    if np.any((found >= 0) & (found < target)):
        raise ValueError("REFERENCE_BEFORE_TARGET")
    return why


def make_sample(tape: pd.DataFrame, cache: FeatureCache, selected_months: set[str] | None = None):
    c = clock()
    plans = targets(c, tape["effective"].to_numpy(np.int64))
    frame = pd.concat([tape.assign(horizon=h) for h in HORIZONS], ignore_index=True)
    target = np.concatenate([plans[h] for h in HORIZONS])
    day = np.searchsorted(c.cal.closes, target, side="right")
    target = np.maximum(target, c.cal.opens[day])
    stock = frame["ticker"].to_numpy(np.int64)
    effective = frame["effective"].to_numpy(np.int64)
    all_quotes, reads = lookup(
        np.r_[stock, tape["ticker"].to_numpy(np.int64)],
        np.r_[target, tape["entry"].to_numpy(np.int64)],
        cache,
        c,
        selected_months,
    )
    quotes = {
        key: value[: len(frame)] if isinstance(value, np.ndarray) else value
        for key, value in all_quotes.items()
    }
    entry_raw = all_quotes["price"][len(frame) :]
    entry_at = all_quotes["found"][len(frame) :]
    if not np.array_equal(entry_at, tape["entry"].to_numpy(np.int64)):
        raise ValueError("MISSING_ACTUAL_ENTRY_BAR")
    factor_existing, *_ = economic_units(
        tape["ticker"].to_numpy(np.int64),
        tape["entry"].to_numpy(np.int64),
        tape["effective"].to_numpy(np.int64),
        tuple(e for e in event_tape() if e.kind == "SPLIT"),
    )
    found = quotes["found"]
    factor, cash, claims, unsupported, touched = economic_units(
        stock, effective, found, event_tape()
    )
    why = reference_status(quotes["bounded"], found, target, unsupported)
    q = frame["quantity"].to_numpy(float)
    legacy_bad = np.zeros(len(frame), dtype=bool)
    for j, events in action_frontiers().items():
        b = stock == j
        legacy_bad[b] = np.searchsorted(events, found[b], side="right") > np.searchsorted(
            events, effective[b], side="right"
        )
    legacy_valid = quotes["bounded"] & (found >= 0) & ~legacy_bad
    legacy_bps = q * (quotes["price"] - frame["fill"].to_numpy(float))
    legacy_bps /= abs(q) * frame["fill"].to_numpy(float) / 10000
    legacy = {"valid": legacy_valid, "bps": legacy_bps}
    valid = why == "VALID"
    later = np.where(valid, quotes["price"], np.nan)
    adjusted = factor * q
    raw_increment = adjusted * later - q * frame["raw"].to_numpy(float)
    actual_increment = adjusted * later - q * frame["fill"].to_numpy(float)
    frame = frame.assign(
        target_at=target,
        reference_at=found,
        actual_entry_raw=np.tile(entry_raw, 3),
        existing_split_factor=np.tile(factor_existing, 3),
        bar_complete_at=found + 1,
        available_at=found + 3,
        lag=np.where(found >= 0, found - target, np.nan),
        later_raw=later,
        share_factor=factor,
        action_cash=q * cash,
        action_claims=q * claims,
        events=touched,
        censor=why,
        price_raw_to_raw=raw_increment,
        price_actual_exit_anchor=actual_increment,
        valid=valid.astype(int),
        total=1,
        ref_notional=abs(q) * frame["raw"].to_numpy(float),
        exit_year=pd.to_datetime(frame["effective"].to_numpy(np.int64) * 60, unit="s", utc=True)
        .strftime("%Y")
        .astype(int),
        symbol=np.asarray(SYMBOLS)[stock],
        side=np.where(q > 0, "LONG", "SHORT"),
        feasibility=np.where(
            frame["cause"].str.startswith("RISK_"),
            "INFEASIBLE_UNDER_REALIZED_RISK",
            "UNFUNDED_NONFORCED",
        ),
    )
    scenario = cost_scenarios(frame, quotes["ratio"], quotes["adv"])
    for k, value in scenario.items():
        frame[k] = value
    frame["action_value"] = frame["action_cash"] + frame["action_claims"]
    frame["conditional_after_price_carry"] = (
        frame["price_raw_to_raw"]
        + frame["action_value"]
        + frame["original_exit_concession_recovery"]
        - frame["assumed_later_exit_concession"]
        - frame["frozen_mark_short_carry"]
    )
    frame["conditional_standalone_net"] = (
        frame["conditional_after_price_carry"] - frame["standalone_fee_difference"]
    )
    frame["raw_bps"] = frame["price_raw_to_raw"] / frame["ref_notional"] * 10000
    frame["executed_anchor_bps"] = frame["price_actual_exit_anchor"] / frame["ref_notional"] * 10000
    frame["conditional_bps"] = frame["conditional_standalone_net"] / frame["ref_notional"] * 10000
    held = np.asarray(
        [
            c.index(int(x)) - c.index(int(y))
            for x, y in zip(
                frame["effective"],
                frame["entry"],
                strict=True,
            )
        ]
    )
    exit_session = np.searchsorted(c.cal.closes, effective, side="right")
    strength = frame["exit_strength"].to_numpy(float)
    quantile_state = np.full(len(frame), "UNKNOWN", dtype="<U12")
    for sid in sorted(set(frame["strategy_id"])):
        member = frame["strategy_id"].to_numpy() == sid
        original = np.asarray(tape.loc[tape["strategy_id"] == sid, "exit_strength"], dtype=float)
        original = original[np.isfinite(original)]
        if len(original):
            cuts = np.quantile(original, [0.2, 0.4, 0.6, 0.8])
            known = member & np.isfinite(strength)
            quantile_state[known] = np.asarray(
                [
                    "Q" + str(int(v) + 1)
                    for v in np.searchsorted(cuts, strength[known], side="right")
                ]
            )
    frame["exit_score_quantile"] = quantile_state
    frame["prior_raw_leg_pnl"] = (
        frame["quantity"] * frame["raw"]
        - frame["quantity"] / frame["existing_split_factor"] * frame["actual_entry_raw"]
    )
    frame["prior_raw_leg_state"] = np.select(
        [frame["prior_raw_leg_pnl"] > 0, frame["prior_raw_leg_pnl"] < 0],
        ["WIN", "LOSS"],
        default="FLAT",
    )
    frame["exit_state"] = np.select(
        [~np.isfinite(strength), strength < 0, strength < 1],
        ["unknown", "reversed", "weak"],
        default="strong",
    )
    frame["entry_state"] = np.select(
        [frame["entry_strength"] < 1, frame["entry_strength"] < 2],
        ["lt1", "1to2"],
        default="2plus",
    )
    frame["holding"] = np.select(
        [held < 60, held < 240, held < 390, held < 1950],
        ["lt60", "60to239", "240to389", "390to1949"],
        default="1950plus",
    )
    frame["session_type"] = np.where(
        c.cal.closes[exit_session] - c.cal.opens[exit_session] == 390, "FULL", "HALF"
    )
    frame["cross_session"] = np.where(day == exit_session, "SAME_SESSION", "LATER_SESSION")
    frame["external_state"] = np.where(frame["external"], "EXTERNAL", "INTERNAL")
    frame["exit_day"] = (
        pd.to_datetime(frame["effective"].to_numpy(np.int64) * 60, unit="s", utc=True)
        .tz_convert("America/New_York")
        .strftime("%Y-%m-%d")
    )
    frame["year_cause"] = frame["exit_year"].astype(str) + "/" + frame["cause"]
    frame["action_scope"] = np.where(frame["events"] > 0, "ACTION_IN_EXTENSION", "NO_TAPE_EVENT")
    frame["cause_side"] = frame["cause"] + "/" + frame["side"]
    frame["cause_state"] = frame["cause"] + "/" + frame["exit_state"]
    frame["feasible_external"] = np.where(
        (frame["feasibility"] == "UNFUNDED_NONFORCED") & frame["external"],
        "UNFUNDED_NONFORCED_EXTERNAL",
        "OTHER",
    )
    frame["all"] = "ALL"
    return (
        frame,
        legacy,
        {
            "source_reads": reads,
            "unique_reference_requests": quotes["unique_requests"],
            "requests": len(frame),
            "tape_hash_required": True,
        },
    )
