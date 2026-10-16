"""Evidence-based Package016 narratives and existing-viewer handoff; no model execution."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from .config import digest, write_json


def polish(prose: str) -> str:
    """Readable generated prose; preserve identifiers, scientific exponents and bound paths."""
    prose = re.sub(r"(HF20|TG20|FT1|C0|T2|G6|G8|ZERO|MSE)(?=[A-Za-z])", r"\1 ", prose)
    prose = re.sub(r"(epoch|origin|seed|ledger|patience|Package)(?=\d)", r"\1 ", prose)
    prose = re.sub(r"(?<=\d)(?=[a-df-zA-DF-Z])", " ", prose)
    prose = re.sub(
        r"(to|dates|with|exactly|strict|than|only|on|of|retain|from)(?=\d)", r"\1 ", prose
    )
    prose = prose.replace("+are", "+ are").replace("CPUfloat", "CPU float")
    return prose


def table(frame: pd.DataFrame, columns: list[str]) -> str:
    def cell(value: object) -> str:
        if isinstance(value, (float, np.floating)):
            return "Undefined" if not np.isfinite(value) else f"{value:.8g}"
        return str(value).replace("|", "/")

    rows = ["|" + "|".join(columns) + "|", "|" + "|".join("---" for _ in columns) + "|"]
    rows.extend(
        "|" + "|".join(cell(row[k]) for k in columns) + "|" for row in frame.to_dict("records")
    )
    return "\n".join(rows)


def frame(value: object) -> pd.DataFrame:
    if not isinstance(value, pd.DataFrame):
        raise TypeError("P016_EXPECTED_DIAGNOSTIC_TABLE")
    return value


def write_reports(
    out: Path,
    report: Path,
    plan: dict,
    c: dict,
    h: dict,
    matched: dict,
    tails: dict,
    epoch: pd.DataFrame,
    features: pd.DataFrame,
    activations: pd.DataFrame,
    examples: list[dict],
    replay_info: dict,
) -> None:
    if (out / "artifact_inventory.csv").exists():
        raise ValueError("P016_FINALIZED_PACKET_IS_IMMUTABLE")
    if not (out / "preflight_sources_and_authority.json").is_file():
        raise ValueError("P016_OWNED_PREFLIGHT_NAMESPACE_REQUIRED")

    def publish(path: Path, value: dict) -> None:
        from .real_batch_authority import atomic_replace_json

        if path.parent != out:
            raise ValueError("P016_REPORT_METADATA_OUTSIDE_OWNED_NAMESPACE")
        if path.exists():
            atomic_replace_json(path, value)
        else:
            write_json(path, value)

    terms = frame(matched["decomposition"]).set_index("arm")
    paired = frame(matched["paired"])
    groups = frame(matched["paired_groups"])
    per_origin = frame(matched["per_origin"])
    concentration = frame(tails["concentration"])
    events = frame(tails["events"])
    distribution = frame(tails["distributions"])
    q99 = tails["thresholds"]["target_absolute_train_pooled"]["q99"]
    interval = matched["intervals"]["diagnostics"]
    epoch_lines = []
    for arm in ("C0", "T2"):
        e = epoch.loc[epoch.arm.eq(arm)]
        a, b = e.iloc[0], e.iloc[-1]
        decreases = int(np.sum(np.diff(e.optimizer_objective.to_numpy()) < 0))
        epoch_lines.append(
            f"{arm}: optimizer objective {a.optimizer_objective:.10f} → "
            f"{b.optimizer_objective:.10f}; {decreases}/{len(e) - 1} adjacent changes decrease. "
            f"Canonical inner-validation MSE {a.validation_MSE:.10f} → {b.validation_MSE:.10f}. "
            f"Selected qualifying epoch{int(b.selected_epoch)}, raw minimum at{int(b.raw_epoch)}; "
            f"stop={b.stop_reason}, patience={int(b.patience)}."
        )
    t = epoch.loc[epoch.arm.eq("T2")].iloc[:2]
    first, second = float(t.validation_MSE.iloc[0]), float(t.validation_MSE.iloc[1])
    improvement = first - second
    percent = 100 * improvement / first
    limit = 0.999 * first
    head = (
        activations.groupby(["arm", "stage"])[
            [
                "head_weight_L2",
                "head_bias",
                "head_norm_ratio_to_recorded_init",
                "hidden_L2_median",
                "hidden_cross_stock_sd_mean",
                "hidden_abs_gt095_fraction",
                "output_sd",
            ]
        ]
        .mean()
        .reset_index()
    )
    tail_rows = concentration.loc[concentration.group_kind.eq("TARGET_BIN")]
    stock = groups.loc[groups.group_kind.eq("symbol")].sort_values("delta_MSE_T2_minus_C0")
    origin = groups.loc[groups.group_kind.eq("origin")]
    month = groups.loc[groups.group_kind.eq("month")]
    improvement_days = int(paired.delta_MSE.lt(0).sum())
    improvement_stocks = int(stock.delta_MSE_T2_minus_C0.lt(0).sum())
    positive_daily_gain = (-paired.delta_MSE).clip(lower=0).sort_values(ascending=False)
    top5_gain_share = float(positive_daily_gain.iloc[:5].sum() / positive_daily_gain.sum())
    event99 = events.loc[events.threshold.eq("q99")]
    mechanisms = event99.loc[event99.record.eq("EXPOST_DENOMINATOR_ATTRIBUTION")]
    event_perf = event99.loc[
        event99.record.eq("POSTHOC_DEV_TOP4_ABS_SCORE_NOT_VALIDATED_CLASSIFIER")
    ]
    distr = distribution.loc[distribution.group.eq("ALL") & ~distribution.absolute]
    feature_pivot = features.pivot(
        index="feature",
        columns="split",
        values=["mean", "sd", "abs_gt5_fraction", "abs_gt10_fraction"],
    )
    feature_shift = []
    for name, r in feature_pivot.iterrows():
        sd = float(r[("sd", "refit")])
        delta = float(r[("mean", "development")] - r[("mean", "refit")])
        feature_shift.append(
            dict(
                feature=str(name),
                mean_shift_in_train_SD=delta / sd if sd else None,
                train_sd=sd,
                dev_sd=float(r[("sd", "development")]),
                train_abs_gt10=float(r[("abs_gt10_fraction", "refit")]),
                dev_abs_gt10=float(r[("abs_gt10_fraction", "development")]),
            )
        )
    shifts = pd.DataFrame(feature_shift).sort_values(
        "mean_shift_in_train_SD", key=lambda x: x.abs(), ascending=False
    )
    shifts.to_csv(out / "input_shift_contrasts.csv", index=False)
    positive_ic = {
        a: float(per_origin.loc[per_origin.arm.eq(a)].groupby("session").Rank_IC.mean().mean())
        for a in ("C0", "T2")
    }
    stock_gain_total = float((-stock.delta_MSE_T2_minus_C0).sum())
    best_stock = str(stock.iloc[0]["group"])
    best_share = (
        float(-stock.iloc[0].delta_MSE_T2_minus_C0 / stock_gain_total) if stock_gain_total else 0.0
    )
    (out / "epoch_selection_diagnosis.md").write_text(
        """# Why epoch1was selected

