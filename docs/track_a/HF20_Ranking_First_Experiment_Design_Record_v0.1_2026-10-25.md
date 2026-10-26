# HF20 ranking-first experiment design record

**Version:** 0.1 — approved research direction and proposed implementation defaults  
**Date:** 25 October 2026  
**Status:** **DESIGN / SCIENTIFIC FREEZE PENDING. NO FITTING AUTHORITY.**  
**Research ledger:** 62/200 historical starts; no new reservation or expenditure  
**Protected confirmation:** 2026 numerical inputs, outcomes, and trading data remain unopened  
**Scope:** Existing 20-stock HF1M-LONG panel. This document selects no new stock and creates no labels, folds, model, source, trading execution, or tests.

## 0. Authority and governing evidence

The user has selected **six directional defaults** for the next experiment protocol. They are adopted as *design decisions*, not permission to train. Additional numbers, eligibility rules, mathematical implementation details, and exact calendar cutoffs below are **recommended defaults awaiting preflight verification and specific approval**. Do not treat this document as a Codex execution prompt.

**Primary records:**

- `docs/track_a/brainstorm/HF20_LSTM_Comprehensive_Review_and_Expansion_Plan_2026-10-24.md`, particularly §§2–3, 5.3–5.10, 8, 11–12.
- `docs/track_a/brainstorm/HF20_Focused_Second_Pass_Ranking_Inputs_Minute_Data_and_Horizons_2026-10-24.md`, particularly §§2–3, 10–14.
- The 25 October 2026 HF20 read-only diagnostic dossier, especially `05_RANKING_FIRST_CONTRACT_PROPOSED.md`, `06_existing_baselines_and_evidence.md`, `08_HF20_RANKING_DIAGNOSTIC_DECISION_RECORD.md`, and `09_DIAGNOSTIC_CONTRACT_AND_COVERAGE.md`. These are reported repository-local artifacts; their full contents have not all been independently inspected here. The supplied coverage record reports several justified **QUALIFIED**, **BLOCKED**, and **NOT_APPLICABLE** statuses.
- Existing P020 source/FT16/TG20 contract, P021 T2 comparator, P022 R1, and P028 mechanism/tail/gradient records. New folds must not silently inherit obsolete five-stock settings.

### Six approved *directional* defaults

1. Cross-sectional ranking is the **primary near-term scientific objective**. Net trading profitability is the ultimate long-run goal but portfolio optimization and trading P&L are deferred.
2. Retain the current **four-hour TG20 ordering** as the first reference task, without claiming the existing price-only outcome is post-issuance executable.
3. Use **four annual historical walk-forward outer evaluation periods: 2021, 2022, 2023, 2024**.
4. Establish **non-LSTM ranking baselines** before fitting new neural ranking objectives.
5. Compare **normalized-rank regression** and **pure pairwise logistic ranking** in a shared LSTM, without treating previous R1 (auxiliary rank loss) as this test.
6. Preserve the **protected 2026 confirmation lock**.

No additional architecture, input channel, horizon, stock selection, hyperparameter tuning, full 2025 exploratory reuse, or live training is authorized.

## 1. Precisely stated prediction task

At each existing admissible forecast origin \(t\), forecast a real-valued score \(s_{i,t}\) for each of the original 20 stocks, with larger scores indicating greater subsequent performance over the same **existing four-hour, price-only** interval. Preserve the 48 scheduled hourly input steps and exact 16 FT16 features, source clocks, stock order, source quality, target eligibility, corporate-action conventions, and old two-origin schedule until a separately versioned change is approved.

The frozen prior task is

\[
R_{i,t}^{(4)}=\log(P_{i,e(t)}/P_{i,b(t)}),\quad
Y_{i,t}=\frac{R_{i,t}^{(4)}-\operatorname{median}_j R_{j,t}^{(4)}}{\operatorname{MAD}_j(R_{j,t}^{(4)})+\epsilon_{\mathrm{fit}}}.
\]

All 20 names share the same origin-specific median and positive denominator; hence

