# HF20 S9-MAG — Stage 1 Research Menu: Calibration and Prediction Objectives

**Version:** Draft v0.1, 27 October 2026  
**Status:** Research-design menu for discussion; **no fitting, backtesting, data downloads, source modifications, protected-period access, or additional experiments are authorized by this document.**  
**Scope:** Improve the existing magnitude-forecasting LSTM's *statistical forecasts*. A separate later stage will examine market-implied movement, options trading, portfolio weights, and execution.  
**Primary references:**

1. `HF20_S9_MAG_Methodological_Replication_and_Options_Research_Handoff_v2_2026-10-27.md` (especially §§3–8, 10–12 and Annexes A–B): executed MAG target, model, controls, folds, results, calibration caveats.
2. `HF20_Complete_Experiment_Consolidation_and_Novel_Architecture_Handoff_v3_2026-10-27.md` (especially §§1–3 and 5–7): full experimental inventory, scientific limitations and binding economy/protection rules.

This is a **menu of independent hypotheses**, not an instruction to run every item. Numbers describing prior work are *reported archival results*, not independently reproduced in this planning document. Proposals below are new unless explicitly identified as completed work.

---

## 1. Why Stage 1 is worth doing

The completed S9-MAG model forecasts the magnitude of a genuine project-defined four-*trading*-hour **endpoint** log return:

\[
R_{i,t}^{(4)}=\log\frac{P_{i,e(t)}}{P_{i,t}},\qquad
A_{i,t}=|R_{i,t}^{(4)}|\geq 0.
\]

It trains on a *transformed* magnitude, using a positive fold/fit-phase scale `s`:

\[
M_{i,t}=\log(1+A_{i,t}/s),\quad
\widehat M_{i,t}=f_\theta(X_{i,t}),\quad
\widehat A_{i,t}^{\rm old}=s\,\operatorname{expm1}\!\left(\max\{\widehat M_{i,t},0\}\right).
\]

The optimized loss is squared error in **M**, not squared error in raw **A**. The lower clamp happens **only when decoding**, not during training. The existing model is a shared one-layer LSTM, `48 × 16` FT16 own-stock inputs, hidden width 32, dropout 0.10 on the final hidden representation, scalar linear readout, 6,433 parameters, AdamW and session/origin/stock-weighted loss.

### Reported baseline facts (2021–2024 exploratory walk-forward)

| Measure | Archived S9-MAG outcome | Interpretation |
|---|---:|---|
| Mean transformed-MSE | **0.232454** | Against `STOCK` 0.269383 and `VOL` 0.268266 |
| Transformed-MSE reduction | **13.7%** vs `STOCK`; **13.3%** vs `VOL` | Favorable in each of the four annual folds; exploratory, not untouched confirmation |
| Raw absolute-log-return MAE | **0.006505** | `STOCK` 0.006903; `VOL` 0.006992; neither control was trained specifically to minimize raw MAE |
| Mean decoded forecast / mean observed | **0.00836 / 0.01031** | Average underprediction of **0.00195 log-return units** (about 0.195 percentage points for small moves) |
| Reported magnitude rank association | **0.408** | Exact estimator/aggregation must be read from saved metrics before using as a promotion rule |
| Tail failures | Some large moves underpredicted | Largest genuine movements matter disproportionately for downstream options decisions |

These results are **broadly encouraging but not a demonstrated profitable strategy**. Four years have already been revisited across HF20 model decisions. S9-MAG's three-class EVENT and signed TG20 QUANTILE companions **did not outperform their stock-specific proper-score controls**. The older A7/A12 slight original-return-MSE gains involved a **different signed task**; they are not established MAG refinements.

### Central statistical distinction

Under ideal squared-error estimation,

\[
\widehat M(X)\approx \mathbb E[M\mid X].
\]

But the conditional expected *raw* absolute movement is

\[
\mu_A(X)=\mathbb E[A\mid X]
=s\{\mathbb E[\exp(M)\mid X]-1\}
\geq s\,\operatorname{expm1}(\mathbb E[M\mid X]),
\]

where the inequality is Jensen's. This establishes a possible *retransformation gap* for an ideal transformed conditional-mean model. It does **not** establish that Jensen bias explains the observed full underprediction: misspecification, optimization, nonstationarity, the decode clamp and distribution shifts can contribute too.

**The first strategic decision is which statistical object we need:**

