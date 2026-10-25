# HF20 LSTM: Evidence Review, Fundamental Fixes, and Larger-Universe Development Plan

**Date:** 24 October 2026  
**Version:** 1.0 — research reassessment and planning record  
**Status:** All further fitting is paused. This document authorizes no experiment, data acquisition, ticker selection, source change, or confirmation access.  
**Research ledger:** **62/200**, unchanged.  
**Objective:** Develop a defensible LSTM-based equity trading system—not demonstrate a particular lead–lag, pairs-trading, attention, or regime mechanism.  
**Intended next major empirical step:** A carefully constructed larger S&P 500 universe, potentially approximately 200–300 stocks or another evidence-supported size. No securities are selected here.

**Navigation:** [Current evidence](#2-what-the-current-model-and-dataset-actually-are) · [Experiment inventory](#3-complete-experiment-inventory-and-what-each-result-supports) · [Twenty-stock adequacy](#4-are-twenty-stocks-genuinely-enough-what-the-literature-permits-us-to-conclude) · [Diagnosis](#5-what-plausibly-went-wrongand-what-has-not-been-demonstrated) · [Before expansion](#8-what-is-worth-doing-on-twenty-stocks-before-expansion) · [Universe design](#9-designing-the-expanded-sp-500-universe-without-selecting-it-now) · [Staged plan](#10-the-staged-development-plan-after-the-pause) · [References](#15-research-references-and-reading-priorities)

---

## Executive decision

**My recommendation is to stop the open-ended search for architectural improvements on the present 20 stocks. Preserve HF20 as an engineering and diagnostic reference, resolve a short list of fundamental design questions, and then make universe expansion the next major empirical step.**

The literature does **not** establish that 20 stocks are inherently insufficient for an LSTM. Nor does the current evidence establish that insufficient stock count caused our disappointing results. A compact shared model can be estimated from 20 series; whether it learns useful trading signals depends on the information in those series, the prediction task, the sampling clock, stability across time, and evaluation. Larger panels offer a stronger setting for broad cross-sectional research, but cannot create conditional-return information that the inputs do not contain. [R01] [R02] [R03]

The strongest findings of this reassessment are:

1. **The near-zero outputs are a symptom to interpret, not an error to mechanically remove.** A conditional-mean forecast should usually be much less variable than realized returns. Raising forecast amplitude, eliminating regularization, or increasing extreme-event calls is not itself progress.
2. **There is a fundamental distinction between our trained objective and the economic quantity we sometimes attribute to it.** T2 estimates a transformed-target regression function. Applying `s*sinh` once is the correct numerical inverse, but does not generally turn a conditional mean in transformed space into the conditional mean of the original return target.
3. **The tails remain difficult, but the actual transformed objective is not dominated by one or two catastrophic observations.** Approximately 24% of refit z-loss lies in the largest 5% of original absolute targets; approximately 76% lies elsewhere. Large-numerator observations contribute much more disproportionate loss than the small-MAD-only group. This weakens the case for another generic tail-suppression experiment. [P09]
4. **Current source and representation conventions deserve more attention before scaling.** The recovered P020 record documents substantial volume-feature fallback, a 15:30 daily-close surrogate, incomplete volume assumptions, and price-only forecast labels beginning at the feature endpoint rather than an executable post-issuance entry. These are disclosed research conventions, not newly demonstrated bugs. Their consequences must not be multiplied unnoticed in a larger trading study. [P01]
5. **The evidence base is much narrower than “15 years × 20 stocks” suggests.** The current development comparison comprises 109 repeatedly inspected sessions. Expanding to more stocks does not create new independent market dates or erase that reuse.
6. **No completed architecture has established a robust improvement over the selected T2 reference.** A7 and A12 deserve preservation as metric-trade-off hypotheses, not promotion; A4–A6 deserve reconsideration after expansion with better controls. A9–A11 have not been run and are now paused—not failed. [P02]–[P10]

**Default path:** limited read-only diagnosis and scalability preparation → larger, point-in-time-aware panel → a small set of strong, information-matched baselines and a simple shared LSTM → selective revisiting of the old hypotheses. A further 20-stock neural fit should require a specific fundamental reason, not merely an unspent budget or another plausible architecture.

---

## 1. Evidence, scope, and corrections to the working narrative

### 1.1 What this document is based on

Three evidence classes are kept separate throughout:

- **Project observations [Pxx]:** supplied Codex reports, uploaded diagnostics, and explicit decisions in this conversation. These document reported experiments; I have not independently rerun the repository or certified the vendor data.
- **External research [Rxx]:** primary papers, author/university records, official publication pages, and the official S&P methodology. A result in another dataset is motivation, not a performance forecast for HF20.
- **Derivations and proposed tests:** mathematical consequences of the stated model, or new research recommendations. They are not previously approved experiments or established causal explanations of HF20 performance.

Appendix C identifies the project evidence. Section 15 supplies the literature references, direct links, and their limitations. Where an earlier report was retrievable only through indexed excerpts, that is disclosed. No missing experiment outcome has been reconstructed from a plausible story.

### 1.2 Decisions that supersede previous plans

All additional runs—including the previously contemplated Experiment 4—are paused. The next phase is reassessment and planned universe expansion, not automatic completion of A9, A10, and A11. The original 10+3 list and A1–A12 menu remain a research archive to revisit selectively.

Pairs trading and lead–lag were examples of relationships the user expected might appear. They are **not** mandatory objectives. Similarly, smoothing, residual modeling, selective trading, time-of-day features, and horizon changes are candidates requiring scrutiny; their repetition in earlier conversation does not give them higher evidential status.

### 1.3 Statements that need tightening

| Earlier shorthand | More defensible statement |
|---|---|
| “The zero-prediction problem improved because forecast SD rose.” | Forecast dispersion rose. Whether that is desirable depends on alignment, calibration, ranking, and economics. |
| “The model cannot predict extreme events because extreme recall is zero.” | Its point predictions never cross the specified realized-event thresholds. That does not by itself evaluate event probabilities or prove absence of tail-ranking information. |
| “We tried all twelve architectures.” | Nine candidates were screened: A1–A8 and A12. A9–A11 remain untested and paused. |
| “More history failed to help.” | Long-history results remain weak. A controlled same-source, same-task estimate of the effect of adding history has not been established here. |
| “Heavy tails dominate training.” | They disproportionately influence the objective, but most current asinh-z loss is outside the largest 5% of targets. Loss concentration is also not gradient concentration. |
| “TG20 is an idiosyncratic/factor-neutral return.” | It is median-centered and MAD-scaled within a chosen future cross-section. Heterogeneous market and sector exposures can remain. |
| “A7 tested independent market information.” | It used two endogenous, self-including panel summaries. No independent full-period market series was used. |
| “Engineering PASS proves the source and forecasting design are correct.” | It verifies specified implementation invariants under disclosed assumptions. Publication timing, rights, action vintage, survivorship, and scientific relevance remain separate issues. |
| “The 63-session validation tail is still the current rule.” | The current P020 contract uses 459 retained inner-validation sessions. The old five-stock rule is not the current HF20 chronology. |

These corrections matter: otherwise the next plan would be designed to solve problems we have not actually established.

---

## 2. What the current model and dataset actually are

### 2.1 Current chronology and sample—not the original five-stock proposal

The source-specific P020 preparation record is the most useful reference for the current long-history inputs. [P01]

| Role | Retained origins | Sessions | Stock-origin rows | Interpretation |
|---|---:|---:|---:|---|
| Inner training | 4,428 | 2,513 | 88,560 | Fits the calibration-pass parameters |
| Inner validation | 766 | 459 | 15,320 | Selects training duration; not untouched evidence |
| Full-prefix refit | 5,210 | 2,980 | 104,200 | In-sample fit after fresh initialization |
| Development | 183 | 109 | 3,660 | Repeatedly inspected exploratory comparison |

The nominal source starts in July 2010. Startup/warm-up runs through March 2011; the refit period is April 2011–June 2025. Inner training ends 23 January 2023; the retained validation starts 3 February 2023 after the prescribed 48-scheduled-hour embargo. Retained development is 15 July–31 December 2025. January–March 2026 numerical confirmation data remain protected. Older five-stock confirmation restrictions also remain intact. [P01]

This is approximately 14 years and three months of fitted history, not fifteen years of independent neural-training samples. Two morning origins, overlapping four-hour outcomes, recurring stocks, and rolling input windows create substantial dependence.

### 2.2 Inputs and prediction task

Each stock has a 48-step sequence of 16 engineered features: momentum/returns, volatility, range/bar state, volume/activity, and trend/technical information. Parameters are shared, but the baseline processes each stock separately. Forty-eight scheduled complete-hour slots are not 48 uninterrupted wall-clock hours. Some indicators summarize history well before the explicit window. [P01] [P02]

For origin \(t\), the current label is

\[
Y_{i,t}=\frac{R^{(4)}_{i,t}-m_t}{D_t+\epsilon},
\qquad
m_t=\operatorname{median}_{j\in\mathcal U_t}R^{(4)}_{j,t},
\qquad
D_t=\operatorname{median}_{j\in\mathcal U_t}|R^{(4)}_{j,t}-m_t|.
\]

The cross-section contains the fixed 20 names under the current complete-panel policy. The floor is fitted using permitted training data; future median/MAD values are outcome construction, never available input features. Price labels are not clipped. [P01]

T2 trains

\[
Z_{i,t}=\operatorname{asinh}(Y_{i,t}/s),\qquad
\widehat Y_{i,t}=s\sinh(\widehat Z_{i,t}).
\]

It uses one width-32 LSTM, a shared linear head, final-representation dropout of 0.1, and zero recurrent state at the beginning of every window. There are 6,433 baseline parameters. The loss averages stocks within origin, origins within session, and sessions equally. AdamW, clipping, and the fresh calibration/refit lifecycle are frozen for the completed comparisons. [P02]

**Three different goals coexist:** transformed MSE is optimized; original-target validation MSE chooses the epoch; cross-sectional ranking is central to promotion and intended trading. This is not automatically wrong, but it is not one consistent statistical objective.

### 2.3 Source conventions that affect the next stage

P020 documents several nontrivial compromises. The “daily close” is the 15:30 last-full-hour observation, not the official 16:00 close; daily feature volume omits the final stub. Some absent minute-volume observations are treated as zero for feature computation under the specified bounded-gap rule, while quality evidence is retained. Other missing feature values use existing training-fitted fallbacks. [P01]

Q2 fallback is approximately **21.68% in refit and 10.05% in development**; Q1 fallback is approximately **6.70% and 4.46%**, respectively. A maximum channel fallback rate of roughly 34.25% was reported across the roles. Masks exist as metadata but are not additional learned input channels. These are material representation facts, not evidence that all volume information is unusable. [P01]

The outcome endpoints are 10:30→14:30 and 11:30→15:30 ET, while issuance is modeled after the origin. Thus, current labels are **price-only forecasting outcomes**, not automatically four-hour executable returns after signal availability. The source report explicitly qualifies publication timing, action vintage, price/volume conventions, and rights. The old five-stock minute-entry execution plan must not be silently substituted for this contract. [P01]

---

## 3. Complete experiment inventory and what each result supports

### 3.1 Core objective, optimization, and capacity investigations

The following are development point estimates on the long-history HF20 population. MSE is original TG20 MSE and IC is daily mean within-origin Spearman IC. Except where indicated, these are single-seed screens. ZERO MSE is approximately **3.116560**, and its mathematical Spearman IC is undefined. [P02]–[P05]

| Model or change | MSE | Daily IC | What was learned |
|---|---:|---:|---|
| C0 / seed 42 | 3.112566 | 0.040318 | Original-target regression gives weak skill |
| T2 / seed 42 | 3.106560 | 0.075559 | Better point estimates than C0; working reference |
| C0 / seed 123 | 3.117257 | 0.014374 | Slightly worse MSE than ZERO |
| T2 / seed 123 | 3.114912 | 0.025493 | T2 improves C0 again, but gain is seed-sensitive |
| H2: Huber objective | 3.111709 | 0.054480 | No improvement over same-seed T2 |
| W1: tail weighting | 3.108253 | 0.050782 | Greater tail emphasis did not improve the main task |
| R1: ranking auxiliary loss | 3.106240 | 0.074718 | Tiny MSE gain; IC slightly worse |
| DM1: direction/magnitude decomposition | 3.116785 | −0.000043 | Signed forecasting did not improve |
| SS1: importance-corrected tail sampling | 3.109769 | 0.053402 | No improvement over T2/42 |
| LRLOW | 3.110404 | 0.071641 | Lower learning rate did not solve the problem |
| DROP0 | 3.104692 | 0.072780 | Lower MSE, lower IC; not a confirmed improvement |
| WD0 | 3.106679 | 0.074069 | Removing weight decay did not help |
| ES025 / seed 123 | 3.112703 | 0.032607 | Better point estimates than T2/123, inconclusive |
| H64 | 3.107416 | 0.035428 | Increasing width did not improve ranking |
| L2H32 | 3.116366 | −0.001326 | Additional recurrent depth performed poorly |

DROP0's MSE is lower than the later A12 MSE. A12 should therefore not be described as the best original-MSE model across the entire search. More generally, different “best” rows for different metrics do not constitute a stable discovery.

T2 improved original-scale MSE and IC relative to C0 in both reported seeds, making it a defensible comparison reference. It has not established a robust net trading strategy. SS1's importance correction preserves the intended population risk in expectation; changing sample exposure and gradient variance is not equivalent to changing the economic target. [P02] [P04]

### 3.2 E1 and QR1: positive evidence for different tasks

**E1:** Development ANY-tail-event average precision is approximately 0.132 versus 0.0415 for the constant-prior ranking reference. However, unweighted cross-entropy is approximately 0.2357 versus 0.2023 for that prior, and the signed ordinal IC is approximately −0.0037. These are better event-discrimination results alongside worse probability scoring and weak directional usefulness—not a calibrated directional trading signal. [P03]

**QR1:** Mean pinball loss is approximately 0.22608 versus 0.22983 for prefix-only unconditional quantiles, about a 1.63% improvement. Its central interval coverage is approximately 89.93%. Crucially, the reported improvement is in the outer quantiles: the median's pinball loss is slightly worse than the constant median, and median forecasts have weak IC. This is consistent with useful conditional dispersion/tail information without strong central signed information. It is not proof of accurate realized-volatility forecasts or original-return alpha. [P04]

**DM1 nuance:** The report also shows improvement in its reported magnitude-error metric relative to its prefix constant, while direction remains effectively chance-level and the combined signed prediction cancels toward zero. The exact magnitude target/units must be kept with that implementation; this should not be relabeled as a demonstrated forecast of dollar volatility. [P04]

### 3.3 A1–A12: completed screens versus untested candidates

| ID | Mechanism | Development MSE / daily IC | Current evidential status |
|---|---|---|---|
| A1 | Temporal attention | 3.10630 / 0.075801 | Tiny joint positive point estimates; uncertainty includes no gain |
| A2 | Multiscale temporal processing | 3.10866 / 0.059596 | No incremental improvement in tested design |
| A3 | GRU | 3.11474 / 0.012118 | Worse under the fixed protocol |
| A4 | Historical peer M1 mean/dispersion | 3.10646 / 0.063840 | Mixed; small MSE gain, worse ranking |
| A5 | Rank-four stock mixing after encoding | 3.10992 / 0.049569 | Mechanism active; forecasts worse |
| A6 | Final-state cross-stock attention | 3.11263 / 0.048202 | Near-uniform attention; forecasts worse |
| A7 | Endpoint market gate, MC1 | 3.10571 / 0.060536 | Small original-MSE gain, worse z-MSE and ranking |
| A8 | One-way global-8/local-32 memories | 3.10859 / 0.047244 | Active global pathway; forecasts worse |
| A9 | Coupled specialized memories | Not run | Paused, not rejected |
| A10 | State-dependent recurrent interactions | Not run | Paused, not rejected |
| A11 | xLSTM | Not run | Paused, not rejected |
| A12 | Two state-routed prediction heads | 3.10543 / 0.065696 | Small original-MSE gain, worse z-MSE and ranking |

Sources: [P06]–[P10]. No new candidate was promoted. P026, P027, and P028 are exploratory screens on reused development data, not independent replications of one another.

**A4's retained development direction:** Mean/dispersion summaries are demonstrably used, but can discard the identity and direction of a useful peer innovation. Its result does not reject all selective peer relationships. Reconsider after expansion, without presuming that directed lead–lag is the desired solution.

**A5's retained lesson:** The network can exchange stock information without using it profitably. The sampled hidden cross-stock Jacobian fraction of about 0.37 measures computational sensitivity, not explained return variance or economic causality. Donor replacement worsens A5 relative to itself, yet it remains worse than T2.

**A6's retained lesson:** Attention near the uniform distribution is not a dead module; it may aggregate common information. But strong dynamic peer selection was not demonstrated. A deeper or sharper attention mechanism is not automatically justified.

**A7/A12's retained direction:** Investigate why original MSE improves slightly while transformed loss and ranking worsen. Candidate explanations include common-level prediction, changed tail/ordinary error trade-offs, calibration, or noise. Preserve this question for later; do not assume regime learning has succeeded.

**A8's scope restriction:** It was the reduced one-way market-only construction, not the full C3 architecture with pooled local-state feedback. Its negative result must not be attributed to every possible global–local recurrent design.

**Information matching:** A4 is not a full-peer control for A5/A6. No trained plain 18-input LSTM controls A7/A8/A12. Comparisons against T2 combine changes in information, capacity, and processing. Identity at initialization does not make a separately trained model equivalent to the saved T2 checkpoint.

### 3.4 Original 10+3 backlog reconciliation

| Original question | What is actually covered | What remains unresolved |
|---|---|---|
| 1. C0/T2 replication | Two reported seeds | Broader seed/fold robustness |
| 2. Early stopping/optimization | P024 and per-run lifecycle audits | Full optimization diagnosis is not exhausted |
| 3. Longer training/alternative objectives | Multiple objectives and stopping/capacity changes | No evidence that simply forcing more epochs is a fix |
| 4. Tail classification | E1 | Calibration, simple risk comparators, replication |
| 5. Tail sampling/weighting | W1 and SS1 | No current reason for another blind weighting scheme |
| 6. Ranking loss | R1 auxiliary formulation | A different pure ranking target is a distinct, untested task—not a repeat result |
| 7. Quantiles | QR1 | Conditional rather than only aggregate calibration; replication |
| 8. Robust losses/transforms | Huber and asinh | Log-cosh/Yeo–Johnson completion not established; low priority |
| 9. Architectures | Nine A-candidates plus P024 capacity changes | A9–A11 untested; all paused |
| 10. More historical data | Long-history dataset established | Controlled causal effect of more years not identified |
| A. Predictive information in inputs | Some diagnostics and prior baselines | Current full-information baseline and interaction audit not fully established |
| B. Direction versus magnitude | DM1 | Further decomposition should be justified by new evidence |
| C. Rare-event predictability before weighting | E1, QR1, W1, SS1 | Directional event value and calibrated probabilities remain unresolved |

This is not a list of mandatory remaining jobs. It prevents both unnecessary repetition and falsely treating a broad research question as settled by one narrow implementation.

---

## 4. Are twenty stocks genuinely enough? What the literature permits us to conclude

### 4.1 The question has several meanings

“Enough” could mean enough to fit a small shared model, enough to reveal a particular conditional relationship, enough to estimate a cross-stock network, enough to validate broad equity performance, or enough to build a diversified portfolio. Those questions have different answers.

For HF20, the most defensible assessment is:

- **Enough for a meaningful pipeline and compact-model pilot:** yes. The data support actual training, independent source checks, and controlled mechanism screens.
- **Proven enough to exhaust four-hour predictive information:** no.
- **Proven too small to learn useful LSTM signals:** also no.
- **A convincing universe for broad S&P 500 generalization:** limited. Twenty retrospectively surviving names give restricted security, sector, and event diversity.
- **A reason to expand next:** yes, provided expansion addresses breadth and data quality rather than merely increasing row count.

No retrieved study provides a transferable threshold such as “an LSTM requires at least 200 stocks.”

### 4.2 Stronger empirical and methodological comparisons

| Research | Actual setting relevant to sample breadth | What transfers—and what does not |
|---|---|---|
| Fischer–Krauss, EJOR 2018 [R01] | S&P 500 constituents, daily directional prediction, 1992–2015 | A serious pooled equity precedent. Its post-2010 cost-adjusted deterioration warns that a large universe is not a cure. |
| Zhang–Zohren–Roberts, DeepLOB, 2019 [R02] | Five LSE stocks for training, rich order-book histories, over 134 million events; additional unseen stocks for transfer | Small stock count can coexist with strong predictive learning when information and sampling are different. Not evidence that hourly OHLCV with five or twenty names is equivalent. |
| Sirignano–Cont, 2019 [R03] | Roughly 1,000 stocks, billions of order-book events; pooled and cross-stock generalization | Supports learning shared structure across securities. Does not establish four-hour alpha from engineered candles. |
| Montero-Manso–Hyndman, IJF 2021 [R04] | Theory and experiments on global versus local time-series forecasting | Shared models need not add a separate parameter set per series. Their general results do not prove our fixed-width neural model is adequate or that series count alone determines success. |
| Lim–Zohren–Roberts, 2019 [R05] | Daily time-series momentum across 88 futures, recurrent trading models | Useful precedent for aligning prediction with a trading objective. Different asset class, signal, and horizon. |
| MASTER and StockMixer, AAAI 2024 [R06] [R07] | Daily stock-forecasting systems with market guidance and/or stock exchange modules | Motivate mechanisms, but P027/P028 are small adaptations, not complete replications. |
| DeepAR, IJF 2020 [R08] | Shared probabilistic recurrent forecasting across related series | Supports pooled distributional learning. Its nonfinancial results do not establish signed-return predictability. |

The DeepLOB trading illustration uses mid-prices without transaction costs; its predictive success must not be turned into a claim of executable net profitability. Conversely, the large-universe Fischer–Krauss result has an explicit adverse later-period qualification. Both observations are useful precisely because they prevent simplistic sample-size conclusions. [R01] [R02]

### 4.3 The number of independent observations is not the number of rows

A simple illustration—not a sample-complexity theorem—is the variance of an average of exchangeable errors with common correlation \(\rho\):

\[
\operatorname{Var}(\bar e)=\frac{\sigma^2}{N}[1+(N-1)\rho],
\qquad
N_{\mathrm{eff}}=\frac{N}{1+(N-1)\rho}.
\]

This shows why correlated observations need not provide a linear reduction in variance. It does **not** measure the effective training sample of a nonlinear panel model; residual dependence, time dependence, conditional heterogeneity, and changing regimes matter separately.

Adding securities can nevertheless contribute new events, different exposures, and more opportunities to observe a relationship. More stocks may also stabilize the cross-sectional median/MAD when there is sufficiently diverse residual variation. But the additional observations occur on the same historical dates. They do not create twenty new financial crises or twenty independent realizations of the 2025 market.

### 4.4 Breadth and useful information are different resources

A stockwise shared LSTM can benefit from more training series without directly observing them when forecasting one stock. A peer-aware network additionally needs access to their contemporaneously available histories. Increasing the training universe and increasing the forecast information set are different interventions.

A larger heterogeneous panel can also expose a limitation of unconditioned pooling. As a toy example, suppose an unobserved group variable changes the coefficient in \(Y=a_G X+\varepsilon\), with coefficients of opposite sign across groups. Pooling without usable group information can average the relationship toward zero. Adding more groups will not repair that omission. This is a possible mechanism, not a diagnosis established for HF20.

**Conclusion:** Treat 200–300 stocks as a plausible research-scale design, not a statistically certified minimum or a promise of better returns. Choose the eventual number from quality, breadth, historical eligibility, compute, and the intended trading problem. Do not choose it by the best development IC.

---
## 5. What plausibly went wrong—and what has not been demonstrated

### 5.1 Small forecasts are compatible with a good conditional-mean estimator

For squared-error prediction of a square-integrable outcome, the optimal population forecast is

\[
\mu(X)=\mathbb E[Y\mid X].
\]

The variance decomposition is

\[
\operatorname{Var}(Y)=\operatorname{Var}(\mu(X))+
\mathbb E[\operatorname{Var}(Y\mid X)].
\]

Most realized variation can be unpredictable given the available inputs. A forecast SD of 0.05 versus realized SD of 1.77 is therefore not, by itself, evidence of a defective network. Matching those SDs would generally inject noise rather than improve a mean forecast. The appropriate forecasting functional and scoring rule must be explicit. [R09]

For any forecast \(f\), using exactly the evaluation weights,

\[
\operatorname{MSE}_w(f)-\operatorname{MSE}_w(0)
=\mathbb E_w[f^2]-2\mathbb E_w[Yf].
\]

The additional forecast energy must be repaid by outcome alignment. T2/42's reduction relative to ZERO is about **0.321%** of ZERO MSE. This is small, but neither automatically meaningless nor evidence of a dependable edge. It does not estimate the best achievable Bayes risk. [P02]

**What would establish a practical problem?** A stronger, honest same-information baseline consistently outperforming the LSTM; reproducible failure to learn a planted admissible signal; systematic output calibration error on genuinely subsequent periods; or a verified implementation defect. Forecast dispersion alone does not do so.

The prior observation that A7/A12 increase forecast SD by about 14%/10% should be relabeled **less compressed outputs**, not “resolution of zero prediction.” Their ranking deteriorates. A positive rescaling of every score preserves ordering and therefore cannot fix Rank IC or an unchanged equal-weight rank portfolio.

### 5.2 Zero tail-threshold recall is not the right sole test of a mean predictor

Consider a stylized outcome that is zero most of the time and equals a large positive or negative number with state-dependent probability. Its tail probability can be predictable while its conditional mean remains small or zero. Requiring a point mean forecast to cross the realized 95th-percentile threshold confounds forecasting the expectation with forecasting a tail event.

This does not excuse poor large-outcome errors. It changes how they should be measured:

- Keep original and transformed error on fixed tail cohorts.
- Measure conditional sign/order performance within those cohorts.
- Evaluate event probabilities using discrimination **and** proper probability scores.
- Evaluate quantiles by pinball loss and conditional coverage, not their median's MSE as though it were trained to estimate a mean.

The E1 and QR1 branches provide reasons to investigate distributional information separately, not to amplify the T2 score until its tail recall is nonzero. Proper scoring-rule theory explains why these tasks need different evaluation. [R09] [R10]

### 5.3 T2's inverse is numerically correct but not a conditional-mean correction

Let \(Z=\operatorname{asinh}(Y/s)\). Ideal transformed squared-error fitting targets

\[
g^*(X)=\mathbb E[Z\mid X].
\]

The current inverse prediction is

\[
f_{T2}(X)=s\sinh(g^*(X)),
\]

but generally

\[
\boxed{s\sinh(\mathbb E[Z\mid X])\ne
\mathbb E[s\sinh Z\mid X]=\mathbb E[Y\mid X].}
\]

This is a target-functional distinction, not evidence of an erroneous double inverse or leakage. Retransformation bias is a longstanding statistical issue; Duan's work is a relevant foundation, not a plug-in guarantee for a heteroskedastic neural return model. [R11]

A mathematical counterexample illustrates the possible severity. With \(s=1\), suppose a conditional outcome equals 1 with probability 0.99 and −200 with probability 0.01. Its mean is −1.01, but its mean asinh value is approximately +0.813. Inverting that transformed mean produces a positive forecast. This is not a proposed financial distribution; it proves that even the sign need not be preserved when a nonlinear transform precedes expectation.

Under the restrictive assumption \(Z\mid X\sim N(\mu(X),\sigma^2(X))\),

\[
\mathbb E[Y\mid X]=s\exp(\sigma^2(X)/2)\sinh(\mu(X)).
\]

That identity is **not** a recommendation to multiply HF20 predictions by an estimated variance factor. The assumed distribution can be wrong, skew matters, and the correction can be unstable. A distribution with heavy tails in z-space may not even have the exponential moments required for a finite inverse-transformed mean.

**Implications for later design:**

1. Preserve T2 as a robust predictive score benchmark; it may be useful without being a calibrated return mean.
2. Decide whether the next primary task is return expectation, relative ordering, sign probability, or a predictive distribution.
3. If trading needs expected returns in economic units, estimate/calibrate that quantity explicitly on permitted historical data, with proper uncertainty and subsequent evaluation.
4. Do not repeat C0 blindly: original-scale MSE was already tested and performed worse. A new mean-oriented model needs a reason beyond rediscovering the inverse issue.

Monotonicity of `sinh` preserves the ordering of a particular vector of predictions. It does not guarantee that ordering conditional transformed means equals ordering conditional original means. Those are different statements.

### 5.4 Three objectives can select different models

The completed lifecycle optimizes z-MSE, selects epochs using original-target MSE, and emphasizes rank IC in the scientific comparison. The A7/A12 result—slightly better original MSE, worse z-MSE, worse ranking—is a concrete illustration. [P08]

There is no theorem requiring all three metrics to improve simultaneously. The existing no-promotion decisions remain valid under the frozen protocol. For the next research stage, however, we should predeclare **one primary objective linked to the intended trading decision**, with explicit secondary guardrails, rather than change the preferred metric after seeing results.

A rank-oriented score need not reproduce realized return magnitudes. Conversely, an expectation forecast used in an optimizer needs economic calibration, not only rank correlation. End-to-end trading objectives have a research precedent, but incorporating costs, path dependence, and constraints prematurely can hide forecast defects inside portfolio fitting. They belong after a valid predictive and execution reference is established. [R05] [R12]

### 5.5 TG20 removes a common level, not all systematic risk

Future cross-sectional centering preserves the realized ranking, but creates a relative rather than absolute prediction problem. If

\[
R_{i,t}^{(4)}=\beta_{i,t}F_{t}^{(4)}+\eta_{i,t}^{(4)},
\]

subtracting a common median does not remove \((\beta_i-\beta_j)F\) from pairwise differences. Nor does it produce identifiable stock-specific alpha.

The random future denominator also matters:

\[
\mathbb E[(R_i-m)/ (D+\epsilon)\mid X]
\ne
\frac{\mathbb E[R_i-m\mid X]}{\mathbb E[D\mid X]+\epsilon}.
\]

Both constructions can be valid research outcomes, but they emphasize different states and are not interchangeable trading forecasts. Enlarging the universe changes the median, MAD, ranking opportunity set, and possibly the floor. A change in TG20 MSE versus a new TG300 MSE is not a clean estimate of a data-size benefit.

**Potential future choices, not current amendments:** retain T2 as a ranking score; compare a bounded cross-sectional rank target; or estimate an executable return/residual mean with a predictable risk scale. Each must retain original economic outcome evaluation. A bounded rank target cannot by itself establish a higher-dollar-return strategy, and an auxiliary pairwise loss was already investigated in R1.

### 5.6 A7/A12 may improve common-level error rather than tradable separation

At each origin, with equal weights across eligible stocks,

\[
\frac1N\sum_i(Y_i-\widehat Y_i)^2
=(\bar Y-\overline{\widehat Y})^2+
\frac1N\sum_i[(Y_i-\bar Y)-(\widehat Y_i-\overline{\widehat Y})]^2.
\]

TG20 is median-centered, so \(\bar Y\) need not be zero. A model can improve the first component without improving pairwise ranks. For a dollar-neutral portfolio, a common predicted offset is not itself a useful cross-sectional allocation signal.

This is an especially relevant **read-only** investigation of A7/A12. Recompute both components using identical keys and session weights for T2 and the candidates, then combine with matched tail-error attribution. Do not state that the common-level explanation has already been verified; the supplied aggregate tables do not settle it.

### 5.7 The heavy-tail diagnosis is now more specific

The P028 tables identify extremes in original absolute TG20 and allocate the actual transformed loss to those same observations. For A7 refit, the ranked largest 1% contributes approximately 7.15% of z-loss; the largest 5% contributes 24.36%. Development counterparts are approximately 6.13% and 22.51%. Other arms are very similar. [P09]

The refit numerator/MAD partition is particularly instructive:

| A7 refit cohort | Evaluation weight mass | Share of actual z-loss | Conditional z-MSE, derived from the supplied table |
|---|---:|---:|---:|
| Large numerator only | 4.74% | 19.51% | 5.44 |
| Small MAD only | 5.12% | 5.59% | 1.45 |
| Both | 0.086% | 0.73% | 11.33 |
| Neither | 90.06% | 74.16% | 1.09 |
| All observations | 100% | 100% | 1.322 |

The table uses **weight mass**, not merely row percentage. Large-numerator-only observations incur roughly 4.1 times the overall mean z-loss, while small-MAD-only observations are about 1.1 times that mean. The rare combined group is difficult but contributes little total mass. These are conditional descriptions—not causal effects of changing a numerator or denominator. [P09]

There is no observed `MAD <= epsilon` cohort in the supplied P028 support record. This does not imply that denominator variation never matters; it means that increasing the floor is not supported as the obvious repair.

Three important distinctions remain mandatory:

- **Ranked percentile versus fixed threshold:** the largest 1% within development contains 36 observations, whereas the training-frozen 99th-percentile event threshold selects 14 development observations. Both are legitimate diagnostics for different questions.
- **Percentile versus percentage of maximum:** 95% of the largest target magnitude is not the 95th percentile. The former selects one refit observation here and no development observations.
- **Loss versus gradient influence:** a quarter of objective loss does not imply a quarter of gradient norm, nor prove that tails drive unstable updates. Current clipping is rare; bounded gradient attribution is needed before a new optimization explanation is asserted.

The original-scale tail errors remain large, including A7 development conditional MSE of approximately 32.26 above the training 95th-percentile threshold and 86.94 above the 99th. However, no paired original-error decomposition against T2 on every identical numerator/MAD and ranked-tail cohort is visible in the supplied tables. Retrieve those saved tables or derive them from immutable predictions before claiming the small A7/A12 gain comes from tails. [P09]

**Priority consequence:** no automatic target clipping, denominator enlargement, rare-event deletion, output amplification, or another generic robust loss. These would alter the task before identifying the limiting mechanism.

### 5.8 Optimization is functioning; optimal learning is not established

The latest models have finite parameter gradients and exact checkpoint replays. P028 calibration clipping is about 0.37–0.52% of updates and refit clipping is zero. A7, A8, and A12 select 7, 6, and 7 epochs, and their raw minima occur at those same epochs. The earlier raw-minimum-versus-qualified-minimum issue is therefore **not** the immediate explanation for P028. [P10]

Nonzero gradients do not prove useful temporal credit assignment, optimal curvature, well-conditioned features, or absence of saturation elsewhere. But the evidence does not support restarting an unrestricted learning-rate/dropout/width search. P024 already tested several obvious candidates.

Training and development MSE levels must also be interpreted against each role's outcome distribution and null baseline. A lower development MSE than training MSE can reflect smaller target variation, not superior generalization. Online dropout-ON training losses are not directly comparable with fixed-checkpoint dropout-OFF validation losses.

A low-error tiny synthetic task is a check of implementation capacity. It is not evidence that a market signal exists. A failure on a carefully matched planted task, on the other hand, would justify debugging before expansion.

### 5.9 The current inputs may conceal or remove useful distinctions

Feature engineering can stabilize noisy price data while also compressing predictive details. Several hypotheses deserve an audit before selecting a replacement representation:

**Fallback ambiguity.** A neutral scaled value may mean a genuinely ordinary observation or a substituted value. The network cannot necessarily distinguish those cases without a causal quality indicator. Mask/time-since-observation methods have a sound methodological precedent, although the frequently cited GRU-D evidence is medical, not financial. A small quality/age-channel experiment would be an adaptation, not a validated trading fix. [R13]

**Incomplete path information.** A sequence of derived indicators may not preserve the price/volume patterns needed for the task. A compact causal representation of normalized OHLC movements, gaps, range, and trusted activity can be tested against—not automatically substituted for—FT16. Research on learned price representations motivates testing the representation itself, but its CNN results do not imply that chart images are necessary or superior for this project. [R14]

**Clock ambiguity.** Equal recurrent steps can represent an hour, an overnight break, or a holiday gap. Some existing features already encode daily, origin-specific, or same-slot information; an audit must identify the residual missing clock information rather than claim all seasonality is absent. [P01]

**Pooling heterogeneity.** Sector, size, liquidity, volatility, and data-quality differences can modify feature effects. A shared model with modest, point-in-time context is a reasonable larger-panel candidate. Unrestricted ticker embeddings are not the default: they can memorize survivors and complicate generalization to new members.

None of these is an established root cause. They are relatively concrete mechanisms with testable input-level controls, unlike adding another unconstrained layer and hoping it helps.

### 5.10 Static training across many years can mix changing relationships

Fifteen calendar years offer more observations and regimes, but potentially older relationships that do not transfer. It is possible to average away a changing conditional effect even with flawless optimization.

This does not justify arbitrarily discarding early years. Research on forecasting after structural breaks emphasizes a bias–variance trade-off: pre-break observations can still be useful, and selecting a window introduces uncertainty. [R15]

P028 also has a specific state-support limitation: the descriptive high-volatility category occupies 74 of 109 development sessions, while the low category has 35 sessions and only one qualifying run of at least five consecutive sessions. Training/selection support passed the approved screening policy, but that is not evidence of several independent low-state episodes in development. These diagnostic bins are not the identities of A12's learned experts. Within-window state transitions were common; MC1 was tested, while MC2 was not. This limits the scope of a broad conclusion that market-state conditioning does not work. [P08]

A larger-panel design should permit a **small predeclared expanding-versus-recent-window comparison** at identical forecast dates, if temporal diagnostics motivate it. Initially this can be screened with a regularized linear model; it need not trigger a large recurrent adaptive-learning program. All labels used by a rolling head or performance controller must have matured, and historical errors must come from predictions actually issued without those outcomes.

### 5.11 We have not yet shown that a valid forecast becomes a profitable trade

Current reports intentionally contain no HF20 trading P&L. A positive Rank IC, low MSE, or conditional tail score is therefore not the final criterion.

Trading value depends on forecast decay, execution delay, spread/slippage assumptions, turnover, netting, borrow, risk exposure, and portfolio constraints. Theoretical work on predictable returns with transaction costs shows why the speed and persistence of a signal matter, not just its sign. [R12]

Before the next model is called a trading model, preserve the distinction:

\[
\text{available information}\rightarrow\text{forecast}\rightarrow
\text{permitted trade}\rightarrow\text{realized position return}\rightarrow
\text{net economic evaluation}.
\]

For a fixed rank-based strategy, multiplying every score by a common positive constant leaves the selected stocks unchanged. For a score-weighted optimizer it changes exposure and risk. “Fixing forecast amplitude” without specifying this mapping is not a complete improvement proposal.

---

## 6. Root-cause assessment: confidence and discriminating evidence

| Candidate explanation | Current support | What would discriminate it | Consequence now |
|---|---|---|---|
| Weak conditional signed information in the supplied features | Consistent with many weak models and strong compression; not proven | Strong same-information simple baselines; stable cross-period conditional tests | Avoid claiming that architecture alone will solve it |
| Twenty names insufficiently diverse for broad cross-sectional learning | Plausible; not identified by existing comparisons | Larger quality-controlled universe with common-stock/common-task bridge | Supports expansion, not a guaranteed cure |
| Objective/forecast-functional mismatch | Mathematically established distinction | Mean-versus-rank contract; read-only common-level/tail/calibration decomposition | Clarify before new labels or portfolio sizing |
| Fallback/quality and clock representation lose information | Concrete source facts, uncertain predictive impact | Native/fallback/age strata, paired causal feature tests if warranted | Audit before multiplying the panel |
| Current labels and execution objective differ | Explicit price-only label contract | Hand-traced post-issuance return bridge and execution feasibility | Must resolve before trading claims |
| Severe clipping/exploding-gradient failure explains P028 | Not supported by supplied telemetry | Existing full telemetry and controlled replay | Do not retune clipping reflexively |
| Strict epoch rule alone explains P028 | Weak: raw and selected minima coincide | Existing curves, no raw-min rescue needed | No special extra-epoch campaign |
| Extreme denominators drive most objective failure | Weak in supplied cohorts; floor-dominated group empty | Matched numerator/MAD contributions and data cases | Do not enlarge floor or erase tails by default |
| Common-level rather than stock-ranking improvement | Plausible for A7/A12, unverified | Exact cross-sectional error decomposition | Preserve as cheap diagnostic |
| Temporal nonstationarity | Plausible; limited era-level evidence supplied | Predeclared rolling-origin, same-information comparisons | Address in larger-panel validation |
| Architecture can represent mechanisms but does not use them usefully | Directly supported in tested forms | Mechanism activity plus matched predictive comparisons | Preserve negative evidence; no universal impossibility claim |
| Current development gains are selection/noise-sensitive | Strong design concern: 109 reused sessions | New locked temporal evaluation, paired controls, seed/fold robustness | Do not promote on these point estimates |

**Overall diagnosis:** There is no demonstrated single catastrophic failure. The evidence instead points to a combination of weak signed signal, task/representation choices, limited cross-sectional diversity, and a narrow reused evaluation period. Source and execution conventions are concrete enough to require a targeted audit, but their contribution to poor predictions is not yet quantified.

---
## 7. Audit of possible improvements—not a list of presumed solutions

The priorities below are judgments for this project, not rankings of methods in general. “Before expansion” means design or bounded diagnostic work unless a separate run is explicitly approved.

| Candidate change | Why it could help | Why it could fail / existing counterevidence | Recommended disposition |
|---|---|---|---|
| Correct label-to-execution mapping | Makes the forecast relevant to a trade that can actually occur | Does not create alpha; may reduce measured signal | **Foundational before economic claims; specify before expanding the trading study** |
| Improve missingness/age/quality representation | Distinguishes ordinary values from fallbacks; avoids silently erasing information | Vendor artifacts can become unstable predictors; retrospective flags may be unavailable live | **High-priority audit; small 20-stock proof only if a concrete gap is verified** |
| Larger, broader S&P 500 panel | More securities, events, factor/sector coverage, and trading opportunities | Correlation, heterogeneous effects, poor-quality additions, survivorship | **Next major empirical direction after the limited prerequisites** |
| Strong information-matched simple baselines | Determines whether recurrence is missing learnable structure | A negative linear result does not rule out nonlinear signals | **Required comparison design, not a competing project** |
| Compact normalized price/path inputs alongside FT16 | Reduces reliance on handcrafted summaries; preserves local movements | Adds noisy/redundant channels; raw levels can create nonstationarity | **High-value larger-panel candidate after source audit** [R14] |
| Modest sector/liquidity/clock context | Supports heterogeneous shared mappings | Sparse groups, unstable labels, identity memorization | **Conditional larger-panel representation test** |
| Objective aligned to relative ordering or executable expected return | Addresses the explicit train/select/trade mismatch | Rank objective may discard payoff magnitude; original MSE already struggled | **Define the task first; one focused comparator later, not a loss sweep** [R09] |
| Recent-window or slowly adaptive fitting | Can track changing feature–return relationships | Less data; noisy updates; causal feedback requirements | **Moderate priority after chronological diagnostics** [R15] |
| Time-of-day and elapsed-time channels | Represents gaps and session-specific effects | Some information already present through M2/Q1; known effects may be gone | **Cheap feature-coverage audit; not an assumed missing alpha** [R16] |
| Independent market/sector context | Information may differ from the endogenous two-proxy panel state | Coverage and clock problems; common state need not predict relative ranks | **Conditional on a lawful, causal source and matched comparator** |
| Factor residual inputs | Separates common movement from stock-specific deviations | Factor errors; changing loadings; residuals need not revert | **Optional representation test, not a compulsory pairs-trading program** [R18] |
| Separate common and relative components | Can distinguish common-level MSE from cross-sectional skill | Free additive heads are not identifiable economic factors | **Read-only decomposition first; no new heads yet** |
| Alternative horizons / intraday resolutions | Different mechanisms may survive at different horizons | Costs rise at short horizons; overnight/session changes at long horizons; multiple testing | **Small predeclared screen later, not best-horizon mining** [R16] [R17] |
| Causal smoothing/filtering | May estimate persistent latent state or reduce measurement noise | Delay, loss of shocks, invented latent dynamics, leakage | **Lower priority unless a specific noise problem is demonstrated** [R19] [R25] |
| E1/QR1 probability/quantile refinement | Builds on the clearest task-specific positive evidence | Could model risk only, not signed returns; calibration remains necessary | **Preserve as separate branches; no automatic fusion** [P03] [P04] |
| Selective trading / abstention | Avoids weak or cost-dominated opportunities | Threshold mining; reduced coverage; high predicted risk can mean worse trades | **Only after honest signal calibration and economic replay** [R12] |
| News/events/other external information | May contain genuinely new information beyond price history | Timestamp/vintage/coverage problems; cost and scope; weak incremental signal | **Later, source-driven hypothesis—not mandatory** |
| xLSTM, coupled cells, larger experts | Alternative inductive biases may improve learning | Current evidence does not identify a memory defect; more capacity can worsen estimation | **Paused; revisit only with a specific mechanism and control** [R24] |
| More robust losses or larger forecast amplitudes | Could alter gradient emphasis or calibration | H2/W1/SS1 and amplitude diagnostics already warn against simplistic fixes | **Low priority without a new diagnosis** |

### 7.1 A compact alternative input design worth retaining

A future minimal alternative should preserve useful price information without feeding raw, split-sensitive price levels indiscriminately. A candidate family—not a frozen feature list—is causal log returns/gaps, normalized OHLC ranges, price distances to known historical anchors, trusted activity, and explicit availability/elapsed-time metadata. Retain a small absolute volatility state so normalization does not erase the environment.

For example, a causal standardized return could be

\[
\widetilde r_{i,t}=\frac{r_{i,t}}{\widehat\sigma_{i,t}^{\mathrm{past}}+\epsilon_\sigma},
\]

with \(\widehat\sigma^{\mathrm{past}}\) also available as a separate input. Its definition, timing, and adjustment convention must be frozen before evaluation. This is not an instruction to recompute FT16 now.

Compare a compact raw-derived representation with FT16 under the same information horizon, then only test their union if the extra representation actually adds value. Supplying every technical indicator and every raw derivative simultaneously would obscure the question.

### 7.2 Smoothing: test an identified state, not the slogan “remove noise”

For a deterministic filter \(S_t=g(X_{\le t})\),

\[
\mathbb E[Y\mid X_{\le t},S_t]=\mathbb E[Y\mid X_{\le t}].
\]

The filter adds no information relative to the full history it uses. It may help a finite model through representation or regularization; if it reaches further back than the baseline, it additionally changes the information horizon.

Start, if justified, with an inexpensive causal exponential average and compare original-plus-filtered against the original input. A state-space filter requires a defensible observation/state model; a two-sided smoother is not causal at historical forecast time. Hamilton's HP-filter critique and subsequent discussion illustrate that filtering can manufacture apparent dynamics. They do not prove that every causal filter is harmful. [R19] [R25]

The failed A2 screen tested one multiscale implementation, not all denoising. Nevertheless, it lowers the priority of trying another averaging architecture without a more specific rationale.

### 7.3 Residuals and pairs: useful candidates, not the objective

A historical factor residual

\[
\widehat\eta_{i,t}=r_{i,t}-\widehat\beta_{i,t^-}^{\top}F_t
\]

can be a legitimate input when the factor observation is available and the exposure estimate is fitted on permitted history. Residual structure has a serious statistical-arbitrage precedent. But covariance removal does not prove stationarity, mean reversion, or expected-return predictability. [R18]

A rolling sum also has mechanical behavior:

\[
S_t=\sum_{j=0}^{L-1}\widehat\eta_{t-j},\qquad
S_{t+1}-S_t=\widehat\eta_{t+1}-\widehat\eta_{t-L+1}.
\]

Part of an apparent “reversion” of this rolling statistic is the old observation leaving the window. It must not be confused with forecastable new residual returns. Any future test must predict the actual new outcome and use an executable hedge convention, not simply demonstrate that a rolling indicator eventually declines.

We should neither force mean reversion nor select stocks because their historical pair backtest looks best. Residual features can be useful without a pairs strategy, and the broader LSTM goal can succeed without any such representation.

### 7.4 Intraday timing and horizon: relevant but not automatic priorities

Published intraday work documents patterns tied to session timing and short-horizon constituent information. Those settings motivate investigating the actual clock; they do not validate the same effect in the current period, selected stocks, or four-hour target. [R16] [R17]

The low-cost first question is whether current feature engineering already captures the proposed timing distinction. If not, a later clock/gap indicator is easier to interpret than another recurrent module. A horizon change should be justified by signal persistence or trading economics, with predeclared alternatives and appropriate purging. The current two-origin same-session protocol is an experimental choice, not a theorem that every useful LSTM trade must last four hours.

### 7.5 Distributional models: promising, but maintain the signed-return question

E1's event-discrimination improvement and QR1's outer-quantile improvement suggest the input may contain useful information about conditional distribution shape. A simple volatility/activity-conditioned probability or quantile baseline is therefore essential: the network should beat more than an unconditional constant before its complexity is credited.

For an unrestricted weighted multiclass cross-entropy objective with weights \(w_k\), the population optimum is

\[
q_k(X)=\frac{w_k p_k(X)}{\sum_j w_j p_j(X)},
\]

not the original class probability \(p_k(X)\). This derivation helps explain why weighted classification and calibrated probabilities are distinct goals. It does not prove that a particular correction fixes the finite fitted E1 network. Any calibration must use permitted historical predictions, not fit and claim improvement on the same development outcomes.

A future distributional LSTM could estimate mean and scale, or quantiles, under proper scores. DeepAR supplies a recurrent probabilistic modeling precedent; it is not a reason to assume that a good risk forecast has a nonzero directional edge. [R08] [R10]

---

## 8. What is worth doing on twenty stocks before expansion?

### 8.1 Default: a bounded read-only dossier, not more architecture fitting

These checks use the existing source manifests, predictions, target operands, checkpoints, and diagnostic exports. Their purpose is to decide what must change in the expanded pipeline. They are recommendations for a later approved task, not work performed by this document.

| Check | Required output | Why it can matter before expansion |
|---|---|---|
| **Clock and economic-outcome bridge** | A few exact feature-end → source-availability → issuance → earliest permitted entry → outcome examples, including gaps and closing periods | Stops price-only forecasting labels from being misrepresented as executable trades |
| **Same-observation loss attribution** | T2 versus A7/A12 and useful controls: original and z-loss on identical tail, numerator/MAD, sign, quality, and state cohorts | Determines whether apparent gains come from tails, ordinary observations, or a common level |
| **Cross-sectional error decomposition** | Common-mean error plus centered-vector error, daily weighted, with ranking/retrieval metrics | Directly tests the most interesting A7/A12 hypothesis without fitting |
| **Fallback and source-quality audit** | Per-channel value-versus-fallback/age distributions; chronological quality strata; actual causal availability of masks | Identifies representation omissions and whether expansion will worsen them |
| **Objective contract** | Clear statement of the forecast functional, loss, selector, trading mapping, and units | Prevents interpreting an inverse-asinh score as calibrated expected raw return |
| **Baseline inventory** | Exact current-source momentum, ridge, nonrecurrent, event-risk, and quantile controls that actually exist | Avoids assuming old five-stock baselines are current HF20 evidence |
| **Scaling readiness** | Variable-N mask design, point-in-time membership plan, storage/compute estimate, and panel-size comparison specification | Prevents an all-N intersection collapse and target-confounded conclusions |

The source-level replay should remain small and deterministic. Existing full-population numerical checks should be reused, not rebuilt as hundreds of new expensive audits.

### 8.2 Conditions that really would justify another small-universe fit

A further 20-stock fit becomes justified only when it can resolve a specific fundamental uncertainty cheaply:

**Verified defect.** A causal-clock error, source-adjustment inconsistency, wrong loss aggregation, feature identity swap, broken gradient path, or label/return mismatch is reproduced. Repair and rerun only affected dependencies, preserving invalidated outputs.

**Concrete missing-information representation.** The audit establishes that the input cannot distinguish a frequent, causally observable missing/stale state from a genuine value, or that an essential price movement is absent from the representation. A tightly matched baseline-versus-fix comparison can verify the new pipeline before scaling. A mask feature still needs an out-of-period check; a training gain alone is insufficient.

**Demonstrable learnability gap.** A comparable simple model shows stable predictive structure that the recurrent implementation misses, and a small controlled test can distinguish a training or interface defect from model choice. This is stronger evidence than merely noticing a low IC.

**An incompatible forecast/trading contract.** A minimal corrected-label/control fit is needed to establish that a new economic task is implemented properly before building a much larger panel. This is a new version of the task, not a retroactive repair of the old result.

**Budget principle:** prefer zero new starts; if one fundamental issue warrants fitting, propose one matched pair first. A second pair requires a genuinely different unresolved issue. This is not a newly authorized numerical budget and does not waive the 200-start ledger or human approval.

### 8.3 What does not justify extending the HF20 search

A small negative IC difference, a near-uniform attention plot, a slope above one, an unused budget, a later unqualified loss minimum, or an interesting new paper is not sufficient on its own. Neither is the desire to get one positive result before expanding.

**If the bounded review finds no fundamental defect, move to the larger universe.** The review should not become a requirement to solve every uncertainty before any broader empirical work can begin.

---

## 9. Designing the expanded S&P 500 universe without selecting it now

### 9.1 Membership must have an explicit time meaning

The official S&P 500 methodology describes a large-cap index of 500 constituent companies, with classifications and eligibility rules that require appropriate records. It is not a static historical list. [R23]

Before selection, resolve which of these is intended:

- **Preferred for an investability claim:** membership known at each historical decision/formation date, with additions, deletions, and security changes handled explicitly.
- **Alternative research constraint:** members of a fixed as-of-date list, studied retrospectively. This may satisfy a present-day selection requirement, but it is a survivor-conditioned study and must be labeled that way.

Do not silently interpret current members as having belonged to the index throughout 2011–2025. Do not require all selected names to have fifteen uninterrupted years of data simply to make tensors rectangular; that creates an additional survivor/age filter. Historical membership availability remains a source requirement to resolve, not a fact assumed in this report.

Membership also differs from security identity: multiple share classes, ticker changes, mergers, spin-offs, and corporate actions need stable identifiers and explicit treatment. Exiting index membership must not cause an already-open trade or an adverse delisting outcome to disappear retrospectively.

### 9.2 Selection criteria to freeze before looking at model returns

| Dimension | What to consider | What to avoid |
|---|---|---|
| Sector and industry breadth | Adequate representation and more than isolated names per meaningful group | Choosing industries because preliminary model IC is high |
| Liquidity and implementation | Historically observable activity, price, trading availability, plausible size limits | Picking only the most backtest-profitable or easiest surviving names |
| Market-cap and volatility diversity | Variation within the permitted S&P 500 universe | Treating larger/smaller within the index as uniformly more predictable |
| Membership and security history | Point-in-time records or an explicitly retrospective alternative | Backfilling present-day membership into earlier periods |
| Source quality | Genuine bar endpoints, publication convention, action handling, volume provenance, missingness | Selecting on future complete coverage while calling the rule investable |
| Corporate actions and outcomes | Consistent prices/share units, delistings and future exits | Deleting difficult cases after their outcomes are known |
| History length | Sufficient causal warm-up for the model in use | A universal fifteen-year survival requirement |
| Dependence and redundancy | Broad opportunities plus adequate related-company coverage | Counting near-duplicate exposures as independent samples |
| Compute/storage | Canonical shared store, masks and on-demand windows | Repeated per-model/per-seed raw datasets |

The target number should be the largest **defensible and manageable** panel for the research question, not necessarily the largest available download. A 200-stock panel with good historical semantics can be preferable to 300 names with inconsistent inputs. Conversely, there is no scientific reason to stop at 300 if a broader compliant panel materially improves coverage and remains manageable.

No sector allocations, thresholds, membership dates, or ticker names are frozen by this document.

### 9.3 The current all-stock-complete rule must not scale blindly

If a complete origin requires every stock to pass a quality condition, larger N can destroy coverage. As a purely illustrative calculation, if each stock independently has a usable origin with probability 0.995, all-stock completeness is

\[
0.995^{20}\approx0.905,\qquad
0.995^{200}\approx0.367,\qquad
0.995^{300}\approx0.222.
\]

Actual missingness is dependent, so these are not forecasts of the dataset. They show the fragility of a full-panel intersection.

A larger design should support a point-in-time eligible set \(\mathcal U_t\), minimum coverage rules, separate feature and label validity, and masks that prevent unavailable peers from entering a forecast. The model should not require adding synthetic prices or deleting a stock because its later outcome will be missing.

For example, supervised weighting may use

\[
L=\frac1{|\mathcal D|}\sum_{d\in\mathcal D}
\frac1{|\mathcal O_d|}\sum_{o\in\mathcal O_d}
\frac{\sum_i v_{i,d,o}\ell(\widehat y_{i,d,o},y_{i,d,o})}
{\sum_i v_{i,d,o}},
\]

where \(v\) is the **supervised validity mask**, distinct from the contemporaneous input/entry eligibility mask. This proposed change must define how the target cross-section is constructed when future outcomes are missing. It is not permission to shrink the historical investable universe using hindsight. Portfolio replay must retain all causally admitted positions and handle unresolved exits honestly.

The changing denominator and membership of a relative label need a new versioned target contract. A variable-N model is not merely a bigger tensor version of TG20.

### 9.4 Separate three benefits that expansion otherwise confounds

**More training securities:** Does a shared mapping generalize better after being estimated across more securities, while the evaluated stock set and economic outcome stay fixed?

**More contemporaneous peer information:** Does access to more peers improve forecasts for an unchanged tradable/evaluation set, with the target held fixed?

**A larger tradable ranking universe:** Does selecting positions from more stocks improve the opportunity set and diversification, under a new relative target and comparable exposure/cost rules?

These questions need not produce three large experiment grids. But the first expansion report must identify which changed.

A useful bridge preserves the original 20-stock evaluation on the same dates and archived TG20 labels, alongside separate evaluation on the new universe. Training an enlarged pool under exactly comparable labels may require a common fixed reference-basket or economic-return target; define that explicitly before claiming a pure training-panel effect. Do not quietly pool TG20 labels for some names and TG300 labels for others.

Report source changes, scaler changes, target changes, stock composition changes, and information access separately. A higher new-universe IC is not automatically better modeling: the cross-section itself is different.

### 9.5 Capacity and computation need controls, not a new architecture sweep

A shared stockwise LSTM does not need a separate parameter set for every new stock. Its parameter count can remain unchanged while compute grows with N. Final-state attention is approximately quadratic in N: going from 20 to 300 stocks multiplies its pairwise dimension by 225. A fixed-rank mixer is cheaper but its stock-axis weights are tied to a specific identity/order convention.

This argues for a simple, variable-panel-compatible baseline first. Recurrent encoders can be processed in chunks when mathematically equivalent, but cross-stock operations and session/origin loss weighting must remain intact; naive microbatching can break the comparison. GPU memory pressure is not permission to change masks, drop hard examples, detach intended communication, or reweight sessions silently.

Archive one canonical source/feature store, lightweight window indices, compact prediction records, and immutable manifests. Do not materialize overlapping 48-step copies separately for every model, seed, or cost setting.

---
## 10. The staged development plan after the pause

These stages are proposals for subsequent decisions. They are not Codex execution authority. The plan deliberately avoids another twelve-model factorial search.

### Stage 0 — Preserve the evidence and answer the fundamental design questions

Archive P021–P028 and the current source/feature/target/checkpoint identities, including the disclosed reporting-only ledger amendment. Keep the record at 62 starts. Do not silently “correct” old results to a new target, sample, or definition of success.

Complete the bounded dossier in Section 8 when authorized. Its decision is one of: **no fundamental defect found; verified defect requiring repair; economic-target revision needed; source/coverage inadequacy blocks expansion; or unresolved but nonblocking scientific limitation**.

The output should contain a one-page decision record, not another unbounded tuning backlog. If only speculative improvements remain, proceed to expansion design.

### Stage 1 — Freeze the expanded data and economic task

Select the membership convention, coverage policy, point-in-time eligibility, intended forecast/trade clock, target reference cross-section, portfolio exposure convention, and permitted source. The stock selection itself is a separate later task.

Build a new, versioned data contract with variable-N/missingness handling. Preserve an anchor comparison to HF20, and explain any changes in daily proxies, volume conventions, target endpoints, and observation age. Test loss/mask behavior on a small synthetic or existing-data slice before any large acquisition or fitting task is authorized.

**Gate:** no unexplained timing, action, masking, outcome, or complete-panel-selection violation. Source limitations may remain explicitly assumption-conditional, but must be compatible with the intended claim. Rights and usable historical membership cannot be fabricated to pass a gate.

### Stage 2 — Establish a small, strong larger-panel reference set

The initial comparison should answer whether useful, transferable predictive information is present and whether recurrence helps exploit it. It should not begin by stacking A7, A12, and a peer mixer.

| Reference | Purpose | Fairness requirement |
|---|---|---|
| ZERO and permitted training-only constant forecasts | Basic expectation/null reference | Never use the later sample mean as a fitted baseline |
| Simple predeclared momentum/reversal score | Economically interpretable price-only comparator | Same available information clock and execution |
| Pooled regularized lagged linear model | Strong low-variance same-information control | Explicit lag/history reach; scaler and penalty selected within permitted training |
| Compact shared LSTM | Main recurrent reference, initially close to current architecture | Same input/target/masks and bounded tuning budget |
| At most one small nonlinear nonrecurrent control when useful | Separates recurrence from generic nonlinearity | Disclose information-history differences; no large boosting search |

A ridge model that receives only the latest bar is not a fair full-sequence comparator. Conversely, a 48×16 flattened input has 768 columns per stock and should be regularized, not treated as 768 independent pieces of information. The useful role of simple models and nonlinear interactions in asset prediction is supported by the broader empirical asset-pricing literature, but monthly characteristic-based results are not direct evidence for hourly candles. [R22]

Also examine a simple historically fitted per-stock/group mean or risk profile where scientifically appropriate. In a fixed survivor panel, a model can exploit persistent security characteristics without learning useful time variation. A stock-profile baseline helps distinguish that possibility; it must not be fitted on the evaluation targets.

**Gate:** technically valid forecasts, adequate comparison populations, and evidence measured by the predeclared primary predictive criterion with uncertainty and economic relevance. A negative baseline screen is a valid result; it is not a command to increase architecture size.

### Stage 3 — Test one representation or objective bottleneck at a time

Choose the next change from the Stage 0/2 evidence, rather than attempting all possibilities:

- Missingness/clock ambiguity → a minimal causal quality/elapsed-time representation.
- Engineered inputs lose usable path information → a compact raw-derived sequence comparator.
- Mean-versus-rank objective mismatch → one clearly defined alternative target/loss, retaining T2 as reference.
- Era instability → a small predeclared window/refresh comparison.
- Informative context missing → one independently justified sector/market/context block, also supplied to the plain comparator.

A hypothesis should specify the expected failure pattern, its strongest simpler control, what would count as an improvement, what would refute it, and the maximum permitted follow-up before fitting. Avoid changing universe, target, clock, feature set, objective, and architecture simultaneously and then claiming a mechanism-specific discovery.

**Gate:** improvement in the task it was designed to solve, stable enough across prespecified periods/seeds to justify further evidence. Training loss, output magnitude, attention entropy, or a successful synthetic task is not a promotion criterion.

### Stage 4 — Revisit the architecture archive selectively

The user's future-development notes remain active as hypotheses:

| Candidate family | Evidence that would justify a revisit | Required control or qualification |
|---|---|---|
| A4 peer summaries | Expanded panel adds meaningful peer breadth; summaries have interpretable information | Same-information baseline; consider whether identity is lost through averaging |
| A5/A6 exchange | Rich peer histories show value or a specific routing/compression limitation remains | Plain full-peer or otherwise adequate information control; fixed-identity and capacity effects disclosed |
| A7/A12 state conditioning | State effects survive simple conditional analysis; MSE-versus-ranking decomposition identifies a relevant task | Plain model with identical state inputs; regime occupancy; no economic expert names without evidence |
| A8 global–local | Common historical state helps and shared memory is a concrete compression hypothesis | Clarify one-way versus local-feedback design; matched information/history reach |
| A1/A2 temporal readout/multiscale | Temporal diagnostics identify useful history the final-state reference loses | Same information, feature horizons, and controlled capacity |
| A3 simple recurrent alternatives | Optimization/runtime or mechanism evidence motivates a cheap alternative | Comparable capacity and protocol |
| A9/A10 specialized recurrence | A defined interaction can be learned in a controlled case and has plausible relevance in the expanded data | Independent/late-fusion or fixed-coefficient controls; no hidden controller that recreates an unrestricted predictor |
| A11 xLSTM | A specific memory limitation is demonstrated and cost is justified | Small matched recurrent reference; acknowledge that the cited original evidence is language modeling, not this financial task |

A7/A12 and A4–A6 are preserved for later development, but no commitment is made to retrain every candidate. The xLSTM paper motivates memory alternatives; it does not supply a reason to expect an improvement merely because standard LSTM performance is weak. [R24]

### Stage 5 — Establish economic usefulness with frozen forecasts

After a predictive reference and execution contract are valid, evaluate a simple, predeclared portfolio map. Separate ranking quality from sizing, risk control, turnover, and cost. Begin with transparent exposures rather than a learned allocator that can compensate for or disguise forecast weaknesses.

Use the actual causally issuable forecast population, not only rows with convenient future exits. Report full-calendar outcomes, long/short contributions, market/sector exposure, turnover, netting, rejected entries, unfilled exits, and multiple explicitly assumed cost levels. A neutral/cash baseline and opportunity-matched randomized reference are useful; a buy-and-hold benchmark is contextual, not automatically risk-matched.

Conditional trading and threshold selection must be fitted on earlier information and evaluated later. Report opportunity coverage and concentration alongside accuracy. A high hit rate on a tiny post-selected subset is not evidence of a useful strategy.

Only then consider whether a calibrated forecast distribution, a turnover-aware objective, or a small allocation layer adds value beyond frozen-alpha simple construction. [R05] [R12]

### Stage 6 — Confirmation and the final claim

Lock the finalist information set, task, fit window, hyperparameters, seed protocol, trading rules, and analysis before accessing the protected confirmation. A later discovery of a deterministic defect must preserve the first-look result and disclose the changed status; it cannot erase the fact that outcomes were seen.

The final statement should distinguish **forecast skill, better information, better architecture at matched information, calibrated risk/event forecasts, and net trading value**. The project need not claim all five to produce a meaningful research result.

---

## 11. Validation changes that expansion cannot substitute for

### 11.1 A larger cross-section does not refresh reused development

The same July–December 2025 outcomes have influenced many design decisions. Adding stocks to those dates creates a new cross-section but not an independent market history. Results on that period remain development evidence, including results on newly added names that share market shocks.

Historical rolling-origin evaluations can assess stability when every fit respects its cutoff. However, the architecture has already been designed using later experience; a retrospective walk-forward is not automatically a pristine prospective test. Label it honestly and keep the genuinely unopened confirmation protected.

The existing January–March 2026 restrictions should remain in place during expansion planning and source-quality checks. No new-stock numerical outcomes from that protected period should be used to choose the expanded universe or architecture without an explicitly revised confirmation policy.

### 11.2 Separate time generalization from security generalization

A broader panel supports two different checks: predicting future dates for previously seen securities, and transferring to securities excluded from training. They address different risks. A model with ticker-specific embeddings or a fixed stock-axis mixer cannot be presented as naturally transferable to unseen names without an appropriate design.

Sector or issuer clustering should be respected when constructing security holdouts. All future-date claims still require chronological training, matured labels, and protected outcomes. The cross-security test does not replace the temporal one.

### 11.3 Seeds, blocks, and repeated selection

Neural seeds measure optimization variation conditional on the same history, not independent market replications. Pair candidate and comparator seeds where sensible and report all predeclared seeds; do not compare a weak baseline seed against a convenient treatment seed.

Preserve entire date/origin cross-sections in uncertainty calculations. A row bootstrap over hundreds of stocks can manufacture precision. The existing one-/two-month, 400-replicate intervals over six development months are sensitivity summaries, not universal significance tests. More bootstrap draws cannot manufacture more independent months.

White's data-snooping framework and the backtest-overfitting literature explain why searching many alternatives changes inference. They do not automatically validate a particular resampling procedure under nonstationarity; the null, dependence assumptions, and candidate family must be specified. [R20] [R21]

Maintain a ledger of successful, failed, inactive, rescued, and abandoned hypotheses. Reused-development superiority is a reason to nominate a candidate for stronger testing—not a final discovery.

### 11.4 Do not use a universal “good IC” threshold

IC depends on universe size/composition, horizon, information set, dependence, exposure, trading rule, and costs. A value such as 0.05 can be useful in one application and economically irrelevant or unstable in another. The original rough IC bands should not become acceptance thresholds.

For the expanded model, use paired improvement against appropriate baselines, time stability, economically relevant tail selection, and honest net accounting. Report both origin and equal-day IC because their weights differ when sessions have different origin counts.

---

## 12. Mandatory diagnostic contract for the next phase

This contract preserves the user's detailed requirements. It is not satisfied by a headline MSE/IC table or an engineering PASS label.

### 12.1 One keyed table linking target, prediction, and economic outcome

For every permitted evaluated observation retain, or deterministically reconstruct:

- security/session/origin, causal input/entry eligibility, supervised validity, and source/recipe/checkpoint identifiers;
- original price-return outcome, target numerator, median, unscaled MAD, epsilon, normalization denominator, original target, and transformed target;
- original model output, transformed prediction, once-only inverse prediction, individual original squared error and actual objective loss;
- session/origin/stock weights, native/fallback/age/quality information, and the current universe definition.

These are private diagnostic records, not new model inputs by default. Report aggregates and a bounded witness set instead of duplicating raw prices or storing every activation.

### 12.2 All four roles, with their different meanings

Inner-training and refit diagnostics are in sample. Inner validation selects training duration. Development is exploratory. Protected confirmation remains closed until separately authorized. Do not combine these roles as independent out-of-sample evidence.

Record online dropout-ON optimization separately from fixed-checkpoint dropout-OFF loss. Every numerical comparison must specify the actual loss space and weights.

### 12.3 Extreme-target, extreme-error, and numerator/denominator cohorts

Use original untransformed absolute target magnitude to define the designated extreme-target cohorts, then calculate transformed and original errors on exactly those observations. Separately identify extreme-error cohorts and fixed training-threshold event cohorts.

For the prespecified percentiles and numerator/MAD thresholds, show row counts, distinct sessions/origins, weight mass, thresholds, error distributions, weighted loss contributions, and loss shares. Preserve positive/negative sides, `NUM_ONLY`, `MAD_ONLY`, `BOTH`, `NEITHER`, floor activity, and relevant source-quality strata. Explain overlaps; a target top-5% set is not the union of two marginal top/bottom-5% sets.

Compare against T2 and other selected controls on **identical keyed observations**. Reconcile cohort sums to total actual objective and original MSE. Do not calculate one model's improvement using its own favorable evaluation subset.

### 12.4 Error attribution rather than merely loss concentration

Include the exact common-level/centered-vector MSE decomposition; forecast energy versus forecast–outcome alignment; stock- and time-level contributions; score dispersion and ties; top/bottom retrieval; calibration fitted only on permitted earlier data; and stability of rankings under small input changes.

A slope above one is a diagnostic, not authorization to rescale on development. One hundred percent of origins changing at least one rank under a perturbation is not proof of meaningful information use; report the size of rank and portfolio changes and score margins.

### 12.5 Learning and mechanism diagnostics

Retain selected/raw-best epochs, fresh initialization and optimizer identities, complete update counts, gradient/clip distributions, finite checks, parameter groups, and exact reloads. For active mechanisms, test the relevant null/identity behavior, gradient connectivity, information matching, masks, and stock-axis conventions.

A source replacement or historical donor perturbation creates a distribution shift. It is not automatically a valid permutation null or a causal identification test. Attention, gates, expert entropy, and Jacobians are computational diagnostics; economic interpretations require separate evidence.

### 12.6 Readable deliverables

Each approved later package should provide a concise diagnosis plus the detailed Markdown/CSV/JSON tables, exact artifact links, dashboard views, and a small trace set. Every conclusion should state the supporting evidence, competing explanations, and smallest discriminating follow-up. No result may be described as complete solely because the original instruction requested it.

The same source case replayed through three models remains one market event, not three independent examples. Source/rights/publication assumptions and the experiment ledger must be visible in the report rather than hidden in engineering logs.

---

## 13. Decisions and unknowns to resolve later—not assumptions to invent now

| Item | Current knowledge | Required resolution before the relevant implementation |
|---|---|---|
| Expanded S&P membership meaning | User requires S&P 500 stocks; no selection made | Point-in-time versus fixed as-of-date survivor convention |
| Exact expanded size | Approximately 200–300 or another justified number is contemplated | Coverage/diversity/compute decision, independent of predictive outcomes |
| Historical membership and outcomes | Not established by present source reports | Obtain/verify suitable records under permitted access |
| Executable prediction outcome | Current HF20 endpoints are price-only and start before modeled issuance | Freeze post-availability entry/exit and horizon semantics |
| Current-source strong baseline coverage | Old baseline plans exist; not all current matched results are established | Inventory actual fitted models and their information sets |
| Detailed current FT16 formula matrix | P020 summary and some conventions verified | Read the exact current formula/recipe matrix before changing any input |
| Full paired T2 tail decomposition | Aggregate and candidate tables exist; complete paired rows not supplied here | Retrieve/derive read-only same-cohort original/z errors |
| Effect of longer history | Long-history dataset exists | Matched window experiment only if later justified |
| E1 calibration and QR1 conditional risk comparisons | Interesting task-specific evidence; not replicated robust claims | Separate calibrated/risk-baseline investigation if prioritized |
| Realized costs/borrow/fills | No new HF20 trading evidence established | Research execution model and disclosed assumptions, not fictitious observed fills |
| A9/A10/A11 performance | No results | Remain paused; do not assign inferred failures or successes |
| Additional prior-thread results not in sources | Not fully recoverable | Ask for the missing report if it materially changes a decision |

These uncertainties do not prevent writing this plan. They do prevent pretending the expanded protocol is already frozen or executable.

---

## 14. Final recommendation and decision rule

### The strongest practical conclusion

**Expand the research opportunity set, not just the tensor size.** A useful larger panel should bring cleaner causal information, broader security coverage, an explicit economic target, variable-universe handling, and stronger validation. A 300-stock version of the exact same unresolved measurement and evaluation assumptions is not a fundamental fix.

I would retain the present compact LSTM as the architectural reference. Its weak results do not show that LSTMs cannot support trading, and the literature does not justify abandoning recurrence solely because twenty stocks did not yield robust improvements. At the same time, no literature finding licenses promising success from a particular number of names or a more elaborate cell.

The most important pre-expansion work is **not** another architecture. It is a bounded check of source/feature quality, causal execution relevance, the transformed forecast functional, and the source of apparent gains. Those checks can mostly be made without training. Any verified fundamental defect should be fixed on a small slice before scaling. Otherwise, proceed to the broader universe rather than spending the remaining budget trying to force a winner from HF20.

### Decision sequence

**Now:** preserve the results and pause fits.

**Before expansion:** resolve only material source/clock/task/masking issues; perform the targeted read-only diagnosis.

**Next major experiment:** a broader S&P 500 panel with a simple shared LSTM and strong matched baselines, designed to separate more training assets, more peer information, and a larger tradable universe.

**Then:** choose one representation, objective, or adaptation change from actual diagnostic evidence. Revisit A4–A6 and A7/A12 under the stronger design when justified. A9–A11 and the remaining 10+3 possibilities stay available, not compulsory.

**Eventually:** judge the system by reproducible out-of-period prediction and net trading value, with source assumptions and model-selection uncertainty honestly reported.

This is a plan to learn what can be improved—not a prediction that expansion or any particular method will generate alpha.

---

## 15. Research references and reading priorities

This is a targeted methodological review, not an exhaustive meta-analysis of every stock-LSTM publication. Publication dates below refer to the identified paper/version, not webpage crawl dates. Public abstracts, publisher/author records, and accessible full HTML were used; no claim is made to have independently replicated the papers. The foundational arguments here do not depend on unverified recent paper-performance claims from the older project literature notes.

### R01 — Fischer and Krauss: broad equity LSTM evidence and its limits

Fischer, T., and Krauss, C. (2018). **Deep learning with long short-term memory networks for financial market predictions.** *European Journal of Operational Research*, 270(2), 654–669. DOI: [10.1016/j.ejor.2017.11.054](https://doi.org/10.1016/j.ejor.2017.11.054).

Publisher abstract/sections inspected. Direct equity-LSTM precedent; the reported weakening of cost-adjusted performance after 2010 is especially relevant to interpreting modern-period expectations. No reported return is used as a target for HF20.

### R02 — DeepLOB: why stock count is not a universal adequacy measure

Zhang, Z., Zohren, S., and Roberts, S. (2019). **DeepLOB: Deep Convolutional Neural Networks for Limit Order Books.** *IEEE Transactions on Signal Processing*, 67(11), 3001–3012. [Author manuscript](https://arxiv.org/abs/1808.03668); [full HTML inspected](https://arxiv.org/html/1808.03668).

Supports the distinction between number of stocks and information/sample structure. Its LOB setting and simplified trading assumptions are not interchangeable with hourly OHLCV.

### R03 — Sirignano and Cont: shared representations across stocks

Sirignano, J., and Cont, R. (2019). **Universal features of price formation in financial markets: perspectives from deep learning.** *Quantitative Finance*, 19(9), 1449–1459. DOI: [10.1080/14697688.2019.1622295](https://doi.org/10.1080/14697688.2019.1622295). [Author manuscript](https://arxiv.org/abs/1803.06917); [full HTML inspected](https://arxiv.org/html/1803.06917).

Relevant to pooled learning and security transfer; its rich event-level information is a major limitation on transfer to HF20.

### R04 — Montero-Manso and Hyndman: global versus local forecasting

Montero-Manso, P., and Hyndman, R. J. (2021). **Principles and algorithms for forecasting groups of time series: locality and globality.** *International Journal of Forecasting*, 37(4), 1632–1653. DOI: [10.1016/j.ijforecast.2021.03.004](https://doi.org/10.1016/j.ijforecast.2021.03.004). [Author manuscript](https://arxiv.org/abs/2008.00444).

Publisher, author, and university summaries inspected. The theory motivates pooling; it supplies no stock-count threshold for reliable financial alpha.

### R05 — Lim, Zohren, and Roberts: trading-objective alignment

Lim, B., Zohren, S., and Roberts, S. (2019). **Enhancing Time-Series Momentum Strategies Using Deep Neural Networks.** *The Journal of Financial Data Science*, 1(4), 19–38. DOI: [10.3905/jfds.2019.1.015](https://doi.org/10.3905/jfds.2019.1.015). [Author manuscript](https://arxiv.org/abs/1904.04912); [full HTML inspected](https://arxiv.org/html/1904.04912v3).

Relevant to position objectives and turnover-aware learning; not a direct validation of short-horizon cross-sectional equity forecasting.

### R06 — MASTER

Li, T., Liu, Z., Shen, Y., Wang, X., Chen, H., and Huang, S. (2024). **MASTER: Market-Guided Stock Transformer for Stock Price Forecasting.** *Proceedings of AAAI*, 38(1), 162–170. [Official publication](https://ojs.aaai.org/index.php/AAAI/article/view/27767).

Official record/abstract inspected; background for conditioning and information exchange. A7's two endogenous proxies are not a reproduction of the original full information design.

### R07 — StockMixer

Fan, J., and Shen, Y. (2024). **StockMixer: A Simple Yet Strong MLP-Based Architecture for Stock Price Forecasting.** *Proceedings of AAAI*, 38(8), 8389–8397. [Official publication](https://ojs.aaai.org/index.php/AAAI/article/view/28681).

Official record/abstract inspected. Motivates efficient information exchange; P027 A5 tests an adaptation, not every component of StockMixer.

### R08 — DeepAR

Salinas, D., Flunkert, V., Gasthaus, J., and Januschowski, T. (2020). **DeepAR: Probabilistic forecasting with autoregressive recurrent networks.** *International Journal of Forecasting*, 36(3), 1181–1191. DOI: [10.1016/j.ijforecast.2019.07.001](https://doi.org/10.1016/j.ijforecast.2019.07.001).

Publisher summary inspected. A methodological precedent for shared probabilistic RNNs, not empirical evidence of equity-return predictability.

### R09 — Point forecasts, statistical functionals, and losses

Gneiting, T. (2011). **Making and Evaluating Point Forecasts.** *Journal of the American Statistical Association*, 106(494), 746–762. DOI: [10.1198/jasa.2011.r10138](https://doi.org/10.1198/jasa.2011.r10138).

Publisher abstract and detailed summary inspected. Central reference for matching a forecast's statistical meaning to its loss and evaluation.

### R10 — Proper probability and distribution scoring

Gneiting, T., and Raftery, A. E. (2007). **Strictly Proper Scoring Rules, Prediction, and Estimation.** *Journal of the American Statistical Association*, 102(477), 359–378. DOI: [10.1198/016214506000001437](https://doi.org/10.1198/016214506000001437).

Publisher record/abstract consulted. Supports evaluating probability calibration and distributional forecasts using appropriate scores rather than point-forecast amplitude.

### R11 — Retransformation

Duan, N. (1983). **Smearing Estimate: A Nonparametric Retransformation Method.** *Journal of the American Statistical Association*, 78(383), 605–610. DOI: [10.1080/01621459.1983.10478017](https://doi.org/10.1080/01621459.1983.10478017).

Publisher record/summary consulted. The asinh equations in Section 5 are direct derivations; they are not a claim that this paper validates a particular HF20 correction.

### R12 — Forecasts, turnover, and costs

Gârleanu, N., and Pedersen, L. H. (2013). **Dynamic Trading with Predictable Returns and Transaction Costs.** *The Journal of Finance*, 68(6), 2309–2340. DOI: [10.1111/jofi.12080](https://doi.org/10.1111/jofi.12080). [NBER working-paper record](https://www.nber.org/papers/w15205).

Publisher/NBER summaries consulted. Relevant to translating noisy, decaying forecasts into cost-aware positions, not a guarantee of a signal.

### R13 — Missingness and elapsed-time information

Che, Z., Purushotham, S., Cho, K., Sontag, D., and Liu, Y. (2018). **Recurrent Neural Networks for Multivariate Time Series with Missing Values.** *Scientific Reports*, 8, 6085. DOI: [10.1038/s41598-018-24271-9](https://doi.org/10.1038/s41598-018-24271-9).

Publisher article consulted. The clinical application supports a modeling principle about masks/intervals, not a demonstrated financial edge or a requirement to implement GRU-D.

### R14 — Learned price representations

Jiang, J., Kelly, B., and Xiu, D. (2023). **(Re-)Imag(in)ing Price Trends.** *The Journal of Finance*, 78(6), 3193–3249. DOI: [10.1111/jofi.13268](https://doi.org/10.1111/jofi.13268). [Yale research record](https://economics.yale.edu/research/re-imagining-price-trends).

Publisher/author summaries consulted. Motivates scrutinizing the representation of price paths; does not establish that image encoding or a CNN should replace this LSTM project.

### R15 — Estimation windows under structural breaks

Pesaran, M. H., and Timmermann, A. (2007). **Selection of estimation window in the presence of breaks.** *Journal of Econometrics*, 137(1), 134–161. DOI: [10.1016/j.jeconom.2006.03.010](https://doi.org/10.1016/j.jeconom.2006.03.010).

Publisher abstract inspected. Supports the bias–variance trade-off in retaining older data; it does not justify selecting a recent window after looking at the final test.

### R16 — Intraday timing

Heston, S. L., Korajczyk, R. A., and Sadka, R. (2010). **Intraday Patterns in the Cross-section of Stock Returns.** *The Journal of Finance*, 65(4), 1369–1407. DOI: [10.1111/j.1540-6261.2010.01573.x](https://doi.org/10.1111/j.1540-6261.2010.01573.x).

Publisher/author summaries inspected. Motivates checking session-specific information; historical effects are not assumed to persist in HF20.

### R17 — Intraday predictive information at a different horizon

Huddleston, D., Liu, F., and Stentoft, L. (2023; online 2021). **Intraday Market Predictability: A Machine Learning Approach.** *Journal of Financial Econometrics*, 21(2), 485–527. DOI: [10.1093/jjfinec/nbab007](https://doi.org/10.1093/jjfinec/nbab007).

Publisher abstract inspected. Five-minute market prediction from constituent information is distinct from four-hour stock-relative ranking.

### R18 — Factor-residual statistical arbitrage

Avellaneda, M., and Lee, J.-H. (2010). **Statistical arbitrage in the US equities market.** *Quantitative Finance*, 10(7), 761–782. DOI: [10.1080/14697680903124632](https://doi.org/10.1080/14697680903124632).

Publisher abstract and methodological notes inspected. Residual mean reversion is a model assumption to test, not an automatic property obtained by regression or PCA.

### R19 — Filtering can create misleading dynamics

Hamilton, J. D. (2018). **Why You Should Never Use the Hodrick-Prescott Filter.** *The Review of Economics and Statistics*, 100(5), 831–843. DOI: [10.1162/rest_a_00706](https://doi.org/10.1162/rest_a_00706). [NBER working-paper record](https://www.nber.org/papers/w23429).

NBER/publisher summary consulted. A warning about filtering assumptions; not a proof against every causal denoiser.

### R20 — Data snooping

White, H. (2000). **A Reality Check for Data Snooping.** *Econometrica*, 68(5), 1097–1126. DOI: [10.1111/1468-0262.00152](https://doi.org/10.1111/1468-0262.00152).

Publisher abstract consulted. Relevant to accounting for the searched family, with method-specific dependence assumptions.

### R21 — Backtest overfitting

Bailey, D. H., Borwein, J. M., López de Prado, M., and Zhu, Q. J. (2017). **The probability of backtest overfitting.** *The Journal of Computational Finance*, 20(4), 39–69. DOI: [10.21314/JCF.2016.322](https://doi.org/10.21314/JCF.2016.322).

Publisher record/summary consulted. Motivates controlling research-selection risk; no claim that one combinatorial validation procedure automatically solves this nonstationary panel.

### R22 — Strong simple/nonlinear financial prediction controls

Gu, S., Kelly, B., and Xiu, D. (2020). **Empirical Asset Pricing via Machine Learning.** *The Review of Financial Studies*, 33(5), 2223–2273. DOI: [10.1093/rfs/hhaa009](https://doi.org/10.1093/rfs/hhaa009).

Publisher material consulted. Broad monthly asset-pricing evidence for careful nonlinear/comparator design; not an hourly LSTM performance benchmark.

### R23 — Universe definition

S&P Dow Jones Indices. **S&P U.S. Indices Methodology.** [Official methodology page](https://www.spglobal.com/spdji/en/methodology/article/sp-us-indices-methodology/), accessed 24 October 2026.

Official page inspected. Current methodology is not a substitute for historical constituent and security-event records.

### R24 — Modern recurrent architecture, retained but deferred

Beck, M., et al. (2024). **xLSTM: Extended Long Short-Term Memory.** *Advances in Neural Information Processing Systems*, 37. [Official NeurIPS publication](https://proceedings.neurips.cc/paper_files/paper/2024/hash/c2ce2f2701c10a2b2f2ea0bfa43cfaa3-Abstract-Conference.html); [author manuscript](https://arxiv.org/abs/2405.04517).

Official abstract inspected. Its language-modeling evidence motivates possible memory experiments, not an automatic escalation of a small financial forecasting model.

### R25 — Qualification to the filtering discussion

Moura, A. (2024). **Why You Should Never Use the Hodrick-Prescott Filter. A Comment on Hamilton (The Review of Economics and Statistics, 2018).** *Journal of Comments and Replications in Economics*, 3(1). [Journal article](https://www.ojs.jcr-econ.org/index.php/jcre/article/view/16); [central-bank working-paper record](https://www.bcl.lu/en/publications/Working-papers/162/index.html).

Journal/working-paper summaries consulted. Included narrowly to avoid presenting one proposed replacement filter as immune to the same general issue of induced dynamics.

**Suggested reading order for this project:** R01 and R04 for the panel-size question; R09 and R11 for the target/loss issue; R13 for missingness; R20/R21 for evidence discipline; then the mechanism-specific papers only when the corresponding hypothesis is selected.

---

## Appendix A. Mathematics and numerical checks used in this review

The equations concerning conditional means, inverse transformations, cross-sectional decomposition, weighted cross-entropy, rolling sums, and completeness probabilities are derivations for this review. They are not newly measured model results.

- T2 reduction versus ZERO: \(1-3.106560/3.1165604\approx0.003209\), or about 0.321%.
- A7/A12 forecast SDs are approximately 3.15%/3.04% of target SD. Those ratios are descriptions, not desired calibration targets.
- A7 refit conditional z-MSE for a cohort is its weighted objective contribution divided by its evaluation weight mass, not its contribution divided by row percentage.
- The four numerator/MAD groups are disjoint; the ranked-target cohorts overlap those groups and must not be added to them.
- A monotone inverse preserves a particular prediction ranking, while exchanging nonlinear transformation and conditional expectation is generally invalid.
- Lower training loss and finite aggregate gradients do not establish adequate temporal credit assignment; conversely, low market predictability is not demonstrated solely by a failed nonlinear fit.

No model was fitted, no raw market dataset was accessed, and no protected numerical outcomes were examined to create this document.

## Appendix B. Minimal future hypothesis card

For each later proposed change, record:

**Question:** What precise limitation is being tested?  
**Evidence:** Which project observation motivates it, and what contradicts it?  
**Information contract:** Which histories, peers, masks, external states, and matured labels may be observed?  
**Outcome:** Exact economic return, relative target, probability, or quantile being forecast.  
**Comparator:** Strongest simpler model with comparable information and training budget.  
**One change:** Input, target, sampling, loss, architecture, or execution—not several silently combined.  
**Evaluation:** Predeclared primary metric, secondary guardrails, paired population, folds/seeds, costs where relevant.  
**Failure interpretation:** Implementation failure, no validation gain, weak information, inadequate support, or unresolved.  
**Maximum follow-up:** What evidence permits one rescue, and what stops the branch?  
**Authorization:** Explicit approval, immutable configuration, ledger effect, and protected-data restrictions.

This makes a negative result useful rather than merely the reason to try another model.

## Appendix C. Project evidence and authority register

### P01 — Current HF1M-long data/feature/target contract

`Pasted markdown(20261023-023925).md`, Package 020 Codex session report, recovered from the available Library/Project file search and read in full. Key sections: 3 (chronology and source-specific policies), 7–8 (loader, target and provenance), 11 (actual counts/fallbacks), 14 (limitations). Its reported tests were not rerun for this review.

### P02 — Long-history C0/T2 results

`Pasted markdown(20261023-050943).md`, Package 021 session report, indexed sections and results recovered through file search and corroborated by later comparison tables. A direct full-text read was unavailable in this pass; numerical conclusions are limited to visible excerpts and supplied later reports.

### P03 — Alternative objective/event screen

`Pasted markdown(20261023-155459).md`, Package 022 collective comparison. Indexed development regression/classification tables and diagnosis recovered through file search; full direct read unavailable in this pass. E1 discrimination, unweighted scoring, and calibration distinctions use those visible tables.

### P04 — Direction/magnitude, quantiles, and sampling

`Pasted markdown(20261023-171525).md`, Package 023 collective comparison, read in full. Contains DM1, QR1, SS1, constant references, interval sensitivity, and explicit scientific holds.

### P05 — Optimization/capacity screen

`Pasted markdown(20261023-205959).md`, Package 024 collective comparison. Results, selection/optimization, and role comparisons retrieved/read. Later sections also appear in the conversation's recovered source excerpts. No unseen replicate is assumed.

### P06 — Temporal architecture screen

`Pasted markdown(20261024-010748).md`, Package 026 comparison. Indexed outcome and uncertainty sections recovered through file search; direct full read unavailable in this pass.

### P07 — Cross-stock screen

P027 final human review, researcher diagnosis, matched comparison, peer falsification, gradients, and transformed-tail tables pasted by the user in this conversation. The repository-local linked files were not independently opened. Their claims are treated as reported evidence with the disclosed source limitations.

### P08 — Market-state screen and source preparation

P028 preparation, construction/support audit, readiness report, final human review, matched comparison, and A7/A8/A12 reports pasted by the user. The 18-input control is absent; A8 is explicitly the one-way reduction; state channels are endogenous panel proxies. The reporting-only ledger correction is preserved as a disclosure, not independently verified repository history.

### P09 — P028 detailed tail diagnostics

Uploaded `Pasted markdown (2)(7).md`: **P028 true transformed-objective tails**, fully provided. Includes all four roles, ranked original-target cohorts, numerator/MAD partitions, magnitude ranges, and training-frozen event errors/recall.

### P10 — P028 architecture and gradient details

Uploaded `Pasted markdown(20261024-060423).md`: conditional design-freeze proposal, subsequently approved by the user for the completed package; uploaded `Pasted markdown(20261024-135923).md`: complete fitting and gradient accounting. The executed scope is corroborated by the supplied P028 closeout. Merely counting parameters in a proposal was not treated as proof of fitted behavior.

### P11 — Research background and audit contracts

`Shared_Project_Specification.md`; `Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md`; `Consolidated_Architecture_Design_Menu.md`; `Recurrent_Architecture_Research.md`; `State_Dependent_Signed_Recurrent_Interactions.md`; `Track_A_Stage_Gated_Audit_and_Failure_Traceability_Plan_v1.1_2026-10-10.md`; the consolidated implementation design record and incremental review plan.

These provide hypotheses and audit principles. They do not override newer explicit HF20 source/chronology decisions. Older literature notes are not used to substantiate unverified empirical claims about the current dataset.

### P12 — Latest user instruction

The present request pauses further experiments, defers all A1–A12/10+3 revisits, and prioritizes a critical reassessment followed by careful larger-S&P-universe planning. It supersedes the earlier assumption that Experiment 4 would automatically come next.

---

## Persistent notes for the next discussion

**Retain:** A4's coarse peer summaries may discard useful individual innovations; revisit cross-stock access after expansion. A7/A12's original-MSE versus z-loss/ranking trade-off merits a matched read-only decomposition and later targeted development. Preserve E1 and QR1 as separate event/distributional hypotheses.

**Do not infer:** that twenty stocks caused failure; that more stocks guarantee success; that every untested architecture failed; that near-zero means must be inflated; that all heavy targets are bad observations; or that supplied engineering gates independently certify investable data.

**Next major direction:** a broader, carefully specified S&P 500 research panel after a short fundamental-design review. No ticker selection or experiment authorization is contained in this file.

[R01]: https://doi.org/10.1016/j.ejor.2017.11.054
[R02]: https://arxiv.org/abs/1808.03668
[R03]: https://arxiv.org/abs/1803.06917
[R04]: https://doi.org/10.1016/j.ijforecast.2021.03.004
[R05]: https://doi.org/10.3905/jfds.2019.1.015
[R06]: https://ojs.aaai.org/index.php/AAAI/article/view/27767
[R07]: https://ojs.aaai.org/index.php/AAAI/article/view/28681
[R08]: https://doi.org/10.1016/j.ijforecast.2019.07.001
[R09]: https://doi.org/10.1198/jasa.2011.r10138
[R10]: https://doi.org/10.1198/016214506000001437
[R11]: https://doi.org/10.1080/01621459.1983.10478017
[R12]: https://doi.org/10.1111/jofi.12080
[R13]: https://doi.org/10.1038/s41598-018-24271-9
[R14]: https://doi.org/10.1111/jofi.13268
[R15]: https://doi.org/10.1016/j.jeconom.2006.03.010
[R16]: https://doi.org/10.1111/j.1540-6261.2010.01573.x
[R17]: https://doi.org/10.1093/jjfinec/nbab007
[R18]: https://doi.org/10.1080/14697680903124632
[R19]: https://www.nber.org/papers/w23429
[R20]: https://doi.org/10.1111/1468-0262.00152
[R21]: https://doi.org/10.21314/JCF.2016.322
[R22]: https://doi.org/10.1093/rfs/hhaa009
[R23]: https://www.spglobal.com/spdji/en/methodology/article/sp-us-indices-methodology/
[R24]: https://arxiv.org/abs/2405.04517
[R25]: https://www.ojs.jcr-econ.org/index.php/jcre/article/view/16
[P01]: #p01--current-hf1m-long-datafeaturetarget-contract
[P02]: #p02--long-history-c0t2-results
[P03]: #p03--alternative-objectiveevent-screen
[P04]: #p04--directionmagnitude-quantiles-and-sampling
[P05]: #p05--optimizationcapacity-screen
[P06]: #p06--temporal-architecture-screen
[P07]: #p07--cross-stock-screen
[P08]: #p08--market-state-screen-and-source-preparation
[P09]: #p09--p028-detailed-tail-diagnostics
[P10]: #p10--p028-architecture-and-gradient-details
[P11]: #p11--research-background-and-audit-contracts
[P12]: #p12--latest-user-instruction
