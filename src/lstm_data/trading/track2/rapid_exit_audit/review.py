"""Read-only candidate hierarchy, reconstruction checks and compact dive inputs."""

from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

from ..rapid_v1.paths import publish
from ..rapid_v1.strategies import IDS
from ..rapid_v2_diagnostics.report import csv_write
from .io import column, csv_at, drawdown, near, table
from .offline import HORIZONS, clock

D = Decimal


def prior_positives(s: dict) -> tuple[list[dict], list[dict]]:
    v1 = csv_at(Path(s["V1_results"]) / "SUMMARY_18_STRATEGIES.csv")
    rows = []
    for name in ("HEADROOM_RESULTS.csv", "HORIZON_RESULTS.csv"):
        for r in csv_at(Path(s["V2_results"]) / name):
            net = D(r["net_PnL_USD"])
            cost = sum(
                D(r[k])
                for k in (
                    "commission_USD",
                    "assumed_spread_USD",
                    "assumed_impact_USD",
                    "borrow_USD",
                    "funding_USD",
                )
            )
            near(
                D(r["gross_signed_price_PnL_USD"]) + D(r["gross_action_value_USD"]) - cost,
                net,
                "V2_ACCOUNT_BRIDGE",
            )
            if net > 0:
                rows.append({"study": "V2", "label": r["variant"], **r})
    summary = csv_at(Path(s["funded"]) / "V3_ALL54_SUMMARY.csv")
    rows.extend(
        {"study": "V3", "label": r["regime"], **r} for r in summary if D(r["net_PnL_USD"]) > 0
    )
    if len(rows) != 5 or any(D(r["net_PnL_USD"]) >= 0 for r in v1):
        raise ValueError("FROZEN_POSITIVE_REFERENCE_CENSUS")
    return rows, summary


def raw_cohorts(frame: pd.DataFrame, summary: list[dict]) -> tuple[pd.DataFrame, list[dict]]:
    first = table(frame[column(frame, "horizon") == "T60"]).copy()
    first["signed_original_entry_units"] = column(first, "quantity") / column(
        first, "existing_split_factor"
    )
    first["raw_gross_part"] = column(first, "quantity") * column(first, "raw") - column(
        first, "signed_original_entry_units"
    ) * column(first, "actual_entry_raw")
    c = clock()
    first = first.sort_values(["case", "lot", "effective", "posted"])
    first["risk_leg"] = column(first, "cause").str.startswith("RISK_")
    group_keys = ["case", "strategy_id", "regime", "lot"]
    cohorts = table(
        first.groupby(group_keys, sort=True).agg(
            ticker=("ticker", "first"),
            symbol=("symbol", "first"),
            quantity=("quantity", "first"),
            origin=("origin", "first"),
            entry=("entry", "first"),
            exit=("effective", "last"),
            entry_strength=("entry_strength", "first"),
            exit_strength=("exit_strength", "last"),
            entry_units=("signed_original_entry_units", "sum"),
            gross_raw=("raw_gross_part", "sum"),
            cause=("cause", "last"),
            partial_exit_legs=("leg_id", "size"),
            risk_any=("risk_leg", "max"),
        )
    ).reset_index()
    risk_rows = table(first.loc[column(first, "risk_leg")])
    risk_first = table(
        risk_rows.groupby(group_keys, sort=True).agg(first_risk=("cause", "first"))
    ).reset_index()
    cohorts = cohorts.merge(risk_first, on=group_keys, how="left", validate="one_to_one")
    cohorts["cause"] = column(cohorts, "first_risk").fillna(column(cohorts, "cause"))
    cohorts["side"] = np.where(column(cohorts, "quantity") > 0, "LONG", "SHORT")
    cohorts["scheduled_age"] = [
        c.index(int(end)) - c.index(int(entry))
        for end, entry in zip(column(cohorts, "exit"), column(cohorts, "entry"), strict=True)
    ]
    cohorts["calendar_age"] = column(cohorts, "exit") - column(cohorts, "entry")
    support = []
    for r in summary:
        b = table(
            cohorts[
                (column(cohorts, "strategy_id") == r["strategy_id"])
                & (column(cohorts, "regime") == r["regime"])
            ]
        )
        residual = float(column(b, "gross_raw").sum()) - float(r["gross_signed_price_PnL_USD"])
        supported = abs(residual) <= 1e-6
        support.append(
            {
                "strategy_id": r["strategy_id"],
                "regime": r["regime"],
                "cohorts": len(b),
                "archived": r["closed_cohorts"],
                "raw_residual_USD": residual,
                "status": "RECONSTRUCTED_RAW_ONLY" if supported else "COHORT_RAW_NOT_IDENTIFIABLE",
            }
        )
        if len(b) != int(r["closed_cohorts"]):
            raise ValueError("RAW_COHORT_CENSUS")
    return cohorts, support


