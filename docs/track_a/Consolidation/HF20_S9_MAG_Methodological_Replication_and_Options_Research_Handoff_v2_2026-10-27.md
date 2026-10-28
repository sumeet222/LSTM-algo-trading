# HF20 S9-MAG — Consolidated Reproducible Methodology, Completed Evidence, and Future Options-Strategy Research (v2)

**Research handoff for a new ChatGPT project conversation**  
**Prepared:** 27 October 2026  
**Revision:** v2 — integrated FT16 and S9-MAG code/recipe extracts delivered 27 October 2026  
**Standard:** Reproducible **methodology**, not a promise of bitwise-identical replay  
**Status:** S9-MAG historical experiment **completed and archived**; follow-up magnitude-LSTM experiments and options trading studies **not yet authorized or executed**.  
**Intended reader:** A researcher who has this document and access to the HF20 local research repository. This document provides the hypotheses, design, mathematical definitions, published-by-this-project results, reconstruction instructions, analysis limitations, and proposed downstream trading research. It does **not** include proprietary underlying OHLCV files, neural checkpoints, or historical options quotes.

> **Important handoff instruction.** Treat this as a *new, separate research thread* devoted to S9-MAG and its possible conversion to risk/options signals. Do **not** initiate training, source downloads, trading simulations, strategy tuning, deployment, protected-data reads, or a new architecture campaign without the user's specific authorization. The user has already inspected the two dashboards and **does not request further dashboard work**; current HF20 priority is the separate novel-architecture research, and this S9-MAG/options study is reserved for later. This handoff is deliberately preserved for later.

---

## 0. Executive summary: what succeeded, and what did not

Our HF20 stockwise LSTM struggled to predict the **direction or cross-sectional ranking** of future four-trading-hour returns. A separate S9 family asked whether identical historical OHLCV-derived inputs could forecast *future movement size* more reliably. The **S9-MAG** arm directly predicted the absolute log return across the project’s genuine four-trading-hour endpoints.

**Main exploratory finding:** On the 2021–2024 walk-forward research folds, S9-MAG reduced **transformed-target mean-squared error** by **13.7% against a training-prefix stock-specific constant baseline**, and by **13.3% against a trailing-volatility-based control**. Both proper-loss comparisons were better in each of four years. In **raw absolute-log-return units**, MAE improved from **0.006903 to 0.006505** versus the stock control (~**5.8%**). The model’s magnitude-ranking association was reported as **0.408**. The performance is supported by paired out-of-sample comparisons, although these four years have been revisited across many research decisions and are **not** untouched confirmatory data.

The key unresolved problem is **calibration**: mean reported predicted `|R|` is **0.00836**, versus observed **0.01031**. The model often misses the size of extreme moves. Moreover, a model of four-hour **endpoint** absolute return does **not** directly predict the realized integrated path variance, a signed return, an option’s P&L, or whether implied volatility is mispriced.

**Future hypothesis (not yet tested):** Properly calibrated S9-MAG forecasts, compared with *synchronized option-implied expected movements*, may help select **long-straddle** entries when forecasted movement materially exceeds the market-implied threshold. Causal smoothing, entry/exit hysteresis, liquidity and option repricing must be evaluated in a separately pre-registered trading study. The signal must beat **implied-volatility-only, realized-volatility-only, and no-trade** alternatives *after bid–ask and fees*.

The established result is about **predictive accuracy**, not alpha, volatility risk premia, option profitability, or executable fills.

### Source-of-truth hierarchy

1. **Actual executed S9 runs, run-specific `configuration.json`, phase target recipes, checkpoint/refit bindings, and saved score Parquets** in the local repository govern exact reproduction.
2. `S9_TARGET_AND_BASELINE_CONTRACT.md`, `S4_REUSED_RECIPES.json`, and the completed numerical/decision reports govern executed target and baseline semantics.
3. The two **executed-code extraction documents incorporated below** establish named FT16 features, minute/source handling, phase scales, actual control formulas, fold-role counts, default initialization and the S9 MAG loss selector. The exact facts and original source references are reproduced in §2–§5 and preserved in full in Annexes A–B. Their readings were not independently re-run here.
4. Proposed changes and option-trading ideas in later sections are **new research**, not part of the executed experiment.

---

## 1. Prior research and why magnitude forecasting was a reasonable hypothesis

### 1.1 Original HF20 problem

HF20 uses a fixed panel of 20 large US equities; each stock has **16 engineered FT16 input features** measured at completed scheduled hourly steps. One small LSTM is trained **across all stocks** but, in the original backbone, each stock’s 48-step sequence is encoded **separately**, not with direct real-time observation of the other 19 stocks inside its forward pass. Its original task was predicting four-trading-hour signed return/relative return ranking. Ranking outcomes are strongly noisy and dependent on other stocks’ behavior; price movement *magnitude* may have more persistent conditional structure.

The latter sentence was a **research hypothesis**, not a mathematical consequence of the data or proof of why direction was weak. Bigger cross-sections, peer-aware architectures, different targets, or better representations might change directional performance.

### 1.2 Antecedent evidence, in chronological scientific order

| Earlier experiment | Source-derived evidence | Why it mattered for S9-MAG |
|---|---|---|
| Earlier development `DM1` direction/magnitude decomposition | Reported magnitude-error improvement against a prefix constant but near-chance signed prediction / cancellation; historical magnitude target units differ and require reference to that experiment. | Suggested that some size information might be learnable even when signed regression fails. **Not** proof that DM1 predicted raw four-hour `|R|`. |
| Earlier development `E1` tail-event classifier | ANY-tail average precision ~0.132 vs pooled-prior prevalence ~0.0415, but unweighted cross-entropy ~0.2357 vs prior ~0.2023; signed ordinal IC ~−0.0037. | Encouraged testing tail-related predictability while emphasizing that discrimination alone is not calibrated risk forecasting. |
| Earlier development `QR1` quantile model | Average pinball ~0.22608 vs pooled unconditional ~0.22983; apparent improvement mainly in **outer quantiles**, weak median. | Suggested conditional dispersion/tail structure independent of mean signed direction. |
| Ranking `S1/S2` | Baselines and NR/T2R recurrent rank forecasting; no stable demonstrated trading edge. | Motivated testing a different economically meaningful target rather than claiming rank success. |
| `S3` horizon/M2 alignment | Two-hour aligned T2R ranking IC improved relative to one comparison by +0.015958 with descriptive interval [−0.000770,+0.029417]; the interval includes zero and primary absolute IC was weak. | Shorter horizon alone did not resolve signed-ranking difficulty. |
| `S4-A` seven-origin, four-trading-hour ranking | T2R equal-year OOS Rank IC ~+0.005921; NR ~+0.003818; M1 momentum ~+0.003383. Paired LSTM-versus-M1 descriptive intervals included zero. | More evaluation origins alone did not establish reliable directional ranking advantage. Its data, timing and fold machinery became S9-MAG’s frozen foundation. |

All development and research OOS results above must be interpreted **post-search/exploratorily**. Do not treat each antecedent experiment as an independent validation. Source references: `HF20_LSTM_Comprehensive_Review_and_Expansion_Plan_2026-10-24.md` §3, `HF20_S3_Horizon_Comparison_and_Aligned_M2_Codex_Prompt_2026-10-25.md`, executed `S3_FINAL_RESEARCH_DECISION.md`, and executed S4 report, plus the uploaded S5/S9 final decision.

### 1.3 The completed four-arm S5/S9 campaign

The campaign fixed **four configurations × four annual folds**, all using seed 42:

| Arm | Objective | Completed | Equal-year OOS result | Conclusion |
|---|---|---:|---|---|
| **S5 `META-T2R`** | Original transformed signed-ranking regression plus six verified clock channels | 4/4 | Daily Rank IC 0.008904; paired vs S4 T2R +0.002983 [−0.010230,+0.014905] | **Inconclusive** incremental ranking skill; not a causal missingness effect |
| **S9 `MAG`** | MSE of log1p-transformed raw four-hour absolute endpoint log return | 4/4 | MSE 0.232454; vs STOCK −0.036929 [−0.042946,−0.031723] | **Qualified promising movement-size prediction** |
| **S9 `EVENT`** | Original E1-compatible natural three-class cross entropy | 4/4 | CE 0.202028 vs stock-prior 0.196030; Δ +0.005998 [+0.002984,+0.009021] | **No incremental proper-score advantage** over stock priors |
| **S9 `QUANTILE`** | Signed TG20 5/50/95% asinh-space pinball | 4/4 | Pinball 0.230705 vs stock quantiles 0.230242; Δ +0.000464 [+0.000035,+0.000914] | **No incremental proper-score advantage** over stock quantiles |

`S5` has metadata, but **all S9 models use the original S4 FT16 and do not use S5’s six clock channels**. The S9 tasks are distinct; do not compare their numeric objective values to one another as if measuring the same outcome.

Campaign status: **16/16 technical PASS**, **32 prefix-recipes**, **64 campaign control receipts/outputs**, research-start ledger **114 → 130/200**, **zero failed neural starts/retries**. **Qualification:** Not all controls have fitted coefficients: MAG `VOL` is parameter-free and its control JSON is `{}`. This is an implementation/completion statement, **not** a scientific promotion decision.

---

## 2. Forecasting population, source data and point-in-time clock

### 2.1 Universe and source lineage

- **Fixed universe:** 20 equities: `AAPL, AMD, AMZN, AVGO, BA, BAC, COP, CSCO, CVX, JNJ, KO, MA, MRK, MS, PEP, SBUX, TSLA, VZ, WFC, XOM`. **Executed model tensor order is now documented in §2.1a** and differs from this alphabetical readability list.
- **Source:** P019B/P020 frozen historical US-equity minute-derived hourly OHLCV, hosted on Hugging Face at the exact pinned revision in §2.1a. The **original upstream vendor remains unverified**, and the original raw Parquet and adjusted stores are **not embedded** here.
- **Inputs:** `48 × 16` exact FT16 values per stock/origin. **All 16 formulas, lookbacks, M2 as-of gates, fitting/scaling rules and source maps are documented below and in Annex A**. Numerical per-phase scalers/floors remain stored in the executed `S4/Fxx_{inner,refit}_recipe.json` files, not in this prose.
- **Complete-panel convention:** The eligible forecast origin has the canonical valid 20-stock cross-section; input-quality gaps use the existing causal feature fallback/mask policy, not retrospective fill based on target outcomes. Missing **label endpoint prices** can invalidate the origin. Never manufacture missing endpoint prices, extend a session across a holiday, or silently change its stock cohort.
- **Source cautions:** Fixed survivor panel, historical action-adjustment vintage, fallback/missing-source rates, price-only proxy, exchange-calendar irregularities, true publication latency, and dataset rights remain qualifications.

### 2.1a Pinned dataset and source lineage (now documented)