- **Expected absolute movement:** `E[A | X]`; relevant to some risk limits and a first-order, imperfect option-payoff comparison. Evaluate with **raw A squared error and calibration**.
- **Typical/median absolute movement:** `median(A | X)`; evaluate with **raw A absolute error**. An estimate of this is not interchangeable with a mean.
- **Upper movement quantiles or tail probabilities:** e.g. `Q_0.90(A | X)` or `P(A > a | X)`; evaluate with **pinball loss, coverage, Brier/log loss**. Useful when large movements dominate decisions.
- **Full conditional movement distribution:** can produce all the preceding summaries but is harder to estimate reliably. Score with proper distributional scores and calibration.

Improved return-*magnitude ranking* remains an important **secondary diagnostic** in Stage 1, but training expressly for ranks and comparing magnitude to option-implied movement belong to later research stages unless separately approved.

---

## 2. Non-negotiable comparison and data contract

Before selecting new models, keep the following reference fixed:

1. **Population:** existing 20 named HF20 stocks, original tensor axis, frozen source/FT16 feature recipes and `48 × 16` windows. The data come from the pinned minute-derived hourly equity source. The later S5 clock channels are **not** already in MAG.
2. **Horizon and timing:** retain the original seven S4/S9 origin types (09:30, 10:30, 11:30, 12:30, 13:30, 14:30, 15:30 ET) and **four trading-hour endpoints**, including the defined overnight-crossing cases. Forecast issuance is modeled about **two minutes after the starting price proxy**; this is **price-only predictive evidence, not executable post-signal P&L**. Do not silently shift endpoints or entry times.
3. **Fold identities:** F21/F22/F23/F24 annual expanding-prefix walk-forward with original source-backed eligible OOS keys, purges, 48-completed-step input embargo, label maturity, fold-specific feature recipes and `s`. The reported matched population is **4,013 origins / 793 sessions / 80,260 stock-origin rows**. The actual repository indices are authoritative.
4. **Loss weighting:** equal stocks within origin, equal origins within session, equal sessions within role, then equal **year** weighting for the four-year summary. Paired comparisons use identical score keys.
5. **Historical reference:** existing seed-42 MAG checkpoints and saved predictions are immutable. The original task uses a task-specific inner-validation epoch selector followed by a **fresh** full-prefix refit; do not reuse a signed-rank stopping rule or scale.
6. **Protection:** 2021–2024 is repeatedly examined **exploratory** OOS, not a fresh confirmatory test; do not use 2025 opportunistically as a newly invented tuning fold. **2026 is protected**; no numerical observations, labels, predictions, hashes or incidental reads without separate authorization.
7. **Engineering:** reuse source, fold manifests, scoring, and plotting. No dashboard overhaul, duplicate bulk data, giant audit infrastructure, per-batch parameter/gradient archives, or automatic training sweeps. Only correctness-critical timing/target/weighting, no-leakage and model-reload checks.

**Crucial calibration-fit rule.** Fitting a calibrator is *supervised learning*, even when the LSTM weights are frozen. A calibrator trained on the same 2021–2024 OOS outcomes on which we report its improvement gives an in-sample or post-selection result, not fresh OOS evidence. The calibrator needs past-only targets and **honest forecasts** from a model that did not fit those targets. See §5 for feasible chronological arrangements.

---

## 3. Detailed experiment menu

Each entry separates **hypothesis**, **minimum experiment**, **comparator**, **success/failure diagnosis**, and **status**. Priorities are **initial recommendations**, not final approval. A low-compute diagnostic should precede extra four-fold LSTM fitting.

### D0 — Reconstruct forecast bias and identify *where* calibration fails

**Priority: mandatory diagnostic, zero neural starts.**

**Hypothesis:** Most of the apparent failure may be concentrated in particular forecast levels, stocks, calendar/origin classes or extreme outcomes; we should not redesign the loss before locating it.

**Read-only analyses:**

- Reproduce the original mean forecast, mean realized magnitude, transformed-MSE, raw MAE, and MAG-versus-`STOCK`/`VOL` paired differences using saved **actual eligible keys and weights**; inspect that decoding uses the correct per-fold **refit** scale.
- Form forecast bins/deciles *descriptively*; plot or tabulate `mean(A)` against `mean(Â)` and a calibration ratio, with count/session information. Estimate mean error, slope/intercept and conditional bias by stock, year, origin slot, **intraday vs overnight-crossing**, causal historical volatility state and previously archived source-quality strata.
- Examine large-movement cohorts: training-prefix 90th/95th percentiles of `A`, top 1%/5% of **errors**, false low forecasts on large events, and the frequency of predicted-versus-realized order inversions in the top magnitude tail. Distinguish outcome-tail loss from residual-tail loss.
- Check whether errors mostly reflect a global level offset, a low-to-high forecast-scale slope, unstable year-specific bias, stock identity, time-of-day, or truly missing dynamic information.
- Inspect transformed-model bias versus decoded raw-magnitude bias; report how much of the error can plausibly be due to Jensen retransformation and how much remains unexplained.