\[
\operatorname{rank}_i R_{i,t}^{(4)}=\operatorname{rank}_i Y_{i,t}
=\operatorname{rank}_i \operatorname{asinh}(Y_{i,t}/s_{\mathrm{fit}}).
\]

This is an **ordering identity**, not equivalence of regression losses. It permits deriving ranking labels without fitting any inverse-asinh expected-return correction. For *ranking-only* models, scores are not in return units and must **not** be passed through `sinh` or reported with a fictitious original-TG20 MSE.

**Critical historical timing qualification:** Current TG20 outcome starts at the feature-end reference, while forecast issuance is modeled two minutes later. Keep the old metric as an historical forecasting comparator; do not call it an executable forward return. The read-only clock audit did not independently certify vendor `available_at`/corporate-action vintage. If a later post-issuance target is desirable, create a distinct proposal and re-audit labels/horizons/embargo first.

## 2. Proposed mathematical losses and primary metric

### 2.1 Normalized-rank regression (first neural candidate)

For ascending realized within-origin midranks \(r_{i,t}\) and \(N_t=20\), define

\[
q_{i,t}=2\frac{r_{i,t}-1}{N_t-1}-1,
\quad L_{\mathrm{NR},t}=\frac{1}{N_t}\sum_i(s_{i,t}-q_{i,t})^2.
\]

This bounded *label* is a proxy for conditional expected ranks; model outputs/gradients are not automatically bounded. Preserve ties using a predeclared average/midrank convention, not random perturbations. This objective is different from original-return/T2 regression.

### 2.2 Pure pairwise logistic ranking (second neural candidate)

For each unordered pair with distinct future returns let \(d_{ij,t}=\operatorname{sign}(R_{i,t}^{(4)}-R_{j,t}^{(4)})\):

\[
L_{\mathrm{PW},t}=\frac1{|\mathcal P_t|}\sum_{(i,j)\in\mathcal P_t}
\log\!\left(1+\exp\left[-d_{ij,t}\frac{s_{i,t}-s_{j,t}}{\tau}\right]\right).
\]

**Proposed simple default:** \(\tau=1\), fixed before training. Each of 190 unordered pairs for a full 20-stock origin counts once, and the mean is normalized by actual valid-pair count; those pairs are **not** independent time samples. No raw-return magnitude weighting, artificial dead-zone, auxiliary asinh loss, or tunable pair-selection grid in the initial comparison. If ties exist, specify exclusion and coverage accounting. Require stable `softplus` numerics.

### 2.3 Identical statistical weighting for all candidates

Preserve the current hierarchical weighting: equal valid stocks/pairs inside origin, equal origins within each session, equal sessions within the applicable phase. Record every valid origin and pair count. Do not let a model with more pair examples or unequal sessions silently change the research objective.

### 2.4 Primary evaluation

At origin \(t\), compute within-origin **Spearman rank IC** between predicted scores and the existing future-return ranks. Average IC across admissible origins within each session, then across eligible sessions within each outer year. **Overall primary summary:** arithmetic mean of the four annual mean IC values (equal outer-year weighting), with all four years separately displayed. This is a recommended default, not a claim of sampling independence.

Report undefined IC when a score vector is constant or all realized outcomes tie; no random tie breaking or fabricated zero correlations. Predeclare whether undefined origins cause a gate failure or are excluded with explicit counts. **Recommended:** include undefined incidence as a hard diagnostic and report the IC average over defined origins, with a minimum-coverage gate frozen *before* fitting.

**Secondary diagnostics:** pairwise concordance, normalized-rank MSE where comparable, top/bottom-four retrieval, predicted-score margin/tie frequency, within-origin dispersion, stock/month/origin-slot/source-quality conditional results, directional extremes, and chronological uncertainty. Do not equate high IC with a profitable strategy. No full P&L in this phase.

## 3. Four annual walk-forward evaluation periods — proposed timing

