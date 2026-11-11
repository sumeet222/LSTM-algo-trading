"""Read-only diagnostics for the frozen Rapid V3 R01 accounts."""

import argparse
import csv
import gzip
import json
import time
from bisect import bisect_right
from collections import defaultdict
from decimal import Decimal
from fractions import Fraction
from math import isclose, sqrt
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from .rapid_v1.cli import peak_memory_bytes
from .rapid_v1.costs import CostReference
from .rapid_v1.paths import canonical, digest, publish
from .rapid_v1.shared_features import FeatureCache
from .rapid_v1.sources import RawMarket
from .rapid_v1.state import decode
from .rapid_v1.strategies import IDS, evaluate
from .rapid_v2_diagnostics.report import csv_write
from .rapid_v3_dynamic.book import DynamicLedger
from .rapid_v3_dynamic.policy import REGIMES, HoldingClock, monitored, scores
from .stage012.calendar_schedule import MarketClock
from .stage012.model_registry import SYMBOLS
from .stage35.final_backtest_v4.execution_calendar import ExecutionCalendar

D = Decimal
USD = D("1e-7")
GROSS_TOL = D("1e-6")
NY = "America/New_York"
FIRST, LAST = "2021-01-01", "2024-12-31"
DEFAULT = Path("trading/track2/rapid_r01_deep_dive")
FACTS = Path("configs/hf1m_p019_verified_event_facts_v1.json")
MODES = tuple(REGIMES)
KEY = ["origin", "ticker", "side"]
MONEY = (
    "gross_signed_price_PnL_USD",
    "gross_action_value_USD",
    "commission_USD",
    "assumed_spread_USD",
    "assumed_impact_USD",
    "borrow_USD",
    "funding_USD",
)


def column(frame: pd.DataFrame, key: str) -> pd.Series:
    item = frame[key]
    if not isinstance(item, pd.Series):
        raise ValueError(f"AMBIGUOUS_COLUMN {key}")
    return item


def table(value: object) -> pd.DataFrame:
    if not isinstance(value, pd.DataFrame):
        raise ValueError("EXPECTED_TABLE")
    return value


