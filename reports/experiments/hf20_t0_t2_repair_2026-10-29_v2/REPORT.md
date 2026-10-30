# HF20 T0/T2 repair — HIST4-SHRINK20-252

Raw: COMPLETED. Normalized: COMPLETED.

**Technical repair completed; no convincing ranking edge.** Raw ridge now uses the entire original population. The new risk proxy covers every saved role and all 4,013 OOS origins, versus the preserved strict-M2 study's 83. Raw ridge equal-year IC is −0.003835. Direct Z slightly improves standardized MSE over raw prediction divided by sigma, but both normalized ranking ICs remain negative. Keep raw economic ordering primary; N1 stays deprioritized. No research neural run or trading work was performed; see the validation-scope warning below.

## Executed method and boundaries

The genuine target is R=log(P_endpoint/P_origin), with endpoint after240 scheduled XNYS minutes. Signed R and sigma use decimal log-return units; Z=R/sigma is dimensionless. These are endpoint returns, not realized path variance. Original seven clocks, genuine endpoints, early closes, source masks, maturity and48-step embargo are unchanged. At09:30 the input ends at the prior completed full hour; the closing half-hour stub is not an extra FT16 step. Nominal entry precedes the assumed origin+2-minute issue: this is not executable P&L or measured vendor arrival.

Original tensor axis: VZ,COP,BAC,BA,AAPL,PEP,MRK,SBUX,CVX,MS,AMD,KO,JNJ,AMZN,XOM,WFC,AVGO,TSLA,MA,CSCO. All48×16 FT16 columns and eight saved phase recipes are reused, including original M2 as supplied to S4. No added features or ticker IDs.

**HIST4-SHRINK20-252 is a new estimator, not modified FT16 M2.** For each stock, use finite genuine returns from the preceding252 regular/full-session dates, strictly excluding current-session and early-close history origins. The252-date interpretation was declared before fitting; every original early-close evaluation origin remains. Historical endpoints can still cross early closes/overnights, using their stored genuine maturities. Require source origin<forecast origin and endpoint+2-minute maturity<=issue. Take last60 valid same-clock and last200 valid all-clock observations, without zero filling or duplicate origins.

With n_all>=30, v=(sum_same(R²)+20*mean_pool(R²))/(n_same+20), sigma=sqrt(max(v,epsilon²)). Reuse the saved per-stock phase-specific M2 floor: a positive physical four-hour RMS fifth percentile fitted only on its original prefix with equal context mass. It is not refitted to the new proxy or OOS values. At n_same=0 the formula uses pooled RMS; n_all<30 stays missing. Overlapping returns and overlap between same/pool samples mean counts are not independent sample sizes or a Bayesian posterior. The pseudocount20 is fixed, not optimized.

The preserved component table has25,457 historical origins, including6,625 with only some stocks' returns valid. It is not limited to fully eligible20-stock panels. Independently supported finite stock returns can enter that stock's history after maturity, even when another stock or FT16 input was unavailable. All finite returns were checked against positive saved genuine endpoint prices. No additional endpoints, raw minutes or market data were reconstructed.

## Full raw ridge and frozen references

| target | model | 2021 | 2022 | 2023 | 2024 | EQ |
| --- | --- | --- | --- | --- | --- | --- |
| R | IND-EQ3 | 0.008550985 | 0.01973816 | 0.01047644 | -0.006384757 | 0.008095209 |
| R | IND-M1 | 0.003829874 | 0.002257178 | 0.0103904 | -0.002945501 | 0.003382987 |
| R | IND-M4 | 0.01245506 | 0.02346921 | -0.002705332 | -4.234366e-05 | 0.008294148 |
| R | RIDGE-R | -0.03393236 | 0.003107587 | 0.006900016 | 0.008586149 | -0.003834651 |
| R | S4-NR | -0.005321352 | 0.01059864 | 0.009054869 | 0.0009395374 | 0.003817924 |
| R | S4-T2R | 0.01520458 | 0.01614774 | 0.0041718 | -0.01184016 | 0.00592099 |


RIDGE-R uses every original inner/refit/validation/OOS key, independently of sigma. The intercept is unpenalized. Training-only response mean/SD are inverted to raw units. The objective is sum of normalized equal-session/origin/stock weighted squared standardized-target errors + lambda*sum(slopes²). Lambda is one of 0.001,0.1,10, chosen by earlier inner-validation native-target MSE; exact ties prefer larger lambda. A fresh full-prefix fit follows. The first-session streamed Gram/RHS builder and ridge solver were reused; no matrix stores or extra search.