| Outer fold | Evaluation sessions | Training history available before evaluation | Proposed inner validation segment |
|---|---|---|---|
| F21 | Calendar 2021 exchange sessions | Historical eligible observations up to end-2020, excluding unmatured labels | Roughly July–December 2020 |
| F22 | Calendar 2022 exchange sessions | Historical eligible observations up to end-2021, excluding unmatured labels | Roughly July–December 2021 |
| F23 | Calendar 2023 exchange sessions | Historical eligible observations up to end-2022, excluding unmatured labels | Roughly July–December 2022 |
| F24 | Calendar 2024 exchange sessions | Historical eligible observations up to end-2023, excluding unmatured labels | Roughly July–December 2023 |

- Each outer year is **genuinely out of sample for its own newly fitted models**. Later-fold training may legitimately include earlier evaluated years, but not future outcomes relative to its own cutoff.
- **Recommended approach:** inner fitting prefix; an approximately last-six-calendar-month chronological inner validation tail with applicable purge; choose training duration/regularization using that tail; then **fresh refit** on the entire outer-fold-eligible historical prefix, using new preprocessing fitted only to that prefix. No outer-year outcomes may affect scaling, model choice, or epoch selection for that fold.
- The exact first/last origin, label-maturity cutoff, validation start, 48-scheduled-step separation where contractually required, daylight/holiday handling, and permitted warm-up coverage must be **computed from canonical source indices** and human-reviewed. Do not implement the rough calendar dates as hardcoded UTC boundaries.
- Reuse the **existing two original forecast origins** and four-hour label eligibility within each outer year; report years/origins not admitted without future-based repairs. Do not assume the original P020 2023–2025 validation assignment can itself serve as any of these four folds.
- These historical outer periods are retrospective walk-forward **research evidence**, not pristine untouched confirmation: the strategy of evaluating these years was selected after other HF20 research. Preserve this interpretation.
- Keep July–December 2025 repeatedly inspected development distinct and out of the first four annual test folds. Keep all 2026 numerical records protected.

**Blocking principle:** **The saved T2/42 model trained/refitted through mid-2025 is NOT an out-of-sample comparator for 2021–2024.** To claim same-fold superiority over T2, an authorized, independently trained **fold-specific T2** control is necessary (or a truly timestamp-compatible archived predecessor if one exists and is verified). The historic T2 numbers may appear only as labeled context.

## 4. Baseline-first experiment ladder (not yet authorized)

**Gate B0 — no fitting:** Verify all dossier reports, inspect the actual `05_RANKING_FIRST_CONTRACT_PROPOSED.md`, calculate exact fold calendars/source admissibility, identify legitimate saved earlier-cutoff predictions, prove 48×16 information equality, identify source-clock caveats, and publish complete anticipated resource/start count. Inspect the P020 feature recipe, do not make up a new one.

**Gate B1 — strong non-neural baselines, separately authorized:**

1. **No-fit controls:** predeclared momentary momentum and reversal ranks from already available FT16 causal values; historical/static stock-profile comparator only if trained/fitted properly on earlier permitted history. Constant ZERO ranking has **undefined Spearman**, so is an MSE/context baseline, not an IC=0 comparator.
2. **Primary linear control:** regularized pooled linear regression on realized *normalized ranks* using all 48×16 historical FT16 values, flattened deterministically in stock/history-feature order (768 inputs per stock). Fit scaling inside each permitted fold and match the LSTM's full lookback. If computationally useful, a *separate* sparse-lag control is allowed only as a clearly **information-reduced** comparison, not a matched alternative.
3. **Optional finite linear pairwise comparator:** same 48×16 stock inputs and pairwise logistic loss. It isolates direct ranking-likelihood improvement from recurrence, provided its regularization/validation is separately specified.
4. **Hyperparameters:** one small, prespecified regularization search within **inner validation only**; provisional default \(\lambda\in\{10^{-4},10^{-3},10^{-2},10^{-1},1,10\}\) expressed for **normalized weighted-mean objective**, carefully translated to any library implementation. Choose by declared ranking validation criterion, not best outer-year IC. No dozens of model families or per-year hand retuning.

