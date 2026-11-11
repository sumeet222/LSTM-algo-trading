"""Read-only post-publication analysis of the sealed final diagnostic accounts.

This module is deliberately outside the sealed online package. Offline prices have
no import path back into the trading engine.
"""

import time
from pathlib import Path

import numpy as np
import pandas as pd

from .rapid_exit_audit.io import as_rows, column, table
from .rapid_final_diag.policy import TREATMENTS
from .rapid_final_diag.provenance import FUNDED, ROOT, load, registry
from .rapid_v1.paths import canonical, digest, publish
from .rapid_v1.shared_features import FeatureCache
from .rapid_v1.strategies import IDS, evaluate
from .rapid_v2_diagnostics.report import csv_write
from .rapid_v3_dynamic.policy import HoldingClock
from .stage012.calendar_schedule import MarketClock
from .stage012.model_registry import SYMBOLS
from .stage35.final_backtest_v4.execution_calendar import ExecutionCalendar

RUN = ROOT / "runs/final-diag-20261110-r1"


def select(df: pd.DataFrame, key: str) -> pd.DataFrame:
    return table(df.loc[column(df, "case") == key])


def money(df: pd.DataFrame, name: str) -> float:
    return float(column(df, name).sum()) if len(df) else 0.0


def verify_funded() -> dict:
    receipt = load(RUN / "RUN_RECEIPT.json")
    m = load(RUN / "funded/FUNDED_MANIFEST.json")
    if receipt["status"] != "COMPLETE" or m["status_counts"] != {"COMPLETE": 13}:
        raise ValueError("FUNDED_NOT_ALL_COMPLETE")
    for name, sha in m["files"].items():
        if digest(RUN / "funded" / name) != sha:
            raise ValueError("FUNDED_OUTPUT_HASH_DRIFT")
    if load(RUN / "funded/CONTROL_PARITY.json")["status"] != "PASS":
        raise ValueError("CONTROL_PARITY_REQUIRED")
    return receipt


def candidates(cache: FeatureCache) -> dict[str, set[tuple]]:
    """Original pure signals only. This is not a replay or an outcome eligibility filter."""
    c = HoldingClock(ExecutionCalendar(MarketClock("2020-01-01", "2025-02-01")))
    base: dict[str, set[tuple]] = {sid: set() for sid in TREATMENTS}
    for date in sorted(cache.by_date):
        if not ("2021-01-01" <= date <= "2024-12-31"):
            continue
        for f in cache.frames(date):
            for sid in TREATMENTS:
                decision = evaluate(sid, f)
                # Calendar admission uses only metadata; outcome availability never filters keys.
                for it in decision.intents:
                    if not c.admits(f, sid[0] == "M", "2024-12-31"):
                        continue
                    for j, side in zip(it.tickers, it.signs, strict=True):
                        base[sid].add((it.origin, j, side))
    return base