**Output:** one compact bias-and-baselines table, several targeted plots or existing-dashboard references, and an explicit decision on which calibration defect is largest. **No training, no new source read, no fitted OOS calibration.**

**Stop/deprioritize:** if no stable calibration pattern is visible outside a tiny tail cohort, avoid fitting elaborate segment-specific maps merely to chase that cohort.

### B0 — Strengthen *same-task* non-neural baselines before promoting new LSTM improvements

**Priority: high; cheapest fit(s) before further neural candidates.**

The archived `STOCK` control is a per-stock **transformed-mean constant**; `VOL` is a **parameter-free decoder of FT16 V2**, the floored hourly open-to-close RMS60, with a fixed normal-absolute-move multiplier. Neither is a fitted conditional expected-magnitude model, and neither is raw-MAE-optimal.

**Candidate simple controls (add only those needed for the chosen criterion):**

1. **Stock raw-MSE constant:** prefix-weighted per-stock `mean(A)`; for raw-MSE comparisons.
2. **Stock raw-MAE constant:** prefix-weighted per-stock `median(A)`; for raw-MAE comparisons.
3. **Stock × origin-clock or stock × intraday/overnight constant:** use **shrunk** historical group means/medians, since sparse cells are noisy; the group definitions are known at the forecast origin.
4. **Calibrated trailing-volatility magnitude:** a small train-prefix fit of future `A` on lagged historic volatility, origin and perhaps stock; this is stronger than the existing unfitted `VOL` scale formula.
5. **Small conditional magnitude regressor** on already available lagged FT16 volatility/range/activity and clock features (e.g., regularized linear or limited nonlinear fit); represents useful competition with a recurrent model, without creating another architecture campaign.
6. **EWMA/HAR-style realized-risk proxy:** if appropriate causal historical variation is available from the frozen minute source, build the smallest prespecified comparison consistent with the exact four-trading-hour endpoint. This is a **new fitted competitor**, not something already evaluated in MAG.

**Test question:** Is the extra MAG skill genuinely sequence-/feature-dependent beyond good stock, clock and volatility statistics? For each proper score use a comparator trained for that *same statistical functional* and the same permitted data, not a convenient baseline optimized for a different loss.

**Stop:** if a baseline matches MAG within paired time-block uncertainty and is similarly calibrated, prefer that baseline for further model complexity tests; keep the MAG result in the archive unchanged.

### C1 — A small, mathematically motivated **retransformation correction**

**Priority: first actual calibration candidate; usually no additional neural starts.**

A direct correction for the transformed-to-raw mean mismatch is a residual **smearing factor**. If `e = M - \hat M`, then

\[
E[A\mid X]=s\left(e^{\hat M(X)}E[e^e\mid X]-1\right).
\]

The equality is algebraic given that definition of `e`; the usefulness of a *fitted* `E[e^e | X]` depends on the quality of `\hat M` and residual estimation.

**Minimum nested tests:**

- **C1a (global):** one earlier-only residual-smearing factor `c = weighted_mean(exp(M-\hat M))`; decode `Â=s·max(0, exp(\hat M)c−1)`. Compare against the original clamped inverse and a simple positive constant correction.
- **C1b (heteroskedastic):** if residual variance clearly changes with the forecast, estimate `c(\hat M)` with a very small number of earlier-fitted bins or constrained smooth map; evaluate whether the added flexibility is justified.
- **C1c (parametric approximation):** if approximately normal residuals in M-space are empirically plausible, use `c\approx exp(\widehat\sigma_e^2/2)` (or a conditional version) as a transparent comparator, **not** as an assumed truth.

**Controls:** historical inverse, raw-mean `STOCK` baseline, same-information raw-volatility control. **Evaluate:** raw-MSE, conditional mean bias, top-decile errors, MAG magnitude ordering and transformed-MSE (the transformed prediction itself should remain unchanged). A common monotone decoder should typically preserve across-stock ranking; stock/condition-specific corrections may change it.

**Potential failure:** residual exponential moments are unstable because a few huge moves dominate `exp(e)`; controls should use prespecified numerical safeguards and report their effect, not silently erase genuine tail observations.

### C2 — Supervised monotone calibration of the existing scalar MAG output

**Priority: high; no new neural encoder needed, but requires a genuinely chronological calibration sample.**

**Question:** Can a simple fitted map `g(\hat M)` correct the magnitude level and slope better than the analytical C1 correction?

**Candidate fits (in increasing flexibility):**