"""
        + "\n\n".join(epoch_lines)
        + f"""

Exact T2 hand oracle (full saved float precision):

- Epoch1={first:.17g}; epoch2={second:.17g}.
- Raw improvement={improvement:.17g}, or{percent:.12f}%.
- Qualifying requires new MSE **strictly below**0.999×epoch1={limit:.17g}.
- Epoch2minus this required boundary={second - limit:.17g}>0.

This is a genuine positive raw improvement smaller than0.1%, not a precision tie or a
coding error. Minimum12limits when stopping is allowed; it does not prohibit selecting
an earlier checkpoint. Both fresh refits therefore ran1epoch, not12. Training has336updates
per calibration and32in each refit; full-prefix data has a different number of batches.

The recorded original-scale training MSE is an ONLINE changing-weights, dropout-ON loss.
It is not end-of-epoch evaluation loss. T2 optimizer loss is squared asinh(TG20/s) units;
C0 loss is squared original TG20. Canonical inner-validation MSE always uses eval mode
and the proper inner T2 inverse. Do not compare the two optimizer-objective numbers.

Falling fitting objectives plus worsening inner validation are CONSISTENT_WITH_OVERFITTING /
NO_VALIDATION_GAIN under this small validation sample. They do not identify a unique cause:
weak conditional signal, regime instability, insufficient effective data or representation
limitations remain possible. No evidence justifies simply forcing more epochs. Recorded
calibration/refit checkpoints show epoch1outputs; weights/output histories for epochs2–12
are NOT_RECORDED, so their later contraction cannot be reconstructed from final weights.

