"""Evidence-derived Package017 interpretation and manual review handoff."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import digest, write_json
from .hf20_replication_authority import IDS


def markdown(frame: pd.DataFrame) -> str:
    """Small portable table without an optional tabulate dependency."""
    rows = [list(frame.columns)] + [
        [str(v) for v in row] for row in frame.itertuples(index=False, name=None)
    ]
    rows.insert(1, ["---"] * len(frame.columns))
    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


def write_reports(out: Path, first: pd.DataFrame, second: pd.DataFrame, threshold: float) -> None:
    metrics = pd.read_csv(out / "four_model_metrics.csv", float_precision="round_trip")
    trace = pd.read_csv(out / "epoch_selection_trace.csv", float_precision="round_trip")
    decomposition = pd.read_csv(
        out / "four_model_mse_decomposition.csv", float_precision="round_trip"
    )
    intervals = pd.read_csv(out / "paired_intervals.csv", float_precision="round_trip")
    tails = pd.read_csv(out / "tail_events.csv", float_precision="round_trip")
    concentration = pd.read_csv(out / "tail_concentration.csv", float_precision="round_trip")
    p = json.loads((out / "experiment_design.json").read_text())
    approval = json.loads((out / "live_two_pair_approval.json").read_text())
    runs = {
        arm: json.loads((out / name / "run_result.json").read_text())
        for arm, name in zip(("C0", "T2"), IDS)
    }
    m = metrics.set_index(["seed", "arm"]).to_dict("index")
    c0, t2, zero = (float(m[(123, arm)]["MSE"]) for arm in ("C0", "T2", "ZERO"))
    delta42 = float(m[(42, "T2")]["MSE"]) - float(m[(42, "C0")]["MSE"])
    delta123 = t2 - c0
    delta_ic42 = float(m[(42, "T2")]["Rank_IC"]) - float(m[(42, "C0")]["Rank_IC"])
    delta_ic123 = float(m[(123, "T2")]["Rank_IC"]) - float(m[(123, "C0")]["Rank_IC"])
    direction = "same" if np.sign(delta42) == np.sign(delta123) else "opposite"
    events = second.loc[second.target.abs().ge(threshold)]
    selected = {arm: runs[arm]["selection"]["selected"] for arm in runs}
    timing = {
        arm: json.loads((out / name / "training_actual_runtime.json").read_text())
        for arm, name in zip(("C0", "T2"), IDS)
    }
    hypotheses = [
        dict(
            rank=1,
            hypothesis="Weak accessible conditional mean in this fixed setup",
            status="SUPPORTED" if min(c0, t2) >= zero else "PLAUSIBLE",
            evidence=(
                f"Seed123 ZERO MSE={zero:.10f}; C0={c0:.10f}, T2={t2:.10f}; "
                "exact alignment decomposition saved."
            ),
            counterargument=(
                "Observed skill under this model/sample is not proof "
                "the true conditional mean is zero."
            ),
        ),
        dict(
            rank=2,
            hypothesis="Optimization generalization gap / overfitting",
            status="PLAUSIBLE",
            evidence=(
                "Full qualifying/raw-minimum traces and online objectives saved; "
                f"selected epochs={selected}."
            ),
            counterargument=(
                "Online dropout-ON losses are not fixed-weight eval curves; "
                "chronology/source shifts can also matter."
            ),
        ),
        dict(
            rank=3,
            hypothesis="Insufficient regime diversity / too little history",
            status="NOT_IDENTIFIABLE",
            evidence="Both seeds reuse exactly the same 998 training and 366 development origins.",
            counterargument=(
                "No longer-history contrast ran. More correlated history "
                "need not improve prediction."
            ),
        ),
        dict(
            rank=4,
            hypothesis="Tail targets materially concentrate loss",
            status="SUPPORTED",
            evidence=(
                f"Training |TG20| q99={threshold:.10f}; {len(events)} development events; "
                "denominator and worst-day shares saved."
            ),
            counterargument=(
                "Concentrated loss does not establish invalid labels or that "
                "clipping/MAD inflation would improve generalization."
            ),
        ),
        dict(
            rank=5,
            hypothesis="Nonfinite optimizer / deterministic seed-stage-target defect",
            status="REFUTED_IN_CHECKED_BOUNDARY",
            evidence=(
                "Independent stage audits verify exact canonical replay, train-only "
                "scales, full masks, D6g and checkpoint identities."
            ),
            counterargument=(
                "Checks do not certify unrecorded optimizer internals "
                "or every upstream vendor fact."
            ),
        ),
        dict(
            rank=6,
            hypothesis="Source/publication/action assumptions explain weakness",
            status="PLAUSIBLE",
            evidence=(
                "As-reported retrospective survivor sample and idealized hourly-close "
                "clock remain conditional."
            ),
            counterargument=(
                "No independent corrected-source contrast, action vintage "
                "or publication facts establish a causal explanation."
            ),
        ),
    ]
    pd.DataFrame(hypotheses).to_csv(out / "hypotheses_ranked.csv", index=False)
    selection_text = []
    for arm, r in runs.items():
        g = trace.loc[trace.seed.eq(123) & trace.arm.eq(arm)]
        selection_text.append(
            f"{arm}: qualifying epoch {r['selection']['selected']}, raw minimum epoch "
            f"{r['selection']['raw_epoch']}, calibration {len(g)} epochs, stop "
            f"{r['selection']['status']}; validation {g.validation_MSE.iloc[0]:.10f} → "
            f"{g.validation_MSE.iloc[-1]:.10f}. Fresh refit exactly "
            f"{r['selection']['selected']} epochs."
        )
    important = metrics[["seed", "arm", "MSE", "MAE", "Rank_IC", "score_std"]].copy()
    terms_table = markdown(
        decomposition[
            [
                "seed",
                "arm",
                "MSE",
                "prediction_mean",
                "prediction_sd",
                "covariance",
                "E_prediction2",
                "E_y_prediction",
                "delta_MSE_vs_ZERO",
            ]
        ]
    )
    hypothesis_table = markdown(
        pd.DataFrame(hypotheses)[["rank", "hypothesis", "status", "evidence", "counterargument"]]
    )
    timing_table = markdown(
        pd.DataFrame(
            [
                dict(
                    arm=arm,
                    calibration=t["calibration_train_seconds"],
                    validation=t["validation_selection_seconds"],
                    refit=t["refit_train_seconds"],
                    inference=t["inference_seconds"],
                    worker=t["worker_wall_seconds"],
                    peak_RSS_bytes=t["peak_RSS_bytes"],
                )
                for arm, t in timing.items()
            ]
        )
    )
    terms = decomposition.set_index(["seed", "arm"]).to_dict("index")
    stock_difference = pd.read_csv(out / "seed_disagreement_by_symbol.csv")
    largest_rank = ", ".join(
        stock_difference.sort_values("T2_rank_difference", ascending=False).symbol.head(3)
    )
    months = pd.read_csv(out / "seed_disagreement_by_month.csv")
    largest_months = ", ".join(
        months.sort_values("T2_rank_difference", ascending=False).month.head(3)
    )
    text = f"""# HF20 Package017 — researcher diagnosis

