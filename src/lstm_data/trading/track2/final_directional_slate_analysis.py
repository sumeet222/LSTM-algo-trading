"""Post-seal analysis only; never imported by the frozen online overlay engines."""

import time
from pathlib import Path

import numpy as np
import pandas as pd

from .final_directional_slate.common import CACHE, POLICIES, ROOT, load
from .final_directional_slate.risk_inputs import RiskInputs
from .rapid_exit_audit.io import as_rows, column, table
from .rapid_v1.paths import digest, publish
from .rapid_v1.shared_features import FeatureCache
from .rapid_v1.strategies import evaluate
from .rapid_v2_diagnostics.report import csv_write
from .stage012.model_registry import SYMBOLS


def run_path(pop: str) -> Path:
    return ROOT / "runs" / ("sizing-" + pop.lower() + "-20261110-r1")


def verify_run(pop: str) -> dict:
    p = run_path(pop)
    r = load(p / "RUN_RECEIPT.json")
    if r["status"] != "COMPLETE" or r["sessions"] != 1005:
        raise ValueError("SIZING_RUN_NOT_COMPLETE " + pop)
    for name, h in load(p / "results/OUTPUT_MANIFEST.json")["files"].items():
        if digest(p / "results" / name) != h:
            raise ValueError("SIZING_RESULT_DRIFT " + name)
    return r


def merge_results() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frames = []
    daily = []
    trades = []
    physical = []
    for pop in ("MATCHED", "ATTAINABLE"):
        verify_run(pop)
        p = run_path(pop) / "results"
        frames.append(pd.read_csv(p / "RESULTS.csv"))
        daily.append(pd.read_parquet(p / "DAILY_NAV.parquet"))
        cohort = pd.read_parquet(p / "COHORTS.parquet")
        lookup = {r.strategy_id + "_" + r.variant: r.arm for r in as_rows(frames[-1])}
        populations = {r.strategy_id + "_" + r.variant: r.population for r in as_rows(frames[-1])}
        cohort["economic_mode"] = column(cohort, "population")
        cohort["population"] = column(cohort, "case").map(populations)
        cohort["book_arm"] = column(cohort, "arm")
        cohort["arm"] = column(cohort, "case").map(lookup)
        if column(cohort, "arm").isna().any():
            raise ValueError("UNBOUND_COHORT_CASE")
        trades.append(cohort)
        physical.append(pd.read_parquet(p / "PHYSICAL_FILLS.parquet"))
    selected = load(ROOT / "SELECTION_RECEIPT.json")["selected"]
    parents = pd.read_csv(ROOT / "FIVE_CANDIDATE_FINANCIAL_COMPARISON.csv")
    parent_days = pd.read_parquet(ROOT / "CANDIDATE_DAILY_NAV.parquet")
    reused = []
    for fid in selected:
        r = next(r for r in as_rows(parents) if r.candidate == fid)
        reused.append(
            {
                **vars(r),
                "candidate": fid,
                "population": "ATTAINABLE",
                "arm": "EQUAL",
                "source_reuse": "EXACT_FROZEN_ORIGINAL_ACCOUNT",
            }
        )
        day = table(parent_days.loc[column(parent_days, "candidate") == fid]).copy()
        day["population"] = "ATTAINABLE"
        day["arm"] = "EQUAL"
        daily.append(day)
    frames.append(pd.DataFrame(reused))
    return (
        pd.concat(frames, ignore_index=True),
        pd.concat(daily, ignore_index=True),
        pd.concat(trades, ignore_index=True),
        pd.concat(physical, ignore_index=True),
    )


