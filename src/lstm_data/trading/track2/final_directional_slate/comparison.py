"""Reuse exact frozen books; weighted ranks are published before any overlay result."""

import time

import numpy as np
import pandas as pd

from ..rapid_exit_audit.io import as_rows, column, table
from ..rapid_v1.paths import digest, publish
from ..rapid_v1.reporting import metrics
from ..rapid_v1.strategies import IDS
from ..rapid_v2_diagnostics.report import csv_write
from ..stage012.model_registry import SYMBOLS
from .common import FINAL_RUN, POLICIES, ROOT, V2, WEIGHTS, load, verify_inputs


def percentile(values: list[float]) -> list[float]:
    if not values or not all(np.isfinite(values)):
        raise ValueError("RANKING_HOLD_UNSUPPORTED_METRIC")
    if len(values) == 1:
        return [0.5]
    return ((pd.Series(values).rank(method="average") - 1) / (len(values) - 1)).tolist()


def collect() -> None:
    started = time.monotonic()
    verify_inputs()
    spec = load(ROOT / "FIVE_ALGORITHM_REGISTRY.json")
    final_rows = pd.read_csv(FINAL_RUN / "FUNDED_TARGETED_RESULTS.csv")
    fixed_rows = pd.read_csv(V2 / "HORIZON_RESULTS.csv")
    daily_new = pd.read_parquet(FINAL_RUN / "DAILY_NAV.parquet")
    daily_old = pd.read_parquet(V2 / "DAILY_NAV.parquet")
    trades = pd.read_parquet(FINAL_RUN / "COMPLETED_COHORTS.parquet")
    mechanism = pd.read_csv(V2 / "ANNUAL_AND_MECHANISM_TABLES.csv")
    result, daily_rows, attribution, checks = [], [], [], []
    for fid, p in POLICIES.items():
        sid, variant = p["case"].split("_", 1)
        original = fixed_rows if fid == "F3" else final_rows
        row = next(r for r in as_rows(original) if r.strategy_id == sid and r.variant == variant)
        source_daily = daily_old if fid == "F3" else daily_new
        d = (
            table(
                source_daily.loc[
                    (column(source_daily, "strategy_id") == sid)
                    & (column(source_daily, "variant") == variant)
                ]
            )
            if fid == "F3"
            else (table(source_daily.loc[column(source_daily, "case") == p["case"]]))
        )
        if len(d) != 1005 or not column(d, "date").is_monotonic_increasing:
            raise ValueError("DAILY_IDENTITY_HOLD " + fid)
        daily = [{str(k): v for k, v in x.items()} for x in d.to_dict("records")]
        m = metrics(daily)
        for x in daily:
            if (
                abs(
                    float(x["cash"])
                    + float(x["claims"])
                    + float(x["physical_value"])
                    + float(x["special"])
                    - float(x["nav"])
                )
                > 1e-7
            ):
                raise ValueError("DAILY_CASH_IDENTITY " + fid)
        for field, actual, expected in [
            ("NAV", m["final_NAV_USD"], row.final_NAV_USD),
            ("cash", daily[-1]["cash"], row.terminal_cash_USD),
            ("commission", daily[-1]["commission"], row.commission_USD),
            ("friction", daily[-1]["friction"], row.assumed_spread_USD + row.assumed_impact_USD),
            ("borrow", daily[-1]["borrow"], row.borrow_USD),
            ("funding", daily[-1]["funding"], row.funding_USD),
            (
                "bridge",
                row.gross_signed_price_PnL_USD + row.gross_action_value_USD - row.total_cost_USD,
                row.net_PnL_USD,
            ),
        ]:
            if abs(float(actual) - float(expected)) > 1e-7:
                raise ValueError(f"ACCOUNT_PARITY_HOLD {fid} {field}")
            checks.append(
                {
                    "candidate": fid,
                    "field": field,
                    "residual": float(actual) - float(expected),
                    "status": "PASS",
                    "daily_rows": len(d),
                }
            )
        nav = column(d, "nav").to_numpy(float)
        ret = nav / np.r_[100000.0, nav[:-1]] - 1
        downside = float(np.sqrt(np.mean(np.minimum(ret, 0) ** 2)))
        extra = {
            "candidate": fid,
            "label": p["label"],
            "family": p["family"],
            "Sortino_daily_downside_RMS_252": float(ret.mean() / downside * np.sqrt(252))
            if downside > 0
            else None,
            "source_case": p["case"],
            "funded_replay": "NOT_RUN_EXACT_ARCHIVE_REUSED",
        }
        if fid != "F3":
            t = table(trades.loc[column(trades, "case") == p["case"]])
            names = table(t.groupby("ticker")[["cash_pnl"]].sum())
            net = column(names, "cash_pnl")
            profitable = net.loc[net > 0].sort_values(ascending=False).iloc[:2]
            top = float(profitable.sum())
            best = float(column(t, "cash_pnl").nlargest(5).sum())
            extra.update(
                top_two_symbols="|".join(SYMBOLS[int(j)] for j in profitable.index),
                best_five_cohort_net=best,
                cohort_support="COMPLETE_CAPTURED_ATTRIBUTION",
            )
            for axis in ("ticker", "direction", "cause"):
                for label, block in t.groupby(axis):
                    z = table(block)
                    attribution.append(
                        {
                            "candidate": fid,
                            "axis": axis,
                            "label": str(label),
                            "cohorts": len(z),
                            "gross_price": float(column(z, "gross_signed_price_pnl").sum()),
                            "net": float(column(z, "cash_pnl").sum()),
                            "actions": float(column(z, "gross_action_cash").sum()),
                        }
                    )
            for year in ("2021", "2022", "2023", "2024"):
                stamp = pd.to_datetime(
                    column(t, "entry_at").to_numpy(float) * 60, unit="s", utc=True
                )
                extra["cohorts_" + year] = int((stamp.strftime("%Y") == year).sum())
        else:
            mech = table(
                mechanism.loc[
                    (column(mechanism, "strategy_id") == sid)
                    & (column(mechanism, "variant") == variant)
                ]
            )
            names = table(mech.loc[column(mech, "dimension") == "ticker"])
            if abs(float(column(names, "net").sum()) - row.net_PnL_USD) > 1e-7:
                raise ValueError("TICKER_ATTRIBUTION_HOLD " + fid)
            profitable = (
                table(names.loc[column(names, "net") > 0])
                .sort_values("net", ascending=False)
                .head(2)
            )
            top = float(column(profitable, "net").sum())
            extra.update(
                top_two_symbols="|".join(
                    SYMBOLS[int(float(j))] for j in column(profitable, "value")
                ),
                best_five_cohort_net=None,
                cohort_support="COHORT_ATTRIBUTION_NOT_IDENTIFIABLE",
            )
            for z in as_rows(mech):
                attribution.append(
                    {
                        "candidate": fid,
                        "axis": z.dimension,
                        "label": str(z.value),
                        "cohorts": z.cohorts,
                        "gross_price": z.gross_price,
                        "net": z.net,
                        "actions": z.actions,
                    }
                )
                if z.dimension == "entry_year":
                    extra["cohorts_" + str(int(float(z.value)))] = int(z.cohorts)
        extra.update(
            net_without_top_two=row.net_PnL_USD - top,
            top_two_net=top,
            cost_margin=(
                row.gross_signed_price_PnL_USD + row.gross_action_value_USD - row.total_cost_USD
            )
            / row.total_cost_USD
            if row.total_cost_USD > 0
            else None,
            drawdown_score=-abs(row.max_drawdown),
            positive_years=sum(a["return"] > 0 for a in m["annual"].values()),
        )
        for year, value in m["annual"].items():
            archived = getattr(row, "return_" + year, None)
            if archived is not None and abs(archived - value["return"]) > 1e-12:
                raise ValueError("ANNUAL_PARITY_HOLD " + fid)
            extra["return_" + year] = value["return"]
        result.append({**vars(row), **extra})
        daily_rows.extend({"candidate": fid, **x} for x in daily)
    csv_write(ROOT / "FIVE_CANDIDATE_FINANCIAL_COMPARISON.csv", result)
    csv_write(ROOT / "CANDIDATE_ATTRIBUTION.csv", attribution)
    csv_write(ROOT / "ARCHIVE_RECONCILIATION.csv", checks)
    pd.DataFrame(daily_rows).to_parquet(
        ROOT / "CANDIDATE_DAILY_NAV.parquet", index=False, compression="zstd"
    )
    eligible = [
        r
        for r in result
        if r["status"] == "COMPLETE"
        and r["closed_cohorts"] >= 80
        and r["RTH_gross_dollar_years"] >= 1
        and not r["terminal_pending"]
        and not r["terminal_stock_symbols"]
    ]
    audit = []
    for metric, weight in WEIGHTS.items():
        ranks = percentile([float(r[metric]) for r in eligible])
        for r, value in zip(eligible, ranks, strict=True):
            audit.append(
                {
                    "candidate": r["candidate"],
                    "metric": metric,
                    "raw_value": r[metric],
                    "percentile": value,
                    "weight": weight,
                    "weighted_score": value * weight,
                }
            )
    csv_write(ROOT / "SELECTION_SCORE_AUDIT.csv", audit)
    scores = {
        r["candidate"]: sum(x["weighted_score"] for x in audit if x["candidate"] == r["candidate"])
        for r in eligible
    }
    selected = []
    families = set()
    for fid in sorted(scores, key=lambda k: (-scores[k], k)):
        family = POLICIES[fid]["family"]
        if family not in families and len(selected) < 3:
            families.add(family)
            selected.append(fid)
    if len(selected) < 2:
        raise ValueError("SELECTION_HOLD_INSUFFICIENT_ELIGIBLE_FAMILIES")
    rows = {r["candidate"]: r for r in result}
    robust = any(
        rows[k]["net_PnL_USD"] > 0 and rows[k]["net_without_top_two"] > 0 for k in selected
    )
    status = (
        "PROVISIONAL_EXPLORATORY_SELECTION" if robust else "NO_ROBUST_POSITIVE_DIRECTIONAL_BASELINE"
    )
    selection = {
        "status": status,
        "registry_identity": spec["identity"],
        "scores": scores,
        "selected": selected,
        "families": [POLICIES[k]["family"] for k in selected],
        "candidate_flags": {
            k: "MECHANISM_CONTROL_ONLY / FAILED_NET_SCREEN"
            if rows[k]["net_PnL_USD"] <= 0
            else "POSITIVE_EXPLORATORY_CONCENTRATED"
            for k in selected
        },
        "robust_positive": robust,
        "score_audit_sha256": digest(ROOT / "SELECTION_SCORE_AUDIT.csv"),
        "comparison_sha256": digest(ROOT / "FIVE_CANDIDATE_FINANCIAL_COMPARISON.csv"),
        "elapsed_seconds": time.monotonic() - started,
    }
    publish(ROOT / "SELECTION_RECEIPT.json", selection)
    lines = [
        "# Predeclared research selection",
        "",
        status,
        "",
        "Within-five average-rank percentiles, fixed30/25/15/15/10/5 weights; no tuning.",
        "At most one R01; three distinct families if eligible. No independent validation.",
        "",
        "| ID | Policy | Score | Net USD | Net without two profitable names | Selected |",
        "|---|---|---:|---:|---:|---|",
    ]
    for k in POLICIES:
        r = rows[k]
        lines.append(
            f"| {k} | {POLICIES[k]['label']} | {scores.get(k, float('nan')):.5f} | "
            f"{r['net_PnL_USD']:,.2f} | {r['net_without_top_two']:,.2f} | {k in selected} |"
        )
    lines += [
        "",
        "Scores and raw metrics are in SELECTION_SCORE_AUDIT.csv. All five are preserved.",
        "The unselected R01 alternative remains an allocator control. A positive total destroyed",
        (
            "by top-two-name omission is explicitly fragile; omission is arithmetic, "
            "not a funded rerun."
        ),
        "Any selected net loser is MECHANISM_CONTROL_ONLY / FAILED_NET_SCREEN.",
        "All18 original mechanisms remain context. Selected mode breakdown is descriptive.",
        "No unseen period or new prices were read; sizing may proceed only after its own gates.",
    ]
    with (ROOT / "SELECTION_DECISION.md").open("x") as f:
        f.write("\n".join(lines) + "\n")
    csv_write(
        ROOT / "ALL18_HISTORICAL_CONTEXT.csv",
        [
            {
                "strategy_id": sid,
                "still_registered": True,
                "frozen_slate_ids": "|".join(
                    k for k, p in POLICIES.items() if p["strategy"] == sid
                ),
                "historical_index": (
                    "trading/track2/rapid_final_diag_v1/"
                    "ALL18_CONTEXT_AND_FINAL_DIAGNOSTIC_MATRIX.csv"
                ),
            }
            for sid in IDS
        ],
    )
    publish(
        ROOT / "COMPARISON_MANIFEST.json",
        {
            "status": "PASS",
            "reused_accounts": 5,
            "new_funded_comparison_replays": 0,
            "selection": selection,
            "files": {p.name: digest(p) for p in sorted(ROOT.iterdir()) if p.is_file()},
        },
    )


if __name__ == "__main__":
    collect()