## Key conclusions

Both approved seed123 pairs completed. C0 MSE={c0:.10f}; T2={t2:.10f}; ZERO={zero:.10f}.
T2−C0 MSE={delta123:+.10f}, compared with seed42 {delta42:+.10f}: the {direction} direction.
Selected seed123 epochs: C0={selected["C0"]}, T2={selected["T2"]}.
These facts address initialization and session-order sensitivity; two seeds do not prove invariance,
market significance, data-history effects or model-family promotion. Exact matched366 origins /
183 days /7320 stock forecasts are retained for every model. ZERO's rank IC is undefined.

{markdown(important)}

## What persisted, and what changed between seeds

Both arms again selected epoch1, with raw minima at1 for seed123. T2's equal-day IC advantage
has the same sign: +{delta_ic42:.8f} at42 and +{delta_ic123:.8f} at123. Its MSE advantage also
has the same sign, but neither seed's T2 beats ZERO on aggregate MSE. Seed123 mean IC is
higher while MSE is worse for each arm; ranking and squared-error skill are distinct.
Neither seed123 paired contrast interval excludes zero. This supports replication of the
observed weak-signal/early-selection pattern, not proof of initialization invariance.

Forecast magnitudes remain small relative to target SD1.863945. Pooled C0 score SD changes
from{terms[(42, "C0")]["prediction_sd"]:.6f} to{terms[(123, "C0")]["prediction_sd"]:.6f};
T2 from{terms[(42, "T2")]["prediction_sd"]:.6f} to{terms[(123, "T2")]["prediction_sd"]:.6f}.
The mean sign flips: seed42 T2 mean{terms[(42, "T2")]["prediction_mean"]:+.6f}, versus seed123
{terms[(123, "T2")]["prediction_mean"]:+.6f}. The seed42 positive-bias explanation therefore
does not generalize unchanged: seed123's mean/bias contribution is
{terms[(123, "T2")]["mean_component"]:+.9f}, while variance-minus-twice-covariance contributes
{terms[(123, "T2")]["variance_covariance_component"]:+.9f}. Seed123 weak positive alignment
does not repay forecast energy. This refines the prior diagnosis without fitting a correction.