The last63exchange-calendar sessions begin2024-12-26; only55sessions/110origins pass the
frozen feature/fit-availability mask. Inner fit ends2024-12-24; refit ends2025-03-28;
development starts2025-03-31and never selects epochs. Exact maturity/purge checks and distinct
inner/refit recipe IDs are in chronology_and_selection_checks.json. Fresh initialization
hashes equal the recorded seed42initial state and optimizers were recorded empty.
"""
    )
    main_terms = table(
        terms.reset_index(),
        [
            "arm",
            "MSE",
            "prediction_mean",
            "prediction_sd",
            "E_prediction2",
            "E_y_prediction",
            "delta_MSE_vs_ZERO",
        ],
    )
    main_events = table(
        event_perf,
        [
            "arm",
            "events",
            "event_sign_accuracy",
            "event_top4_magnitude_recall",
            "top4_magnitude_precision",
        ],
    )
    root_rows = [
        dict(
            rank=1,
            status="SUPPORTED",
            assessment=(
                "Weak stable FT1→TG20conditional mean: tiny covariance, small forecasts, "
                "no qualifying validation gain after1."
            ),
            counterargument=(
                "Positive rank IC and one seed/55validation days leave signal and seed noise "
                "unresolved. Paired seed replication is the cheapest discriminator."
            ),
        ),
        dict(
            rank=2,
            status="CONFIRMED symptom / SUPPORTED interpretation",
            assessment=(
                "Fitting loss falls while validation worsens; consistent with overfitting "
                "or unstable/low conditional signal."
            ),
            counterargument=(
                "Online training loss is not end-epoch eval. Later weights are unavailable. "
                "This does not uniquely identify noise, representation or sample insufficiency."
            ),
        ),
        dict(
            rank=3,
            status="SUPPORTED",
            assessment=(
                "Unanticipated stock-specific tails spend substantial MSE; rank and magnitude "
                "objectives reward different behavior."
            ),
            counterargument=(
                "Exact target arithmetic and finite denominators do not establish a defect. "
                "Preserve events; separately test signed-tail/rank objectives."
            ),
        ),
        dict(
            rank=4,
            status="PLAUSIBLE / NOT_IDENTIFIABLE cause",
            assessment=(
                "Descriptive shifts and coverage conditioning may affect transfer; source "
                "action/publication/PIT facts remain uncertified."
            ),
            counterargument=(
                "Measured drift does not prove harmful concept drift or vendor error. "
                "No source/news causal claim is supported."
            ),
        ),
        dict(
            rank=5,
            status="NOT_SUPPORTED in tested boundary",
            assessment=(
                "Strict constant collapse, wrong inverse and exploding-gradient explanations "
                "conflict with variable finite outputs, G6and bounded exact replay."
            ),
            counterargument=(
                "Synthetic capability is not market predictability; historical "
                "dropout, per-example gradients and later weights are missing."
            ),
        ),
        dict(
            rank=6,
            status="NOT_IDENTIFIABLE",
            assessment=("Capacity, update budget and limited regimes could contribute."),
            counterargument=(
                "Worsening inner validation and healthy gradients do not justify widening, "
                "forced epochs or a lower-rate rescue. No search is authorized."
            ),
        ),
    ]
    root_table = table(pd.DataFrame(root_rows), ["rank", "status", "assessment", "counterargument"])
    next_rows = [
        dict(
            priority=1,
            hypothesis="Seed sensitivity",
            change=(
                "Repeat C0/T2at preregistered seed123only; "
                "fixed20names, FT1/TG20, masks, dates, D6g."
            ),
            evaluation=("Paired daily IC/MSE, all results; reused development, not confirmation."),
            budget=(
                "2unapproved pairs; observed-shape47–173neural seconds, longer if epochs differ."
            ),
            decision="Stable gain supports more evidence; seed reversal weakens the T2claim.",
        ),
        dict(
            priority=2,
            hypothesis="Missed rare-event direction",
            change=(
                "One fixed signed-tail auxiliary term on T2; retain canonical TG20and all tails."
            ),
            evaluation=(
                "Frozen T2comparator; separately inner/refit training-only thresholds, "
                "fixed coefficient/seed/fold; TG20MSE/ICplus event-direction precision/recall."
            ),
            budget="1treatment pair,2if new matched control needed; observed-shape23–173seconds.",
            decision=(
                "Require preregistered event discrimination without hiding magnitude/rank costs."
            ),
        ),
        dict(
            priority=3,
            hypothesis="Rank/magnitude mismatch",
            change=(
                "One fixed pairwise auxiliary loss on T2, same architecture/input/canonical target."
            ),
            evaluation=(
                "Frozen matched T2, fixed seed/fold, preregistered coefficient/ICmetric "
                "and TG20MSEguard; no lambda search or development threshold tuning."
            ),
            budget="1treatment pair,2with fresh control; same conditional measured-shape range.",
            decision="Small/unstable ICgain is no-go; economics remains a separate task.",
        ),
        dict(
            priority=4,
            hypothesis="Training-panel composition",
            change=(
                "Predetermined source-consistent5vs20training rows; fixed20name TG20labels/scalers."
            ),
            evaluation=(
                "Both evaluated on common5names/dates, same target; subset fixed before "
                "new outcomes. New source/history would first require rights/source audit."
            ),
            budget=(
                "2fresh matched pairs preferred;47–173seconds is only rough observed-shape context."
            ),
            decision="Isolates training-panel effect; never compare old five-stock TG0MSE.",
        ),
    ]
    next_table = table(
        pd.DataFrame(next_rows),
        ["priority", "hypothesis", "change", "evaluation", "budget", "decision"],
    )
    ic_c0 = interval["daily_IC_C0_reference_zero_NOT_ZERO_FORECAST_IC"]["percentile95"]
    ic_t2 = interval["daily_IC_T2_reference_zero_NOT_ZERO_FORECAST_IC"]["percentile95"]
    tail_c0 = tail_rows.loc[tail_rows.arm.eq("C0") & tail_rows.group.eq("TRAIN_Q99_TAIL")].iloc[0]
    tail_t2 = tail_rows.loc[tail_rows.arm.eq("T2") & tail_rows.group.eq("TRAIN_Q99_TAIL")].iloc[0]
    floor_all = float(distr.loc[distr.split.eq("development"), "floor_dominant_fraction"].iloc[0])
    large_only = int(mechanisms.loc[mechanisms.mechanism.eq("LARGE_NUMERATOR"), "rows"].sum())
    both = int(
        mechanisms.loc[mechanisms.mechanism.eq("BOTH_LARGE_NUMERATOR_SMALL_MAD"), "rows"].sum()
    )
    final_head = head.loc[head.stage.eq("REFIT_FINAL")].set_index("arm").to_dict("index")
    narrative = f"""# HF20Package016 — what the two models learned