def opportunity_rows(trades: pd.DataFrame, potential: dict[str, set[tuple]]) -> list[dict]:
    rows = []
    for sid, treatment in TREATMENTS.items():
        control_key = sid + ("_H100" if sid == "R01" else "_CONTROL")
        left = select(trades, control_key)
        right = select(trades, sid + "_" + treatment)

        def records(df: pd.DataFrame) -> dict:
            result = {}
            for r in as_rows(df):
                key = (int(r.origin), int(r.ticker), int(r.direction))
                if key in result:
                    raise ValueError("DUPLICATE_COHORT_OPPORTUNITY")
                result[key] = r
            return result

        a, b = records(left), records(right)
        for key in sorted(a.keys() | b.keys()):
            x, y = a.get(key), b.get(key)
            rows.append(
                {
                    "strategy_id": sid,
                    "control": control_key,
                    "treatment": sid + "_" + treatment,
                    "origin": key[0],
                    "ticker": SYMBOLS[key[1]],
                    "side": key[2],
                    "category": "BOTH_ENTERED"
                    if x is not None and y is not None
                    else ("CONTROL_ONLY" if x is not None else "TREATMENT_ONLY"),
                    "control_net": x.cash_pnl if x else None,
                    "treatment_net": y.cash_pnl if y else None,
                    "control_gross": x.gross_signed_price_pnl if x else None,
                    "treatment_gross": y.gross_signed_price_pnl if y else None,
                    "control_entry": x.entry_at if x else None,
                    "treatment_entry": y.entry_at if y else None,
                    "control_exit": x.exit_at if x else None,
                    "treatment_exit": y.exit_at if y else None,
                    "control_entry_notional": x.entry_notional_raw_USD if x else None,
                    "treatment_entry_notional": y.entry_notional_raw_USD if y else None,
                    "control_cause": x.cause if x else None,
                    "treatment_cause": y.cause if y else None,
                    "quantity_or_notional_changed": bool(
                        x and y and x.entry_notional_raw_USD != y.entry_notional_raw_USD
                    ),
                    "exit_changed": bool(x and y and x.exit_at != y.exit_at),
                    "raw_causal_key_verified": key in potential[sid],
                    "not_an_isolated_causal_dollar_effect": True,
                }
            )
        missing = potential[sid] - (a.keys() | b.keys())
        rows.append(
            {
                "strategy_id": sid,
                "category": "NEITHER_FUNDED_AGGREGATE",
                "count": len(missing),
                "unfilled_per_key_reason": "NOT_EXPORTED_PER_KEY; see aggregate rejection counts",
            }
        )
    return rows


def offline_sample(tape: pd.DataFrame, pairs: list[dict], cache: FeatureCache, out: Path) -> dict:
    from .rapid_exit_audit.offline import make_sample

    chosen = []
    for sid, name in TREATMENTS.items():
        key = sid + "_" + name
        d = select(tape, key)
        changed_origins = {
            int(r["origin"]) for r in pairs if r["strategy_id"] == sid and r.get("exit_changed")
        }
        d = table(d.loc[column(d, "origin").isin(changed_origins)])
        records = d.to_dict("records")
        # The future outcome is absent from this deterministic selection operation.
        records.sort(key=lambda r: canonical(r))
        chosen.extend(records[:100])
    if not chosen:
        return {"status": "NO_CHANGED_EXITS", "sampled_portions": 0}
    selected = pd.DataFrame(chosen)
    publish(
        out / "OFFLINE_SELECTION_BEFORE_MARKS.json",
        {
            "sample_sha256": canonical(chosen),
            "portions": len(chosen),
            "rule": "hash-smallest 100 portions/treatment among changed same-origin exits",
            "limitation": "bounded descriptive sample; not weighted to infer population dollars",
            "funded_manifest_sha256": digest(RUN / "funded/FUNDED_MANIFEST.json"),
        },
    )
    sample, _legacy, receipt = make_sample(selected, cache)
    sample.to_parquet(out / "OFFLINE_CHANGED_EXIT_SAMPLE.parquet", index=False, compression="zstd")
    rows = []
    for key, group in sample.groupby(["case", "horizon", "cause", "side", "feasibility"]):
        d = table(group)
        valid = table(d.loc[column(d, "censor") == "VALID"])
        values = column(valid, "price_raw_to_raw").to_numpy(float)
        bps = column(valid, "raw_bps").to_numpy(float)
        labels = tuple(key) if isinstance(key, tuple) else (key,)
        rows.append(
            dict(zip(("case", "horizon", "cause", "side", "feasibility"), labels))
            | {
                "sampled": len(d),
                "valid": len(valid),
                "censored": len(d) - len(valid),
                "raw_signed_USD": float(values.sum()),
                "missed_upside_USD": float(values[values > 0].sum()),
                "avoided_loss_USD": float(-values[values < 0].sum()),
                "mean_raw_bps": float(np.mean(bps)) if len(bps) else None,
                "favorable_fraction": float(np.mean(values > 0)) if len(values) else None,
                "median_raw_USD": float(np.median(values)) if len(values) else None,
                "basis": "UNFUNDED_OFFLINE_RAW_TO_RAW; no combined portfolio inference",
            }
        )
    csv_write(out / "OFFLINE_CHANGED_EXIT_EXTENSIONS.csv", rows)
    publish(out / "OFFLINE_SOURCE_RECEIPT.json", receipt)
    return {
        "status": "DESCRIPTIVE_SAMPLE_ONLY",
        "sampled_portions": len(chosen),
        "targets": len(sample),
        "valid": int(column(sample, "valid").sum()),
    }