1. **Positive affine raw-scale map:** `Â=max(0,a+b·Â_old)` with `b≥0`, fitted to raw `A` under weighted squared error. May also fit an intercept on M-space, but don't confuse M-space fit with raw-mean calibration.
2. **Positive multiplicative map:** `Â=c·Â_old`, `c≥0`; robust one-parameter reference.
3. **Constrained monotone piecewise-linear or low-knot spline:** modest curvature without changing the order of predictions within a group.
4. **Isotonic regression:** flexible monotone fit **only when** the chronological calibration sample has enough distinct scores and stable coverage; compare complexity and flat-step/tie frequency against (1)–(3).

**Fairness:** give the same calibration opportunity to applicable simple controls. Refit and choose the map **on past-only honest predicted–realized pairs**, never on the target research OOS period being scored as new evidence.

**Diagnostics:** reliability by prediction decile/stock/year, raw-MSE improvement, slope/bias persistence, forecast range, calibration-map extrapolation beyond the earlier sample. Isotonic staircases can introduce ties in magnitude ranking; count them.

**Promotion:** a stable gain over the one-parameter/simple correction *across years and predeclared cohorts*, not a large in-sample fit improvement.

### C3 — Context-aware **partial-pooling** calibration (only if D0 supports it)

**Priority: conditional, not a default grid.**

There may be a genuine distinction between morning same-session moves, overnight-crossing moves and high-volatility moves. A **single universal map** could be systematically wrong for one class.

**Smallest meaningful method:** fit a low-degree/calibrated correction such as

\[
\widehat A=g_0(\widehat M)+\delta_{\rm overnight}+\delta_{\rm clock}
+\delta_{\rm vol\ state}+\delta_{\rm stock},
\]

with positivity enforcement and **shrinkage** of group effects toward the global map. Choose at most one or two context families justified by D0, not every stock × seven slots × several regimes interaction. As appropriate, make the correction multiplicative or model it on log-mean scale.

**Ablations:** global map → one prespecified context family → optional second family; compare with matched stock×clock non-neural controls. The historical state must be known *before issuance*. No hindsight earnings/event label or retrospective source-quality classification as a live input.

**Failure mode:** group effects vary in sign by year or disappear after shrinking, indicating variance rather than stable heterogeneity. Stop instead of multiplying calibration cells.

### O1 — Train the same LSTM for the **raw expected absolute movement**

**Priority: first new supervised LSTM objective, after calibration comparisons.**

**Hypothesis:** A new objective may estimate `E[A|X]` more directly than calibrating `E[log(1+A/s)|X]`. With the same FT16, LSTM width, data and schedule, output a nonnegative raw-magnitude forecast, e.g.

\[
\widehat A=s_f\,\operatorname{softplus}(z_\theta(X)),\qquad
L_{\rm rawmean}=E_w\left[\left(\frac{A-\widehat A}{s_f}\right)^2\right],
\]

where `s_f` is fitted from permitted earlier data (the scaling normalizes numerical gradients; it does **not** redefine the reported raw outcome). Other smooth positive links are permissible as explicitly separate variants, not a gratuitous link-function grid.

**Comparator:** (i) saved S9-MAG decoded forecast; (ii) saved MAG + the most defensible C1/C2 calibrator; (iii) raw-MSE-optimal stock/clock/volatility baselines. Same **eligible origin/stock keys**, and for newly trained arms the same feature information and equivalent fitting opportunity.

**Measure:** raw weighted MSE is the primary expected-magnitude proper score; raw MAE, calibration, large-move accuracy, transformed-target MSE and magnitude ranking are supplementary. Since raw MSE can emphasize rare moves, report loss **and gradient** concentration; the original tail events must not be deleted or winsorized post hoc.

**Failure:** improvements are confined to rare extreme outcomes while ordinary errors explode, or no gain remains over causal calibration of the existing model. If direct MSE is numerically unstable, try **one declared optimization-scale fix**, not an architecture sweep.

### O2 — A **hybrid transformed + raw-magnitude loss**

**Priority: conditional; only if C1/C2 and O1 reveal a useful trade-off.**

**Motivation:** the transformed objective may optimize stably on ordinary moves, while a raw-scale component could push the estimator toward the desired physical mean. For one **linked positive forecast** `Â(\hat M)`, consider

\[
L=E_w[(\hat M-M)^2]
+\lambda E_w\left[\left(\frac{\widehat A-A}{s_f}\right)^2\right].
\]

**Important:** this loss targets a **compromise**; it is not automatically a proper squared-error loss for either `E[M|X]` or `E[A|X]` in isolation. Choose **one small prespecified** `λ` if empirical evidence justifies it; compare with the pure-objective controls and a baseline with comparable tuning budget.