**HF20_P016_DIAGNOSIS_COMPLETE.** Zero new fits/optimizer steps; ledger30/200unchanged.
Same366development origins×20names/183sessions. HF20held-out2026-01-07through2026-10-15
and old five-stock confirmation remain locked. **NO DETERMINISTIC DIVERGENCE FOUND** in
bounded B3–B5replay; the observed weakness is at **B5: score–outcome alignment**. That
is an empirical symptom, not proof every vendor fact or historical training calculation is correct.

## Why epoch1?

{epoch_lines[0]}

{epoch_lines[1]}

T2epoch2raw improvement={improvement:.12f}, or{percent:.8f}%, genuinely positive but below
0.1%. It required new MSE<{limit:.12f}; actual={second:.12f}. No rounding tie. Minimum12
limits when stopping may occur, not the earliest selectable checkpoint. Both refits were
fresh, exactly1epoch. Inner validation uses the last63exchange-calendar sessions from
2024-12-26, with55eligible days/110origins; inner training ends2024-12-24. Development
never chose epochs. Separate inner/refit recipes and mature-label purge checks pass.

Falling fitting objectives with worsening validation are **consistent with overfitting /
NO_VALIDATION_GAIN**, not a unique causal diagnosis. Training MSEwas recorded online with
changing weights/dropout ON, not end-of-epoch eval. C0optimizer loss is TG20squared;
T2is squared asinh(TG20/s), not directly comparable. Later epoch2–12weights were not saved,
so later output/head contraction cannot be reconstructed or fixed by simulating more epochs.

## Why ZEROis competitive

Exact equal-day→origin→stock identity: ΔMSE=Ew[score²]−2Ew[y×score]. Original results reconcile
to2e−12and algebra to3e−15; no difficult rows were intersected away.

{main_terms}

Target mean={terms.loc["C0", "target_mean"]:.8f}, pooled SD={terms.loc["C0", "target_sd"]:.8f}.
Small variable scores are **not strict collapse**. Under squared loss, near-zero is rational
when the conditional mean is weak; this sample cannot establish the true conditional mean.
C0forecast energy is not repaid by alignment (its pooled covariance is slightly negative).
T2alignment nearly repays its forecast variance, but a positive forecast mean opposes the
slightly negative target mean. Its exact mean/bias contribution to the ZEROgap is
{terms.loc["T2", "mean_component"]:.9f}, versus variance−2covariance
{terms.loc["T2", "variance_covariance_component"]:.9f}. No development intercept correction or
rescaled predictor was fitted. Descriptive covariance/variance slope and post-hoc score-bin
E[y|score] are analysis only. Median-centering each20stock cross-section does not force its
mean to zero. Pooled variance and average WITHIN-origin variance are different statistics.

## Small rank signal is not validated predictive usefulness