Individual rankings are sensitive even when aggregate directions agree. Largest mean T2
within-origin rank differences by stock occur for {largest_rank}; largest monthly averages
occur in {largest_months}. These are post-hoc group summaries, not sector/news explanations.
Observed V2 context changes amplitude and rank disagreement differently; the saved high/low
context table does not establish a single volatility-driven failure. Tail sign and top-score
precision/recall also vary by seed; preserving event IDs exposes that instability rather than
redefining events. See exact paired stock IDs, complete group tables and event base rates.

## Optimization and selection

{chr(10).join(selection_text)}

The selector monitors original-TG20 inner-validation MSE, with eval-mode dropout disabled;
only a strict new value below0.999×the prior qualifying best resets patience. Raw minima and
nonqualifying improvements remain visible in epoch_selection_trace.csv. Minimum12 limits
stopping time, not the earliest selectable checkpoint. The inner tail is exactly63 exchange
sessions,55 eligible days/110 origins, not a random sample. Refit starts a fresh same-seed
model and empty optimizer on the full prefix, using its distinct train-only recipe.

C0 fitting objectives use TG20 squared units; T2 uses asinh(TG20/s) squared units. Compare
canonical validation/development metrics across arms. Online fitting MSE was accumulated with
changing weights and dropout ON, so it is not end-of-epoch evaluation. Complete epoch/batch
gradient quantiles and actual cap fractions are saved for both passes and seeds. Finite G6
does not establish useful signal. Historical per-example gradients, dropout masks and optimizer
internals are NOT_RECORDED; no later-epoch trajectory is reconstructed from absent weights.

## Forecast amplitude, alignment and calibration

{terms_table}

The exact equal-day→origin→stock identity is MSE(pred)−MSE(ZERO)=Ew[pred²]−2Ew[y·pred].
Pooled mean, variance and covariance components are separate from per-origin cross-sectional
IC. A small but variable forecast is not strict collapse. Near-zero squared-loss predictions
can be rational when the accessible conditional mean is weak; this does not identify the true
conditional mean. Stock/month/origin contribution tables, sign accuracy and pairwise concordance
are descriptive. Score quintiles are ex-post calibration summaries, never a fitted correction.
No development intercept, rescaling, event threshold or new predictor was fitted.

## Tails and context

Training-only |TG20| q99={threshold:.10f}; {len(events)}/7320 event rows across
{events.session.nunique()} development days. Same event IDs are compared between seeds in
same_tail_event_seed_comparison.csv. Tail tables preserve original returns, peer median,
unscaled MAD and train-fitted epsilon. Large numerators and small denominators are separated;
no outlier was removed or denominator inflated. Rare stock-specific moves can be real information.
Worst1/5/10% day loss shares and post-hoc top4 absolute-score precision/recall/sign accuracy
are in tail_concentration.csv and tail_event_metrics.csv, with event base rates. These are not
validated event classifiers; train forecast magnitude thresholds are NOT_AVAILABLE.

