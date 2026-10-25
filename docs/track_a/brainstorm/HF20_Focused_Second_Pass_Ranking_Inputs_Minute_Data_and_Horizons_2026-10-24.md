# HF20 focused second pass: ranking-first learning, inputs, minute data, and prediction horizons

**Date:** 24 October 2026  
**Version:** 1.0 — focused research addendum; not a Codex execution prompt  
**Primary immediate objective:** Reliably rank future stock performance across multiple chronological evaluation periods.  
**Ultimate objective:** An LSTM-based equity trading system. Portfolio selection, execution-cost optimization, and profitability assessment are deferred in this pass.  
**Research ledger:** **62/200**, unchanged. No model was trained and no new empirical performance result was generated for this report.  
**Universe:** The existing HF20 panel for the agreed diagnostic work. No stock selection or expanded-universe construction is undertaken here.

**Exact baseline document:** `HF20_LSTM_Comprehensive_Review_and_Expansion_Plan_2026-10-24.md`, titled *HF20 LSTM: Evidence Review, Fundamental Fixes, and Larger-Universe Development Plan*. This is the date-suffixed project file corresponding to the shorter filename in the request. The file inspected in this environment has SHA256 `1657b7a37791e3e67b90e367089879ee302d3cfa89e9a6a71d258b3711687a94`. It is not overwritten by this addendum.

**Evidence notation:** **[HF20, §x]** refers to that document; **[P028-T]** and **[P028-G]** refer to the supplied detailed tail and gradient reports; **[Sxx]** identifies external research listed in Section 15. New mathematics is explicitly presented as derivation; proposed tests are not reported findings. Repository code, predictions, raw minute data, and protected outcomes were not independently rerun or examined here.

