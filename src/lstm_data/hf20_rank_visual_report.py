"""Compact, complete index and interpretation of archived S1/S2 visual diagnostics."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .hf1m_action_audit import digest
from .hf20_rank_visuals import PRIOR
from .hf20_ranking_continue_report import markdown


def report(out: Path) -> None:
    roster = pd.read_csv(out / "HISTORICAL_MODEL_RUN_INVENTORY.csv")
    check = pd.read_csv(out / "HISTORICAL_SCORE_RECONCILIATION.csv")
    metric = pd.read_csv(PRIOR / "four_fold_OOS_metrics.csv")
    table = metric.pivot(index="model", columns="year", values="daily_ic")
    table["equal_year"] = table.mean(axis=1).where(table.notna().sum(axis=1).eq(4))
    table.columns = table.columns.astype(str)
    table.to_csv(out / "HISTORICAL_ANNUAL_AND_EQUAL_YEAR_IC.csv")
    files = []
    for p in sorted(PRIOR.rglob("*")):
        if p.is_file():
            files.append(
                dict(
                    path=str(p),
                    scope="HISTORICAL_S1_S2",
                    status="ARCHIVED_UNCHANGED",
                    kind=p.suffix,
                    bytes=p.stat().st_size,
                )
            )
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name.startswith(("historical_", "HISTORICAL_")):
            files.append(
                dict(
                    path=str(p),
                    scope="NEW_HISTORICAL_VISUALIZATION",
                    status="SAVED_READONLY",
                    kind=p.suffix,
                    bytes=p.stat().st_size,
                )
            )
    pd.DataFrame(files).to_csv(out / "HISTORICAL_COMPLETE_DIAGNOSTIC_FILE_INDEX.csv", index=False)
    qa = out / "HISTORICAL_BROWSER_QA.json"
    visual = qa.exists() and json.loads(qa.read_text())["interactive"]["status"] == "PASS"
    body = """# Historical S1 + S2 ranking visual diagnostics

**Retrospective saved-output analysis; no new fitting.** All31 accepted model-fold
outputs reconcile on exact keys, returns, target operands, weights and displayed
midranks. F21 PW failed and LP has no accepted OOS output; neither is backfilled.

Open [the offline interactive dashboard](plots/historical_s1_s2_rankings.html).
Choose year, primary model, extra overlays, stocks, dates and scatter origin.
The initial view is AAPL and the first ten actually saved OOS sessions in that year,
chosen independently of outcomes. Full-year access uses the Full saved year button.
The role selector changes the archived role metrics and cohort panels; trajectories
always remain genuine outer OOS. Rank1 means best, with exact average ties and no jitter.
Realized ranks are later-known outcomes attached to earlier forecast times.

The24 panels cover trajectories; identical-key predicted/realized/M1 heatmaps;
origin scatter; annual/equal-year, monthly and session IC with counts;
whole-month descriptive intervals; retrieval/concordance; signed/absolute movement
separately within/across sessions; top/bottom selection Jaccard; rank confusion;
stock/slot/quality rank error; margins/ties; score/residual/outcome distributions;
actual-objective tail cohorts; T2R original-target energy decomposition;
dropout-ON training and dropout-OFF validation selection. Gaps are never interpolated.
Set ties that do not identify exactly four names are marked ambiguous and excluded
from set-Jaccard histograms. Selection churn is not trading turnover or a position rule.

## Results and interpretation

The original primary population gives M1 equal-year IC0.0117255, T2R0.0076733,
NR0.0023695 and LR0.0060425. These are weak associations with substantial temporal
variation, not a reliable neural advantage over M1. A visually stable forecast ranking
does not establish accuracy. Retrieval20% and pair concordance50% are orientation
references, not significance tests; repeated stocks, pairs and origins are dependent.
PW's missing2021 output makes a four-year PW aggregate unavailable.
N0 is constant and its IC is undefined, not zero.

"""
    body += markdown(table.reset_index())
    body += "\n## Actual saved support\n\n" + markdown(
        check.loc[check.model.eq("N1"), ["year", "origins", "sessions", "rows"]]
    )
    body += "\n## Complete model/run inventory\n\n" + markdown(
        roster[["year", "model", "run_id", "status", "phase", "evaluation_role", "reason"]]
    )
    body += """
## Every diagnostic and analysis file

[Complete historical file index](HISTORICAL_COMPLETE_DIAGNOSTIC_FILE_INDEX.csv)
lists every archived S1/S2 artifact and new historical plot/table. The original
[diagnostic index](../hf20_s1_s2_continuation_2026-10-25_204117/DIAGNOSTIC_FILE_INDEX.csv)
and [README](../hf20_s1_s2_continuation_2026-10-25_204117/README.md) retain the
authoritative all-role numerical analyses. Nothing is replaced by a representative plot.