| year | target | penalty | train_origins | fit_stop |
| --- | --- | --- | --- | --- |
| 2021 | R | 0.1 | 12171 | 2020-12-31 |
| 2022 | R | 10 | 13173 | 2021-12-31 |
| 2023 | R | 0.001 | 14395 | 2022-12-30 |
| 2024 | R | 10 | 15332 | 2023-12-29 |
| 2021 | Z | 0.1 | 12171 | 2020-12-31 |
| 2022 | Z | 10 | 13173 | 2021-12-31 |
| 2023 | Z | 0.001 | 14395 | 2022-12-30 |
| 2024 | Z | 10 | 15332 | 2023-12-29 |


All eight selected penalties are shown, not an OOS winner. Raw and Z happen to choose the same penalties in each fold. Complete scale coverage means their training and scoring keys also match here; raw fitting would remain full even if risk coverage were lower. Eight final fits and24 validation solves total.

Frozen M1/M4/EQ3 values are reused from the first session; T1 was not rerun. Its M2 equal-year IC remains0.003599808, with undefined origins as previously reported. S4 T2R/NR are saved neural ranking references, with exact keys/labels and all eight annual ICs replayed. Their ordinal/TG20 training targets preserve within-origin R ordering, but their scores are not calibrated raw-return forecasts. Only ranking is compared; this is not an equal-loss architectural ablation.

Raw ridge has positive IC in three years but a large negative2021 result; its equal-year IC is below every displayed reference. Paired intervals below include zero, so point underperformance is not formal evidence of inferiority. There is no consistent or economically established raw ranking skill.

## Coverage before normalized fits

| year | role | original_origins | scale_complete | fraction | n_same_p50 | n_all_p50 | fallback | floor_hit | age_same_p95 | age_all_p95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | inner_train | 11449 | 11449 | 1 | 60 | 200 | 0 | 0.01567386 | 1 | 1 |
| 2021 | inner_validation | 674 | 674 | 1 | 60 | 200 | 0 | 0 | 1 | 1 |
| 2021 | refit | 12171 | 12171 | 1 | 60 | 200 | 0 | 0.01591488 | 1 | 1 |
| 2021 | oos | 955 | 955 | 1 | 60 | 200 | 0 | 0.006649215 | 1 | 1 |
| 2022 | inner_train | 12716 | 12716 | 1 | 60 | 200 | 0 | 0.01645565 | 1 | 1 |
| 2022 | inner_validation | 457 | 457 | 1 | 60 | 200 | 0 | 0.01345733 | 1 | 1 |
| 2022 | refit | 13173 | 13173 | 1 | 60 | 200 | 0 | 0.01664389 | 1 | 1 |
| 2022 | oos | 1180 | 1180 | 1 | 60 | 200 | 0 | 0 | 1 | 1 |
| 2023 | inner_train | 13896 | 13896 | 1 | 60 | 200 | 0 | 0.01717761 | 1 | 1 |
| 2023 | inner_validation | 453 | 453 | 1 | 60 | 200 | 0 | 0 | 1 | 1 |
| 2023 | refit | 14395 | 14395 | 1 | 60 | 200 | 0 | 0.01803057 | 1 | 1 |
| 2023 | oos | 887 | 887 | 1 | 60 | 200 | 0 | 0.001014656 | 1 | 1 |
| 2024 | inner_train | 14945 | 14945 | 1 | 60 | 200 | 0 | 0.01820341 | 1 | 1 |
| 2024 | inner_validation | 350 | 350 | 1 | 60 | 200 | 0 | 0.002571429 | 1 | 1 |
| 2024 | refit | 15332 | 15332 | 1 | 60 | 200 | 0 | 0.01822658 | 1 | 1 |
| 2024 | oos | 991 | 991 | 1 | 60 | 200 | 0 | 0.001816347 | 1 | 1 |


Coverage gate was recorded before normalized fitting/scoring: each year>=90% OOS; independent validation>=50 sessions and>=25 origins per clock, retaining executed S4 adequacy; both categories and all seven OOS clocks represented. All16 roles are100% complete. Every OOS stock has n_same=60 and n_all=200; pure pooled-fallback rate is0%. Pool mass is approximately14.1–14.4% per context. COVERAGE.csv also reports each stock/clock/category, scheduled gaps, floors and ages.