def collect() -> None:
    start = time.monotonic()
    out = ROOT / "analysis_03"
    out.mkdir(exist_ok=False)
    summary, days, trades, physical = merge_results()
    checks = []
    concentration = []
    attribute = []
    annual = []
    differences = []
    # Never use a zero/unfilled row as a filled trade; record its denominator separately.
    filled = table(trades.loc[column(trades, "entry_at").notna()])
    for r in as_rows(summary):

        def choose(d: pd.DataFrame) -> pd.DataFrame:
            return table(
                d.loc[
                    (column(d, "candidate") == r.candidate)
                    & (column(d, "population") == r.population)
                    & (column(d, "arm") == r.arm)
                ]
            )

        d = choose(days)
        if len(d) != 1005 or column(d, "nav").isna().any():
            raise ValueError("DAILY_OUTCOME_HOLD")
        nav = column(d, "nav").to_numpy(float)
        if not np.isfinite(nav).all() or np.any(nav <= 0):
            raise ValueError("INVALID_NAV")
        ret = nav / np.r_[100000.0, nav[:-1]] - 1
        downside = float(np.sqrt(np.mean(np.minimum(ret, 0) ** 2)))
        idx = (
            (column(summary, "candidate") == r.candidate)
            & (column(summary, "population") == r.population)
            & (column(summary, "arm") == r.arm)
        )
        summary.loc[idx, "Sortino_daily_downside_RMS_252"] = float(
            ret.mean() / downside * np.sqrt(252)
        )
        summary.loc[idx, "risk_closed_cohorts"] = getattr(r, "risk_closed_cohorts", np.nan)
        # The fixed ledger's any-risk cohort count is its supported alternative.
        if not np.isfinite(float(getattr(r, "risk_closed_cohorts", np.nan))):
            summary.loc[idx, "risk_closed_cohorts"] = r.cohorts_with_risk_fill
        bridge = (
            r.gross_signed_price_PnL_USD
            + r.gross_action_value_USD
            - r.commission_USD
            - r.assumed_spread_USD
            - r.assumed_impact_USD
            - r.borrow_USD
            - r.funding_USD
            - r.net_PnL_USD
        )
        if abs(bridge) > 1e-7 or abs(nav[-1] - 100000 - r.net_PnL_USD) > 1e-7:
            raise ValueError("ACCOUNT_BRIDGE_HOLD")
        checks.append(
            {
                "candidate": r.candidate,
                "population": r.population,
                "arm": r.arm,
                "scope": "ACCOUNT",
                "residual": bridge,
                "status": "PASS",
            }
        )
        if not (r.population == "ATTAINABLE" and r.arm == "EQUAL"):
            t = choose(filled)
            p = choose(physical)
            for name, wanted in (
                ("cash_pnl", r.net_PnL_USD),
                ("gross_signed_price_pnl", r.gross_signed_price_PnL_USD),
                ("gross_action_cash", r.gross_action_value_USD),
            ):
                if column(t, name).isna().any():
                    raise ValueError("MISSING_COHORT_VALUE")
                delta = float(column(t, name).sum()) - float(wanted)
                if abs(delta) > 1e-7:
                    raise ValueError("COHORT_NET_GROSS_ACTION_BRIDGE")
                checks.append(
                    {
                        "candidate": r.candidate,
                        "population": r.population,
                        "arm": r.arm,
                        "scope": name,
                        "residual": delta,
                        "status": "PASS",
                    }
                )
            notional = abs(column(p, "shares")) * column(p, "external_price")
            for name, wanted in (
                ("commission", r.commission_USD),
                ("print_slippage", r.assumed_spread_USD),
                ("impact", r.assumed_impact_USD),
            ):
                delta = float(column(p, name).sum()) - float(wanted)
                if abs(delta) > 1e-7:
                    raise ValueError("PHYSICAL_COMPONENT_BRIDGE " + r.candidate + " " + name)
                checks.append(
                    {
                        "candidate": r.candidate,
                        "population": r.population,
                        "arm": r.arm,
                        "scope": name,
                        "residual": delta,
                        "status": "PASS",
                    }
                )
            if len(set(column(p, "order_id"))) != r.external_orders:
                raise ValueError("PHYSICAL_ORDER_COUNT")
            if abs(float(notional.sum()) - r.executed_turnover_USD) > 1e-7:
                raise ValueError("PHYSICAL_NOTIONAL_BRIDGE")
            names = column(table(t.groupby("ticker")[["cash_pnl"]].sum()), "cash_pnl")
            best = names.loc[names > 0].sort_values(ascending=False).head(2)
            concentration.append(
                {
                    "candidate": r.candidate,
                    "population": r.population,
                    "arm": r.arm,
                    "cohorts": len(t),
                    "net_USD": r.net_PnL_USD,
                    "top_two_symbols": "|".join(SYMBOLS[int(j)] for j in best.index),
                    "top_two_net_USD": float(best.sum()),
                    "net_without_top_two_ARITHMETIC_ONLY": r.net_PnL_USD - float(best.sum()),
                    "best_five_net": float(column(t, "cash_pnl").nlargest(5).sum()),
                    "worst_five_net": float(column(t, "cash_pnl").nsmallest(5).sum()),
                    "net_winners": float(
                        column(t, "cash_pnl").where(column(t, "cash_pnl") > 0, 0).sum()
                    ),
                    "net_losers": float(
                        column(t, "cash_pnl").where(column(t, "cash_pnl") < 0, 0).sum()
                    ),
                }
            )
            for axis in ("ticker", "direction", "cause"):
                for label, block in t.groupby(axis):
                    z = table(block)
                    attribute.append(
                        {
                            "candidate": r.candidate,
                            "population": r.population,
                            "arm": r.arm,
                            "axis": axis,
                            "label": str(label),
                            "cohorts": len(z),
                            "gross_price": float(column(z, "gross_signed_price_pnl").sum()),
                            "actions": float(column(z, "gross_action_cash").sum()),
                            "net": float(column(z, "cash_pnl").sum()),
                        }
                    )
        previous_nav = 100000.0
        previous_cost = {k: 0.0 for k in ("commission", "friction", "borrow", "funding")}
        for year, block in d.groupby(column(d, "date").astype(str).str.slice(0, 4)):
            z = table(block)
            last = z.iloc[-1]
            costs = {k: float(last[k]) - previous_cost[k] for k in previous_cost}
            annual.append(
                {
                    "candidate": r.candidate,
                    "population": r.population,
                    "arm": r.arm,
                    "year": str(year),
                    "net_NAV_change": float(last["nav"]) - previous_nav,
                    "return": float(last["nav"]) / previous_nav - 1,
                    **costs,
                }
            )
            previous_nav = float(last["nav"])
            previous_cost = {k: float(last[k]) for k in previous_cost}
    selected = load(ROOT / "SELECTION_RECEIPT.json")["selected"]
    for fid in selected:
        for pop in ("MATCHED", "ATTAINABLE"):
            group = table(
                summary.loc[
                    (column(summary, "candidate") == fid) & (column(summary, "population") == pop)
                ]
            )
            a = {r.arm: r for r in as_rows(group)}
            s = a["S2C_RISK"]
            for reference in ("EQUAL", "ROLLING_RISK", "EWMA_RISK"):
                r = a[reference]
                x = table(
                    days.loc[
                        (column(days, "candidate") == fid)
                        & (column(days, "population") == pop)
                        & (column(days, "arm") == "S2C_RISK")
                    ]
                )
                y = table(
                    days.loc[
                        (column(days, "candidate") == fid)
                        & (column(days, "population") == pop)
                        & (column(days, "arm") == reference)
                    ]
                )
                if list(column(x, "date")) != list(column(y, "date")):
                    raise ValueError("PAIRED_DAY_CENSUS")
                sx = column(x, "nav").to_numpy(float)
                sy = column(y, "nav").to_numpy(float)
                dr = sx / np.r_[100000.0, sx[:-1]] - sy / np.r_[100000.0, sy[:-1]]
                differences.append(
                    {
                        "candidate": fid,
                        "population": pop,
                        "reference_arm": reference,
                        "source_opportunities_paired": pop == "MATCHED",
                        "S2C_minus_reference_net_USD": s.net_PnL_USD - r.net_PnL_USD,
                        "S2C_minus_reference_exposure_normalized": (
                            s.net_per_1M_RTH_gross_dollar_years_USD
                            - r.net_per_1M_RTH_gross_dollar_years_USD
                        ),
                        "daily_difference_observations": len(dr),
                        "mean_daily_return_difference": float(dr.mean()),
                        "daily_difference_sd": float(dr.std(ddof=1)),
                        "annualized_arithmetic_difference_DESCRIPTIVE": float(dr.mean() * 252),
                        "compound_NAV_difference_USD": s.final_NAV_USD - r.final_NAV_USD,
                        "NOT_INDEPENDENT_STATISTICAL_TEST": True,
                    }
                )
    summary.to_csv(ROOT / "FOUR_ARM_S2C_SIZING_RESULTS.csv", index=False)
    csv_write(out / "RECONCILIATION.csv", checks)
    csv_write(out / "CONCENTRATION_AND_TAILS.csv", concentration)
    csv_write(out / "COHORT_ATTRIBUTION.csv", attribute)
    csv_write(out / "ANNUAL_NAV_AND_COSTS.csv", annual)
    csv_write(out / "S2C_PAIRED_RETURN_CONTRASTS.csv", differences)
    days.to_parquet(out / "COMBINED_DAILY_NAV.parquet", index=False, compression="zstd")
    coverage = pd.read_csv(ROOT / "RISK_OPPORTUNITY_COUNTS.csv")
    info = []
    for r in as_rows(summary):
        z = table(
            coverage.loc[
                (column(coverage, "candidate") == r.candidate)
                & (column(coverage, "population") == r.population)
                & (column(coverage, "arm") == r.arm)
            ]
        )
        count = {x.status: int(x.count) for x in as_rows(z)}
        info.append(
            {
                "candidate": r.candidate,
                "population": r.population,
                "arm": r.arm,
                "risk_ready_original_alpha_keys": count.get("READY", 0),
                "risk_missing_original_alpha_keys": count.get("MISSING", 0),
                "filled_cohorts": r.cohorts,
                "physical_orders": r.external_orders,
                "comparison": "COMMON_CAUSAL_BASE"
                if r.population == "MATCHED"
                else "NONPAIRED_SECONDARY",
            }
        )
    csv_write(ROOT / "S2C_MATCHED_VS_ATTAINABLE.csv", info)
    # Aggregate matched executed-key divergence, no outcome-conditioned opportunity selection.
    divergence = []
    matched = table(filled.loc[column(filled, "population") == "MATCHED"])
    for fid in selected:
        z = table(matched.loc[column(matched, "candidate") == fid])
        maps = {}
        for arm, block in z.groupby("arm"):
            maps[str(arm)] = {
                (int(r.origin), int(r.ticker), int(r.direction)): r for r in as_rows(table(block))
            }
        for ref in ("EQUAL", "ROLLING_RISK", "EWMA_RISK"):
            a, b = maps[ref], maps["S2C_RISK"]
            both = a.keys() & b.keys()
            divergence.append(
                {
                    "candidate": fid,
                    "population": "MATCHED",
                    "reference_arm": ref,
                    "both_entered": len(both),
                    "reference_only": len(a.keys() - b.keys()),
                    "S2C_only": len(b.keys() - a.keys()),
                    "shared_exit_timestamp_changed": sum(
                        a[k].exit_at != b[k].exit_at for k in both
                    ),
                    "shared_entry_notional_changed": sum(
                        a[k].entry_notional_raw_USD != b[k].entry_notional_raw_USD for k in both
                    ),
                    "source_opportunity_base_identical": True,
                    "funded_selection_is_endogenous": True,
                }
            )
    csv_write(out / "PAIRED_FUNDED_PATH_DIVERGENCE.csv", divergence)
    decile_diagnostic(out)
    publish(
        out / "ANALYSIS_MANIFEST.json",
        {
            "status": "PASS",
            "rows": len(summary),
            "selected": selected,
            "new_accounts": 21,
            "archived_equal_reuses": 3,
            "wall_seconds": time.monotonic() - start,
            "null_sizing": "NOT_RUN_NO_PREAPPROVED_SIGN_INDEPENDENT_MODULE",
            "files": {str(p): digest(p) for p in sorted(out.iterdir())},
            "summary_sha256": digest(ROOT / "FOUR_ARM_S2C_SIZING_RESULTS.csv"),
        },
    )