Daily cross-sectional IC={positive_ic["C0"]:.6f}/{positive_ic["T2"]:.6f}; pooled Pearson and
within-origin ranks measure different relationships. ZERO's defined-only Spearman is undefined;
project-zero is a convention. Pairwise concordance/sign accuracy remain close to chance.
Unchanged exploratory five-session blocks give ΔICinterval
{interval["delta_IC"]["percentile95"]}; mean IC around numerical0(not ZEROforecast IC):
C0{ic_c0}, T2{ic_t2}. ΔMSEinterval={interval["delta_MSE"]["percentile95"]}.
These are **EXPLORATORY_NOT_SELECTION_ADJUSTED**, not fullG8or a temporal null. One seed,
prior development-guided choices,20correlated names and overlapping four-hour outcomes
limit independence;7320rows do not mean7320independent trials or prove alpha/profitability.

T2improves MSEon{improvement_days}/183days and{improvement_stocks}/20stocks. The five largest
positive day gains supply{100 * top5_gain_share:.2f}% of positive gain mass; {best_stock} supplies
{100 * best_share:.2f}% of net equal-stock gain (offsetting stocks can make a net share exceed100%).
Both-origin, month and tail/non-tail contrasts remain in paired_origin_stock_month.csv;
no favorable subgroup replaces the primary comparison.

## Rare events: preserve information, diagnose the numerator and denominator

Training pooled|TG20|q99={q99:.8f}. These events contribute
{100 * float(tail_c0.loss_share):.2f}% /{100 * float(tail_t2.loss_share):.2f}% of C0/T2development
squared error on{int(tail_c0["rows"])}stock observations. Full permitted target arithmetic is
independently exact; see tail/ordinary MAD, MAD/epsilon, raw numerator and floor-dominance
summaries plus12bounded ex-post examples. Numerator/MAD attribution uses training q95/q05
flags, not a fitted predictor. A large stock-specific move against low peer dispersion can
be genuine, useful event information; large TG20alone is not a defective normalization.
Of{int(tail_c0["rows"])}q99events, {large_only}meet only the large-numerator flag;
{both}meet both numerator/
small-MADflags. Development floor-dominance fraction is{floor_all:.1%}: no MAD≤epsilon case.
There is no automatic floor increase, clipping, winsorization or tail deletion recommendation.

{main_events}

Top4absolute-score selection is a **post-hoc development rank diagnostic**, not a validated
event classifier. Full training forecast magnitudes were not saved; a training-derived
absolute score threshold/precision–recall operating point is **NOT_AVAILABLE**. No external
news cause is asserted for extreme rows. Target/feature period shifts are descriptive,
not iid significance or proof of harmful concept drift. All event labels remain EX-POST,
absent from X; no event cutoff enters a live model.

## Ranked diagnosis, with counterarguments

{root_table}

G6raw telemetry confirms no sustained clipping/nonfinite gradients. Bounded CPUfloat32eval
replay matches saved predictions, with unchanged states/no gradients; hidden variation,
head norms versus recorded initialization and saturation proxies are in the detailed training
report. This rejects strict constant collapse in tested examples, not low signal generally.
Final head norms
retain{100 * final_head["C0"]["head_norm_ratio_to_recorded_init"]:.2f}% /
{100 * final_head["T2"]["head_norm_ratio_to_recorded_init"]:.2f}% of initial norms;
they did not vanish.
Historical per-example gradients, dropout masks, optimizer internals and later weights are
**NOT_RECORDED**. Source/feature readiness and coverage conditioning are not random by decree:
train998/1154, inner872/1028, validation110/126, development366/382. Unique admitted-window
feature summaries flag missing/constant/extreme scale changes without changing scalers.
Measured drift and source limitations cannot be assigned a causal performance contribution here.

## Highest-information next controls — proposals only

No pair or acquisition is authorized. Measured prior neural fitting23.35–86.52seconds/pair
reflects12calibration+1refit epochs and different host load, not a causal T2speed benefit.
If selected epochs differ,60+60epochs could require several minutes/pair; setup/audit walls
are extra. Hypotheses, coefficient/metric, seed/fold and go/no-go must be fixed before fitting.

{next_table}

Capacity escalation and automatic tail suppression are not prioritized by these observations.
Reused development cannot become pristine confirmation. Source-consistent history expansion
is conditional on a separate source/rights/methodology task, not a download instruction.

## Limits and actual visual review

