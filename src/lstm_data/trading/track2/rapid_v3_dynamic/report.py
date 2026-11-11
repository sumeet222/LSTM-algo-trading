"""Compact funded outputs and source-bound closed-exit tape."""

import csv
import json
from collections import Counter
from pathlib import Path
from statistics import median

import numpy as np
import pandas as pd

from ..rapid_v1.paths import digest, publish
from ..rapid_v1.strategies import IDS
from ..rapid_v2_diagnostics.report import GROSS_BASIS, csv_write, summarize
from .engine import DynamicBatch
from .policy import REGIMES


def quantiles(counter: Counter) -> dict:
    if not counter:
        return {}
    keys = np.asarray(sorted(counter), dtype=int)
    counts = np.cumsum([counter[k] for k in keys])
    return {
        f"p{p}": int(keys[np.searchsorted(counts, (p * int(counts[-1]) + 99) // 100)])
        for p in (25, 50, 75, 90)
    }


def result_rows(engine: DynamicBatch) -> list[dict]:
    rows = []
    for a in engine.dynamic_accounts:
        row = summarize(engine, a)
        c = a.totals
        risk = int(c.get("risk_closed", 0))
        count = int(row["closed_cohorts"])
        realized = c.get("policy_closed", 0) + risk
        if realized != count:
            raise ValueError("MISSING_COHORT_EXIT_REASON:" + a.arm)
        turnover = row["executed_turnover_USD"]
        net = row["net_PnL_USD"]
        row.update(
            {
                "regime": a.regime,
                "name_cap": a.name_cap,
                "risk_closed_cohorts": risk,
                "risk_exit_share": risk / count if count else None,
                "risk_before_240": c.get("risk_before_240", 0),
                "policy_before_240": c.get("policy_before_240", 0),
                "name_breach_decisions": a.causes["observed:NAME_CAP"],
                "vintage_breach_decisions": a.causes["observed:VINTAGE_CAP"],
                "other_cap_breach_decisions": sum(
                    a.causes["observed:" + s]
                    for s in ("NONPOSITIVE_NAV", "GROSS_CAP", "RESTRICTED_CASH")
                ),
                "signed_arrival_USD": c.get("v3_signed_arrival", 0),
                "absolute_arrival_USD": c.get("v3_absolute_arrival", 0),
                "net_per_1M_turnover_USD": net * 1_000_000 / turnover
                if net is not None and turnover
                else None,
                "exit_leg_missing_source_delay": a.stats.counts["EXIT_LEG_MISSING_SOURCE_DELAY"],
                "trailing_raw_open_beyond_level": a.stats.counts[
                    "TRAILING_EXIT_BEYOND_STOP_THRESHOLD"
                ],
                "cooldown_rejections": a.rejected.get("V3_SIGNAL_COOLDOWN", 0),
                "max_age_cutoff": a.rejected.get("V3_MAXIMUM_HOLD_CALENDAR_CUTOFF", 0),
                "trail_scale_unavailable": a.stats.counts["V3_TRAIL_PREENTRY_SCALE_UNAVAILABLE"],
            }
        )
        daily = engine.daily_rows[a.arm]
        nav = float(a.initial)
        for year in sorted({r["date"][:4] for r in daily}):
            end = next(r["nav"] for r in reversed(daily) if r["date"].startswith(year))
            row[f"return_{year}"] = (
                float(end) / nav - 1
                if (end is not None and row["status"] != "HOLD" and nav > 0)
                else None
            )
            nav = float(end) if end is not None else float("nan")
        rows.append(row)
    return rows


def emit(engine: DynamicBatch, directory: Path, parents: dict) -> dict:
    rows = result_rows(engine)
    if {(r["strategy_id"], r["regime"]) for r in rows} != {
        (s, r) for s in IDS for r in REGIMES
    } or len(rows) != 54:
        raise ValueError("V3_CASE_AXIS")
    directory.mkdir(exist_ok=False, parents=True)
    csv_write(directory / "V3_ALL54_SUMMARY.csv", rows)
    csv_write(directory / "V3_RISK_REGIME_COMPARISON.csv", rows)
    reasons, annual, daily, exits = [], [], [], []
    for a, row in zip(engine.dynamic_accounts, rows, strict=True):
        keys = {
            "strategy_id": row["strategy_id"],
            "regime": a.regime,
            "mode": row["mode"],
            "status": row["status"],
            "gross_basis": GROSS_BASIS,
        }
        for cause, item in sorted(a.by_reason.items()):
            d = item["totals"]
            reasons.append(
                {
                    **keys,
                    "cause": cause,
                    **d,
                    "exit_share": float(d["cohorts"]) / int(row["closed_cohorts"]),
                    "overnight_fraction": d["overnight"] / d["cohorts"],
                    "at_least_390_scheduled_minutes_fraction": d["multi_day"] / d["cohorts"],
                    "mean_entry_strength": d["entry_strength"] / d["cohorts"],
                    "mean_aligned_exit_strength": d["exit_strength"] / d["exit_strength_known"]
                    if d["exit_strength_known"]
                    else None,
                    "simultaneous_triggers": json.dumps(item["triggers"], sort_keys=True),
                    **{f"{p}_wall_minutes": x for p, x in quantiles(item["wall"]).items()},
                    **{
                        f"{p}_scheduled_minutes": x for p, x in quantiles(item["scheduled"]).items()
                    },
                }
            )
        for key, values in sorted(a.breakdown.items()):
            axis, label = key.split("|", 1)
            annual.append({**keys, "axis": axis, "label": label, **values})
        for year in ("2021", "2022", "2023", "2024"):
            annual.append(
                {
                    **keys,
                    "axis": "account_year",
                    "label": year,
                    "NAV_return": row.get(f"return_{year}"),
                }
            )
        annual.extend(
            {**keys, "axis": "rejection", "label": k, "count": v}
            for k, v in sorted(a.rejected.items())
        )
        daily.extend(
            {**keys, **{k: float(x) if hasattr(x, "as_tuple") else x for k, x in d.items()}}
            for d in engine.daily_rows[a.arm]
        )
        exits.extend(a.exit_tape)
    if any(
        x["entry"] > x["effective"]
        or x["decision"] >= x["effective"]
        or x["posted"] < x["effective"] + 3
        for x in exits
    ):
        raise ValueError("EXIT_TAPE_CAUSAL_ORDER")
    csv_write(directory / "V3_EXIT_REASONS.csv", reasons)
    csv_write(directory / "V3_ANNUAL_CAUSAL_DIAGNOSTICS.csv", annual)
    pd.DataFrame(daily).to_parquet(directory / "DAILY_NAV.parquet", index=False, compression="zstd")
    pd.DataFrame(exits).to_parquet(
        directory / "SEALED_ACTUAL_EXIT_LEGS.parquet", index=False, compression="zstd"
    )
    references = []
    for version, path in (
        ("V1", Path(parents["V1_results"]) / "SUMMARY_18_STRATEGIES.csv"),
        ("V2", Path(parents["V2_results"]) / "HORIZON_RESULTS.csv"),
    ):
        table = pd.read_csv(path)
        for r in table.to_dict("records"):
            references.append(
                {
                    "version": version,
                    "strategy_id": r["strategy_id"],
                    "variant": r.get("variant", "H100_240"),
                    "gross_price_USD": r["gross_signed_price_PnL_USD"],
                    "action_value_USD": r["gross_action_value_USD"],
                    "net_USD": r["net_PnL_USD"],
                }
            )
    csv_write(directory / "IMMUTABLE_FIXED_REFERENCES.csv", references)
    max_residual = max(a.maximum_residual for a in engine.dynamic_accounts)
    a = {
        "cases": 54,
        "status_counts": dict(Counter(r["status"] for r in rows)),
        "cohort_closes": sum(int(r["closed_cohorts"]) for r in rows),
        "exit_legs": len(exits),
        "daily_rows": len(daily),
        "maximum_ledger_residual_USD": str(max_residual),
        "files": {p.name: digest(p) for p in sorted(directory.iterdir())},
    }
    publish(directory / "FUNDED_OUTPUT_MANIFEST.json", a)
    return a


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as stream:
        return list(csv.DictReader(stream))


def assess(directory: Path, offline: Path, target: Path) -> None:
    funded = read_csv(directory / "V3_ALL54_SUMMARY.csv")
    exits = read_csv(offline / "V3_POST_EXIT_EXTENSION.csv")
    compare = read_csv(directory / "IMMUTABLE_FIXED_REFERENCES.csv")
    lines = [
        "# Rapid V3 screening assessment",
        "",
        "Reused 2021–24. Fixed survivors, conditional shorts and actions, OHLCV price proxies.",
        "",
        "| ID | Conservative net USD | Standard net USD | High-risk net USD | V1 fixed net USD |",
        "|---|---:|---:|---:|---:|",
    ]
    for sid in IDS:
        data = {r["regime"]: r for r in funded if r["strategy_id"] == sid}
        ref = next(r for r in compare if r["strategy_id"] == sid and r["version"] == "V1")
        cells = [
            f"{float(data[r]['net_PnL_USD']):,.0f}" if data[r]["net_PnL_USD"] else data[r]["status"]
            for r in REGIMES
        ]
        lines.append(f"| {sid} | " + " | ".join(cells) + f" | {float(ref['net_USD']):,.0f} |")
    lines.extend(
        [
            "",
            "## Risk, exposure and churn",
            "",
            "| Mode | Regime | Positive | Risk exits | Median gross NAV | External orders | "
            "Median realized trading minutes |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for mode in ("MICRO_PRO", "RETAIL_CONSERVATIVE"):
        for regime in REGIMES:
            data = [r for r in funded if r["mode"] == mode and r["regime"] == regime]
            total, risk, orders = (
                sum(int(r[k]) for r in data)
                for k in (
                    "closed_cohorts",
                    "risk_closed_cohorts",
                    "external_orders",
                )
            )
            gross = median(float(r["mean_RTH_marked_gross_fraction"]) for r in data)
            held = median(
                float(r["median_scheduled_minutes"]) for r in data if r["median_scheduled_minutes"]
            )
            pos = sum(bool(r["net_PnL_USD"] and float(r["net_PnL_USD"]) > 0) for r in data)
            lines.append(
                f"| {mode} | {regime} | {pos} | {risk:,}/{total:,} | "
                f"{gross:.2%} | {orders:,} | {held:.0f} |"
            )
    lines.extend(
        [
            "",
            "## M04 and R07",
            "",
            "| ID | Regime | Gross USD | Actions USD | Cost USD | Net USD | Returns 2021–24 |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for r in funded:
        if r["strategy_id"] not in ("M04", "R07"):
            continue
        years = " / ".join(
            f"{float(r[f'return_{y}']):.2%}" if r[f"return_{y}"] else "HOLD"
            for y in (2021, 2022, 2023, 2024)
        )
        values = [
            f"{float(r[k]):,.0f}" if r[k] else r["status"]
            for k in (
                "gross_signed_price_PnL_USD",
                "gross_action_value_USD",
                "total_cost_USD",
                "net_PnL_USD",
            )
        ]
        lines.append(
            f"| {r['strategy_id']} | {r['regime']} | " + " | ".join(values) + f" | {years} |"
        )
    lines.extend(
        [
            "",
            "## Offline later-reference comparison",
            "",
            "The score strata pool observations descriptively across strategies and causes.",
            "The mean is not a feasible portfolio return.",
            "",
            "| Aligned exit score | Valid exit legs | Mean signed added bps |",
            "|---|---:|---:|",
        ]
    )
    for label in ("reversed", "weak", "strong", "unknown"):
        data = [
            r
            for r in exits
            if r["axis"] == "exit_strength"
            and r["horizon"] == "T240"
            and r["label"] == label
            and r["mean_bps"]
        ]
        n = sum(int(r["valid"]) for r in data)
        if n:
            added = sum(float(r["mean_bps"]) * int(r["valid"]) for r in data) / n
            lines.append(f"| {label} | {n:,} | {added:.2f} |")
    lines.extend(
        [
            "",
            "The later reference is a valid raw open. Incremental carry and a new "
            "funded path are excluded. Risk-forced extensions violate the realized constraint. "
            "Missing marks and corporate actions remain censored.",
            "",
            "Any prospective follow-on requires a new period and fixed rules. The economic "
            "comparisons use the original V1 mode pricing and commission assumptions.",
            "",
        ]
    )
    with target.open("x") as stream:
        stream.write("\n".join(lines))