def decile_diagnostic(out: Path) -> None:
    risk = RiskInputs()
    cache = FeatureCache(
        Path(
            "trading/track2/rapid_v1/cache/49a590a7d44f5900b67cf2faf37584b584a942807cca2fbab262250b80ea1f93"
        )
    )
    geo = pd.read_parquet(CACHE / "movement_geometry.parquet")
    time = (
        pd.DatetimeIndex(column(geo, "entry_end_utc")).as_unit("ns").astype("int64").to_numpy()
        // 60_000_000_000
    )
    end = (
        pd.DatetimeIndex(column(geo, "exit_end_utc")).as_unit("ns").astype("int64").to_numpy()
        // 60_000_000_000
    )
    rows = {int(t): i for i, t in enumerate(time)}
    moves = np.load(CACHE / "matured_source_moves.npy", mmap_mode="r")
    points = []
    selected = load(ROOT / "SELECTION_RECEIPT.json")["selected"]
    for date in sorted(cache.by_date):
        if not "2021-01-01" <= date <= "2024-12-31":
            continue
        for f in cache.frames(date):
            i = risk.index[f.origin]
            m = rows.get(f.origin)
            for fid in selected:
                for it in evaluate(POLICIES[fid]["strategy"], f).intents:
                    j = it.tickers[0]
                    a = risk.data["magnitude"][i, j]
                    if not np.isfinite(a):
                        continue
                    y = (
                        abs(float(moves[m, j]))
                        if m is not None and end[m] <= 28928159
                        else float("nan")
                    )
                    points.append(
                        {"candidate": fid, "forecast": a, "future_nominal_240_abs_move": y}
                    )
    d = pd.DataFrame(points)
    result = []
    for fid, block in d.groupby("candidate"):
        z = table(block).copy()
        # Quantile bins use forecasts, not label availability; this is postrun-only.
        labels = pd.qcut(column(z, "forecast"), 10, labels=False, duplicates="drop")
        if not isinstance(labels, pd.Series):
            raise ValueError("POSTHOC_DECILE_SCHEMA")
        z["decile"] = labels.to_numpy(float) + 1
        for rank, group in z.groupby("decile"):
            g = table(group)
            y = column(g, "future_nominal_240_abs_move")
            result.append(
                {
                    "candidate": str(fid),
                    "posthoc_decile": str(rank),
                    "forecasts": len(g),
                    "future_label_observed": int(y.notna().sum()),
                    "censored_future_label": int(y.isna().sum()),
                    "mean_forecast": float(column(g, "forecast").mean()),
                    "mean_nominal_240_abs_move": float(y.mean()),
                    "not_actual_holding_horizon": True,
                    "never_entry_eligibility": True,
                }
            )
    csv_write(out / "POSTHOC_MAGNITUDE_DECILES.csv", result)


if __name__ == "__main__":
    collect()