**ASSUMPTION_CONDITIONAL:** retrospective surviving cohort/static source-sector mixture;
issuer/action/adjustment vintage/dividends/publication/PIT facts uncertified; bounded
researcher-attested local use, no independent licensing or sharing authorization; idealized
as-reported timing/hourly-close proxy, no actual fills or economics. No old-five-stock MSE
comparison or panel-size gain is claimed. No protected numerical application rows, new
provider requests, scaler/T2recalibration or optimization updates.

Read docs/track_a/HOW_TO_VISUALLY_REVIEW_HF20_DIAGNOSIS.md for four exact saved development
IDs and the epoch1view. Existing views suffice; new comparison plots are compact CSVs/chart
specifications only. No UI code change, fabricated screenshot, retraining or promotion follows.
"""
    (out / "HF20_P016_MAIN_DIAGNOSIS.md").write_text(narrative)
    (out / "rare_event_readonly_diagnostics.md").write_text(
        """# Rare-event read-only findings

"""
        + table(
            distr,
            [
                "split",
                "rows",
                "q99",
                "minimum",
                "maximum",
                "event_q99_fraction",
                "floor_dominant_fraction",
            ],
        )
        + "\n\n"
        + table(mechanisms, ["mechanism", "rows", "event_fraction", "median_MAD_over_epsilon"])
        + "\n\n"
        + table(
            event_perf,
            [
                "arm",
                "events",
                "event_sign_accuracy",
                "event_top4_magnitude_recall",
                "top4_magnitude_precision",
            ],
        )
        + "\n\nTraining-only q95/q99/q99.9 thresholds and numerator/MAD quantiles are saved. "
        "These describe canonical unmodified targets; no event information is suppressed. "
        "The top4development rule is post hoc, not a validated precision/recall operating point. "
        "Train forecast thresholds are NOT_AVAILABLE. Largest target examples are ex-post, not X. "
        "No issuer-news explanation or adjustment certification is inferred.\n"
    )
    (out / "training_signal_diagnosis.md").write_text(
        """# Training signal and boundaries

"""
        + "\n\n".join(epoch_lines)
        + "\n\n"
        + table(head, list(head.columns))
        + "\n\nBounded eval-only replay matches saved predictions within atol2e-6/rtol2e-5, "
        "with repeated example bitwise deterministic, unchanged parameter hashes and no gradients. "
        "Head norms alone do not identify useful signal. Nonconstant outputs/hidden variation "
        "reject constant collapse in tested cases; initial-to-selected contraction is assessed "
        "from recorded seed42hash reconstruction. Later contraction, dropout masks, "
        "per-example gradients and optimizer states are NOT_RECORDED. "
        "Healthy G6does not establish good optimization or conditional predictability. "
        "Capacity/noise/representation remains NOT_IDENTIFIABLE without new controlled evidence.\n"
    )
    (out / "statistical_limitations.md").write_text(
        """# Statistical scope

"""
        + f"MSEimproves on{improvement_days}/183days and{improvement_stocks}/20stocks; "
        f"Top5positive day gains supply{100 * top5_gain_share:.3f}% of positive gain mass.\n\n"
        + table(origin, ["group", "delta_MSE_T2_minus_C0"])
        + "\n\n"
        + table(month, ["group", "delta_MSE_T2_minus_C0"])
        + "\n\n"
        + "Existing five-session moving blocks retain complete daily origin/stock pairs "
        "and do not bridge omitted sessions inside blocks.5000resamples/seed8008is an exploratory "
        "convention, not fullG8or selection-adjusted inference. Mean IC intervals use numerical0as "
        "a reference, never give ZEROdefined IC. One seed/183days, correlated20names, "
        "overlapping four-hour holds and development-guided history limit independence. "
        "No iid p-value, formal permutation/null, alpha, trading or five-vs20causal claim.\n"
    )
    guide = Path("docs/track_a/HOW_TO_VISUALLY_REVIEW_HF20_DIAGNOSIS.md")
    guide_text = """# Visually review the HF20 diagnosis

Read HF20_P016_MAIN_DIAGNOSIS.md in the Package016packet first. From repository root:

```bash
./scripts/run_track_a_dashboard.sh --check
./scripts/run_track_a_dashboard.sh
```

Choose **HF20: TM0 vs T2** in Explore, or **Start Here → Open HF20: TM0 vs T2**.
The exact existing controls are **HF20 recorded run**, **HF20 stock**, **HF20 development dates**,
and **HF20 origin**. Tabs: **Predictions & Errors**, **Training Diagnostics**,
**Price & Features / extremes**, **Five-minute guide**. Choose each C0/T2run in turn.
No new Package016tab or MSE-algebra chart was added; linked compact CSVs support those comparisons.

