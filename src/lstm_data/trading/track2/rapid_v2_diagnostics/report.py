"""Fail-closed case summaries, exact V1 reconciliation and compact tables."""

import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from ..rapid_v1.paths import digest, publish
from ..rapid_v1.reporting import metrics
from ..rapid_v1.strategies import IDS
from .book import ZERO, D, Ledger
from .engine import Batch

USD_TOL = D("0.0000001")
REL_TOL = 1e-12
GROSS_BASIS = "RAW_OPEN_PRICE_PNL_BEFORE_MODELED_CONCESSION_AND_COMMISSION"


def weighted_median(counter: Counter) -> float | None:
    total = counter.total()
    if not total:
        return None
    wanted = ((total - 1) // 2, total // 2)
    found = []
    cumulative = 0
    for value, count in sorted(counter.items()):
        cumulative += count
        while len(found) < 2 and cumulative > wanted[len(found)]:
            found.append(value)
    return sum(found) / 2


def csv_write(path: Path, rows: list[dict]) -> None:
    columns = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def summation(a: Ledger, name: str) -> D:
    return a.totals.get(name, ZERO)


def summarize(engine: Batch, a: Ledger, keep_terminal: bool = True) -> dict:
    if keep_terminal:
        engine.final_cohorts(a)
    rows = engine.daily_rows[a.arm]
    case = engine.case_by_key[a.arm]
    m = metrics(rows)
    nav = a.nav()
    hold = engine.account_holds.get(a.arm, [])
    if a.pending or any(a.quantity) or a.risk_hold or a.unpriced_special or a.nav_incomplete:
        hold = [*hold, "UNRESOLVED_TERMINAL_EXPOSURE_ORDER_OR_PRICE"]
    c = a.totals
    net = summation(a, "net")
    cost = a.commission + a.friction + a.borrow_paid + a.funding_paid
    gross, actions = summation(a, "gross_price"), summation(a, "actions")
    if (
        nav is not None
        and nav.is_finite()
        and (
            abs(net - (nav - a.initial)) > USD_TOL
            or abs(gross + actions - cost - net) > USD_TOL
            or abs(a.stats.spread + a.stats.impact - a.friction) > USD_TOL
        )
    ):
        raise ValueError("ACCOUNT_OR_ATTRIBUTION_DRIFT:" + a.arm)
    notional = summation(a, "turnover")
    filled = int(summation(a, "cohorts"))
    duration = sum(r["RTH_minutes"] for r in rows)
    exposure = sum(r["gross_dollar_minutes"] for r in rows) / (252 * 390)
    mean_nav = float(np.mean([float(r["nav"]) for r in rows if r["nav"] is not None]))
    status = (
        "HOLD" if hold or m["status"] != "COMPLETE" else ("COMPLETE" if filled else "NO_TRADES")
    )
    if status == "HOLD":
        m = {}
    return {
        "strategy_id": case.strategy,
        "mode": case.mode,
        "variant": case.variant,
        "headroom": case.headroom,
        "nominal_horizon": case.horizon,
        "horizon_unit": case.unit,
        "status": status,
        "hold_reasons": "|".join(hold),
        "sessions": len(rows),
        "cohorts": filled,
        "closed_cohorts": summation(a, "completed"),
        "early_exits": summation(a, "early"),
        "early_rate": float(summation(a, "early")) / filled if filled else None,
        "scheduled_final_exits": summation(a, "scheduled"),
        "risk_final_exits": summation(a, "risk_final"),
        "cohorts_with_risk_fill": summation(a, "any_forced"),
        "risk_external_orders": summation(a, "forced_external_orders"),
        "risk_order_notional_USD": summation(a, "forced_external_fill_notional"),
        "risk_attributed_notional_USD": summation(a, "forced_attributed_notional"),
        "external_orders": summation(a, "physical_orders"),
        "external_fills": summation(a, "external_fills"),
        "executed_turnover_USD": notional,
        "raw_open_turnover_USD": summation(a, "raw_turnover"),
        "turnover_over_mean_NAV": float(notional) / mean_nav if mean_nav > 0 else None,
        "median_wall_minutes": weighted_median(a.durations),
        "median_scheduled_minutes": weighted_median(a.scheduled_durations),
        "mean_wall_minutes": (
            sum(k * v for k, v in a.durations.items()) / a.durations.total()
            if a.durations
            else None
        ),
        "mean_RTH_marked_gross_fraction": sum(r["gross_NAV_minutes"] for r in rows) / duration,
        "mean_RTH_spendable_cash_fraction": (
            sum(r["spendable_cash_NAV_minutes"] for r in rows) / duration
        ),
        "mean_close_reserved_virtual_gross_fraction": float(
            np.mean(
                [float(r["virtual_gross"] / r["nav"]) for r in rows if r["nav"] and r["nav"] > 0]
            )
        ),
        "RTH_gross_dollar_years": exposure,
        "gross_signed_price_PnL_USD": gross,
        "gross_winners_USD": summation(a, "gross_winners"),
        "gross_losers_USD": summation(a, "gross_losers"),
        "gross_action_value_USD": actions,
        "commission_USD": a.commission,
        "assumed_spread_USD": a.stats.spread,
        "assumed_impact_USD": a.stats.impact,
        "borrow_USD": a.borrow_paid,
        "funding_USD": a.funding_paid,
        "total_cost_USD": cost,
        "gross_edge_per_1M_turnover_USD": gross / notional * 1_000_000 if notional else None,
        "cost_per_1M_turnover_USD": cost / notional * 1_000_000 if notional else None,
        "gross_per_cohort_USD": gross / filled if filled else None,
        "gross_per_1M_RTH_gross_dollar_years_USD": (
            float(gross) * 1_000_000 / exposure if exposure else None
        ),
        "net_per_1M_RTH_gross_dollar_years_USD": (
            float(net) * 1_000_000 / exposure if exposure and status != "HOLD" else None
        ),
        "net_PnL_USD": net if status != "HOLD" else None,
        "final_NAV_USD": m.get("final_NAV_USD"),
        "Sharpe_252_zero_rf": m.get("Sharpe_252_zero_rf"),
        "CAGR": m.get("CAGR"),
        "max_drawdown": m.get("max_drawdown"),
        "initial_cash_USD": a.initial,
        "terminal_cash_USD": a.cash,
        "terminal_restricted_USD": a.restricted(),
        "terminal_claims_USD": a.claim_total(),
        "terminal_pending": len(a.pending),
        "terminal_stock_symbols": int(np.count_nonzero(a.quantity)),
        "max_ledger_residual_USD": a.maximum_residual,
        "candidate_intents": c.get("candidate_intents", ZERO),
        "scheduled_name_opportunities": c.get("opportunities", ZERO),
        "duplicate_suppression": a.rejected.get("DUPLICATE_ACTIVE_SAME_SIGN", 0),
        "order_budget_suppression": a.rejected.get("ENTRY_ORDER_CAP", 0),
        "retail_minimum_notional": a.rejected.get("RETAIL_MIN_NOTIONAL", 0),
        "calendar_cutoff": a.rejected.get("CALENDAR_TERMINAL_CUTOFF", 0),
        "future_slot_unavailable": a.rejected.get("FUTURE_SESSION_SLOT_UNAVAILABLE", 0),
        "missing_bar_attempts": a.stats.counts["V5_PENDING_MISSING_BAR"],
        "simulated_entry_expiries": a.stats.counts["EXPIRED_UNFILLED_BY_V5_SIMULATION"],
        "gross_basis": GROSS_BASIS,
        "concession_embedded_in_executed_cash": True,
    }


def baseline_check(engine: Batch, rows: list[dict], expected: Path) -> dict:
    """Check every baseline account and every daily NAV against the immutable V1 export."""
    max_difference = 0.0
    max_day = 0.0
    counts = Counter()
    for row in rows:
        if row["variant"] != "H100":
            continue
        sid = row["strategy_id"]
        old = json.loads((expected / sid / "summary.json").read_text())
        old_daily = pd.read_parquet(expected / sid / "daily_nav.parquet")
        current = engine.daily_rows[sid + "_H100"]
        if list(old_daily["date"]) != [x["date"] for x in current]:
            raise ValueError("BASELINE_CALENDAR_DRIFT:" + sid)
        for field in (
            "nav",
            "cash",
            "restricted",
            "claims",
            "special",
            "commission",
            "friction",
            "borrow",
            "funding",
            "physical_value",
            "virtual_gross",
        ):
            actual = np.asarray([float(x[field]) for x in current])
            diff = float(np.max(np.abs(actual - old_daily[field].to_numpy(float))))
            max_day = max(max_day, diff)
            if not np.isfinite(diff) or diff > float(USD_TOL):
                raise ValueError(f"BASELINE_DAILY_DRIFT:{sid}:{field}:{diff}")
        pairs = {
            "cohorts": "cohorts_filled",
            "external_orders": "physical_external_orders",
            "external_fills": "physical_external_fill_events",
            "net_PnL_USD": "net_PnL_USD",
            "gross_signed_price_PnL_USD": "gross_signed_price_PnL_USD",
            "gross_action_value_USD": "gross_action_value_USD",
            "commission_USD": "commissions_USD",
            "assumed_spread_USD": "print_slippage_USD",
            "assumed_impact_USD": "impact_USD",
            "borrow_USD": "borrow_USD",
            "funding_USD": "funding_USD",
            "terminal_claims_USD": "terminal_claims_USD",
            "candidate_intents": "candidate_intents",
        }
        for lhs, rhs in pairs.items():
            error = abs(float(row[lhs]) - float(old[rhs]))
            max_difference = max(max_difference, error)
            if error > float(USD_TOL) or not np.isfinite(error):
                raise ValueError(f"BASELINE_VECTOR_DRIFT:{sid}:{lhs}:{error}")
        for field in ("Sharpe_252_zero_rf", "CAGR", "max_drawdown"):
            if old[field] is None and row[field] is None:
                continue
            if abs(float(row[field]) - float(old[field])) > REL_TOL:
                raise ValueError(f"BASELINE_RETURN_METRIC_DRIFT:{sid}:{field}")
        old_trades = pd.read_parquet(expected / sid / "trades.parquet")
        early = (
            int((old_trades["exit_at"] < old_trades["endpoint"]).sum()) if len(old_trades) else 0
        )
        if early != row["early_exits"]:
            raise ValueError("BASELINE_EARLY_EXIT_COUNT_DRIFT:" + sid)
        counts[row["mode"] + "_orders"] += int(row["external_orders"])
        counts[row["mode"] + "_early"] += early
    if sum(x["variant"] == "H100" for x in rows) != len(IDS):
        raise ValueError("BASELINE_CASE_CENSUS")
    return {
        "status": "PASS",
        "maximum_daily_USD_difference": max_day,
        "maximum_summary_difference": max_difference,
        "counts": dict(counts),
        "USD_tolerance": str(USD_TOL),
        "return_tolerance": REL_TOL,
        "V1_manifest_sha256": digest(expected / "manifest.json"),
    }


def friction(a: Ledger, summary: dict, source: Path) -> tuple[dict, list[dict]]:
    fills = pd.read_parquet(source / summary["strategy_id"] / "physical_orders.parquet")
    absq = fills["shares"].abs()
    reference = fills["raw_open"]
    executed = fills["external_price"]
    difference = fills["shares"] * (executed - reference)
    if not np.allclose(difference, fills["print_slippage"] + fills["impact"], atol=1e-8, rtol=0):
        raise ValueError("V1_PER_FILL_PRICE_DECOMPOSITION")
    groups = (
        fills.assign(q=absq, value=absq * executed)
        .groupby("order_id")
        .agg(
            shares=("q", "sum"),
            notional=("value", "sum"),
            fees=("commission", "sum"),
        )
    )
    n = len(groups)
    shares = np.asarray(groups["shares"], dtype=float)
    notionals = np.asarray(groups["notional"], dtype=float)
    expected = np.asarray(
        [
            float(max(D(1), D(".005") * D(int(q))).quantize(D(".01")))
            if a.population.startswith("RETAIL")
            else float(D(".002") * D(int(q)))
            for q in shares
        ]
    )
    if not np.allclose(groups["fees"], expected, atol=1e-8, rtol=0):
        raise ValueError("V1_ORDER_COMMISSION_MISMATCH")
    if n != summary["external_orders"]:
        raise ValueError("V1_PHYSICAL_ORDER_COUNT")
    turnover = float(summary["executed_turnover_USD"])
    concession = float(a.friction)
    price_impact_uncapped_tick = float((absq * reference * (fills["h"] + fills["j"])).sum())
    if int(summation(a, "arrival_covered_fills")) != len(fills):
        raise ValueError("V1_ARRIVAL_MARK_COVERAGE")
    record = {
        k: summary[k]
        for k in (
            "strategy_id",
            "mode",
            "external_orders",
            "external_fills",
            "executed_turnover_USD",
            "raw_open_turnover_USD",
            "gross_signed_price_PnL_USD",
            "gross_action_value_USD",
            "commission_USD",
            "assumed_spread_USD",
            "assumed_impact_USD",
            "borrow_USD",
            "funding_USD",
            "total_cost_USD",
            "net_PnL_USD",
            "gross_basis",
            "concession_embedded_in_executed_cash",
        )
    }
    edge = float(summary["gross_signed_price_PnL_USD"])
    record.update(
        {
            "median_order_abs_shares": float(np.median(shares)),
            "median_order_notional_USD": float(np.median(notionals)),
            "minimum_fee_binding_orders": int(
                ((groups["fees"] == 1) & (groups["shares"] * 0.005 < 1)).sum()
            ),
            "signed_arrival_drift_USD": summation(a, "signed_arrival_drift"),
            "absolute_arrival_drift_USD": summation(a, "absolute_arrival_drift"),
            "adverse_arrival_fills": summation(a, "adverse"),
            "favorable_arrival_fills": summation(a, "favorable"),
            "flat_arrival_fills": summation(a, "flat"),
            "adverse_tick_rounding_already_in_price_components_USD": (
                concession - price_impact_uncapped_tick
            ),
            "effective_per_roundtrip_bps": 20_000 * float(summary["total_cost_USD"]) / turnover,
            "paid_cost_per_1M_executed_turnover_USD": 1e6
            * float(summary["total_cost_USD"])
            / turnover,
            "cost_over_gross_edge_when_positive": float(summary["total_cost_USD"]) / edge
            if edge > 0
            else None,
            "modeled_zero_incremental_concession_same_path_USD": float(summary["net_PnL_USD"])
            + concession,
            "unknown_midquote": True,
            "double_count_audit": "NO_ARITHMETIC_DUPLICATION_FOUND",
            "shares_1_49_orders": int((groups["shares"] < 50).sum()),
            "shares_50_199_orders": int(
                ((groups["shares"] >= 50) & (groups["shares"] < 200)).sum()
            ),
            "shares_200_plus_orders": int((groups["shares"] >= 200).sum()),
            "notional_lt_2000_orders": int((groups["notional"] < 2000).sum()),
            "notional_2000_to_5000_orders": int(((notionals >= 2000) & (notionals < 5000)).sum()),
            "notional_5000_plus_orders": int((groups["notional"] >= 5000).sum()),
        }
    )
    bucket = []
    for key, values in sorted(a.breakdown.items()):
        if key.startswith("friction|"):
            _, ticker, window = key.split("|")
            bucket.append(
                {
                    "strategy_id": summary["strategy_id"],
                    "ticker_index": ticker,
                    "fill_ET_half_hour": window,
                    **values,
                }
            )
    return record, bucket


def emit(engine: Batch, out: Path, expected: Path) -> dict:
    rows = [summarize(engine, a) for a in engine.fast_accounts]
    baseline = baseline_check(engine, rows, expected)
    if len(rows) != 108 or len({(r["strategy_id"], r["variant"]) for r in rows}) != 108:
        raise ValueError("FULL_STUDY_AXIS_INCOMPLETE")
    csv_write(out / "HEADROOM_RESULTS.csv", [r for r in rows if r["variant"].startswith("H")])
    csv_write(out / "HORIZON_RESULTS.csv", [r for r in rows if r["variant"] not in ("H70", "H85")])
    attribution, annual, f, f_by, days, causes, rejected = [], [], [], [], [], [], []
    for a, row in zip(engine.fast_accounts, rows, strict=True):
        case = {"strategy_id": row["strategy_id"], "variant": row["variant"], "mode": row["mode"]}
        for key, b in sorted(a.breakdown.items()):
            if not key.startswith("friction|"):
                dimension, value = key.split("|")
                attribution.append(
                    {
                        **case,
                        "dimension": dimension,
                        "value": value,
                        "gross_basis": GROSS_BASIS,
                        **b,
                    }
                )
        last_nav = float(a.initial)
        daily = engine.daily_rows[a.arm]
        for year in sorted({d["date"][:4] for d in daily}):
            sub = [d for d in daily if d["date"].startswith(year)]
            year_costs = {
                field + "_USD": float(
                    sub[-1][field]
                    - next((d[field] for d in reversed(daily) if d["date"] < sub[0]["date"]), ZERO)
                )
                for field in ("commission", "friction", "borrow", "funding")
            }
            end = float(sub[-1]["nav"]) if sub[-1]["nav"] is not None else None
            annual.append(
                {
                    **case,
                    "year": year,
                    "status": row["status"],
                    "opening_NAV_USD": last_nav,
                    "ending_NAV_USD": end,
                    "net_NAV_change_USD": (
                        end - last_nav if end is not None and row["status"] != "HOLD" else None
                    ),
                    "return": (
                        end / last_nav - 1
                        if end is not None and last_nav > 0 and row["status"] != "HOLD"
                        else None
                    ),
                    "close_lot_gross_basis": GROSS_BASIS,
                    "closed_lot_gross_USD": a.breakdown.get("attribution_year|" + year, {}).get(
                        "gross_price", ZERO
                    ),
                    "closed_lot_actions_USD": a.breakdown.get("attribution_year|" + year, {}).get(
                        "actions", ZERO
                    ),
                    **year_costs,
                }
            )
            last_nav = end if end is not None else float("nan")
        days.extend(
            {**case, **{k: float(v) if isinstance(v, D) else v for k, v in d.items()}}
            for d in daily
        )
        causes.extend({**case, "cause": c, "cohort_count": n} for c, n in a.causes.items())
        rejected.extend(
            {**case, "reason": reason, "count": count} for reason, count in a.rejected.items()
        )
        if row["variant"] == "H100":
            record, bucket = friction(a, row, expected)
            f.append(record)
            f_by.extend(bucket)
    csv_write(out / "FRICTION_DECOMPOSITION.csv", f)
    csv_write(out / "ARRIVAL_BY_TICKER_AND_TIME.csv", f_by)
    csv_write(out / "ANNUAL_RESULTS.csv", annual)
    csv_write(out / "ANNUAL_AND_MECHANISM_TABLES.csv", attribution)
    csv_write(out / "RISK_CAUSES.csv", causes)
    csv_write(out / "ABSTENTIONS_AND_REJECTIONS.csv", rejected)
    pd.DataFrame(days).to_parquet(out / "DAILY_NAV.parquet", compression="zstd", index=False)
    publish(out / "BASELINE_PARITY.json", baseline)
    publish(
        out / "NO_TRADE_CONTEXT.json",
        {
            "initial_NAV_USD": 100000,
            "final_NAV_USD": 100000,
            "gross_PnL_USD": 0,
            "action_value_USD": 0,
            "net_PnL_USD": 0,
            "Sharpe": None,
            "turnover_USD": 0,
        },
    )
    return {
        "status_counts": dict(Counter(r["status"] for r in rows)),
        "maximum_ledger_residual_USD": str(max(a.maximum_residual for a in engine.fast_accounts)),
        "baseline": baseline,
        "unique_cases": len(rows),
    }