def matrix(out: Path, summary: list[dict], positives: list[dict]) -> tuple[list[dict], list[str]]:
    stats = csv_at(out / "ALL18_POST_EXIT_EXTENSIONS.csv")
    matrix_rows = []
    for sid in IDS:
        base = [r for r in summary if r["strategy_id"] == sid]
        horizons = []
        qualifying_cells = []
        concentration_cells = []
        broad_regimes = []
        for regime in ("CONSERVATIVE", "STANDARD", "HIGH_RISK"):
            qualified = 0
            for horizon in HORIZONS:
                a = next(
                    r
                    for r in stats
                    if r["strategy_id"] == sid
                    and r["regime"] == regime
                    and r["horizon"] == horizon
                    and r["axis"] == "feasible_external"
                    and r["label"] == "UNFUNDED_NONFORCED_EXTERNAL"
                )
                # Year support uses all nonforced external rows, computed independently below.
                qualified += bool(
                    int(a["valid"]) >= 100
                    and float(a["signed_raw_USD"] or 0) > 0
                    and float(a["conditional_standalone_USD"] or 0) > 0
                )
                if (
                    int(a["valid"]) >= 100
                    and float(a["signed_raw_USD"] or 0) > 0
                    and (float(a["conditional_standalone_USD"] or 0) > 0)
                ):
                    qualifying_cells.append(regime + "/" + horizon)
                    if (
                        float(a.get("raw_less_top_5_positive_USD") or 0) > 0
                        and float(a.get("raw_less_top_2_stock_USD") or 0) > 0
                    ):
                        concentration_cells.append(regime + "/" + horizon)
                horizons.append(a)
            if qualified >= 2:
                broad_regimes.append(regime)
        own = [r for r in positives if r["strategy_id"] == sid]
        robust = sum(
            int(a["valid"]) >= 100
            and float(a.get("raw_less_top_5_positive_USD") or 0) > 0
            and float(a.get("raw_less_top_2_stock_USD") or 0) > 0
            for a in horizons
        )
        matrix_rows.append(
            {
                "strategy_id": sid,
                "mode": base[0]["mode"],
                "actual_label": "ACTUAL_POSITIVE_EXPLORATORY" if own else "",
                "exact_funded_positive_configs": "|".join(
                    r["study"] + "/" + r["label"] for r in own
                ),
                "diagnostic_label": "CANDIDATE_PENDING_YEAR_CHECK"
                if len(broad_regimes) >= 2
                else "NEGATIVE_OR_INCONCLUSIVE",
                "qualifying_regimes": "|".join(broad_regimes),
                "raw_cost_supported_cells": "|".join(qualifying_cells),
                "raw_concentration_supported_cells": "|".join(concentration_cells),
                "concentration_supported_cells": robust,
                "V3_net_conservative": base[0]["net_PnL_USD"],
                "V3_net_standard": base[1]["net_PnL_USD"],
                "V3_net_high_risk": base[2]["net_PnL_USD"],
                "deep_dive": "MANDATORY"
                if sid in ("M04", "R07")
                else "R01_DELTA_ONLY"
                if sid == "R01"
                else "PENDING",
            }
        )
    return matrix_rows, []