Latest same-clock history is typically one regular session old (95th percentile1); maximum ages by OOS year are5/4/5/6 sessions. The60 same-clock observations span at most83/81/91/89 regular sessions. Pool's latest observation is at most2 sessions old. Hence broad coverage is not dominated by empty-context fallback or very old last observations, but stale/missing intervals and unequal clock behavior remain qualifications. OOS floor-hit cell fractions are0.665%,0%,0.101%,0.182%; these are descriptive cell fractions, distinct from headline session weights.

Morning and15:30 AVGO traces in CHECKS.json list genuine origins/endpoints/maturities and directly replay the formula. An immature prior interval is excluded. No actual n_same=0,n_all>=30 case occurs in these histories; the explicit synthetic fallback fixture uses200 returns of0.01 and no same-clock history, giving pooled RMS0.01 before its floor. The real first-history origin on2010-07-01 has n_all=0 and stays missing. It is warmup, not an evaluation observation. No missing example is invented.

## Raw versus normalized realized ordering

| fold | Kendall_tau_b | Spearman | bottom4_changed_fraction | mean_absolute_rank_move | pair_inversion | top4_changed_fraction |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | 0.8500902 | 0.9453704 | 0.1522796 | 1.191056 | 0.07495341 | 0.1783783 |
| 2022 | 0.8209759 | 0.9245729 | 0.1836933 | 1.387138 | 0.08951044 | 0.1922647 |
| 2023 | 0.843975 | 0.9423161 | 0.1711103 | 1.221095 | 0.07801187 | 0.1711294 |
| 2024 | 0.8445816 | 0.9430734 | 0.1777444 | 1.23196 | 0.07770888 | 0.1969065 |
| EQ | 0.8399057 | 0.9388332 | 0.1712069 | 1.257812 | 0.08004615 | 0.1846697 |


Equal-year normalization reverses8.005% of unordered pairs, changes18.467% of top-four membership (0.739 names/origin) and17.121% of bottom-four (0.685 names). Mean absolute rank movement is1.258 positions. Intraday/overnight inversion rates are8.028%/8.022%; top changes18.350%/18.586%, bottom17.301%/16.993%. These are separate conditional session reducers, not a simple row-weighted decomposition. Raw and normalized orderings are distinct; this does not imply improved equal-dollar selection or portfolio Sharpe. The old83-origin result is only a preserved coverage contrast, not an estimator-selection contest.

## Matched ranking matrix

| target | model | 2021 | 2022 | 2023 | 2024 | EQ |
| --- | --- | --- | --- | --- | --- | --- |
| R | IND-EQ3 | 0.008550985 | 0.01973816 | 0.01047644 | -0.006384757 | 0.008095209 |
| R | IND-M1 | 0.003829874 | 0.002257178 | 0.0103904 | -0.002945501 | 0.003382987 |
| R | IND-M4 | 0.01245506 | 0.02346921 | -0.002705332 | -4.234366e-05 | 0.008294148 |
| R | RIDGE-R | -0.03393236 | 0.003107587 | 0.006900016 | 0.008586149 | -0.003834651 |
| R | RIDGE-R-RISK | -0.0377521 | 0.01079914 | 0.0003894942 | 0.01449642 | -0.003016762 |
| R | RIDGE-Z | -0.03265526 | 0.002693367 | 0.004715723 | 0.01277226 | -0.003118477 |
| R | RIDGE-Z-RAW | -0.02353322 | -0.00727665 | 0.01052903 | 0.005516261 | -0.003691143 |
| Z | IND-EQ3 | 0.007966774 | 0.01421706 | 0.009347388 | -0.001658161 | 0.007468266 |
| Z | IND-M1 | 0.00169317 | -0.002223037 | 0.007891807 | 0.002029376 | 0.002347829 |
| Z | IND-M4 | 0.009812441 | 0.01895643 | -0.003590133 | -0.003119987 | 0.005514687 |
| Z | RIDGE-R | -0.02536812 | -0.002773202 | 0.00546387 | 0.004239558 | -0.004609475 |
| Z | RIDGE-R-RISK | -0.0313124 | 0.007894609 | -0.002806631 | 0.01158595 | -0.003659618 |
| Z | RIDGE-Z | -0.02155007 | 0.0009394439 | 0.003386129 | 0.01153665 | -0.001421963 |
| Z | RIDGE-Z-RAW | -0.01426968 | -0.009909044 | 0.009750736 | 0.004110839 | -0.002579288 |


All cells use the same80,260 rows/4,013 origins/793 sessions. Direct Z versus R-RISK improves normalized IC in2021/2023 but not2022/2024; equal-year gain is 0.002238, interval[−0.004851,0.008681]. Both equal-year ICs remain negative. Z-RAW is only sigma times Z prediction, not a new fit or assumed calibration. No target or calibrator was selected on these OOS comparisons.

