"""Postrun recovery of three special physical rows and deterministic diagnostic tables.

Only a previously sealed checkpoint is read. No trading event is regenerated.
"""

import gzip
import json

import numpy as np
import pandas as pd

from .rapid_exit_audit.io import as_rows, column, table
from .rapid_final_diag.provenance import ROOT
from .rapid_v1.paths import digest, publish
from .rapid_v1.portfolio import CompactStats
from .rapid_v1.state import decode
from .rapid_v2_diagnostics.report import csv_write
from .stage012.model_registry import SYMBOLS

RUN = ROOT / "runs/final-diag-20261110-r1"


def supplement() -> None:
    out = ROOT / "supplement_01"
    out.mkdir(exist_ok=False)
    source = RUN / "states/2021-12-31.json.gz"
    accounts = decode(json.loads(gzip.decompress(source.read_bytes()))["body"]["accounts"])
    rows = []
    if not isinstance(accounts, list):
        raise ValueError("CHECKPOINT_ACCOUNT_LIST")
    for a in accounts:
        if not isinstance(a, dict) or not isinstance(a.get("stats"), CompactStats):
            raise ValueError("CHECKPOINT_ACCOUNT_STATS")
        stats = a["stats"]
        if not isinstance(stats, CompactStats):
            raise ValueError("CHECKPOINT_STATS_TYPE")
        for r in stats.anomalies:
            if r["kind"] != "OGN_EXTERNAL_DISPOSAL":
                continue
            q, raw, fee, cash = (
                r[k] for k in ("external_delta", "raw_reference", "fee", "external_cash")
            )
            concession = -q * raw - cash - fee
            rows.append(
                {
                    "case": a["arm"],
                    "strategy_id": a["arm"],
                    "order_id": "OGN:" + str(r["decision"]),
                    "ticker": 20,
                    "decision": r["decision"],
                    "effective": r["effective"],
                    "posted": r["at"],
                    "shares": float(q),
                    "raw_open": float(raw),
                    "external_price": float(-(cash + fee) / q),
                    "commission": float(fee),
                    "print_slippage": float(concession / 2),
                    "impact": float(concession / 2),
                    "status": "SPECIAL_OBSERVED",
                    "source": "SEALED_OGN_SIP;CONDITIONAL_DISTRIBUTION_POLICY",
                    "recovered_from_checkpoint_sha256": digest(source),
                }
            )
    pd.DataFrame(rows).to_parquet(
        out / "RECOVERED_OGN_PHYSICAL_ROWS.parquet", index=False, compression="zstd"
    )
    physical = pd.concat(
        [pd.read_parquet(RUN / "funded/PHYSICAL_FILLS.parquet"), pd.DataFrame(rows)],
        ignore_index=True,
    )
    summaries = pd.read_csv(RUN / "funded/FUNDED_TARGETED_RESULTS.csv")
    costs, bands, checks = [], [], []
    for r in as_rows(summaries):
        key = r.strategy_id + "_" + r.variant
        f = table(physical.loc[column(physical, "case") == key]).copy()
        f["notional"] = abs(column(f, "shares")) * column(f, "external_price")
        f["abs_shares"] = abs(column(f, "shares"))
        orders = table(
            f.groupby("order_id")[
                ["notional", "abs_shares", "commission", "print_slippage", "impact"]
            ].sum()
        )
        for k, expected in (
            ("commission", r.commission_USD),
            ("print_slippage", r.assumed_spread_USD),
            ("impact", r.assumed_impact_USD),
            ("notional", r.executed_turnover_USD),
        ):
            difference = float(column(orders, k).sum()) - float(expected)
            if abs(difference) > 1e-7:
                raise ValueError(f"PHYSICAL_ACCOUNT_BRIDGE {key} {k} {difference}")
            checks.append({"case": key, "field": k, "residual": difference, "status": "PASS"})
        if len(orders) != r.external_orders:
            raise ValueError("PHYSICAL_ORDER_CENSUS " + key)
        fee = column(orders, "commission").to_numpy(float)
        notional = column(orders, "notional").to_numpy(float)
        costs.append(
            {
                "case": key,
                "physical_orders": len(orders),
                "physical_fill_rows": len(f),
                "median_order_notional": float(np.median(notional)),
                "p25_order_notional": float(np.quantile(notional, 0.25)),
                "p75_order_notional": float(np.quantile(notional, 0.75)),
                "median_order_shares": float(np.median(column(orders, "abs_shares"))),
                "minimum_fee_order_fraction": float(np.mean(fee == 1))
                if r.mode == "RETAIL_CONSERVATIVE"
                else 0.0,
                "commission_USD": float(fee.sum()),
                "spread_USD": float(column(orders, "print_slippage").sum()),
                "impact_USD": float(column(orders, "impact").sum()),
                "borrow_USD": r.borrow_USD,
                "funding_USD": r.funding_USD,
                "arrival_drift_USD": r.signed_arrival_USD,
                "absolute_arrival_NOT_EXTRA_COST_USD": r.absolute_arrival_USD,
                "concession_0p5_same_holdings_net": r.net_PnL_USD
                + 0.5 * (r.assumed_spread_USD + r.assumed_impact_USD),
                "concession_1p5_same_holdings_net": r.net_PnL_USD
                - 0.5 * (r.assumed_spread_USD + r.assumed_impact_USD),
                "hypothetical_arithmetic_not_funded_rerun": True,
            }
        )
        for lo, hi in ((0, 1000), (1000, 2000), (2000, 5000), (5000, 10000), (10000, float("inf"))):
            b = (notional >= lo) & (notional < hi)
            bands.append(
                {
                    "case": key,
                    "lower_notional": lo,
                    "upper_notional": hi,
                    "orders": int(b.sum()),
                    "notional": float(notional[b].sum()),
                    "commission": float(fee[b].sum()),
                }
            )
    csv_write(out / "PHYSICAL_ORDERS_RECONCILIATION.csv", checks)
    csv_write(out / "PHYSICAL_COST_DIAGNOSTICS_COMPLETE.csv", costs)
    csv_write(out / "ORDER_NOTIONAL_BANDS.csv", bands)
    trade = pd.read_parquet(RUN / "funded/COMPLETED_COHORTS.parquet")
    concentration = []
    for k, block in trade.groupby("case"):
        d = table(block)
        totals = column(table(d.groupby("ticker")[["cash_pnl"]].sum()), "cash_pnl").sort_values(
            ascending=False
        )
        net = float(column(d, "cash_pnl").sum())
        top = totals.index.to_numpy()[:2]
        concentration.append(
            {
                "case": str(k),
                "top_two_symbols": "|".join(SYMBOLS[int(j)] for j in top),
                "top_two_net_USD": float(totals.iloc[:2].sum()),
                "net_without_top_two_ARITHMETIC_ONLY": net - float(totals.iloc[:2].sum()),
                "top_five_cohort_net": float(column(d, "cash_pnl").nlargest(5).sum()),
                "worst_five_cohort_net": float(column(d, "cash_pnl").nsmallest(5).sum()),
            }
        )
    csv_write(out / "CONCENTRATION.csv", concentration)
    vintage = []
    for r in as_rows(summaries):
        key = r.strategy_id + "_" + r.variant
        d = table(trade.loc[column(trade, "case") == key])
        risk = column(d, "cause").str.startswith("RISK_")
        primary = int((column(d, "cause") == "RISK_VINTAGE_CAP").sum())
        anyv = int((risk & column(d, "triggers").str.contains("VINTAGE_CAP", na=False)).sum())
        vintage.append(
            {
                "case": key,
                "primary_vintage_closed_cohorts": primary,
                "any_vintage_trigger_closed_cohorts": anyv,
                "eligible_original_candidate_intents": r.candidate_intents,
                "primary_vintage_per_candidate": primary / r.candidate_intents,
                "any_vintage_per_candidate": anyv / r.candidate_intents,
                "whole_account_liquidation_tag_not_individual_causal_effect": True,
            }
        )
    csv_write(out / "VINTAGE_RISK_PER_OPPORTUNITY.csv", vintage)
    reserve = pd.read_csv(RUN / "funded/R01_ENTRY_RESERVES.csv")
    stress = []
    for origin, block in reserve.groupby("origin"):
        d = table(block)
        first = d.iloc[0]
        s = np.exp(column(d, "v20").to_numpy(float))
        new = column(d, "new_commitment").to_numpy(float)
        lhs = float(first["A"]) + float(np.sum(new * s))
        rhs = 0.2 * (
            float(first["N"]) - float(first["R"]) - float(first["L"]) - float(np.sum(new * (s - 1)))
        )
        residual = lhs - rhs
        if residual > 1e-7:
            raise ValueError("RESERVE_INEQUALITY " + str(origin))
        stress.append(
            {
                "origin": str(origin),
                "legs": len(d),
                "t": float(first["t"]),
                "stressed_commitment": lhs,
                "stressed_cap": rhs,
                "residual": residual,
            }
        )
    csv_write(out / "R01_STRESS_INEQUALITY_CHECKS.csv", stress)
    publish(
        out / "SUPPLEMENT_MANIFEST.json",
        {
            "status": "PASS",
            "reason": "Three omitted OGN physical rows recovered from exact saved events",
            "funded_performance_changed": False,
            "funded_replay_performed": False,
            "checkpoint_sha256": digest(source),
            "recovered_rows": len(rows),
            "funded_manifest_sha256": digest(RUN / "funded/FUNDED_MANIFEST.json"),
            "analysis_receipt_sha256": digest(ROOT / "analysis_01/ANALYSIS_RECEIPT.json"),
            "files": {p.name: digest(p) for p in sorted(out.iterdir())},
        },
    )


if __name__ == "__main__":
    supplement()
