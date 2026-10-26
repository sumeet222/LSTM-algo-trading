"""Saved-score S4 per-run and collective closeout; never fits or decodes protected sources."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_audit import digest
from .hf20_rank_visuals import PRIOR
from .hf20_ranking import origin_ic
from .hf20_ranking_continue_report import markdown
from .hf20_s4_authority import RUNS
from .hf20_s4_data import ROLES


def block_interval(daily: pd.Series) -> dict:
    """Resample complete observed calendar-month blocks, preserving session dependence."""
    d = daily.dropna()
    if d.empty:
        return dict(mean=None, low=None, high=None, sessions=0, months=0)
    bins = d.groupby(d.index.astype(str).str[:7]).agg(["sum", "count"])
    ix = np.random.default_rng(22042).integers(len(bins), size=(400, len(bins)))
    draws = bins["sum"].to_numpy()[ix].sum(1) / bins["count"].to_numpy()[ix].sum(1)
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return dict(
        mean=float(d.mean()), low=float(lo), high=float(hi), sessions=len(d), months=len(bins)
    )


def paired(f: pd.DataFrame, g: pd.DataFrame, label: str) -> list[dict]:
    keys = ["origin_id", "ticker"]
    joined = f.merge(
        g[keys + ["score", "return_4h"]],
        on=keys,
        suffixes=("", "_reference"),
        validate="one_to_one",
    )
    if joined.empty or joined.groupby("origin_id").size().ne(20).any():
        raise ValueError("S4_MATCHED_COMPLETE20_REQUIRED")
    np.testing.assert_allclose(joined.return_4h, joined.return_4h_reference, rtol=1e-11, atol=1e-12)
    days = joined.session_date_et.to_numpy()[::20]
    truth = joined.return_4h.to_numpy().reshape(-1, 20)
    a = origin_ic(truth, joined.score.to_numpy().reshape(-1, 20))
    b = origin_ic(truth, joined.score_reference.to_numpy().reshape(-1, 20))
    o = joined.iloc[::20]
    results = []
    for name, mask in [
        ("ALL_MATCHED", np.ones(len(o), bool)),
        ("OLD_MORNING", o.slot.isin(["10:30", "11:30"]).to_numpy()),
        ("OPENING", o.slot.eq("09:30").to_numpy()),
        ("AFTERNOON", o.slot.isin(["12:30", "13:30", "14:30", "15:30"]).to_numpy()),
        ("INTRADAY", o.category.eq("INTRADAY").to_numpy()),
        ("OVERNIGHT", o.category.eq("OVERNIGHT").to_numpy()),
    ]:
        if not mask.any():
            continue
        frame = pd.DataFrame(
            dict(day=days[mask], model=a[mask], reference=b[mask], delta=(a - b)[mask])
        )
        daily = frame.groupby("day")[["model", "reference", "delta"]].mean()
        results.append(
            dict(
                reference=label,
                group=name,
                origins=int(mask.sum()),
                model_IC=float(daily.model.mean()),
                reference_IC=float(daily.reference.mean()),
                **block_interval(daily.delta),
            )
        )
    return results


def per_run(out: Path, dest: Path) -> None:
    """Reviewable report exists before the immutable per-run gate is published."""
    metrics = pd.DataFrame([json.loads((dest / f"{r}_metrics.json").read_text()) for r in ROLES])
    report = (
        f"# {dest.name}: complete diagnostic map\n\n"
        "Exploratory price-only ranking; no executable P&L. Seven candidate origin slots, "
        "including conditional 09:32 opening issuance. OOS never selects epochs.\n\n"
        + markdown(
            metrics[
                [
                    "role",
                    "origins",
                    "sessions",
                    "daily_ic",
                    "actual_objective",
                    "top4",
                    "bottom4",
                    "pair_concordance",
                ]
            ]
        )
        + "\n\n[Interactive run view](../plots/s4_a_rankings.html) — "
        "select the exact fold and objective. "
        "Rank trajectories, all20 heatmaps, M1, monthly/session IC, retrieval, score margins, "
        "movement, true objective tails, energy and training selector panels.\n\n"
        "Each role has keyed scores, metrics, origin/slot/month tables, train-threshold tail "
        "cohorts, NUM/MAD intersections, original-Y and transformed-objective attribution, "
        "error-ranked complements, common/centered energy and source-quality strata. "
        "The role filename identifies inner training, inner validation, "
        "full-prefix refit or OOS.\n\n"
        "Calibration/refit epoch JSON separates online dropout-ON from full-population OFF "
        "metrics. Batch and parameter-gradient CSVs retain preclip/postclip/update norms. "
        "Binding JSON identifies the selected checkpoint and fresh refit reload. "
        "NR ordinal MSE and T2R transformed MSE have different units.\n\n"
        "All files for this run:\n\n"
    )
    report += "\n".join(f"- [{p.name}]({p.name})" for p in sorted(dest.iterdir()) if p.is_file())
    (dest / "RUN_DIAGNOSTICS.md").write_text(report + "\n")


def closeout(out: Path) -> None:
    roster, metrics, comparisons, categories, cohorts, traces = [], [], [], [], [], []
    for run in RUNS:
        dest = out / run
        passed = (dest / "PASS.json").exists()
        roster.append(
            dict(
                run_id=run,
                status="PASS"
                if passed
                else "FAILED"
                if (dest / "FAILURE.json").exists()
                else "NOT_RUN",
                report=str(dest / "RUN_DIAGNOSTICS.md"),
                dashboard=str(out / "plots/s4_a_rankings.html"),
            )
        )
        if not passed:
            continue
        gate = json.loads((dest / "PASS.json").read_text())
        for path, sha in gate["files"].items():
            if digest(Path(path)) != sha:
                raise ValueError("S4_COMPLETED_GATE_ARTIFACT_CHANGED")
        year = 2000 + int(run.split("-")[2][1:])
        arm = run.split("-")[4]
        f = pd.read_parquet(dest / "oos_scores.parquet")
        for role in ROLES:
            metrics.append(
                dict(run_id=run, **json.loads((dest / f"{role}_metrics.json").read_text()))
            )
            c = pd.read_csv(dest / f"{role}_energy_and_objective_cohorts.csv")
            c["run_id"] = run
            cohorts.append(c)
        c = pd.read_csv(dest / "category_and_anchor_metrics.csv")
        c["run_id"] = run
        categories.append(c)
        for p in sorted(dest.glob("*.json")):
            if p.stem.startswith(("calibration_", "refit_")) and p.stem.split("_")[-1].isdigit():
                traces.append(dict(run_id=run, **json.loads(p.read_text())))
        for ref in ["N1", "N2", "P"]:
            g = pd.read_parquet(out / f"F{year % 100}_S4_{ref}/oos_scores.parquet")
            comparisons.extend(
                dict(run_id=run, year=year, model=arm, **v) for v in paired(f, g, ref)
            )
        prior = PRIOR / f"HF20-S1S2-F{year % 100}-{arm}-S42/oos_scores.parquet"
        if prior.exists():
            comparisons.extend(
                dict(run_id=run, year=year, model=arm, **v)
                for v in paired(
                    f, pd.read_parquet(prior), "ARCHIVED_S2_DIFFERENT_FITTING_POPULATION"
                )
            )
    pd.DataFrame(roster).to_csv(out / "S4_EIGHT_START_DIAGNOSTIC_INDEX.csv", index=False)
    if not metrics:
        return
    m = pd.DataFrame(metrics)
    m.to_csv(out / "S4_ALL_ROLE_METRICS.csv", index=False)
    pd.DataFrame(comparisons).to_csv(
        out / "S4_MATCHED_BASELINE_AND_ARCHIVE_COMPARISONS.csv", index=False
    )
    pd.concat(categories, ignore_index=True).to_csv(
        out / "S4_CATEGORY_AND_ANCHOR_METRICS.csv", index=False
    )
    pd.concat(cohorts, ignore_index=True).to_csv(
        out / "S4_ALL_ROLE_EXTREME_OBJECTIVE_NUM_MAD_ENERGY.csv", index=False
    )
    pd.DataFrame(traces).to_json(
        out / "S4_COMPLETE_TRAINING_TRACE.json", orient="records", indent=2
    )
    annual = m.loc[m.role.eq("oos")]
    complete = len(annual) == 8 and annual.groupby("model").size().eq(4).all()
    equal = (
        annual.groupby("model")[["daily_ic", "top4", "bottom4", "pair_concordance"]].mean()
        if complete
        else pd.DataFrame()
    )
    equal.to_csv(out / "S4_EQUAL_YEAR_METRICS.csv")
    (out / "S4_VISUAL_AND_SCIENTIFIC_DIAGNOSTICS.md").write_text(
        "# S4-A: all-eight-run diagnostic review\n\n"
        + (
            "Eight numerical/visual payload stage gates passed; "
            "final browser QA is separately required.\n\n"
            if complete
            else "NOT_ALL_EIGHT_COMPLETED. No complete-campaign claim.\n\n"
        )
        + markdown(annual)
        + "\n\nEqual-year metrics (only complete four-fold arms):\n\n"
        + markdown(equal.reset_index())
        + "\n\n[All eight run reports](S4_EIGHT_START_DIAGNOSTIC_INDEX.csv) · "
        "[Complete file index](DIAGNOSTIC_FILE_INDEX.csv) · "
        "[Interactive dashboard](plots/s4_a_rankings.html).\n\n"
        "The matched-baseline table reports identical-key N1/N2/P differences and whole-month "
        "descriptive intervals. Archived S2 comparisons use common morning keys with verified "
        "returns but different fitting populations; they do not isolate one causal effect. "
        "The primary estimate weights sessions equally, then years equally; category-balanced "
        "and paired-session contrasts remain secondary. All intervals are exploratory, with "
        "shared overnight episodes and uncorrected research search. No trading-profit claim.\n\n"
        "The extreme-objective table retains every role and original TG20 event cohort, "
        "actual optimized loss, numerator/MAD decomposition and energy identities. Do not "
        "compare NR loss magnitudes against T2R loss. See all eight individual reports for "
        "checkpoint, gradient, fallback, tail and exact source-provenance files.\n"
    )
    inventory = []
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name != "DIAGNOSTIC_FILE_INDEX.csv":
            inventory.append(
                dict(
                    path=str(p),
                    bytes=p.stat().st_size,
                    sha256=digest(p),
                    type=p.suffix,
                    local_private=p.suffix in (".pt", ".parquet", ".npz", ".npy")
                    or p.suffix == ".html",
                )
            )
    pd.DataFrame(inventory).to_csv(out / "DIAGNOSTIC_FILE_INDEX.csv", index=False)