**Navigation:** [Ranking contract](#ranking-contract) · [Ranking losses](#ranking-losses) · [Input audit](#input-audit) · [Minute inputs](#minute-inputs) · [Horizons/interday](#horizons) · [Magnitude](#magnitude) · [Dropout audit](#dropout-audit) · [Section 8 workstreams](#diagnostic-workstreams) · [Information tests](#information-tests) · [Next decisions](#next-decisions) · [References](#references)

---

## Executive assessment

The most defensible next research direction is **not “make the forecasts larger.”** It is to align the prediction problem with cross-sectional ordering, determine whether the current inputs contain stable ordering information, and investigate information that hourly feature aggregation may hide.

This pass changes the emphasis of HF20 in five ways:

1. **Ranking becomes the primary prediction objective.** The immediate question is whether a score orders subsequent stock performance reliably over time—not whether it reproduces the magnitude of a realized TG20 outcome. A complete ranking contract still needs to be frozen before fitting.
2. **Minute inputs, forecast issuance frequency, and outcome horizon are separated.** Minute observations can inform an hourly forecast whose outcome spans several hours or the next session. None of those choices forces minute-by-minute trading.
3. **Overnight and multiday outcomes become explicit research candidates.** The two morning origins and same-session four-hour target are retained as a reference, not treated as the only permissible problem.
4. **Magnitude forecasting stays a separate, potentially useful capability.** It can contribute to risk estimates or help a signed model, but magnitude alone does not generally determine which stock will outperform.
5. **The “heavy dropout plus no asinh” idea is not supported as a first remedy.** Stronger dropout does not remove the large-residual factor in squared-error gradients; for the present linear readout it can add a shrinkage-like penalty. Nor does it guarantee an accurate conditional mean. Pure ranking losses address the current objective more directly.

**Practical recommendation:** complete all seven HF20 §8.1 diagnostic workstreams, preserve §12, and prepare a versioned ranking-first task specification. The strongest new candidates for a bounded later study are a simple direct-ranking objective and a controlled test of information retained from minute paths. They are candidates for approval, not automatic runs. Do not combine new inputs, new horizons, stronger dropout, and a new loss in one experiment and call the result an explanation.

### Disposition of the ideas in this request

| Idea | Assessment after this pass | What would make it worth testing |
|---|---|---|
| Direct ranking instead of magnitude regression | **Strong objective-alignment rationale; not an empirical guarantee** | A frozen rank target/metric and matched simple/LSTM controls |
| Minute inputs while producing hourly forecasts | **Credible information-representation hypothesis** | Usable minute coverage and evidence that hourly summaries discard relevant structure |
| Overnight or multiday outcomes | **Credible change of prediction task** | Correct endpoint definitions, gap/action handling, and chronological horizon comparison |
| Minute inputs plus interday outcomes | **Coherent combination, but harder to attribute** | Separate information and horizon controls before combining them |
| Variable-hour predictions | **Useful as fixed, prespecified horizons first** | A small horizon set, common-origin comparisons, correct label maturity |
| Magnitude as a trading signal | **Useful potentially, but not an automatic directional signal** | Improvement over simple risk/activity baselines and, separately, incremental signed-ranking evidence |
| Stronger dropout with untransformed MSE | **Low priority under current evidence** | Reproducible overfitting/optimization evidence specific to the proposed mean-target model |
| More features or more complex recurrent cells | **Not a default response** | A concrete representational or learnability gap revealed by the diagnostics |

---

## 1. What carries forward, what changes, and what remains paused

### 1.1 Preserve the original evidence

HF20 §§2–6 remain the record of the completed experiments. In particular:

- T2/42 is a **working signed-score reference**, not an independently established best model. Its development Rank IC is about 0.0756; T2/123 is about 0.0255. The seed difference remains important.
- R1 tested an auxiliary pairwise ranking term alongside the existing objective, not an exhaustive investigation of pure ranking. Its tiny original-MSE improvement did not improve daily IC.
- A7/A12 improved original MSE slightly but worsened z-MSE and ranking. Preserve the common-level-versus-cross-sectional-error hypothesis; it is not yet established.
- E1 and QR1 have task-specific event/outer-quantile evidence. Their results do not establish reliable signed ranks or accurately calibrated future realized volatility.
- A9–A11 remain untested and paused. A1–A8/A12 results must not be described as failures of every possible member of those architecture families.
- The repeatedly used July–December 2025 development population has 109 sessions, 183 origins, and 3,660 stock-origin observations. It is not refreshed by asking a new question of it. [HF20, §§2–3, 11]

These facts motivate the present review; this document does not retroactively change the success criteria of P021–P028.

### 1.2 Adopt the user's updated ordering of goals

The immediate goal is **stable cross-sectional predictive ordering**. Full portfolio implementation, position sizing, turnover optimization, cost-sensitive threshold selection, and profitability conclusions in HF20 §5.11 are deferred.

This is a change in research sequencing, not a claim that ranking alone proves eventual profitability. We do not need to build a backtest to compare ranking losses. We still need to define a genuinely future outcome using an information cutoff that is available at forecast issuance. Otherwise we could improve the ranking of a partly elapsed return rather than improve forecasting.

**Revision to HF20 §7, first row:** replace the immediate emphasis on execution economics with **“freeze causal forecast-origin and future-outcome semantics before comparing ranking models.”** Keep a minimal record of how these outcomes could later relate to tradable intervals; defer the execution engine and P&L work.

### 1.3 Complete all of HF20 §8, without turning it into a new architecture sweep

The user has accepted the seven §8.1 diagnostic workstreams. Section 10 below translates every one into the current ranking-first scope. This report does **not** claim those diagnostics have already been executed.

Baseline inventory is read-only. Training a missing baseline is a new supervised fitting task, even if it is inexpensive and non-neural. Likewise, creating new horizon labels, building minute encoders, fitting calibration maps, or extending forecast populations needs a separate scoped implementation decision. Existing authorizations and the protected-data boundary remain intact.

---

<a id="ranking-contract"></a>

## 2. Freeze what “predict ranking” means before choosing a loss

### 2.1 Define the object being ranked

For an origin \(t\) and a prespecified horizon \(h\), let

\[
R^{(h)}_{i,t}=\log\frac{P_{i,e(t,h)}}{P_{i,b(t)}}
\]

be a consistently defined subsequent return. Here \(b(t)\) is the start reference and \(e(t,h)\) the endpoint; their timing and price conventions must be stated. At an origin, all stocks being ranked must have the same economic interval and return convention.

The task is to produce scores \(s_{i,t,h}\) so that larger scores tend to correspond to larger subsequent returns across the eligible stocks. The current four-hour label remains the historical anchor. A revised start time, horizon, or endpoint creates a new version of the target; it does not silently replace TG20.

**Relative prediction is not automatically easier than absolute prediction.** A common shock can cancel in return differences, which may help. Conversely, after that shock is removed, the remaining ordering may depend on noisier stock-specific innovations. The answer is empirical, not a theorem favoring ranking.

### 2.2 Asinh is unnecessary for constructing pure ordering labels

At a fixed origin, TG20 subtracts the same median and divides by the same positive denominator for every stock. Its asinh transformation is strictly increasing. Therefore,

\[
\operatorname{rank}(R^{(4)}_{i,t})
=\operatorname{rank}(Y_{i,t})
=\operatorname{rank}(\operatorname{asinh}(Y_{i,t}/s)).
\]

The same statement holds for ties under a consistent rule. Thus a new pure-ranking model can use orders derived from the existing outcomes **without needing to regress transformed or untransformed return magnitudes**. Existing T2 predictions remain a valid ranking comparator; applying its common positive-scale `s*sinh` inverse does not change their ordering.

This does not mean the existing T2 loss was equivalent to rank training. Its loss still responds to transformed distances between outcomes. Nor does it mean that a per-stock volatility-normalized target has the same ordering: dividing each stock by a different scale generally changes the task.

### 2.3 Expected return, probability of winning, and expected rank differ

The following are different predictive quantities:

\[
\mu_i=E[R_i\mid\mathcal F_t],\qquad
p_{ij}=P(R_i>R_j\mid\mathcal F_t),\qquad
u_i=E[\operatorname{rank}(R_i)\mid\mathcal F_t].
\]

As a mathematical example, let stock A return 100 with probability 0.01 and −1 otherwise, while stock B always returns zero. A has the higher expected return, 0.01 versus zero, but loses to B 99% of the time. This is a decision-theoretic example, not a model of HF20.

For **expected Spearman correlation**, there is a useful precise result. Assume a fixed \(N\), no realized ties, and a predicted permutation \(\widehat r\). Then

\[
\rho_S=1-\frac{6\sum_i(\widehat r_i-r_i)^2}{N(N^2-1)}.
\]

Conditional on the available information, maximizing expected Spearman is equivalent to maximizing

\[
\sum_i\widehat r_i E[r_i\mid\mathcal F_t].
\]

By ordering the conditional expected ranks, one obtains an optimal permutation for this criterion. This follows because the sums of squared ranks are fixed and the remaining term is a dot product. Ties, changing eligible sets, and restricted model information require their own treatment; this is not a universal consistency theorem for every ranking surrogate.

**Consequence:** exact estimation of \(E[Y\mid X]\) is not a prerequisite for the rank-first project. The statistical target should match the chosen ranking criterion. General guidance on matching a forecast functional to its loss comes from Gneiting; finance-specific learning-to-rank work supplies empirical motivation, not a guarantee for HF20. [S01] [S06]

### 2.4 Proposed ranking contract

Before new fitting, record the following in a versioned card:

| Item | Recommended starting position; not yet a numerical freeze |
|---|---|
| Main task | Rank subsequent returns within the contemporaneously eligible cross-section |
| Main evaluation | Mean within-origin Spearman IC, aggregated equally within session and then equally across sessions |
| Secondary ranking checks | Pairwise concordance, normalized rank error, top/bottom retrieval, score ties, rank stability, per-period and per-origin performance |
| Outcomes | One reference horizon; a small, separately labeled set of horizon alternatives only when authorized |
| Primary comparison | Same information, stock/date population, label, and fitting opportunity; T2 retained as reference |
| Training candidate | Normalized-rank regression and/or one pure pairwise objective; see Section 3 |
| Checkpoint selection | A prespecified ranking-led rule, with deterministic tie handling and a bounded stopping policy |
| Time robustness | Multiple chronological folds and matched seeds, not the best reused-development result |
| Economics | Deferred; no claim of profitable trading from IC alone |

Keep the current constant-score convention explicit: mathematical Spearman is undefined for a constant score vector; report the constant rate and any project-defined zero score separately. Do not add tiny random noise to create an artificial ranking.

For a genuinely ranking-only model, original-return MSE is not a primary acceptance test. Its output has score units, not expected-return units. Old T2 original/z-MSE diagnostics remain available for old models, but should not be manufactured for a new ranking score by arbitrarily applying `sinh`.

A ranking-led selector may use validation daily IC, but IC can be noisy. Its patience, qualifying improvement, tie rule, and any smoothing must be fixed before fitting. The old positive-loss rule `new_MSE < .999*best_MSE` must **not** be mechanically applied to a correlation that can be zero or negative. A surrogate-loss stopping monitor is also possible if declared in advance; model comparison must remain ranking-led. No stopping-rule change is made retrospectively to P028.

---

<a id="ranking-losses"></a>

## 3. Which ranking objectives deserve a controlled test?

### 3.1 Lowest-complexity direct target: normalized realized rank

Let \(r_{i,t}\) be the ascending midrank within the eligible cross-section and define

\[
q_{i,t}=2\frac{r_{i,t}-1}{N_t-1}-1,\qquad N_t>1.
\]

Train the shared encoder/head with

\[
L_{\mathrm{rank-reg}}
=\frac1{|\mathcal D|}\sum_d\frac1{|\mathcal O_d|}
\sum_{t\in\mathcal O_d}\frac1{N_t}\sum_i(s_{i,t}-q_{i,t})^2.
\]

The target is bounded and ordinal. It removes the direct dependence of the target magnitude on a rare extreme return or small MAD. It is still squared-error regression, but it regresses a **rank quantity**, not return size. Its population optimum under squared loss is the conditional expected normalized rank given the model's information. The derivation in §2.3 explains why this is a defensible simple control for full-cross-section Spearman.

It is not identical to maximizing sample IC. A finite or misspecified model can still make poor orderings; a linear output can still become extreme; and the bounded target does not bound every parameter gradient. Nevertheless, this is easier to audit than a complex listwise system and directly addresses the present objective mismatch.

A common predicted offset cannot improve ranking. For the complete equal-weight rank target, the cross-sectional mean is zero. Track common-score and centered-score error separately; an explicitly centered score path may be a later design choice rather than an unannounced change.

### 3.2 Pure pairwise logistic ranking: the main alternative

For unequal realized outcomes, define \(d_{ij,t}=\operatorname{sign}(R_{i,t}-R_{j,t})\). A RankNet-style loss is

\[
L_{\mathrm{pair},t}
=\frac1{|\mathcal P_t|}\sum_{(i,j)\in\mathcal P_t}
\log\left[1+\exp\left(-d_{ij,t}\frac{s_{i,t}-s_{j,t}}{\tau}\right)\right],
\]

with \(\tau>0\) fixed by the approved protocol and each unordered pair counted once. Aggregate origins and sessions with the same declared hierarchy. RankNet supplies the underlying probabilistic pairwise approach. [S02]

This tests something **different from R1**: no asinh regression term remains in the primary objective. It does not assume that a particular mixture coefficient was the only issue in R1.

Important advantages and limitations:

- The raw size of a return gap does not multiply the loss when labels are only order signs.
- The derivative with respect to the score difference is bounded in magnitude by \(1/\tau\); parameter gradients also depend on the network Jacobian and are not thereby globally bounded.
- Confidently incorrect pairs can have arbitrarily large logistic loss. “No heavy return-magnitude multiplier” is not the same as “bounded loss.”
- Twenty stocks give 190 unordered pairs at an origin, **not 190 independent market observations**.
- Tiny realized differences may be difficult to distinguish from endpoint noise. Show performance by outcome-gap bins, but do not tune a favorable gap cutoff on development. A future label-based tie/dead-zone convention changes the supervised task and needs advance approval.
- Pairwise preferences need not admit a perfectly transitive scalar ranking in every conditional distribution. A single-score model is a useful restriction, not unrestricted pair-probability estimation.

Normalize by the actual valid pair count before date aggregation. With a future variable panel, otherwise large cross-sections would receive unintended extra weight.

### 3.3 Listwise alternatives: legitimate, but not all first runs

| Objective | What it optimizes | Relevance and caution |
|---|---|---|
| **ListNet-style cross-entropy** | A probability distribution over items derived from target and predicted scores | Uses the full cross-section as a training instance; a softmax of raw returns can reintroduce tail/scale emphasis. Prefer an explicitly justified rank-derived relevance convention if the task is ordinal. [S03] |
| **ListMLE** | Likelihood of the observed permutation under a score-based ranking model | Uses the full ordering; tie treatment and noisy adjacent ranks matter. Not equivalent to expected Spearman. [S04] |
| **Differentiable Spearman** | Correlation involving a smooth ranking operator | Closest metric alignment, but smoothing strength, ties, constant scores, and gradient behavior need controlled checks. [S05] |
| **LambdaRank/LambdaMART or top-weighted ranking** | A surrogate emphasizing changes in a chosen ranking metric | Potentially useful later for a specified selection objective; do not prematurely optimize an arbitrary top-k portfolio when the current goal is broad ranking. [S06] |

For example, with a descending realized permutation \(\pi\), ListMLE uses

\[
-\sum_{k=1}^{N}\log
\frac{\exp(s_{\pi_k})}{\sum_{j=k}^{N}\exp(s_{\pi_j})}.
\]

A ListNet-style top-one construction could define target probabilities from normalized realized ranks, then compare them with softmax scores. This is a proposed HF20 adaptation; neither it nor the displayed ListMLE likelihood is a proof of improvement on financial data.

The finance ranking literature supports taking the objective seriously. Poh and coauthors compare ranking methods in a monthly cross-sectional momentum setting, while Feng and coauthors combine temporal stock representations and ranking-oriented learning. The frequencies, inputs, objectives, and evaluation differ from HF20. In particular, a paper with a combined regression/ranking objective does not establish that pure ranking will win here. [S06] [S07]

### 3.4 Recommended order, conditional on later approval

**First specify and test the implementation of normalized-rank targets and a pure pairwise loss.** Use a regularized linear score as a transparent comparator to the shared LSTM. This is a small diagnostic design, not a recommendation to train five losses across every architecture.

If ranking information is established but a concrete surrogate mismatch remains, consider one listwise or differentiable-Spearman alternative. Do not proceed simply because an earlier loss had a disappointing point estimate.

Do not require a pure rank model to improve original TG20 MSE: that would recreate the conflicting-objective problem. Preserve return-based descriptive checks, but keep the declared ranking criterion primary.

---

<a id="input-audit"></a>

## 4. Extending HF20 §5.9: what information might the inputs hide?

The original section identifies fallback ambiguity, compressed price paths, clock ambiguity, and heterogeneous pooled relationships. The following turns those into falsifiable questions rather than assuming more features are better.

### 4.1 Missing, ordinary, and stale values must be distinguishable when observable

A standardized zero can be a genuine ordinary feature or a substituted fallback. A repeated price can be a true unchanged observation, an allowed stale input proxy, or a missing vendor observation. These situations are not interchangeable.

The appropriate audit is not simply “add a mask.” For each current FT16 channel, establish the native value, fallback value, reason, observation age, and **when that reason became knowable**. A retrospective quality flag that used later data cannot become a live model input.

Proposed minimal fixes, only if the audit identifies a material ambiguity, are a causal validity indicator, an elapsed-time/age variable, or a compact feature-family quality summary. Compare against the same model with the original information. Do not add every internal quality flag or a vendor-era identifier by default.

Che et al. provide a primary methodological precedent for masks and elapsed time in recurrent prediction. Their empirical application is clinical data; this supports an information-design question, not a proven equity signal. [S08]

### 4.2 The model may see indicators but not the path that produced them

Two hourly bars can have the same open, high, low, close, and total volume but very different paths: early rise and reversal, late breakout, intermittent trading, or a concentrated volume burst. An hourly feature vector cannot reconstruct information discarded by aggregation.

A useful audit asks: **which potentially predictive distinctions are absent from FT16, rather than merely difficult for its LSTM to learn?** Candidate representations include causal return/gap sequences, normalized intrahour paths, range position, trusted activity profiles, and separate absolute volatility context.

Jiang, Kelly, and Xiu motivate learning price representations rather than restricting attention to a few traditional indicators. Their image-based research is not evidence that this project needs chart images or that a minute representation will work. [S09]

### 4.3 Preserve relative and absolute scale deliberately

Normalization can improve stability while discarding information. A return divided by its historical volatility conveys a standardized shock; it does not convey the underlying volatility level unless that is retained elsewhere. Similarly, stockwise normalization can remove distinctions across stocks that matter for a shared model.

The audit should identify what FT16 already preserves before proposing replacements. A candidate design may combine a standardized local return with the causally known scale and a contemporaneous cross-sectional context. Do not use future MAD, future volatility, or test-fitted cross-sectional thresholds as inputs.

For ranking labels, multiplying all stocks by the same positive factor preserves ordering. Scaling stocks by their individual volatilities changes the realized order. That can define a legitimate risk-adjusted ranking task, but it is not the same task.

### 4.4 Represent trading time and wall-clock time separately

The current 48 observations are scheduled complete-hour slots, not 48 uninterrupted hours. An overnight gap, weekend, early close, and ordinary one-hour step should not be confused merely because they are adjacent tensor entries.

First audit M2, Q1, and the existing daily-origin features: some session-specific information is already present. Then identify whether an explicit origin-slot indicator, historical slot indicator, elapsed minutes, session-boundary flag, or separate overnight return would add a genuinely missing distinction.

The literature documents session-specific and overnight/intraday differences, but not their persistence in this exact modern HF20 sample. [S10] [S12] [S13]

### 4.5 Shared parameters can average away heterogeneous effects

A shared mapping can encounter a positive relationship in one group and a negative one in another. If its inputs do not identify the relevant context, pooling can average those coefficients toward zero. This is a plausible statistical mechanism, not a demonstrated explanation of our compressed scores.

A low-complexity test uses a few predeclared, causally available contexts and interactions—such as volatility state, origin slot, or verified sector context—in a regularized model before introducing a mixture of recurrent experts. Avoid unrestricted ticker embeddings as the default response.

Also compare against a historically fitted stock-profile score. If a model largely reproduces persistent per-stock average ranks rather than time-varying forecasts, that is different evidence from learning a dynamic pattern. Both can be measured; neither should be mislabeled.

### 4.6 Check whether the sequence is actually being used

A static nonlinear model or a lagged linear model may perform similarly to the LSTM because the useful information is concentrated in the latest indicators. Alternatively, the LSTM may fail to use earlier information.

A later controlled comparison should hold the information horizon fixed: full permitted lag history versus latest-step or explicitly chosen summaries. Read-only history replacement, order perturbation, and hidden-state probes can assess functional sensitivity, but these create artificial inputs and do not identify a causal or market signal.

Learning from a planted ranking signal is a technical capability test. It does not demonstrate real predictive information. A reproducible failure on a correctly constructed synthetic task would justify a small repair before any larger study.

---

<a id="minute-inputs"></a>

## 5. Minute data while working on hourly windows

### 5.1 Separate five design axes

| Axis | Meaning | A coherent example—not a selected design |
|---|---|---|
| Observation resolution | How frequently inputs are observed | One-minute bars |
| Lookback reach | How much past calendar/trading history is available | The same 48 completed hourly slots as the reference |
| Internal representation | How that history is encoded | Within-hour encoder followed by an hourly LSTM |
| Forecast cadence | When a new cross-sectional ranking is issued | At completed hourly endpoints |
| Outcome horizon | What future return is ranked | Four trading hours, or a separately specified next-session interval |

Minute input does **not** imply a one-minute return target, one-minute decisions, or one-minute holding periods. Likewise, an overnight target does not require extended-hours minute inputs. These are separate interventions.

“Working on hourly windows” can mean only the latest hour of minute observations, or minute detail inside each hour of a multi-hour history. This report develops both options. The eventual experiment card must choose explicitly; they have different information reach.

### 5.2 Three progressively more demanding representations

**MIN-0 — Hourly reference.** Keep the current engineered hourly information. This is the anchor, not a claim that its summaries are sufficient.

**MIN-1 — A few within-hour statistics.** Derive a small, prespecified set of quantities from actual observed minute paths, such as early-versus-late movement, realized variation, signed semivariation, and availability/age. Add only distinctions not already encoded by the hourly indicators. This asks whether intrahour detail matters without immediately introducing a long recurrent sequence.

**MIN-2 — A learned minute-to-hour encoder.** Let \(u_{i,b,k}\) contain minute-derived inputs for minute \(k\) in completed hour block \(b\), with valid-data masks and timing metadata. Construct

\[
e_{i,b}=\operatorname{Encoder}_{\text{minute}}(u_{i,b,1:K_b},\text{mask},\text{time}),
\]

then

\[
(h_{i,b},c_{i,b})=
\operatorname{LSTM}_{\text{hour}}([e_{i,b};x^{\text{hour}}_{i,b}],h_{i,b-1},c_{i,b-1}),
\qquad s_{i,t,h}=g_h(h_{i,t}).
\]

A small recurrent or convolutional encoder is a proposal, not a frozen architecture. Parameters can be shared across hours and stocks. The outcome is supervised once per forecast origin; the 60 minutes within an hour do not create 60 independent copies of its future label.

A cheaper variant encodes only the most recent hour at minute resolution and combines it with the existing longer hourly history. That tests recent-path information without processing every minute in all 48 hours. Compare its actual information reach honestly against a full-window minute encoder.

The hierarchical design here is our methodological proposal. DeepLOB demonstrates useful learned high-frequency representations coupled with LSTM in a much richer order-book setting; it does **not** establish an advantage from minute OHLCV or validate this exact hierarchy. Huddleston et al. study predictive information from five-minute constituent returns for the aggregate market, which is also a different outcome. [S11] [S20]

### 5.3 Why not begin with one 2,880-step LSTM?

Forty-eight complete hours of one-minute inputs can require 2,880 recurrent steps per stock, compared with 48 now. This increases computation and temporal credit-assignment distance; it does not multiply independent forecast events by 60. It may also give the model many repeated proxy/fallback observations.

The layered minute-to-hour design shortens the hourly recurrence but can itself discard information in its within-hour bottleneck. The appropriate question is whether that trade-off helps, not whether hierarchical models are universally better. Any comparison should disclose parameter count, compute, pooling, actual input history, and whether a simpler intrahour summary receives comparable information.

### 5.4 Minute data quality is a prerequisite, not a footnote

Before using the existing source at finer resolution, audit:

- Which minute cells are genuinely observed, versus synthesized by the current input proxy/fallback convention?
- Can observed zero volume be distinguished from absent/unverified volume? Do not infer order flow or bid/ask imbalance from unsigned OHLCV.
- Do all inputs belong to completed, available bars at the forecast cutoff? Is asynchronous stock availability handled without later observations?
- Are a short closing stub, early close, overnight interval, and missing minute represented honestly? Never fill a closed market with fictitious zero-return minute bars and describe them as observations.
- Are within-hour features constructed from only the finished hour, not from its later daily high, close, or full-session volume?
- Does the minute input population match the hourly comparator, or did stricter data requirements remove difficult dates?

These checks extend HF20 §§5.9 and 8; they do not authorize new downloads or invent missing source fields. The existing high fallback exposure is a reason to inspect minute inputs more carefully, not to assume that finer resolution is cleaner.

### 5.5 Lowest-cost discriminating comparison

Hold fixed the stock set, permitted dates, outcome horizon, forecast origins, and ranking objective. Compare hourly information with one carefully defined intrahour representation. Test the representation first through a simple score model where practical, then through the LSTM if evidence warrants it.

The failed A2 experiment used multiscale processing of the supplied hourly representation. It did not test whether minute detail discarded before feature construction contains useful information. Conversely, A2's negative result is not a reason to relabel another hourly average as a genuinely new minute-data experiment. [HF20, §3.3]

---

<a id="horizons"></a>

## 6. Beyond two morning origins: interday outcomes and variable hours

### 6.1 More forecast origins are not automatically more trades

We can investigate rankings at additional completed-hour endpoints while making no trading decisions. This broadens the prediction sample and lets us test whether information differs by time of day. The statistical evaluation must retain all forecasts according to the declared sampling rule, rather than pretending overlapping predictions are independently funded positions.

More origins also change the distribution of observations. A model that improves after adding afternoon origins may benefit from a different task or sample—not merely more training rows. Keep the current morning-origin slice as a separately reported anchor, and show the new-origin results separately.

Session-specific evidence in Heston et al. supports examining this question, not assuming any particular modern intraday effect. [S10]

### 6.2 Distinguish several outcome clocks

| Candidate outcome | What must be specified | Main interpretive issue |
|---|---|---|
| Next 1, 2, or 4 full trading hours within the same session | Endpoint, availability lag, early-close eligibility | Different horizons can retain different origins |
| Current-session remainder | Exact endpoint and remaining duration | The horizon varies systematically with origin time |
| Next-session same clock time | Trading calendar and complete overnight gap | Not the same as “24 trading hours” |
| Origin to next-session open or close | Actual open/close reference and price/action convention | Mixes intraday and overnight components in different proportions |
| A fixed number of sessions | Endpoint convention and intervening gaps/actions | More overlap and fewer independent outcome episodes |

These are a candidate menu, not a grid to run. Within an origin/horizon comparison, every stock must be ranked on the same interval. Comparing one stock's one-hour outcome with another stock's next-day outcome is not an ordinary cross-sectional ranking task.

The current all-four-hour, no-overnight setup is a design choice. It is not a requirement imposed by the LSTM. [HF20, §§2.3, 7.4]

### 6.3 Interday outcomes deserve separate component diagnostics

For properly defined close \(C_d\) and next open \(O_{d+1}\), log returns admit the identity

\[
\log\frac{P_{e}}{P_b}
=
\log\frac{C_d}{P_b}
+\log\frac{O_{d+1}}{C_d}
+\log\frac{P_e}{O_{d+1}}.
\]

The three terms describe the remaining day, overnight gap, and following-session segment. This is an accounting identity, not a claim that separately forecasting their ranks and adding those ranks yields the total-return rank—it generally does not.

Lou, Polk, and Skouras document distinct overnight/intraday continuation and cross-period patterns. Hendershott, Livdan, and Rösch document different day/night relationships with beta. These are strong reasons not to assume a longer holding interval is just more of the same process. They do not show that overnight forecasting is easier for HF20. [S12] [S13]

The original source contract's 15:30 daily-close surrogate is especially relevant. A 15:30-to-next-open return contains the final regular-session half-hour as well as the overnight gap. Do not call it a pure close-to-open return. Actual closing/opening observations, price adjustments, distributions, and label maturity must be verified for any new interday outcome. A declared surrogate could be a research target, but it needs an honest name.

Portfolio borrow, overnight funding, and realized fills remain deferred. Causal price definitions and corporate-action consistency do not: they determine whether the new ranking labels are meaningful.

### 6.4 “Variable hours” has three different meanings

**Separate fixed-horizon tasks.** Compare a small prespecified set of \(h\), initially using the current morning origins where feasible. This is the cleanest first test of horizon dependence.

**A horizon-conditioned predictor.** Supply the requested horizon to a shared model,

\[
s_{i,t,h}=f_\theta(X_{i,\le t},h,\text{known calendar context}).
\]

Alternatively, use separate readout heads for the approved horizons. Both are legitimate proposals. Multi-horizon fitting can share information or cause negative transfer; it is not automatically more efficient statistically. Record each horizon's performance separately and compare against a single-horizon reference before attributing a benefit.

**Choosing a horizon adaptively.** Selecting how long to hold based on the current state or predicted future path is a later policy problem. Selecting the horizon with the best realized future return is hindsight. For now, ask whether a model can rank at known requested horizons; do not add an adaptive exit policy.

For a multi-horizon supervised loss, a possible normalization is

\[
L=\frac1{|\mathcal H|}\sum_{h\in\mathcal H}L_h,
\]

with each \(L_h\) already normalized over its approved sessions, origins, and valid cross-section. This defines an explicit weighting choice. Missing horizons, differing origin support, and several labels for the same stock-time must not silently change weights. It is not an instruction to fit all horizons now.

### 6.5 Purging and chronology become more demanding

An example belongs in a fitting set only when its complete outcome is permitted and matured by the fitting cutoff. For multiple horizons, apply the rule to each supervised head and the relevant longest label reach. The original 48-step embargo is not a substitute for checking actual endpoint and availability timestamps after the horizon changes.

Overlapping outcomes, common overnight gaps, and repeated stock cross-sections remain dependent. More hourly forecast rows do not create more independent overnight shocks. Resampling must keep the dependent date/origin panels together, with block-length sensitivity appropriate to the new horizon.

Any label reaching into the protected 2026 period remains unavailable during this research stage. Do not use it even when the forecast origin was in late 2025.

---

## 7. Combining minute detail with interday outcomes

The combination is coherent: recent minute paths may describe the state at issuance, while slower hourly/daily inputs describe longer-lived context. Whether either predicts the subsequent interday order is unknown.

A useful conceptual separation is:

| | Existing four-hour outcome | One precisely specified interday outcome |
|---|---|---|
| Existing hourly inputs | Archived reference or properly matched refit | Is the outcome horizon the limitation? |
| Minute-informed hourly representation | Does intrahour information add value at the current horizon? | Is there an interaction between finer inputs and a longer outcome? |

This is an **attribution map**, not authorization for four new models. Depending on the diagnostic evidence, only one contrast may be worth testing first. The combined corner should not be the sole comparison against old T2, because input resolution and outcome horizon would both have changed.

An important possibility is that minute detail helps a nearby horizon but becomes irrelevant for an overnight gap driven by new information. Another is that recent activity interacts with slower state and matters for the next session. Both are hypotheses. Neither follows from high-frequency predictive papers with different information sets.

The minute-aware model should retain the necessary slow context. Replacing a 48-hour history with only the latest 60 minute observations would confound finer resolution with a drastically shorter lookback.

---

<a id="magnitude"></a>

## 8. Can predicting magnitude become a useful signal?

### 8.1 Define “magnitude” before developing it

These are different outcomes:

\[
E[|R^{(h)}|\mid\mathcal F_t],\quad
E[(R^{(h)})^2\mid\mathcal F_t],\quad
E[\mathrm{RV}^{(h)}\mid\mathcal F_t],\quad
P(|Y^{(h)}|>c\mid\mathcal F_t),\quad
Q_\alpha(Y^{(h)}\mid\mathcal F_t).
\]

Absolute endpoint movement, squared endpoint movement, realized path variation, a normalized tail event, and a quantile are not interchangeable. A path can move substantially and end near its start. TG20 magnitude is also relative and normalized; it is not absolute stock-return volatility.

E1/QR1 provide motivation to preserve distributional research. Their existing results should not be relabeled as success at every outcome above. [HF20, §§3.2, 7.5]

### 8.2 Magnitude alone supplies no direction in an important counterexample

Suppose

\[
R_i=\sigma_i\varepsilon_i,
\]

where the conditional joint distribution of \(\varepsilon\) is centrally symmetric and every pairwise return difference has no atom at zero. Even if every \(\sigma_i\) is perfectly predictable,

\[
P(R_i>R_j\mid\mathcal F_t)=\tfrac12
\]

for every pair under these assumptions, because each difference is symmetric around zero. Expected ranks are therefore the same. Selecting a high-volatility stock as long and a low-volatility stock as short does not acquire an expected directional advantage from this scale information alone.

Conversely, a zero conditional mean does not by itself rule out good ranking: a stock with return +1 with probability 0.99 and −99 otherwise has mean zero but beats a constant-zero comparator 99% of the time. Distribution asymmetry matters. These examples explain why mean, magnitude, event probabilities, and ranking must be kept distinct.

### 8.3 Three legitimate roles for magnitude

**A separate forecast product.** Accurately forecasting risk or tail exposure can be valuable even when signed ranks are weak. This is a different task, not evidence that the main ranking objective has been solved.

**An input or auxiliary target for ranking.** A causally generated magnitude forecast might condition a directional relationship, or auxiliary supervision might improve the representation. It may also distract a shared encoder by emphasizing an easier task. Demonstrate incremental ranking value against the same signed model and simple risk features before combining branches.

**Later risk management or selection.** A calibrated risk forecast can inform exposure, confidence, or whether a separately established directional forecast is worth using. Moreira and Muir provide evidence for volatility-managed portfolios in their factor setting. That supports potential economic usefulness of risk forecasts, not a directional signal for our stocks or permission to build a portfolio now. [S17]

### 8.4 What to test before claiming a magnitude-based improvement

Compare a proposed magnitude model with appropriate simple controls: a training-only stock/group scale, trailing absolute return or variance, and—when the outcome really is realized volatility—a suitably constructed multi-horizon volatility baseline. Corsi's HAR-RV is a primary reference for the latter, not a universal baseline for every definition of magnitude. [S18]

Evaluate the actual quantity with an appropriate score and calibration check. For probabilities use discrimination and proper probability scores; for quantiles use pinball and conditional coverage. Aggregate interval coverage alone can conceal poor conditional behavior. [S19]

To ask whether the forecast improves ranking, form historical out-of-fold or genuinely prequential magnitude predictions. Do not give a second-stage ranker optimistic in-sample predictions from a model fitted on the same labels. Keep actual future magnitude as a label or diagnostic only.

For a signed decomposition, define

\[
p_+=P(R>0\mid\mathcal F),\quad p_-=P(R<0\mid\mathcal F),
\]

\[
a_+=E[|R|\mid R>0,\mathcal F],\quad
a_-=E[|R|\mid R<0,\mathcal F].
\]

Then

\[
E[R\mid\mathcal F]=p_+a_+-p_-a_-.
\]

This identity shows what is missing when only unconditional magnitude is predicted. DM1 already attempted a related direction/magnitude decomposition and did not improve the signed task. A new variant needs new evidence, not merely this identity. [HF20, §3.2]

**Disposition:** preserve magnitude research, but do not let it replace the primary ranking question or automatically fuse T2, E1, and QR1.

---

<a id="dropout-audit"></a>

## 9. Audit of “stronger dropout, without asinh, to prevent clipping and get E[Y|X]”

I interpret **“heavy dropping” as stronger neural dropout**, not deleting extreme outcomes. No observation deletion, winsorization, or dropout rate is approved by that interpretation. The exact intended meaning must be confirmed before any implementation.

### 9.1 Dropout and gradient clipping solve different problems

Dropout is a regularization technique. Gradient-norm clipping limits the size of an update's gradient vector when it exceeds a threshold. Neither implies the other. The original dropout work and the recurrent-gradient analysis motivate these distinct uses. [S14] [S16]

For original-target squared loss,

\[
\nabla_\theta(Y-f_\theta(X))^2
=2(f_\theta(X)-Y)\nabla_\theta f_\theta(X).
\]

Changing dropout does not remove the large-residual factor. It also does not guarantee a smaller network Jacobian. Inverted dropout increases retained activations by the reciprocal of the keep probability; stronger dropout can increase stochastic variability rather than eliminate gradient spikes.

Current P028 clipping is rare in calibration and zero in refit. That is counterevidence to “clipping is the current bottleneck,” although raw-target C0 had different gradient behavior and must be assessed in its own objective. [HF20, §5.8; P028-G]

### 9.2 A derivation directly relevant to the present final-head dropout

Condition on a hidden vector \(h\), with a linear head and independent dropout masks \(B_j\sim\mathrm{Bernoulli}(\kappa)\), where \(\kappa\) is the keep probability. The training output is

\[
f_B=b+\sum_j w_j h_j B_j/\kappa.
\]

Then

\[
E_B[(Y-f_B)^2\mid h,Y]
=(Y-b-w^\top h)^2+
\frac{1-\kappa}{\kappa}\sum_j(w_jh_j)^2.
\]

For this specific setup, increasing dropout adds a larger penalty on readout contributions. This can be useful regularization, but it can also encourage more conservative outputs. It is not a proof that dropout always shrinks every fitted prediction; it is a direct reason not to assume that heavier dropout will cure forecast compression.

The formula is a derivation for the current style of linear readout, not an empirical result attributed to the cited dropout papers. Recurrent dropout is a different design: the placement of masks and whether they are shared across time matter. Gal and Ghahramani's variational recurrent dropout uses a particular mask construction, evaluated on language/sentiment tasks, not this equity problem. [S15]

### 9.3 Removing asinh does not guarantee “the actual conditional expectation”

Unrestricted population minimization of original-target squared loss yields \(E[Y\mid X]\), assuming the required moment exists. Finite data, a restricted neural class, regularization, early stopping, nonstationarity, and imperfect optimization all prevent that identity from being an accuracy guarantee.

Furthermore, **\(E[\mathrm{TG20}\mid X]\) is not \(E[R\mid X]\)**. TG20 contains a random future cross-sectional median and denominator. Removing asinh only changes the nonlinear transformation layer; it does not convert TG20 to a raw-return expectation. [HF20, §§5.3–5.5]

A global, training-fitted positive constant rescaling of an untransformed target can change numerical units without changing its ideal mean functional after rescaling back. That is different from nonlinear transformation or stock-specific/future-outcome weighting. It still does not establish superior ranking, and changing units interacts with optimization settings.

### 9.4 Decision

**Do not prioritize this combined intervention now.** It changes both regularization and target loss, so any result would be hard to attribute. C0 already supplies adverse evidence for simply reverting to original TG20 MSE, and P024 did not establish a general regularization fix. Neither result rules out a specifically justified future dropout test, but there is no current basis for making it the main remedy.

If a later mean-oriented model demonstrably overfits, compare one predeclared regularization change under the same target and input before combining changes. If the immediate task is ranking, direct ranking objectives are the clearer first question. Keep clipping as a documented optimization safeguard rather than treating zero clipping as a success criterion.

---

<a id="diagnostic-workstreams"></a>

## 10. All seven HF20 §8 workstreams: ranking-first diagnostic specification

These workstreams are retained in full. The user's agreement establishes the intended diagnostic scope; this document is the research specification, not a claim that the repository work has been completed.

| HF20 §8.1 workstream | Concrete output now | Boundary |
|---|---|---|
| **1. Clock and outcome bridge** | Exact historical source endpoint → information availability → issuance → target start/end/maturity examples; record what changes for other hours and overnight outcomes | Keep causal forecast semantics. Defer fills, borrow, costs, sizing, and P&L. Preserve the historical price-only label as such. |
| **2. Same-observation loss attribution** | T2 versus A7/A12 and useful saved controls on identical original-target, numerator/MAD, sign, quality, and state cohorts; original and actual z-loss deltas and complements | Existing forecasts/labels only. A new label or missing model needs explicit scope; do not infer paired gains from separate cohort totals. |
| **3. Cross-sectional error decomposition** | Per-origin common-mean error and centered-vector error, then exact session weighting; pairwise concordance and retrieval alongside | Tests the A7/A12 explanation without fitting a new mean head or changing predictions. |
| **4. Fallback and source-quality audit** | Channel-level native/fallback/age distributions, chronology, causal availability of flags, minute versus hourly observed support, and missingness/outcome associations | Descriptive associations do not license retrospective deletion or establish a source defect. |
| **5. Objective contract** | Return interval, cross-section, rank/tie conventions, primary metric, candidate loss, stopping rule, and score units | Ranking is primary. Full trading optimization is deferred. New training settings still need a freeze. |
| **6. Baseline inventory** | Exact current-source models, information histories, labels, dates, fit rules, and available forecasts; identify missing ranking/risk controls | Inventory is not fitting. Do not substitute old five-stock ridge results for current HF20 evidence. |
| **7. Scaling readiness** | Model/data interfaces for variable valid panels, normalization, masks, storage, and comparison populations | Interface review only here: no ticker selection, target universe size, sector allocation, or download. |

For each output, require a status such as **verified observation**, **unresolved**, **not available**, or **proposal**. Missing evidence cannot be converted to PASS by repeating the intended design.

### 10.1 The A7/A12 question should be answered, not merely repeated

Using saved predictions and identical weights, compute

\[
\operatorname{MSE}_t
=(\bar Y_t-\overline{\widehat Y}_t)^2
+\frac1{N_t}\sum_i[(Y_{i,t}-\bar Y_t)
-(\widehat Y_{i,t}-\overline{\widehat Y}_t)]^2.
\]

Then compare both components and their candidate-minus-T2 differences across roles, periods, and target cohorts. If a gain is mostly common-level error reduction with no centered-rank improvement, that supports a limited interpretation of the apparent MSE gain. If it is concentrated in centered extreme observations, that is a different finding. If the differences are unstable, retain uncertainty.

Neither explanation can be read from calibration slopes or attention plots alone. Do not fit a new intercept/scale on development to make the explanation look better.

### 10.2 Do not overinterpret the existing tails

P028's largest 5% of original absolute targets contribute approximately 24% of refit z-loss; most z-loss lies outside that cohort. Small-MAD-only and high-numerator-only cohorts are distinct, and neither is automatically the top-target cohort. Empty `MAD <= epsilon` observations reject one simple floor-dominance story, not all effects of denominator variation. [P028-T]

Preserve target-ranked, error-ranked, and training-frozen event thresholds as separate diagnostics. Compute loss differences, not only loss shares: two models can have nearly identical shares but different absolute errors. A quarter of the loss does not imply a quarter of the gradient norm or of the forecasting opportunity.

---

<a id="information-tests"></a>

## 11. How to investigate “weak conditional information” rather than merely speculate

The root-cause row in HF20 §6 needs to become a sequence of discriminating tests. Under the revised goal, ask specifically about **conditional ordering information** as well as signed-return means.

### 11.1 Start with a bounded evidence ladder

**Step A — Inventory and audit the existing observations.** Verify that every feature and label is available at the stated time, and identify source/fallback/clock ambiguities. Reuse the agreed §8 dossier.

**Step B — Inspect conditional associations without pretending they prove forecasting skill.** For a small predeclared set of feature families, examine within-origin feature ranks versus future return ranks, and conditional curves/bins. Fit thresholds or bin boundaries on permitted training history; evaluate later periods separately. Include a few justified interactions such as state × momentum only when the question is explicit. Zero marginal correlation does not rule out interactions.

**Step C — Fit strong simple ranking controls only when separately authorized.** Use the same full history/information that the LSTM sees. A 48×16 flattened lag vector has 768 components; a regularized score is feasible as a conceptual baseline, but its tuning and computation still require a bounded plan. A sparse-lag alternative is cheaper but must be labeled as having less information.

Candidate controls are a regularized linear predictor of normalized rank, a linear pairwise score, and at most one compact nonlinear nonrecurrent model. They are not a mandate to run a large tree/MLP search. Gu, Kelly, and Xiu motivate testing nonlinear interactions and strong comparators in financial prediction, but their monthly asset-pricing results do not establish intraday ranking signal here. [S21]

**Step D — Compare the simple controls and LSTM across actual chronological folds.** Freeze the information set, targets, cutoffs, and limited tuning rules before fitting. A family that improves only on the familiar 2025 window is not a prolonged-period result.

**Step E — Only then choose a targeted remedy.** A changed input, horizon, objective, or training interface should answer the detected limitation; it should not be selected merely because another candidate is available.

### 11.2 What outcomes would mean

| Observation | Supported interpretation | Next discriminating action |
|---|---|---|
| Simple same-information ranker is stable; LSTM is not | Available ordering structure is not being exploited as well by the tested LSTM | Check objective, historical reach, regularization, temporal credit assignment, and train/validation lifecycle |
| Linear model is weak; small nonlinear control is stable | Interactions/nonlinearity may matter | Give the LSTM comparable context and assess whether its representation can express the relevant dependence |
| Original FT16 controls are weak; minute-informed controls improve at fixed horizon | Aggregation/representation is a plausible limitation | Validate minute data and test one matched LSTM representation change |
| Current horizon is weak; a prespecified alternative is more stable | Task timescale may be poorly matched | Replicate that horizon comparison without changing every other choice |
| Skill appears only in certain eras | Nonstationarity is plausible | Review a small, predeclared window/refresh comparison; do not pick the best era retroactively |
| Quality-only or historical stock-profile scores explain much of the result | The model may exploit source/identity structure rather than useful dynamic information | Check causal availability and temporal robustness; separate static and dynamic contributions |
| All tested models are weak with broad uncertainty | No demonstrated accessible ordering information under the tested setup | Do not conclude impossibility; avoid an indefinite 20-stock search and retain the larger-panel direction |

The data cannot establish a finite universal “information ceiling” from the failure of a few models. Conversely, successful synthetic tasks and healthy gradients cannot establish that market information exists.

### 11.3 Information controls must match the claim

A market-aware LSTM should be compared with a plain predictor receiving the same market history. A minute encoder should be compared with a suitable minute-informed simple representation—not only a model denied all minute information. A full-peer network needs a richer control than two peer averages for an architecture-only claim.

Where an adequate control is unaffordable, a combined information-plus-architecture comparison is still reportable, as in P027/P028. Label that limitation instead of claiming clean mechanism identification.

### 11.4 Nonstationarity is a candidate, not a reason to throw away old data

A fixed model may pool inconsistent relationships across many years. A recent-window model may adapt better or simply overfit a smaller sample. Keep the historical expanding-window reference and evaluate any recent-window alternative at identical forecast dates under a small predeclared design. HF20 §5.10 already describes this bias–variance question; it should not become an unrestricted retraining-frequency search.

---

## 12. What “reliable ranking over prolonged periods” should require

A larger or more detailed feature tensor does not make the evaluation period longer. The familiar 109 development sessions remain exploratory.

A future evaluation specification should include:

- **Several nonoverlapping chronological outer periods** within permitted history, each predicted by a model fitted only on earlier matured outcomes, with its own correctly fitted preprocessing and inner selection.
- **Paired model comparisons** on the same origin-stock sets; per-fold daily IC, pairwise accuracy, and retrieval measures, alongside aggregate results.
- **Matched seed replication for shortlisted neural comparisons**, reporting all selected seeds rather than choosing the best baseline/treatment combination.
- **Performance concentration and stability:** contributions by month, origin slot, stock, state, source-quality stratum, and horizon; evaluate whether the result disappears outside one narrow cohort.
- **Dependence-aware uncertainty** retaining entire cross-sections and related sessions. Overlapping returns and stock pairs are not independent trials.
- **A clearly protected final period**, not inspected to choose loss, horizon, input resolution, or missingness thresholds.

**Critical distinction:** slicing the historical predictions of a model refitted through June 2025 into earlier years does not produce out-of-sample historical folds. Those years were in its fitting data. Genuine chronological evaluations require the appropriate earlier-cutoff fits or existing valid issued forecasts.

Likewise, a retrospective walk-forward devised after studying later results is useful robustness evidence but not a pristine prospective experiment. Repeated data reuse and specification search change inference; White's framework is a foundational reference for this issue, not a blanket validation of any chosen bootstrap. [S22]

“Stable ranking” also does not mean the predicted order should never change. An almost fixed stock ranking can look stable while contributing little time-varying information. Compare against historical stock-profile scores and distinguish **stable predictive performance** from **unchanging predictions**.

Before fitting, decide how fold performance will be aggregated and what material improvement would justify replication. No universal IC cutoff or arbitrary fraction of positive folds is established here. A confidence interval from six heavily reused months cannot certify prolonged robustness, regardless of the number of bootstrap draws.

---

## 13. Preserve HF20 §12 and extend it for ranking, minute inputs, and new horizons

### 13.1 Existing return-regression models retain the full contract

For T2 and the completed return-score models, keep the original untransformed targets and their operands, transformed targets, predictions, once-only inverse, both error spaces, exact session/origin weights, and four role identities. Preserve all original tail, numerator/MAD, source-case, gradient, mechanism, checkpoint, and protected-data requirements. No headline IC table replaces them. [HF20, §12; P028-T; P028-G]

### 13.2 Pure ranking models need truthful score units

For a new ranking model, retain original returns/TG20 as **outcomes and cohort definitions**. Add realized ranks, predicted scores/ranks, ties, score margins, and the actual ranking objective.

Do not invent original-return or asinh prediction errors when the model does not output a return estimate. Mark those errors **not applicable to an uncalibrated rank score**. A separately fitted return calibration map is a new model component requiring proper historical fitting and later evaluation, not a reporting trick.

This is a necessary adaptation of §12, not relaxation of the detailed diagnostics. On each original-target extreme cohort, still report ranking error, concordance, event-direction or selection diagnostics where defined, and actual objective contributions.

### 13.3 Pairwise loss attribution needs an explicit accounting rule

Pairwise losses involve two stocks. A possible exact allocation is

\[
a_{i,t}=\frac1{2|\mathcal P_t|}
\sum_{j:(i,j)\ \text{or}\ (j,i)\in\mathcal P_t}\ell_{ij,t},
\qquad
\sum_i a_{i,t}=L_{\mathrm{pair},t}.
\]

Then original-outcome cohorts can sum the allocated shares without counting each pair twice. Alternatively, classify pairs by both endpoints' cohorts; state the convention and reconcile the total. Listwise losses also need a specified allocation or a genuinely list-level report—do not fabricate additive stock attribution for a nonadditive quantity.

For rank-regression, attribution is pointwise and simpler. In every case distinguish actual optimized loss from original-return error and from diagnostic tail selection.

### 13.4 New input and horizon checks

Minute-aware models require reconstruction of which minute observations formed every hourly representation, their valid-data masks, source times, and any within-hour statistics. Interday targets require actual session boundaries, opening/closing references, gaps, corporate-action conventions, and endpoint availability.

Multi-horizon models need validity counts, purges, loss weights, and outcome components **per horizon**. A missing long-horizon label must not silently invalidate an otherwise usable short-horizon prediction or admit a future-derived input flag.

### 13.5 Rank stability and temporal learning diagnostics

Report score margins, tie/constant rates, and the size of rank changes under bounded input perturbations. Changing at least one rank at every origin is not itself meaningful evidence, especially when scores are close.

Where justified, inspect the sensitivity to earlier versus recent history on fixed cases. Maintain exact training versus evaluation-mode distinctions. Nonzero global gradient norms do not prove that useful early-sequence information is learned; donor shifts and shuffles are distribution perturbations, not automatic causal or permutation tests.

The final diagnostic output should identify the smallest supported explanation and its competing alternatives. A negative result can be complete and useful without an automatic rescue.

---

<a id="next-decisions"></a>

## 14. Focused next-decision plan

### Phase A — Complete the agreed diagnostics on HF20

Complete all seven workstreams in Section 10, using the existing approved data and evidence where possible. Close with a concise decision record separating verified issues, unresolved but nonblocking issues, and proposed experiments. Trading work and stock selection remain outside this pass.

### Phase B — Freeze the ranking-first research contract

Specify the main return interval and ranking labels; future-information boundary; daily/origin weighting; primary metric; tie conventions; one or two candidate objectives; baseline information sets; stopping rules; temporal validation; and diagnostic extensions.

The main new mathematical conclusion is that **we can investigate ranking directly without first recovering a calibrated original-return mean or solving the inverse-asinh problem**. Preserve T2 as a benchmark, not as the only legitimate output interpretation.

### Phase C — Decide whether one fundamental small-universe comparison is justified

Three kinds of evidence would justify a bounded 20-stock proof before a larger study:

1. A verified source/clock/input ambiguity needs a controlled repair.
2. A strong simple ranking model reveals structure that the LSTM or its current objective misses.
3. The ranking loss or minute-to-hour interface needs a compact scientific/engineering validation before scaling.

A pure ranking comparison is now a stronger candidate than heavy dropout plus raw MSE because it directly changes the quantity being learned. But choosing a candidate for a proposal is not authorizing a run. Do not turn this into all losses × all horizons × all resolutions × all old architectures.

### Phase D — Order the remaining hypotheses by what the evidence says

| Evidence after the diagnostics | Most focused follow-up candidate |
|---|---|
| Objective mismatch remains the clearest issue | Simple direct-ranking control and matched LSTM |
| Frequent causal fallback/age ambiguity | Minimal quality/time representation, holding target/loss fixed |
| Hourly summaries discard relevant information | One minute-informed hourly representation, holding horizon/origins fixed |
| Ranking strength changes by prespecified horizon | A small fixed-horizon comparison before multi-horizon routing |
| Overnight and intraday behavior differ materially | An explicitly defined interday target and component diagnosis |
| Risk/outer-quantile information is clearer than signed order | Separate magnitude calibration/benchmarking; no automatic fusion |
| No specific small-panel remedy is supported | Stop extending the HF20 search; carry the lessons into the separately planned broader universe |

The expanded-universe task remains a future prompt. No stocks, counts, sector allocations, or new source are selected here.

### Bottom line

**The priority is ranking-first task alignment and information diagnosis, not stronger output amplitudes or another recurrent-cell design.** Minute detail and interday outcomes are serious candidates, but they must be tested as separate choices before their combination is credited. Magnitude may be useful without supplying a directional ranking. Stronger dropout is not a mathematical replacement for asinh or gradient clipping.

The immediate diagnostic work should tell us which of these possibilities has concrete support. It is not a requirement to make the 20-stock study succeed before moving on.

---

<a id="references"></a>

## 15. Literature: sources, relevance, and limits

This is a focused methodological review, not an exhaustive stock-prediction meta-analysis. References were checked through primary publisher, conference, author, or institutional records. Full accessible HTML was used where available; otherwise the cited evidence is limited to the publication record/abstract. No external backtest was replicated. Performance claims from another market, frequency, or information set are not forecasts for HF20.

### Ranking and statistical objectives

**S01 — Gneiting, T. (2011).** *Making and Evaluating Point Forecasts.* Journal of the American Statistical Association, 106(494), 746–762. [Publisher/DOI](https://doi.org/10.1198/jasa.2011.r10138).  
Use: match the loss to the statistical functional. The expected-rank/Spearman argument in this addendum is a direct derivation, not an empirical claim from this paper.

**S02 — Burges, C. J. C., et al. (2005).** *Learning to Rank Using Gradient Descent.* ICML, 89–96. [Microsoft Research](https://www.microsoft.com/en-us/research/publication/learning-to-rank-using-gradient-descent/); [DOI](https://doi.org/10.1145/1102351.1102363).  
Use: RankNet's probabilistic pairwise loss. Its search-ranking experiments do not establish financial predictive skill.

**S03 — Cao, Z., Qin, T., Liu, T.-Y., Tsai, M.-F., and Li, H. (2007).** *Learning to Rank: From Pairwise Approach to Listwise Approach.* ICML, 129–136. [Microsoft Research](https://www.microsoft.com/en-us/research/publication/learning-to-rank-from-pairwise-approach-to-listwise-approach/); [DOI](https://doi.org/10.1145/1273496.1273513).  
Use: ListNet/listwise construction. Target probability mappings require deliberate financial-task adaptation.

**S04 — Xia, F., Liu, T.-Y., Wang, J., Zhang, W., and Li, H. (2008).** *Listwise Approach to Learning to Rank: Theory and Algorithm.* ICML, 1192–1199. [ACM/DOI](https://doi.org/10.1145/1390156.1390306).  
Use: ListMLE as a permutation-likelihood alternative. Do not assume equivalence to the HF20 Spearman criterion.

**S05 — Blondel, M., Teboul, O., Berthet, Q., and Djolonga, J. (2020).** *Fast Differentiable Sorting and Ranking.* ICML, PMLR 119, 950–959. [Official proceedings](https://proceedings.mlr.press/v119/blondel20a.html).  
Use: differentiable ranking and a Spearman application. A smoothing-based training objective remains a surrogate with implementation choices.

**S06 — Poh, D., Lim, B., Zohren, S., and Roberts, S. (2020 manuscript).** *Building Cross-Sectional Systematic Strategies by Learning to Rank.* [Author manuscript](https://arxiv.org/abs/2012.07149); [full HTML](https://arxiv.org/html/2012.07149); [Oxford publication record](https://ora.ox.ac.uk/objects/uuid:08cdf48f-dd90-473b-a529-b4fdb5ff4717).  
Use: a finance-specific comparison of pairwise/listwise and regress-then-rank approaches. The inspected manuscript uses monthly cross-sectional momentum; do not transfer reported performance to four-hour HF20.

**S07 — Feng, F., He, X., Wang, X., Luo, C., Liu, Y., and Chua, T.-S. (2019).** *Temporal Relational Ranking for Stock Prediction.* ACM Transactions on Information Systems, 37(2), Article 27. [Author manuscript](https://arxiv.org/abs/1809.09441); [full HTML](https://arxiv.org/html/1809.09441); [DOI](https://doi.org/10.1145/3309547).  
Use: temporal stock representations with a ranking-oriented objective and relational information. Not a reason to rerun peer architectures or claim pure-ranking superiority without a matched test.

### Information representation and timing

**S08 — Che, Z., Purushotham, S., Cho, K., Sontag, D., and Liu, Y. (2018).** *Recurrent Neural Networks for Multivariate Time Series with Missing Values.* Scientific Reports, 8, 6085. [Full article](https://www.nature.com/articles/s41598-018-24271-9).  
Use: distinguish values, masks, and time since observation. The source application is clinical, not financial.

**S09 — Jiang, J., Kelly, B., and Xiu, D. (2023).** *(Re-)Imag(in)ing Price Trends.* Journal of Finance, 78(6), 3193–3249. [Publisher](https://doi.org/10.1111/jofi.13268); [Yale record](https://economics.yale.edu/research/re-imagining-price-trends).  
Use: investigate representation of price paths rather than assume traditional indicator summaries are sufficient. Does not imply image inputs are necessary here.

**S10 — Heston, S. L., Korajczyk, R. A., and Sadka, R. (2010).** *Intraday Patterns in the Cross-section of Stock Returns.* Journal of Finance, 65(4), 1369–1407. [Publisher](https://doi.org/10.1111/j.1540-6261.2010.01573.x); [Northwestern record](https://www.kellogg.northwestern.edu/academics-research/research/detail/2010/intraday-patterns-in-the-cross-section-of-stock-returns/).  
Use: session-specific patterns warrant a timing audit. Their historical observations are not established effects in our data.

**S11 — Huddleston, D., Liu, F., and Stentoft, L. (2023; online 2021).** *Intraday Market Predictability: A Machine Learning Approach.* Journal of Financial Econometrics, 21(2), 485–527. [Publisher](https://academic.oup.com/jfec/article-abstract/21/2/485/6400345); [DOI](https://doi.org/10.1093/jjfinec/nbab007).  
Use: five-minute constituent histories can contain information not summarized by an aggregate series in their study. Aggregate-market prediction is not cross-sectional stock ranking.

**S12 — Lou, D., Polk, C., and Skouras, S. (2019).** *A Tug of War: Overnight versus Intraday Expected Returns.* Journal of Financial Economics, 134(1), 192–213. [DOI](https://doi.org/10.1016/j.jfineco.2019.03.011); [author research page](https://personal.lse.ac.uk/polk/research/work.htm).  
Use: overnight and intraday outcomes may have different structure. This does not make interday holding or prediction automatically superior.

**S13 — Hendershott, T., Livdan, D., and Rösch, D. (2020).** *Asset Pricing: A Tale of Night and Day.* Journal of Financial Economics, 138(3), 635–662. [DOI](https://doi.org/10.1016/j.jfineco.2020.06.006); [author-institution record](https://researchconnect.buffalo.edu/en/publications/asset-pricing-a-tale-of-night-and-day/).  
Use: economic exposure can relate differently to day/night outcomes. Not a ready-made HF20 predictor.

### Regularization, gradients, and magnitude

**S14 — Srivastava, N., Hinton, G., Krizhevsky, A., Sutskever, I., and Salakhutdinov, R. (2014).** *Dropout: A Simple Way to Prevent Neural Networks from Overfitting.* JMLR, 15, 1929–1958. [Official article](https://jmlr.org/papers/v15/srivastava14a.html).  
Use: regularization through dropout. The linear-readout penalty equation in this report is a separate derivation; the paper does not establish that larger dropout prevents clipped return gradients.

**S15 — Gal, Y., and Ghahramani, Z. (2016).** *A Theoretically Grounded Application of Dropout in Recurrent Neural Networks.* NeurIPS 29. [Official proceedings](https://papers.nips.cc/paper_files/paper/2016/hash/076a0c97d09cf1a0ec3e19c7f2529f2b-Abstract.html); [author manuscript](https://arxiv.org/abs/1512.05287).  
Use: recurrent dropout placement/mask structure matters. Language-model evidence does not prescribe a financial dropout rate.

**S16 — Pascanu, R., Mikolov, T., and Bengio, Y. (2013).** *On the Difficulty of Training Recurrent Neural Networks.* ICML, PMLR 28(3), 1310–1318. [Official proceedings](https://proceedings.mlr.press/v28/pascanu13.html).  
Use: exploding/vanishing gradients and norm clipping. Successful clipping is an optimization safeguard, not a forecasting objective.

**S17 — Moreira, A., and Muir, T. (2017).** *Volatility-Managed Portfolios.* Journal of Finance, 72(4), 1611–1644. [NBER record and published-version details](https://www.nber.org/papers/w22208).  
Use: volatility forecasts may have later economic value without being standalone directional alpha. Portfolio work is deferred here.

**S18 — Corsi, F. (2009).** *A Simple Approximate Long-Memory Model of Realized Volatility.* Journal of Financial Econometrics, 7(2), 174–196. [Publisher/DOI](https://doi.org/10.1093/jjfinec/nbp001).  
Use: a strong simple realized-volatility comparator when that is genuinely the outcome. It is not a model of the magnitude of every normalized endpoint return.

**S19 — Gneiting, T., and Raftery, A. E. (2007).** *Strictly Proper Scoring Rules, Prediction, and Estimation.* JASA, 102(477), 359–378. [Publisher/DOI](https://doi.org/10.1198/016214506000001437).  
Use: evaluate probability/distribution predictions using appropriate scores, not event-threshold calls from a mean score.

**S20 — Zhang, Z., Zohren, S., and Roberts, S. (2019).** *DeepLOB: Deep Convolutional Neural Networks for Limit Order Books.* IEEE Transactions on Signal Processing, 67(11), 3001–3012. [Author manuscript](https://arxiv.org/abs/1808.03668); [full HTML](https://arxiv.org/html/1808.03668).  
Use: learned high-frequency representation plus recurrence is a serious research direction. Minute OHLCV lacks the order-book information in this paper; its simplified trading illustration is not our economic evidence.

### Comparators and validation

**S21 — Gu, S., Kelly, B., and Xiu, D. (2020).** *Empirical Asset Pricing via Machine Learning.* Review of Financial Studies, 33(5), 2223–2273. [Publisher/DOI](https://doi.org/10.1093/rfs/hhaa009).  
Use: strong simple/nonlinear controls and predictor interactions. Monthly risk-premium evidence is not proof of intraday signal.

**S22 — White, H. (2000).** *A Reality Check for Data Snooping.* Econometrica, 68(5), 1097–1126. [Publisher/DOI](https://doi.org/10.1111/1468-0262.00152).  
Use: repeated specification search changes inference. The paper does not automatically certify a particular HF20 resampling design.

### Project sources used in this addendum

**HF20:** `HF20_LSTM_Comprehensive_Review_and_Expansion_Plan_2026-10-24.md`. Relevant sections: 2–3, 5.3–5.10, 6–8, 11–12. The present request changes the near-term role of §5.11 and §7's first row, without rewriting the prior evidence.

**P028-T:** `Pasted markdown (2)(7).md`, *P028 true transformed-objective tails*. Supplied complete four-role original-target cohorts and actual z-loss accounting.

**P028-G:** `Pasted markdown(20261024-135923).md`, *P028 complete fitting and gradient accounting*. Supplied calibration/refit update, gradient, and checkpoint summaries.

The latest user-pasted matched comparison and per-arm reports supply the A7/A8/A12 performance context. Exact current FT16 formula details beyond those documented in HF20 remain a repository-audit item; no missing formula, historical decision, or experiment result is invented here.

---

## Appendix A. Questions to freeze before the relevant implementation

These are decision fields, not requests to repeat the full earlier conversation.

| Question | Why it matters | Current state |
|---|---|---|
| Rank raw future returns, TG20 order, or individual-risk-adjusted returns? | The first two share ordering under the current common normalization; the third may not | Raw-return/TG20 order is the natural reference; final card pending |
| What does “hourly windows” mean operationally? | Latest-hour minute sequence versus minute detail in every hour of a longer history | Both analyzed; not selected |
| Which new horizon, if any? | Endpoint and overnight meaning determine the label | No new horizon authorized |
| What is the revised origin population? | More times change sample composition and dependence | Existing origins retained as anchor |
| Which rank loss and checkpoint monitor? | Return MSE and rank IC can prefer different fits | Recommended simple shortlist, not a numerical freeze |
| Does “heavy dropping” mean stronger dropout? | Must not turn an ambiguous suggestion into data deletion | Assumed for analysis only; confirm before execution |
| Which causal quality/timing fields actually exist? | Retrospective audit flags may not be usable live | To be established by §8 work |
| Which simple controls already exist on current data? | Avoid unnecessary fits and unfair comparisons | Baseline inventory pending |
| What demonstrates prolonged robustness? | Six reused months and repeated seeds are insufficient alone | Chronological protocol to be frozen |

## Appendix B. Decision summary to retain

**Adopted direction:** ranking first; eventual net economics later. All HF20 §8 diagnostics and §12 evidence requirements remain part of the intended work.

**Most useful new candidates:** direct rank-target/pairwise learning; minute information within hourly representations; separately specified horizons including interday outcomes; causal missingness/time context.

**Preserve separately:** E1/QR1 and magnitude forecasting; A4's information-compression limitation; A7/A12's MSE-versus-ordering question; the remaining architecture archive.

**Do not assume:** relative ranking is intrinsically easy; larger outputs are better; stronger dropout prevents clipping; inverse-asinh scores are expected returns; minute data are clean; overnight returns are easier; magnitude alone gives directional ranks; or one negative model proves no information exists.

**Operational boundary:** no new empirical run, no stock selection, no source download, no protected 2026 access, and no portfolio fitting was performed for this document. Ledger remains **62/200**.

[S01]: https://doi.org/10.1198/jasa.2011.r10138
[S02]: https://www.microsoft.com/en-us/research/publication/learning-to-rank-using-gradient-descent/
[S03]: https://www.microsoft.com/en-us/research/publication/learning-to-rank-from-pairwise-approach-to-listwise-approach/
[S04]: https://doi.org/10.1145/1390156.1390306
[S05]: https://proceedings.mlr.press/v119/blondel20a.html
[S06]: https://arxiv.org/html/2012.07149
[S07]: https://arxiv.org/html/1809.09441
[S08]: https://www.nature.com/articles/s41598-018-24271-9
[S09]: https://doi.org/10.1111/jofi.13268
[S10]: https://doi.org/10.1111/j.1540-6261.2010.01573.x
[S11]: https://academic.oup.com/jfec/article-abstract/21/2/485/6400345
[S12]: https://personal.lse.ac.uk/polk/research/work.htm
[S13]: https://researchconnect.buffalo.edu/en/publications/asset-pricing-a-tale-of-night-and-day/
[S14]: https://jmlr.org/papers/v15/srivastava14a.html
[S15]: https://papers.nips.cc/paper_files/paper/2016/hash/076a0c97d09cf1a0ec3e19c7f2529f2b-Abstract.html
[S16]: https://proceedings.mlr.press/v28/pascanu13.html
[S17]: https://www.nber.org/papers/w22208
[S18]: https://doi.org/10.1093/jjfinec/nbp001
[S19]: https://doi.org/10.1198/016214506000001437
[S20]: https://arxiv.org/html/1808.03668
[S21]: https://doi.org/10.1093/rfs/hhaa009
[S22]: https://doi.org/10.1111/1468-0262.00152
[P028-T]: #project-sources-used-in-this-addendum
[P028-G]: #project-sources-used-in-this-addendum