def run_analysis() -> None:
    start = time.monotonic()
    receipt = verify_funded()
    spec = registry()
    out = ROOT / "analysis_01"
    out.mkdir(exist_ok=False)
    base = RUN / "funded"
    summary = pd.read_csv(base / "FUNDED_TARGETED_RESULTS.csv")
    trades = pd.read_parquet(base / "COMPLETED_COHORTS.parquet")
    physical = pd.read_parquet(base / "PHYSICAL_FILLS.parquet")
    tape = pd.read_parquet(base / "ACTUAL_EXIT_PORTIONS.parquet")
    summary["case"] = column(summary, "strategy_id") + "_" + column(summary, "variant")
    attribution, tails, checks, order_rows = [], [], [], []
    for r in as_rows(summary):
        d = select(trades, r.case)
        for field, expected in (
            ("cash_pnl", r.net_PnL_USD),
            ("gross_signed_price_pnl", r.gross_signed_price_PnL_USD),
            ("gross_action_cash", r.gross_action_value_USD),
        ):
            residual = money(d, field) - expected
            if abs(residual) > 1e-7:
                raise ValueError(f"COHORT_ACCOUNT_RESIDUAL {r.case} {field} {residual}")
            checks.append({"case": r.case, "field": field, "residual": residual, "status": "PASS"})
        net = column(d, "cash_pnl").to_numpy(float)
        gross = column(d, "gross_signed_price_pnl").to_numpy(float)
        tails.append(
            {
                "case": r.case,
                "cohorts": len(d),
                "net_winners": float(net[net > 0].sum()),
                "net_losers": float(net[net < 0].sum()),
                "gross_winners": float(gross[gross > 0].sum()),
                "gross_losers": float(gross[gross < 0].sum()),
                "worst_net": float(net.min()) if len(net) else None,
                "worst_five_net": float(np.sort(net)[:5].sum()),
                "best_five_net": float(np.sort(net)[-5:].sum()),
                "win_rate_net": float(np.mean(net > 0)) if len(net) else None,
                "net_profit_factor": float(net[net > 0].sum() / -net[net < 0].sum())
                if np.any(net < 0)
                else None,
            }
        )
        d = d.assign(
            entry_year=pd.to_datetime(
                column(d, "entry_at").to_numpy(float) * 60, unit="s", utc=True
            ).strftime("%Y"),
            entry_half=np.where(column(d, "origin") < 27875520, "2021_2022", "2023_2024"),
        )
        # Half boundary is 2023-01-01T00:00Z in epoch minutes; no market outcome use.
        for axis in ("ticker", "direction", "cause", "entry_year", "entry_half"):
            for label, block in d.groupby(axis):
                group = table(block)
                attribution.append(
                    {
                        "case": r.case,
                        "axis": axis,
                        "label": str(label),
                        "cohorts": len(group),
                        "net": money(group, "cash_pnl"),
                        "gross_price": money(group, "gross_signed_price_pnl"),
                        "actions": money(group, "gross_action_cash"),
                        "cost": money(group, "cost"),
                        "borrow": money(group, "borrow"),
                        "funding": money(group, "funding"),
                    }
                )
        f = select(physical, r.case)
        q = column(f, "shares").to_numpy(float)
        notional = abs(q) * column(f, "external_price").to_numpy(float)
        order_ids = column(f, "order_id")
        fee = f.groupby("order_id")["commission"].sum()
        order_rows.append(
            {
                "case": r.case,
                "external_orders": len(set(order_ids)),
                "fill_rows": len(f),
                "median_fill_shares": float(np.median(abs(q))),
                "median_fill_notional": float(np.median(notional)),
                "physical_commission": money(f, "commission"),
                "physical_print": money(f, "print_slippage"),
                "physical_impact": money(f, "impact"),
                "minimum_bound_orders": int(np.sum(np.asarray(fee) == 1))
                if r.mode.startswith("RETAIL")
                else 0,
                "arrival_drift_USD": r.signed_arrival_USD,
                "absolute_arrival_NOT_EXTRA_COST": r.absolute_arrival_USD,
                "same_holdings_half_concession_net": r.net_PnL_USD
                + 0.5 * (r.assumed_spread_USD + r.assumed_impact_USD),
                "same_holdings_1p5_concession_net": r.net_PnL_USD
                - 0.5 * (r.assumed_spread_USD + r.assumed_impact_USD),
            }
        )
    csv_write(out / "COHORT_ACCOUNT_RECONCILIATION.csv", checks)
    csv_write(out / "COHORT_TAILS.csv", tails)
    csv_write(out / "COHORT_ATTRIBUTION.csv", attribution)
    csv_write(out / "PHYSICAL_COST_DIAGNOSTICS.csv", order_rows)
    cache = FeatureCache(Path(spec["cache"]))
    pairs = opportunity_rows(trades, candidates(cache))
    csv_write(out / "PAIRED_OPPORTUNITY_AND_EXIT_DIVERGENCE.csv", pairs)
    offline = offline_sample(tape, pairs, cache, out)
    old = pd.read_csv(FUNDED / "V3_ALL54_SUMMARY.csv")
    v2 = Path(load(ROOT.parent / "rapid_v3_dynamic/PARENT_BOUNDARY.json")["V2_results"])
    fixed = pd.read_csv(v2 / "HORIZON_RESULTS.csv")
    v1 = pd.read_csv(
        Path(load(ROOT.parent / "rapid_v3_dynamic/PARENT_BOUNDARY.json")["V1_results"])
        / "SUMMARY_18_STRATEGIES.csv"
    )
    context = []
    for sid in IDS:
        previous = table(old.loc[column(old, "strategy_id") == sid])
        positive = table(
            fixed.loc[(column(fixed, "strategy_id") == sid) & (column(fixed, "net_PnL_USD") > 0)]
        )
        prior = table(v1.loc[column(v1, "strategy_id") == sid])
        context.append(
            {
                "strategy_id": sid,
                "retained": True,
                "V1_net_USD": float(column(prior, "net_PnL_USD").iloc[0]),
                "V2_positive_exact_variants": "|".join(str(x) for x in column(positive, "variant")),
                "V3_positive_exact_regimes": "|".join(
                    str(r.regime) for r in as_rows(previous) if r.net_PnL_USD > 0
                ),
                "final_variant_status": "COMPLETE"
                if sid in TREATMENTS
                else "NO_NEW_FUNDED_VARIANT",
                "role": "FUNDED_MECHANISM"
                if sid in TREATMENTS
                else ("COMPACT_NONFUNDED_CONTEXT" if sid == "M06" else "HISTORICAL_CONTEXT"),
            }
        )
    csv_write(out / "ALL18_CONTEXT_AND_FINAL_DIAGNOSTIC_MATRIX.csv", context)
    publish(
        out / "ANALYSIS_RECEIPT.json",
        {
            "status": "PASS",
            "accounts": len(summary),
            "cohorts": len(trades),
            "physical_fill_rows": len(physical),
            "paired_rows": len(pairs),
            "offline": offline,
            "wall_seconds": time.monotonic() - start,
            "funded_wall_seconds": receipt["elapsed_seconds"],
            "files": {p.name: digest(p) for p in sorted(out.iterdir())},
        },
    )


if __name__ == "__main__":
    run_analysis()