## Target-unit MSE

| target | model | 2021 | 2022 | 2023 | 2024 | EQ |
| --- | --- | --- | --- | --- | --- | --- |
| R | RIDGE-R | 0.0002035035 | 0.000351708 | 0.0001947277 | 0.0002196704 | 0.0002424024 |


| target | model | 2021 | 2022 | 2023 | 2024 | EQ |
| --- | --- | --- | --- | --- | --- | --- |
| R | RIDGE-R | 0.0002035035 | 0.000351708 | 0.0001947277 | 0.0002196704 | 0.0002424024 |
| R | RIDGE-Z-RAW | 0.0002025149 | 0.0003521239 | 0.0001920977 | 0.0002196055 | 0.0002415855 |
| Z | RIDGE-R-RISK | 1.00505 | 1.028863 | 1.025227 | 1.183775 | 1.060729 |
| Z | RIDGE-Z | 0.9944871 | 1.028967 | 1.002921 | 1.181755 | 1.052032 |


Raw ridge equal-year MSE exceeds an always-zero return forecast by 0.857% (zero MSE=0.000240341855). Direct Z lowers Z-MSE relative to R-RISK by0.820%, improving three years, but remains above the zero standardized-return forecast. Thus the modest loss improvement does not establish useful positive rank forecasting. Native R errors are decimal log returns/squared log returns; Z errors are dimensionless/squared dimensionless.

| target | model | MSE | MAE | bias | predicted_mean | actual_mean | predicted_cross_section_SD | actual_cross_section_SD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R | RIDGE-R | 0.0002424024 | 0.01038485 | 6.245546e-05 | 0.0003087072 | 0.0002462518 | 0.0009863931 | 0.01172492 |
| R | RIDGE-Z-RAW | 0.0002415855 | 0.01034592 | 3.447325e-05 | 0.000280725 | 0.0002462518 | 0.0008157832 | 0.01172492 |
| Z | RIDGE-R-RISK | 1.060729 | 0.7424789 | 0.0004156652 | 0.01640408 | 0.01598841 | 0.07617918 | 0.7933091 |
| Z | RIDGE-Z | 1.052032 | 0.7381499 | 0.001117004 | 0.01710541 | 0.01598841 | 0.04833286 | 0.7933091 |


Prediction dispersion is much smaller than outcome dispersion; narrow conditional means alone are not a calibration failure. Bias and dispersion are diagnostics, not a new calibration fit. Conditional category results (all other clock/stock coverage diagnostics remain in COVERAGE.csv):

| scope | target | model | IC | MSE | bottom4 | top4 |
| --- | --- | --- | --- | --- | --- | --- |
| INTRADAY | R | RIDGE-R | -0.002259489 | 0.000125104 | 0.2008459 | 0.2284124 |
| INTRADAY | R | RIDGE-R-RISK | -0.003656204 | nan | 0.192027 | 0.1986318 |
| INTRADAY | R | RIDGE-Z | -0.003456876 | nan | 0.2148658 | 0.2055728 |
| INTRADAY | Z | RIDGE-R | -0.003309915 | nan | 0.2055037 | 0.1968465 |
| INTRADAY | Z | RIDGE-R-RISK | -0.005124389 | 0.8280889 | 0.2064828 | 0.1980196 |
| INTRADAY | Z | RIDGE-Z | -0.0006741921 | 0.8151557 | 0.2065208 | 0.1964385 |
| OVERNIGHT | R | RIDGE-R | -0.005848507 | 0.0003310305 | 0.1870888 | 0.2389993 |
| OVERNIGHT | R | RIDGE-R-RISK | -0.003761616 | nan | 0.185855 | 0.2051247 |
| OVERNIGHT | R | RIDGE-Z | -0.005835069 | nan | 0.1954934 | 0.2198089 |
| OVERNIGHT | Z | RIDGE-R | -0.006351594 | nan | 0.2067945 | 0.2023472 |
| OVERNIGHT | Z | RIDGE-R-RISK | -0.003632549 | 1.222821 | 0.2045984 | 0.2108139 |
| OVERNIGHT | Z | RIDGE-Z | -0.004751205 | 1.216917 | 0.2031294 | 0.1999409 |


## Descriptive paired month intervals

