# HF20 T0–T2: raw versus ex-ante RMS-normalized ranking

**PARTIAL_BLOCKED — retain raw-return ordering as the primary outcome.** The original raw
indicator comparison is complete on all 80,260 rows. The required 20-stock RMS coverage leaves
only 83/4,013 origins (2.07%), with no 2024 support.
Consequently there is **no four-year normalized-target or ridge conclusion**. This is a
coverage failure, not empirical evidence that risk normalization is inferior. No ARCH-N1 work
was launched.

## 1. Frozen design and causal scale

Source: pinned `mito0o852/OHLCV-1m` revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`, using
only authorized saved adjusted hourly derivatives and genuine endpoint returns. Executed S4
directory: `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation`. Its
`opening_reaudit_v2/S4_ORIGIN_SOURCE_ELIGIBILITY.parquet`,
`S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet`, `F21–F24_*_indices.csv`, and eight
`*_recipe.json` files are the actual bindings; exact IDs/hashes are in REPRODUCIBILITY.json.
The S9 `S4_REUSED_RECIPES.json` independently authenticates the same recipes. No reconstructed
calendar split or substitute indicator was used.

The tensor order remains
VZ,COP,BAC,BA,AAPL,PEP,MRK,SBUX,CVX,MS,AMD,KO,JNJ,AMZN,XOM,WFC,AVGO,TSLA,MA,CSCO. Original
annual rows are 19,100/23,600/17,740/19,820 (955/1,180/887/991 origins),793 sessions total. R
is the signed genuine 240-scheduled-XNYS-minute endpoint log return. Nominal entry precedes the
assumed issuance by approximately 2 minutes; actual vendor arrival is unmeasured. Calendar,
early-close and overnight definitions remain those stored by S4.

**Explicit convention difference:** executed M2 uses the preceding 60 *regular-session
scheduled occurrences*, locked strictly before 09:30 on the historical input session, retaining
unavailable slots as missing. It needs 57 finite outcomes and rejects three consecutive missing
slots. We reuse the physical RMS at the latest actual S4 input step and the forecast clock
context. At 09:30 this inherits the prior input-session lock. This conservative, potentially
stale denominator is not a newly refreshed issue-time volatility forecast. The saved per-stock
floor is the prefix-fitted fifth percentile of positive RMS values with equal mass across seven
contexts; inner/refit floors and feature recipes remain phase-specific. Sigma=max(native
RMS,floor); missing RMS is never filled. Z=R/sigma. No scaled V2 or future volatility is used.

Weights are equal stocks within origin, equal eligible origins within session, equal sessions
within year, then equal four annual scores only when all four exist. Rank ties use midranks;
top/bottom membership is fractional at boundary ties. Constant scores have undefined historical
IC; the separately labeled zero convention and its frequency are retained. METRICS.csv includes
annual/category rank, retrieval, pair, tie and output-unit diagnostics.

## 2. Coverage is the decisive limitation

Risk-complete origin counts by saved role:

| year | inner_train | inner_validation | oos | refit |
| --- | --- | --- | --- | --- |
| 2021 | 3663 | 172 | 3 | 3867 |
| 2022 | 3876 | 0 | 56 | 3876 |
| 2023 | 3904 | 28 | 24 | 3932 |
| 2024 | 3964 | 0 | 0 | 3964 |


OOS coverage is 3/955,56/1,180,24/887,0/991. All 78 intraday origins are 11:30; the five
overnight origins are 15:30 in 2022. No 09:30,10:30,12:30,13:30 or 14:30 origin is
risk-complete. The 2021 sample is just January 14,15,19;2023 is January–February. Only 1,660
stock rows and 83 sessions support the target comparison. This is not representative
seven-clock coverage.

Native sigma is unavailable in 88.99% of AVGO OOS rows,48.37% for MA and 36.36% for AMZN
(simple row proportions, not headline weights). One missing stock removes an origin from the
common 20-stock analysis. S4 features retain their original prefix fallbacks, so raw-only
indicators remain evaluable. F22/F24 have zero risk-valid inner-validation origins, blocking
both ridge target variants there. F24 also has no risk-valid OOS origins. No stocks, coverage
rule, source or validation window were changed to rescue these arms.

## 3. T0 — realized ordering differs, on a very narrow sample

| fold | Kendall_tau_b | Spearman | bottom4_changed_fraction | pair_inversion | top4_changed_fraction |
| --- | --- | --- | --- | --- | --- |
| 2021 | 0.8877193 | 0.9679198 | 0.08333333 | 0.05614035 | 0.25 |
| 2022 | 0.8003759 | 0.9140977 | 0.2410714 | 0.09981203 | 0.2098214 |
| 2023 | 0.8342105 | 0.939787 | 0.1354167 | 0.08289474 | 0.1770833 |


For the 83 available origins pooled descriptively (each has its own session; **not an
equal-four-year score**), Spearman is0.9235, Kendall
tau-b0.8133, and9.33% of 190
pairs invert. Top-four membership changes20.18% (0.807
names/origin), bottom-four20.48% (0.819 names/origin).
Raw target pairs have no ties in this sample. In the five overnight cases, inversions are
9.47%, top-four changes 25%, bottom-four 30%; this cannot establish an overnight effect.

Sigma and absolute-target distributions below use annual hierarchical weighted empirical
quantiles; R and sigma are decimal log-return units, Z dimensionless. No common OOS cell hits
its floor. Minimum sigma is 0.004739, so the observed differences are not numerical near-zero
divisions. The largest absolute Z is 5.305; normalized tails remain. Per-stock exploratory
movements include high-risk TSLA/AMD and lower-risk PEP; normalization moves positive low-risk
returns upward and negative low-risk returns downward relative to peers, preserving individual
signs. It is not universally a preference for low-risk stocks. Common TG20 median/MAD
transformation preserves raw ordering; individual sigma division need not.

| fold | variable | p0 | p50 | p99 | p100 |
| --- | --- | --- | --- | --- | --- |
| 2021 | sigma | 0.004740988 | 0.008348524 | 0.01769519 | 0.01769519 |
| 2021 | R | 0.0002626625 | 0.005050799 | 0.03061311 | 0.03061311 |
| 2021 | Z | 0.03206313 | 0.5638669 | 4.111338 | 4.111338 |
| 2022 | sigma | 0.004739183 | 0.01088467 | 0.02619533 | 0.03900063 |
| 2022 | R | 0 | 0.006061543 | 0.04597705 | 0.07078366 |
| 2022 | Z | 0 | 0.5921808 | 3.372761 | 5.305024 |
| 2023 | sigma | 0.004883925 | 0.008785854 | 0.0209805 | 0.02172753 |
| 2023 | R | 0 | 0.005372506 | 0.04241694 | 0.05847811 |
| 2023 | Z | 0 | 0.6248791 | 3.103438 | 5.043224 |


## 4. T1 — distinct indicators, weak evidence of incremental prediction

Original raw population, annual and equal-four-year historical Spearman IC:

| target | model | 2021 | 2022 | 2023 | 2024 | EQ |
| --- | --- | --- | --- | --- | --- | --- |
| R | IND-EQ3 | 0.008550985 | 0.01973816 | 0.01047644 | -0.006384757 | 0.008095209 |
| R | IND-M1 | 0.003829874 | 0.002257178 | 0.0103904 | -0.002945501 | 0.003382987 |
| R | IND-M2 | 0.001912331 | 0.02078108 | -0.0003019258 | -0.007992258 | 0.003599808 |
| R | IND-M4 | 0.01245506 | 0.02346921 | -0.002705332 | -4.234366e-05 | 0.008294148 |


M1 is the executed latest normalized hourly open-to-close movement; M2 is the same-context
historical mean 20/RMS60 indicator; M4 is the executed older daily momentum excluding the
newest approximately 20 sessions. Positive signs are fixed. Each is converted to normalized
ascending cross-sectional midranks; EQ3 is their unweighted mean. Native scaling/fallbacks are
preserved. BASELINE-N1 is M1, not proposed ARCH-N1. Archived M1 scores, keys and R match
exactly, and all four annual IC/retrieval/pair metrics replay within 1e-12; equal-year IC is
0.003382987.

Equal-year retrieval/pair/undefined-IC diagnostics:

| model | IC_zero | bottom4 | pair_concordance | top4 | undefined_IC_rate |
| --- | --- | --- | --- | --- | --- |
| IND-EQ3 | 0.008095209 | 0.201918 | 0.5026072 | 0.2048758 | 0 |
| IND-M1 | 0.003382987 | 0.2029752 | 0.5012538 | 0.2149129 | 0 |
| IND-M2 | 0.004094983 | 0.2061376 | 0.5017918 | 0.2049629 | 0.0340159 |
| IND-M4 | 0.008479237 | 0.2028916 | 0.5030058 | 0.221633 | 0.05634072 |


M2 and M4 have undefined/constant cross-sections at 3.40% and 5.63% under hierarchical
weighting; M1/EQ3 have none. Historical IC excludes undefined origins within each day's defined
support. IC_zero instead assigns them 0; these differ and are not silently interchanged.
Top/bottom chance retrieval is 0.20 and pair chance credit 0.50.

The indicators give substantially different orderings:

| target | model | IC | pair_inversion |
| --- | --- | --- | --- |
| IND-M1 | IND-M2 | 0.009772007 | 0.460552 |
| IND-M1 | IND-M4 | 0.004709075 | 0.4593997 |
| IND-M2 | IND-M4 | -0.02562593 | 0.4604602 |


M1–M2 and M1–M4 rank correlations are only 0.0098/0.0047, but difference alone is not useful
complementarity. EQ3 exceeds M1 IC in three of four years by an equal-year 0.004712,
with descriptive 95% interval [-0.007685, 0.016710].
Its top-four retrieval is lower than M1. Thus the
fixed combination does not establish a reliable incremental advantage.

Matched risk-valid indicators, with identical raw/Z keys within each displayed fold:

| target | model | 2021 | 2022 | 2023 |
| --- | --- | --- | --- | --- |
| R | IND-EQ3 | 0.0966761 | 0.04100859 | -0.05836482 |
| R | IND-M1 | 0.114787 | -0.02089615 | -0.02246225 |
| R | IND-M2 | 0.07819549 | 0.02768528 | 0.0518797 |
| R | IND-M4 | -0.0160401 | 0.05496651 | -0.1387845 |
| Z | IND-EQ3 | 0.07663824 | 0.05857341 | -0.06480967 |
| Z | IND-M1 | 0.04711779 | -0.004568243 | -0.02214628 |
| Z | IND-M2 | 0.05313283 | 0.04124597 | 0.03226817 |
| Z | IND-M4 | 0.03759398 | 0.06899839 | -0.1295113 |


There is no 2024 result or four-year average. Normalized IC changes sign/direction across these
sparse slices; they cannot identify a winning target.

## 5. T2 — valid partial fits, insufficient comparative evidence

Inputs are all 48×16=768 chronological FT16 values, not the 112-column alternative. One pooled
stock-shared model per target includes an unpenalized intercept. Training-only target mean/SD
are inverted back to R or Z units. The objective is weighted mean squared standardized-target
error plus lambda times squared slopes; observation weights sum 1. Penalties were fixed at
0.001,0.1,10 and selected by earlier inner-validation native-target MSE, with exact ties
preferring larger lambda. Full-prefix refits use the same risk-complete origins for R and Z.
F21 selected 10 for both; F23 selected 0.1 for both. Neither feature scales nor penalties use
OOS observations.

Four final target fits and 12 inner target trial solves were executed: R/Z in F21 and F23 only.
F22/F24 were not fitted. IND-RIDGE3 was omitted. R-RISK divides the saved raw forecast by
sigma; Z-RAW multiplies the saved Z forecast by sigma; neither is another fit. Cross-target
ranking matrix:

| target | model | 2021 | 2023 |
| --- | --- | --- | --- |
| R | RIDGE-R | 0.2526316 | -0.03088972 |
| R | RIDGE-R-RISK | 0.2421053 | -0.01973684 |
| R | RIDGE-Z | 0.2531328 | -0.01635338 |
| R | RIDGE-Z-RAW | 0.2300752 | -0.01585213 |
| Z | RIDGE-R | 0.2325815 | -0.03302005 |
| Z | RIDGE-R-RISK | 0.2345865 | -0.03201754 |
| Z | RIDGE-Z | 0.2385965 | -0.01296992 |
| Z | RIDGE-Z-RAW | 0.2185464 | -0.008270677 |


The F21 results use only 3 origins; F23 only 24. RIDGE-R beats M1 raw IC in F21 but not F23.
Direct Z has slightly higher Z IC than R-RISK in both, but F23 both remain negative. This does
not establish consistent ridge superiority or select a target/architecture. Target-unit
diagnostics (MSE in squared log-return units for R and squared standardized units for Z; SD is
the mean within-origin cross-sectional SD):

| fold | target | model | MSE | actual_cross_section_SD | bias | predicted_cross_section_SD |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | R | RIDGE-R | 8.012217e-05 | 0.008341566 | 0.001743978 | 0.0006985576 |
| 2021 | R | RIDGE-Z-RAW | 8.084295e-05 | 0.008341566 | 0.001726796 | 0.0004854927 |
| 2021 | Z | RIDGE-R-RISK | 0.98594 | 0.9416049 | 0.1460621 | 0.07386853 |
| 2021 | Z | RIDGE-Z | 1.000245 | 0.9416049 | 0.1462923 | 0.04195207 |
| 2023 | R | RIDGE-R | 0.000133821 | 0.008115312 | -0.001104801 | 0.001825771 |
| 2023 | R | RIDGE-Z-RAW | 0.0001298058 | 0.008115312 | -0.0009016785 | 0.001488338 |
| 2023 | Z | RIDGE-R-RISK | 1.128981 | 0.707264 | -0.1039142 | 0.2013227 |
| 2023 | Z | RIDGE-Z | 1.061765 | 0.707264 | -0.07888548 | 0.1398974 |


Forecast dispersion is much smaller than realized dispersion. A conditional-mean forecast can
be narrow without being wrongly calibrated; this tiny sample cannot establish calibration.
Z-RAW is a derived diagnostic, not automatically a calibrated raw-return forecast.

Paired IC differences, candidate minus reference; positive favors candidate:

| comparison_population | target | candidate | reference | year | delta | low | high | n_months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| risk_common | R | RIDGE-R | IND-M1 | 2023 | -0.008427471 | -0.0924812 | 0.07562626 | 2 |
| risk_common | Z | RIDGE-Z | IND-M1 | 2023 | 0.009176358 | -0.04360902 | 0.06196174 | 2 |
| risk_common | Z | RIDGE-Z | RIDGE-R-RISK | 2023 | 0.01904762 | 0.005012531 | 0.03308271 | 2 |
| raw_original | R | IND-EQ3 | IND-M1 | EQ | 0.004712222 | -0.007685163 | 0.01670973 | 48 |


The existing 400-draw, seed 22042 whole-calendar-month within-year routine is reused, retaining
whole sessions/cross-sections. F21 has one month, so its degenerate interval is suppressed as
uninformative in PAIRED.csv. F23 has only two months; even the positive direct-Z versus R-RISK
interval is fragile and not selection-adjusted confirmation. All 2021–24 years have been
repeatedly researched. No independent-row inference is reported.

## 6. Decision and minimal next decision

Keep **raw signed-return ordering primary** for the stated equal-dollar long-upper/short-lower
economic question. Dividing each stock by its own sigma changes that economic ordering; it is a
distinct secondary risk-aware question, not an automatic improvement in portfolio returns.
Covariance, exposures, execution and costs remain necessary for any portfolio claim.

The highest-information next design decision is whether ARCH-N1 should learn a **direct
residual rank correction around M1**, with a matched linear correction control, versus a
raw-return prediction objective. This is a hypothesis for researcher discussion, not approval
to train either. The present raw indicators provide a reproducible anchor; the sparse ridge
comparison cannot adjudicate the objectives. Before a full normalized-target comparison, a
researcher must approve a coverage remedy and verify lawful historical validation support. The
minimal remedy is an explicitly approved historical support/validation plan using existing
permitted derivatives; do not silently relax 57/60, impute sigma, drop stocks, shift OOS keys
or choose a penalty from OOS results.

## 7. Correctness, reproduction and stop

| Check | Result |
| --- | --- |
| Exact S4 keys/order | PASS: all 80,260 original rows; risk exclusions explicit; archived M1 parity |
| Causality | PASS: morning/overnight three-history traces, strict lock and endpoint+2 maturity; immature overnight observation excluded |
| Floors/ranks | PASS: positive prefix floors, synthetic low-vol floor hit, sign/tie/TG20 fixture, no nonfinite admitted Z |
| Training isolation | PASS: saved roles, genuine maturity cutoffs,48-completed-step embargo, saved phase recipes; F22/F24 fitting BLOCKED |
| Metrics | PASS: hand origin, unequal-origin day weights, signed pair/tie fixtures; no portfolio results |

Focused tests: 29 passed; Ruff passes. Full installed Pylance/basic analyzes 549 Python files
with zero errors/warnings without changed severity/exclusions. Human editor check: PENDING researcher confirmation for the final549-file task; earlier546-file GARCH confirmation not reused.
Source vintage/vendor provenance, surviving-universe bias, nominal-origin/+2-minute issuance
assumptions and repeated-search limitations remain unresolved.

Operational failures are preserved in execution.log/recovery.log: a diagnostic mistakenly
requested a risk-complete morning origin, then the continuation reached F22's zero-support
gate. F21 saved coefficients were reused byte-for-byte, never refitted. Six F21 trial MSE
values were lost from memory at the first abort; their selected penalties remain in
coefficients and the log. RIDGE_SELECTION.csv labels the missing values explicitly. No solver
failure, penalty retuning or extra neural start occurred. The final completion pass
took 177.7 s with measured peak RSS 1.333 GB;
The initial pass had already used 110.8 s before its diagnostic abort; the first recovery
reached 122.3 s before the zero-validation-support stop. Current compact output is
approximately 3.51 MB. No dependency changes; .venv Python 3.14.6 and existing
NumPy/pandas routines only.

The final arithmetic review corrected EQ3 rounding: summing exact half-integer midranks before
division preserves ties in the declared equal-weight combination. Directly averaging the
float32 rank encodings had broken13,094 exact pair ties through rounding. The old EQ3 column
is retained as a small diagnostic NPZ; only saved-score arithmetic was corrected, with zero
additional model fits. Numerical tables and uncertainty intervals use the corrected scores.

Report-only replay, with **no fitting, feature replay or market reads**:

```sh
.venv/bin/python -B -m lstm_data.hf20_targets report
.venv/bin/python -m pytest tests/test_hf20_targets.py tests/test_hf20_s4_readonly.py -q
.venv/bin/ruff check src/lstm_data/hf20_targets.py
.venv/bin/ruff check src/lstm_data/hf20_targets_report.py tests/test_hf20_targets.py
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-pylance-extension>/dist
```

The report command uses only OOS_SCORES.parquet, CHECKS.json and the four archived M1 metrics;
saved inputs/recipes remain project-relative. Numerical tables replay from saved predictions.
Historical fit/recovery commands are logged but consumed: do not rerun them. A clean-machine
refit would require the authenticated private artifacts and renewed execution authority; no
download is implied.

Created code: `src/lstm_data/hf20_targets.py`, `src/lstm_data/hf20_targets_report.py`; test:
`tests/test_hf20_targets.py`. This experiment contains REPORT.md, METRICS.csv, PAIRED.csv,
small keyed OOS_SCORES.parquet, F21/F23 coefficients, selection/fit tables,
predeclaration/checks and execution/validation logs. Parquet/NPZ are intentionally ignored;
small code/tables/reports are uncommitted. The mandatory session report is under
`reports/codex_sessions/`. No pre-existing file, source, registry or historical experiment was
changed. No Git fetch/commit/push, raw-minute read, download, 2025/2026 market access, neural
inference/training or trading backtest. Live neural ledger remains 186/300; new neural starts
0.

**STOP.** T1 raw analysis is complete; T0 and T2 are partial for the stated coverage reasons.
Further coverage changes, architecture design or neural fitting require explicit researcher
approval.