**Stop:** if the mixed model merely trades away transformed-MSE for raw-MSE without any stable improvement over O1 or C2. Do not optimize `λ` against repeatedly inspected OOS years.

### O3 — Raw **median / robust location** models as *different estimands*

**Priority: secondary; useful for distinguishing typical-move forecasting from tail-sensitive mean forecasting.**

**Possible objectives:**

- Raw `L1`: `L=E_w|A-Â|`; targets conditional **median**. Include an earlier-trained stock median control.
- Raw Huber or log-cosh loss, with its scale set using **permitted training**: robust central-location compromise. Its minimizer generally is **not** the raw conditional mean.
- Avoid treating the old signed-target H2 experiment as if it tested Huber on raw absolute MAG. It did not.

**Scientific use:** determine whether better average MAE is obtained by a much more conservative prediction. **Do not promote a median forecaster as an improved expected-absolute-move forecast** if we ultimately need mean/tail utility for options.

**Stop:** if robust losses reduce ordinary MAE but worsen upper-tail reliability needed for the chosen downstream decision; preserve the task distinction in the report.

### O4 — **Upper magnitude quantiles, expectiles, and extreme-movement risk**

**Priority: potentially high for options, but *after* a good mean/median baseline.**

S9-QUANTILE previously predicted **signed TG20 transformed quantiles** and did not beat fitted stock-quantile controls. It did **not** establish the performance of quantiles of **raw `A=|R|`**.

**Two defensible and distinct candidates:**

1. **Conditional magnitude quantiles:** `q_τ(X)` for a small predeclared `τ` set (for example, 0.50 and 0.90, reserving 0.95 for later), trained by pinball loss

   \[
   \rho_\tau(A-q)=(A-q)(\tau-\mathbf 1\{A<q\}).
   \]

   Evaluate quantile-specific pinball, conditional coverage, calibration and tail ranking. Use **stock/clock/historical-volatility conditional quantile controls**, not just a global empirical quantile. If multiple heads are trained jointly, enforce or report **quantile crossing**.

2. **Upper expectile:** `e_τ(X)` minimizing

   \[
   E_w\left[|\tau-\mathbf1\{A<e_\tau\}|(A-e_\tau)^2\right]
   \]

   for one predeclared `τ>0.5`. Unlike `E[A|X]` or a quantile, an expectile is a tail-sensitive *squared-loss functional*; label it accurately.

**Event-score alternative:** choose a movement threshold `a` from permitted training history and evaluate `P(A>a|X)` with **Brier and cross-entropy**, against a strong stock/clock conditional event-rate baseline. This is a different target, not automatically improved by minimizing MAG transformed-MSE. Earlier S9-EVENT's worse CE against stock-specific prior is an important caution.

**Stop:** if the network's pinball/Brier/coverage is no better than well-fitted same-task controls or its tail reliability is unstable across chronological years.

### O5 — A **small probabilistic magnitude head** for mean + uncertainty

**Priority: conditional, higher complexity; not the first attempt.**

**Question:** Is the difficulty caused by fitting one conditional location when the distribution of `A` is very skewed, heavy-tailed and state-dependent? A one- or two-parameter **Gamma**, **lognormal-on-positive-A**, or explicitly **zero-inflated/hurdle** construction could output a mean, upper quantiles and tail probabilities from a single shared encoder.

**Minimal scientifically interpretable version:** keep original recurrent backbone; add a positive scale/dispersion head and one location/mean head, with constrained parameterization. Fit by **distributional negative log likelihood** and/or a properly specified **CRPS** comparator. If the empirical `A=0` mass is material, a continuous positive density alone may not be a coherent complete likelihood; examine the zero-mass before deciding the family.

**Why this is not automatically preferable:** it imposes a parametric distribution that may be wrong, especially for jumps, corporate events and overnight gaps. NLL can be fragile when dispersion collapses or tails are wrong; record those problems rather than quietly switching to an unbounded mixture.

**Comparators:** fixed/stock-dependent historical distribution, EWMA/HAR-style conditional scale distribution, simple calibrated MAG + tail quantiles. **Promote only if** it improves out-of-fold distributional score *and* reliability over these baselines; retain a point-mean accuracy comparison from the implied distribution.

**Defer:** mixture-density networks, generalized Pareto shock tails and complex multihead mixtures until a simpler conditional distribution has a specific demonstrated failure.

### O6 — Explicit **large-underprediction penalty**: use carefully or not at all

**Priority: reserve diagnostic, not default.**

It is tempting to weight errors by realized movement (`w(A)`), or to punish underprediction more than overprediction. However, **outcome-dependent reweighting changes the population functional being estimated**. A forecast trained this way cannot then be called `E[A|X]` without correction/qualification.

