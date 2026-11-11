"""Compact typed research tables; exact ledger checks precede float exports."""

import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

from .diagnostics import quality_summary
from .paths import ROOT, V5, digest, publish
from .runner import FastEngine
from .strategies import IDS, mode

D = Decimal
QUALIFICATION = (
    "Exploratory reused2021-24 fixed survivors;retrospective QA/actions;"
    "assumed receipt and borrow;OHLCV trade-print proxies,not NBBO/locates/broker fills;"
    "no independent Stage6 audit or untouched confirmation."
)


def metrics(rows: list[dict]) -> dict:
    if not rows:
        return {"status": "NO_ACCOUNT_DAYS"}
    if any(
        r["status"] != "OBSERVED"
        or r["nav"] is None
        or not np.isfinite(float(r["nav"]))
        or float(r["nav"]) <= 0
        for r in rows
    ):
        return {
            "status": "HOLD",
            "reason": "INCOMPLETE_NONPOSITIVE_OR_NONFINITE_NAV",
            "net_PnL_USD": None,
        }
    nav = np.asarray([float(r["nav"]) for r in rows])
    ret = nav / np.r_[100000.0, nav[:-1]] - 1
    std = float(np.std(ret, ddof=1)) if len(ret) > 1 else 0.0
    wealth = np.r_[100000.0, nav]
    dd = wealth / np.maximum.accumulate(wealth) - 1
    years = max(
        (pd.Timestamp(rows[-1]["date"]) - pd.Timestamp(rows[0]["date"])).days / 365.25, 1 / 365.25
    )
    annual = {}
    prior = 100000.0
    for year in sorted({r["date"][:4] for r in rows}):
        indexes = [i for i, r in enumerate(rows) if r["date"].startswith(year)]
        end = float(nav[indexes[-1]])
        annual[year] = {
            "start_NAV": prior,
            "end_NAV": end,
            "return": end / prior - 1,
            "sessions": len(indexes),
        }
        prior = end
    return {
        "status": "COMPLETE",
        "final_NAV_USD": float(nav[-1]),
        "net_PnL_USD": float(nav[-1] - 100000),
        "total_return": float(nav[-1] / 100000 - 1),
        "CAGR": float((nav[-1] / 100000) ** (1 / years) - 1),
        "Sharpe_252_zero_rf": float(np.mean(ret) / std * np.sqrt(252)) if std > 0 else None,
        "volatility_252": std * np.sqrt(252),
        "max_drawdown": float(dd.min()),
        "annual": annual,
        "sessions": len(rows),
        "qualification": QUALIFICATION,
    }


def clean(value):
    if isinstance(value, D):
        return float(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, (list, tuple, dict)):
        return json.dumps(value, default=str, sort_keys=True)
    return value