- Public hosting: **[Hugging Face `mito0o852/OHLCV-1m`](https://huggingface.co/datasets/mito0o852/OHLCV-1m)** at revision **`776328445b7ac6e7815ef3a483e9c8ded1eb6d56`**, monthly `data/ohlcv_YYYY-MM.parquet`; original upstream vendor/feed quality remains **NOT VERIFIED**.
- The archived acquisition covered **July 2010–March 2026 (189 monthly files)**, but S9's **actual numerical source stops December 2024**. Historical feature warmup is July 2010–March 2011; expanding permitted fit data begin **2011-04-01**. **No 2025 tuning or protected 2026 numeric data** entered S9, according to its extracted source inventory.
- Exact stock-axis order: **`VZ, COP, BAC, BA, AAPL, PEP, MRK, SBUX, CVX, MS, AMD, KO, JNJ, AMZN, XOM, WFC, AVGO, TSLA, MA, CSCO`**. Do not silently alphabetize tensors or permute fitted stock constants.
- Raw minute timestamps are UTC minute starts; apply the `exchange_calendars` **XNYS** schedule, DST, holidays and early closes. Regular-session completed full-hour bins end 10:30–15:30 ET; the 15:30–16:00 **stub exists in source and target-endpoint construction, but is not an FT16 recurrent input bar**.
- Split-adjusted OHLC is in a backward **March 2026 split-consistent basis**, not dividend-total-return adjusted; source volume remains as-reported shares. COP spinoff at 2012-05-01 gets a hard compatible-price-basis boundary, not an invented multiplicative adjustment.
- Actual minute schema, HTTP revision URLs, source file/row-group validation, corporate-action event lists, source masks and reproducible code/receipt paths are in the complete §2/§3 of the appended replication supplement.

### 2.1b Original missing/bad-data treatment (do not replace with generic filling)

The extraction distinguishes **source validity**, **feature availability** and **target eligibility**:

1. Minute observations must have minute-aligned UTC timestamps, finite positive OHLC, finite nonnegative volume, and consistent high/low. Exact duplicate rows collapse; when **conflicting versions share a ticker/timestamp, all conflicting versions are excluded** (full activated source counts: 856 records/406 keys). Large authentic moves are not automatically discarded.
2. P019B retained genuine moves and quarantined **18 unresolved RTH minute records**, triggering **14 affected hourly-bin** reaggregations. High/low and volume for quarantined/invalid hourly bins are not trusted; no close proxy is allowed in an anomaly-containing hour. The resolved action/event ledger, rather than a generic outlier cap, controls this.
3. A causal **`close_input_cap5`** may reuse an earlier observed close for a permitted short missing terminal run of at most **five minutes**, with no future interpolation, overnight carry, empty-bin substitution or action-blocked proxy. The genuine terminal close is stored separately; a proxy **cannot** become a genuine target endpoint.
4. Feature-only volume may treat at most five missing minutes as zeros **only under additional genuine-observation/no-conflict/no-invalid conditions**; observed volume remains a lower bound. A six-hour daily volume requires six usable full-hour sums and a consistent split-share regime.
5. Missing **native** FT16 values use training-prefix median fallback for 13 unbounded channels (becoming normalized zero) or literal neutral zero for `B2/T2/T5`. No winsorization or sequence normalization. Feature fallback **cannot repair a failed all-48-close input eligibility test**.
6. A missing, quarantined, invalid, price-basis-incompatible or nonexistent **exact genuine return endpoint** in *any* stock excludes the **entire 20-stock forecast origin**. There is **no target price imputation, forward/backfill, proxy, nearest-minute replacement or exit-time shift**.

These policies are derived from executed source code/receipts, and differ from the old 99-stock/30-minute EBM dataset's filling rules; do not import those unrelated policies here.

### 2.1c FT16 complete 16-feature map and preprocessing (newly extracted)

All S9-MAG recurrent inputs are the 16 **own-stock**, dimensionless features below; there are **no** S5 clock, ticker-ID, USA500, cross-sectional factor or future-label channels. Values are native quantities **before** the frozen per-phase scaling:

| Position | ID | Native feature: exact mathematical definition (before robust scaling) | Source/lookback |
|---:|---|---|---|
| 1 | `M1` | $a_t/\max(s_{60,t},h_i)$, $a_t=\log(C_t/O_t)$ | Hourly open/cap5 close; 60 scheduled bars, ≥57 valid; current hour included |
| 2 | `M2` | $\mu^{(o)}_{20,i,t}/\max(s^{(o)}_{60,i,t},b_i)$ | Matured historical same-origin **four-trading-hour** returns; 20 prior regular-origin days (≥19), RMS60 (≥57), context-specific |
| 3 | `M3` | $\log(D_k/D_{k-5})/[\sqrt{5}\max(s_{63,k},\delta_i)]$ | Prior genuine 15:30-surrogate daily closes, RMS63 ≥60 |
| 4 | `M4` | $\log(D_{k-20}/D_{k-125})/[\sqrt{105}\max(s_{63,k},\delta_i)]$ | 105 daily-return intervals, skipping last 20 sessions; daily RMS63 |
| 5 | `V1` | $\log\max(s_{12,t},h_i)$ | RMS of hourly $\log(C/O)$, 12/12 |
| 6 | `V2` | $\log\max(s_{60,t},h_i)$ | Hourly RMS60, ≥57 valid |
| 7 | `V3` | $V1_t-V2_t$ | Log short/long floored RMS ratio |
| 8 | `B1` | $\log(H_t/L_t)$ | Safe observed hourly high/low; may be partial and quality-marked |
| 9 | `B2` | $(2C_t-H_t-L_t)/(H_t-L_t)$ | Close location, zero if zero range; invalid if outside ±(1+1e−10) |
| 10 | `Q1` | $\log[(U_t+q^h_{i,r})/(\bar U^{slot}_{20,t}+q^h_{i,r})]$ | Same scheduled-slot prior 20 occurrences, ≥19; current excluded, same share regime |
| 11 | `Q2` | $\log[(\operatorname{Mean}_{5,5}(W)_k+q^d_{i,r})/(\operatorname{Mean}_{60,57}(W)_k+q^d_{i,r})]$ | Previous regular-session six-hour volumes; same share regime |
| 12 | `T1` | $\log[C_t/\operatorname{Mean}_{20,19}(D)_k]$ | Current cap5 close versus mean of prior daily surrogate closes |
| 13 | `T2` | $\operatorname{Mean}_{20,19}(\operatorname{sign}(d))_k$ | Prior daily-return signs, including zero |
| 14 | `T3` | $(E_{6,t}-E_{18,t})/C_t$ | EMA6/EMA18 on cap5 closes; ≥360 post-seed updates and 69/72 recent coverage |
| 15 | `T4` | $(E_{24,t}-E_{72,t})/C_t$ | EMA24/EMA72; same initialization and gates |
| 16 | `T5` | $(\mathrm{RSI}_{14,t}-50)/50$ | Wilder RSI14, first 14 connected changes +≥140 updates and recent coverage |

`C_t` is the capped causal completed-hour closing-price input proxy, distinct from the genuine hourly terminal `G_t`. `D_k` is a genuine **15:30 surrogate**, not the 16:00 close. $s_{n,t}$ and $s_{63,k}$ are **root mean squares** of returns, not demeaned standard deviations. $h_i,\delta_i,b_i$ are positive fitted floors. Volume pseudocounts $q$ are per-stock and split-share-regime. Full formula edge cases, EMA/RSI state transitions and M2 maturity gates are preserved verbatim in the annex.

**Actual input normalization:** For 13 unbounded channels (`M1/M2/M3/M4/V1/V2/V3/B1/Q1/Q2/T1/T3/T4`), fit native median `c` and **unscaled** MAD on eligible unique input-history keys from the *earlier training prefix*; use MAD if positive, else IQR/1.349, else population SD, else 1. Output `(native_or_c−c)/scale`. For bounded `B2/T2/T5`, missing→0 and center=0/scale=1. Every 48×16 inference tensor is `float32`. All original input floors, volume pseudocounts and scaling values are **fold/phase-specific**, not globally fixed; preserve the eight executed `S4/Fxx_{inner,refit}_recipe.json` records. Historical M2 returns are allowed **only after endpoint+2-minute maturity**, checked as of each historical input session; seven contexts are pooled equally (1/7) when fitting M2-specific scales/floors.

**Cross-experiment distinction:** Original S1/S2 FT16 uses **two** M2 contexts (10:30, 11:30); S3-A retains old M2 at h1/h2, S3-B replaces *only* M2 with a horizon-aligned variant; S4/S9 uses **seven** genuine four-trading-hour contexts; S5 adds six time metadata channels for 22 total. Thus FT16 **feature IDs may match without numerically identical model inputs**. Complete rolling-window gates, split regime handling, code locations and source-to-run lineage appear in the verbatim annex.


### 2.2 Inputs are *completed scheduled hours*, not wall-clock 48-hour intervals

An input tensor has shape `(batch_of_stocks, 48, 16)` under the model’s own batching implementation. For a forecast origin at time `t`, only 48 **completed and information-available scheduled hourly observation slots** enter the LSTM. For the special 09:30 origin, the current 09:30–10:30 hourly bar is *not completed* and cannot be included; the most recent input hour is from the preceding session. Session gaps/weekends/holidays do not become fabricated hourly bars.

If a saved channel was created using a rolling transformation over additional prehistory, reconstruct the channel *causally* using its original lookback and training-phase fallbacks. Historical feature availability must precede the assumed forecast issuance cutoff.

### 2.3 Seven candidate forecast origins and exactly four trading hours to outcome

**Candidate origin clocks, America/New_York:** `09:30, 10:30, 11:30, 12:30, 13:30, 14:30, 15:30`. Only **actually source-eligible** events are saved. Some dates have fewer than seven.

| Candidate origin | Genuine four-trading-hour target endpoint | Category |
|---|---|---|
| 09:30 | 13:30 **same exchange session** | Intraday |
| 10:30 | 14:30 **same exchange session** | Intraday |
| 11:30 | 15:30 **same exchange session** | Intraday |
| 12:30 | 10:00 **next exchange session** | Overnight-crossing |
| 13:30 | 11:00 **next exchange session** | Overnight-crossing |
| 14:30 | 12:00 **next exchange session** | Overnight-crossing |
| 15:30 | 13:00 **next exchange session** | Overnight-crossing |

The latter four accumulate the remainder of the current trading session and then finish on the next regular session; the **15:30–16:00 closing half-hour** matters. Required 10:00/11:00/12:00/13:00 target prices come from genuine minute observations at the documented source convention; do not interpolate, fabricate or shift them when unavailable. Use the actual exchange calendar for holidays, daylight-saving transitions and early closes. Inspect source-endpoint policies and *actual saved eligible keys* for exceptions.

**Timing qualification:** The study assumes approximately a **two-minute issuance delay** after the labeled price origin (e.g. a 09:30 minute opening-price proxy and a modeled 09:32 issuance at the opening). The outcome begins at the **earlier labeled price**, not a verified executable fill available after issuance. For options backtesting, require real option quotes and underlying/option synchronization at genuinely tradable decision times; the magnitude target is *not* already a realized trading P&L.

### 2.4 Frozen annual expanding-prefix folds

| Fold | Outer research OOS year | OOS stock-origin rows | Eligible origins | Eligible exchange sessions |
|---|---|---:|---:|---:|
| F21 | 2021 | 19,100 | 955 | 188 |
| F22 | 2022 | 23,600 | 1,180 | 210 |
| F23 | 2023 | 17,740 | 887 | 187 |
| F24 | 2024 | 19,820 | 991 | 208 |
| **Total** | **2021–2024** | **80,260** | **4,013** | **793** |

**Executed nominal fold roles and real admitted OOS dates (source-extracted):**

| Fold | Inner-training stop | Nominal validation | Refit stop | First–last admitted OOS origin ET | OOS sessions / origins / rows |
|---|---|---|---|---|---|
| F21 | 2020-06-30 | 2020-07-01–2020-12-31 | 2020-12-31 | 2021-01-13–2021-12-31 | 188 / 955 / 19,100 |
| F22 | 2021-06-30 | 2021-07-01–2021-12-31 | 2021-12-31 | 2022-01-12–2022-12-30 | 210 / 1,180 / 23,600 |
| F23 | 2022-06-30 | 2022-07-01–2022-12-30 | 2022-12-30 | 2023-01-13–2023-12-29 | 187 / 887 / 17,740 |
| F24 | 2023-06-30 | 2023-07-01–2023-12-29 | 2023-12-29 | 2024-01-11–2024-12-31 | 208 / 991 / 19,820 |

For a **validation/OOS** origin, its **first** scheduled input hour must lie strictly beyond the preceding inner/refit cutoff (the **48-scheduled-step** embargo, not 48 calendar hours). Labels must mature before the role's conservative cutoff `(local midnight after cutoff)−4 hours`. Preserve complete actual source masks and the saved `S4/Fxx_{inner_train,inner_validation,refit,oos}_indices.csv`; the calendar date ranges are **not** substitutes for these indices. Training/refit starts 2011-04-01. Validation has at least 50 sessions and 25 origins per each of seven contexts. See §4 of the appended supplement for **every role's** sessions, origins, stock-row counts and admitted dates.

For each fold, model fitting and target transformations use only earlier history, with **label-maturity cutoff**, required embargo/purge and chronological inner calibration training/validation. The baseline protocol takes a roughly last-six-calendar-month validation tail, with **exact eligible boundary keys determined by frozen per-fold index/recipe files**, not by calendar guesses. Once the number of epochs is selected on inner validation, **freshly initialize the model and optimizer with the prescribed seed** and refit on the full earlier eligible prefix for that selected count. Evaluate the outer year exactly once with that checkpoint.

Later folds legitimately train on earlier OOS years; these four folds are **not independent experiments**. Historical 2025 exploration and all protected **2026** content/hashes must remain outside new fit or exploratory tuning. Release of a protected confirmation set requires a separately authorized, frozen confirmatory plan; this handoff does not release it.

---

## 3. Exact statistical target and what the network estimates

Let `P_{i,t}` be the frozen project price proxy at forecast origin `t` for stock `i`, and `P_{i,e(t)}` the genuine project price proxy at the four-trading-hour outcome endpoint `e(t)`.

**Raw signed log return**:

\[
R_{i,t}^{(4)} = \log\!\left(\frac{P_{i,e(t)}}{P_{i,t}}\right).
\]

**Raw endpoint magnitude**, the economic quantity of interest:

\[
A_{i,t} = |R_{i,t}^{(4)}| \ge 0.
\]

This is **not** absolute TG20, realized intrapath quadratic variation, high–low realized range, conditional integrated variance, or next-day volatility. It ignores the path between endpoints except insofar as path information informs the forecast.

**S9-MAG fitted regression target**:

\[
m_{i,t} = \log\big(1 + A_{i,t}/s_f\big),\qquad s_f>0.
\]

`f` denotes the fold and either its inner-training or refit role. **The exact scale statistic and the eight executed scales are now documented below.** The code and saved run target recipes, not an arbitrary replacement scale or retrospectively OOS-fitted number, govern reproduction.

**Executed exact target scale rule (now verified from saved run recipes):**

\[
 s_f=\max\{Q^w_{0.5}(|R|),10^{-8}\},\qquad
 m=\log(1+|R|/s_f),
\]

where $Q^w_{0.5}$ is the **earlier-role session/origin/stock-weighted median**, selecting the first sorted observation whose cumulative normalized weight reaches 0.5 (stable sort, no interpolation). Each fold uses a separately fitted inner-train scale and refit scale:

| Fold | Inner fitted $s_f$ | Refit fitted $s_f$ |
|---|---:|---:|
| F21 | 0.005797117684325846 | 0.0058994931438253 |
| F22 | 0.0059347355198145265 | 0.005957669984582455 |
| F23 | 0.0060897938914411046 | 0.006150424755601047 |
| F24 | 0.006174065175292481 | 0.0061703009229596 |

The model output is an **unconstrained** scalar and is optimized directly in transformed space, with **no ReLU, class weighting, target clipping, TG20 transform or extra tail weight**. At inference/reporting only, inverse once as $\widehat A=s_f\operatorname{expm1}(\max\{\widehat m,0\})$. The lower-clamp is now explicitly verified; it was not applied inside training.

The network outputs one scalar transformed forecast `\hat m_{i,t}`; the **actual training loss** is squared error in the *transformed magnitude*:

\[
\ell_{i,t}^{\mathrm{MAG}} = (\hat m_{i,t}-m_{i,t})^2.
\]

For reported raw-scale movement visualization, the transform is inverted **once**:

\[
\widehat A_{i,t}
= s_f\,\operatorname{expm1}\bigl(\max\{0,\hat m_{i,t}\}\bigr),
\]

with the **verified lower clamp only at decode/reporting time**. The unconstrained neural output and transformed-MSE training loss are unchanged by this postprocessing.

**Important statistical distinction:** Because of the nonlinear transform,

\[
 s_f\operatorname{expm1}\!\left(\mathbb{E}[m\mid X]\right)
\neq \mathbb{E}[A\mid X]
\]

in general (by Jensen’s inequality even with no clipping). Therefore `\hat A` is a nonnegative movement-size score with meaningful raw-scale diagnostics but is **not certified as a calibrated conditional expectation of `|R|`**. An options trading study must handle this issue explicitly.

### Objective hierarchy and evaluation weights

Within each role/year, the executed hierarchical loss gives **equal weight to eligible stocks within an origin**, **equal weight to valid origins within an exchange session**, and **equal weight to sessions**. Schematic unweighted-by-sector example for a role `D`:

\[
L_D = \frac{1}{|D|}\sum_{d\in D}
\frac{1}{|\mathcal{O}_d|}\sum_{t\in \mathcal O_d}
\frac{1}{20}\sum_{i\in\mathcal U_t}
(\hat m_{i,t}-m_{i,t})^2.
\]

Actual saved masks, denominators and role weights govern when eligibility differs. For combined results take the **arithmetic average of the four annual weighted losses**, not a pooled 80,260-row average. For paired controls use the **identical saved keys, labels and weights**.

---

## 4. Frozen S9-MAG neural architecture and training recipe

### 4.1 Architecture — core details to preserve

| Component | Executed S9-MAG reference |
|---|---|
| Model class | Standard PyTorch-style **single-layer, shared stockwise LSTM**; identical learned parameters used for all 20 stocks |
| Per-stock recurrent input | **48 × 16** completed FT16 features, chronological sequence |
| Hidden state size | **32** |
| Recurrent layers | **1** |
| Recurrent hidden/cell initialization | **Zero** at the beginning of each independent 48-step window; no cross-window persistent state |
| Cross-stock information | **No direct joint 20-stock mixer, market router, peer attention or ticker-ID embedding** in this model; stock histories share fit parameters |
| Output representation | Final LSTM hidden vector for each stock window |
| Dropout | **0.10 applied to the final hidden representation before the head**, training only; **no recurrent dropout** |
| Readout | **Linear 32 → 1** scalar regression head, predicting `log1p(A/s)` |
| Trainable parameters (reference) | **6,433**: LSTM `4×32×(16+32)+8×32 = 6,400`, plus scalar head `32+1=33` |
| Numeric platform | **CPU / float32** in frozen historical protocol; completed campaign peak RSS reported within the approved 2 GB cap |
| Clock channels | **None appended** (those belong to S5, not S9-MAG) |
| Target | `log1p(raw four-hour endpoint |log return| / training-fitted scale)` |
| Optimized loss | **Unweighted squared error of transformed magnitude**, aggregated under the existing role/session weighting; no ranking loss |

Standard LSTM equations (for one stock at each completed input step `k`), with `\odot` meaning componentwise multiplication:

\[
\begin{aligned}
i_k &= \sigma(W_{ii}x_k+W_{hi}h_{k-1}+b_i),\\
f_k &= \sigma(W_{if}x_k+W_{hf}h_{k-1}+b_f),\\
g_k &= \tanh(W_{ig}x_k+W_{hg}h_{k-1}+b_g),\\
o_k &= \sigma(W_{io}x_k+W_{ho}h_{k-1}+b_o),\\
c_k &= f_k\odot c_{k-1}+i_k\odot g_k,\\
h_k &= o_k\odot\tanh(c_k),\\
\hat m_{i,t} &= w^\top\operatorname{Dropout}_{0.1}(h_{48})+b.
\end{aligned}
\]

(The parameter count uses the usual PyTorch two-bias LSTM representation; the displayed gate equation combines corresponding biases.) The training target/loss are what distinguish S9-MAG from earlier signed-return/ranking versions of the same backbone.

### 4.2 Optimizer, weighting, checkpoint/refit

| Parameter | Frozen reference |
|---|---|
| Optimizer | **AdamW** |
| Learning rate | **0.001** |
| Adam betas | **(0.9, 0.999)** |
| Adam epsilon | **1e−8** |
| Weight decay | **0.01 on weight matrices; 0 on bias vectors** |
| Gradient control | Global gradient norm clipping at **1.0** |
| Minibatching | **16 complete exchange sessions per batch**, retaining their eligible origins and stocks; true executed update counts shown below |
| Random seed | **42**, independently reset at calibration and fresh refit |
| Validation | Chronological inner-validation **magnitude task loss**, dropout **OFF**; **not** signed Rank IC and **not** OOS loss |
| Stop/selection | **First finite nonnegative validation loss qualifies**; later qualification requires `L <= 0.999*best_qualified_loss`; **minimum calibration 12 epochs**, patience **10**, maximum **60**. Selected epoch can precede raw numerical minimum; do **not** apply S4 rank-IC selection. |
| Fresh refit | New same-seed initial network and empty optimizer; full earlier fitting prefix for exactly the selected number of epochs |
| Evaluation | Dropout OFF, checkpoint reloaded exactly; untouched **within that fold** annual OOS |

**Exact executed selection, stochastic order and model initialization (extracted from the saved implementation):**

- `nn.LSTM(input_size=16, hidden_size=32, num_layers=1, batch_first=True)` → last hidden state → dropout 0.10 → `nn.Linear(32,1)`. **6,433** trainable parameters. **PyTorch default initialization**; no custom Xavier, orthogonal initialization or forget-gate-bias adjustment. `torch==2.10.0`, CPU, FP32, four intra-op and one inter-op threads, deterministic algorithms enabled. Constructor order LSTM/dropout/head and seed 42 reset for each fresh phase.
- AdamW lr 0.001, betas 0.9/0.999, eps 1e−8; matrices weight decay 0.01, 1-D biases decay 0; global L2 clipping 1; no scheduler or AMP. Group 16 complete admitted sessions per optimizer batch, no gradient accumulation. Sort dates, then shuffle the session order afresh each epoch $n$ using `np.random.default_rng(42+n)`; within-session origins/stock order preserved. Final short session batch kept.
- During each calibration epoch, evaluate whole chronological inner validation with dropout off. The **first finite nonnegative** weighted validation loss qualifies; later epoch loss `L` replaces selected best **only if `L <= 0.999 * best_qualified_loss`**. Equality qualifies. Nonqualification increments patience. Stop at **epoch ≥12 and patience ≥10**, otherwise cap at 60. The raw minimum is logged separately, **not** the selected stopping criterion; F21 selected 27 although raw numerical minimum was at 30.
- After selection, create a **new** identically seeded model and **new** AdamW optimizer; refit all eligible earlier data for exactly selected epochs; checkpoint `refit_final.pt` contains model and optimizer. Never continue from validation checkpoint. Inference calls `eval()` with new zero recurrent states per independent 48-step window.
- FP32 model/validation versus FP64 exported diagnostic reductions can produce last-digit differences: preserve the actual loss and reduction units, not just exported scores. The complete actual per-fold validation bests and checkpoint binding hashes are in the appended supplement.

**Observed calibration and refit counts:**

| Run | Calibration epochs | Selected refit epochs | Raw best validation epoch | Calibration updates | Fresh refit updates |
|---|---:|---:|---:|---:|---:|
| `HF20-S9-F21-H4-MAG-S42` | 37 | **27** | 30 | 4,884 | 3,780 |
| `HF20-S9-F22-H4-MAG-S42` | 30 | **20** | 20 | 4,380 | 3,040 |
| `HF20-S9-F23-H4-MAG-S42` | 51 | **41** | 41 | 8,160 | 6,765 |
| `HF20-S9-F24-H4-MAG-S42` | 37 | **27** | 27 | 6,364 | 4,806 |

The F21 raw-best epoch (30) differs from selected epoch (27) because the frozen improvement qualification was not met, **not** because the model secretly chose a later OOS winner. Optimizer-step counts reflect actual eligible training minibatches and phases; do not use them to back-solve or redefine row eligibility.

### 4.3 Model-training pseudocode (conceptual, not a replacement for code)

```python
for fold in [2021, 2022, 2023, 2024]:
    # Recover exact, frozen, per-fold indices/calendar/source data; use no OOS data in any fit.
    inner_train, inner_val, refit_train, oos = load_frozen_fold_roles(fold)

    # All transformations, fallback values and target scale are phase-specific
    # and fit ONLY on the permitted training prefix for each fitting phase.
    inner_recipe = fit_or_load_original_inner_recipe(inner_train)
    val_model = fresh_shared_lstm(input_dim=16, hidden_dim=32,
                                  layers=1, head_dim=1, seed=42)
    # minibatch = complete sessions; loss uses exact session/origin/stock weights
    selected_epoch = train_and_select_on_inner_validation(
        val_model, inner_train, inner_val,
        optimizer="AdamW", lr=0.001, weight_decay_matrices=0.01,
        clip_global_norm=1.0,
        target="log1p(abs_four_trading_hour_log_return / inner_scale)",
        criterion="frozen_validation_MAG_MSE_qualification_rule",
    )

    refit_recipe = fit_or_load_original_refit_recipe(refit_train)
    final_model = fresh_shared_lstm(input_dim=16, hidden_dim=32,
                                    layers=1, head_dim=1, seed=42)
    train_exactly_n_epochs(final_model, refit_train, refit_recipe,
                           n_epochs=selected_epoch)
    save_checkpoint_and_binding(final_model, refit_recipe, fold)
    evaluate_once_on_saved_eligible_oos_keys(final_model, oos,
                                              refit_recipe, dropout=False)
```

Do not execute this pseudocode as written; the functions are descriptive names. To reproduce exact historical values, **reuse the repository’s executed source/weights/checkpoints/target recipes and recover all frozen metadata**.

---

## 5. Baselines: what does “STOCK” mean?

A **same-task stock-level baseline** supplies one fitted typical transformed magnitude for each stock, estimated from **earlier permitted training data**, independently of recent history at the forecast origin:

\[
\hat m_{i,t}^{\rm STOCK}=c_{i,f}
\qquad\text{for all admissible forecast times in fold }f.
\]

For weighted squared error, the optimized stock constant is the **training-phase weighted mean** of transformed magnitude for that stock:

\[
c_{i,f}=\frac{\sum_{t\in\mathrm{train}(f)}w_{i,t}\,m_{i,t}}
{\sum_{t\in\mathrm{train}(f)}w_{i,t}}.
\]

The fitted weights are now verified: each admitted stock row has role mass `1/(D*n_d*20)`, where `D` is number of admitted sessions and `n_d` origins on that session. The exact numerical STOCK means appear in the copied source-extraction table in Annex B and in the executed control JSONs. A constant may change **between** annual folds after authorized refitting, but **not intra-fold** in response to that day’s price history. It captures that, for instance, TSLA may have a different unconditional typical four-hour move from KO. The stock baseline is stronger than one global constant, but not a dynamic conditional-volatility benchmark.

The other completed controls are:

- **`GLOBAL`:** one pooled, training-prefix fitted transformed-magnitude constant for the full stock population; no stock identity or recent-history variation.
- **`VOL`:** the **parameter-free** FT16 `V2` (floored RMS60 hourly open-to-close return) decoder and fixed normal-absolute-move multiplier, **fully specified below**. No EWMA, regression fit or extra volatility lookback is present.

All three controls **produce predictions on the same transformed magnitude target** as MAG and are evaluated on exactly matched origin/stock keys. `GLOBAL` and `STOCK` optimize fitted transformed-MSE constants; `VOL` is **not fitted to that target**. The fact that MAG beats `STOCK` means it carries predictive information beyond stationary cross-stock typical movement levels **in this exploratory sample**. Beating `VOL` is stronger evidence against a purely generic trailing-volatility explanation, but not proof of option-market inefficiency.

**Newly recovered executed `VOL` control — this corrects the earlier placeholder.** The control is **parameter-free**, not a fitted EWMA or fitted volatility regression. At the latest input step, take the saved, **already scaled/imputed** FT16 `V2` channel and undo its frozen phase-specific affine transformation:

\[
 \sigma_{i,t}=\exp(V2^{\mathrm{scaled}}_{i,t} \, s_{V2}+c_{V2}),\qquad
 \widehat m^{\mathrm{VOL}}_{i,t}
 =\log\left(1+\frac{2\sqrt{2/\pi}\,\sigma_{i,t}}{s_f}\right).
\]

Thus the decoded raw VOL magnitude is $2\sqrt{2/\pi}\sigma$. Here $\sigma$ is the **floored hourly open-to-close RMS60 or its native feature fallback** represented by the tensor, **not** close-to-close volatility, an EWMA estimate, an option IV or a fitted conditional-volatility model. The saved `inner_VOL_control.json` and `refit_VOL_control.json` are `{}`. The `GLOBAL` and `STOCK` controls **are** prefix-weighted means in transformed space, using exactly the same session/origin/stock weighting as the neural model; stock means are separate by ticker, fixed through the role. Their exact 4×20 inner/refit coefficient matrix is reproduced in the source-preserving supplement annex.

All three produce **same-task transformed-magnitude** predictions scored on matched keys; do not say all three were statistically fitted or that VOL was MSE-optimized. This matters when interpreting the 13.3% reduction relative to VOL.

**Important:** A baseline optimized for transformed MSE is **not necessarily** the optimal baseline for *raw* absolute-return MAE/MSE or for option P&L. Do not overinterpret raw-MAE comparisons as if the baseline was raw-MAE-optimal. Later work should add information-matched, dynamically calibrated and options-implied baselines.

---

## 6. Completed results, quantitative reproducibility targets

### 6.1 Primary proper-loss comparisons (negative paired delta is MAG improvement)

`Δ = MAG loss − baseline loss`. All numbers below use the executed transformed-MSE definition and equal-year averaging.

| OOS year | MAG transformed MSE | Δ vs `STOCK` transformed MSE | Δ vs `VOL` transformed MSE |
|---|---:|---:|---:|
| 2021 | 0.222777 | −0.038667 | −0.037156 |
| 2022 | 0.279200 | −0.069598 | −0.039514 |
| 2023 | 0.208858 | −0.018095 | −0.036084 |
| 2024 | 0.218982 | −0.021357 | −0.030494 |
| **Equal-year four-fold result** | **0.232454** | **−0.036929** | **−0.035812** |

The corresponding equal-year control MSEs are approximately **0.269383 (`STOCK`)** and **0.268266 (`VOL`)**, so the relative improvements are **13.7%** and **13.3%** respectively.

Descriptive **95% whole-month bootstrap intervals** for the paired equal-year proper-loss differences:

- MAG minus `STOCK`: **[−0.042946, −0.031723]**, better in all four years.
- MAG minus `VOL`: **[−0.040886, −0.031409]**, better in all four years.

They exclude zero *within the chosen exploratory exercise*; they **are not** confirmatory p-values or evidence immune to repeated model searches, overlapping four-hour returns, temporal dependence, selection bias, or the four-year scope.

### 6.2 Raw absolute-movement accuracy and calibration

| Metric | MAG | `STOCK` | `VOL` | Interpretation |
|---|---:|---:|---:|---|
| Raw `|R|` MAE | **0.006505** | 0.006903 | 0.006992 | MAG ~5.8% better than stock constant, ~7.0% better than volatility proxy on this reported metric |
| Mean raw-scale predicted magnitude | **0.00836** | — | — | Forecast is systematically low relative to realized mean |
| Mean realized raw magnitude | **0.01031** | — | — | Approximately 1.95 percentage points per hundred in magnitude units above prediction (`0.00195` log-return units) |
| Reported magnitude rank association | **0.408** | — | — | Larger predicted movements tend to correspond to larger realized magnitudes, but need exact definition/weighting from metrics file |

The observed/predicted mean gap is **0.00195 log-return units** (about **0.195 percentage points** of absolute return for small moves), **not** “1.95 percentage points.” The displayed inverse is not certified as `E[|R| | X]`. Raw MAE/MSE are informative diagnostics; transformed MSE was what was optimized.

### 6.3 Breadth across periods, stocks and strata

Using the uploaded matched `S5_S9_OOS_PAIRED_SOURCE_STOCK_STRATA.csv` and counting negative *proper-loss* deltas relative to the executed controls:

| Matched descriptive grouping | MAG better than `STOCK` | MAG better than `VOL` |
|---|---:|---:|
| Stock × year, 20 × 4 | **78/80** | **80/80** |
| Months, 12 × 4 | **48/48** | **48/48** |
| Clock slots × year, 7 × 4 | **28/28** | **28/28** |
| Intraday/overnight categories × year | **8/8** | **8/8** |
| Source-quality strata × year | **8/8** | **8/8** |
| Source fallback strata × year | **8/8** | **8/8** |
| Nonempty reported age-band strata × year | **15/16** | **16/16** |

The average over years is favorable for **all 20/20 stocks** against `STOCK`. These overlapping groups and repeated observations **are not separate independent replications**. For two stock-year `STOCK` exceptions, consult the attached source/stock table; do not hide them behind the annual average. Stratum quality and fallback descriptions reflect **post hoc diagnostics**, not causally identified inputs or modifications of the evaluation sample.

### 6.4 Tail-loss concentration and the reason to be cautious about extremes

The completed MAG true optimized-loss analysis reports approximately:

- OOS training-95th-tail **observation mass**: **5.87%**.
- Share of actual transformed MAG loss from this tail: **24.08%**.
- Actual MAG loss share from the largest **1% of errors**: **9.49%**.
- Under source NUM/MAD attribution partitions, MAG loss shares: **NUM_ONLY ~22.71%**, **MAD_ONLY ~1.46%**, `BOTH` recorded separately. These cohorts are retrospective attribution partitions; do **not** mistake them for causality or exclusive total-loss partitions across overlapping cohorts.
- The observed 2021 MAG chart has occasional realized moves near 5–6% while the network’s predictions are much more compressed. That chart displays a single stock/fold, not a complete estimate of aggregate tail calibration.

Error/loss spikes are especially relevant for downstream options: a magnitude forecaster can improve average squared error while still **missing precisely the large jumps a long straddle needs**.

### 6.5 Descriptive chart findings supplied by the user

The Firefox `S5_S9_VISUAL_DIAGNOSTICS.html` screenshots selected `HF20-S9-F21-H4-MAG-S42`, `role=oos`, and later showed the full 2021 AAPL observation range.

- **Time-series panel:** true absolute endpoint returns are sharply variable, while MAG forecasts and stock/vol controls have a narrower band; forecast is not an exact jump detector.
- **Full-role calibration curve:** observed movement is above identity for the forecast buckets shown, consistent with **underprediction**. Full-role charts use all stocks/eligible OOS rows for that run, not just AAPL.
- **All-period AAPL scatter and residuals:** sizable noise, some positive association between forecast magnitude and realized magnitude, large positive misses and negative errors.
- **Rolling transformed-loss panel:** distinct error spikes at different dates; descriptive evidence for follow-up regime/conditional-calibration investigation, not proof of a market-regime mechanism.

These screenshots *validate the kind of diagnostic view available*, not correctness of a backtest or an option trade. The report states that selected-ticker trajectories may display subsets/windows and must not be confused with full-role weighted statistics.

---

## 7. Scientific interpretation and known limitations

1. **Prospective-outcome vs pre-observation:** MAG OOS is annual held-out for each fold, but the entire 2021–2024 historical sample has been revisited repeatedly across HF20 hypothesis/model choices. Descriptive confidence intervals do not undo meta-selection. A genuinely independent future evaluation must be specified **before** checking it.
2. **Overlapping outcomes and shared panel:** Seven candidate origins/day have overlapping four-trading-hour labels; all 20 stocks share market regimes and many event times. Do not treat 80,260 rows, 4,013 origins, 793 sessions, or 48 months as independent iid economic experiments.
3. **Target is endpoint `|R|`, not path variance:** Two price paths can have the same endpoint magnitude but very different intrapath variation and delta-hedging P&L. A realized-variance swap or continuously delta-hedged gamma strategy requires a different target and matching data.
4. **Model is not direction-aware:** MAG cannot, by itself, choose long versus short equity. Nor is its output a signed return forecast, a calibrated event probability, or a risk-neutral valuation.
5. **Calibration:** `log1p` inversion and lower clamp do not deliver a conditional raw `E|R|`; model systematically underpredicts large moves. A downstream threshold on uncalibrated raw predicted values is unsafe as an economic decision rule.
6. **Price-only timing:** Original label entry/exit proxy predates the modeled issuance by two minutes and lacks independently certified publication/fills. No identical-minute option quote feed has been supplied.
7. **Universe/vintage:** Fixed 20 historically surviving symbols, frozen corporate-action assumptions, coverage restrictions, and source-quality fallback may affect generalizability and access to economically true returns.
8. **Comparison class:** `STOCK`, `GLOBAL`, `VOL` are legitimate but limited baselines. A stronger time-of-day/overnight/stock-conditional volatility baseline, HAR-style realized-volatility control, or options-market benchmark may narrow the benefit.
9. **One seed/architecture:** Four calendar folds use seed 42, not four seeds; higher parameter counts or different architectures were not compared within S9-MAG. No claim of optimal architecture, training budget or production stability.
10. **Risk under options:** High conditional movement may already be **priced into implied volatility**, so forecasting magnitude is necessary but not sufficient to make long volatility profitable.

The finding that MAG is better than the `STOCK` and historical `VOL` controls supports a **qualified historical predictive effect**, not an assertion that an option strategy will profit.

---

## 8. Exact reproduction and read-only inspection guide

### 8.1 Required source materials in the local repository

**S9 campaign root** (relative to repository root):

```text
reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation/
```

**Primary reports and tabular evidence:**

```text
S5_S9_FINAL_RESEARCH_DECISION.md
S9_TARGET_AND_BASELINE_CONTRACT.md
S5_S9_GENERATED_RESEARCH_TABLES.md
S5_S9_MODEL_METRICS.csv
S5_S9_MATCHED_BASELINE_DIFFERENCES.csv
S5_S9_PAIRED_OOS_UNCERTAINTY.csv
S5_S9_OOS_PAIRED_SESSION_DIFFERENCES.csv
S5_S9_OOS_PAIRED_SOURCE_STOCK_STRATA.csv
S5_S9_EXTREME_LOSS_SUMMARY.csv
S5_S9_TRAINING_TRACE.csv
S5_S9_DETAILED_TRAINING_AND_EXTREME_DIAGNOSTICS.md
S5_S9_DIAGNOSTIC_INDEX.md
S5_S9_VISUAL_DIAGNOSTICS.html
RUN_INVENTORY.csv
S5_S9_VERIFICATION.json
S4_REUSED_RECIPES.json
```

**One run per annual fold**, exact IDs:

```text
HF20-S9-F21-H4-MAG-S42/
HF20-S9-F22-H4-MAG-S42/
HF20-S9-F23-H4-MAG-S42/
HF20-S9-F24-H4-MAG-S42/
```

Within **each run** inspect, at minimum:

```text
configuration.json
inner_target_recipe.json
refit_target_recipe.json
calibration_binding.json
refit_binding.json
refit_final.pt
inner_train_scores.parquet
inner_validation_scores.parquet
refit_scores.parquet
oos_scores.parquet
inner_GLOBAL_control.json
inner_STOCK_control.json
inner_VOL_control.json
refit_GLOBAL_control.json
refit_STOCK_control.json
refit_VOL_control.json
oos_GLOBAL_control_scores.parquet
oos_STOCK_control_scores.parquet
oos_VOL_control_scores.parquet
oos_metrics.json
model_and_control_metrics.csv
matched_baseline_differences.csv
RUN_DIAGNOSTICS.md
PASS.json
```

Where actual names or locations differ, follow `S5_S9_DIAGNOSTIC_INDEX.md` and inventory; never silently replace absent files with new values. Role-specific checkpoint and epoch files are also linked there. The source project’s frozen P019B/P020 **minute/hour/FT16 recipe, stock order, source qualification and fallback code** are necessary for a from-raw-data replay.

### 8.2 Minimum read-only reproduction first — **no retraining required**

1. Locate the four actual MAG run folders and verify their `configuration.json`, `refit_target_recipe.json`, checkpoint bindings, source/feature hashes, and saved OOS records. Confirm hidden size 32, FT16 dimension 16, seed 42, objective and phases.
2. Read/merge the **saved** fold-specific `oos_scores.parquet` with matching saved same-task control score Parquets on **exact** `(fold, origin timestamp, ticker, horizon, role, target endpoint)` keys. Preserve saved masks and weights; never join only on ticker/calendar date or accidentally mix targets.
3. Verify once-only target inversion, raw `|R|`, transformed `m`, clipped displayed prediction and true `|R|`, their source prices/endpoint timestamps, and **all 20 eligible rows/origin**.
4. Independently recalculate transformed MSE and raw MAE per role/fold, plus matched paired losses versus `STOCK` and `VOL`, using saved hierarchical weights. Verify the equal-year totals in §6.1 and raw-MAE figures in §6.2. Do not recompute a differently weighted pooled score and call it a failure.
5. Load training trace and selected epochs from saved receipts; compare with §4.2. Recreate main **read-only** plots if desired. No optimizer updates, re-fitting controls, scanning protected data, or new threshold search are required for this replay.
6. Reconcile per-year/stock/month/category/clock source strata with the attached `S5_S9_OOS_PAIRED_SOURCE_STOCK_STRATA.csv`. Preserve empty/undefined groups and sample counts. If any discrepancy appears, report the exact role/key/weight mismatch rather than tweaking outputs.
7. Read reports’ source/admissibility caveats before extending any evaluation to option quotes.

### 8.3 To rerun training **later**, only under explicit authorization

The absolute minimum scientific invariants are: correct 48×16 causal FT16 features, correct true four-trading-hour endpoints, correct fold-specific train/val/refit/OOS and embargo, correctly fitted target scale, correct optimizer/hyperparameters/validation-loss selector, fresh refit, proper weighted loss, same-task controls, and no protected-data reads. Reuse the source repository’s working code and existing sanity tests, not a new experiment/audit framework.

For a **byte-exact numerical rerun**, retain the following original **numerical files and executed code/bytes** (the underlying methodological formulas and procedures are now documented in §2–§5 and Annexes A–B):

| Data/code/bytes still required for **exact numerical replay** | Original authoritative location |
|---|---|
| Exact minute OHLCV, provenance and split/action data | Pinned Hugging Face revision and original `A18/P019B` manifests and quarantined-source stores |
| Fitted **numeric** FT16 phase floors/scalers (not just their formulas) | Eight executed `S4/Fxx_{inner,refit}_recipe.json` files and source-key stores |
| Exact member indices and matched source/origin endpoint arrays | Saved `S4/Fxx_{inner_train,inner_validation,refit,oos}_indices.csv` and `opening_reaudit_v2` source/endpoint Parquets |
| Actual code, installed dependency/kernel versions and selected MAG checkpoints | Source at recorded execution identity, per-MAG `configuration.json`, `calibration_binding.json`, `refit_binding.json`, and `refit_final.pt` |
| Full original controls/score exports when verifying historical rather than analogous results | Per-fold `inner/refit_*_control.json`, `oos_scores.parquet` and matching control score exports |

**Reconstruction honesty:** All **methodological** FT16 formulas, phase-statistic definitions, numeric magnitude scales, VOL definition, optimizer/stopping rules, split masks and QA policies are now described in this handoff. An identical historical 0.232454 score still requires the original pinned source and numerical artifacts listed above. Without those bytes, an independent rerun is a faithful *methodological reproduction*, not certification of a byte-for-byte identical model.

### 8.4 Where the dashboards stand

- S9’s actual browser-openable research panel: `S5_S9_VISUAL_DIAGNOSTICS.html` (`?view=HF20-S9-F21-H4-MAG-S42` and analogous F22–F24); it is a completed *separate* S5/S9 diagnostic artifact.
- S1/S2 and S4 ranking diagnostics are existing working HTML views. **The user has already inspected the relevant dashboards and explicitly decided no further visualization implementation is needed.** Preserve them as-is; this future S9/options handoff does not authorize changes.
- Existing S9 charts show movement forecasts and proper-loss diagnostics, not options P&L.

---

## 9. The separate *future* signal-generation study (not performed yet)

### 9.1 Correct economics: a high absolute-return forecast does not imply a long-straddle edge

At time `t`, MAG forecasts a physical-measure realized **endpoint magnitude** over its designated future four *trading* hours. A long straddle consists of an option **call and put with the same strike and expiration**; its future mark-to-market value also depends on option **expiry beyond the horizon**, time decay, bid–ask spread, implied-volatility evolution, skew/smile, rates/dividends, discrete execution and option-specific liquidity.

A correct future research question is **not** merely “Is MAG’s `|R|` forecast high?” It is:

> On timestamp-matched data, after causal calibration and costs, does forecasted physical movement/distribution **exceed movement already reflected in an appropriate option-implied comparator** enough to predict positive **tradable long-straddle** mark-to-market return at the actual intended exit?

That question differs from trading Asian options. An Asian option depends on an average underlying price over a sampling period, so it is **not** the most direct instrument for our current endpoint-magnitude target. Plain long straddles (possibly very short dated) are the initial **hypothesis to test**; delta-hedged options or variance derivatives require additional path-level forecasting.

### 9.2 A scientifically valid signal pipeline

Keep each stage modular so failure can be attributed; separate **LSTM fitting**, **prediction calibration**, **decision rule**, and **trade execution/backtest**:

1. **Freeze a magnitude forecaster:** reuse the S9-MAG checkpoint/saved OOS predictions as the historical reference. New fits/architectures are separate comparisons; no post hoc retraining on the reported fold’s OOS outcomes.
2. **Calibrate physical absolute-move estimates:** use a *permitted earlier training/validation* segment and, when necessary, earlier out-of-fold *prequential* forecasts to map `\hat m` or its raw inverse into `\widehat{\mathbb E}_P[|R|\mid\mathcal F_t]`, forecast decile distributions, or conditional tail probabilities. Candidate calibrators include a monotone isotonic map or constrained one-dimensional spline/GLM. Avoid post-search fit on 2021–24 OOS outcomes followed by reporting the same data as independent validation.
3. **Estimate the market-implied benchmark:** use **synchronized, executable** call/put bid/ask, strike, expiration, Greeks/IV surface, underlying and distributions. Quote retrieval, filters and publication time must be before decision issuance. A crude same-horizon Black–Scholes normal approximation is `E|R| ≈ sqrt(2/pi) σ sqrt(Δt)` when assumptions apply, but it is **not** automatically the option market’s exact four-hour expected endpoint move. Handle session/overnight/calendar time and term structure correctly; options typically expire later than four hours and an IV-smile-based risk-neutral distribution is not the same as the physical one.
4. **Define an economically interpretable gap:** examples include `g_{i,t}=\widehat{E}_P|R_{4h}|-\widehat{E}_Q|R_{4h}|` or an appropriately scaled ratio `\widehat{E}_P|R_{4h}| / \widehat{E}_Q|R_{4h}| - 1`. The risk-neutral quantity and the physical quantity should be matched by horizon and payoff; **a positive gap is not yet proof of positive straddle P&L**.
5. **Causal smoothing:** optional `\tilde g_t = \alpha g_t + (1-\alpha)\tilde g_{t^-}` or rolling median on **past currently available** forecasts only; update at actual eligible origins, not fictional hourly samples. Explicitly handle each stock, overnight gaps and missing origin observations. Smoothing may reduce turnover **and** delay detection of rare jumps; quantify both.
6. **Thresholds and hysteresis:** enter only if `\tilde g_t` clears a fixed entry threshold and a margin above estimated round-trip costs; exit/stand aside under a lower exit threshold. Choose threshold/`\alpha` on a *separate chronological strategy-validation set*, or predeclare them before untouched test. Do not tune them to already observed S9-MAG OOS returns and then call that result unbiased.
7. **Execution-aware contract selection:** predeclare strike (e.g. nearest liquid ATM), expiration, quote timestamp, spread/depth thresholds, maximum position duration, whether position closes at the next four-*trading*-hour endpoint, and behavior around early close, expiry, earnings, overnight and ex-dividend. Avoid hidden survivorship/contract-selection look-ahead.
8. **Trade P&L and capital risk:** use buying both options **at ask**, exit selling both **at bid**, fees/slippage, permitted size/margin and possible exercise/assignment. Include IV changes and theta; do **not** compute “profit = realized `|R|` − current straddle premium” for a four-hour mark-to-market exit if options remain unexpired.
9. **Benchmarks and ablations:** no-trade/cash, random matched-frequency trades, IV-only threshold, underlying trailing-variance/EWMA/HAR-inspired magnitude baseline + same signal calibration, STOCK-only and GLOBAL-only, unsmoothed vs smoothed, and naive unconditional straddle buy. Ensure same trading clocks/contracts/costs, exposure and support.
10. **Statistical/economic reporting:** paired net P&L on matched event windows, drawdown, positive-trade probability, mean/median P&L per debit, risk-adjusted returns with correct capital convention, turnover, delta/vega/gamma exposure, borrow/fees, spread/IV sensitivity, and regime/month/year stability. Resampling must preserve common days/cross-stock dependence and overlapping holdings. Keep train/selection/OOS/confirmation clearly separated.

No inference of profitability is permitted from the current S9-MAG MSE or MAE alone.

### 9.3 Core option-trading mathematics

Let `C_t(K,T)` and `P_t(K,T)` denote the market option prices for a call/put with strike `K` and common expiration `T`. The **quoted mid-price** of a theoretical straddle is:

\[
V_t^{\rm mid}(K,T)=C_t^{\rm mid}(K,T)+P_t^{\rm mid}(K,T).
\]

At expiration the combined payoff is exactly

\[
(S_T-K)^+ +(K-S_T)^+=|S_T-K|,
\]

and the **expiration** long-straddle payoff net of initial premiums is `|S_T-K|-(C_t^{ask}+P_t^{ask})` before fees. However, our model forecast horizon is **four trading hours**, and the chosen options often **will not expire at its end**. For a four-hour exit at `u=e(t)` (if actually executable), a simple one-contract-per-leg round-trip P&L is:

\[
\Pi_{t,u}=C_u^{\rm bid}(K,T)+P_u^{\rm bid}(K,T)
- C_t^{\rm ask}(K,T)-P_t^{\rm ask}(K,T)
-\text{fees/slippage},
\]

with contract multiplier/corporate actions handled consistently. This depends on the entire future option pricing state `(S_u,T-u, IV_u, smile_u, ...)`, **not only** the stock’s `|R_{t,u}|`.

As a *rough* benchmark under an approximately zero-drift normal log return with total variance `\sigma^2\Delta t`:

\[
\mathbb E[|R|]\approx \sqrt{\frac{2}{\pi}}\,\sigma\sqrt{\Delta t}.
\]

Do **not** interpret annualized option IV as exactly the same-horizon `\sigma` or annualize a four-trading-hour return by dividing through **calendar hours** without an intraday/overnight model. Non-Gaussian tails, volatility risk premium, jumps and options repricing invalidate naive equality. The option-implied expectation would be under a pricing measure `Q`, whereas MAG estimates historical physical `P` behavior.

For a delta-hedged option position, a high-frequency approximate gamma/theta exposure has a term resembling

\[
\Delta \Pi \approx \frac12\Gamma S^2\Bigl[(\Delta S/S)^2 - \sigma_{\rm implied}^2\Delta t\Bigr]
\]

**only under simplifying assumptions** (constant/reliable gamma and IV, sufficiently short interval, adequate hedge frequency, frictionless markets and omitted vega/jump terms). This highlights why **path variance** is a different research target from absolute endpoint return. It is **not** a trading P&L formula to use unadjusted.

### 9.4 Smallest viable follow-up design — avoid another engineering spiral

**Stage A — read-only feasibility:** Check availability/cost of historical option quote series matching **2021–2024** named equities at decision and four-hour exit times. Verify actual bid/ask *both legs*, contract IDs, expiry, tradeability and action/stock-price timestamps. **No option data means no execution-realistic option backtest.** A scenario/Black–Scholes illustration is allowed only when explicitly labeled *synthetic pricing*, not a realized backtest.

**Stage B — limited predictive-to-implied comparison:** With sufficient genuine quotes, compare **frozen** MAG and VOL predictions to matched implied move on a predeclared sample, with no strategy threshold optimization. Diagnose calibration, coverage and where model-vs-IV gaps occur.

**Stage C — separately approved bounded strategy test:** Freeze a *small* number of scientifically motivated threshold/smoothing/hysteresis settings using separate chronological strategy-selection history; then run one cost-aware walk-forward OOS test and a matched exposure null. Do not train multiple neural architectures as part of a *signal execution* experiment.

**Stage D — genuinely held-back confirmatory evaluation:** Only after the entire feature/model/calibration/options-contract/threshold/exit/risk protocol is frozen, request authorization to use a still-untouched holdout. The protected 2026 series is **not unlocked by this document**. Historical option data must actually be available for that holdout.

---

## 10. Potential follow-up LSTM improvements (prioritize hypotheses, not architecture churn)

Do not run these merely because the research-start ledger has room. Each should address a specific failure diagnosed here, use matched input data and controls, and require a **newly permitted selection/confirmation protocol**.

| Priority | Candidate change | Scientific mechanism to test | Minimal necessary comparison / caution |
|---|---|---|---|
| **1** | **Original-scale calibration** of MAG inverse | Underprediction and nonlinear inverse bias | Read-only reliability first; separately trained causal calibrator versus `STOCK`, `VOL`, raw-MAE-optimal control; avoid test-set calibration |
| **2** | **Time-of-day / overnight / holiday state** in magnitude model | Morning vs overnight target mechanics differ; S9-MAG had no S5 clock channels | One matched MAG+causal-clock arm versus frozen MAG, with same folds and validation; no claim that S5 ranking metadata already helps MAG |
| **3** | **Direct expected absolute magnitude, robust/quantile/asymmetric loss** | Transform-MSE optimum may not align with raw move or positive-tail utility | Compare proper raw-scale or distributional objective and calibration; disclose which conditional functional is learned |
| **4** | **Conditional volatility/path features** | FT16 may omit useful realized variation/gap/range/activity information | Small information-matched FT16+causal-history comparison; do not feed future bars or option marks post issuance |
| **5** | **Economically relevant option implied features** | Implied volatility and option skew may contain stronger contemporaneous risk information than prices alone | Only with historical point-in-time option chains and affordable quotes; matched IV-only control necessary |
| **6** | **Heavy-tail distribution / hurdle / mixture head** | Absolute magnitude is heteroskedastic and has rare extreme episodes | Proper probabilistic score, tail calibration and better stock-specific/volatility baselines; E1/QUANTILE already failed against stock controls |
| **7** | **Multi-horizon/path forecasting** | Four-hour endpoints may be mismatched with listed option expiries and gamma/hedge economics | Predeclare horizons and data timestamps; train new label only under separate approval |
| **8** | **Peer-aware / regime-aware recurrent architecture** | Joint market shocks and regimes may alter absolute-move risk | Start with a light market-state proxy and matching simple baseline; do not assume more parameters are beneficial |
| **9** | **Larger point-in-time stock universe and rolling refits** | 20 fixed large survivors may limit generalization; more series improve sample breadth | Handle universe membership/availability and survivor bias; preserve prior HF20 comparators |

A strong methodological alternative to an LSTM tweak is a **well-specified non-neural volatility model** (EWMA, GARCH, HAR-style or a simple nonlinear conditional magnitude regressor) using the **same causal input information**. If it matches/exceeds MAG, that is useful information about which model complexity is warranted.

**Critical distinction:** S9 EVENT and QUANTILE’s failure against stronger per-stock controls means “add event/quantile heads” is **not** an already validated improvement. A well-calibrated distributional model might still be useful, but must beat the right task-specific controls.

---

## 11. Suggested research questions for the new conversation

The reader should be able to pursue the following in order, without confusing predictive skill with economic utility:

1. **Statistical estimand:** What does inverse `log1p` magnitude-MSE actually estimate? Can we derive a validated estimate or distribution for `E_P(|R| | X)`, and how does its calibration change across months, stocks, overnight segments and extreme events?
2. **Source reliability:** Are MAG gains preserved across real source-quality/fallback groups, missing observations and actual decision-to-entry delays? The uploaded strata are promising but not an independent source audit.
3. **Comparison strength:** How much remains after a *time-of-day- and stock-aware* conditional historical-magnitude baseline (plus same-horizon EWMA/HAR/GARCH where feasible), rather than only static `STOCK` and existing `VOL`?
4. **Regime stability:** Do rank association, tail recall and calibrated expected absolute-move error persist during volatility transitions, earnings, market gaps and major news releases? Conditions must be defined with **past-available** data.
5. **Implied move bridge:** Can a given 4h physical magnitude forecast be compared fairly with a **4h risk-neutral expected move** extracted from a longer-expiry volatility surface, incorporating calendars and jumps? Quantify uncertainty in that conversion.
6. **Strategy economics:** Given executable entry/exit option prices, how much predictive advantage is needed to cover theta, vega risk, spreads and trading fees? What horizon/expiration pairs are actually tradable?
7. **Smoothing trade-off:** Does causal smoothing/hysteresis improve *net option strategy utility* compared with raw signals after losing response time to abrupt jumps?
8. **Honest evaluation:** What new time period and option dataset can be kept fully outside model/calibration/strategy selection, and is the resulting study feasible with low-cost or free data?

A useful initial answer in the future thread would be a **feasibility/economic-identification memo**, not a huge Codex execution prompt.

---

## 12. Practical project constraints and instructions for a future agent

- **No work now:** This is a preservation/handoff file. Do not train, refit, backtest, or create new dashboards on reading it. Confirm the hypothesis and the next authorized work package with the user when they return.
- **Cost and engineering discipline are hard requirements.** The earlier S5/S9 campaign produced 89,187 optimizer update batches and over 535,000 nonzero parameter-gradient records with extensive stage receipts. That achieved technical auditability, but the user repeatedly objected to the **engineering overhead**. Future experiments must reuse existing fit/data/plot systems and require **only correctness-critical** time-leakage, target-identity, weighting, proper-score, model-reload and quote-execution tests. Do not build new framework layers, hash every plot as a blocking gate, or perform redundant rehearsals.
- **Read-only analysis first.** S9-MAG is already trained and archived; diagnostics alone require zero new starts. A new strategy pipeline can consume **saved, properly aligned OOS predictions** for exploratory research. A genuine causal calibration/secondary fit requires history available before its target evaluation and an authorized new selection/validation plan.
- **Preserve old results.** Never silently modify S1–S5/S9 artifacts, frozen FT16 recipes, run ledgers, saved checkpoints or historical reports. New experiments get additive namespace and explicit version/status.
- **Budget:** 130/200 neural starts consumed as of completed S5/S9 campaign; **70 remaining** in that ledger, but the remaining starts are **not approval to train anything**.
- **2026 protected:** No numerical 2026 content, hashes or confirmation evaluation without the separate authorized release. Do not use 2025 as an opportunistic tuning year merely because it is not called an OOS fold.
- **Data economics:** User has previously expressed a **free-data preference**. The existing stock dataset and past fits do *not* supply bid/ask options quotes. Genuine historical 1-minute U.S. option NBBO is commonly a commercial dataset; verify feasible options data access **before** promising a realizable options backtest. Do not conflate free historical options volume with historical option quotes.
- **Scientific reporting:** Separate `TECHNICAL PASS`, `PREDICTION SKILL`, `CALIBRATION`, `STRATEGY EDGE`, and `EXECUTION FEASIBILITY`; a pass on the first cannot imply the others. Avoid invented outperformance, return, Sharpe, fill, p-value or realized option trading result.

---

## 13. References and useful reading

### A. Existing project-local materials (primary factual evidence)

1. Executed `reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation/S5_S9_FINAL_RESEARCH_DECISION.md` — scientific summary, completed start ledger and comparisons.
2. Executed `.../S9_TARGET_AND_BASELINE_CONTRACT.md` — authoritative MAG target-scale/control contract; obtain exact implementation-dependent fields here.
3. Executed `.../S5_S9_DETAILED_TRAINING_AND_EXTREME_DIAGNOSTICS.md` — actual epochs and tail-loss decomposition.
4. Executed `.../S5_S9_PAIRED_OOS_UNCERTAINTY.csv` — 2021–24 and equal-year paired deltas, descriptive whole-month intervals.
5. Executed `.../S5_S9_OOS_PAIRED_SOURCE_STOCK_STRATA.csv` — 1,764 matched proper-loss comparisons across S9 families, groups and controls.
6. Executed `.../S5_S9_VISUAL_DIAGNOSTICS.html` — read-only genuine saved-model charts, with model/role/ticker/time selectors.
7. Executed `.../S5_S9_DIAGNOSTIC_INDEX.md` — complete list of 16 run directories and saved outputs; only four MAG runs are directly relevant to this study.
8. `HF20_S5_S9_Combined_Bounded_Codex_Execution_and_Diagnostics_2026-10-26.md` — original approved design intent; **superseded on actual parameters/results by executed receipts**.
9. `HF20_S4A_Revised_Codex_Prompt_S1_S2_Visuals_8_Neural_Starts_2026-10-26.md` — inherited seven-origin/FT16/S4 architecture/source protocol.
10. `HF20_FT16_Complete_Feature_Specification.md` — executed-code FT16 formulas, clock, preprocessing, exact recipe identity and stage lineage, preserved fully in Annex A below.
11. `HF20_S9_MAG_Exact_Replication_Supplement.md` — executed-code source acquisition, QA/quarantine, cohort, split, baseline, seed, training, checkpoint and environment identities, preserved fully in Annex B below.
10. `HF20_LSTM_Comprehensive_Review_and_Expansion_Plan_2026-10-24.md` — E1, QR1, DM1 and older recurrent evidence; study limitations.
11. `HF20_Focused_Second_Pass_Ranking_Inputs_Minute_Data_and_Horizons_2026-10-24.md` — clock/origin/feature/magnitude research questions and broader comparison design.

### B. Public options/market-data references (background, not S9-MAG experimental evidence)

- **Options Industry Council (OIC):** [Long Straddle — structure, premiums, volatility, time decay, breakeven](https://prd-web.optionseducation.org/strategies/all-strategies/long-straddle). Explains the risk of paying two option premiums and negative theta.
- **OCC:** [Characteristics and Risks of Standardized Options](https://www.theocc.com/company-information/documents-and-archives/options-disclosure-document). Authoritative options mechanics and exercise/assignment risks.
- **Cboe DataShop:** [Option Quote Intervals](https://datashop.cboe.com/option-quote-intervals). Documents commercial 1-minute and other quote interval snapshots containing NBBO, strikes/expiries and optional IV/Greeks; **not** a free 2021–24 backtest dataset.
- **Cboe:** [Options Analytics Historical Data](https://www.cboe.com/solutions/options-analytics/historical-data/). Illustrates actual quote/trade/Greeks availability constraints.
- **Nasdaq Data Link:** [ORATS Smoothed Options Market Quotes](https://data.nasdaq.com/databases/OSMV). Premium, daily-frequency example; **daily quotes are not sufficient** for a trustworthy four-hour intraday option-entry/exit backtest.

### C. Formula and research caution

An investor’s expected *physical* absolute move `E_P(|R|)` need not equal an option-implied *risk-neutral* expectation `E_Q(|R|)`. A volatility-risk-premium argument cannot be established by forecast magnitude alone. Historical options strategies must use quoted, synchronized executable markets, term structure, implied-volatility dynamics, bid–ask spreads, fees and proper point-in-time validation.

---

## 14. Definition of “complete” for a later research write-up

A later follow-up should state explicitly whether it accomplished **(A) exact replication of S9-MAG**, **(B) improved calibrated magnitude prediction**, **(C) evidence of predictive advantage over *implied* movement**, **(D) a realistic, cost-aware long-straddle strategy**, and/or **(E) genuine independent confirmation**. These are five separate claims. Each must have the appropriate source and matched comparator. Completing (A) or (B) alone never licenses claims about (C)–(E).

**Retained research conclusion:** S9-MAG is the clearest positive, though still exploratory, evidence from the current compact HF20 LSTM for **four-trading-hour absolute endpoint movement**. Preserve the four annual fold checkpoints, input recipe, transformed-target scale, control fits, decisions, estimates and caveats. Develop thresholds/smoothing/options-based trading as a **separate later research protocol**, not an automatic continuation of the completed LSTM campaign.

---

## 15. Integrated source documentation, authority and preservation

**Extraction provenance (27 October 2026):** The two appended Codex documents report inspection of repository HEAD `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42` (branch `feat/track-a-data-intake`), executed S4/S9 artifacts and saved configuration/recipe files. These descriptions were **not independently reproduced on the original numerical datasets** in this documentation session. Their local-code references and values are source-derived, not new empirical findings. Actual executed artifacts always prevail on discrepancies. Their statements that “only this document was created” refer to their original *read-only extraction tasks*, not to the present consolidation.

The main narrative has been **updated** with the newly established details. The following complete source documents are also preserved **without dropping lesser-used formulas, per-stock coefficients, reference paths or uncertainty statements** so that this file alone is a detailed project handoff. Their standalone Markdown links refer to the original repository root, and may be unresolved when viewed outside that checkout.

### Annex A — Full executed-code FT16 feature specification (preserved source)

#### HF20 FT16 Complete Feature Specification

Extracted 2026-10-27 from existing implementation, fitted recipes and completed-run records at Git commit `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42` (branch `feat/track-a-data-intake`). This describes the **minute-derived HF20/P019B/P020 experiments**, especially completed **S4-A and S9-MAG**, rather than the proposed hourly USA500 research protocol. FT16 contains own-stock information; it has no USA500 channel, stock ID, sector, raw price-level channel or future label channel.

Only this document was created. No training, downloads, dataset reconstruction, new scientific audits, tests or static checks were run. Existing completion/verification receipts below are historical evidence, not checks rerun for this extraction. The explicit single-file scope supersedes the repository's additional session-report-file convention.

##### 1. Authority and exact artifact locations

The following directory aliases are used only to shorten references in this document; all paths are repository-relative.

| Alias | Exact directory |
| --- | --- |
| `P019B` | `reports/data_audit/ta019b_action_qa_2026-10-22_201224` |
| `P020` | `reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122` |
| `S12` | `reports/experiments/hf20_s1_s2_continuation_2026-10-25_204117` |
| `S3` | `reports/experiments/hf20_s3_live_2026-10-26_010204` |
| `S4` | `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation` |
| `S59` | `reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation` |

**Executed evidence takes precedence over proposal labels.** Despite its directory name and the frozen card's `PROPOSED_...` kind, `S4/S4_LIVE_FINAL_VERIFICATION.json` records eight completed neural runs, eight prefix recipes, zero failures and unchanged approved execution. Individual `S4/HF20-S4A-F{21..24}-H4-{NR,T2R}-S42/PASS.json` and saved calibration/refit configurations establish execution. `S59/HF20-S9-F{21..24}-H4-MAG-S42/configuration.json` records `input_dim:16`, seed 42 and execution SHA256 `e19fc1da419d6456d16a7dec7777bc7e1400b2d0412be65ba116906d01cfd73e`; each has a completed `PASS.json`.

`S59/S4_REUSED_RECIPES.json` binds the **eight actual S4 input recipes**, `S4/F{21..24}_{inner,refit}_recipe.json`, by saved SHA256. S9's per-run `inner_target_recipe.json` and `refit_target_recipe.json` are **task/label recipes**, not replacement FT16 scalers. The executed path `hf20_s5s9.Data.phase()` loads the S4 input recipe directly.

Core identity is frozen in [configs/hf1m_long_ft16_v1.json](configs/hf1m_long_ft16_v1.json): feature ID `HF20_HF1M_LONG_v1_FT16_v1`; source `mito0o852/OHLCV-1m`, revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`; action namespace `HF20_HF1M_LONG_v1_ACTION_QA_v1`. `P020/model_input_contract.json` binds source-derived stores, grid, origins, targets and `train_only_fit_recipes.json`; later annual runs reuse the formula family with earlier, fold-specific recipes.

Fixed stock-axis order: `VZ, COP, BAC, BA, AAPL, PEP, MRK, SBUX, CVX, MS, AMD, KO, JNJ, AMZN, XOM, WFC, AVGO, TSLA, MA, CSCO`.

##### 2. Notation, source fields and clocks

For stock \(i\), \(t\) indexes **scheduled, non-stub, completed RTH full-hour positions**, ordered by UTC time. An ordinary session contributes six bars, 09:30–10:30 through 14:30–15:30 Eastern. The final 15:30–16:00 stub is excluded from FT16. Early-close sessions contribute their available full hours; no overnight/weekend bars are inserted. UTC timestamps and `America/New_York` session dates preserve DST/calendar ordering.

- \(O_t,H_t,L_t\): adjusted hourly `open`, `high`, `low`. Open requires the genuine first minute at the scheduled start. High/low are extrema of genuine, unquarantined observed minutes; any quarantine in the hour masks both extrema. A partial observed range is not certified complete-hour high/low.
- \(C_t\): **`close_input_cap5`**, genuine terminal-minute close when available, otherwise the permitted causal terminal close proxy. It is used by OC, B2, T1 and indicators. Distinguish \(G_t=\texttt{close}\), which requires the genuine minute at `hour_end_utc - 1 minute` and is used for daily closes and historical-return endpoints.
- \(U_t\): `volume_for_feature`, derived from `observed_volume`; never price-proxy volume. Units are as-reported source shares. Quality rules are in §4.
- \(D_k\): genuine \(G\) at 15:30 on the \(k\)-th ordinary six-full-hour session. This uses the 15:29 minute's close; it is a **15:30 surrogate**, not the exchange's 16:00 daily close. Earlier missing hours do not invalidate an independently genuine terminal close. Early-close sessions are excluded from this daily series.
- \(W_k\): sum of the six \(U\) values on regular session \(k\), only if all six are finite and share one volume regime. This is six-hour observed/lower-bound volume, not full-session exchange volume.
- \(k(t)\): last regular-session index **strictly before the session containing \(t\)**. All daily components below use this index, including on early-close input days. Set \(d_k=\log(D_k/D_{k-1})\), masking price-basis transitions.
- \(\operatorname{Mean}_{n,m}(x)\), \(\operatorname{RMS}_{n,m}(x)\): last **n scheduled positions**, at least **m finite values**, no run of three missing positions within the window, and no result before n positions exist. Means divide by the number of observed values; RMS is \(\sqrt{\operatorname{mean}(x^2)}\), not demeaned standard deviation. Missing positions remain indexed.

Define \(a_t=\log(C_t/O_t)\), \(s_{12,t}=\operatorname{RMS}_{12,12}(a)_t\), \(s_{60,t}=\operatorname{RMS}_{60,57}(a)_t\), and \(s_{63,k}=\operatorname{RMS}_{63,60}(d)_k\). These hourly RMS values include the current completed hour. Let \(h_i,\delta_i,b_i\) be the fitted hourly, daily and M2 floors; \(q^h_{i,r},q^d_{i,r}\) are fitted volume pseudocounts for the current share regime \(r\), as defined in §4.

Source: `src/lstm_data/hf_minute_long_qa.py:60–88` (`calendar_frame`), `hf1m_action_source.py:67–95,141–248` (`price_factors`, `adjust_prices`, `derive_month`), `hf1m_ft16_math.py:15–33,84–191` (`rolling`, `regime_rolling`, `build`).

##### 3. All 16 native features, in tensor order

Names in code are the IDs below; parenthetical descriptions explain their economic meaning. Formulas are **before affine scaling/fallback**. All 16 outputs are dimensionless. Log returns use natural logs and decimal returns, not percentages or basis points; no volatility annualization is applied.

| # / exact name | Exact native formula | Source fields and lookback | Native units / special rule |
| --- | --- | --- | --- |
| 1 **M1** (hourly momentum) | \(a_t/\max(s_{60,t},h_i)\) | Current `open`, `close_input_cap5`; 60 scheduled hourly OC returns, ≥57 valid | Volatility-normalized return; current OC is included in RMS60 |
| 2 **M2** (same-origin historical momentum) | \(\mu^{(o)}_{20,i,t}/\max(s^{(o)}_{60,i,t},b_i)\) | Genuine historical same-origin endpoint log returns: mean over 20 prior regular-origin days, ≥19 valid; RMS over 60, ≥57 valid | Normalized historical return, session-start locked; exact context/horizon rules below |
| 3 **M3** (five-session momentum) | \(\log(D_k/D_{k-5})/[\sqrt5\max(s_{63,k},\delta_i)]\) | Prior genuine regular-session closes; 5 return intervals plus 63 daily-return RMS positions, ≥60 valid | Volatility-normalized return |
| 4 **M4** (skip-month momentum) | \(\log(D_{k-20}/D_{k-125})/[\sqrt{105}\max(s_{63,k},\delta_i)]\) | Prior genuine daily closes, 105 return intervals ending 20 regular sessions before k; needs close lag 125; daily RMS63 as above | Volatility-normalized return; not a 125-session cumulative return |
| 5 **V1** (short volatility) | \(\log\max(s_{12,t},h_i)\) | `open`, `close_input_cap5`; 12/12 hourly OC returns | Log of decimal-return RMS |
| 6 **V2** (long volatility) | \(\log\max(s_{60,t},h_i)\) | Same fields; 57/60 hourly OC returns | Log of decimal-return RMS |
| 7 **V3** (volatility ratio) | \(V1_t-V2_t\) | Same fields; 12/60 hourly windows | Log short/long floored RMS ratio |
| 8 **B1** (range) | \(\log(H_t/L_t)\) | Current observed adjusted `high`, `low` | Log price ratio; may describe a partial observed range |
| 9 **B2** (close location) | \((2C_t-H_t-L_t)/(H_t-L_t)\) | Current `close_input_cap5`, `high`, `low` | Zero if width is zero; nonfinite width or absolute result >\(1+10^{-10}\) → missing, **not clipped** |
| 10 **Q1** (same-slot relative volume) | \(\log[(U_t+q^h_{i,r})/(\bar U^{slot}_{20,t}+q^h_{i,r})]\) | Current usable hourly volume; mean of previous 20 occurrences of the same scheduled slot, ≥19 valid, current value excluded | Log share-volume ratio; previous slot occurrences can include early-close sessions; all dependencies must match current share regime |
| 11 **Q2** (daily volume trend) | \(\log[(\operatorname{Mean}_{5,5}(W)_k+q^d_{i,r})/(\operatorname{Mean}_{60,57}(W)_k+q^d_{i,r})]\) | Six-hour daily volumes from prior regular sessions; 5/5 and 57/60 | Log share-volume ratio; regime-consistent windows |
| 12 **T1** (moving-average distance) | \(\log[C_t/\operatorname{Mean}_{20,19}(D)_k]\) | Current `close_input_cap5`, 20 prior regular-session closes | Log price ratio; daily mean stays within one price basis |
| 13 **T2** (daily sign trend) | \(\operatorname{Mean}_{20,19}(\operatorname{sign}(d))_k\) | Genuine prior daily closes; 20 daily-return positions, ≥19 valid | Bounded [−1,1]; exact zero return has sign 0 |
| 14 **T3** (short EMA spread) | \((E_{6,t}-E_{18,t})/C_t\) | `close_input_cap5`; recursive EMA6/18, with ≥360 post-seed EMA updates and recent coverage gate | Relative price spread |
| 15 **T4** (long EMA spread) | \((E_{24,t}-E_{72,t})/C_t\) | Same field; recursive EMA24/72, same warmup/coverage gate | Relative price spread |
| 16 **T5** (normalized RSI) | \((\operatorname{RSI}_{14,t}-50)/50\) | Successive `close_input_cap5` price differences; 14 seed changes + ≥140 subsequent Wilder updates, recent coverage gate | Bounded [−1,1]; special zero-gain/loss rules below |

Formula authority: `src/lstm_data/hf1m_ft16_fit.py:49–76` (`native`) and `hf1m_ft16_math.py:123–229` (`build`). The order is `hf1m_ft16_source.py:15–17`, not alphabetical order. M3/M4 momentum numerators require their specified endpoints; the code does not add a separate completeness requirement over all 5/105 intervening closes.

###### M2: historical labels used only after maturity

For P020/S1/S2, context \(o=0\) is the 10:30 origin and \(o=1\) is 11:30. On prior regular day j,

\[
R^{(o)}_{i,j}=\log\left(G_{i,p_j[o+4]}/G_{i,p_j[o]}\right),\quad
\mu^{(o)}_{20,i,t}=\operatorname{Mean}_{20,19}(R^{(o)})_{k(t)},\quad
s^{(o)}_{60,i,t}=\operatorname{RMS}_{60,57}(R^{(o)})_{k(t)}.
\]

Here \(p_j[0..5]\) are that day's six full-hour positions. Endpoints must be genuine and price-basis compatible. The forecast's context is held fixed across **all 48 historical steps**, but each step uses its own preceding-day history. It is not a current forecast's future return repeated into the sequence.

S4/S9 use seven contexts: `0..5 = 10:30,11:30,12:30,13:30,14:30,15:30`, `6 = 09:30`. Historical R is the genuine endpoint return over **240 XNYS trading minutes**, including closing stubs and pausing across closures; later origins can mature next session. Opening R uses the genuine first-minute **open**, not close. For each historical input session, only prior regular-origin days enter; an endpoint whose `label_maturity_utc >= current session 09:30` is masked **within its original scheduled slot**. In particular, the latest overnight outcome is not available merely because its origin day is yesterday. Apply the same 20/60 count/gap rules; values are locked for that entire input session. Early-close input days use preceding regular-origin dates with the same maturity test. COP dependency masks also apply.

Authority: `hf1m_ft16_math.py:157–159,214–229`; `hf20_s4_clock.py:18–70`; `hf20_s4_preflight.py:143–212,219–250`. S3-B's verified horizon substitution is described in §6.

###### EMA and RSI state, exactly

For each period p ∈ {6,18,24,72}, seed \(E_p=C\) at the first valid close; thereafter \(E_{p,t}=\alpha_p C_t+(1-\alpha_p)E_{p,prev}\), \(\alpha_p=2/(p+1)\). The first seed does **not** increment `ema_updates`. T3/T4 require `ema_updates >= 360`. All T3/T4/T5 outputs additionally require a valid current close and ≥69 valid closes in the last 72 scheduled positions with maximum missing run two; the full 72 positions must exist.

RSI seeds average gain/loss with arithmetic means of positive/negative parts of the first 14 valid predecessor-connected price changes. Each later connected change Δ updates \(A=(13A+\max(\Delta,0))/14\), \(B=(13B+\max(-\Delta,0))/14\). After ≥140 such post-seed updates, \(RSI=100-100/(1+A/B)\). Normalized output is 0 when A=B=0, +1 when only B=0, −1 when only A=0.

A missing close freezes EMAs and clears the RSI predecessor. Before RSI seeding it also clears seed changes; after seeding it preserves gain/loss averages but creates no change across the gap. Three consecutive invalid scheduled full-hour closes reset the entire indicator state; a price-basis change also resets it. Normal overnight closure is not a missing scheduled observation. Authority: `stock_features.py:44–96` (`IndicatorState`); `hf1m_ft16_math.py:192–213`.

##### 4. Preprocessing, fitted parameters and fallback

###### Price, volume and missingness policy

P019B adjusts **OHLC prices only** backward for verified splits through 2026-03-31; prices are split-consistent, not dividend-total-return adjusted. Volume remains in observed share units. COP's 2012-05-01 spinoff separates price bases; the 125-regular-session dependency history plus 48-step envelope is masked. Split share regimes separately reset incompatible volume ratios. No unverified inverse split-volume conversion is applied. See `configs/hf1m_action_qa_v1.json`, `configs/hf1m_p019_verified_event_facts_v1.json`, `hf1m_action_source.py:67–95,237–256`, `hf1m_action_release.py:208–236`, and S4's equivalent `hf20_s4_preflight.field_masks():25–54`.

P019B removes 18 unresolved RTH minutes; genuine expected opens/closes can survive independently, but affected-hour high/low are masked and volume is unusable. No close proxy is allowed in a quarantined hour. Elsewhere `close_input_cap5` can reuse an original causal terminal proxy with missing-run cap five. Proxy creation uses a preceding observed close, never interpolation from a later bar, and rejects no-observation/action-blocked bins; carry state resets each session. The completed bin's known gap length determines acceptance; a later-discovered longer outage cannot rewrite an earlier trailing proxy. See `hf_minute_long_qa.py:92–118,395–403` and `hf1m_action_source.py:210–234`.

Usable hourly volume requires at least one genuine minute, ≤5 absent minutes, longest gap ≤5 minutes, and **zero conflicts, quarantines and invalid minutes**. Absent-minute zero is a feature-only assumption: observed sums remain lower bounds, not evidence of no trades. Otherwise \(U_t\) is missing. Real observed zero volume is retained. Daily W requires all six usable hours and compatible volume bases; stub volume is excluded. Q1's prior matching slots and Q2's daily windows cannot mix share regimes. Missing or unseen fitted pseudocount regimes produce native missingness, then feature fallback. Authority: `hf1m_ft16_math.py:36–63,147–191`.

###### Fitting population and numerical rules

For each fold/phase, the fit-hour set F is the **union** of all 48 scheduled history keys of `source_input_eligible` origins in that training prefix, clipped to `[2011-04-01, fit_stop_inclusive]`. No overlapping-window multiplicity and no label-value filter are used to choose feature-fit keys. Warmup components may use source history from July 2010, but those pre-start keys are excluded from fitted input statistics. For daily floor and M2 pools, J is the first F timestamp per input session (`drop_duplicates("session_date_et")`), including eligible early-close input days.

| Fitted quantity | Exact estimation |
| --- | --- |
| Hourly floor \(h_i\) | NumPy 5th percentile of strictly positive finite RMS12 **concatenated with** RMS60 at F, separately per stock (a timestamp can contribute both RMS values) |
| Daily floor \(\delta_i\) | NumPy 5th percentile of positive finite carried RMS63 values at J, separately per stock |
| M2 floor \(b_i\) | Weighted 5th percentile of positive finite M2 RMS values at J, separately per stock; context total mass 1/2 for original two-context runs, 1/7 for S4/S9; equal weights within each context's valid values |
| Hourly/day volume pseudocount | 0.01 × median positive finite volume, separately per stock and share regime. Hour pool uses F; daily pool uses **all regular days** in `[2011-04-01, stop]`, not just J. Both hour and day positive pools must exist for that regime |
| Common-channel center/scale | Native finite values pooled across stocks and unique F timestamps, independently for each of the 15 non-M2 channels; no window/session-loss weighting |
| M2 center/scale | Native finite stock/session/context values at J, pooled across stocks with equal total mass per context (1/2 or 1/7), not weighted by forecast-slot frequency |

An unweighted quantile uses `np.quantile` / `np.percentile` default linear interpolation. A weighted quantile sorts values stably and selects the first value whose normalized cumulative weight is ≥q (`searchsorted(..., side="left")`); it does not interpolate. Missing all required positive/native training pools raises an error; it does not borrow another stock's floor or another regime's pseudocount.

For each of the **13 unbounded channels** (M1/M2/M3/M4/V1/V2/V3/B1/Q1/Q2/T1/T3/T4), let c be its native training median and MAD = median(|x−c|), using the above weights for M2. Use scale s = MAD if positive; otherwise `(Q75−Q25)/1.349`; otherwise population SD about the mean; otherwise exactly 1 for a constant. **MAD is unscaled**, without a 1.4826 factor. Replace nonfinite native x with c, then output `(x−c)/s`. Consequently these fallbacks become model-space zero. Fit statistics use native values **before imputation**.

**B2/T2/T5:** replace nonfinite values by neutral 0; center 0/scale 1, `BOUNDED_IDENTITY`. There is **no input clipping, winsorization, asinh/log1p mapping of the full tensor, or per-sequence normalization**. Feature-specific logarithms and denominator floors are already part of the native formulas. Final arrays are cast to `float32`; component arithmetic generally uses NumPy floating arrays. Native-missing/fallback/proxy/quality masks remain separate diagnostic data, not extra FT16 channels. A missing required input close cannot be repaired by feature median fallback to admit a deficient 48-close window. Targets have no feature-style imputation.

Authority: `hf1m_ft16_fit.py:12–46,49–187`; S4 seven-context counterpart `hf20_s4_fit.fit_expanded():13–125`; recipe application `hf20_s4_witnesses.scaled():19–32`; prefix selection `hf20_s4_data.py:105–157` and `hf20_ranking_data.py:189–243`.

###### Actual saved fitting windows

S4 and S9 use the following eight input recipes. Every start is **2011-04-01**; an inner recipe is applied unchanged to inner validation, and a refit recipe unchanged to that fold's OOS year. All exact floors, pseudocounts, scalers, native fallbacks and fit-hour indices are in the corresponding `S4/Fxx_phase_recipe.json` (`floors`, `scalers`, `fallbacks`, `fit_hour_indices`).

| Fold / OOS year | Inner inclusive stop | Refit inclusive stop | Unique F timestamps inner / refit | Unique J sessions inner / refit |
| --- | --- | --- | --- | --- |
| F21 / 2021 | 2020-06-30 | 2020-12-31 | 13,102 / 13,864 | 2,198 / 2,326 |
| F22 / 2022 | 2021-06-30 | 2021-12-31 | 14,567 / 15,247 | 2,445 / 2,560 |
| F23 / 2023 | 2022-06-30 | 2022-12-30 | 15,991 / 16,716 | 2,684 / 2,808 |
| F24 / 2024 | 2023-06-30 | 2023-12-29 | 17,420 / 18,164 | 2,926 / 3,052 |

Original P020 preparation's `P020/train_only_fit_recipes.json` instead has inner stop **2023-01-23** and refit stop **2025-06-30**. Those are not the annual S4/S9 recipes and must not be substituted for them. S1/S2 annual recipes also share the earlier cutoffs above but have different input-key populations, e.g. F21 inner has 13,057 F timestamps / 2,197 J sessions rather than S4's 13,102 / 2,198.

##### 5. Exact 48-step sequence and leakage controls

For an admitted origin, set `first_step = entry_index − 47`. Gather the 48 consecutive scheduled grid positions `first_step + arange(48)` in chronological order. The common 15 fields depend on stock and historical timestamp; M2 additionally selects the **forecast-origin context for every historical step**. In S4, `assemble()` returns `[origins, 20 stocks, 48 steps, 16 features]`, `float32`, in §3 order. The LSTM receives stock sequences reshaped to `[origins×20,48,16]`; weights are shared across stocks, and hidden/cell states start at zero on every call. No recurrent state carries from an overlapping prior sequence.

At a full-hour forecast, the last step is the bar ending at that origin. At conditional **09:30**, the last step is the most recent prior-session full-hour bar (normally ending 15:30, or 12:30 on an early close). Neither the new day's 09:30–10:30 bar nor the opening price is inserted into FT16. The opening price is a genuine reference for labels only. Thus 48 means scheduled trading observations, **not 48 elapsed clock hours**, and feature calculations can require substantially older history.

Input eligibility requires all 20 stocks to have 48 finite cap5 input closes, the daily-history warmup (`day_index >=125`, allowing the required 126 prior regular-session closes), ≥360 cumulative genuine hourly closes, and the COP dependency envelope. Other native channel deficiencies use the declared feature fallback. Input eligibility is computed independently of future endpoint validity; supervised/evaluation membership additionally requires a complete eligible 20-stock label panel. S4's final `eligible` combines its source and label masks, rather than manufacturing missing endpoints.

Issuance is assumed at origin +2 minutes; label maturity at genuine endpoint +2 minutes. S4 endpoints consume 240 actual trading minutes and may include overnight closure; the price-only return starts at the nominal origin, **before issuance**, and is not an executable fill return. For a normal 10:30 forecast the newest feature bar covers 09:30–10:30; for 09:30 issuance at 09:32, inputs still end with the prior session's last full hour. Publication latency is an assumption, not verified historical availability.

Daily statistics always use prior regular days, Q1 shifts same-slot history by one occurrence, all rolling functions are backward-looking, and M2 maturity is checked at **each historical input session**, not just at the current prediction time. Scalers/floors/fallbacks are prefix-only and fixed for the relevant validation/OOS phase. Split admission requires the first of all 48 input steps to be after the preceding boundary (48-full-step embargo), and labels to mature before their role cutoff. S4 additionally retains the conservative four-hour boundary limit: cutoff-day local midnight +1 day −4 hours, with `label_maturity_utc < limit`. Future outcomes remain labels except for strictly matured historical outcomes used in M2.

Authority: `hf20_s4_preflight.input_valid():57–67` and `run():235–255`; `hf20_s4_witnesses.assemble():35–56`; `hf20_s4_data.S4Data:32–76,159–178`; `hf20_s4_epoch.py:47`; `neural_engine.SharedLSTM:28–54`. Original two-slot gather: `hf20_ranking_data.assemble():24–49`. S4 clock: `hf20_s4_clock.schedule():39–70`.

##### 6. Are S1–S9 identical?

**No: stable feature IDs/economic meanings do not imply identical contexts, fitted parameters or complete model inputs.**

| Stage | Verified executed input treatment |
| --- | --- |
| S1 | Baselines consume the original two-context FT16 path; full-history ridge uses the 48-step information. Not every control uses all channels: N1/N2 use M1/sign reversal; N0/P are constant/profile controls. See `S12/S1_FOUR_FOLD_RANKING_BASELINES.md` and `S12/Fxx_phase_recipe.json` |
| S2 | Same two-context FT16 recipe family and per-fold inputs as S1 for T2R/NR/PW; objectives differ, not feature formulas. Failed F21 PW is preserved and has no completed refit/OOS surrogate. See `S12/S2_FOUR_FOLD_LSTM_RANKING_COMPARISON.md`, `hf20_ranking_data.py` |
| S3-A | H1/H2 labels change, but all 16 input channels, including original **four-hour M2**, reuse S1/S2 phase recipes. H4 references are archived runs, not new fits |
| S3-B | **Only M2 changes** to historical same-origin H1 or H2 genuine endpoint returns; mean20/RMS60, gap rules, two contexts and 50/50 pooling remain. M2 floors, fallback center and scaler are refitted on the original unique input-prefix day keys. Other 15 channels remain unchanged. Saved `S3_M2` overrides are authoritative; inherited top-level M2 fields are lineage, not the active B parameters |
| S4-A | Same 15 non-M2 native formulas; **seven M2 contexts**, 240-trading-minute endpoint/maturity handling and prior48 opening inputs. Feature-fit origin/key support expands, so even common-channel fitted floors/scalers can differ from S1/S2. M2 pooling changes to equal 1/7 context mass. NR and T2R share these phase recipes |
| S5 | Reuses S4 FT16 unchanged, then appends **six clock fields**, making **22 model inputs**: `step_sin`, `step_cos`, `session_boundary`, `elapsed_scheduled_wall`, `origin_sin`, `origin_cos`. Scheduled elapsed time is not observed-price age; source-repair flags are not model features |
| S6–S8 | **NOT VERIFIED as executed FT16 experiments.** Latest completed S5/S9 handoff explicitly states no S6/S7/S8 was launched; no identical-feature assertion is justified for those stages |
| S9-MAG / EVENT / QUANTILE | Exactly S4's 48×16 input and saved phase recipes, no S5 extra metadata. Different label/head/objective definitions do not change FT16 |

S3 evidence: `S3/EXECUTION_MANIFEST.json`, `S3/S3_FINAL_RESEARCH_DECISION.md`, `S3/{A,B}/Fxx_H{1,2}/Fxx_phase_recipe.json`; `hf20_horizon_data.py:42–45,92–164`; `hf20_horizon_math.py:98–175`. In B, apply `S3_M2.floors` and `S3_M2.scaler`. Older `hf20_s3_horizons_2026-10-26_000127_preparation` documents marked NOT_RUN predate completed live execution and do not establish final run status.

S5/S9 evidence: `hf20_s5s9.py:23–51,82–131`; S6–S8 status: `S59/LIVE_WORK_SESSION_REPORT.md`, §16. For MAG specifically, the optimized target is `log1p(abs(R)/magnitude_scale)`, with prefix-fitted magnitude scale; this is **not a feature transformation** (`hf20_s5s9.py:60–67,141–179`). Likewise the target-transform term **T2/T2R/asinh is distinct from FT16 feature T2**, the daily sign average.

##### 7. Source map for replication

Line ranges refer to source at the extraction commit; paths below are exact. No module listed here was executed for this extraction.

| File | Relevant implementation / evidence |
| --- | --- |
| `configs/hf1m_long_ft16_v1.json:1–91` | Source revision, symbols, feature ID/order, warmup/splits, volume tier, timing assumptions; original P020 recipe defaults |
| `configs/hf1m_action_qa_v1.json` and `configs/hf1m_p019_verified_event_facts_v1.json` | Frozen price adjustment, quarantine and event facts; volume regime policy |
| `src/lstm_data/hf1m_action_source.py:67–95,141–309` | Price split factors, genuine-hour aggregation, quarantines, cap5 terminal input-close selection |
| `src/lstm_data/hf_minute_long_qa.py:48–118,395–403` | Minute validity, session-hour grid, causal bounded proxy rules |
| `src/lstm_data/hf1m_action_masks.py:39–41,49–108` | Scheduled full-window AND, original source warmup/basis eligibility |
| `src/lstm_data/hf1m_action_release.py:208–236` | P019B volume-basis and COP dependency overlay |
| `src/lstm_data/hf1m_ft16_source.py:13–17,24–101` | Exact order/bounded IDs, source allowlists and identity checks |
| `src/lstm_data/hf1m_ft16_math.py:15–63,84–232` | Rolling rules, quality-conditioned volume, all source components/daily alignment/original M2 |
| `src/lstm_data/stock_features.py:44–96` | Actual imported EMA/Wilder state; other legacy feature calculators are not this pipeline |
| `src/lstm_data/hf1m_ft16_fit.py:12–187` | Quantiles, robust scales, positive floors, native 16-channel formulas and original two-context fitting |
| `src/lstm_data/hf1m_ft16_prepare.py:47–102,129–154` | P020 origin/window timing, input-only fitting keys, separate target parameters |
| `src/lstm_data/hf20_ranking_data.py:24–49,75–140,189–273` | S1/S2 gather, annual split masks and actual prefix recipes |
| `src/lstm_data/hf20_s4_clock.py:10–83` | XNYS schedule, actual trading-minute endpoints, seven contexts and issuance/maturity |
| `src/lstm_data/hf20_s4_preflight.py:25–67,70–140,154–212,235–255` | P019B-equivalent masks, permitted monthly source inventory, expanded M2 and prior48 opening indices |
| `src/lstm_data/hf20_s4_fit.py:13–125` | Executed S4 seven-context fitting implementation (historical docstring still says proposed) |
| `src/lstm_data/hf20_s4_witnesses.py:19–56` | Apply sealed scales and gather exact float32 48×16 tensors |
| `src/lstm_data/hf20_s4_data.py:32–76,90–178` | Fold maturity/embargo, fitting keys, saved recipe application and role guards |
| `src/lstm_data/hf20_s4_run.py:30–45` | Actual source adapter loads card-selected `opening_reaudit_v2` source/endpoint stores and replaces M2 components with seven-context values |
| `src/lstm_data/hf20_s5s9.py:82–131` | S9 reuses exact S4 recipes; only S5 appends metadata |

For byte-exact input replication, preserve the **saved recipe**, not just the written formulas. Resolve the recorded monthly inputs from `P019B/adjusted_hourly_manifest.json` and `S4/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv`. The adjusted-hourly root is `data/processed/hf20_hf1m_long_v1_action_qa_v1/ta019b_action_qa_2026-10-22_201224/hourly/`. S4 source/role identities are in `S4/opening_reaudit_v2/S4_ORIGIN_SOURCE_ELIGIBILITY.parquet`, `S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet` in that same subdirectory, and `S4/Fxx_{inner_train,inner_validation,refit,oos}_indices.csv`.

Existing scalar/tensor evidence: `P020/independent_oracle_and_causality.json`, `P020/preparation_execution_snapshots/hf1m_ft16_{math,fit,source,prepare,loader}.py.txt`, and `S4/opening_reaudit_v2/{S4_ARCHIVED_ALL16_TENSOR_IDENTITY,S4_ALL16_SCALAR_SOURCE_WITNESSES}.csv`. These are supporting historical records; archived original-recipe tensor identity does **not** mean newly fitted S4 recipes equal S1/S2 recipes. S9 input-recipe SHA identities are recorded in `S59/S4_REUSED_RECIPES.json`.

##### 8. NOT VERIFIED / replication qualifications

- **NOT VERIFIED — historical publication latency and point-in-time availability.** Config explicitly sets `publication_timing_verified:false`; two-minute issuance is assumed. Arithmetic cutoffs/maturity controls do not certify that a vendor delivered each minute, opening quote or correction by that time.
- **NOT VERIFIED — historical action-information vintage.** Executed OHLC uses backward split factors through March 2026 and known quarantine/event facts. This is the implemented retrospective representation; it does not prove those facts were known contemporaneously. Scale invariance and stored causal-prefix evidence do not independently certify historical publication timing.
- **NOT VERIFIED — economic meaning of missing minute volume, complete extrema and share-volume adjustment.** Small absent gaps are assumed zero only for features. Provider absence versus no trading is unresolved; observed ranges/volumes can be incomplete. No independently verified inverse split-volume convention exists, so replication must retain share-regime masking rather than invent an adjustment.
- **NOT VERIFIED — bitwise reproduction on another machine from this document alone.** Exact source bytes, recorded adjusted-hourly/endpoint stores, fitted numerical recipes, grid order and compatible NumPy/pandas/calendar versions remain necessary. This extraction did not reopen numerical datasets, rerun hash audits, reconstruct tensors or validate a clean-machine replay. Existing manifests/receipts supply recorded identities, not a fresh certification. Private source accessibility/redistribution is not established here.
- **NOT VERIFIED — S6/S7/S8 executed definitions.** The latest completed handoff says they were not launched; proposals cannot supply executed definitions. No feature equality claim is made for them.

No unknown formula or parameter was filled from a generic indicator library, older source branch, proposal or inferred research preference. Numerical input parameters are available in the cited saved recipes; they are phase-specific, not universal constants omitted from the implementation.


### Annex B — Full S9-MAG reproducibility supplement (preserved source)

#### HF20 S9-MAG Exact Replication Supplement

Documentation extraction, 2026-10-27; inspected repository HEAD `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42`, branch `feat/track-a-data-intake`. Scope: the four completed seed-42 **HF20 S9-MAG** lifecycles, F21–F24. This is an exploratory retrospective absolute-return-magnitude experiment, with no trading simulation or protected-2026 evaluation.

The executed code, saved recipes, role indices, configurations, checkpoint contents and binding records govern this specification. The existing [FT16 specification](HF20_FT16_Complete_Feature_Specification.md) supplies the detailed 16-feature formulas; this supplement specifies their S9-MAG application. Only this new document was written. Checkpoints were deserialized for inspection without model construction, forward inference or updates. No downloads, preprocessing, training, audits or tests were run, and no existing files were changed. The explicit one-file request overrides the additional session-report-file convention.

##### 1. Identities and authoritative artifacts

These aliases below denote exact repository-relative directories, not alternate sources.

Unless explicitly identified as PyTorch package code, an unprefixed Python module reference such as `hf20_s5s9.py:60–67` means `src/lstm_data/hf20_s5s9.py` at those lines in the inspected repository version.

| Alias | Directory |
| --- | --- |
| `A18` | `reports/data_audit/ta018d_hf1m_long_2026-10-22_155547` |
| `P019B` | `reports/data_audit/ta019b_action_qa_2026-10-22_201224` |
| `P020` | `reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122` |
| `S4` | `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation` |
| `S9` | `reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation` |
| `MAGxx` | `S9/HF20-S9-Fxx-H4-MAG-S42`, xx ∈ {21,22,23,24} |

All four `MAGxx/configuration.json` record the same input dimension 16, seed 42, initialization identity and execution hash. Each has `PASS.json`, two target recipes, two checkpoint bindings and four saved role score/metric bundles. `S9/S5_S9_VERIFICATION.json` records all 16 campaign lifecycles completed, including these four MAG runs. Do not substitute rehearsal outputs, proposal-only receipts or other S9 objectives.

- Source revision: `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`.
- Action namespace: `HF20_HF1M_LONG_v1_ACTION_QA_v1`; feature ID: `HF20_HF1M_LONG_v1_FT16_v1`.
- S9 execution SHA256: `e19fc1da419d6456d16a7dec7777bc7e1400b2d0412be65ba116906d01cfd73e`.
- S4 execution SHA256: `a737c9219513ddbbfffb882a2e76af7708e2f3ee55a297e1b145790bc47f2a95`.
- Recorded preparation/live-session starting Git HEAD: `960b81753036366522dbbd61189d4e4d51d25967` (`S9/START.json`, `reports/codex_sessions/2026-10-27_005216_hf20_s5_s9_live_final.md`). Execution included then-uncommitted files; that Git SHA alone is insufficient. Use the recorded execution hash and artifact bindings.

`src/lstm_data/hf20_s5s9_run.py:36–46` defines the S9 code hash from the S4 execution identity plus the `hf20_s5s9*` files; `hf20_s4_authority.py:21–41` defines the underlying source bundle. `S9/design.json`, `LIVE_AUTHORITY.json`, `EXECUTION_STARTED.json`, `S4_REUSED_RECIPES.json` and the v23 journal `reports/audit/track_a_real_pairs_v23_hf20_s5_s9.jsonl` bind the actual campaign. Earlier preparation status is not final execution status.

##### 2. Dataset, acquisition and historical clock

###### Provider, files and request semantics

The source is the Hugging Face dataset uploaded under **`mito0o852/OHLCV-1m`**: [dataset page](https://huggingface.co/datasets/mito0o852/OHLCV-1m). **NOT VERIFIED:** the uploader's original exchange/vendor feed, consolidation/feed tier, historical correction vintage and independent completeness certification. This was not an Alpaca, TwelveData, Yahoo or course USA500 download.

Acquisition code uses these immutable endpoints, where `REV` is the revision above and `YYYY-MM` the selected provider month:

```text
https://huggingface.co/api/datasets/mito0o852/OHLCV-1m/revision/REV
https://huggingface.co/api/datasets/mito0o852/OHLCV-1m/tree/REV?recursive=true&limit=1000
https://huggingface.co/datasets/mito0o852/OHLCV-1m/resolve/REV/data/ohlcv_YYYY-MM.parquet
```

There are **no server-side ticker/date/adjustment/bar-size query parameters**. Code scans monthly Parquet ticker columns and filters exact strings locally. Sparse reads add `?range_start=START&range_end=END` and HTTP `Range: bytes=START-END`, `Accept-Encoding: identity`; all seven source columns are selected from relevant row groups, `use_threads=False`. If projected selected-group compressed bytes exceed 75% of file size, the code uses a complete-month streamed download and its pinned SHA256 instead. Range reads validate returned range/size; full downloads validate complete size/hash. HTTP uses no login/credentials, `trust_env=False`, no automatic retries; recorded redirects/requests and per-month strategies are in `A18/months/YYYY-MM/{http_events.jsonl,raw_receipt.json,row_groups.json}` and the complete manifest. The threshold is a transport choice, not a sample filter.

Authority: `src/lstm_data/hf_minute_long_io.py:188–258,261–305,309–438` (`verify_remote`, `selected_table`, `stream_full`, `acquire_month`), `hf_minute_boundary_io.py:17–18,22–75` (`RemoteParquet`), `hf_hourly_source.py:41–104` (`PublicHTTP`).

**Stock-axis order, preserved everywhere:**

```text
VZ COP BAC BA AAPL PEP MRK SBUX CVX MS AMD KO JNJ AMZN XOM WFC AVGO TSLA MA CSCO
```

This fixed surviving-stock cohort is not historical index membership; survivorship/issuer lineage remains a qualification. No OOS performance-based stock selection is implemented in these runs.

###### Distinguish acquired history from S9-used history

| Layer | Exact date/month policy |
| --- | --- |
| Activated minute acquisition | 189 monthly files, July 2010–March 2026; manifest `A18/complete_acquisition_manifest.json`. Earlier legacy acquisitions are excluded from the active source |
| P020 preparation | Warmup 2010-07-01–2011-03-31; original training 2011-04-01–2025-06-30; development 2025-07-01–2025-12-31; protected 2026-01-01–2026-03-31 |
| **S9 numerical source** | **Only July 2010–December 2024** monthly adjusted-hourly and genuine-minute partitions; no 2025 tuning or protected-2026 numerical access/hash. Source inventory: `S4/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv` |
| S9 fitted samples | Expanding training prefixes beginning 2011-04-01; annual OOS years 2021,2022,2023,2024; exact admitted dates in §4 |

Nominal source bounds do not imply every stock/minute exists. Preserve the per-stock missingness and exact saved origin indices. The full stock/minute tape was not independently re-read for this document; per-symbol first/last genuine-minute timestamps are **NOT VERIFIED here**. Existing per-session coverage is bound by `A18/ticker_session_hour_coverage_manifest.json`.

###### Timestamp and minute-to-hour construction

Raw schema is `timestamp: timestamp[ns,UTC]`, float64 `open,high,low,close,volume`, and string `ticker`; source rows/file/row-group identities are appended without overwriting raw values. The pipeline interprets timestamps as **minute starts**. Calendar is `exchange_calendars` **XNYS**, with actual holidays, early closes and DST. RTH minute starts are `[session.open, session.close)`; ET dates use `America/New_York`. Noncalendar/extended observations remain source evidence but do not enter hourly features or endpoint anchors.

Bins are anchored at 09:30 ET: offsets `floor(minute_of_session/60)`. Normal full hours are 09:30–10:30 through 14:30–15:30; a separate 15:30–16:00 stub is retained in source processing but excluded from FT16. A normal full-hour close at 10:30 means the close of the **10:29 minute**. Genuine hourly open requires an observation at the scheduled first minute; genuine close requires `hour_end−1 minute`. High/low are extrema of safe observed minute highs/lows, volume their sum. Partial observed extrema are not certified complete-hour extrema. Empty/missing scheduled positions remain indexed.

Authority: `src/lstm_data/hf_minute_boundary.py:70–80,223–237` (`validate_schema`, `session_grid`), `hf_minute_long_qa.py:48–88`, `hf1m_action_source.py:141–204` (`derive_month`); S9 source loader `hf20_s4_preflight.py:70–140`.

###### Corporate actions and point-in-time limitations

Prices are backward split-consistent OHLC in the March-2026 share basis: for each applicable split at date e, divide prices strictly before e by `factor_denominator`; multiply factors when needed. Volume is unchanged. There is no dividend/total-return adjustment or fabricated inverse split-volume adjustment. The exact event facts are `configs/hf1m_p019_verified_event_facts_v1.json`, used by `configs/hf1m_action_qa_v1.json`.

Applied splits: KO 2012-08-13 ×2; MA 2014-01-22 ×10; AAPL 2014-06-09 ×7 and 2020-08-31 ×4; SBUX 2015-04-09 ×2; TSLA 2020-08-31 ×5 and 2022-08-25 ×3; AMZN 2022-06-06 ×20; AVGO 2024-07-15 ×10. COP's 2012-05-01 spinoff has no invented multiplicative adjustment: preserve levels in separate PRE/POST price bases and exclude dependent histories crossing the boundary. Split dates create separate as-reported share-volume regimes.

Authority: `src/lstm_data/hf1m_action_source.py:67–95,237–256`; COP/volume masks `hf1m_action_release.py:208–236`, S4 equivalent `hf20_s4_preflight.field_masks():25–54`.

**NOT VERIFIED:** historical arrival/publication times of bars, openings, corporate-action facts and corrections. Factors/quarantine decisions are retrospective. `configs/hf1m_long_ft16_v1.json` explicitly records `publication_timing_verified:false`. Origin+2-minute issuance is a proxy, not an exchange execution timestamp. Dataset access was based on human-reported maintainer permission for private research; redistribution and independent data rights are not certified by this supplement.

##### 3. Data quality: source treatment versus feature treatment

###### Source detection, filtering and correction

1. Parse timestamps in UTC; reject NaT, non-minute alignment and rows whose ET month differs from their file month. Require finite OHLCV, positive OHLC, nonnegative volume, high ≥ every OHLC value and low ≤ every OHLC value. Preserve genuine zero volume and rare/extreme candles otherwise.
2. Exact duplicates across the seven original fields collapse to one canonical observation. If distinct versions share `(ticker,timestamp)`, **all versions are excluded**, not first/last selected or averaged. Raw records remain immutable. The activated full-history acquisition report records no invalid raw rows or exact-copy duplicates, but 856 conflicting records / 406 keys excluded; these are full-source counts, not S9-only sample counts.
3. Compare expected XNYS minute grid against canonical observations to flag absence, conflict/invalid minutes, missing opens/closes, longest gaps, no-observation bins and coverage outside first/last source dates. No pre/post-coverage price history is invented.
4. Source QA flags absolute adjacent genuine-close changes >`log(1.25)` across overnight/month boundaries, genuine zero volume, and 30 consecutive same-OHLC zero-volume observations. These flags alone do not delete a genuine market move. Large jumps block original proxy creation in the affected bin.
5. P019 scans additional event candidates using: ALL_SESSION adjacent close and open/previous close; RTH adjacent close; minute body `abs(log(close/open))>log(1.25)`; minute high/low >1.5; session first-30/previous-session last-30 observed-close median ratio outside `[1/1.25,1.25]`. Comparisons are strict. Session medians are retrospective diagnosis only. External evidence/manual dispositions, not an automatic return cap, decide action treatment.
6. P019B's 67 candidate IDs resolve to 17 split-adjusted candidates, 4 genuine moves retained, 18 unresolved RTH minutes locally quarantined, 24 EH out-of-scope candidates, 3 KO mixed-basis premarket candidates excluded from RTH influence, and the COP spinoff boundary. Do not remove every detected jump. All five fields of the 18 RTH minutes are excluded; 14 affected hourly bins are reaggregated. Independently genuine scheduled opens/closes may survive; high/low and volume quality are untrusted, and **no proxy is allowed anywhere in an anomaly-containing hour**.

Exact dispositions/timestamps are in `P019B/unresolved_event_ledger_v3.json`, bound by `canonical_event_ledger_pointer.json` to SHA256 `015d672c11d61b3a14441a2abbfb689ffa59191016398bdc32bb580524a0b937`. This ledger, not the summary counts, reproduces the exclusions. Quality tiers are diagnostic metadata; the eventual S4 origin mask is the actual admission rule.

Sources: `src/lstm_data/hf_minute_long_qa.py:48–57,176–240,306–440`; `hf1m_action_audit.scan_stock():110–174`; `configs/hf1m_p019_action_scan_v1.json`; `hf1m_action_source.event_dispositions():98–138` and `derive_month():141–309`. Acquisition findings: `reports/codex_sessions/2026-10-22_184817_ta018d_hf1m_long.md`.

###### Input close proxies and feature-level fallback

Original cap5 proxies are a separate derived layer, not genuine raw bars. A missing run can reuse its preceding observed close only when its completed-bin known length, including a leading carry gap, is ≤5 minutes. No future-price interpolation, overnight carry, no-observation-bin fill or action-blocked-bin fill occurs; state resets per session. A trailing short run remains accepted under the information known at that completion even if the next bin reveals a longer outage. P019B uses only a permitted terminal proxy for `close_input_cap5`, split-adjusted like prices; genuine `close` remains separate. Proxy OHLC/zero-volume placeholders do not become genuine extrema or observed volume. Sources: `hf_minute_long_qa.bounded_hour_proxies():92–118,395–403`; `hf1m_action_source.py:210–234`.

FT16 order is `M1 M2 M3 M4 V1 V2 V3 B1 B2 Q1 Q2 T1 T2 T3 T4 T5`; exactly 48 full-hour steps, no S5 clock metadata. Apply `S4/Fxx_{inner,refit}_recipe.json` as-is; `S9/S4_REUSED_RECIPES.json` records all eight hashes. Important distinctions from source cleaning:

- Hour volume is usable only with >0 genuine minutes, ≤5 absent minutes, longest gap ≤5, zero conflicts/quarantines/invalid minutes. Absent-minute zero is a feature-only assumption; volume remains an observed lower bound. Otherwise volume-derived channels become native missing. Daily volume requires six usable full-hour sums in one share regime; stubs excluded.
- Rolling windows keep scheduled gaps: required counts include 12/12 or 57/60 hourly OC returns, 60/63 daily returns, 19/20 matching-slot histories; maximum two consecutive misses. Indicators freeze/disconnect on missing closes and reset after three invalid full-hour positions or basis transitions. Full EMA/RSI seeding rules are in the FT16 specification and `stock_features.IndicatorState():44–96`.
- Fitted floors and volume pseudocounts use unique input-only eligible training-prefix keys; hourly/day volume pseudocounts are 1% of positive training medians by stock/share regime. An unfitted regime stays native missing. M2 uses matured prior regular-origin returns, seven contexts pooled equally 1/7, mean20/RMS60 with 19/20 and 57/60 coverage. No current or immature future outcome enters M2.
- Thirteen unbounded channels use native pooled median/unscaled MAD, then IQR/1.349, population SD, or constant scale 1 if necessary. Native nonfinite values receive the fitted center; B2/T2/T5 instead receive neutral zero and identity scale. No winsorization, input clipping or per-sequence normalization. B2 outside `1+1e-10` in absolute value is missing, not clipped. Masks stay outside the tensor.
- Feature fallback does not repair a deficient 48-input-close window to admit it. COP's 125-regular-session dependency plus 48-step envelope remains excluded. All fitted statistics are phase-specific, never fitted on validation/OOS. The original P020 2025-refit recipe must not replace S4's earlier annual recipes.

Authority: `hf1m_ft16_math.py:15–63,84–232`, `hf1m_ft16_fit.py:12–76`, `hf20_s4_fit.fit_expanded():13–125`, `hf20_s4_witnesses.py:19–56`, `hf20_s4_data.py:105–157`. See [HF20_FT16_Complete_Feature_Specification.md](HF20_FT16_Complete_Feature_Specification.md) for exact feature-by-feature mathematics.

###### Missing target endpoint prices

Targets require **positive finite genuine prices for all 20 names** at both exact endpoints, plus COP price-basis compatibility. A missing/quarantined endpoint in one stock invalidates the **entire origin's 20-stock label panel**. No target median fill, price proxy, forward/backfill, nearest-time substitution, external daily price or endpoint shift is used. Historical bad/missing endpoints similarly leave scheduled holes in M2, subject to its coverage/fallback rules. Missing intermediate hour/16:00 closes can make decomposition unavailable without invalidating a direct return whose two exact endpoints are genuine. Authority: `hf20_s4_clock.complete_prices():73–77`; `hf20_s4_preflight.py:143–151,219–268`; `hf20_s4_opening.py:145–160`.

##### 4. Samples, splits, maturity, embargo and weights

###### Origin and sequence construction

Candidate regular-session ET clocks are **09:30,10:30,11:30,12:30,13:30,14:30,15:30**, only when strictly before the actual session close. Context IDs are 6 for opening, then 0–5 for the six full-hour ends. From nominal origin t consume **240 actual XNYS trading minutes**, including closing stubs and pausing across overnight/weekend/holiday closures. Normal exits for the seven clocks are respectively 13:30,14:30,15:30 same session, then 10:00,11:00,12:00,13:00 next session. Early closes use the same trading-minute algorithm.

Opening entry is the genuine **09:30 minute open**; other entries and all exits use the genuine close of the minute starting one minute before the endpoint. Issuance is t+2 minutes and label maturity endpoint+2 minutes. Returns start before assumed issuance and are price-only outcomes, not realizable fill returns.

At full-hour origin t, `entry_index` maps to its completed-hour grid row; at opening, it is the previous completed full hour (normally prior session 15:30; early close 12:30). `first_step=entry_index−47`; gather exactly those 48 scheduled chronological full hours. No opening price or unfinished 09:30–10:30 bar enters FT16. M2 uses the forecast context throughout the sequence, with history locked separately at each historical input session's open.

Source admission: every stock has all 48 finite cap5 closes, sufficient daily warmup (`day_index>=125`), ≥360 cumulative genuine hourly closes and no active COP dependency crossing. Other feature deficiencies use their allowed fallback. Final origin `eligible` combines that input mask with complete20 endpoint eligibility and session date ≥2011-04-01. Supervised label validity does not determine the feature-fit input-key population.

Sources: `hf20_s4_clock.py:10–83`, `hf20_s4_preflight.py:57–67,154–212,219–268`, `hf20_s4_witnesses.assemble():35–56`, `hf20_s4_run.source_data():30–45`.

###### Nominal chronological roles

All inner/refit starts are 2011-04-01. Validation is the last six **calendar** months before the OOS year; no random sample split. These date windows are followed by the source/maturity/embargo filters.

| Fold | Inner inclusive stop | Nominal validation | Refit inclusive stop | Nominal OOS |
| --- | --- | --- | --- | --- |
| F21 | 2020-06-30 | 2020-07-01–2020-12-31 | 2020-12-31 | 2021-01-01–2021-12-31 |
| F22 | 2021-06-30 | 2021-07-01–2021-12-31 | 2021-12-31 | 2022-01-01–2022-12-31 |
| F23 | 2022-06-30 | 2022-07-01–2022-12-30 | 2022-12-30 | 2023-01-01–2023-12-31 |
| F24 | 2023-06-30 | 2023-07-01–2023-12-29 | 2023-12-29 | 2024-01-01–2024-12-31 |

For validation, require the **first of its 48 input steps** to have session date strictly after the inner cutoff; for OOS strictly after the refit cutoff. This is a 48-scheduled-step input embargo, not a fixed elapsed-hour or calendar-day gap. All roles also require `label_maturity_utc < local_midnight(cutoff)+1 day−4 hours`. Cutoff is inner stop for inner training, refit stop for validation/refit, and December 31 of OOS year for OOS. Preserve the conservative four-hour cutoff even when the actual endpoint matures earlier. For F23 refit, for example, cutoff uses December 30, not the weekend December 31. Validation must have ≥50 sessions and ≥25 origins in each of seven contexts.

Exact mask implementation: `src/lstm_data/hf20_s4_data.py:32–76`. Exact samples are `S4/Fxx_{inner_train,inner_validation,refit,oos}_indices.csv`; do not recreate membership from the date table alone. S9 inherits these populations unchanged.

###### Actual saved support and admitted date bounds

Bounds below are first/last admitted **origin ET session dates**, not label-exit dates. Counts are saved in `S9/S5_S9_ROLE_COUNTS.csv`, `S4/opening_reaudit_v2/S4_FOLD_ROLE_SLOT_COUNTS.csv`, and each `MAGxx/role_metrics.json`; bounds were read from the saved role indices.

| Fold | Role | Admitted date bounds | Sessions | Origins | Stock rows |
| --- | --- | --- | ---: | ---: | ---: |
| F21 | inner_train | 2011-04-01–2020-06-30 | 2,100 | 11,449 | 228,980 |
| F21 | inner_validation | 2020-07-13–2020-12-30 | 120 | 674 | 13,480 |
| F21 | refit | 2011-04-01–2020-12-30 | 2,227 | 12,171 | 243,420 |
| F21 | oos | 2021-01-13–2021-12-31 | 188 | 955 | 19,100 |
| F22 | inner_train | 2011-04-01–2021-06-29 | 2,331 | 12,716 | 254,320 |
| F22 | inner_validation | 2021-07-22–2021-12-31 | 92 | 457 | 9,140 |
| F22 | refit | 2011-04-01–2021-12-31 | 2,423 | 13,173 | 263,460 |
| F22 | oos | 2022-01-12–2022-12-30 | 210 | 1,180 | 23,600 |
| F23 | inner_train | 2011-04-01–2022-06-30 | 2,547 | 13,896 | 277,920 |
| F23 | inner_validation | 2022-07-13–2022-12-30 | 86 | 453 | 9,060 |
| F23 | refit | 2011-04-01–2022-12-30 | 2,640 | 14,395 | 287,900 |
| F23 | oos | 2023-01-13–2023-12-29 | 187 | 887 | 17,740 |
| F24 | inner_train | 2011-04-01–2023-06-30 | 2,740 | 14,945 | 298,900 |
| F24 | inner_validation | 2023-07-14–2023-12-29 | 87 | 350 | 7,000 |
| F24 | refit | 2011-04-01–2023-12-29 | 2,835 | 15,332 | 306,640 |
| F24 | oos | 2024-01-11–2024-12-31 | 208 | 991 | 19,820 |

Refit can admit boundary observations omitted from embargoed validation; it is not necessarily the union of inner_train and inner_validation.

###### Weighting

For a role with D admitted sessions, n_d admitted origins on session d, and all 20 names, stock-row mass is **`1/(D*n_d*20)`**. Each session has equal total weight, origins equal within session, stocks equal within origin. The same formula fits magnitude scales and GLOBAL/STOCK controls; it is not uniform weighting of every row across the history. `hf20_ranking.origin_weights():39–41`; `hf20_s5s9_metrics.weights():15–16`. Annual report summaries average years equally rather than pooling unequal annual sample sizes.

##### 5. Magnitude target, inversion and three controls

For exact genuine endpoints, let `R=log(P_exit/P_entry)` and `A=abs(R)` in decimal log-return units. In each fold/phase fit

\[
s_A=\max\{Q^{w}_{0.5}(A),10^{-8}\},\qquad m=\log(1+A/s_A).
\]

The pooled weighted median uses the stock-row weights above; sort stably and select the first observed value whose normalized cumulative weight is ≥0.5 (`searchsorted(...,side="left")`), without interpolation. Inner parameters use **inner_train** only; refit parameters use **refit** only. Saved tail/NUM/MAD thresholds are diagnostic cohort definitions, not additional target clipping or loss weights.

A scalar unconstrained head predicts `m_hat`; optimized row loss is `(m_hat−log1p(abs(R)/s_A))²`. R is not cross-sectionally demeaned or divided by MAD for MAG. TG20, epsilon and asinh Z are retained as companion diagnostics but **do not enter the MAG loss**. The FT16 feature named T2 is unrelated to the T2R target transform.

For reporting/inference, retain raw `prediction_m=m_hat` and decode once:

\[
\widehat A=s_A\operatorname{expm1}(\max(\widehat m,0)).
\]

Only the inverse lower-clamps predicted m at zero. There is no upper cap, target winsorization, output ReLU in the model, smearing/Jensen correction, sign reconstruction or portfolio mapping. This estimates transformed magnitude; its inversion is not an unbiased conditional expected absolute return. Sources: `hf20_s5s9.py:60–67,141–175`, `hf1m_ft16_fit.quantile():12–20`, `hf20_s5s9_metrics.decode():29–36`.

###### Exact phase parameters

These are the full saved decimal values from `MAGxx/{inner,refit}_target_recipe.json` and `{inner,refit}_GLOBAL_control.json`.

| Fold | Inner magnitude scale | Refit magnitude scale | Inner GLOBAL m | Refit GLOBAL m |
| --- | ---: | ---: | ---: | ---: |
| F21 | 0.005797117684325846 | 0.0058994931438253 | 0.7807054887617804 | 0.7804020257437488 |
| F22 | 0.0059347355198145265 | 0.005957669984582455 | 0.7800440769243104 | 0.7795002079091725 |
| F23 | 0.0060897938914411046 | 0.006150424755601047 | 0.780037173411231 | 0.779600015468851 |
| F24 | 0.006174065175292481 | 0.0061703009229596 | 0.7786992711980216 | 0.7780814265022555 |

###### Control definitions

**GLOBAL:** fitted weighted mean of m over all training stocks/origins/sessions, broadcast to every evaluation row. **STOCK:** one fitted weighted mean m per stock, averaging origins with session-normalized weights. Both are means in **transformed space**, not mean raw A transformed afterward. Each phase's training coefficients remain fixed for its evaluation roles; all controls use exactly the neural run's eligible keys and phase scale.

**VOL:** parameter-free, `inner_VOL_control.json` and `refit_VOL_control.json` are `{}`. At the last input step decode the actual scaled/imputed float32 V2 channel through its frozen affine recipe:

\[
\sigma=\exp(V2_{scaled}\,s_{V2}+c_{V2}),\qquad
\widehat m_{VOL}=\log(1+2\sqrt{2/\pi}\,\sigma/s_A).
\]

Thus decoded raw magnitude is `2*sqrt(2/pi)*sigma`. Sigma is the **floored RMS60 of hourly open-to-close returns, or its native feature fallback**, as represented in the consumed tensor; do not recompute a new close-to-close or overnight volatility. The multiplier is fixed, with no fitted regression, cross-sectional rho, quantile bins or optimization for MAG. EVENT/QUANTILE control rules in the shared module do not apply.

Authority: `hf20_s5s9.Data.volatility():133–138`; `hf20_s5s9_metrics.fit_control():223–242`, `control_raw():268–273`; `hf20_s5s9_report.finish_run():264–305` explicitly bypasses fitting MAG/VOL.

###### Exact STOCK coefficients (predicted m)

Column I is inner, R is refit; row order is the fixed stock axis. Values are transcribed at saved JSON precision from `MAGxx/{inner,refit}_STOCK_control.json`, key `value`.

| Ticker | F21 I | F21 R | F22 I | F22 R | F23 I | F23 R | F24 I | F24 R |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| VZ | 0.6279239829544796 | 0.6167956218897865 | 0.6111868859978398 | 0.6063645879065321 | 0.6024794237421662 | 0.6046993122653715 | 0.6059534101854324 | 0.6095732038337187 |
| COP | 0.8649228246455933 | 0.8724123331712701 | 0.8774437958724485 | 0.8790176260826301 | 0.8821195316836852 | 0.8833155990178297 | 0.8819279444737617 | 0.8794144093456454 |
| BAC | 0.8509585259857807 | 0.8470046027304942 | 0.844737468828631 | 0.8432745197123446 | 0.8394720347706234 | 0.8360168331262082 | 0.8338673165986042 | 0.832847367223927 |
| BA | 0.7966578398437266 | 0.8086393844849904 | 0.8153904119609365 | 0.8178858106957089 | 0.8281163642465779 | 0.8301363982847985 | 0.8300477165844106 | 0.8272891594421045 |
| AAPL | 0.762259958350848 | 0.7668212840001577 | 0.7659805582226921 | 0.7645625328609627 | 0.7646081352111939 | 0.7659347484636029 | 0.7640595384640354 | 0.7620176374449703 |
| PEP | 0.565912532805736 | 0.5648754603141318 | 0.5659250521473685 | 0.5653923959861803 | 0.5640893187456197 | 0.5625970823939321 | 0.5612584301086677 | 0.561035513490638 |
| MRK | 0.6741091901021926 | 0.6701630347400371 | 0.667412713954337 | 0.668873895831577 | 0.6644209539481736 | 0.6623056013718924 | 0.6615410830249369 | 0.6615497094326539 |
| SBUX | 0.7314813757620817 | 0.7287625934246942 | 0.7284180320590486 | 0.7261141528792093 | 0.7291581860787641 | 0.7293217552223225 | 0.7261484641294293 | 0.723533801072121 |
| CVX | 0.7326044265457307 | 0.7396449233417284 | 0.7416967422315551 | 0.7410215533593928 | 0.7437594466866562 | 0.7443197027187195 | 0.7434080032876285 | 0.7421434290692308 |
| MS | 0.8976736246286194 | 0.8898513329895162 | 0.8866560083235383 | 0.8849190527579411 | 0.8813116625956565 | 0.8766079526679454 | 0.8714132807655216 | 0.868096573895736 |
| AMD | 1.1911804336055587 | 1.1772892041545568 | 1.1670303861878246 | 1.1672819676126576 | 1.1637840329612998 | 1.160878067363297 | 1.1589997956606992 | 1.1594172176638717 |
| KO | 0.570023040151916 | 0.5727389014919869 | 0.5716668398804869 | 0.5706262058399103 | 0.5702301894840448 | 0.5705492777806171 | 0.5674047345594221 | 0.5660014792851307 |
| JNJ | 0.5805823030395609 | 0.5791104007215112 | 0.5772595748116877 | 0.5749511118049682 | 0.572624189050347 | 0.5694789506076492 | 0.5669630970276622 | 0.5679642971461746 |
| AMZN | 0.831234442505602 | 0.8308253448121442 | 0.8273375170467794 | 0.8240723685425374 | 0.8280194274407634 | 0.8332842721975509 | 0.8365133962841659 | 0.8395944352310111 |
| XOM | 0.6831851437157815 | 0.6950894615572155 | 0.7031660567018804 | 0.7075932994665731 | 0.7147017937655964 | 0.717080032403105 | 0.720006334757303 | 0.7216554265287107 |
| WFC | 0.7386934820054066 | 0.7473715869489501 | 0.7523987584500912 | 0.7565053289432724 | 0.7612790087609722 | 0.7606807716835553 | 0.7632459085306618 | 0.7640994163630038 |
| AVGO | 0.920097330904426 | 0.9070145791019004 | 0.9044769678994897 | 0.8978844391551416 | 0.8934294269451727 | 0.8890947107655133 | 0.8867874504318067 | 0.888056011922942 |
| TSLA | 1.1358787529448477 | 1.1412772017239643 | 1.1417226649210317 | 1.1399749670634702 | 1.1409808347983368 | 1.1421804962722573 | 1.1459934731875774 | 1.1466114252491153 |
| MA | 0.7335556318096461 | 0.734229336479566 | 0.7366476156145039 | 0.7407029121166331 | 0.7449162758797422 | 0.7437195827768808 | 0.741231959503208 | 0.7363643441421157 |
| CSCO | 0.7251749329280699 | 0.7181239267963748 | 0.7143274873740106 | 0.7129854295657729 | 0.7112432314292202 | 0.7097991619939825 | 0.707214086395472 | 0.7043636722622822 |

##### 6. Model, optimization, selection and refit

###### Executed hyperparameters and initialization

| Item | Executed setting |
| --- | --- |
| Architecture | Shared unidirectional `nn.LSTM(input_size=16,hidden_size=32,num_layers=1,batch_first=True)`, default biases, no projection; scalar `nn.Linear(32,1)` head |
| Sequence | 48×16 per stock; no stock embedding, peer/market input, persistent hidden/cell state, padding or truncated-state carry |
| Readout/dropout | Last hidden state, `nn.Dropout(0.10)`, then affine head; this is readout dropout, not inter-layer recurrent dropout |
| Parameter count | 6,433: 6,144 LSTM matrix +32 head matrix elements; 256 LSTM bias +1 head bias elements |
| Seed | Exactly 42; Python `random`, NumPy legacy RNG and `torch.manual_seed`; `torch.use_deterministic_algorithms(True)` |
| Initialization | PyTorch 2.10.0 defaults; no custom Xavier/orthogonal/forget-bias override. LSTM parameters uniform ±1/√32; Linear uses `kaiming_uniform_(a=√5)` and uniform bias ±1/√32. Preserve constructor order: LSTM, dropout, head |
| Initial parameter identity | `1e6f1b81ccd0286b5da1eb7c47ffff1702ae8b677f34c2058f7538417bc928bc` for all four runs |
| Device/numerics | CPU float32 model and training inputs/targets; no AMP, GPU/MPS or mixed precision; 4 intra-op threads, 1 inter-op thread |
| Optimizer | AdamW, fixed lr 0.001, betas (0.9,0.999), eps 1e−8, AMSGrad false; no scheduler/warmup |
| Weight decay | 0.01 for all 2-D matrices (including head); 0 for 1-D biases |
| Gradient rule | One global L2 `clip_grad_norm_(...,1.0,error_if_nonfinite=True)` per optimizer step; nonfinite loss/gradient/weights fail closed |
| Batches | 16 complete admitted sessions; all their eligible origins and all 20 stocks; keep final shorter session batch; no accumulation or replacement sampling |
| Epoch policy | Minimum 12 calibration epochs before stopping, maximum 60, patience 10; exact qualifying loss rule below |

Sources: `src/lstm_data/neural_engine.py:18–57,159–171`; `hf20_s5s9.model_for():40–51`; `hf20_s5s9_run.py:224–320,348–378,512–513`; each run's saved configuration. Default initialization was also inspected in the installed `torch==2.10.0` package's `torch/nn/modules/rnn.py:RNNBase.reset_parameters` and `torch/nn/modules/linear.py:Linear.reset_parameters`.

All four refit checkpoint contents have float32 tensors: `lstm.weight_ih_l0[128,16]`, `weight_hh_l0[128,32]`, `bias_ih_l0[128]`, `bias_hh_l0[128]`, `head.weight[1,32]`, `head.bias[1]`. Saved AdamW groups additionally record `maximize=False`, `foreach=None`, `capturable=False`, `differentiable=False`, `fused=None`, `decoupled_weight_decay=True`. Preserve defaults/CPU backend rather than enabling fused/foreach execution independently.

###### Exact epoch order and objective reductions

Group the selected role positions by ET session date, sort dates, then for epoch n shuffle with a **fresh `np.random.default_rng(42+n)`**. Group indices retain original chronological origin order; flatten origin-major then stock-major into `[origins*20,48,16]`. Every batch calls `model.train()`, clears gradients, computes per-stock transformed squared error, averages the 20 stocks, and weights each origin by `1/(number_of_sessions_in_this_batch * origins_on_its_day)`. Sum to one scalar and take one optimizer step. There is no extra full-history scaling of the final short batch's gradient. Phase-specific day lists make refit batches different, but the same epoch-number shuffle seeds are reused. There are no DataLoader workers; the runner directly constructs batches.

After every calibration epoch, `predict()` evaluates the **entire** inner-training and validation roles with dropout off, `torch.inference_mode()`, batches of 32 origins, and unchanged chronological sample order. Selection's `off()` loss recomputes targets from R cast to float32 and reduces stock mean, then full-role session-normalized origin weights. Online training loss is reported separately; it is not the selection statistic.

Saved score exports later recompute row loss in float64 from saved float32 predictions and original float64 R, then aggregate with row weights. Therefore last-digit differences between validation traces and saved diagnostic metrics are expected; do not use exported float64 losses to reconstruct the stopping rule. Sources: `hf20_s5s9_run.predict/off/epoch():189–320`; `hf20_s5s9_metrics.make_frame():173–220`.

###### Selector and actual completed epochs

`objective_screen_run.Selector:40–65` is the imported MAG selector. First finite nonnegative loss qualifies. Later validation L qualifies only when **`L <= 0.999*best_qualified_loss`**; equality qualifies. A qualifying epoch replaces selected epoch/best and resets patience, otherwise patience increments. Independently track the raw numerical minimum. Stop when epoch≥12 and patience≥10, else at epoch 60. The selected epoch can be less than 12 and need not equal the raw minimum. There is no rank-IC selection for MAG.

| Fold | Calibration stop | Selected / refit epochs | Raw-best epoch | Calibration optimizer updates | Refit updates | Saved qualified best validation loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| F21 | 37 | 27 | 30 | 4,884 | 3,780 | 0.27765695714096117 |
| F22 | 30 | 20 | 20 | 4,380 | 3,040 | 0.222935593875287 |
| F23 | 51 | 41 | 41 | 8,160 | 6,765 | 0.25486852119791253 |
| F24 | 37 | 27 | 27 | 6,364 | 4,806 | 0.20448313889638625 |

All stop statuses are `PATIENCE_STOP`. F21 raw-best loss was 0.2775669336205141 at epoch 30, insufficient to replace qualified epoch 27. Counts and losses above are recorded in `MAGxx/calibration_binding.json` and `refit_binding.json`; refit optimizer step counters were inspected in the four saved checkpoints.

###### Refit, checkpoint and inference rules

Each epoch saves `calibration_NNN.pt` containing model `state_dict` only. At calibration stop, `calibration_stop_optimizer.pt` contains the **stop-epoch** optimizer, not selected-epoch optimizer state. Reload selected calibration weights for both inner_train and inner_validation exports.

Then apply the refit FT16 recipe and refit magnitude scale; recreate the seed-42 model at the identical initial parameter hash and a fresh empty AdamW optimizer. Train the **whole admitted refit role** for exactly the selected number of epochs, with no further validation selection or OOS inspection. This is not fine-tuning the selected calibration weights. `refit_final.pt` contains `{model: state_dict, optimizer: optimizer_state_dict}`. Recreate a model, load saved model weights, and export refit/OOS from that final model; historical runner asserts exact prediction equality with checkpoint reload.

For inference use the matching fold's **refit** input recipe, magnitude scale, checkpoint and exact endpoint/source conventions. Set `eval()` and use the scalar head output without target inversion inside the LSTM. Apply the decode formula once afterward. Raw R, TG20 or future endpoint availability are not model input fields. Omitted LSTM h0/c0 are new zeros on every call.

Sources: `hf20_s5s9_run.neural():323–486`, `predict():189–202`, `neural_engine.SharedLSTM.encode():40–54`. The checkpoint serialization does not include full Python/NumPy/Torch RNG states; a bitwise resumed training procedure is not supplied by these files.

###### Saved checkpoint paths and recorded SHA256

Each filename below is under its corresponding `MAGxx/`; hashes are **recorded binding values**, not a fresh hash audit in this task.

| Fold | Selected calibration file | Recorded calibration SHA256 | Recorded `refit_final.pt` SHA256 |
| --- | --- | --- | --- |
| F21 | `calibration_027.pt` | `9b09865ab9e495f29b1cff69b7c4dc11d16949c873fafe88ead79453c66791b0` | `0cd6d35ef59be7ca184680de0489fdcf2d2b24871219594c18f49c1a213971e7` |
| F22 | `calibration_020.pt` | `c4c49eb12b396ad172ece5ac0c0e495380186e72c0b4166ff701a89ee193ccd8` | `2ce9c2f9c9036b9df3885ed2667c6b30bee68fac8e227fdcdc2be3ca274a7412` |
| F23 | `calibration_041.pt` | `5f06f005b7b48e55d6fa8ba307435c83f8cb041b8a32a1d300137323e884457a` | `97be88d97a7a350813f03dadc2fcb95ecefcd0aaee945e30f985a7cd81632b8b` |
| F24 | `calibration_027.pt` | `cc86cf4a7d41408e0e5e46ed8a358d7b1d9e939c7ad0c37332d8ef6c13536c1f` | `3e985c2c2ab3042a5914513c6be34cbc9c2ddc4aaf54ba69fdccd84f8f26c1e8` |

##### 7. Reproduction entry points, artifacts and numerical qualifications

###### Required inputs and saved outputs

To reproduce existing scores using checkpoints, retain these exact artifacts and their recorded identities:

| Required layer | Paths / role |
| --- | --- |
| Source provenance | `A18/complete_acquisition_manifest.json`, `source_revision_manifest.json`, `months/YYYY-MM/*receipt.json`; raw selected minute path `data/raw/hf20_hf1m_long_v1/REV/raw_1m_selected/YYYY-MM.parquet` (REV as above) |
| Authoritative canonical minute QA | `data/processed/hf20_hf1m_long_v1/REV/qa_v2/canonical_observed/YYYY-MM.parquet`; original cap5 proxies/quality are separate `qa_v2/` stores. `qa_v2`, not earlier QA attempts, governs |
| P019B adjustment/exclusion layer | `P019B/adjusted_hourly_manifest.json`, event ledger/pointer, `pre_feature_gate.json`, field-mask manifest; adjusted hours under `data/processed/hf20_hf1m_long_v1_action_qa_v1/ta019b_action_qa_2026-10-22_201224/hourly/` |
| P020 lineage | `configs/hf1m_long_ft16_v1.json`, `P020/model_input_contract.json`, original `train_only_fit_recipes.json`; lineage only where superseded by S4 phase recipes |
| Actual S4 source/targets | `S4/S4_FROZEN_EXPERIMENT_CARD.json`; `S4/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv`, `S4_ORIGIN_SOURCE_ELIGIBILITY.parquet`, `S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet` (all three in that subdirectory). Card-selected source is **opening_reaudit_v2** |
| Actual input fits/populations | Eight `S4/Fxx_{inner,refit}_recipe.json`; sixteen `S4/Fxx_role_indices.csv`; `S9/S4_REUSED_RECIPES.json` |
| MAG target/control/model | Per-run `configuration.json`, two target recipes, six control JSON files, two bindings, selected calibration checkpoint, `refit_final.pt` |
| Existing comparison outputs | Per-run `role_scores.parquet`, `role_metrics.json`, `role_KIND_control_scores.parquet`, `model_and_control_metrics.csv`, `RUN_DIAGNOSTICS.md`; root `S5_S9_ROLE_COUNTS.csv`, `S5_S9_VERIFICATION.json`, `artifact_inventory.csv` |

Actual `Data()` calls `hf20_s4_run.source_data(S4)`, loads the saved source/endpoint stores, rebuilds source components in memory and expands M2; it is not a standalone checkpoint-only inference CLI. This reconstruction was **not invoked here**. Source code: `hf20_s4_run.py:30–45`, `hf20_s4_preflight.py:70–140`, `hf20_s5s9.py:82–115`. The legacy P020 contract is also an inherited metadata dependency (`hf20_s4_data.py:23–30`; `hf20_ranking_data.metadata():52–72`). Private Parquets/checkpoints are intentionally ignored by Git; cloning alone does not supply them.

###### Actual commands and executable boundaries

Historical commands are documented for reproducibility, **not executed by this extraction**:

```bash
# Activated source acquisition/QA; A18 contains its state/identity prerequisites.
.venv/bin/python -B -m lstm_data.hf_minute_long --run --out reports/data_audit/ta018d_hf1m_long_2026-10-22_155547
# Adjusted source and original P020 feature preparation.
.venv/bin/python -B -m lstm_data.hf1m_action_source --out reports/data_audit/ta019b_action_qa_2026-10-22_201224
.venv/bin/python -B -m lstm_data.hf1m_ft16_prepare --out reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122
# Executed S5/S9 untrained preparation and complete live campaign.
.venv/bin/python -m lstm_data.hf20_s5s9_prepare --out reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation/preflight_v2
.venv/bin/python -u -m lstm_data.hf20_s5s9_run --out reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation
```

These are staged entry points, not a complete from-empty-directory recipe. P019B release/masks, original source QA state, S4's approved opening reaudit/fits and evidence bindings must already exist. Their historical creation commands and prerequisites are recorded in `reports/codex_sessions/2026-10-22_184817_ta018d_hf1m_long.md`, `2026-10-22_204909_ta019b_action_qa_release.md`, `2026-10-22_214605_ta020_hf1m_long_ft16_tg20.md`, `2026-10-26_125645_hf20_s1s2_visual_s4a_opening_preflight.md` and `2026-10-26_155600_hf20_s4a_live_final.md`.

The actual neural runner has only `--out`; **no MAG-only `--arm`, `--seed`, `--resume` or fold-selection argument exists**. It executes S5 F21–F24, then MAG F21–F24, then EVENT and QUANTILE. It requires frozen live authority/preflight/code/input bindings and rejects an existing journal or `EXECUTION_STARTED.json` (`hf20_s5s9_run.py:504–527`). Therefore the completed namespace is not restartable and its prior authority is exhausted. **NOT VERIFIED:** a turnkey independent training/inference CLI that bypasses this campaign lifecycle while preserving every rule; none was implemented for this documentation task.

Saved-output report entry points, distinct from training, are `scripts/summarize_s5_s9_saved_outputs.py --out S9` and `scripts/render_s5_s9_complete_views.py --out S9 --reuse-screenshots` (replace alias S9 with its full path). They write reports; they were not run under this read-only request.

###### Environment and bitwise identity

Authoritative setup route: repository `.venv`, `python -m pip install -e '.[dev,neural]'` (README); include `visualization` extra for Plotly reports. `pyproject.toml` requires Python ≥3.11,<3.15; NumPy ≥2.2,<3; pandas ≥2.3,<3.1; PyArrow ≥21,<24; exchange-calendars ≥4.11,<5; requests ≥2.32.5,<3; python-dotenv ≥1.1,<2; neural extra pins **torch==2.10.0**. Report extra pins Plotly 6.3.1 and Streamlit 1.64.0; Streamlit is not the MAG training engine.

Recorded acquisition environment (`A18/runtime_environment.json`): macOS 27.0.1 arm64, Python 3.14.6 / Clang 21, NumPy 2.5.3, pandas 3.0.6, PyArrow 23.0.1, exchange-calendars 4.13.2, requests 2.34.2. The earlier completed S3 session records the same Python/NumPy/pandas/PyArrow plus torch 2.10.0; S9's handoff reports no environment changes. **NOT VERIFIED:** a full package/build/BLAS/backend freeze captured specifically at the S9 live start. Current broad dependency ranges alone cannot guarantee byte-identical recomputation.

Deterministic seeds and CPU execution improve reproducibility but do not certify cross-machine bitwise identity. Differences can arise from CPU/OS/PyTorch kernels or threading, default AdamW dispatch, compiler/math-library builds, NumPy quantile/transcendental and float32 rounding, calendar/tzdata versions, and reordered origin/stock keys. Preserve FP32 training versus FP64 export reductions, batch/inference chunk sizes, constructor/RNG call order and saved source/recipes. Changing batch size changes stochastic training even with seed 42. Serialized file bytes may differ while tensor values agree. No RNG state was checkpointed for arbitrary continuation.

**NOT VERIFIED:** fresh cross-machine reconstruction/checkpoint forward equality, full source hash revalidation or independent lawful access to the private artifacts. This task inspected saved metadata/checkpoint structures only. Existing `refit_binding.json` records `reload_max_error:0` for every fold, and the completed runner required exact reload predictions; those historical checks were not repeated here.

##### 8. Saved-results reconciliation reference

The following are existing **OOS transformed magnitude MSE** values, copied from each `MAGxx/model_and_control_metrics.csv` and neural `oos_metrics.json`; no metrics were recomputed. They provide a compact expected-output reference for the four identified refit models.

| Fold | NEURAL | GLOBAL | STOCK | VOL |
| --- | ---: | ---: | ---: | ---: |
| F21 | 0.22277650031658225 | 0.28464272048962214 | 0.261443862246743 | 0.2599329619784624 |
| F22 | 0.27920023665744426 | 0.38055613654435844 | 0.3487977528967771 | 0.3187140675233866 |
| F23 | 0.20885746933969868 | 0.2549552875755001 | 0.22695279066099444 | 0.24494115063661848 |
| F24 | 0.21898243045736782 | 0.2680606168260498 | 0.24033893466207923 | 0.2494764069720326 |

The saved handoff reports equal-year MAG MSE ≈0.232454 and qualifies the result as magnitude information with raw-magnitude underprediction. These are retrospective exploratory results, not confirmation, signed alpha or transaction-cost-adjusted performance. Source publication/action-vintage and survivor-cohort limitations remain part of exact replication, not details to silently repair.


---

**END — S9-MAG v2 consolidated methodological handoff, 27 October 2026. All existing empirical performance claims remain exploratory; no implementation, retraining, dashboard changes or trading studies were performed by this documentation revision.**