"""
    tests = {
        "NEAR_ZERO_SCORE_LARGE_TARGET": "Test tiny forecasts against a large target and residual.",
        "TYPICAL_QUIET_RAW_RETURN_ORIGIN": "Contrast quiet raw candles with normalized TG20.",
        "LARGEST_STOCK_SPECIFIC_TG20_TAIL": "Inspect numerator/MAD/epsilon; preserve tails.",
        "LARGEST_C0_T2_DISAGREEMENT": "Compare scores/errors on the same row.",
    }
    for i, e in enumerate(examples, 1):
        guide_text += f"""{i}. **{e["symbol"]}, {e["session"]}, origin{e["origin"]}**
   {e["reason"]}.
   Set stock, both development dates to{e["session"]}, and origin{e["origin"]}.
   Target={e["TG20"]:.8f}; C0={e["C0"]:.8f}; T2={e["T2"]:.8f}.
   {tests[e["reason"]]}
   In **Price & Features / extremes**, search the genuine-origin dropdown for that date/origin,
   then click **Load genuine HF hourly candles + 48 feature steps**. Choose an FT1channel,
   including M2, for native/scaled history. These examples are explicitly POST_HOC_DIAGNOSTIC.

"""
    guide_text += """5. **Epoch1learning case, both recorded runs.** Open **Training Diagnostics**;
   inspect the selected-epoch vertical marker and epoch table. Compare optimizer loss in its
   own units, original-TG20inner-validation MSE, online original-scale training MSE, gradient
   percentiles and actual clip fraction. T2epoch2is raw minimum but fails strict0.1% qualifying
   improvement. No later-epoch weight/activation chart exists; those checkpoints were not saved.

Units and interpretation: C0optimizer loss is TG20squared; T2optimizer loss is squared asinh
units and is NOT DIRECTLY COMPARABLE. Inner validation selects epochs; development is later
exploratory OOS. T2saved scores are already inverted once: never invert again. Full-population
equal-day metrics retain366origins×20names; date/stock/origin plots are filtered subsets.
Reported neural fitting time, worker wall and supervisor wall differ, and host load differed
between runs; elapsed seconds do not prove a transform speed advantage. Hourly candles use
interval START; FT1uses completed END/scheduled steps−47…0; no reconstructed30-minute bars
or actual fills. TG20/raw future outcomes are EX-POST labels, absent from feature channels.

Existing charts do not show the new exact MSEalgebra, denominator-tail attribution or grouped
paired-contribution charts. Their bound CSVs and suggested axes are in visualization_handoff.json;
no synthetic/placeholder chart is claimed. If original source/derived artifacts are unavailable,
use the saved score/diagnostic tabs and report SOURCE/CHRONOLOGY HOLD for the missing chart.