| population | target | candidate | reference | metric | year | delta | low | high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| raw_full | R | RIDGE-R | IND-M1 | IC_zero | EQ | -0.007217638 | -0.0268239 | 0.01066864 |
| raw_full | R | RIDGE-R | IND-M4 | IC_zero | EQ | -0.01231389 | -0.03548218 | 0.006225802 |
| raw_full | R | RIDGE-R | IND-EQ3 | IC_zero | EQ | -0.01192986 | -0.03163306 | 0.005946132 |
| raw_full | R | RIDGE-R | S4-T2R | IC_zero | EQ | -0.009755642 | -0.02638805 | 0.006171615 |
| raw_full | R | RIDGE-R | S4-NR | IC_zero | EQ | -0.007652575 | -0.02492764 | 0.007932067 |
| risk_common | Z | RIDGE-Z | RIDGE-R-RISK | IC_zero | EQ | 0.002237655 | -0.004850654 | 0.008680827 |
| risk_common | Z | RIDGE-Z | RIDGE-R-RISK | MSE | EQ | -0.008696452 | -0.01300601 | -0.005985337 |
| risk_common | Z | RIDGE-Z | IND-EQ3 | IC_zero | EQ | -0.008890229 | -0.02739757 | 0.007294396 |


Reuse400 draws, seed22042, whole calendar months within year with sessions/stocks kept together and equal four-year aggregation. Positive delta IC favors candidate; negative delta MSE favors candidate. Paired IC_zero explicitly uses the project's zero convention for undefined constants; headline IC retains the historical defined-origin convention. M4's undefined cases explain its small convention difference. All ridge ICs are defined. Every annual direction is in PAIRED.csv. The Z-MSE interval is below zero, but repeatedly inspected2021–24 results are descriptive, not selection-adjusted confirmation or independent-row significance.

## Decision, checks and reproduction

T0 is operationally repaired on the full panel under this explicitly declared historical proxy. Full raw ridge supplies the missing baseline and shows no convincing rank edge. Direct Z offers a modest standardized-loss improvement, not demonstrated ranking value beyond dividing raw predictions by the same risk. Keep raw economic ordering primary and normalized ordering secondary. Retain these full-population ridge and frozen indicator controls if future architectures are discussed. N1 remains deprioritized; these results do not authorize promotion, new neural training or priority changes.

PASS: exact raw/risk key separation, prefix-only transforms/selection, saved-role embargo/maturity, positive physical floors, synthetic pool/missing/immature cases, unpenalized intercept, hand rank/tie and unequal-day weighting fixtures.32 focused tests pass; Ruff and a basic type check of the three new Python files are used. No whole-project/editor sweep is required by this repair prompt. Source feed/action vintage, survivor universe, assumed two-minute timing, overlapping outcomes and pooled clock composition remain limitations; this is not executable alpha.

WARN: an accidentally broad legacy ranking-test invocation also ran disposable synthetic neural fixtures, outside the intended non-neural validation scope. It returned32 passes and2 failures at the legacy10GB project resource guard; no real-data neural fit/inference or research-ledger entry occurred. The failed legacy checks remain unresolved and were not weakened or retried. The requested repair/read-only suite is reported separately. This validation-scope deviation does not change the saved ridge results, but is retained for researcher review.

Source revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56; predecessor/source/role bindings: PLAN.json and the prior REPRODUCIBILITY.json. The saved S4 eligibility, genuine component table, F21–F24 indices and eight phase recipes remain authoritative. Canonical derivatives were read once for feature replay; no raw-minute scan, market download,2025 research or protected2026 access. Old T0/T1/T2 files are unchanged.

Entry commands (run is consumed; report is fitting-disabled):

```sh
VECLIB_MAXIMUM_THREADS=4 .venv/bin/python -u -B -m lstm_data.hf20_targets_repair run
.venv/bin/python -B -m lstm_data.hf20_targets_repair report
.venv/bin/python -m pytest tests/test_hf20_targets_repair.py tests/test_hf20_targets.py tests/test_hf20_s4_readonly.py -q
```

The report reads saved new scores and frozen references; it does not fit models, replay market features or perform neural inference. R_SCORES stores full raw forecasts; RISK_SCORES scales; Z_SCORES normalized forecasts. Small coefficients and FITS.csv preserve all selected models and trial losses; no training matrices are stored. Reports/tables/code are uncommitted; Parquet/NPZ remain local/ignored.

Numerical execution: 192.2s; peak process RSS 1.064GB. Incremental disk and final checks are recorded in CHECKS.json/session report. No dependency changes. Created two repair modules and one targeted test file; no old code edits. Live neural ledger186/300 unchanged, new starts0. No Git fetch/commit/push. **STOP for researcher review.**