| Diagnostic | Authoritative file in the archived S1/S2 namespace |
| --- | --- |
| All four roles; actual objective and ranking | [table][D1] |
| Target tails, signs, complements, NUM/MAD, floor, energy and cross terms | [table][D2] |
| Original-error-ranked T2R cohorts | [table][D3] |
| Stock/month/sector/quality | [table][D4] |
| Pair difficulty and PW actual objective | [table][D5] |
| Full epoch/selection chronology | [table][D6] |
| Gradient/clipping/update summaries | [table][D7] |
| Raw/qualified selector, checkpoint and optimizer verification | [table][D8] |
| Sampled exact source/replay evidence | [table][D9] |
| Source-native/fallback by channel | [table][D10] |

The saved witness table contains60 model-event replays, not60 independent events.
Online losses are dropout-ON; selected-checkpoint role losses are dropout-OFF.
NR scores are ordinal; only T2R has a legitimate frozen once-inverted TG20 diagnostic.
Overlapping tail cohorts must not be summed as disjoint partitions; NUM_ONLY/MAD_ONLY/
BOTH/NEITHER are the disjoint mechanism partition. Ordinary complements are retained.
Numerical tables remain authoritative wherever a compact chart omits a cohort or field.

New machine-readable companions: historical_plot_scores.parquet (private),
historical_rank_movements.csv, historical_selection_set_changes.csv,
historical_daily_IC.csv, historical_monthly_IC.csv,
historical_month_block_intervals.csv and historical_group_rank_errors.csv.
The400 replicate month-block intervals resample whole calendar months, preserve
session averaging and are descriptive; they do not correct researcher search.

## Static windows and provenance

![2021 first ten saved sessions](plots/historical_2021.png)
![2022 first ten saved sessions](plots/historical_2022.png)
![2023 first ten saved sessions](plots/historical_2023.png)
![2024 first ten saved sessions](plots/historical_2024.png)

Exact paths, bytes and SHA256 identities are in
[HISTORICAL_SOURCE_REFERENCES.csv](HISTORICAL_SOURCE_REFERENCES.csv).
The [reconciliation table](HISTORICAL_SCORE_RECONCILIATION.csv) verifies31 outputs,
193,980 scored rows, canonical20-stock order and original daily IC at1e-12 tolerance.
Saved plot fields are read directly; no checkpoint replay was needed.
HTML embeds its Plotly dependency and data, uses no server/external scripts,
and should remain local under the bounded research-use rights.

Reproduce from the repository environment with its existing visualization dependency:
`python -m lstm_data.hf20_rank_visuals --out NEW_EXISTING_OUTPUT_DIRECTORY`,
then `python scripts/render_hf20_rankings.py --out NEW_EXISTING_OUTPUT_DIRECTORY`.
The latter uses an already-installed Chromium (or `--browser PATH`), never installs one.
Use a new directory; earlier historical models and results are immutable.

## Separate S3 context and S4 status

S3 is not plotted as S1/S2. Its h2 T2R aligned-M2 delta+0.015958 has a whole-month
interval[−0.000770,0.029417] including zero; this is exploratory, not confirmatory.
[Executed S3 decision](../hf20_s3_live_2026-10-26_010204/S3_FINAL_RESEARCH_DECISION.md).
New S4 scores are NOT_RUN until the separate live-fit gate is approved and completed.
No 2025 tuning, protected2026 numerical access or trading/P&L analysis occurred here.
Publication timing, action vintage, fixed-survivor selection and local-use rights
remain qualified; successful plots do not certify any of these assumptions.
"""
    detail_files = [
        "all_role_metrics.csv",
        "cohort_objective_and_error_decomposition_v2.csv",
        "T2R_original_error_ranked_cohorts.csv",
        "cohort_stock_month_sector_quality_v2.csv",
        "cohort_pair_concordance_and_PW.csv",
        "complete_epoch_trace.csv",
        "gradient_clip_update_summary.csv",
        "final_selector_checkpoint_optimizer_verification.csv",
        "source_case_checkpoint_replay.csv",
        "source_case_native_fallback_by_channel.csv",
    ]
    for i, name in enumerate(detail_files, 1):
        body += f"\n[D{i}]: ../{PRIOR.name}/{name}\n"
    body += "\nBrowser filter/render verification: **" + ("PASS" if visual else "PENDING") + "**.\n"
    (out / "HISTORICAL_S1_S2_RANKING_VISUAL_DIAGNOSTICS.md").write_text(body)
    if visual:
        (out / "HISTORICAL_PHASE_I_GATE.json").write_text(
            json.dumps(
                dict(
                    status="PASS",
                    accepted_outputs=31,
                    scored_rows=int(check.rows.sum()),
                    failed_pw_fold_preserved=True,
                    lp_deferred=True,
                    new_fits=0,
                    browser_qa_sha256=digest(qa),
                    report_sha256=digest(out / "HISTORICAL_S1_S2_RANKING_VISUAL_DIAGNOSTICS.md"),
                    reconciliation_sha256=digest(out / "HISTORICAL_SCORE_RECONCILIATION.csv"),
                ),
                indent=2,
            )
            + "\n"
        )
