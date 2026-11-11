"""Human-readable views of an already sealed offline audit."""

import argparse
from pathlib import Path

from .io import csv_at, json_at

ROOT = Path("trading/track2/rapid_exit_audit_v1")


def num(row: dict, key: str) -> float:
    return float(row.get(key) or 0)


def dollar(value: float) -> str:
    return f"{value:,.0f}"


def write(path: Path, lines: list[str]) -> None:
    with path.open("x") as stream:
        stream.write("\n".join(lines) + "\n")


def get_cell(stats: list[dict], sid: str, regime: str, horizon: str, axis: str, label: str) -> dict:
    return next(
        r
        for r in stats
        if r["strategy_id"] == sid
        and r["regime"] == regime
        and r["horizon"] == horizon
        and r["axis"] == axis
        and r["label"] == label
    )


def summaries(result: Path) -> None:
    receipt = json_at(result / "RUN_RECEIPT.json")
    matrix = csv_at(result / "ALL18_CANDIDATE_EVIDENCE_MATRIX.csv")
    stats = csv_at(result / "ALL18_POST_EXIT_EXTENSIONS.csv")
    positive = csv_at(result / "PRIOR_FUNDED_POSITIVE_CONFIGURATIONS.csv")
    review = json_at(result / "CANDIDATE_REVIEW_RECEIPT.json")
    s = json_at(ROOT / "INPUT_SEAL.json")
    summary = csv_at(Path(s["funded"]) / "V3_ALL54_SUMMARY.csv")
    lines = [
        "# All-18 post-exit mechanism report",
        "",
        f"The full population has {receipt['actual_exit_legs']:,} actual exit legs and "
        f"{receipt['reference_targets']:,} predeclared targets. Rows are leg quantities, "
        "including partial and internal/external portions. Each independent account has "
        "its own capital. Extension dollars do not combine into a portfolio result.",
        "",
        "## Conservative-account context",
        "",
        "| ID | Executed V3 net USD | Nonforced external +60 raw bps | +240 raw bps | "
        "Next-full-session raw bps | Diagnostic evidence |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for m in matrix:
        sid = m["strategy_id"]
        cells = [
            get_cell(
                stats, sid, "CONSERVATIVE", h, "feasible_external", "UNFUNDED_NONFORCED_EXTERNAL"
            )
            for h in ("T60", "T240", "NEXT_FULL_SESSION")
        ]
        lines.append(
            f"| {sid} | {dollar(num(m, 'V3_net_conservative'))} | "
            + " | ".join(f"{num(c, 'equal_leg_mean_bps'):.2f}" for c in cells)
            + f" | {m['diagnostic_label']} |"
        )
    lines.extend(
        [
            "",
            "All 54 account/regime combinations and conditional cost columns are in the "
            "CSV. This table uses the conservative regime consistently. Negative actual "
            "performance remains visible. Nonforced means no recorded risk trigger on that "
            "leg and supplies no capital-feasibility certificate.",
            "",
            "## Previously executed positive configurations",
            "",
            "| Study | ID | Exact configuration | Net USD |",
            "|---|---|---|---:|",
        ]
    )
    for r in positive:
        lines.append(
            f"| {r['study']} | {r['strategy_id']} | {r['label']} | "
            f"{dollar(num(r, 'net_PnL_USD'))} |"
        )
    lines.extend(
        [
            "",
            "## Price, action and cost basis",
            "",
            "Primary bps and favorable fractions use raw-to-raw signed price change, adjusted "
            "for supported share splits. Signed ordinary distributions are shown separately, "
            "as paid cash or an unpaid claim at the reference. Unsupported distributed assets "
            "are censored. Old V3 pooling used the actual adverse exit fill as anchor and "
            "censored every intervening corporate action. The legacy four-state means are "
            "independently reproduced in a dedicated CSV. They include exit-concession recovery.",
            "",
            "Conditional standalone dollars add ordinary action value and original exit-concession "
            "recovery, subtract a new assumed exit concession and 2% ACT/365 short carry at the "
            "frozen exit mark, then subtract the difference of hypothetical standalone old/new "
            "ticket fees. No new entry or full roundtrip is charged. Actual netting, constraints "
            "and fee allocation may differ. Internal-only actual legs carry no external "
            "execution charge in the saved book. A hypothetical later standalone sale is a "
            "distinct conditional treatment. It is kept identifiable through the external flag.",
            "",
            "Raw exit-dollar weighting and absolute share weighting are separate. Equal-exit-day "
            "means and 5/95% day dispersion are descriptive dependence checks. The leg count "
            "does not establish an independent sample size. Exit-score quintiles are formed "
            "from the saved per-strategy score distribution without future prices and preserve "
            "unknown scores. A latched submission score can predate its fill.",
            "",
            "## Coverage and confounds",
            "",
            "The five-minute reference search is restricted to the target session. The "
            "next-full-session target retains the same opening offset and skips half-days. "
            "Censoring distinguishes cutoff, absent price, forward-limit gaps and unsupported "
            "distributions. No market data after 2024 was opened. Risk-forced rows are labeled "
            "INFEASIBLE_UNDER_REALIZED_RISK. A good later mark can follow a correct risk exit. "
            "Every horizon is a fixed later reference with both missed upside and avoided loss.",
            "",
            "No independent Stage 6 analysis, funded refinement, final baseline selection or "
            "LSTM sizing occurred. The 2021–2024 survivor panel and source/action cleaning "
            "have been repeatedly researched. Positive hypotheses require untouched evidence.",
        ]
    )
    write(ROOT / "ALL18_POST_EXIT_MECHANISM_REPORT.md", lines)
    notes = [
        "# Candidate review",
        "",
        "The sealed rubric separates actual positive configurations, diagnostic mechanisms "
        "and negative/inconclusive support. Every ID remains eligible. A positive parent "
        "label applies only to the listed funded configuration. No future-reference "
        "outcome is a traded result.",
        "",
        "| ID | Funded positive evidence | Diagnostic | Dive |",
        "|---|---|---|---|",
    ]
    for r in matrix:
        notes.append(
            f"| {r['strategy_id']} | {r['exact_funded_positive_configs'] or 'None'} | "
            f"{r['diagnostic_label']} | {r['deep_dive']} |"
        )
    notes.extend(
        [
            "",
            f"Additional full dives selected by the fixed rule were {review['additional']}. "
            "R07 and M04 are mandatory from prior actual positives. R01 receives a delta only. "
            "Qualifying cell counts, years, raw-to-raw margin, conditional standalone margin, "
            "and top-five/top-two concentration checks are retained in the evidence matrix. "
            "A positive mean alone cannot promote a strategy. Missing cohort-level net "
            "allocations lower interpretation quality.",
        ]
    )
    write(ROOT / "CANDIDATE_SELECTION_NOTES.md", notes)
    for sid in ["M04", "R07", *review["additional"]]:
        deep(sid, result, summary, stats, positive)
    r01_delta(result, stats)


def deep(
    sid: str, result: Path, summary: list[dict], stats: list[dict], positive: list[dict]
) -> None:
    table = csv_at(result / (sid + "_DEEP_DIVE_TABLES.csv"))
    own = [r for r in summary if r["strategy_id"] == sid]
    exact = [r for r in table if r["view"] == "exact_frozen_V3_cohort_aggregate"]
    causal = next(
        r for r in csv_at(result / "ALL18_EXECUTED_EXIT_CONTRACTS.csv") if r["strategy_id"] == sid
    )
    lines = [
        f"# {sid} descriptive deep dive",
        "",
        "All amounts describe executed archived books or separately labeled offline "
        "marks. The investigation followed repeated inspection of the same survivor "
        "sample. Full net individual-cohort outcomes were compacted. Exact frozen "
        "grouped net and raw reconstruction support are identified in the data table.",
        "",
        "## Executed mechanism",
        "",
        causal["direction_rule"]
        + ". "
        + causal["entry_cadence"]
        + ". Slots "
        + causal["entry_slots"]
        + ".",
        causal["exit_monitor"] + ". " + causal["monitor_cadence"] + ".",
        "The entry event qualifier is preserved at formation. Breakout and gap event "
        "references stay frozen for the hold. Ongoing monitoring, trail, maximum and "
        "account risk follow the original V3 adapter. Compression or confirmation volume "
        "need not persist after entry. " + causal["maximum"] + ".",
        "",
        "## Executed account evidence",
        "",
        "| Regime | Gross price USD | Actions USD | Costs USD | Net USD | "
        "Risk lots / closed | Median trading min | Mean gross/NAV |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in own:
        lines.append(
            f"| {r['regime']} | {dollar(num(r, 'gross_signed_price_PnL_USD'))} | "
            f"{dollar(num(r, 'gross_action_value_USD'))} | {dollar(num(r, 'total_cost_USD'))} | "
            f"{dollar(num(r, 'net_PnL_USD'))} | {r['risk_closed_cohorts']}/{r['closed_cohorts']} | "
            f"{r['median_scheduled_minutes']} | {num(r, 'mean_RTH_marked_gross_fraction'):.1%} |"
        )
    lines.extend(
        [
            "",
            "| Regime | 2021 | 2022 | 2023 | 2024 | Sharpe | CAGR | Max DD |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for r in own:
        lines.append(
            f"| {r['regime']} | "
            + " | ".join(f"{num(r, 'return_' + str(y)):.2%}" for y in (2021, 2022, 2023, 2024))
            + f" | {num(r, 'Sharpe_252_zero_rf'):.3f} | {num(r, 'CAGR'):.2%} | "
            f"{num(r, 'max_drawdown'):.2%} |"
        )
    for r in positive:
        if r["strategy_id"] == sid:
            lines.append(
                f"\nPrior {r['study']}/{r['label']} net was "
                f"USD {num(r, 'net_PnL_USD'):,.6f}. That configuration retains "
                "its own holding and cap rules."
            )
    lines.extend(
        [
            "",
            "## Attribution and fragility",
            "",
            "| Regime | Long net USD | Short net USD | Top two net tickers | "
            "Their net contribution | Account less their contribution |",
            "|---|---:|---:|---|---:|---:|",
        ]
    )
    for r in own:
        regime = r["regime"]
        b = [x for x in exact if x["regime"] == regime]
        long = next(x for x in b if x["axis"] == "side" and x["label"] == "1")
        short = next(x for x in b if x["axis"] == "side" and x["label"] == "-1")
        tickers = sorted(
            [x for x in b if x["axis"] == "ticker"], key=lambda x: num(x, "net"), reverse=True
        )[:2]
        value = sum(num(x, "net") for x in tickers)
        lines.append(
            f"| {regime} | {dollar(num(long, 'net'))} | {dollar(num(short, 'net'))} | "
            + ",".join(x["label"] for x in tickers)
            + f" | {dollar(value)} | "
            f"{dollar(num(r, 'net_PnL_USD') - value)} |"
        )
    lines.extend(
        [
            "",
            "Raw tails, winner/loser sums, months, realized holding, side, ticker, "
            "drawdown episodes and shared-entry/changed-exit counts are in the companion "
            "table. A raw reconstruction mismatch prevents raw cohort claims for that "
            "case. Exact group tables remain usable. Removing contributors is arithmetic "
            "with all other book effects fixed.",
            "",
            "## Nonforced external extensions",
            "",
            "| Regime | Horizon | Valid / exits | Raw mean bps | Conditional bps per exit dollar | "
            "Missed upside USD | Avoided loss USD |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for regime in ("CONSERVATIVE", "STANDARD", "HIGH_RISK"):
        for horizon in ("T60", "T240", "NEXT_FULL_SESSION"):
            r = get_cell(
                stats, sid, regime, horizon, "feasible_external", "UNFUNDED_NONFORCED_EXTERNAL"
            )
            conditional = num(r, "conditional_standalone_USD")
            # The table carries the normalized raw denominator in the raw-weighted bps.
            denominator = (
                num(r, "signed_raw_USD") / num(r, "notional_weighted_bps") * 10000
                if num(r, "notional_weighted_bps")
                else 0.0
            )
            cbps = conditional / denominator * 10000 if denominator else float("nan")
            lines.append(
                f"| {regime} | {horizon} | {r['valid']}/{r['exits']} | "
                f"{num(r, 'equal_leg_mean_bps'):.2f} | {cbps:.2f} | "
                f"{dollar(num(r, 'missed_upside_USD'))} | {dollar(num(r, 'avoided_loss_USD'))} |"
            )
    lines.extend(
        [
            "",
            "This panel excludes recorded risk-forced and internal portions. The complete "
            "table retains both and all source censors. Conditional standalone margin has "
            "a hypothetical replacement exit, frozen-mark short carry and standalone ticket "
            "difference. It neither reserves capital nor cancels other cohorts. Exact "
            "net preceding-cohort versus future-mark correlation is unavailable from the "
            "compacted archive. The separate raw-leg and saved-strength strata describe "
            "associations without replacing absent net allocations.",
            "",
            "## Cost intensity",
            "",
            "| Regime | External orders | Commission | Price concession | Impact | Borrow | "
            "Turnover | Account cost bps | Break-even bps |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for r in own:
        turnover = num(r, "executed_turnover_USD")
        edge = (
            (num(r, "gross_signed_price_PnL_USD") + num(r, "gross_action_value_USD"))
            / turnover
            * 10000
        )
        lines.append(
            f"| {r['regime']} | {r['external_orders']} | "
            + " | ".join(
                dollar(num(r, k))
                for k in (
                    "commission_USD",
                    "assumed_spread_USD",
                    "assumed_impact_USD",
                    "borrow_USD",
                )
            )
            + f" | {dollar(turnover)} | "
            + f"{num(r, 'total_cost_USD') / turnover * 10000:.2f} | {edge:.2f} |"
        )
        concession = num(r, "assumed_spread_USD") + num(r, "assumed_impact_USD")
        lines.append(
            f"\n{r['regime']} same-holdings price-cost arithmetic at .5/1/1.5× gives "
            + "/".join(
                dollar(num(r, "net_PnL_USD") + (1 - k) * concession) for k in (0.5, 1.0, 1.5)
            )
            + " USD. Quantities, fees and carry stay fixed in this accounting sensitivity."
        )
    lines.extend(
        [
            "",
            "Risk labels may be whole-account spillovers. Their incidence and primary "
            "precedence cannot reconstruct missing per-order headroom. Strong or weak "
            "scores may have different stock, side and year mixes. All 2024 reference "
            "cutoffs, half-days, ordinary actions and unsupported special crossings stay "
            "visible in the common coverage table.",
            "",
            "## Comparison and next hypothesis",
            "",
            "R01 is a weekly six-minus-one-month momentum rank with concentrated long gains. "
            "This mechanism keeps its own cadence and cost mode. The unchanged V1/V2/V3 "
            "controls remain available, with different executed holds and book feedback. "
            "The companion findings appendix sets the proposal and its falsification rule.",
        ]
    )
    write(ROOT / (sid + "_DEEP_DIVE.md"), lines)


def r01_delta(result: Path, stats: list[dict]) -> None:
    lines = [
        "# R01 all-18 post-exit delta",
        "",
        "The completed R01 diagnosis remains authoritative. Its execution, concentrated "
        "TSLA/AVGO long gains and entry-reserve proposal are preserved. This audit "
        "changes the diagnostic reference contract through a five-minute search bound "
        "and supported split/dividend adjustments. It also separates raw-open movement "
        "from recovery of the original modeled exit concession.",
        "",
        "| H85 subset | Horizon | Valid | Raw missed upside | Raw avoided loss |",
        "|---|---|---:|---:|---:|",
    ]
    for label in ("INFEASIBLE_UNDER_REALIZED_RISK", "UNFUNDED_NONFORCED"):
        for h in ("T60", "T240", "NEXT_FULL_SESSION"):
            r = get_cell(stats, "R01", "CONSERVATIVE", h, "feasibility", label)
            lines.append(
                f"| {label} | {h} | {r['valid']} | "
                f"{dollar(num(r, 'missed_upside_USD'))} | {dollar(num(r, 'avoided_loss_USD'))} |"
            )
    lines.extend(
        [
            "",
            "The earlier USD 7,851 and USD 9,652 risk-next-session totals used an executed "
            "exit anchor. Raw-to-raw totals remove original concession recovery. The exact "
            "legacy mean/state checks are retained separately. Grouping changes and "
            "dividend/split handling should not be interpreted as a new funded result.",
            "",
            "[Original R01 handoff](../rapid_r01_deep_dive/R01_DEEP_DIVE_HANDOFF.md). "
            "R01 remains an unchanged benchmark and delta-only review. S2-C remains on HOLD.",
        ]
    )
    write(ROOT / "R01_NEW_POST_EXIT_DELTA.md", lines)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("result", type=Path)
    summaries(p.parse_args().result)