**Principled options:** compare one **upper expectile** or quantile from O4, or choose a *proper* probability/distribution score matched to the downstream decision. If trying a label-weighted loss as a utility-driven heuristic, state the tilted target, match a same-utility non-neural comparator, and report calibration damage on the actual raw mean.

**Avoid:** repeating the earlier signed-task W1/SS1 tail-weighting campaigns merely because tail events are difficult; they did not establish a MAG improvement and an unrestricted weighting search is easy to overfit.

### O7 — Shrinkage toward a credible magnitude baseline (small structural objective alternative)

**Priority: optional; consider only if D0/B0 identifies a strong simple risk forecast.**

Instead of allowing the LSTM to relearn predictable stock and clock levels, learn a **small residual correction** around a prefix-fitted baseline, e.g.

\[
\widehat A(X)=\operatorname{softplus}\left(b(X)+\delta_\theta(X)\right),
\qquad L=L_{\rm rawmean}+\lambda\|\delta_\theta\|^2.
\]

Here `b(X)` is a causally computed baseline score on a compatible scale; its training must not use its own evaluation outcomes. **Controls:** baseline alone, linear residual adjustment, plain same-information LSTM with no anchor. The correction must be necessary, not merely a rescaled copy of the baseline.

**Caution:** an anchor trained on M-space and used as though it were the raw mean produces a target mismatch. Use a baseline for the same estimand or explicitly calibrate it. The novelty, if any, would be a verified estimation benefit—not the additive residual operation itself.

---

## 4. What we *should not* merge into Stage 1 prematurely

- **New horizons, separate overnight-holding labels and S5-style clock input experiments** belong primarily to **Stage 2**. Stage 1 should still *diagnose* its existing overnight-crossing subset, since that is already in MAG. If D0 finds a large clock bias, C3 can test a tiny chronological calibration; a new clock-trained LSTM should be a separately labeled Stage 2 arm.
- **New minute-path/feature blocks** belong to Stage 3. Stage 1 baselines may use already saved, available FT16 lags; new minute features are an explicit **information change**, not an objective-only ablation.
- **Attention, A7/A12 gates, global–local recurrent redesign, xLSTM or state-dependent coupling** belong to Stage 4; earlier slight signed-regression improvements do not establish a magnitude benefit.
- **Training a magnitude ranking model** and **predicted-minus-implied movement ranking** belong to Stage 5. Within Stage 1, track the effect of each forecast change on existing *magnitude ranking* without changing the supervised target in the same run.
- **Additional prediction horizons and broad multitask architectures** belong to Stage 6. A compact magnitude quantile/uncertainty head in O4/O5 is a Stage 1 exception because it directly addresses calibration and the predicted functional.
- **Option straddles, signal thresholds, IV comparisons, delta hedging and portfolio allocation** are downstream. A properly calibrated `E_P[A]` by itself is not a four-hour option-value forecast, option-implied mispricing, or net return.

---

## 5. Honest chronological calibration and evaluation design

**Do not treat a mapping fit to 2021–2024 saved OOS forecasts and scored on the same pairs as a new OOS success.** There are two useful levels of work:

### Level I — read-only exploratory diagnosis (no new starts)

Reuse historical saved 2021–2024 predictions to **describe** reliability, sources of bias, Jensen-gap candidates, error concentration, stock/year effects and monotonicity. Plotting an *oracle/in-sample* calibration curve is acceptable as a **diagnostic ceiling**, if labeled as such; it cannot be reported as deployable performance or as a reason to claim a new post-search improvement.

### Level II — honest fitted calibration (must be explicitly designed/approved)

For each outer evaluation year `f`, fitting a calibrator requires earlier **prequential or temporally out-of-fold** `(issued MAG prediction, matured A label)` pairs lying strictly before that outer year. Possible approaches:

**A. Reserved chronological calibration tail:** use an earlier prefix to fit/select the neural encoder; generate predictions on a later, untouched-with-respect-to-that-fit calibration tail; fit calibration map; deploy that *same* encoder plus map to the next evaluation period. This sacrifices the historical MAG full-prefix fresh-refit procedure and therefore requires a **matched no-calibrator comparator trained under the same restricted history**. It is cleanest for isolating calibration.

**B. Earlier-prefix prequential forecast bank:** create a small sequence of strictly chronological earlier-prefix models, issue honest forecasts on their subsequent earlier blocks, and fit a calibration map on those completed labels. Apply the map to a later separately refitted outer-year model only with a declared **model-distribution-shift check**, since forecasts from successive models can have different scales. This preserves much of the historical full-refit opportunity but has more compute and complexity.