def source_year_support(frame: pd.DataFrame, rows: list[dict]) -> list[str]:
    selected = []
    for r in rows:
        sid = r["strategy_id"]
        matched = []
        f = table(
            frame[
                (column(frame, "strategy_id") == sid)
                & (column(frame, "feasible_external") == "UNFUNDED_NONFORCED_EXTERNAL")
                & (column(frame, "valid") == 1)
            ]
        )
        for key, group in f.groupby(["regime", "horizon"]):
            if not isinstance(key, tuple) or len(key) != 2:
                raise ValueError("CELL_GROUP_SCHEMA")
            regime, horizon = key
            g = table(group)
            by_year = table(
                g.groupby("exit_year")[["price_raw_to_raw", "conditional_standalone_net"]].sum()
            )
            years = int(
                (
                    (column(by_year, "price_raw_to_raw") > 0)
                    & (column(by_year, "conditional_standalone_net") > 0)
                ).sum()
            )
            cell = str(regime) + "/" + str(horizon)
            if years >= 2 and cell in str(r["raw_cost_supported_cells"]).split("|"):
                matched.append(cell)
        r["year_supported_cells"] = "|".join(matched)
        two_horizons = all(
            sum(key.startswith(regime + "/") for key in matched) >= 2
            for regime in str(r["qualifying_regimes"]).split("|")
            if regime
        )
        qualifies = bool(
            r["qualifying_regimes"]
            and two_horizons
            and len(set(matched) & set(str(r["raw_concentration_supported_cells"]).split("|"))) >= 2
        )
        r["diagnostic_label"] = (
            "DIAGNOSTICALLY_INTERESTING" if qualifies else "NEGATIVE_OR_INCONCLUSIVE"
        )
        if sid not in ("M04", "R07", "R01") and qualifies and len(selected) < 3:
            r["deep_dive"] = "ADDITIONAL_MECHANISM"
            selected.append(sid)
        elif r["deep_dive"] == "PENDING":
            r["deep_dive"] = "COMPACT_CONTEXT"
        r["evidence_quality"] = (
            "MEDIUM_AGGREGATES_AND_OFFLINE"
            if r["actual_label"] or qualifies
            else "LOW_ECONOMIC_OR_MECHANISM_SUPPORT"
        )
    return selected