**Gate B2 — shared LSTM comparisons, separately authorized only after B1 review:**

- Keep baseline one-layer hidden-32 LSTM, 48 FT16 steps, shared stockwise weights, 10% final readout dropout, existing optimizer/decay/clipping/whole-session batching unless a specific objective needs an explicitly frozen compatible change.
- Candidate **NR-LSTM** uses \(L_{\mathrm{NR}}\); candidate **PW-LSTM** uses \(L_{\mathrm{PW}}\). Do not combine objectives in the initial screen, retrain A7/A12, add peer channels, change source, or introduce minute inputs here.
- **Recommended default for checkpointing** (requires source/code feasibility and human signoff): evaluate dropout-OFF validation **daily Rank IC** each epoch; min 12, max 60, patience 10; strict positive *absolute* qualification increase of 0.001 IC (rather than multiply by 0.999, which fails at zero/negative IC). Track the actual raw best separately and publish qualification/censoring behavior. Then freshly initialize/refit for selected count. Verify that 0.001 is treated as a *proposed threshold*, not backfit using 2021–2024 test outcomes. No automatic rescue if it behaves poorly.
- **Seed policy:** first screen predeclared seed 42 for matched arms; seek seed 123 replication **only** if warranted by a separately approved stability gate. Seed 123 is not a permission already granted; there must be no best-seed selection.
- **Comparator:** fold-matched T2 using the same input information, training cutoffs, and evaluation years; its different loss remains a substantive treatment difference. Preserve saved full-history T2/42 only as archival context.
- **Budget:** four folds × each separately authorized fitted neural model × seeds will incur multiple independently counted research starts. No fit begins until exact journal charging, CPU/RSS/disk/time estimate, gating, failed-start rule, and implementation hashes are approved. Ledger stays 62/200 until then.

**Gate B3 — scientific analysis:** frozen primary metric across all four years; per-fold differences and uncertainty; no result-based switching of favored years, alternative endpoints, or optimized score thresholds. A positive finding must generalize beyond one year/stock or a handful of extremes and must beat transparent same-information controls.

## 5. Required source and numerical safeguards

- **Source:** Only existing immutable, pinned HF20 historical minute→hour input lineage and frozen P020 FT16/TG20, unless another source is explicitly authorized. No new ticker, independent market series, extra current/future quality flags, or newly learned scaler.
- **Chronology:** Every input available no later than its modeled information cutoff; outcomes mature after their true endpoints, and embargo/purge respects the full permissible input and target reach. First/final sessions and origin counts must be independently reconciled for each fold.
- **Cross-section:** Original 20-stock, fixed-order population. Do not redefine membership or silently relax complete-panel eligibility to create fold support. Disclose survivor conditioning and inherited corporate-action/source-publication assumptions.
- **Exactness:** Reconcile raw future returns → origin median and MAD → TG20 → realized rank; reconcile proposed point/pair losses against independent oracles and session weights; deterministic tie handling; synthetic planted-rank recovery and swapped-stock-coordinate invariance/null tests; checkpoint identities, optimizer updates, gradient connectivity, calibration/refit isolation, deterministic replay.
- **Data integrity:** No raw panel duplication per seed/fold. Immutable prior experiment outputs/checkpoints/hashes and protected-rejection-before-I/O tests remain. Preserve failures and all attempted starts, no silent retries.

## 6. Mandatory evidence for any *later authorized* fit

Inherit **all** HF20 comprehensive review §12 and focused second pass §13 diagnostics, adapted to score units:

- all permitted training, validation, refit and genuinely OOS outer-fold roles, with phase/provenance and exact denominators;
- target original return/TG20 rank and original numerator/median/MAD/epsilon, stable top-1%/5% original-target cohorts, extreme-error cohorts, training-frozen thresholds, positive/negative extremes, numerator-only/MAD-only/both/neither and source-quality strata;
- actual optimized rank-regression or pairwise loss and cohort allocations; for pairwise objective allocate one-half each pair contribution to each endpoint with independent conservation check; **no fictitious original-return squared error from raw rank scores**;
- rank IC, pairwise concordance, retrieval, score ties and gaps, per-origin/session/year contributions, chronological stability and uncertainty preserving entire dependent stock cross-sections;
- finite gradients, pre/post clipping/update norms, true optimizer step counts, hyperparameter-selection trace, raw/qualified extrema, fresh refit identities, 22 authentic deterministic bounded source cases per authorized arm where feasible, and explicit numerical proof of every gate;
- source vintage/rights qualifications, all failed/inactive records, machine-readable tables, readable narrative, and read-only visual inspection surfaces if justified.

Do not pool outcomes from fitting/selection years as independent OOS evidence. A bootstrap over dependent rows or many pairs is invalid as independent-year inference. Four outer years are useful but not automatically enough for a definitive economic claim.

## 7. Decisions still requiring technical preflight / human scientific freeze

| Open item | Recommended default | Requirement before authorization |
|---|---|---|
| Exact annual boundaries, matured label cutoffs and eligible counts | 2021/22/23/24 official exchange sessions | Calculate from canonical indexes; include warm-up, 48-step embargo and holidays |
| Inner validation and refit | Last six calendar months of each historical prefix | Freeze precise boundary and purge, and refit leakage exclusion |
| Prediction timing | Keep historical TG20 four-hour price-only first | Explicitly label it non-executable; independently propose future post-issuance experiment later |
| Undefined IC / realized ties | Average midranks; report undefined rate and a coverage floor | Define minimum defined origins per day/year and exclusion rule before runs |
| Pairwise \(\tau\) | Fixed 1.0 | Test numeric conditioning on synthetic data only; no outer-year tuning |
| Linear penalty grid | Six stated values | Verify weighted-mean loss convention; normalize penalty for actual library |
| Checkpoint selector | Daily Rank IC, 0.001 absolute qualification, 12–60 epochs, patience 10 | Check calibration feasibility and compare with existing D6g semantics, not selection on development |
| First seed and comparator | Matched seed 42; fold-specific T2 | Count all four-fold starts explicitly, inspect whether truly equivalent older-cutoff T2 exists |
| Fit capacity, storage, training budget | Small staged approval groups B1 then B2 | Benchmark expected time/memory before live authorization |
| Data source publication/action clocks | Existing assumptions condition historical study | Do not promote to executable or fully point-in-time claims without certification |
| 2025/2026 use | 2025 old development contextual only; 2026 protected | Hard pre-I/O tests and separate future authorization |

## 8. Proposed next deliverable and authorization boundary

**Next deliverable (design-only):** Codex or a researcher should inspect the repo's current `05_RANKING_FIRST_CONTRACT_PROPOSED.md`, dossier reports 01/06/08/09, and canonical P020 manifests; return an exact four-fold eligibility/calendar card, causal/tie/IC selection specifications, matched-baseline definitions, preflight tests, and a complete *proposed* fit ledger/resource estimate. It must stop for **human review before any fitting**.

**Explicitly not authorized:** fitting linear or neural models; labels or new-source construction; inference/prediction generation; loading protected 2026 numerical data; opening trading/P&L runs; new horizons/minute input models; installing packages; changing the research ledger; retraining or promoting A1–A12; choosing/expanding stocks.

**Future research candidates retained but outside this initial comparison:** rolling-window versus expanding-window fitting; more intraday forecast origins and alternative horizons; minute-informed hourly inputs; overnight/multiday outcomes; causal age/quality information; magnitude/quantile/event branches; A4 and A7/A12 follow-up; A9–A11 untested. No immediate full factorial design.

### Final decision

The six user-selected defaults constitute a coherent **ranking-first scientific direction**, and a four-year walk-forward design is the correct next evaluation proposal. The numerical training contract, exact fold calendars and controls are **not yet frozen**. The full research ledger remains **62/200**, and all optimizer/model fitting remains **closed**.