def frame(rows: list[dict], columns: list[str]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame([{k: clean(v) for k, v in row.items()} for row in rows])


def footprint(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def terminal_rows(engine: FastEngine, strategy: str) -> list[dict]:
    a = next(a for a in engine.fast_accounts if a.arm == strategy)
    rows = []
    for lot in a.lots.values():
        mark = (a.prices[lot.ticker] or D(0)) * lot.quantity
        claims = sum((v for (_, key), (v, _) in a.claims.items() if key == lot.key), D(0))
        special = a.special_values.get(lot.key, D(0))
        regular = a.stats.lot_regular_cost.get(lot.key, D(0))
        rows.append(
            {
                "key": lot.key,
                "ticker": lot.ticker,
                "origin": lot.origin,
                "endpoint": lot.endpoint,
                "entry_at": lot.entry_at,
                "exit_at": lot.exit_at,
                "entry_price": lot.entry_price,
                "exit_price": lot.exit_price,
                "direction": lot.direction,
                "requested": lot.requested,
                "unit_factor": lot.unit_factor,
                "cash_pnl": lot.cash + mark + claims + special,
                "cash_only": lot.cash,
                "remaining_shares": lot.quantity,
                "ordinary_claims": claims,
                "special_claims": special,
                "fees": lot.fees,
                "cost": lot.cost,
                "borrow": lot.borrow,
                "funding": lot.funding,
                "regular_trading_cost": regular,
                "gross_signed_price_pnl": lot.cash + mark - lot.nontrade + regular,
                "gross_action_cash": lot.nontrade
                + lot.borrow
                + lot.funding
                + lot.cost
                - regular
                + claims
                + special,
                "intent_lineage": a.stats.lot_lineage.get(lot.key, ""),
                "source": a.source_pointer,
                "decision": a.stats.lot_decision.get(lot.key),
                "terminal_status": "OPEN_MARKED_HOLD" if lot.quantity else "PRICED_UNPAID_CLAIM",
            }
        )
    return rows


def write_results(engine: FastEngine, out: Path, run_info: dict) -> dict:
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)
    summaries = []
    quality_rows = []
    examples = {}
    maximum_strategy = 0
    for a in engine.fast_accounts:
        s = a.arm
        dest = out / s
        dest.mkdir()
        daily = engine.daily_rows[s]
        for r in daily:
            rhs = r["cash"] + r["physical_value"] + r["claims"] + r["special"]
            if r["nav"] is not None and abs(r["nav"] - rhs) > D("1e-8"):
                raise ValueError("DAILY_NAV_IDENTITY")
        tail = terminal_rows(engine, s)
        all_trades = a.stats.trade_rows + tail
        pnl = sum((r["cash_pnl"] for r in all_trades), D(0))
        last = a.nav()
        if last is not None and abs(last - 100000 - pnl) > D("1e-8"):
            raise ValueError("COHORT_NAV_RECONCILIATION")
        regular_gross = sum((r["gross_signed_price_pnl"] for r in all_trades), D(0))
        action_gross = sum((r["gross_action_cash"] for r in all_trades), D(0))
        cost = a.commission + a.friction + a.borrow_paid + a.funding_paid
        if last is not None and abs(regular_gross + action_gross - cost - pnl) > D("1e-8"):
            raise ValueError("PNL_COMPONENT_RECONCILIATION")
        executed = [r for r in all_trades if r["entry_at"] is not None]
        if a.pending or any(a.quantity) or a.unpriced_special or a.risk_hold:
            engine.account_holds.setdefault(s, []).append(
                "TERMINAL_ORDER_STOCK_OR_UNPRICED_SPECIAL"
            )
        summary = metrics(daily)
        if s in engine.account_holds:
            summary.clear()
            summary.update(
                status="HOLD",
                hold_reasons=engine.account_holds[s],
                last_known_equity_USD=str(last),
                net_PnL_USD=None,
            )
        elif not executed:
            summary["status"] = "NO_TRADES"
        grosses = np.asarray([float(r["gross_signed_price_pnl"]) for r in executed])
        w = grosses[grosses > 0]
        losses = grosses[grosses < 0]
        orders = {}
        for row in a.stats.physical_rows:
            o = orders.setdefault(row["order_id"], {"fee": D(0), "q": D(0), "notional": D(0)})
            o["fee"] += row["commission"]
            o["q"] += abs(row["shares"])
            o["notional"] += abs(row["shares"] * row["external_price"])
        notionals = np.asarray([float(v["notional"]) for v in orders.values()])
        signal = engine.signal_rows[s]
        holds = [r["exit_at"] - r["entry_at"] for r in executed if r["exit_at"] is not None]
        summary.update(
            strategy_id=s,
            mode=mode(s),
            gross_signed_price_PnL_USD=str(regular_gross),
            gross_action_value_USD=str(action_gross),
            gross_winning_USD=float(w.sum()),
            gross_losing_USD=float(losses.sum()),
            average_gross_winner_USD=float(w.mean()) if len(w) else None,
            average_gross_loser_USD=float(losses.mean()) if len(losses) else None,
            gross_price_hit_rate=float(np.mean(grosses > 0)) if len(grosses) else None,
            gross_cost_addback_same_holdings_USD=str(
                (last - 100000 + cost) if last is not None else "UNPRICED"
            ),
            cost_addback_limitation=(
                "Arithmetic same-holdings attribution. No independent frictionless rerun."
            ),
            commissions_USD=str(a.commission),
            print_slippage_USD=str(a.stats.spread),
            impact_USD=str(a.stats.impact),
            borrow_USD=str(a.borrow_paid),
            funding_USD=str(a.funding_paid),
            total_cost_USD=str(cost),
            cohorts_filled=len(executed),
            physical_external_orders=len(orders),
            physical_external_fill_events=len(a.stats.physical_rows),
            median_external_order_notional_USD=float(np.median(notionals))
            if len(notionals)
            else None,
            minimum_fee_binding_orders=sum(
                o["fee"] == 1 and D(".005") * o["q"] < 1 for o in orders.values()
            )
            if s.startswith("R")
            else 0,
            candidate_intents=sum(r["candidate_intents"] for r in signal),
            scheduled_name_opportunities=sum(r["potential"] for r in signal),
            observed_calendar_name_opportunities=sum(r["calendar_names"] for r in signal),
            rejections=dict(a.rejected),
            execution_counts=dict(a.stats.counts),
            median_holding_wall_minutes=float(np.median(holds)) if holds else None,
            average_virtual_gross_NAV=float(
                np.mean(
                    [
                        float(r["virtual_gross"]) / float(r["nav"])
                        for r in daily
                        if r["nav"] and r["nav"] > 0
                    ]
                )
            )
            if daily
            else None,
            turnover_over_mean_NAV=float(
                notionals.sum() / np.mean([float(r["nav"]) for r in daily if r["nav"] is not None])
            )
            if len(notionals) and daily
            else 0,
            balance_residual_USD=str(a.maximum_residual),
            terminal_claims_USD=str(a.claim_total()),
            terminal_special_USD=str(sum(a.special_values.values(), D(0))),
            terminal_stock_symbols=int(np.count_nonzero(a.quantity)),
            regulatory_pass_through="not modeled;unavailable,not observed zero",
            qualification=QUALIFICATION,
        )
        if abs(a.friction - a.stats.spread - a.stats.impact) > D("1e-8"):
            raise ValueError("FRICTION_COMPONENTS")
        qreasons = engine.quality.reasons[s].copy()
        qreasons["TERMINAL_UNMATURED_OR_UNOBSERVED"] += sum(
            p.intent.strategy_id == s for p in engine.quality.pending
        )
        quality = quality_summary(engine.quality.completed[s], qreasons)
        quality.update(strategy_id=s, mode=mode(s), qualification=QUALIFICATION)
        publish(
            dest / "config.json", next(x for x in engine.registry["strategies"] if x["id"] == s)
        )
        publish(dest / "summary.json", summary)
        publish(
            dest / "diagnostics.json",
            {"quality": quality, "anomalies": a.stats.anomalies, "qualification": QUALIFICATION},
        )
        frame(daily, ["date", "nav", "status"]).to_parquet(
            dest / "daily_nav.parquet", index=False, compression="zstd"
        )
        frame(executed, ["key", "entry_at", "exit_at", "cash_pnl"]).to_parquet(
            dest / "trades.parquet", index=False, compression="zstd"
        )
        frame(a.stats.physical_rows, ["order_id", "shares", "commission"]).to_parquet(
            dest / "physical_orders.parquet", index=False, compression="zstd"
        )
        frame(signal, ["date", "slot", "potential", "candidate_intents"]).to_csv(
            dest / "signal_counts.csv", index=False
        )
        pd.DataFrame(
            [
                {"component": k, "USD": float(v)}
                for k, v in {
                    "commission": a.commission,
                    "incremental_print_slippage": a.stats.spread,
                    "impact": a.stats.impact,
                    "borrow": a.borrow_paid,
                    "funding": a.funding_paid,
                    "gross_action_value": action_gross,
                }.items()
            ]
        ).to_csv(dest / "cost_breakdown.csv", index=False)
        publish(
            dest / "terminal_state.json",
            {
                "lots": tail,
                "pending_orders": [vars(o) for o in a.pending.values()],
                "qualification": QUALIFICATION,
            },
        )
        size = footprint(dest)
        maximum_strategy = max(maximum_strategy, size)
        if size > 25 * 2**20:
            raise ValueError("STRATEGY_OUTPUT_HARD_LIMIT")
        summaries.append(summary)
        quality_rows.append({k: v for k, v in quality.items() if not isinstance(v, (dict, list))})
        examples[s] = [{k: clean(v) for k, v in r.items()} for r in executed if r["cash_pnl"] < 0][
            :5
        ]
    if tuple(s["strategy_id"] for s in summaries) != IDS:
        raise ValueError("MISSING_OR_DUPLICATE_STRATEGY_RESULTS")
    flat = [
        {
            **{k: v for k, v in r.items() if not isinstance(v, (dict, list))},
            **{year + "_return": row["return"] for year, row in r.get("annual", {}).items()},
        }
        for r in summaries
    ]
    pd.DataFrame(flat).to_csv(out / "SUMMARY_18_STRATEGIES.csv", index=False)
    pd.DataFrame(quality_rows).to_csv(out / "SIGNAL_QUALITY_18.csv", index=False)
    publish(out / "EXPERIMENT_REGISTRY.json", engine.registry)
    publish(out / "SHARED_FEATURE_CACHE_MANIFEST.json", engine.cache.manifest)
    publish(out / "LOSING_TRADE_EXAMPLES.json", examples)
    lines = [
        "# Directional screening diagnostics",
        "",
        QUALIFICATION,
        "",
        "Each funded result uses raw-share OHLCV and the registered costs.",
        "Positive and negative gross sums use signed price changes before costs.",
        "Arithmetic cost addbacks retain the simulated holdings and decisions.",
        "",
        "| ID | Status | Gross wins USD | Gross losses USD | Costs USD | Net P&L USD |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for r in summaries:
        net = r.get("net_PnL_USD")
        net_label = "N/A" if net is None else f"{net:,.2f}"
        lines.append(
            f"| {r['strategy_id']} | {r['status']} | {r['gross_winning_USD']:,.2f} | "
            f"{r['gross_losing_USD']:,.2f} | {float(r['total_cost_USD']):,.2f} | {net_label} |"
        )
    lines.extend(
        [
            "",
            "Per-strategy diagnostics retain the candidate frontier, bounded rejection and "
            "execution examples, same-opportunity opposite-sign null and censored outcomes.",
            "The losing-trade examples identify feature and execution lineage. The physical-order "
            "tables separate price friction, cumulative fees and external order counts.",
        ]
    )
    (out / "DIAGNOSTICS_AND_FAILURE_MODES.md").write_text("\n".join(lines) + "\n")
    for name in ("REUSE_AND_RUNTIME_PLAN.md", "POLICY_AND_ASSUMPTIONS.md"):
        (out / name).write_bytes((ROOT / name).read_bytes())
    controls = json.loads(
        (V5 / "BASELINE_FOUR_ARM_RESULTS/baseline_v5_r2/DESCRIPTIVE_ANALYSIS_V5.json").read_text()
    )
    publish(
        out / "CONTEXT_CONTROLS.json",
        {
            "NO_TRADE": {
                "initial": 100000,
                "final": 100000,
                "return": 0,
                "funding_and_interest": 0,
            },
            "LEGACY_V5_SIGN": {
                "source": str(
                    V5 / "BASELINE_FOUR_ARM_RESULTS/baseline_v5_r2/DESCRIPTIVE_ANALYSIS_V5.json"
                ),
                "metrics": controls["metrics"]["baseline/matched/EQUAL"],
                "caveat": ("Frozen legacy context. Frequency, costs and sizing population differ."),
            },
            "qualification": QUALIFICATION,
        },
    )
    size = footprint(out)
    if size > 500 * 2**20:
        raise ValueError("TOTAL_OUTPUT_HARD_LIMIT")
    publish(
        out / "EXECUTION_AND_RESOURCE_REPORT.json",
        {
            **run_info,
            "output_bytes_before_final_manifest": size,
            "maximum_strategy_bytes": maximum_strategy,
            "shared_cache_bytes": engine.cache.manifest["bytes"],
            "no_per_minute_journal": True,
            "no_daily_checkpoints": True,
            "source_read_partitions": len(engine.market.reads),
            "qualification": QUALIFICATION,
        },
    )
    publish(
        out / "manifest.json",
        {
            "registry_identity": engine.registry["identity"],
            "status_counts": dict(Counter(r["status"] for r in summaries)),
            "strategy_IDs": IDS,
            "files": {str(p.relative_to(out)): digest(p) for p in out.rglob("*") if p.is_file()},
            "self_exclusion": "manifest.json",
            "qualification": QUALIFICATION,
        },
    )
    return {
        "status_counts": dict(Counter(r["status"] for r in summaries)),
        "output_bytes": footprint(out),
        "max_strategy_bytes": maximum_strategy,
    }