**C. Existing inner-validation forecasts:** if archived/calculable, use them only with an explicit caveat: the *inner-calibration checkpoint* differs from the final fresh-refit checkpoint, and the same validation tail may have determined the epoch. Fitting a calibrator on those forecasts might be leakage-free with respect to the outer year, but is **not a clean, identical-model heldout calibration experiment** unless the full selection/calibration design accounts for reuse. It is a lower-cost exploratory alternative, not assumed valid automatically.

**Initial recommendation:** for the first *fitted* C1/C2 comparison, choose **A** if isolating calibration is the priority; for an eventual end-to-end fully refitted model, carefully design **B** only if the simple calibration evidence warrants it. For F21, genuine pre-2021 calibration observations would have to be prepared; no future fold's outcomes may be borrowed to initialize F21. If no honest calibration data are available, mark the calibrated F21 result unavailable rather than manufacturing an estimate.

**Selection nesting:** decide the calibration family and hyperparameters using earlier history only; the current year's actual outcome is used only for scoring. If calibrators and new neural objectives are both tuned, use a chronological internal design that isolates their selections; do not choose the best of many variants by repeated OOS-year inspection and then call its resulting confidence interval confirmatory.

---

## 6. Metrics, robustness and promotion standard

### 6.1 Different targets require different primary scores

| Prediction product | Main proper scoring/evaluation | Necessary calibration check | Important secondary check |
|---|---|---|---|
| Transformed location `E[M|X]` | **Transformed MSE**, exactly as executed | Mean residual in M-space | Raw error only after named decoder |
| Raw mean `E[A|X]` | **Raw A MSE** with fixed role weighting | Mean observed vs mean predicted, reliability by bins and periods | Raw MAE; magnitude-rank IC; tail misses |
| Raw median | **Raw A MAE** | Approximately 50% below predicted median | Tail errors, rank IC |
| Raw `τ` quantile | **Pinball loss at τ** | Empirical `P(A≤qτ)` vs `τ`; conditional coverage | Exceedance ranking and pinball by year |
| Event probability `P(A>a|X)` | **Brier and log loss** | Reliability, event base-rate comparison | Average precision / ROC as discrimination-only metrics |
| Full conditional distribution | **NLL and/or CRPS** | PIT/quantile coverage, zero-mass and tail calibration | Implied mean MAE/MSE and tail scores |

All scores should use the **same year/session/origin/stock aggregation convention** as the historical MAG program wherever coherent. Compare **paired per-session/per-origin differences** and report annual results separately; descriptive whole-month/block uncertainty is preferable to assuming overlapping stock-hours are IID. Seeds assess optimizer variability, not independent market years.

### 6.2 Fixed diagnostic dashboard — tables are sufficient

- **Mean magnitude calibration:** weighted `E[A]`, `E[Â]`, difference, ratio, decile reliability, calibration slope, counts and confidence summaries; note nonlinear decoding of M.
- **Tail fidelity:** fixed earlier-training thresholds (such as 90th/95th), coverage/recall, false-low rate, conditional error and tail-specific proper scores; also ordinary-row errors and loss concentration.
- **Magnitude ranking:** within-origin Spearman correlation between the estimated *magnitude score* and realized `A`, plus top/bottom magnitude retrieval and tie rates, with an identical-key simple comparator. Do **not** label this signed-return IC or take the archival `0.408` as a guaranteed same-definition baseline without verifying its metric implementation.
- **Generalization:** 2021/2022/2023/2024 separate results; stocks and clock classes; chronological subset stability and matched baselines; no optimistic “20 stocks × 4 years = 80 independent tests” inference.
- **Economic relevance later:** report whether outputs could plausibly distinguish a large move from an option-implied hurdle, but **do not tune a straddle signal or claim net P&L in Stage 1**.

**Promotion principle:** A complicated predictor should beat a simpler predictor **for the same conditional functional, same permitted information and actual usable population**, without severe degradation in the important ordinary/tail cohorts. Meaningful gains must persist chronologically. A new model that only improves a secondary descriptive metric should be recorded as a trade-off, not automatically called superior.

---

## 7. Recommended decision ladder — small initial set, not a full factorial sweep