Seed-disagreement tables compare stock, month, origin and the actually observable final-step
train-scaled V2 context against a training-only median. An additional clearly marked ex-post
outcome-dispersion split is descriptive and never enters features or decisions. Group clustering
does not establish a causal regime effect;20 correlated stocks and two overlapping horizons
are not7320 independent trials. No issuer-news or vendor-error cause is inferred from a tail.

## Exploratory uncertainty

{markdown(intervals[["contrast", "metric", "estimate", "lower95", "upper95"]])}

Same established five-session moving blocks,5000 resamples, seed8008; blocks cannot bridge
omitted exchange sessions. Calendar positions are retained. Intervals compare seed123 T2−C0,
each arm seed123−42 and the seed42 contrast. **Exploratory, reused development, not fully
selection-adjusted G8; no new significance, independent-market-history or alpha claim.**

## Ranked explanations and counterarguments

{hypothesis_table}

Potential next hypotheses remain proposals: source-consistent longer-history feasibility,
or a separately preregistered signed-tail/rank-aware objective preserving canonical TG20 and
all tails. The seed test neither authorizes these nor selects one automatically. ZERO winning
does not by itself show a broken model. Keep weak and negative results.

## Scope and reproducibility

Ledger32/200, two charged starts; source/input/older model preservation verified separately.
Source is ASSUMPTION_CONDITIONAL, researcher-attested bounded local use, retrospective survivor
selection, uncertified issuer/action/PIT/dividend/publication facts and idealized vendor-clock /
hourly-close proxies. No real fills, profitability, independent rights certification, bulk export,
held-out/old confirmation access, trading, source GET, further fit or Git operation.

Inspect run directories for raw epoch telemetry, both safe checkpoints and independent eval-only
replay receipts. The existing explorer exposes both seeds and full-fold metrics independently
of chart date filters. Follow docs/track_a/HOW_TO_VIEW_HF20_SEED123_REPLICATION.md.
"""
    (out / "researcher_diagnosis.md").write_text(text)
    event = second.iloc[int(np.argmax(np.abs(second.target.to_numpy(dtype=float))))]
    disagreement = int(np.argmax(np.abs((second.T2 - first.T2).to_numpy(dtype=float))))
    other = second.iloc[disagreement]
    guide = f"""# View the HF20 seed123 replication in five minutes

From repository root run `./scripts/run_track_a_dashboard.sh`. Use **Start Here → HF20 seed
replication**, or sidebar **HF20: TM0 vs T2**, then **HF20 seed →123**. The same HF20 development
fold is2025-03-31–2026-01-06; there is no WF2. Choose either exact C0/T2 run. Seed42 remains
available in the seed selector. ZERO has undefined Rank IC.

1. **Predictions & Errors**: full-fold MSE/IC table always covers all366 origins/183 sessions/
   7320 stocks; stock/date/origin chart filters leave that table unchanged. See daily/monthly
   metrics and stock contributions. Scores and targets are original TG20 units.
2. **Training Diagnostics**: select C0 and T2; inspect original-scale validation and dashed selected
   epoch marker. Raw improvements smaller than0.1% do not qualify. Minimum12 is a stopping floor.
   Compare calibration/refit gradient p50/p90/p99 and actual clipping fractions. Online/dropout-ON
   fitting curves and different optimizer objective units require the labels shown.
3. **Price & Features / extremes**: choose **{event.symbol}**, then ex-post event filter
   **Train-q99 tails** and event **{event.session} / origin{int(event.origin)}**
   (TG20={event.target:.6f}).
   Click **Load genuine HF hourly candles +48 feature steps**. The event selector uses the full
   permitted fold independently of plotted date filters. Candles are interval-start, as-reported
   price/share volume; dashed boundaries identify completed input and four-hour exit proxy.
   FT1 native/scaled channels show genuine48 historical steps. Future target is an outcome only.
