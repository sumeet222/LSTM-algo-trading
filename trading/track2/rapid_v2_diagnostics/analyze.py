"""Compare the sealed all-ID matrices without rerunning the market tape."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from statistics import median

from lstm_data.trading.track2.rapid_v1.paths import digest, publish
from lstm_data.trading.track2.rapid_v1.strategies import IDS
from lstm_data.trading.track2.rapid_v2_diagnostics.report import csv_write

CANDIDATES = ("M01", "M06", "R03", "R07")
HEADROOM = ("H100", "H85", "H70")
HORIZONS = {"M": ("T60", "T120", "H100", "T480"), "R": ("H100", "D1", "D3", "D5")}


def read(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def values(rows: list[dict[str, str]], key: str) -> list[float]:
    return [float(r[key]) for r in rows if r.get(key)]


def count(rows: list[dict[str, str]], key: str) -> int:
    return sum(int(r[key]) for r in rows)


def label(v: str | float | None, spec: str = ",.0f") -> str:
    return format(float(v), spec) if v is not None and v != "" else "N/A"


def compare_headroom(head: dict, chosen: list[str]) -> list[dict]:
    result = []
    for sid in chosen:
        base = head[sid, "H100"]
        for variant in HEADROOM[1:]:
            row = head[sid, variant]
            good = row["status"] != "HOLD" and base["status"] != "HOLD"
            result.append(
                {
                    "strategy_id": sid,
                    "variant": variant,
                    "status": row["status"],
                    "early_rate_change_pp": 100
                    * (float(row["early_rate"]) - float(base["early_rate"]))
                    if row["early_rate"] and base["early_rate"]
                    else None,
                    "change_in_net_USD": float(row["net_PnL_USD"]) - float(base["net_PnL_USD"])
                    if good
                    else None,
                    "change_in_net_per_1M_gross_RTH_dollar_years_USD": (
                        float(row["net_per_1M_RTH_gross_dollar_years_USD"])
                        - float(base["net_per_1M_RTH_gross_dollar_years_USD"])
                    )
                    if good
                    and row["net_per_1M_RTH_gross_dollar_years_USD"]
                    and base["net_per_1M_RTH_gross_dollar_years_USD"]
                    else None,
                    "change_in_gross_price_USD": float(row["gross_signed_price_PnL_USD"])
                    - float(base["gross_signed_price_PnL_USD"]),
                    "change_in_actions_USD": float(row["gross_action_value_USD"])
                    - float(base["gross_action_value_USD"]),
                    "change_in_cost_USD": float(row["total_cost_USD"])
                    - float(base["total_cost_USD"]),
                    "change_in_external_orders": int(row["external_orders"])
                    - int(base["external_orders"]),
                    "gross_basis": row["gross_basis"],
                }
            )
    return result


def analyze(run: Path, output: Path) -> None:
    completion = json.loads((run / "RUN_COMPLETION.json").read_text())
    directory = Path(completion["results"])
    manifest = directory / "MANIFEST.json"
    if digest(manifest) != completion["result_manifest_sha256"]:
        raise ValueError("UNVERIFIED_RESULTS")
    for key, sha in json.loads(manifest.read_text())["result_files"].items():
        if digest(directory / key) != sha:
            raise ValueError("RESULT_PAYLOAD_DRIFT:" + key)
    head_rows, time_rows, friction = (
        read(directory / file)
        for file in (
            "HEADROOM_RESULTS.csv",
            "HORIZON_RESULTS.csv",
            "FRICTION_DECOMPOSITION.csv",
        )
    )
    head = {(r["strategy_id"], r["variant"]): r for r in head_rows}
    horizon = {(r["strategy_id"], r["variant"]): r for r in time_rows}
    if set(head) != {(s, h) for s in IDS for h in HEADROOM} or set(horizon) != {
        (s, h) for s in IDS for h in HORIZONS[s[0]]
    }:
        raise ValueError("MATRIX_AXES")
    output.mkdir(exist_ok=False)
    paired = compare_headroom(head, list(IDS))
    csv_write(output / "HEADROOM_PAIRED_CONTRASTS.csv", paired)
    winners = []
    for sid in IDS:
        rows = [horizon[sid, h] for h in HORIZONS[sid[0]] if horizon[sid, h]["net_PnL_USD"]]
        if not rows:
            winners.append({"strategy_id": sid, "status": "NO_RECONCILED_RESULT"})
            continue
        best_net = max(rows, key=lambda r: float(r["net_PnL_USD"]))
        priced = [r for r in rows if r["gross_edge_per_1M_turnover_USD"]]
        best_gross = max(priced, key=lambda r: float(r["gross_edge_per_1M_turnover_USD"]))
        winners.append(
            {
                "strategy_id": sid,
                "status": "DESCRIPTIVE_REUSED_SAMPLE",
                "best_net_variant": best_net["variant"],
                "best_net_USD": best_net["net_PnL_USD"],
                "median_net_USD": median(values(rows, "net_PnL_USD")),
                "best_gross_intensity_variant": best_gross["variant"],
                "best_gross_edge_per_1M_turnover_USD": best_gross["gross_edge_per_1M_turnover_USD"],
                "median_gross_edge_per_1M_turnover_USD": median(
                    values(priced, "gross_edge_per_1M_turnover_USD")
                ),
                "best_net_gross_price_USD": best_net["gross_signed_price_PnL_USD"],
                "best_net_actions_USD": best_net["gross_action_value_USD"],
                "best_net_cost_USD": best_net["total_cost_USD"],
                "gross_basis": best_net["gross_basis"],
            }
        )
    csv_write(output / "HORIZON_DESCRIPTIVE_CONTRASTS.csv", winners)
    report = [
        "# HF20 Track 2 Rapid V2 screening diagnostics",
        "",
        f"The sealed run finished **{completion['status']}** across "
        f"{completion['unique_cases']} unique cases. H100 reproduces the original V1 baseline. "
        "This is a reused, fixed-survivor 2021–24 sample. All horizons and budget fractions "
        "were specified before new results.",
        "",
        "## Headroom and actual early exits",
        "",
        "| Mode | Budget | Net improved vs H100 | Exposure-normalized net improved | "
        "Cohorts | Early | Early rate | Risk external orders |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    mode_summaries = {}
    for mode, initial in (("MICRO_PRO", "M"), ("RETAIL_CONSERVATIVE", "R")):
        for h in HEADROOM:
            rows = [r for r in head_rows if r["mode"] == mode and r["variant"] == h]
            n, early, risk = (
                count(rows, k) for k in ("cohorts", "early_exits", "risk_external_orders")
            )
            changes = [
                r for r in paired if r["strategy_id"].startswith(initial) and r["variant"] == h
            ]
            p = sum((r["change_in_net_USD"] or 0) > 1e-7 for r in changes)
            norm = sum(
                (r["change_in_net_per_1M_gross_RTH_dollar_years_USD"] or 0) > 1e-7 for r in changes
            )
            report.append(
                f"| {mode} | {h} | {p if changes else '—'} | {norm if changes else '—'} | "
                f"{n:,} | {early:,} | {early / n:.2%} | {risk:,} |"
            )
            mode_summaries[mode + "_" + h] = {
                "cohorts": n,
                "early": early,
                "net_improved": p,
                "normalized_improved": norm,
            }
    report.extend(
        [
            "",
            "Risk-order dollars distinguish the full notional of each affected external fill "
            "from the portion attributed to risk-reduction legs. Internal crosses create zero "
            "external cost. A final exit after the target may still carry a risk-order role. "
            "Actual early rate uses final effective exit before the nominal endpoint.",
            "",
            "## Friction and arrival movement",
            "",
            "| Mode | External orders | Signed drift | Absolute drift | Assumed spread | "
            "Assumed impact | Commission | Borrow |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for mode in ("MICRO_PRO", "RETAIL_CONSERVATIVE"):
        f = [r for r in friction if r["mode"] == mode]
        cols = (
            "signed_arrival_drift_USD",
            "absolute_arrival_drift_USD",
            "assumed_spread_USD",
            "assumed_impact_USD",
            "commission_USD",
            "borrow_USD",
        )
        report.append(
            f"| {mode} | {count(f, 'external_orders'):,} | "
            + " | ".join(label(sum(values(f, c))) for c in cols)
            + " |"
        )
    report.extend(
        [
            "",
            "For signed physical quantity q, received submission mark m, valid next raw open p "
            "and modeled fill f, arrival drift is q × (p − m), the incremental concession is "
            "q × (f − p), and their sum is q × (f − m). A positive value is adverse. Absolute "
            "drift measures movement in either direction. Arrival already changes the raw-open "
            "price P&L and is excluded from the separately assessed cost.",
            "",
            "Micro uses the received volatility ratio and submitted physical quantity "
            "relative to ADV. Its order commission is $0.002 per share. Retail uses 5 bp per side "
            "for each component and rounds to the adverse cent. V1 apportions "
            "that tick rounding between its two price components. The retail commission is "
            "$0.005/share with a cumulative $1 order minimum. The historical midpoint is unknown. "
            "Both modes start with a raw transaction-print proxy.",
            "",
            "The cash bridge is gross raw-open signed-price P&L plus action value less physical "
            "commissions, both incremental price concessions, borrow and funding. Executed cash "
            "already includes the concessions. Gross signed-price P&L restores them "
            "once. No arithmetic double count was found. The zero-concession column adds back only "
            "these two price components on the exact same fills. It gives no new funded NAV path.",
            "",
            "## All-ID horizon comparison",
            "",
            "| ID | Best net horizon | Net USD | Median net USD | Best gross/turnover horizon | "
            "Gross USD per $1M | Median gross USD per $1M |",
            "|---|---|---:|---:|---|---:|---:|",
        ]
    )
    for x in winners:
        report.append(
            f"| {x['strategy_id']} | {x.get('best_net_variant', 'HOLD')} | "
            f"{label(x.get('best_net_USD'))} | {label(x.get('median_net_USD'))} | "
            f"{x.get('best_gross_intensity_variant', 'HOLD')} | "
            f"{label(x.get('best_gross_edge_per_1M_turnover_USD'))} | "
            f"{label(x.get('median_gross_edge_per_1M_turnover_USD'))} |"
        )
    report.extend(
        [
            "",
            "T codes are scheduled trading minutes and D codes are same-slot session counts. "
            "H100 is 240 scheduled trading minutes. Horizon changes leave directional inputs and "
            "signal thresholds frozen. They alter overlapping capital and the set of funded fills.",
            "",
            "## Four mechanism candidates",
            "",
            "| ID | Variant | Net USD | Gross price USD | Action USD | Cost USD | "
            "Gross USD per $1M turnover | Early | Median scheduled minutes |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for sid in CANDIDATES:
        for h in HEADROOM + tuple(v for v in HORIZONS[sid[0]] if v != "H100"):
            r = head.get((sid, h), horizon.get((sid, h)))
            for_key = (
                "net_PnL_USD",
                "gross_signed_price_PnL_USD",
                "gross_action_value_USD",
                "total_cost_USD",
                "gross_edge_per_1M_turnover_USD",
            )
            if r is None:
                raise ValueError("MECHANISM_AXIS")
            report.append(
                f"| {sid} | {h} | "
                + " | ".join(label(r[k]) for k in for_key)
                + f" | {label(r['early_rate'], '.1%')} | "
                f"{label(r['median_scheduled_minutes'])} |"
            )
    all_rows = {**head, **horizon}
    positive = [
        f"{sid}/{case}"
        for (sid, case), r in all_rows.items()
        if r["net_PnL_USD"] and float(r["net_PnL_USD"]) > 0
    ]
    report.extend(
        [
            "",
            "Positive net cases: " + (", ".join(positive) if positive else "none") + ".",
            "",
            "The tables describe selected outcomes on an already examined period. Comparing "
            "gross dollars per turnover and per RTH gross dollar-year helps distinguish changes "
            "in exposure from changes in price edge. No variant receives confirmatory status. "
            "A later retail experiment could precommit a 10-session and a longer horizon on new "
            "data. Actual spreads, impact, locates and receipt delays remain unknown. Conditional "
            "corporate actions and retrospective QA limit inference.",
            "",
        ]
    )
    (output / "RAPID_V2_SCREENING_DIAGNOSTICS.md").write_text("\n".join(report))
    publish(
        output / "ANALYSIS_MANIFEST.json",
        {
            "parent_result_manifest_sha256": digest(manifest),
            "analysis_code_sha256": digest(Path(__file__)),
            "files": {p.name: digest(p) for p in sorted(output.iterdir())},
            "status_counts": dict(Counter(r["status"] for r in all_rows.values())),
            "headroom": mode_summaries,
            "positive_net": positive,
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    analyze(args.run, args.output)