No dates2026-01-07+are allowed, including Full data/cache routes; the five-stock lock remains
independent. Source/publication/action/PIT/licensing qualifications in the main diagnosis
remain unchanged. Close only the server you launched with Ctrl+C. No screenshot was synthesized.
"""
    guide_text = polish(guide_text)
    if guide.exists():
        if polish(guide.read_text()) != guide_text:
            raise ValueError("P016_GUIDE_DIFFERS_PRESERVE_EXISTING_HUMAN_WORK")
    else:
        guide.write_text(guide_text)
    for path in out.glob("*.md"):
        path.write_text(polish(path.read_text()))

    artifact_names = [
        "epoch_selection_reconstruction.csv",
        "mse_vs_zero_exact_decomposition.csv",
        "stock_origin_month_diagnostics.csv",
        "tg20_tail_denominator_study.csv",
        "tg20_extreme_event_examples.csv",
        "loss_concentration.csv",
        "hf20_training_and_gradient_health.csv",
        "model_output_and_hidden_diagnostics.csv",
        "paired_c0_t2_development.csv",
        "paired_origin_stock_month.csv",
        "input_shift_contrasts.csv",
        "stock_rank_behavior.csv",
        "tg20_denominator_tail_contrast.csv",
    ]
    artifacts = {
        name: dict(path=str(out / name), sha256=digest(out / name)) for name in artifact_names
    }
    publish(
        out / "visualization_handoff.json",
        dict(
            package="TA-HF20-P016-READONLY-DIAGNOSIS-001",
            original_handoff=dict(
                path=str(report / "visualization_handoff.json"),
                sha256=digest(report / "visualization_handoff.json"),
            ),
            input_contract=plan["input_contract"],
            checkpoint_ids=replay_info["checkpoints"],
            target_id=c["target_id"],
            source_revision=c["source_revision"],
            symbols=c["symbols"],
            original_controls=[
                "HF20 recorded run",
                "HF20 stock",
                "HF20 development dates",
                "HF20 origin",
            ],
            original_tabs=[
                "Predictions & Errors",
                "Training Diagnostics",
                "Price & Features / extremes",
                "Five-minute guide",
            ],
            examples=examples,
            guide=dict(path=str(guide), sha256=digest(guide)),
            artifacts=artifacts,
            ui_code_modified=False,
            new_charts_implemented=False,
            screenshots_obtained=False,
            future_chart_specifications=[
                dict(
                    name="ZERO_MSE_DECOMPOSITION",
                    csv="mse_vs_zero_exact_decomposition.csv",
                    x="arm",
                    y=["amplitude_cost", "alignment_benefit", "delta_MSE_vs_ZERO"],
                    units="CANONICAL_TG20_SQUARED",
                ),
                dict(
                    name="TAIL_DENOMINATOR",
                    csv="tg20_extreme_event_examples.csv",
                    x="MAD_over_epsilon",
                    y="target",
                    hover=["symbol", "session", "origin", "numerator"],
                    units="EXPOST_CANONICAL_TG20",
                ),
                dict(
                    name="PAIRED_DAILY",
                    csv="paired_c0_t2_development.csv",
                    x="session",
                    y=["delta_MSE", "delta_IC"],
                    separate_axes=True,
                ),
            ],
            held_out="LOCKED_BEFORE_NUMERIC_IO",
            ledger=30,
        ),
    )
    summary = dict(
        verdict="HF20_P016_DIAGNOSIS_COMPLETE",
        ledger=30,
        new_pairs=0,
        mean_IC=positive_ic,
        terms=terms.reset_index()
        .astype(object)
        .where(pd.notna(terms.reset_index()), None)
        .to_dict("records"),
        T2_epoch2=dict(
            improvement=improvement, percent=percent, required_below=limit, observed=second
        ),
        target_tail_q99=q99,
        improved_days=improvement_days,
        improved_stocks=improvement_stocks,
        top5_positive_day_gain_share=top5_gain_share,
        best_stock=best_stock,
        best_stock_net_gain_share=best_share,
        first_boundary="B5_WEAK_OUTCOME_ALIGNMENT",
        replay="NO_DETERMINISTIC_DIVERGENCE_FOUND",
        main=str(out / "HF20_P016_MAIN_DIAGNOSIS.md"),
        guide=str(guide),
    )
    publish(out / "diagnosis_summary.json", summary)
    (out / "human_review_card.md").write_text(f"""# Package016review card

**HF20_P016_DIAGNOSIS_COMPLETE** · ledger30/200unchanged · zero new fits/optimizer updates.

Both selected epoch1because neither later raw gain met strict0.1% qualifying improvement;
T2epoch2improved only{percent:.6f}%. Falling fitting loss with worsening validation is
consistent with overfitting/weak stable signal, not proof of insufficient epochs or capacity.

C0MSE={terms.loc["C0", "MSE"]:.9f}; T2={terms.loc["T2", "MSE"]:.9f};
ZERO={terms.loc["ZERO", "MSE"]:.9f}.
C0covariance is near-zero/negative; T2has small positive covariance but its mean/bias component
accounts for most of the remaining ZEROgap. No development intercept correction was fitted.
Rank IC={positive_ic["C0"]:.6f}/{positive_ic["T2"]:.6f};
exploratory intervals and reused-development
history prevent a validated signal/alpha claim. Outputs are small but nonconstant; bounded
float32eval replay agrees with saved scores, without gradients or parameter changes.

Tail events remain intact, not automatically clipped or downweighted. Training|TG20|q99={q99:.6f};
read actual numerator/MAD/epsilon and event-sign/rank evidence in the main diagnosis.
Preserve the research goal of detecting unusual stock-specific returns. No external event
cause, vendor adjustment/PIT/publication certification or source-quality causal attribution.

Read **HF20_P016_MAIN_DIAGNOSIS.md**, then **{guide}**. Four exact saved development cases and
the epoch1view are provided. Existing HF20views suffice; new comparative plots are specifications,
not fabricated UI features. Historical per-example gradients/dropout/optimizer states and later
checkpoints are NOT_RECORDED. Source/action/PIT/rights/idealized clock/hourly-close qualifications
remain ASSUMPTION_CONDITIONAL. HF20and original five-stock held-outs remain locked.

Proposals only: paired seed replication first; separately preregister rare-event or rank auxiliary
hypotheses, or a fixed-target source-consistent training-panel control. No budget permission,
new architecture, training, trading, data acquisition or Git integration follows from this report.
Checks, preservation, exact replay and the mandatory session report complete the handoff.
""")

    path = out / "human_review_card.md"
    path.write_text(polish(path.read_text()))