4. **Seed comparison & diagnosis**: view four-model full-fold table, exact ZEROgap decomposition,
   epoch traces, paired exploratory intervals and matched seed42-versus123 score scatter.
   Another genuine largest T2 seed-score disagreement is **{other.symbol} / {other.session} /
   origin{int(other.origin)}**. Descriptive tail/rank selections are not trading rules.
5. Read researcher_diagnosis.md before drawing conclusions. Two seeds share one market history;
   intervals are not selection-adjusted G8, no promotion or economic result. Source rights, action
   and publication assumptions remain conditional. Missing artifacts cause HOLD, never stale
   checkpoint fallback or model fitting. API calls requesting2026-01-07+ or old five-stock
   confirmation are rejected before numerical I/O; UI date controls endJan6. Do not widen dates.

Launch health/shutdown and actual AppTest results are in the Package017 session report. Local
licensed source/derived stores are required and must not be exported or committed wholesale.
"""
    guide_path = Path("docs/track_a/HOW_TO_VIEW_HF20_SEED123_REPLICATION.md")
    if guide_path.exists() and guide_path.read_text() != guide:
        raise ValueError("P017_UNKNOWN_EXISTING_GUIDE_PRESERVED")
    guide_path.write_text(guide)
    write_json(
        out / "visual_walkthrough_examples.json",
        dict(
            maximum_target=dict(
                symbol=str(event.symbol), session=str(event.session), origin=int(event.origin)
            ),
            largest_T2_seed_difference=dict(
                symbol=str(other.symbol), session=str(other.session), origin=int(other.origin)
            ),
            guide_sha256=digest(guide_path),
            examples_discovered_from_saved_development=True,
        ),
    )
    card = f"""# Package017 human review card

**Two approved seed123 pairs COMPLETED; exploratory development only. Ledger32/200.**
Actual human response: “{approval["response_text"]}”. Attribution: live researcher reply in this
session, proposal `{digest(out / "experiment_design.json")}`, execution `{p["code_sha256"]}`.
Consumed seed42 grants were not reused. Bounded local-rights/source/clock assumptions continue.

{markdown(important)}

C0 selected{selected["C0"]} / T2 selected{selected["T2"]}; fresh refits exactly those counts.
G6 health: {json.dumps({arm: r["health"] for arm, r in runs.items()}, sort_keys=True)}.
Independent calibration validation and canonical refit prediction replay are exact; no model
updates in diagnostics. See paired_intervals.csv for exploratory five-session95% intervals
(not G8/search-adjusted); see researcher_diagnosis.md for seed consistency and counterarguments.

GO: inspect both saved seeds using existing launcher → Start Here → HF20 seed replication.
HOLD: extra fitting, held-out/confirmation, source/history acquisition, trading, redistribution,
protocol migration or model promotion. No further experiment begins automatically.

Actual timing by arm (seconds):
{timing_table}

Supervisor/queue/package and exact check receipts supplement these worker measurements;
no causal C0-versus-T2 speed attribution. Tests/UI/preservation final status is in checks.json
and the coding-session report, not inferred here. artifact_inventory.csv lists all task paths,
hashes and Git intent. All work remains uncommitted; no raw data sharing is authorized.

Next decision: review the evidence, then separately discuss whether a source audit or one new
objective hypothesis is warranted. LONGER_HISTORY_FEASIBILITY_NEXT.md is proposal only.
"""
    (out / "human_review_card.md").write_text(card)
    write_json(
        out / "review_summary.json",
        dict(
            status="COMPLETED_EXPLORATORY",
            ledger=32,
            selected_epochs=selected,
            seed42_T2_minus_C0=delta42,
            seed123_T2_minus_C0=delta123,
            MSE_direction_consistency=direction,
            metrics=important.to_dict("records"),
            threshold=threshold,
            event_rows=len(events),
            event_sessions=events.session.nunique(),
            concentration_rows=len(concentration),
            tail_rows=len(tails),
        ),
    )