def select(frame: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
    return table(frame.loc[mask])


def as_rows(frame: pd.DataFrame) -> list[SimpleNamespace]:
    if not all(isinstance(name, str) for name in frame.columns):
        raise ValueError("NON_STRING_COLUMN_NAME")
    return [
        SimpleNamespace(**{str(k): v for k, v in row.items()}) for row in frame.to_dict("records")
    ]


def sum_d(values: pd.Series) -> D:
    return sum((D(str(x)) for x in values), D(0))


def json_at(path: Path) -> dict:
    return json.loads(path.read_text())


def csv_at(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def seal_check(seal: dict) -> None:
    for name, spec in seal["files"].items():
        p = Path(name)
        if p.stat().st_mtime_ns != spec["mtime_ns"] or digest(p) != spec["sha256"]:
            raise ValueError(f"SEALED_INPUT_DRIFT {name}")


def near(actual: D, expected: D, label: str, tol: D = USD) -> None:
    if not actual.is_finite() or not expected.is_finite() or abs(actual - expected) > tol:
        raise ValueError(f"{label}: {actual} versus {expected}")


def dollars(row: dict[str, str]) -> tuple[D, D]:
    price, actions, *costs = map(D, (row[k] for k in MONEY))
    cost = sum(costs, D(0))
    return price + actions - cost, cost


def checkpoint(path: Path, binding: dict) -> dict[str, DynamicLedger]:
    envelope = json.loads(gzip.decompress(path.read_bytes()))
    body = envelope["body"]
    if body["binding"] != binding or envelope["sha256"] != canonical(body) or body["legacy"]:
        raise ValueError("CHECKPOINT_BINDING")
    state = dict(body["state"]["mapping"])
    if state["last_completed"] != LAST or state["days_completed"] != 1005:
        raise ValueError("CHECKPOINT_FRONTIER")
    accounts = {}
    for encoded in body["accounts"]["items"]:
        arm = dict(encoded["mapping"])["arm"]
        if arm.startswith("R01_"):
            a = DynamicLedger(**decode(encoded))
            a.reconcile()
            accounts[a.regime] = a
    if set(accounts) != set(MODES):
        raise ValueError("CHECKPOINT_R01_REGIME_AXIS")
    return accounts


def opportunities(cache: FeatureCache, clock: HoldingClock) -> pd.DataFrame:
    """Evaluate the inherited direction rule on received features alone."""
    rows = []
    for date in cache.by_date:
        for f in cache.frames(date):
            result = evaluate("R01", f)
            if not result.scheduled:
                continue
            if f.slot != 1 or not f.weekly_scan or f.decision != f.origin + 2:
                raise ValueError("R01_SCAN_CLOCK")
            _, ranks = scores("R01", f)
            for i in result.intents:
                j, side = i.tickers[0], i.signs[0]
                ahead = ranks * side > ranks[j] * side
                ties = (ranks == ranks[j]) & (np.arange(len(SYMBOLS)) < j)
                rank = 1 + int(np.sum(ahead | ties))
                if rank > 2 or f.prior_available > f.decision or i.lineage != f.lineage:
                    raise ValueError("R01_CAUSAL_TAIL_RANK")
                rows.append(
                    {
                        "origin": f.origin,
                        "ticker": j,
                        "side": side,
                        "date": f.session,
                        "decision": f.decision,
                        "lineage": f.lineage,
                        "rank": rank,
                        "J": float(ranks[j]),
                        "strength": i.strength,
                        "prior_available": f.prior_available,
                        "prior_v20": float(f.values["v20"][j]),
                        "calendar_admissible": clock.admits(f, False, LAST),
                    }
                )
    out = pd.DataFrame(rows).sort_values(KEY)
    if out.duplicated(KEY).any() or out.duplicated(["origin", "ticker"]).any():
        raise ValueError("DUPLICATE_R01_OPPORTUNITY")
    cuts = pd.qcut(column(out, "strength"), 10, duplicates="raise")
    if not isinstance(cuts, pd.Series):
        raise ValueError("SCORE_BIN_SCHEMA")
    out["score_decile"] = cuts.cat.codes + 1
    return out


def stamp(series: pd.Series) -> pd.DatetimeIndex:
    return pd.to_datetime(series.to_numpy(dtype=np.int64) * 60, unit="s", utc=True).tz_convert(NY)


def validated_legs(funded: Path, opp: pd.DataFrame) -> pd.DataFrame:
    legs = pd.read_parquet(
        funded / "SEALED_ACTUAL_EXIT_LEGS.parquet", filters=[("strategy_id", "==", "R01")]
    ).rename(columns={"decision": "exit_decision"})
    legs["side"] = np.sign(column(legs, "quantity")).astype(int)
    legs = legs.merge(opp, on=KEY, how="left", validate="many_to_one", indicator=True)
    if (
        column(legs, "_merge").ne("both").any()
        or not np.allclose(
            column(legs, "entry_strength"), column(legs, "strength"), rtol=0, atol=1e-12
        )
        or (column(legs, "entry") <= column(legs, "decision")).any()
        or (column(legs, "entry") > column(legs, "origin") + 10).any()
        or (column(legs, "effective") <= column(legs, "exit_decision")).any()
        or (column(legs, "posted") < column(legs, "effective") + 3).any()
        or (column(legs, "entry") > column(legs, "effective")).any()
        or not column(legs, "external").all()
    ):
        raise ValueError("R01_EXIT_TAPE_OPPORTUNITY_OR_CLOCK")
    legs["entry_date"] = stamp(column(legs, "entry")).strftime("%Y-%m-%d")
    legs["exit_date"] = stamp(column(legs, "effective")).strftime("%Y-%m-%d")
    return legs.drop(columns="_merge")


def raw_points(legs: pd.DataFrame, fixture: bool = False) -> tuple[dict, pd.DataFrame, list[dict]]:
    """Query just actual saved execution markers in one vetted raw-share pass."""
    wanted: dict[str, set[tuple[int, int]]] = defaultdict(set)
    for row in as_rows(legs):
        wanted[row.entry_date].add((row.entry, row.ticker))
        wanted[row.exit_date].add((row.effective, row.ticker))
    scope = (min(wanted), max(wanted)) if fixture else (FIRST, LAST)
    market = RawMarket(*scope)
    prices = {}
    dates, closes = [], []
    factors = np.ones(len(SYMBOLS))
    splits = split_events()
    for day in market.days():
        for j, date, ratio in splits:
            if day.date == date:
                factors[j] *= ratio
        dates.append(day.date)
        closes.append(np.where(day.valid[-1], day.closes[-1] * factors, np.nan))
        for at, j in wanted.get(day.date, ()):
            i = int(at - day.starts[0])
            if i < 0 or i >= len(day.starts) or day.starts[i] != at or not day.valid[i, j]:
                raise ValueError("UNSUPPORTED_ACTUAL_FILL_MARKER")
            prices[at, j] = D(str(day.opens[i, j]))
    returns = pd.DataFrame(closes, index=pd.Index(dates, name="date"), columns=list(SYMBOLS))
    returns = returns.pct_change(fill_method=None)
    return prices, returns, market.reads


def split_events() -> list[tuple[int, str, int]]:
    return [
        (SYMBOLS.index(a["ticker"]), a["date"], int(a["factor_denominator"]))
        for a in json_at(FACTS)["events"]
        if a["kind"] == "SPLIT" and FIRST <= a["date"] <= LAST
    ]


def entry_units(
    q: int,
    ticker: int,
    first: str,
    last: str,
    splits: list[tuple[int, str, int]],
) -> Fraction:
    ratio = 1
    for j, date, factor in splits:
        if j == ticker and first < date <= last:
            ratio *= factor
    return Fraction(q, ratio)


def monitor_history(cache: FeatureCache, clock: HoldingClock) -> tuple[list[int], dict]:
    frontier = {}
    for day in cache.by_date:
        for f in cache.frames(day):
            session = clock.session(f.origin)
            if not monitored("R01", f, clock.cal.closes[session] - clock.cal.opens[session] == 390):
                continue
            score, ranks = scores("R01", f)
            frontier[f.decision] = (f.latest_observation_end, score, ranks)
    return sorted(frontier), frontier


def add_causal_rank(cohorts: pd.DataFrame, cache: FeatureCache, clock: HoldingClock) -> None:
    stamps, frontier = monitor_history(cache, clock)
    ranks, aligned, observed_at = [], [], []
    for row in as_rows(cohorts):
        i = bisect_right(stamps, row.last_exit_decision) - 1
        if i < 0:
            observed_at.append(None)
            ranks.append(None)
            aligned.append(None)
            continue
        observed, score, r = frontier[stamps[i]]
        known = observed > row.entry and np.isfinite(score[row.ticker])
        observed_at.append(stamps[i] if known else None)
        ranks.append(1 + int(np.sum(r * row.side > r[row.ticker] * row.side)) if known else None)
        aligned.append(score[row.ticker] * row.side if known else None)
    cohorts["last_supported_monitor_decision"] = observed_at
    cohorts["last_supported_monitor_rank"] = ranks
    cohorts["last_supported_monitor_aligned_z"] = aligned


def infer_ticket(q: int, raw: D) -> tuple[D, D, D]:
    fill, fee, *_ = CostReference("RETAIL_CONSERVATIVE").quote(raw, D(q), D(0), D(0), 0)
    return fill, fee, D(q) * (fill - raw)


def reconstruction(
    legs: pd.DataFrame,
    prices: dict,
    clock: HoldingClock,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    cohorts, tickets = [], []
    splits = split_events()
    for ident, values in legs.groupby(["regime", "lot"], sort=True):
        if not isinstance(ident, tuple) or len(ident) != 2:
            raise ValueError("LOT_GROUP_KEY")
        regime, key = ident
        group = table(values)
        items = as_rows(group.sort_values(["effective", "posted"]))
        first, last = items[0], items[-1]
        if len(set(group["entry"])) != 1 or len(set(group["side"])) != 1:
            raise ValueError("R01_LOT_IDENTITY")
        raw_entry = prices[first.entry, first.ticker]
        units = sum(
            entry_units(r.quantity, r.ticker, r.entry_date, r.exit_date, splits) for r in items
        )
        if units != int(units):
            raise ValueError("NONINTEGRAL_ENTRY_BASIS")
        q = int(units)
        fill, fee, price_cost = infer_ticket(q, raw_entry)
        tickets.append(ticket(first, "ENTRY", first.entry, q, raw_entry, fill, fee, price_cost))
        gross, exits_raw = -q * raw_entry, D(0)
        final = last.cause
        risk_legs = 0
        for leg in items:
            raw_exit = prices[leg.effective, leg.ticker]
            near(D(str(leg.raw)), raw_exit, "RAW_EXIT_PARITY")
            fill_x, fee_x, price_x = infer_ticket(-leg.quantity, raw_exit)
            near(fill_x, D(str(leg.fill)), "EXTERNAL_RETAIL_FILL_PARITY")
            exits_raw += abs(leg.quantity) * raw_exit
            gross += leg.quantity * raw_exit
            fee += fee_x
            price_cost += price_x
            risk_legs += int(leg.cause.startswith("RISK_"))
            tickets.append(
                ticket(leg, "EXIT", leg.effective, -leg.quantity, raw_exit, fill_x, fee_x, price_x)
            )
        # Once a risk cause is recorded, V3 retains its first primary cause.
        if risk_legs:
            final = next(r.cause for r in items if r.cause.startswith("RISK_"))
        age = clock.index(last.effective) - clock.index(first.entry)
        cohorts.append(
            {
                "regime": regime,
                "lot": key,
                "ticker": first.ticker,
                "symbol": SYMBOLS[first.ticker],
                "side": first.side,
                "origin": first.origin,
                "lineage": first.lineage,
                "entry": first.entry,
                "last_exit": last.effective,
                "last_exit_decision": last.exit_decision,
                "entry_date": first.entry_date,
                "exit_date": last.exit_date,
                "entry_qty": q,
                "entry_notional": abs(q) * raw_entry,
                "entry_raw": raw_entry,
                "exit_raw_per_entry_share": (gross + q * raw_entry) / q,
                "gross": gross,
                "net_before_actions_carry": gross - fee - price_cost,
                "spread": price_cost / 2,
                "impact": price_cost / 2,
                "commission": fee,
                "raw_turnover": abs(q) * raw_entry + exits_raw,
                "exit_legs": len(items),
                "risk_legs": risk_legs,
                "risk": bool(risk_legs),
                "final_fill_risk": last.cause.startswith("RISK_"),
                "cause": final,
                "rank": first.rank,
                "strength": first.strength,
                "score_decile": first.score_decile,
                "exit_strength": last.exit_strength,
                "prior_v20": first.prior_v20,
                "scheduled_minutes": age,
                "wall_minutes": last.effective - first.entry,
                "before_maximum": last.effective
                < clock.cal.next(clock.maximum(first.entry, False) + 2),
                "overnight": first.entry_date != last.exit_date,
                "exit_gap": bool(group["source_delay"].any()),
                "first_fill_delay": first.entry - first.decision,
            }
        )
    return pd.DataFrame(cohorts), pd.DataFrame(tickets)


def ticket(
    r: SimpleNamespace, role: str, at: int, q: int, raw: D, fill: D, fee: D, cost: D
) -> dict:
    return {
        "regime": r.regime,
        "role": role,
        "lot": r.lot,
        "ticker": r.ticker,
        "at": at,
        "quantity": q,
        "raw_turnover": abs(q) * raw,
        "turnover": abs(q) * fill,
        "fee": fee,
        "concession": cost,
    }


def drawdown(nav: pd.Series, dates: pd.Series, initial: float) -> dict:
    wealth = np.r_[initial, nav.to_numpy(float)]
    labels = ["INITIAL", *map(str, dates)]
    high = np.maximum.accumulate(wealth)
    dd = wealth / high - 1
    trough = int(np.argmin(dd))
    peak = int(np.flatnonzero(wealth[: trough + 1] == high[trough])[-1])
    recovery = np.flatnonzero(wealth[trough + 1 :] >= wealth[peak])
    best, start, end, streak = 0, 0, 0, 0
    for n, x in enumerate(dd):
        streak = streak + 1 if x < 0 else 0
        if streak > best:
            best, start, end = streak, n - streak + 1, n
    return {
        "max_drawdown": float(dd[trough]),
        "dd_peak": labels[peak],
        "dd_trough": labels[trough],
        "dd_recovery": labels[trough + 1 + int(recovery[0])] if recovery.size else "UNRECOVERED",
        "underwater_sessions": best,
        "underwater_first": labels[start],
        "underwater_last": labels[end],
    }


def extras(a: DynamicLedger) -> list[dict]:
    out = []
    for r in a.stats.anomalies:
        if r["kind"] != "OGN_EXTERNAL_DISPOSAL":
            continue
        q, raw = D(r["external_delta"]), D(r["raw_reference"])
        fee, cash = D(r["fee"]), D(r["external_cash"])
        if not q:
            raise ValueError("ZERO_OGN_EXTERNAL_QUANTITY")
        fill = -(cash + fee) / q
        out.append(
            {
                "regime": a.regime,
                "role": "OGN",
                "lot": "SPECIAL",
                "ticker": 20,
                "at": r["effective"],
                "quantity": int(q),
                "raw_turnover": abs(q) * raw,
                "turnover": abs(q) * fill,
                "fee": fee,
                "concession": q * (fill - raw),
            }
        )
    if len(out) != a.stats.counts["OGN_EXTERNAL_DISPOSAL"]:
        raise ValueError("OGN_TICKET_COVERAGE")
    return out


def financial_check(
    row: dict[str, str],
    daily: pd.DataFrame,
    a: DynamicLedger,
    c: pd.DataFrame,
    t: pd.DataFrame,
    reasons: list[dict[str, str]],
) -> dict:
    nav, initial = D(row["final_NAV_USD"]), D(row["initial_cash_USD"])
    net, cost = dollars(row)
    state_nav = a.nav()
    if state_nav is None or len(daily) != 1005 or not column(daily, "status").eq("OBSERVED").all():
        raise ValueError("R01_NAV_FRONTIER")
    if (
        column(daily, "date").duplicated().any()
        or not column(daily, "date").is_monotonic_increasing
    ):
        raise ValueError("R01_NAV_DATES")
    nav_error = column(daily, "nav") - daily[["cash", "claims", "physical_value", "special"]].sum(
        axis=1
    )
    near(D(str(nav_error.abs().max())), D(0), "DAILY_NAV_BALANCE")
    near(state_nav, nav, "TERMINAL_NAV")
    near(D(str(column(daily, "nav").iloc[-1])), nav, "DAILY_TERMINAL_NAV")
    near(initial + net, state_nav, "CASH_BRIDGE")
    near(net, D(row["net_PnL_USD"]), "NET_REPORT")
    near(cost, D(row["total_cost_USD"]), "TOTAL_COST")
    for key, value in (
        ("terminal_cash_USD", a.cash),
        ("terminal_claims_USD", a.claim_total()),
        ("terminal_restricted_USD", a.restricted()),
        ("commission_USD", a.commission),
        ("borrow_USD", a.borrow_paid),
        ("funding_USD", a.funding_paid),
        ("assumed_spread_USD", a.stats.spread),
        ("assumed_impact_USD", a.stats.impact),
    ):
        near(value, D(row[key]), key)
    for key, value in (
        ("executed_turnover_USD", sum_d(column(t, "turnover"))),
        ("raw_open_turnover_USD", sum_d(column(t, "raw_turnover"))),
        ("commission_USD", sum_d(column(t, "fee"))),
        ("assumed_spread_USD", sum_d(column(t, "concession")) / 2),
        ("gross_signed_price_PnL_USD", sum_d(column(c, "gross"))),
        ("gross_winners_USD", sum_d(column(select(c, column(c, "gross") > 0), "gross"))),
        ("gross_losers_USD", sum_d(column(select(c, column(c, "gross") < 0), "gross"))),
    ):
        near(value, D(row[key]), key, GROSS_TOL)
    if t.duplicated(["ticker", "at"]).any() or a.pending or any(a.quantity):
        raise ValueError("TICKET_INFERENCE_OR_TERMINAL_ORDERS")
    counts = {
        "cohorts": len(c),
        "closed_cohorts": len(c),
        "early_exits": 0,
        "external_orders": len(t),
        "external_fills": a.stats.counts["EXTERNAL_PHYSICAL_FILLS"],
        "risk_final_exits": int(column(c, "final_fill_risk").sum()),
        "scheduled_final_exits": len(c) - int(column(c, "final_fill_risk").sum()),
        "cohorts_with_risk_fill": int(column(c, "risk").sum()),
        "risk_closed_cohorts": int(column(c, "risk").sum()),
        "risk_before_240": int((column(c, "risk") & (column(c, "scheduled_minutes") < 240)).sum()),
        "policy_before_240": int(
            (~column(c, "risk") & (column(c, "scheduled_minutes") < 240)).sum()
        ),
    }
    if any(D(row[k]) != v for k, v in counts.items()) or len(t) != counts["external_fills"]:
        raise ValueError("R01_COHORT_OR_ORDER_CENSUS")
    for reason in reasons:
        x = select(c, column(c, "cause") == reason["cause"])
        if len(x) != int(reason["cohorts"]):
            raise ValueError("R01_EXIT_CAUSE_CENSUS")
        near(sum_d(column(x, "gross")), D(reason["gross_price"]), "EXIT_CAUSE_GROSS", GROSS_TOL)
    if len(c) != sum(int(x["cohorts"]) for x in reasons):
        raise ValueError("R01_MISSING_EXIT_CAUSE")
    returns = (
        column(daily, "nav").to_numpy(float) / np.r_[float(initial), column(daily, "nav")[:-1]] - 1
    )
    years = (
        pd.Timestamp(column(daily, "date").iloc[-1]) - pd.Timestamp(column(daily, "date").iloc[0])
    ).days / 365.25
    dt = drawdown(column(daily, "nav"), column(daily, "date"), float(initial))
    computed = {
        "Sharpe_252_zero_rf": returns.mean() / returns.std(ddof=1) * sqrt(252),
        "CAGR": (float(state_nav / initial)) ** (1 / years) - 1,
        "max_drawdown": dt["max_drawdown"],
    }
    previous = float(initial)
    for year, values in daily.groupby(column(daily, "date").str[:4]):
        end = values["nav"].iloc[-1]
        computed[f"return_{year}"] = end / previous - 1
        previous = end
    if any(not isclose(v, float(row[k]), abs_tol=1e-12) for k, v in computed.items()):
        raise ValueError("R01_DAILY_METRIC_DRIFT")
    return {
        "regime": a.regime,
        "status": "PASS",
        "initial_USD": initial,
        **{k: row[k] for k in MONEY},
        "net_USD": net,
        "terminal_NAV_exact_USD": state_nav,
        "terminal_cash_USD": a.cash,
        "terminal_claims_USD": a.claim_total(),
        "terminal_restricted_USD": a.restricted(),
        "terminal_stock_symbols": 0,
        "terminal_pending": 0,
        "cash_bridge_error_USD": initial + net - state_nav,
        "max_daily_float_residual_USD": nav_error.abs().max(),
        "executed_turnover_USD": sum_d(column(t, "turnover")),
        **counts,
        **computed,
        **dt,
    }


def inputs(seal: dict) -> tuple[Path, dict, FeatureCache, HoldingClock, dict[str, DynamicLedger]]:
    cache = FeatureCache(Path(seal["cache"]))
    status = json_at(Path(seal["status_path"]))
    funded = Path(status["funded_directory"])
    manifest_path = funded / "FUNDED_OUTPUT_MANIFEST.json"
    manifest = json_at(manifest_path)
    if digest(manifest_path) != status["funded_manifest_sha256"] or any(
        digest(funded / k) != h for k, h in manifest["files"].items()
    ):
        raise ValueError("FUNDED_MANIFEST_DRIFT")
    clock = HoldingClock(ExecutionCalendar(MarketClock("2020-01-01", "2025-02-01")))
    registry_id = json_at(Path(seal["v1_results"]) / "EXPERIMENT_REGISTRY.json")["identity"]
    account = checkpoint(
        Path(seal["status_path"]).parent / "states" / (LAST + ".json.gz"),
        {
            "registry": registry_id,
            "cache": cache.manifest["identity"],
            "first": FIRST,
            "last": LAST,
            "cases": [f"{i}_{r}" for i in IDS for r in MODES],
            "variant_registry": status["registry"],
        },
    )
    return funded, status, cache, clock, account


def extract(destination: Path, fixture: bool = False) -> None:
    started = time.monotonic()
    seal = json_at(DEFAULT / "R01_INPUT_SEAL.json")
    seal_check(seal)
    funded, status, cache, clock, accounts = inputs(seal)
    opp = opportunities(cache, clock)
    legs = validated_legs(funded, opp)
    first, last = seal["protocol"]["source_fixture"]
    if fixture:
        legs = select(legs, column(legs, "date").between(first, last))
        if not len(legs) or len(column(legs, "regime").unique()) != 3:
            raise ValueError("EMPTY_R01_VALIDATION_FIXTURE")
    prices, market_returns, sources = raw_points(legs, fixture)
    cohort, tickets = reconstruction(legs, prices, clock)
    if fixture:
        publish(
            destination,
            {
                "status": "PASS",
                "formation_window": [first, last],
                "source_lookup": "Sealed minute panels at actual entry and exit markers",
                "cohorts": len(cohort),
                "exit_legs": len(legs),
                "gross_by_regime": {
                    regime: sum_d(
                        column(select(cohort, column(cohort, "regime") == regime), "gross")
                    )
                    for regime in MODES
                },
                "seconds": time.monotonic() - started,
                "peak_RSS_bytes": peak_memory_bytes(),
            },
        )
        return
    source_hashes = {r["path"]: r["sha256"] for r in sources}
    if source_hashes != {r["path"]: r["sha256"] for r in status["source_months"]}:
        raise ValueError("R01_RAW_PROJECTION_SCOPE")
    tickets = pd.concat([tickets, pd.DataFrame([r for a in accounts.values() for r in extras(a)])])
    add_causal_rank(cohort, cache, clock)
    summary = {
        r["regime"]: r for r in csv_at(funded / "V3_ALL54_SUMMARY.csv") if r["strategy_id"] == "R01"
    }
    reasons = [r for r in csv_at(funded / "V3_EXIT_REASONS.csv") if r["strategy_id"] == "R01"]
    daily = pd.read_parquet(funded / "DAILY_NAV.parquet", filters=[("strategy_id", "==", "R01")])
    reconciliation = [
        financial_check(
            summary[m],
            select(daily, column(daily, "regime") == m),
            accounts[m],
            select(cohort, column(cohort, "regime") == m),
            select(tickets, column(tickets, "regime") == m),
            [r for r in reasons if r["regime"] == m],
        )
        for m in MODES
    ]
    destination.mkdir(exist_ok=False, parents=True)
    csv_write(destination / "R01_RECONCILIATION.csv", reconciliation)
    print("PASS", len(opp), len(cohort), len(tickets), flush=True)
    write_analysis(
        destination,
        seal,
        status,
        funded,
        summary,
        reasons,
        accounts,
        opp,
        cohort,
        tickets,
        daily,
        market_returns,
    )
    publish(
        destination / "EXTRACTION_RECEIPT.json",
        {
            "status": "PASS",
            "input_seal_sha256": digest(DEFAULT / "R01_INPUT_SEAL.json"),
            "scans": len(sources),
            "source_hashes": source_hashes,
            "opportunities": len(opp),
            "closed_cohorts": len(cohort),
            "physical_orders": len(tickets),
            "funded_replays": 0,
            "seconds": time.monotonic() - started,
            "peak_RSS_bytes": peak_memory_bytes(),
        },
    )


def write_analysis(
    destination: Path,
    seal: dict,
    status: dict,
    funded: Path,
    summary: dict,
    reasons: list[dict],
    accounts: dict[str, DynamicLedger],
    opp: pd.DataFrame,
    cohort: pd.DataFrame,
    tickets: pd.DataFrame,
    daily: pd.DataFrame,
    market_returns: pd.DataFrame,
) -> None:
    annual = csv_at(funded / "V3_ANNUAL_CAUSAL_DIAGNOSTICS.csv")
    archived = [r for r in annual if r["strategy_id"] == "R01"]
    raw, comparison, matches = comparisons(opp, cohort, summary)
    csv_write(destination / "R01_REGIME_DIVERGENCE.csv", comparison)
    matches.to_csv(destination / "R01_OPPORTUNITY_MATCH.csv", index=False)
    raw.to_csv(destination / "R01_RECONSTRUCTED_COHORTS.csv", index=False)
    tables = attribution(raw, tickets, daily, market_returns, archived, reasons, summary)
    csv_write(destination / "R01_CONCENTRATION_AND_ATTRIBUTION.csv", tables)
    offline = Path(seal["status_path"]).parent / "offline_diagnostic"
    receipt = json_at(offline / "POST_EXIT_RECEIPT.json")
    source = offline / "V3_POST_EXIT_EXTENSION.csv"
    if (
        receipt["output_sha256"] != digest(source)
        or receipt["funded_manifest_sha256"] != status["funded_manifest_sha256"]
    ):
        raise ValueError("R01_OFFLINE_SOURCE_DRIFT")
    fragility = post_exit_cost(tickets, summary, csv_at(source))
    csv_write(destination / "R01_POST_EXIT_AND_COST_DIAGNOSTICS.csv", fragility)
    write_events(destination, accounts)
    fixed_references(destination, seal)


def comparisons(
    opp: pd.DataFrame,
    c: pd.DataFrame,
    summary: dict,
) -> tuple[pd.DataFrame, list[dict], pd.DataFrame]:
    m = opp.copy()
    cols = [
        "entry",
        "last_exit",
        "entry_qty",
        "entry_notional",
        "gross",
        "cause",
        "risk",
        "scheduled_minutes",
        "commission",
        "spread",
        "impact",
    ]
    for regime in MODES:
        filled = select(c, column(c, "regime") == regime)
        m = m.merge(
            table(filled[[*KEY, *cols]]).rename(columns={k: f"{regime}_{k}" for k in cols}),
            on=KEY,
            how="left",
            validate="one_to_one",
        )
        m[f"{regime}_filled"] = m[f"{regime}_entry"].notna()
    groups = m.apply(lambda r: "+".join(k for k in MODES if r[f"{k}_filled"]) or "NONE", axis=1)
    m["membership"] = groups
    c = c.merge(m[[*KEY, "membership"]], on=KEY, validate="many_to_one")
    rows = []
    for group, g in m.groupby("membership"):
        for regime in MODES:
            b = select(c, (column(c, "membership") == group) & (column(c, "regime") == regime))
            rows.append(
                {
                    "view": "three_way_membership",
                    "membership": group,
                    "regime": regime,
                    "opportunities": len(g),
                    "closed_cohorts": len(b),
                    "gross_price_USD": column(b, "gross").sum(),
                    "price_net_before_actions_carry_USD": column(
                        b, "net_before_actions_carry"
                    ).sum(),
                    "risk_closed": int(column(b, "risk").sum()),
                }
            )
    for regime in MODES:
        b = select(c, column(c, "regime") == regime)
        s = summary[regime]
        dup, cool, cutoff = map(
            int, (s["duplicate_suppression"], s["cooldown_rejections"], s["max_age_cutoff"])
        )
        if len(b) + dup + cool + cutoff != len(opp):
            raise ValueError("R01_REJECTION_CENSUS")
        rows.append(
            {
                "view": "regime_census",
                "regime": regime,
                "opportunities": len(opp),
                "closed_cohorts": len(b),
                "rejected_active_same_side": dup,
                "rejected_cooldown": cool,
                "rejected_max_age_cutoff": cutoff,
                "risk_closed": int(column(b, "risk").sum()),
                "risk_before_maximum_fill": int(
                    (column(b, "risk") & column(b, "before_maximum")).sum()
                ),
                "name_cap_check_count": s["name_breach_decisions"],
                "vintage_cap_check_count": s["vintage_breach_decisions"],
                "gross_per_1M_turnover_USD": s["gross_edge_per_1M_turnover_USD"],
                "net_per_1M_turnover_USD": s["net_per_1M_turnover_USD"],
                "net_per_1M_gross_RTH_dollar_years_USD": s["net_per_1M_RTH_gross_dollar_years_USD"],
            }
        )
    for comparator in MODES[1:]:
        a, b = (select(c, column(c, "regime") == k).set_index(KEY) for k in (MODES[0], comparator))
        ids = a.index.intersection(b.index)
        x, y = table(a.loc[ids]), table(b.loc[ids])
        q1, q2 = column(x, "entry_qty"), column(y, "entry_qty")
        qmean = (q1 + q2).map(lambda q: D(int(q)) / 2)
        move = (
            column(x, "exit_raw_per_entry_share")
            - column(x, "entry_raw")
            + column(y, "exit_raw_per_entry_share")
            - column(y, "entry_raw")
        ) / 2
        qty = sum_d((q1 - q2) * move)
        entry = sum_d(-qmean * (column(x, "entry_raw") - column(y, "entry_raw")))
        exit_ = sum_d(
            qmean * (column(x, "exit_raw_per_entry_share") - column(y, "exit_raw_per_entry_share"))
        )
        shared = sum_d(column(x, "gross")) - sum_d(column(y, "gross"))
        near(qty + entry + exit_, shared, "SHARED_OPPORTUNITY_BRIDGE", GROSS_TOL)
        only_a = sum_d(column(table(a.loc[a.index.difference(b.index)]), "gross"))
        only_b = sum_d(column(table(b.loc[b.index.difference(a.index)]), "gross"))
        total = sum_d(column(a, "gross")) - sum_d(column(b, "gross"))
        near(shared + only_a - only_b, total, "OPPORTUNITY_GROSS_BRIDGE", GROSS_TOL)
        rows.append(
            {
                "view": "H85_minus_comparator",
                "regime": comparator,
                "opportunities": len(ids),
                "only_H85": len(a) - len(ids),
                "only_comparator": len(b) - len(ids),
                "H85_only_gross_USD": only_a,
                "comparator_only_gross_USD": only_b,
                "total_gross_delta_USD": total,
                "shared_gross_delta_USD": shared,
                "shared_qty_component_USD": qty,
                "shared_entry_price_component_USD": entry,
                "shared_exit_price_component_USD": exit_,
                "shared_quantity_diff": int((q1 != q2).sum()),
                "shared_first_entry_time_diff": int(
                    (column(x, "entry") != column(y, "entry")).sum()
                ),
                "shared_last_exit_time_diff": int(
                    (column(x, "last_exit") != column(y, "last_exit")).sum()
                ),
                "shared_gross_return_H85": column(x, "gross").sum()
                / column(x, "entry_notional").sum(),
                "shared_gross_return_comparator": column(y, "gross").sum()
                / column(y, "entry_notional").sum(),
                "shared_direct_cost_H85_USD": column(x, "gross").sum()
                - column(x, "net_before_actions_carry").sum(),
                "shared_direct_cost_comparator_USD": column(y, "gross").sum()
                - column(y, "net_before_actions_carry").sum(),
            }
        )
        states = np.char.add(
            np.where(column(x, "risk"), "RISK/", "POLICY/"),
            np.where(column(y, "risk"), "RISK", "POLICY"),
        )
        for label in sorted(set(states)):
            p, q = table(x.loc[states == label]), table(y.loc[states == label])
            rows.append(
                {
                    "view": "shared_exit_type_H85_vs_comparator",
                    "regime": comparator,
                    "membership": label,
                    "opportunities": len(p),
                    "shared_gross_delta_USD": column(p, "gross").sum() - column(q, "gross").sum(),
                    "shared_gross_return_H85": column(p, "gross").sum()
                    / column(p, "entry_notional").sum(),
                    "shared_gross_return_comparator": column(q, "gross").sum()
                    / column(q, "entry_notional").sum(),
                    "shared_last_exit_time_diff": int(
                        (column(p, "last_exit") != column(q, "last_exit")).sum()
                    ),
                    "median_hold_H85": float(
                        np.median(column(p, "scheduled_minutes").to_numpy(int))
                    ),
                    "median_hold_comparator": float(
                        np.median(column(q, "scheduled_minutes").to_numpy(int))
                    ),
                }
            )
    return c, rows, m


def distribution(values: pd.Series) -> dict:
    x = values.astype(float)
    winners, losses = x.where(x > 0).dropna(), x.where(x < 0).dropna()
    return {
        "count": len(x),
        "winners": len(winners),
        "losers": len(losses),
        "flat": int(x.eq(0).sum()),
        "hit_rate": len(winners) / len(x),
        "sum_winners_USD": winners.sum(),
        "sum_losers_USD": losses.sum(),
        "mean_winner_USD": winners.mean(),
        "mean_loser_USD": losses.mean(),
        "median_winner_USD": winners.median(),
        "median_loser_USD": losses.median(),
        "payoff_ratio": winners.mean() / -losses.mean() if len(winners) and len(losses) else None,
        "profit_factor": winners.sum() / -losses.sum() if len(losses) else None,
        **{f"p{p}_USD": x.quantile(p / 100) for p in (5, 25, 50, 75, 95)},
    }


def calendar_views(g: pd.DataFrame, proxy: pd.Series) -> list[dict]:
    x = g.copy()
    x["portfolio_daily_return"] = column(x, "nav") / column(x, "nav").shift(fill_value=100000) - 1
    x["before"] = column(x, "nav").shift(fill_value=100000)
    x["no_exposure"] = column(x, "gross_dollar_minutes").eq(0)
    x["matched_proxy"] = column(x, "date").map(proxy.to_dict())
    date = pd.to_datetime(column(x, "date"))
    x["quarter"] = date.dt.to_period("Q").astype(str)
    x["month"] = date.dt.strftime("%Y-%m")
    x["year"] = date.dt.strftime("%Y")
    x["half"] = np.where(date.dt.year <= 2022, "2021-22", "2023-24")
    out = []
    for axis in ("quarter", "month", "year", "half"):
        for label, g in x.groupby(axis):
            out.append(
                {
                    "view": "daily_NAV",
                    "axis": axis,
                    "label": label,
                    "count": len(g),
                    "account_NAV_change_USD": column(g, "nav").iloc[-1]
                    - column(g, "before").iloc[0],
                    "return": column(g, "nav").iloc[-1] / column(g, "before").iloc[0] - 1,
                    "no_exposure_session_fraction": column(g, "no_exposure").mean(),
                    "gross_NAV_fraction_RTH": column(g, "gross_NAV_minutes").sum()
                    / column(g, "RTH_minutes").sum(),
                    "cash_NAV_fraction_RTH": column(g, "spendable_cash_NAV_minutes").sum()
                    / column(g, "RTH_minutes").sum(),
                }
            )
    pair = table(x[["matched_proxy", "portfolio_daily_return"]]).dropna()
    cov = pair.cov()
    out.append(
        {
            "view": "contemporaneous_equal_weight_survivor_proxy",
            "count": len(pair),
            "beta": float(cov.to_numpy(float)[0, 1] / cov.to_numpy(float)[0, 0]),
            "correlation": pair.corr().iloc[0, 1],
            "no_exposure_session_fraction": column(x, "no_exposure").mean(),
            "cash_NAV_fraction_RTH": column(x, "spendable_cash_NAV_minutes").sum()
            / column(x, "RTH_minutes").sum(),
        }
    )
    return out


def attribution(
    c: pd.DataFrame,
    t: pd.DataFrame,
    daily: pd.DataFrame,
    returns: pd.DataFrame,
    archived: list[dict],
    reasons: list[dict],
    summary: dict,
) -> list[dict]:
    c = c.copy()
    c["entry_month"] = column(c, "entry_date").str[:7]
    c["ticker_side"] = column(c, "symbol") + "/" + column(c, "side").map({1: "LONG", -1: "SHORT"})
    c["origin_ET"] = stamp(column(c, "origin")).strftime("%H:%M")
    c["monitor_rank_band"] = pd.cut(
        column(c, "last_supported_monitor_rank"), [0, 2, 4, 20], labels=["1-2", "3-4", "5-20"]
    )
    c["exit_month"] = column(c, "exit_date").str[:7]
    c["exit_quarter"] = pd.to_datetime(column(c, "exit_date")).dt.to_period("Q").astype(str)
    c["weekday"] = pd.to_datetime(column(c, "entry_date")).dt.day_name()
    c["hold_bucket"] = pd.cut(column(c, "scheduled_minutes"), [-1, 390, 1170, 1950, 99999])
    c["pre_entry_vol_bucket"] = pd.cut(column(c, "prior_v20"), [-1, 0.01, 0.02, 0.03, 100])
    c["exit_score_bucket"] = pd.cut(column(c, "exit_strength"), [-np.inf, -1, 0, 1, np.inf])
    c["overnight"] = np.where(column(c, "overnight"), "MULTI_SESSION", "SAME_SESSION")
    c["source_gap"] = np.where(column(c, "exit_gap"), "DEFERRED", "NO_SAVED_EXIT_GAP")
    past_peers = {}
    for symbol in SYMBOLS:
        peers = returns.drop(columns=symbol)
        past_peers[symbol] = peers.mean(axis=1).where(peers.notna().sum(axis=1) >= 11).shift(1)
    c["past_peer_return_sign"] = [
        "UNAVAILABLE" if not np.isfinite(value) else ("UP" if value > 0 else "DOWN_OR_FLAT")
        for row in as_rows(c)
        for value in [past_peers[row.symbol].get(row.entry_date, np.nan)]
    ]
    for regime in MODES:
        for axis in ("attribution_year", "entry_year", "ticker", "side", "slot", "overnight"):
            group = [r for r in archived if r["axis"] == axis and r["regime"] == regime]
            for field, reference in (
                ("gross_price", "gross_signed_price_PnL_USD"),
                ("actions", "gross_action_value_USD"),
                ("net", "net_PnL_USD"),
            ):
                near(
                    sum((D(r[field]) for r in group), D(0)),
                    D(summary[regime][reference]),
                    f"R01_FROZEN_ATTRIBUTION_{axis}_{field}",
                )
    rows: list[dict] = []
    for regime, g in c.groupby("regime"):
        src = summary[regime]
        for field, view in (
            ("gross", "gross_raw_price"),
            ("net_before_actions_carry", "after_execution_before_actions_and_carry"),
        ):
            rows.append({"regime": regime, "view": view, **distribution(column(g, field))})
            for k in (1, 5, 10, 20):
                for tail, subset in (
                    (
                        "positive",
                        select(g, column(g, field) > 0).sort_values(field, ascending=False).head(k),
                    ),
                    ("negative", select(g, column(g, field) < 0).sort_values(field).head(k)),
                ):
                    removed = sum_d(column(subset, field))
                    remaining = sum_d(column(g, field)) - removed
                    rows.append(
                        {
                            "regime": regime,
                            "view": "tail_omission_arithmetic",
                            "axis": view,
                            "label": tail,
                            "count": len(subset),
                            "removed_USD": removed,
                            "remaining_USD": remaining,
                            "changes_sign": (remaining > 0) != (column(g, field).sum() > 0),
                            "gross_plus_actions_minus_cost_account_less_raw_tail_USD": D(
                                src["net_PnL_USD"]
                            )
                            - removed
                            if field == "gross"
                            else None,
                        }
                    )
        for axis in (
            "side",
            "symbol",
            "ticker_side",
            "origin_ET",
            "monitor_rank_band",
            "entry_month",
            "exit_month",
            "exit_quarter",
            "weekday",
            "rank",
            "score_decile",
            "exit_score_bucket",
            "hold_bucket",
            "pre_entry_vol_bucket",
            "past_peer_return_sign",
            "cause",
            "overnight",
            "source_gap",
            "first_fill_delay",
        ):
            for label, b in g.groupby(axis, dropna=False, observed=True):
                notional = column(b, "entry_notional").sum()
                turnover = column(b, "raw_turnover").sum()
                rows.append(
                    {
                        "regime": regime,
                        "view": "reconstructed_ordinary_share",
                        "axis": axis,
                        "label": str(label),
                        "count": len(b),
                        "support": "LOW_SUPPORT" if len(b) < 20 else "AT_LEAST_20_COHORTS",
                        "gross_price_USD": column(b, "gross").sum(),
                        "raw_turnover_USD": turnover,
                        "gross_per_1M_raw_turnover_USD": column(b, "gross").sum()
                        * 1_000_000
                        / turnover,
                        "gross_over_entry_notional": column(b, "gross").sum() / notional,
                        "direct_execution_cost_bps_raw_turnover": (
                            (
                                column(b, "commission").sum()
                                + column(b, "spread").sum()
                                + column(b, "impact").sum()
                            )
                            * 10000
                            / turnover
                        ),
                        "net_before_actions_carry_USD": column(b, "net_before_actions_carry").sum(),
                        "commission_USD": column(b, "commission").sum(),
                        "spread_USD": column(b, "spread").sum(),
                        "impact_USD": column(b, "impact").sum(),
                        "risk_closes": int(column(b, "risk").sum()),
                        "median_scheduled_minutes": column(b, "scheduled_minutes").median(),
                        "exact_cohort_net_support": "NOT_IDENTIFIABLE_FROM_AVAILABLE_EXPORTS",
                    }
                )
        per_day = select(daily, column(daily, "regime") == regime)
        proxy = returns.mean(axis=1).where(returns.notna().sum(axis=1) >= 12)
        rows.extend({"regime": regime, **row} for row in calendar_views(per_day, proxy))
        tick = t[column(t, "regime") == regime]
        rows.append(
            {
                "regime": regime,
                "view": "account_totals",
                "count": len(g),
                "gross_price_USD": src["gross_signed_price_PnL_USD"],
                "action_value_USD": src["gross_action_value_USD"],
                "net_USD": src["net_PnL_USD"],
                "exact_cohort_net_support": "NOT_IDENTIFIABLE_FROM_AVAILABLE_EXPORTS",
                "gross_per_1M_RTH_dollar_years_USD": src["gross_per_1M_RTH_gross_dollar_years_USD"],
                "net_per_1M_RTH_dollar_years_USD": src["net_per_1M_RTH_gross_dollar_years_USD"],
                "orders_per_cohort": len(tick) / len(g),
            }
        )
    for r in archived:
        if r["axis"] not in {"rejection", "account_year"}:
            rows.append(
                {
                    "regime": r["regime"],
                    "view": "exact_frozen_cohort_aggregate",
                    "axis": r["axis"],
                    "label": SYMBOLS[int(r["label"])] if r["axis"] == "ticker" else r["label"],
                    "count": r["completed"],
                    "gross_price_USD": r["gross_price"],
                    "action_value_USD": r["actions"],
                    "net_USD": r["net"],
                    "combined_cohort_cost_USD": r["cohort_cost"],
                    "borrow_USD": r["cohort_borrow"],
                }
            )
    for r in reasons:
        g = select(c, (column(c, "regime") == r["regime"]) & (column(c, "cause") == r["cause"]))
        entry_capital_years = sum(
            (
                n * int(m)
                for n, m in zip(
                    column(g, "entry_notional"), column(g, "scheduled_minutes"), strict=True
                )
            ),
            D(0),
        ) / (252 * 390)
        rows.append(
            {
                "regime": r["regime"],
                "view": "exact_frozen_exit_cause",
                "axis": "cause",
                "label": r["cause"],
                "count": r["cohorts"],
                "gross_price_USD": r["gross_price"],
                "action_value_USD": r["action_value"],
                "net_USD": r["net"],
                "median_scheduled_minutes": r["p50_scheduled_minutes"],
                "net_per_1M_entry_notional_proxy_year_USD": D(r["net"])
                * 1_000_000
                / entry_capital_years,
                "support": "LOW_SUPPORT" if int(r["cohorts"]) < 20 else "AT_LEAST_20_COHORTS",
            }
        )
    return rows


def post_exit_cost(tickets: pd.DataFrame, summary: dict, offline: list[dict]) -> list[dict]:
    rows = []
    for r in offline:
        if r["strategy_id"] == "R01" and r["axis"] in ("all", "entry_strength", "side", "year"):
            rows.append({"view": "SEALED_UNFUNDED_LATER_MARK", **r})
    for regime, s in summary.items():
        _, cost = dollars(s)
        turnover = D(s["executed_turnover_USD"])
        net = D(s["net_PnL_USD"])
        t = select(tickets, column(tickets, "regime") == regime)
        concession = D(s["assumed_spread_USD"]) + D(s["assumed_impact_USD"])
        rows.append(
            {
                "view": "physical_ticket_reconstruction",
                "regime": regime,
                "count": len(t),
                "commission_USD": s["commission_USD"],
                "spread_USD": s["assumed_spread_USD"],
                "impact_USD": s["assumed_impact_USD"],
                "borrow_USD": s["borrow_USD"],
                "funding_USD": s["funding_USD"],
                "cost_per_order_USD": cost / len(t),
                "signed_adverse_arrival_USD": s["signed_arrival_USD"],
                "absolute_arrival_USD_not_cost": s["absolute_arrival_USD"],
                "fee_at_minimum": int(column(t, "fee").eq(1).sum()),
                "fee_at_minimum_fraction": column(t, "fee").eq(1).mean(),
                "shares_below_or_at_200": int(column(t, "quantity").abs().le(200).sum()),
                "cost_per_turnover_bps": cost * 10000 / turnover,
                "break_even_cost_per_turnover_bps": (
                    D(s["gross_signed_price_PnL_USD"]) + D(s["gross_action_value_USD"])
                )
                * 10000
                / turnover,
                **{
                    f"p{q}_ticket_USD": column(t, "turnover").astype(float).quantile(q / 100)
                    for q in (25, 50, 75)
                },
            }
        )
        for k in (D(".5"), D(1), D("1.5")):
            rows.append(
                {
                    "view": "same_holdings_cost_arithmetic",
                    "regime": regime,
                    "spread_impact_multiplier": k,
                    "net_USD": net + (1 - k) * concession,
                    "status": "UNFUNDED_ARITHMETIC_NO_REOPTIMIZATION",
                }
            )
    return rows


def write_events(destination: Path, accounts: dict[str, DynamicLedger]) -> None:
    result = {}
    for regime, a in accounts.items():
        result[regime] = {
            "events": a.stats.counts,
            "rejects": a.rejected,
            "causes": a.causes,
            "terminal_claims": [
                dict(event=k[0], lot=k[1], USD=v, due=t) for k, (v, t) in a.claims.items()
            ],
            "bounded_event_examples": a.stats.anomalies,
            "bounded_action_examples": a.ledger_examples,
        }
    publish(destination / "R01_COMMITTED_EVENT_EVIDENCE.json", result)


def fixed_references(destination: Path, seal: dict) -> None:
    v1 = Path(seal["v1_results"])
    v2 = Path(seal["v2_results"])
    v1_r = next(r for r in csv_at(v1 / "SUMMARY_18_STRATEGIES.csv") if r["strategy_id"] == "R01")
    rows = [{"study": "V1", **v1_r}]
    rows.extend(
        {"study": "V2", **r}
        for file in ("HEADROOM_RESULTS.csv", "HORIZON_RESULTS.csv")
        for r in csv_at(v2 / file)
        if r["strategy_id"] == "R01"
    )
    csv_write(destination / "R01_FIXED_REFERENCES.csv", rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--fixture", action="store_true")
    args = parser.parse_args()
    extract(args.destination, args.fixture)


if __name__ == "__main__":
    main()