| Order | One research decision | Suggested scope | Proceed when... |
|---:|---|---|---|
| **0** | D0 read-only calibration and tail breakdown | **0 neural starts** | We understand whether bias is global, high-forecast, stock/clock-specific or tail-driven |
| **1** | B0 same-functional stock/clock/conditional-volatility controls | Mostly cheap non-neural fits; bounded feature set | The original MAG advantage still merits additional LSTM complexity |
| **2** | C1a + C2 simplest global maps | **0 new neural starts**, but **past-only honest** calibration fit necessary | Out-of-period mean/tail calibration improves beyond constant/multiplicative correction |
| **3** | **O1 direct raw-mean LSTM** versus best calibrated MAG | One compact neural family; initial seed 42, same four folds if authorized | Objective alignment gives incremental raw-mean skill, not just larger forecasts |
| **4** | Choose **one** follow-up: C3 conditional calibration, O4 upper magnitude quantile/expectile, or O5 probabilistic head | Condition on observed failure; not all three | A specific unresolved weakness remains and strong controls are ready |
| **5** | O2 hybrid or O7 residual-anchored LSTM | **Reserve**, only after a concrete bias/variance trade-off is documented | A simpler correction/direct objective demonstrably lacks needed capability |
| **6** | Replicate finalist with additional seeds and later genuinely independent confirmation | A separate approved and frozen evaluation | Predictive claim justifies extra compute; 2026 boundary remains untouched until explicitly released |

**Reason for this order:** We should not expend new model training merely to fix a one-dimensional decoder. Conversely, a global calibration factor cannot create missing within-day conditional ranking or predict rare jumps. Direct raw-MSE training is therefore a useful early architecture-**fixed** intervention. Sophisticated distributions/mixtures and asymmetric penalties come later only when the simpler stages fail in an informative way.

### Budget and operational suggestions (not approved allocations)

- **Read-only and non-neural first.** Use saved checkpoints/predictions; inspect a small number of existing metrics and trace examples. Do not build a new dashboard.
- **One new candidate neural family** across F21–F24 normally means **four fold-specific training/refit starts** under the current ledger nomenclature, not one model. A second seed for a finalist is an additional four; avoid a blanket multiple-seed/grid launch at screening.
- The last reported ledger was **130/200 started neural pairs** (70 nominal remaining), but confirm with the **live repository** before scheduling. Remaining budget does not imply automatic authorization.
- Use an append-only compact experiment card: hypothesis, estimand, unchanged/changed information set, target and loss, training and calibration chronology, comparators, valid-key population, primary score, stop criterion, resources and short outcome summary. Do not log every minibatch parameter.
- Do not overwrite old MAG results, alter historical FT16/scale recipes, or test an unauthorized new horizon/period while implementing an objective change.

---

## 8. Initial decisions to settle in our next discussion

1. **What is primary for Stage 1:** a calibrated **conditional expected absolute move**, or a **tail/upper-quantile forecast**? Recommendation: establish the conditional mean and its calibration first; retain magnitude ranking/tails as secondary diagnostics.
2. **What can serve as truly earlier calibration data** in the existing fold structure? Recommendation: start with read-only D0, then choose chronological method **A** for a controlled calibrator study, openly matching the encoder training history.
3. **How strong must the control be?** Recommendation: at minimum add raw-mean/median `STOCK` controls and a **stock×clock-aware conditional volatility** control; do not rely solely on the archived simple `VOL`.
4. **Which new LSTM objective gets the first fitting budget?** Recommendation: **O1 direct raw expected magnitude**, compared against frozen MAG and causally calibrated MAG under a fairly matched training opportunity.
5. **When to introduce tails/quantiles?** Recommendation: only after D0/O1 demonstrate whether extreme-move misses remain structurally important; prefer a single declared O4 objective before a full O5 probabilistic mixture.
6. **How to protect interpretation?** Keep 2021–2024 explicitly exploratory, the unchanged 2026 confirmation set closed, and downstream options-profit claims outside this stage.

---

## 9. Definition of a successful Stage 1 outcome

**Strong positive:** A plainly specified calibration procedure or changed target/objective improves the **appropriate proper out-of-sample statistical score** over both original S9-MAG and strong same-functional controls, with credible chronological, calibration and tail diagnostics, without tuning on the scored period.

**Valuable mixed result:** Raw-mean calibration improves, but magnitude ranking does not; or a tail-quantile objective improves coverage while ordinary raw-MAE deteriorates. Report the distinct statistical product rather than a single “winner.”

**Useful negative:** A stock×clock/volatility baseline or simple calibration matches or beats the more complex LSTM, or a new raw objective does not improve its declared estimand. Stop the branch; the original S9 result remains documented.

**Insufficient evidence:** Effects appear only in one year, one scarce clock class or one seed, or the calibrator was fitted/evaluated on the same observed pairs. Retain the hypothesis as exploratory and do not promote it.

**Completion for this document:** agreement on a *small* first experiment card (likely D0/B0/C1–C2), with explicit training/calendar/score definitions and resource cap **before** producing any Codex implementation prompt. No automatic work proceeds from this plan.