def deep_inputs(
    out: Path,
    frame: pd.DataFrame,
    cohorts: pd.DataFrame,
    support: list[dict],
    s: dict,
    selected: list[str],
    summary: list[dict],
) -> None:
    ids = ["M04", "R07", *selected]
    exact = csv_at(Path(s["funded"]) / "V3_ANNUAL_CAUSAL_DIAGNOSTICS.csv")
    reasons = csv_at(Path(s["funded"]) / "V3_EXIT_REASONS.csv")
    daily = pd.read_parquet(Path(s["funded"]) / "DAILY_NAV.parquet")
    v2 = Path(s["V2_results"])
    view = []
    for sid in ids:
        for r in summary:
            if r["strategy_id"] != sid:
                continue
            regime = r["regime"]
            b = table(
                cohorts[
                    (column(cohorts, "strategy_id") == sid) & (column(cohorts, "regime") == regime)
                ]
            )
            raw_ok = next(x for x in support if x["strategy_id"] == sid and x["regime"] == regime)
            view.append({"strategy_id": sid, "view": "account_summary", **r, **raw_ok})
            d = table(
                daily[(column(daily, "strategy_id") == sid) & (column(daily, "regime") == regime)]
            )
            previous = 100000.0
            for label, g0 in d.groupby(pd.to_datetime(column(d, "date")).dt.to_period("M")):
                g = table(g0)
                end = float(column(g, "nav").iloc[-1])
                view.append(
                    {
                        "strategy_id": sid,
                        "regime": regime,
                        "view": "daily_NAV_month",
                        "label": str(label),
                        "NAV_change_USD": end - previous,
                        "return": end / previous - 1,
                    }
                )
                previous = end
            view.append(
                {
                    "strategy_id": sid,
                    "regime": regime,
                    "view": "drawdown_episode",
                    **drawdown(column(d, "nav"), column(d, "date"), 100000.0),
                }
            )
            if raw_ok["status"] != "RECONSTRUCTED_RAW_ONLY":
                continue
            b["exit_year"] = (
                pd.to_datetime(column(b, "exit").to_numpy(np.int64) * 60, unit="s", utc=True)
                .strftime("%Y")
                .astype(int)
            )
            b["entry_month"] = pd.to_datetime(
                column(b, "entry").to_numpy(np.int64) * 60, unit="s", utc=True
            ).strftime("%Y-%m")
            b["holding"] = np.select(
                [
                    column(b, "scheduled_age") <= 240,
                    column(b, "scheduled_age") <= 390,
                    column(b, "scheduled_age") <= 1950,
                ],
                ["le240", "241to390", "391to1950"],
                default="1951plus",
            )
            for k in (1, 5, 10, 20):
                gross = column(b, "gross_raw").to_numpy(float)
                high = np.sort(gross[gross > 0])[-k:]
                low = np.sort(gross[gross < 0])[:k]
                view.append(
                    {
                        "strategy_id": sid,
                        "regime": regime,
                        "view": "raw_tail_arithmetic",
                        "label": str(k),
                        "top_gross": float(high.sum()),
                        "bottom_gross": float(low.sum()),
                        "raw_less_top": float(gross.sum() - high.sum()),
                        "account_net_less_raw_top_fixed_other_components": float(r["net_PnL_USD"])
                        - float(high.sum()),
                        "gross_hit_rate": float(np.mean(gross > 0)),
                        "gross_median": float(np.median(gross)),
                        "average_gross_winner": float(gross[gross > 0].mean()),
                        "average_gross_loser": float(gross[gross < 0].mean()),
                    }
                )
            for axis in ("symbol", "side", "cause", "entry_month", "holding", "exit_year"):
                for label, g0 in b.groupby(axis):
                    g = table(g0)
                    view.append(
                        {
                            "strategy_id": sid,
                            "regime": regime,
                            "view": "raw_cohort",
                            "axis": axis,
                            "label": str(label),
                            "cohorts": len(g),
                            "gross_raw": float(column(g, "gross_raw").sum()),
                            "median_scheduled_age": float(column(g, "scheduled_age").median()),
                        }
                    )
            other = table(cohorts[column(cohorts, "strategy_id") == sid])
            for alternative in ("STANDARD", "HIGH_RISK"):
                if regime != "CONSERVATIVE":
                    continue
                a = b.set_index(["origin", "ticker", "side"])
                c = table(other[column(other, "regime") == alternative]).set_index(
                    ["origin", "ticker", "side"]
                )
                common = a.index.intersection(c.index)
                x, y = table(a.loc[common]), table(c.loc[common])
                view.append(
                    {
                        "strategy_id": sid,
                        "regime": alternative,
                        "view": "shared_vs_conservative",
                        "shared": len(common),
                        "only_conservative": len(a) - len(common),
                        "only_comparator": len(c) - len(common),
                        "shared_gross_conservative": float(column(x, "gross_raw").sum()),
                        "shared_gross_comparator": float(column(y, "gross_raw").sum()),
                        "first_entry_time_changed": int(
                            (column(x, "entry") != column(y, "entry")).sum()
                        ),
                        "last_exit_time_changed": int(
                            (column(x, "exit") != column(y, "exit")).sum()
                        ),
                    }
                )
        for r in exact:
            if r["strategy_id"] == sid:
                view.append({"view": "exact_frozen_V3_cohort_aggregate", **r})
        for r in reasons:
            if r["strategy_id"] == sid:
                view.append({"view": "exact_frozen_V3_exit_cause", **r})
        for file in ("ANNUAL_RESULTS.csv", "ANNUAL_AND_MECHANISM_TABLES.csv"):
            for r in csv_at(v2 / file):
                if r["strategy_id"] == sid:
                    view.append({"view": "exact_frozen_V2_" + file.replace(".csv", ""), **r})
        csv_write(
            out / (sid + "_DEEP_DIVE_TABLES.csv"), [r for r in view if r["strategy_id"] == sid]
        )
    csv_write(out / "COHORT_RAW_RECONSTRUCTION_SUPPORT.csv", support)


def analyze(out: Path, frame: pd.DataFrame, s: dict) -> None:
    positives, summary = prior_positives(s)
    csv_write(out / "PRIOR_FUNDED_POSITIVE_CONFIGURATIONS.csv", positives)
    cohorts, support = raw_cohorts(frame, summary)
    rows, _ = matrix(out, summary, positives)
    selected = source_year_support(frame, rows)
    for r in rows:
        own = [x for x in support if x["strategy_id"] == r["strategy_id"]]
        r["cohort_raw_support"] = "|".join(x["regime"] + ":" + x["status"] for x in own)
    csv_write(out / "ALL18_CANDIDATE_EVIDENCE_MATRIX.csv", rows)
    deep_inputs(out, frame, cohorts, support, s, selected, summary)
    publish(
        out / "CANDIDATE_REVIEW_RECEIPT.json",
        {
            "mandatory": ["M04", "R07"],
            "additional": selected,
            "R01": "DELTA_ONLY",
            "all18": list(IDS),
            "funded_positive_configurations": len(positives),
            "cohort_reconstruction": {
                k: sum(r["status"] == k for r in support) for k in {r["status"] for r in support}
            },
            "new_funded_runs": 0,
        },
    )
