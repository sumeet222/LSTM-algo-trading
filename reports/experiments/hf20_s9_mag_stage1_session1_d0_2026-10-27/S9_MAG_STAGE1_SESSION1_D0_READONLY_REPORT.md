# S9 MAG Stage 1 / Session 1 — D0 read-only report

Prepared 27 October 2026. **Status: PARTIAL (all feasible saved-score D0 computations complete; missing menu and independent calibration history remain explicit limitations).** No fitting or inference was performed. F21–F24 forecasts are historically out of fit within fold, but all new analysis is post-search exploratory. Sections below separate archive reproduction from descriptive and retrospective cohorts.

## 1. Executive result

1. **Historical results reproduced:** 80,260 rows, 4,013 origins, 793 sessions; correct tensor order, refit scales and hierarchical weights. Equal-year MAG transformed MSE 0.232454 and raw MAE 0.006505 match saved controls/reports.
2. **Broad underprediction:** mean Ahat 0.008361 vs A 0.010313, ratio 0.811 (18.9% shortfall). Bias is negative in 4/4 years, 48/48 months, 80/80 stock-years, 28/28 clock-years and all forecast deciles.
3. **Uneven severity:** overnight-crossing ratio 0.765 vs intraday 0.907; 15:30 ratio 0.694. This is not just one extreme forecast bin or one bad year.
4. **Tails dominate mean shortfall:** prefix-95 exceedances have 5.87% weight mass and 24.08% of transformed loss; predicted/realized mean is 0.294. Their unconditional signed-error contribution accounts for 92.2% of net mean underprediction. Ordinary-period mean ratio is 0.981.
5. **Ordering survives level failure:** within-origin magnitude Spearman 0.326608 (STOCK 0.300056, VOL 0.296950); historical all-row association 0.408184 is a different statistic. A large move can rank high yet be far too small in predicted level.
6. **F21 chronology is the constraint:** pre-2021 inner-validation pairs exist, but selected the epoch and use a different encoder/scale from the full refit. No selector-independent pre-F21 forecast bank was located in these saved S9 exports. A rigorous four-fold C1 result is not ready from existing artifacts alone.

**Recommended next discussion:** if F21 must be included, will the researcher choose strategy A with a truly reserved calibration tail and matched restricted-history uncalibrated comparator, accepting separately authorized encoder work? An artifact-only strategy C pilot would instead require explicit acceptance of selector reuse and refit-transfer limits. No choice or improvement is frozen here.

## 2. Source and metric reproduction

S9 root `S9 = reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation`; S4 root `S4 = reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation`. These aliases below are repository-relative. The four runs are `HF20-S9-F21-H4-MAG-S42`, `HF20-S9-F22-H4-MAG-S42`, `HF20-S9-F23-H4-MAG-S42`, `HF20-S9-F24-H4-MAG-S42` under S9.

Each run supplies `oos_scores.parquet`, `oos_STOCK_control_scores.parquet`, `oos_VOL_control_scores.parquet`, `configuration.json`, `inner_target_recipe.json`, `refit_target_recipe.json`, `calibration_binding.json`, `refit_binding.json`, and `refit_STOCK_control.json`/`refit_VOL_control.json`. Actual member/endpoint records: `S4/F{21,22,23,24}_{inner_train,inner_validation,refit,oos}_indices.csv`. Feature recipes: `S4/Fxx_{inner,refit}_recipe.json`, bound in `S9/S4_REUSED_RECIPES.json`. Saved controls bind the exact canonical neural score file. Checkpoints were not opened or run; their saved binding IDs were checked against score metadata.

Tensor order preserved exactly: `VZ COP BAC BA AAPL PEP MRK SBUX CVX MS AMD KO JNJ AMZN XOM WFC AVGO TSLA MA CSCO`. Every admitted origin has exactly these 20 stocks in this order. Zero duplicate, missing or mismatched keys. Four-fold total **80,260 rows / 4,013 origins / 793 sessions**. No dropping or imputation.

| year | rows | origins | sessions | inner_scale | refit_scale | abs_r95 | abs_r99 | decode_max_error | negative_outputs | min_Mhat | max_Mhat |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 19100 | 955 | 188 | 0.0057971176843258461 | 0.0058994931438253002 | 0.029390 | 0.055894 | 0.000000 | 0 | 0.280733 | 1.713990 |
| 2022 | 23600 | 1180 | 210 | 0.0059347355198145265 | 0.0059576699845824551 | 0.029493 | 0.055005 | 0.000000 | 0 | 0.329084 | 2.077727 |
| 2023 | 17740 | 887 | 187 | 0.0060897938914411046 | 0.0061504247556010468 | 0.030580 | 0.056214 | 0.000000 | 0 | 0.298317 | 1.738142 |
| 2024 | 19820 | 991 | 208 | 0.0061740651752924813 | 0.0061703009229596003 | 0.030383 | 0.055878 | 0.000000 | 0 | 0.286137 | 1.807235 |

Executed `A=abs(return_4h)`; original `M=log1p(A/refit_scale)` reconstructed in float64 from saved labels. `prediction_m == raw_0`; saved `prediction_A` equals freshly recomputed `refit_scale*expm1(max(raw_0,0))`. Loss reconstruction uses **unclamped** `raw_0`. Nonfinite numeric fields: zero. Negative outputs/clamped-to-zero forecasts: zero in every fold. No inner-scale substitution or double inverse. Cached forecasts remain the evaluated forecasts; only arithmetic identities were recomputed.

All S4 origin IDs, dates, slots, endpoint and maturity timestamps agree in order; saved `trading_minutes=240`. Issuance is origin+2 minutes and maturity endpoint+2 minutes. Last input end is at/before origin. These checks do not independently reconstruct the exchange calendar or certify historical publication. The closing stub is not treated as an input hour. Original price-only target begins before approximate issuance and is not verified executable return.

Weights: `w=1/(D*n_day*20)` within year; equal four-year mean. All saved row weights match. For descriptive subsets, condition original role weights on group membership **within each year**, then give represented years equal weight. No naive equal-row pooling. This differs from the legacy `strata()` helper's rebalancing of members after filtering; archive full-population metrics are unaffected. Cohort masses/loss shares retain unconditional role weights, averaged over years.

Annual/equal-year transformed-target MSE (dimensionless squared log1p units; original out-of-fit saved population):

| year | MAG | STOCK | VOL | MAG-STOCK | MAG-VOL |
| --- | --- | --- | --- | --- | --- |
| 2021 | 0.222777 | 0.261444 | 0.259933 | -0.038667 | -0.037156 |
| 2022 | 0.279200 | 0.348798 | 0.318714 | -0.069598 | -0.039514 |
| 2023 | 0.208857 | 0.226953 | 0.244941 | -0.018095 | -0.036084 |
| 2024 | 0.218982 | 0.240339 | 0.249476 | -0.021357 | -0.030494 |
| EQ | 0.232454 | 0.269383 | 0.268266 | -0.036929 | -0.035812 |

Raw errors use absolute log-return units (MAE/means) or their squares (MSE). 0.01 magnitude is approximately 1% for small moves. Annual/equal-year original forecasts:

| year | model | observed | predicted | raw_MAE | raw_MSE |
| --- | --- | --- | --- | --- | --- |
| 2021 | MAG | 0.009800 | 0.007626 | 0.006094 | 0.000089 |
| 2021 | STOCK | 0.009800 | 0.007153 | 0.006528 | 0.000103 |
| 2021 | VOL | 0.009800 | 0.008711 | 0.006601 | 0.000095 |
| 2022 | MAG | 0.012951 | 0.010628 | 0.008071 | 0.000154 |
| 2022 | STOCK | 0.012951 | 0.007208 | 0.008736 | 0.000202 |
| 2022 | VOL | 0.012951 | 0.011410 | 0.008598 | 0.000165 |
| 2023 | MAG | 0.009252 | 0.007460 | 0.005825 | 0.000091 |
| 2023 | STOCK | 0.009252 | 0.007442 | 0.006048 | 0.000097 |
| 2023 | VOL | 0.009252 | 0.008362 | 0.006327 | 0.000100 |
| 2024 | MAG | 0.009249 | 0.007731 | 0.006029 | 0.000116 |
| 2024 | STOCK | 0.009249 | 0.007446 | 0.006301 | 0.000126 |
| 2024 | VOL | 0.009249 | 0.008370 | 0.006443 | 0.000122 |
| EQ | MAG | 0.010313 | 0.008361 | 0.006505 | 0.000113 |
| EQ | STOCK | 0.010313 | 0.007312 | 0.006903 | 0.000132 |
| EQ | VOL | 0.010313 | 0.009213 | 0.006992 | 0.000121 |

**MATCH:** every annual MAG/STOCK/VOL transformed MSE, MAE, squared saved RMSE and historical all-row rank statistic agrees with `S9/S5_S9_MODEL_METRICS.csv` at atol=1e-12, rtol=1e-11. Equal-year archive targets 0.232454/0.269383/0.268266 MSE, 0.006505/0.006903/0.006992 MAE, 0.00836/0.01031 forecast/realized means and 0.408 association match their printed precision. No material metric discrepancy required hand-trace correction. `STOCK` is a prefix mean of M, not raw A; `VOL` is parameter-free `2*sqrt(2/pi)*sigma_proxy`, with saved empty coefficient JSON, not a fitted raw-mean benchmark. A handoff accounting qualification conflates parameter-free MAG VOL outputs with the 64 charged fits: the actual `BASELINE_ATTEMPTS.jsonl` has 16 MAG, 24 EVENT and 24 QUANTILE starts, with zero MAG/VOL starts. Thus 64 historical fitted controls plus eight additional phase-specific parameter-free MAG VOL outputs is the correct distinction. No ledger entry was changed.

**Minor handoff rounding MISMATCH:** the v2 prose annual table prints F23 MAG MSE 0.208858; the executed CSV and saved scores give 0.20885746933969868, which rounds to 0.208857 at six decimals. The executed-source annex preserves the precise number. This is a prose rounding inconsistency, not a key/scale/loss failure; no historical file was corrected. Archive mean/rank targets above agree at their reported precision. No adjusted values were used to force a match.

## 3. Where raw-magnitude bias lives

Overall/year profile; positive `M_residual=M-Mhat` means transformed underprediction; raw `bias=Ahat-A` uses the opposite sign convention:

| year | observed | predicted | bias | absolute_bias | ratio | raw_MAE | raw_MSE | M_residual | M_residual_sd | M_residual_p95 | M_residual_p99 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 0.009800 | 0.007626 | -0.002174 | 0.002174 | 0.778151 | 0.006094 | 0.000089 | 0.021681 | 0.471494 | 0.835602 | 1.170152 |
| 2022 | 0.012951 | 0.010628 | -0.002324 | 0.002324 | 0.820593 | 0.008071 | 0.000154 | -0.017734 | 0.528096 | 0.863861 | 1.212003 |
| 2023 | 0.009252 | 0.007460 | -0.001792 | 0.001792 | 0.806270 | 0.005825 | 0.000091 | 0.003687 | 0.456994 | 0.789994 | 1.194289 |
| 2024 | 0.009249 | 0.007731 | -0.001518 | 0.001518 | 0.835878 | 0.006029 | 0.000116 | -0.025508 | 0.467260 | 0.774921 | 1.219220 |
| EQ | 0.010313 | 0.008361 | -0.001952 | 0.001952 | 0.810725 | 0.006505 | 0.000113 | -0.004469 | 0.482114 | 0.816999 | 1.199493 |

### Forecast strength

Ten bins from weighted empirical forecast-score deciles, separately within each OOS year and also pooled using equal-year role mass. Identical forecast values stay together; unique cutpoints only. Bins are **descriptive historical score boundaries**, never proposed calibration boundaries. Table shows pooled bins; all annual bins are in the aggregate CSV. Each group's means follow the subset weighting above, so pooled bins are not unweighted averages over rows. No bins have a zero-score point mass.

| group | forecast_min | forecast_max | rows | sessions | predicted | observed | bias | ratio | raw_MAE | raw_MSE | M_residual_sd | M_residual_p99 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.001912 | 0.004209 | 7158 | 705 | 0.003572 | 0.004235 | -0.000663 | 0.843401 | 0.002678 | 0.000015 | 0.315720 | 0.926136 |
| 2 | 0.004209 | 0.005090 | 7480 | 769 | 0.004669 | 0.005512 | -0.000844 | 0.846963 | 0.003420 | 0.000024 | 0.359785 | 0.952398 |
| 3 | 0.005090 | 0.005878 | 7689 | 783 | 0.005489 | 0.006607 | -0.001118 | 0.830792 | 0.004235 | 0.000043 | 0.408220 | 1.107101 |
| 4 | 0.005878 | 0.006656 | 7720 | 787 | 0.006273 | 0.007545 | -0.001272 | 0.831358 | 0.004746 | 0.000052 | 0.428806 | 1.117723 |
| 5 | 0.006656 | 0.007475 | 7852 | 785 | 0.007068 | 0.008621 | -0.001553 | 0.819845 | 0.005485 | 0.000075 | 0.460061 | 1.149937 |
| 6 | 0.007475 | 0.008384 | 8040 | 782 | 0.007921 | 0.009741 | -0.001820 | 0.813136 | 0.006262 | 0.000087 | 0.490405 | 1.214272 |
| 7 | 0.008384 | 0.009453 | 8110 | 785 | 0.008895 | 0.010787 | -0.001892 | 0.824605 | 0.006863 | 0.000098 | 0.506384 | 1.229414 |
| 8 | 0.009453 | 0.011009 | 8421 | 772 | 0.010168 | 0.012502 | -0.002334 | 0.813278 | 0.008003 | 0.000143 | 0.540882 | 1.260013 |
| 9 | 0.011009 | 0.013850 | 8791 | 762 | 0.012244 | 0.015976 | -0.003731 | 0.766439 | 0.009999 | 0.000231 | 0.580074 | 1.391177 |
| 10 | 0.013850 | 0.041622 | 8999 | 741 | 0.016911 | 0.021557 | -0.004646 | 0.784488 | 0.013402 | 0.000367 | 0.637620 | 1.427501 |

### Stock and clock heterogeneity

All 20 stocks, ordered from most negative to least negative equal-year mean bias; counts prevent a best/worst-only view from hiding coverage:

| group | rows | sessions | observed | predicted | bias | ratio | transformed_MSE | raw_MAE | raw_MSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TSLA | 4013 | 793 | 0.020479 | 0.015471 | -0.005008 | 0.755445 | 0.404537 | 0.013021 | 0.000380 |
| AMD | 4013 | 793 | 0.018185 | 0.013981 | -0.004204 | 0.768815 | 0.364262 | 0.011384 | 0.000282 |
| AVGO | 4013 | 793 | 0.012587 | 0.009790 | -0.002797 | 0.777769 | 0.279994 | 0.007884 | 0.000145 |
| BA | 4013 | 793 | 0.012919 | 0.010425 | -0.002494 | 0.806944 | 0.285994 | 0.008156 | 0.000150 |
| AMZN | 4013 | 793 | 0.011961 | 0.009565 | -0.002396 | 0.799653 | 0.267245 | 0.007547 | 0.000152 |
| COP | 4013 | 793 | 0.011928 | 0.009624 | -0.002303 | 0.806888 | 0.255630 | 0.007359 | 0.000113 |
| WFC | 4013 | 793 | 0.010999 | 0.008714 | -0.002285 | 0.792239 | 0.248234 | 0.006898 | 0.000119 |
| MS | 4013 | 793 | 0.010234 | 0.008052 | -0.002181 | 0.786839 | 0.238987 | 0.006446 | 0.000100 |
| XOM | 4013 | 793 | 0.010228 | 0.008184 | -0.002044 | 0.800142 | 0.223561 | 0.006256 | 0.000082 |
| BAC | 4013 | 793 | 0.010149 | 0.008106 | -0.002043 | 0.798705 | 0.244222 | 0.006491 | 0.000093 |
| SBUX | 4013 | 793 | 0.009276 | 0.007436 | -0.001840 | 0.801665 | 0.227262 | 0.006051 | 0.000136 |
| CVX | 4013 | 793 | 0.009296 | 0.007627 | -0.001669 | 0.820497 | 0.211481 | 0.005776 | 0.000074 |
| AAPL | 4013 | 793 | 0.009314 | 0.007795 | -0.001519 | 0.836871 | 0.214432 | 0.005808 | 0.000073 |
| MA | 4013 | 793 | 0.008891 | 0.007424 | -0.001466 | 0.835085 | 0.205984 | 0.005579 | 0.000070 |
| CSCO | 4013 | 793 | 0.007924 | 0.006531 | -0.001393 | 0.824174 | 0.194810 | 0.005059 | 0.000084 |
| MRK | 4013 | 793 | 0.007398 | 0.006470 | -0.000928 | 0.874567 | 0.183157 | 0.004761 | 0.000058 |
| VZ | 4013 | 793 | 0.006993 | 0.006123 | -0.000870 | 0.875617 | 0.181646 | 0.004607 | 0.000055 |
| KO | 4013 | 793 | 0.005673 | 0.005120 | -0.000554 | 0.902435 | 0.127751 | 0.003477 | 0.000024 |
| PEP | 4013 | 793 | 0.006033 | 0.005504 | -0.000529 | 0.912334 | 0.145450 | 0.003801 | 0.000028 |
| JNJ | 4013 | 793 | 0.005800 | 0.005283 | -0.000516 | 0.910945 | 0.144443 | 0.003734 | 0.000031 |

Stock raw mean bias by OOS year (stability check, overlapping groups are not independent replications):

| group | 2021 | 2022 | 2023 | 2024 |
| --- | --- | --- | --- | --- |
| AAPL | -0.001531 | -0.002001 | -0.001324 | -0.001222 |
| AMD | -0.003926 | -0.004410 | -0.005124 | -0.003356 |
| AMZN | -0.001672 | -0.003355 | -0.002988 | -0.001571 |
| AVGO | -0.002173 | -0.002442 | -0.002668 | -0.003906 |
| BA | -0.003330 | -0.003637 | -0.001065 | -0.001944 |
| BAC | -0.002230 | -0.002194 | -0.002307 | -0.001441 |
| COP | -0.002933 | -0.003341 | -0.002021 | -0.000919 |
| CSCO | -0.001703 | -0.001562 | -0.001469 | -0.000839 |
| CVX | -0.001932 | -0.002442 | -0.001382 | -0.000918 |
| JNJ | -0.000911 | -0.000571 | -0.000427 | -0.000157 |
| KO | -0.001010 | -0.001006 | -0.000045 | -0.000153 |
| MA | -0.002714 | -0.002072 | -0.000723 | -0.000356 |
| MRK | -0.001707 | -0.000899 | -0.000643 | -0.000462 |
| MS | -0.002493 | -0.002483 | -0.002094 | -0.001656 |
| PEP | -0.000978 | -0.000562 | -0.000235 | -0.000341 |
| SBUX | -0.002019 | -0.002297 | -0.001005 | -0.002037 |
| TSLA | -0.004454 | -0.005017 | -0.005424 | -0.005138 |
| VZ | -0.000573 | -0.001044 | -0.000911 | -0.000951 |
| WFC | -0.002398 | -0.002438 | -0.002205 | -0.002099 |
| XOM | -0.002799 | -0.002695 | -0.001791 | -0.000892 |

Seven saved origin slots, plus the saved target's INTRADAY/OVERNIGHT category. Later origins retain their actual next-session endpoints; these are not newly constructed overnight labels.

| group | rows | sessions | observed | predicted | bias | ratio | transformed_MSE | raw_MAE | raw_MSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 09:30 | 9900 | 495 | 0.010149 | 0.008990 | -0.001158 | 0.885873 | 0.229160 | 0.006339 | 0.000087 |
| 10:30 | 12200 | 610 | 0.007229 | 0.006545 | -0.000684 | 0.905319 | 0.166644 | 0.004508 | 0.000044 |
| 11:30 | 12920 | 646 | 0.006162 | 0.005647 | -0.000515 | 0.916416 | 0.150071 | 0.003970 | 0.000036 |
| 12:30 | 12000 | 600 | 0.011562 | 0.009122 | -0.002440 | 0.788954 | 0.263876 | 0.007322 | 0.000141 |
| 13:30 | 10800 | 540 | 0.012572 | 0.010001 | -0.002571 | 0.795501 | 0.276394 | 0.007928 | 0.000165 |
| 14:30 | 10940 | 547 | 0.012666 | 0.010157 | -0.002509 | 0.801932 | 0.272813 | 0.007916 | 0.000152 |
| 15:30 | 11500 | 575 | 0.013017 | 0.009035 | -0.003982 | 0.694092 | 0.289849 | 0.008248 | 0.000181 |

| group | 2021 | 2022 | 2023 | 2024 |
| --- | --- | --- | --- | --- |
| 09:30 | -0.001717 | -0.000829 | -0.001125 | -0.000962 |
| 10:30 | -0.000588 | -0.001034 | -0.000720 | -0.000397 |
| 11:30 | -0.000430 | -0.000707 | -0.000725 | -0.000199 |
| 12:30 | -0.002498 | -0.003103 | -0.002198 | -0.001961 |
| 13:30 | -0.002488 | -0.003499 | -0.002146 | -0.002151 |
| 14:30 | -0.003311 | -0.002734 | -0.001949 | -0.002041 |
| 15:30 | -0.004482 | -0.004643 | -0.003790 | -0.003013 |

| group | rows | sessions | observed | predicted | bias | ratio | transformed_MSE | raw_MAE | raw_MSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INTRADAY | 34800 | 757 | 0.007576 | 0.006869 | -0.000707 | 0.906637 | 0.175942 | 0.004771 | 0.000052 |
| OVERNIGHT | 45460 | 771 | 0.012431 | 0.009515 | -0.002916 | 0.765434 | 0.276018 | 0.007845 | 0.000159 |

### Calendar, volatility and source context

All 48 calendar months and 16 quarters are tabulated in `D0_AGGREGATED_DIAGNOSTICS.csv`, with counts/means/ratios/proper MSE/raw MAE/MSE; no favorable period was chosen. Quarter compact view:

| group | rows | sessions | observed | predicted | bias | ratio | transformed_MSE | raw_MAE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021Q1 | 4720 | 45 | 0.011223 | 0.008779 | -0.002444 | 0.782232 | 0.245323 | 0.006899 |
| 2021Q2 | 5240 | 51 | 0.008506 | 0.007098 | -0.001409 | 0.834408 | 0.197112 | 0.005279 |
| 2021Q3 | 3520 | 35 | 0.008615 | 0.006771 | -0.001844 | 0.785973 | 0.205322 | 0.005442 |
| 2021Q4 | 5620 | 57 | 0.010562 | 0.007713 | -0.002849 | 0.730273 | 0.238657 | 0.006587 |
| 2022Q1 | 6400 | 55 | 0.013155 | 0.010655 | -0.002500 | 0.809990 | 0.275690 | 0.008114 |
| 2022Q2 | 7300 | 62 | 0.014668 | 0.011817 | -0.002851 | 0.805606 | 0.308029 | 0.009182 |
| 2022Q3 | 4740 | 45 | 0.011778 | 0.009866 | -0.001912 | 0.837632 | 0.261778 | 0.007306 |
| 2022Q4 | 5160 | 48 | 0.011599 | 0.009774 | -0.001825 | 0.842633 | 0.262319 | 0.007303 |
| 2023Q1 | 3880 | 37 | 0.010161 | 0.008171 | -0.001989 | 0.804210 | 0.222577 | 0.006349 |
| 2023Q2 | 6200 | 55 | 0.009312 | 0.007546 | -0.001766 | 0.810354 | 0.207014 | 0.005837 |
| 2023Q3 | 4360 | 55 | 0.008616 | 0.007069 | -0.001547 | 0.820420 | 0.196331 | 0.005388 |
| 2023Q4 | 3300 | 40 | 0.009206 | 0.007222 | -0.001984 | 0.784483 | 0.215926 | 0.005926 |
| 2024Q1 | 3980 | 47 | 0.008426 | 0.007324 | -0.001102 | 0.869243 | 0.199598 | 0.005469 |
| 2024Q2 | 5200 | 56 | 0.008883 | 0.007451 | -0.001432 | 0.838754 | 0.203924 | 0.005701 |
| 2024Q3 | 6740 | 64 | 0.010356 | 0.008388 | -0.001968 | 0.809947 | 0.243855 | 0.006759 |
| 2024Q4 | 3900 | 41 | 0.008965 | 0.007555 | -0.001409 | 0.842792 | 0.222945 | 0.005981 |

Volatility states 0–3 reuse each fold's **already fitted** EVENT refit `VOL` control's 25/50/75% cuts on log(sigma_proxy); this same construction is documented in the saved S9 summarizer. These are historical training-prefix cuts, not OOS/future-volatility regimes. `sigma_proxy` is decoded/imputed/floored FT16 V2 hourly open-to-close RMS60. Native unsmoothed/unimputed volatility and newly computed realized volatility were not reconstructed.

| group | rows | sessions | observed | predicted | bias | ratio | transformed_MSE | raw_MAE | raw_MSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 9945 | 625 | 0.005990 | 0.004820 | -0.001170 | 0.804634 | 0.150541 | 0.003832 | 0.000041 |
| 1 | 16315 | 772 | 0.007404 | 0.006135 | -0.001269 | 0.828601 | 0.178503 | 0.004685 | 0.000056 |
| 2 | 26492 | 793 | 0.009471 | 0.007730 | -0.001741 | 0.816148 | 0.221612 | 0.005973 | 0.000089 |
| 3 | 27508 | 793 | 0.014769 | 0.011720 | -0.003049 | 0.793541 | 0.313084 | 0.009319 | 0.000207 |

Quality/fallback/terminal-age are already saved, directly keyed retrospective source diagnostics; not asserted observable model inputs. `SOURCE_FLAGGED` means assumed-zero or price-proxy minutes; fallback ANY means at least one feature-fallback cell. Age bins ZERO/LE1/LE2/LE5 use archived cut semantics. No source QA rebuild:

| group | rows | sessions | observed | predicted | bias | ratio | transformed_MSE | raw_MAE | raw_MSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NO_LISTED_SOURCE_FLAG | 42512 | 793 | 0.011504 | 0.009214 | -0.002290 | 0.800917 | 0.251109 | 0.007202 | 0.000133 |
| SOURCE_FLAGGED | 37748 | 793 | 0.009039 | 0.007457 | -0.001583 | 0.824905 | 0.213148 | 0.005764 | 0.000090 |

| group | rows | sessions | observed | predicted | bias | ratio | transformed_MSE | raw_MAE | raw_MSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ANY | 34910 | 793 | 0.010326 | 0.008426 | -0.001900 | 0.816016 | 0.236749 | 0.006535 | 0.000107 |
| NONE | 45350 | 691 | 0.010317 | 0.008307 | -0.002009 | 0.805249 | 0.230100 | 0.006499 | 0.000118 |

| group | rows | sessions | observed | predicted | bias | ratio | transformed_MSE | raw_MAE | raw_MSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LE1 | 6371 | 736 | 0.009804 | 0.007870 | -0.001935 | 0.802679 | 0.230814 | 0.006224 | 0.000116 |
| LE2 | 1608 | 341 | 0.010343 | 0.008189 | -0.002154 | 0.791745 | 0.224463 | 0.006288 | 0.000093 |
| LE5 | 1338 | 184 | 0.011120 | 0.008636 | -0.002484 | 0.776623 | 0.254642 | 0.006950 | 0.000115 |
| ZERO | 70943 | 793 | 0.010351 | 0.008403 | -0.001948 | 0.811836 | 0.232784 | 0.006533 | 0.000113 |

**Stability versus heterogeneity:** all stock-year and clock-year bias signs are negative, as are all 48 months and 16 quarters. This supports a persistent global raw-mean discrepancy. Its absolute scale is larger for TSLA/AMD (equal-year biases −0.005008/−0.004204) than JNJ/PEP (−0.000516/−0.000529), partly reflecting different move sizes. The 15:30 shortfall recurs in each year; all seven slots retain negative annual signs. Source-flagged and unflagged groups both underpredict, as do fallback ANY/NONE and all four prefix-volatility states. Thus the bias is not confined to recorded repairs. Age LE5 has only 184 pooled sessions and lacks one year's group; its EQ uses represented years only. It cannot establish stable age-specific effects. Clock/source/stock/year groups overlap heavily; no independent-replication claim.

Forecast-decile ratios (~0.766–0.847 pooled; ~0.732–0.882 across annual deciles) suggest a broadly multiplicative level discrepancy with larger absolute errors and residual dispersion at high scores. They do not identify one universal factor: clock ratios differ, tail and ordinary cohorts differ sharply, and conditional means do not identify a deployable calibration map. No analytic calibrator slope was estimated.

## 4. Tails, magnitude ordering and Jensen gap

### Tails and false-low forecasts

Saved refit `abs_r95` and `abs_r99` are prefix-weighted empirical raw-A thresholds (first sorted value reaching cumulative mass; no interpolation). Their labels mature before the outer year; exact prefix index maturity was checked. **No stored 90th threshold exists in the inspected target recipes: UNAVAILABLE; no 90th threshold was estimated.** The saved 99th threshold is an additional available check. No OOS outcomes determine a deployable threshold.

Retrospective REALIZED_TOP1/TOP5 and ABS_RAW_ERROR_TOP1/TOP5 use the largest floor(N*pct/100) rows **within each year**, stable saved-row order for exact ties. The archive's ERROR_TOP cohorts instead sort transformed squared loss; these are shown under TRANSFORMED_LOSS_ARCHIVE and must not be confused with raw-error cohorts. Cohort averages condition original role weights within year; masses and transformed-loss shares are unconditional equal-year averages.

| group | rows | sessions | observed | predicted | raw_MAE | raw_MSE | mass | loss_share | weighted_low_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PREFIX95 | 5126 | 690 | 0.044639 | 0.013127 | 0.031515 | 0.001314 | 0.058706 | 0.240843 | 0.163955 |
| ORDINARY_LE_PREFIX95 | 75134 | 793 | 0.008210 | 0.008058 | 0.005011 | 0.000043 | 0.941294 | 0.759157 | 0.520444 |
| PREFIX99 | 839 | 257 | 0.075964 | 0.014615 | 0.061349 | 0.004305 | 0.009352 | 0.075394 | 0.123592 |
| REALIZED_TOP1 | 802 | 264 | 0.074408 | 0.014790 | 0.059617 | 0.004124 | 0.009455 | 0.079880 | 0.117807 |
| REALIZED_TOP5 | 4013 | 673 | 0.046555 | 0.013385 | 0.033169 | 0.001428 | 0.047799 | 0.221717 | 0.150321 |
| ABS_RAW_ERROR_TOP1 | 802 | 271 | 0.073488 | 0.013375 | 0.060114 | 0.004157 | 0.009543 | 0.085988 | 0.174272 |
| ABS_RAW_ERROR_TOP5 | 4013 | 670 | 0.045370 | 0.012137 | 0.033793 | 0.001448 | 0.048143 | 0.243615 | 0.229548 |
| TRANSFORMED_LOSS_ARCHIVE_TOP1 | 802 | 310 | 0.057027 | 0.012219 | 0.052044 | 0.003494 | 0.009761 | 0.094875 | 0.279572 |
| TRANSFORMED_LOSS_ARCHIVE_TOP5 | 4013 | 698 | 0.032039 | 0.011669 | 0.029572 | 0.001268 | 0.048272 | 0.278320 | 0.260631 |

`weighted_low_fraction` is the role-weighted fraction of the indicated cohort whose MAG score is in its origin's bottom half (20-name average rank <=10.5). For PREFIX95 this is the false-low rate; chance under unrelated scores is about 50%, not an event probability. Annual exact numerators/denominators, low rates, counts and loss contributions appear below; ordinary complement is retained.

| year | rows | sessions | low_count | event_count | low_fraction | weighted_low_fraction | mass | loss_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 1062 | 160 | 159.000000 | 1062.000000 | 0.149718 | 0.147725 | 0.053265 | 0.236000 |
| 2022 | 2451 | 201 | 524.000000 | 2451.000000 | 0.213790 | 0.211874 | 0.100012 | 0.282341 |
| 2023 | 682 | 158 | 99.000000 | 682.000000 | 0.145161 | 0.150577 | 0.037839 | 0.215238 |
| 2024 | 931 | 171 | 135.000000 | 931.000000 | 0.145005 | 0.145646 | 0.043706 | 0.229795 |

Five largest raw underpredictions only (retrospective examples, unweighted row values; error=Ahat-A):

| year | session_date_et | slot | ticker | A | prediction_A | error |
| --- | --- | --- | --- | --- | --- | --- |
| 2024 | 2024-08-12 | 13:30 | SBUX | 0.199853 | 0.011147 | -0.188705 |
| 2024 | 2024-04-30 | 15:30 | SBUX | 0.193376 | 0.007190 | -0.186186 |
| 2024 | 2024-08-12 | 15:30 | SBUX | 0.190565 | 0.009764 | -0.180800 |
| 2024 | 2024-04-30 | 13:30 | SBUX | 0.178353 | 0.006935 | -0.171418 |
| 2024 | 2024-10-23 | 15:30 | TSLA | 0.181018 | 0.011377 | -0.169642 |

### Magnitude ranking

The historical ~0.408 is **equal-year mean of annual all-row magnitude rank association**: unweighted pandas midranks across all stock-origin rows of that year, followed by a weighted Pearson correlation of ranks using hierarchical row weights. It mixes stock identity, time and cross-section. It is not a signed-return IC or within-origin IC. Reproduced directly from the implementation `hf20_s5s9_metrics.weighted_rank_association`.

New diagnostic `ic`: within each 20-stock origin Spearman via average ties, then origin mean within session, session mean within year, equal years. Constant scores yield undefined IC and are not converted to zero; `undefined` reports their fraction. Top/bottom-four retrieval uses fractional membership across boundary ties (expected overlap under independent random tie-breaks); chance 0.20. Pair concordance excludes realized tied pairs, assigns predicted ties 0.5, chance 0.50. `ties` is fraction of predicted tied pairs; `constant` is fraction of constant-score origins. All fractions use origin→session→year means.

| year | model | historical_allrow_rank | ic | pair | top4 | bottom4 | ties | constant | undefined |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | MAG | 0.442990 | 0.326127 | 0.618441 | 0.392161 | 0.318642 | 0.000000 | 0.000000 | 0.000000 |
| 2021 | STOCK | 0.262321 | 0.289525 | 0.602727 | 0.338333 | 0.318171 | 0.000000 | 0.000000 | 0.000000 |
| 2021 | VOL | 0.295089 | 0.303205 | 0.610053 | 0.385844 | 0.308777 | 0.000016 | 0.000000 | 0.000000 |
| 2022 | MAG | 0.419301 | 0.350872 | 0.626979 | 0.430774 | 0.322115 | 0.000000 | 0.000000 | 0.000000 |
| 2022 | STOCK | 0.274246 | 0.310564 | 0.611881 | 0.345992 | 0.326134 | 0.000000 | 0.000000 | 0.000000 |
| 2022 | VOL | 0.298321 | 0.320683 | 0.615346 | 0.417194 | 0.308415 | 0.009650 | 0.000000 | 0.000000 |
| 2023 | MAG | 0.390094 | 0.317063 | 0.614072 | 0.421594 | 0.292415 | 0.000000 | 0.000000 | 0.000000 |
| 2023 | STOCK | 0.280489 | 0.303854 | 0.609351 | 0.402034 | 0.300261 | 0.000000 | 0.000000 | 0.000000 |
| 2023 | VOL | 0.271268 | 0.283005 | 0.602058 | 0.388442 | 0.294894 | 0.001689 | 0.000000 | 0.000000 |
| 2024 | MAG | 0.380350 | 0.312368 | 0.612916 | 0.462858 | 0.269697 | 0.000000 | 0.000000 | 0.000000 |
| 2024 | STOCK | 0.269598 | 0.296283 | 0.605940 | 0.432260 | 0.278815 | 0.000000 | 0.000000 | 0.000000 |
| 2024 | VOL | 0.261325 | 0.280906 | 0.599665 | 0.430371 | 0.271337 | 0.001007 | 0.000000 | 0.000000 |
| EQ | MAG | 0.408184 | 0.326608 | 0.618102 | 0.426847 | 0.300717 | 0.000000 | 0.000000 | 0.000000 |
| EQ | STOCK | 0.271664 | 0.300056 | 0.607475 | 0.379655 | 0.305845 | 0.000000 | 0.000000 | 0.000000 |
| EQ | VOL | 0.281501 | 0.296950 | 0.606780 | 0.405463 | 0.295856 | 0.003090 | 0.000000 | 0.000000 |

**Tail interpretation (SUPPORTED descriptively):** prefix95 realized mean 0.044639 vs predicted 0.013127; ordinary complement 0.008210 vs 0.008058. Large moves are usually not assigned bottom-half scores: 917/5,126 such rows are bottom-half (annual weighted false-low mean 16.4%, ranging 14.6–21.2%). That does not constitute reliable jump prediction: many high-ranked events remain severely underpredicted. The whole forecast range is 0.001912–0.041622, while largest misses include realized magnitudes near 0.20. Retrospective top1% realized mean 0.074408 vs forecast 0.014790 further shows compressed amplitude.

Within-origin MAG IC and pair concordance exceed both controls in each year; top4 retrieval averages 42.7% vs 38.0% STOCK and 40.5% VOL. Bottom4 retrieval (30.1%) slightly trails STOCK (30.6%). This is movement-size discrimination, not signed equity ranking. Supported facts are partial ordering and tail-level shortfall; failure to know unanticipated jumps, limited input information, or shrinkage may all contribute. Their causal shares remain unknown.

### Jensen gap and competing explanations

For unconstrained saved Mhat and e=M−Mhat, `A=s*(exp(M)−1)=s*(exp(Mhat)*exp(e)−1)` exactly. If a model were the ideal E[M|X], Jensen implies `s*(exp(E[M|X])−1) <= E[A|X]`. That directional result concerns an ideal conditional mean; it does not identify the source of the entire observed bias. In this population no decode clamp is active.

The annual residual table and forecast-bin residual dispersions/p99 show whether M is centered and how its upper tail varies. Positive raw misses coexist with transformed residuals of either sign; convex inversion can make raw means low even when mean M residual is near zero or negative. We did **not** calculate/deploy a smearing factor, multiply forecasts by residual moments, save adjusted scores, or score a hypothetical correction. `exp(e)` is especially sensitive to rare positive residuals, so OOS residual averages could not serve as honest calibration history.

**SUPPORTED:** raw mean bias is negative every year even though mean M residual changes sign (+0.0217, −0.0177, +0.0037, −0.0255; equal-year −0.00447). Pooled residual SD is 0.4821 and 99th percentile 1.1995; dispersion rises from 0.316 in the lowest forecast bin to 0.638 in the highest. Thus correcting a single M-space signed bias cannot by itself explain the raw mean gap.

**SUGGESTIVE:** transformed/raw functional mismatch and conditional heteroskedasticity are consistent with these facts. Systematic clock differences and annual changes also suggest imperfect conditioning or distribution shift. **UNRESOLVED:** how much each of misspecification, original-scale bias, irreducible event noise, source/clock composition and year shifts causes the gap. Jensen's inequality proves no allocation of historical blame. No OOS oracle factor or corrected forecast performance is reported.

## 5. Chronological calibration and B0 readiness

Saved earlier-prefix inventory (counts/date metadata only for interpretation/recipe verification, no new predictive performance claims on prefixes):

| year | role | rows | origins | sessions | start | stop | last_maturity | selected_epoch | scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | inner_train | 228980 | 11449 | 2100 | 2011-04-01 | 2020-06-30 | 2020-06-30 19:32:00+00:00 | 27 | 0.005797 |
| 2021 | inner_validation | 13480 | 674 | 120 | 2020-07-13 | 2020-12-30 | 2020-12-31 17:02:00+00:00 | 27 | 0.005797 |
| 2021 | refit | 243420 | 12171 | 2227 | 2011-04-01 | 2020-12-30 | 2020-12-31 17:02:00+00:00 | 27 | 0.005899 |
| 2022 | inner_train | 254320 | 12716 | 2331 | 2011-04-01 | 2021-06-29 | 2021-06-30 16:02:00+00:00 | 20 | 0.005935 |
| 2022 | inner_validation | 9140 | 457 | 92 | 2021-07-22 | 2021-12-31 | 2021-12-31 20:32:00+00:00 | 20 | 0.005935 |
| 2022 | refit | 263460 | 13173 | 2423 | 2011-04-01 | 2021-12-31 | 2021-12-31 20:32:00+00:00 | 20 | 0.005958 |
| 2023 | inner_train | 277920 | 13896 | 2547 | 2011-04-01 | 2022-06-30 | 2022-06-30 19:32:00+00:00 | 41 | 0.006090 |
| 2023 | inner_validation | 9060 | 453 | 86 | 2022-07-13 | 2022-12-30 | 2022-12-30 20:32:00+00:00 | 41 | 0.006090 |
| 2023 | refit | 287900 | 14395 | 2640 | 2011-04-01 | 2022-12-30 | 2022-12-30 20:32:00+00:00 | 41 | 0.006150 |
| 2024 | inner_train | 298900 | 14945 | 2740 | 2011-04-01 | 2023-06-30 | 2023-06-30 19:32:00+00:00 | 27 | 0.006174 |
| 2024 | inner_validation | 7000 | 350 | 87 | 2023-07-14 | 2023-12-29 | 2023-12-29 19:32:00+00:00 | 27 | 0.006174 |
| 2024 | refit | 306640 | 15332 | 2835 | 2011-04-01 | 2023-12-29 | 2023-12-29 19:32:00+00:00 | 27 | 0.006170 |

`inner_train_scores` are in sample for the selected calibration encoder. `inner_validation_scores` are out of optimizer training but were evaluated every epoch to select that same checkpoint: they are **not selector-independent calibration data**. `refit_scores` are in sample for the fresh full-prefix encoder. `oos_scores` are held out within the fold. The runner reloads selected calibration weights for inner exports, then resets seed/model/optimizer for a fresh full-prefix refit. Inner/refit scales and feature recipes differ. Saved bindings identify `calibration_{027,020,041,027}.pt` versus `refit_final.pt`; no checkpoint forward pass or new paired population was generated.

| Later evaluation | Earlier saved out-of-fit history | Readiness |
| --- | --- | --- |
| F21 | 2020 inner validation: 674 origins, 120 sessions; selected epoch 27 | C only, exploratory selector reuse/model mismatch. Strict independent bank UNAVAILABLE / NEW FIT REQUIRED. |
| F22 | F21 outer scores (2021), 955 origins/188 sessions | Earlier chronological bank exists; different encoder/refit scale; transfer protocol and shift check required. |
| F23 | F21–F22 outer scores, 2,135 origins/398 sessions | Same caveat; never use F23 outcomes for F23 calibration. |
| F24 | F21–F23 outer scores, 3,022 origins/585 sessions | Same caveat; never use F24 outcomes for F24 calibration. |

Those outer labels mature before the next evaluation year. Earlier OOS pairs can be a sparse annual prequential bank, but they do not supply pre-F21 history or predictions of the newly refitted encoder on genuinely unseen earlier observations. Residuals must use each generating model's own target scale. A raw decode/re-encode under another scale does not establish conditional-mean equivalence or repair encoder distribution shift. All years remain post-search.

| Design | Saved-artifact feasibility | Main scientific trade-off |
| --- | --- | --- |
| A: reserved chronological calibration tail | Not already independent of selection/training in current exports; NEW FIT/FORECAST WORK REQUIRED | Most defensible uniform four-fold design: separate earlier epoch selection from calibration, purge/mature labels, freeze encoder before tail, compare calibrated and uncalibrated versions of that identical restricted-history encoder. Reusing today's selector-exposed tail would not implement this design. |
| B: honest earlier-prefix prequential bank | Limited bank available for F22–F24, absent pre-F21 | Uses more encoder history at evaluation; requires a declared bank window/weight rule and refit-distribution shift check. Full four-fold bank requires new earlier encoder fits. |
| C: archived inner-validation pairs | Present for every fold; no new encoder inference needed for these pairs | Lowest-cost exploratory pilot only: labels also chose epoch, limited recent sessions, different inner/refit scalers and weights. Direct transfer to full refit cannot be presented as validated calibration. |

**Recommendation for discussion:** A is the smallest scientifically clean all-four-fold C1a experiment if a uniform F21 result is required. Begin with one global scalar residual-smearing hypothesis, no stock or clock segmentation, and its matched restricted-history raw comparator. Freeze calendar tail, separate selector period, maturity/embargo, residual units, weights, clamp convention and primary raw-mean MSE/calibration metrics before fitting. Also retain original transformed MSE and raw MAE. If the researcher requires a non-neural-only next session, finish B0 and decide whether C is an explicitly limited exploratory pilot; an honest A-based four-fold C1 claim must wait for separately authorized encoder work.

| Later B0/C1 prerequisite | Saved availability | New calculation/work later |
| --- | --- | --- |
| Prefix raw-mean/median B0 | `return_4h`, weights and exact refit keys already saved in each `refit_scores.parquet`; raw A is abs(R) | New prefix-only baseline fitting, separately authorized; no source rebuild needed. Existing STOCK optimizes M, not raw A. |
| Stock×clock B0 | ticker, slot/category and raw A on same prefix keys | New prefix-only grouped controls and a predeclared sparse-cell policy. |
| Conditional-volatility B0 | `sigma_proxy` is decoded phase FT16 V2; stock/clock keys and phase scalers saved | A limited matched-information control needs no minute rebuild. Additional V1/range/history channels are not in score exports; require separately permitted materialization. |
| Original M | No dedicated M column; exact phase scale + raw A exist | Formula-only transform, not a fit; do not confuse saved Z/TG20 with M. |
| C1 residual pairs | inner validation and earlier outer-year pairs above | Chronology/model-transfer decision before any smearing estimate. In-sample refit pairs cannot substitute for honest residual history. |

Reuse `hf20_s5s9_metrics.decode/metrics`, ranking/weight primitives, `hf20_s5s9_report.verify_frame` mathematics, saved S4 role indices/phase recipes and saved bindings. Do not invoke `Data()` or the completed campaign runner just to analyze saved scores: those paths reconstruct sources or initiate fitting. B0 grouped controls and a separately approved artifact-only C1 pilot could share one later non-neural session after the design decision. Minimum new code is a bounded key/phase reader and permitted prefix-fit/calibration routine with exact weights and matched evaluation; no new framework, source dataset or dashboard is needed. No future runtime promise.

## 6. Decision table — diagnosed patterns are not fitted improvements

The research-menu file is missing, so C1a/b/c/C2 names below are discussion labels from the live instruction, not recovered frozen menu definitions.

| D0 finding | Possible later implication | Evidence quality | Researcher decision |
| --- | --- | --- | --- |
| Broad raw mean gap with near-centered M | Discuss scalar C1a first; no fitted benefit established | SUPPORTED pattern, SUGGESTIVE mechanism | Choose A/B/C chronology and estimand; decide F21 scope. |
| Decile dispersion/ratios vary | Reason to consider score/state-conditional C1b/C1c hypotheses only after scalar control | Exploratory heterogeneity | Recover exact menu definitions and predeclare limited comparison; OOS bins cannot become calibration boundaries. |
| Overnight/15:30 gap recurs | Clock-conditioned hypothesis may deserve later review; first fit stock×clock B0 on past prefixes | SUPPORTED descriptive pattern, causation UNRESOLVED | Whether a conditional map or later C2/objective change is justified after C1a/B0. |
| Tail amplitudes missed despite ranking | C2/later objective question may remain after level calibration | SUPPORTED shortfall; irreducible noise vs misspecification UNRESOLVED | Choose raw mean/median/tail estimand; no automatic new neural objective. |
| STOCK/VOL are limited functional controls | B0 raw mean/median and conditional-volatility controls are needed | Exact executed formulas | Declare information set, prefix weights and comparison metric. |
| F21 independent pairs absent | A or new pre-F21 bank requires new authorized encoder work; C remains qualified exploratory | Exact saved roles and epoch-selection implementation | Do not invent historical forecasts or calibrate on F21 outcomes. |

## 7. Reproduction, integrity and files changed

From the repository root, with the existing declared environment and legally available ignored saved artifacts:

```bash
.venv/bin/python -B reports/experiments/hf20_s9_mag_stage1_session1_d0_2026-10-27/replay_d0.py
```

The helper imports only pathlib/hashlib/json/NumPy/pandas. It never imports a model runner or source loader; no training, fitting, optimization, neural forward pass, score adjustment, data download, minute/FT16 rebuild, trade signal or backtest is present. It reads explicit F21–F24 paths and earlier prefixes; no recursive source loaders or discovery globs. Source hashes are limited to correctness-critical permitted recipes/canonical saved scores and control bindings; no protected content/hash was read. No 2025 numerical analysis. No canonical artifact, configuration, dashboard, ledger or old report was modified.

Scope reference availability: `HF20_S9_MAG_Stage1_Calibration_and_Prediction_Objectives_Research_Menu_v0.1_2026-10-27.md` **not found** in repository filename inventory; no supplied copy beyond the detailed live prompt. The prompt governs D0 and A/B/C definitions; exact C1a/b/c/C2 menu wording must be checked before freezing later work. The S9 v2 and complete-experiment v3 handoffs under `docs/track_a/Consolidation/` were read, with executed-source annexes; existing sources override handoff prose. No external search/install was needed or performed.

Source readers actually used (deduplicated explicit paths; checkpoints and raw sources are deliberately absent):

83 distinct executed-artifact reads, compressed here by the four explicit run/fold IDs above (not a recursive loader):

- S9 root: `S4_REUSED_RECIPES.json`, `S5_S9_MODEL_METRICS.csv`.
- Each MAG run: `configuration.json`, `inner_target_recipe.json`, `refit_target_recipe.json`, `calibration_binding.json`, `refit_binding.json`; the four `inner_train/inner_validation/refit/oos` `_scores.parquet` files; `oos_STOCK_control_scores.parquet`, `oos_VOL_control_scores.parquet`, `refit_STOCK_control.json`, `refit_VOL_control.json`.
- S4: `S4_FROZEN_EXPERIMENT_CARD.json`, eight `Fxx_{inner,refit}_recipe.json`, sixteen `Fxx_{inner_train,inner_validation,refit,oos}_indices.csv`.
- Each `S9/HF20-S9-Fxx-H4-EVENT-S42/refit_VOL_control.json`: cutoffs only. No EVENT prediction population was analyzed.

Read-only interpretation also inspected the two named Consolidation handoffs, newest S5/S9 session reports, final research decision, and executed target/decoder/metric/selection/export code. Existing HTML is referenced by `S9/S5_S9_VISUAL_DIAGNOSTICS.html` without loading or changing it. No bulk source, checkpoint tensors, 2025 or protected 2026 stores were accessed.

Verification: the replay's strict key/order/endpoint/scale/decode/weight/binding/metric assertions passed on all four folds, with 379 aggregate records and 15 ranking records. `ruff check` passed. The full-project basic Pylance-stub parity check completed over 498 Python files with **0 errors / 0 warnings**:

```bash
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
```

The absolute path above is the actual local editor-check tooling location, not a runtime dependency; on another machine select that machine's installed Pylance `dist`. Select repository `.venv/bin/python`, restart Pylance and refresh Problems; the final editor view remains human-confirmed. No pytest suite was invoked because existing tests include fitting paths outside this zero-fit session; the replay's mathematical assertions are the targeted smoke/verification. PyArrow emitted nonfatal sandbox CPU-cache/neon sysctl warnings; all reads and calculations completed. No installation or sandbox escalation was needed. Initial helper float32-inverse/read-only-array bugs and six type diagnostics were corrected; they were not historical score mismatches. Final checked arithmetic uses FP64 decode.

Starting/ending branch `feat/track-a-data-intake`, commit `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42`; fetch succeeded, upstream 0 ahead / 0 behind. Four pre-existing untracked documentation files (shown as three entries by initial short status) remain untouched. No tracked changes, staging, commits, push, pull or merge. This package and the mandatory session report are new, uncommitted files for review.

New output files (read-only **with respect to research sources**, ordinary writable report files):

| File in this namespace | Bytes | Purpose |
| --- | --- | --- |
| S9_MAG_STAGE1_SESSION1_D0_READONLY_REPORT.md | 47564 | Self-contained scientific review |
| replay_d0.py | 62646 | One namespaced descriptive replay helper |
| D0_AGGREGATED_DIAGNOSTICS.csv | 133961 | 379 aggregate rows; all groups/annual bins/cohorts |
| D0_MAGNITUDE_RANKING.csv | 1936 | 15 annual/equal-year predictor summaries |

Mandatory handoff: `reports/codex_sessions/2026-10-27_184041_hf20_s9_mag_d0_readonly.md`. No new figures, prediction Parquets, adjusted forecasts, model artifacts, framework layers or dashboard files. Review the package and handoff before any separate commit; no automatic Git publication was authorized.

Completion: [x] no fitting/inference/trading; [x] 2026 content/hashes closed and no 2025 analysis; [x] saved three-predictor metrics reproduced; [x] feasible D0 dimensions, tails and magnitude ranking complete; [x] no fitted-improvement claim; [x] chronology inventoried with F21 limitation; [x] compact additive package. Missing 90th threshold, independent pre-F21 forecast bank and research menu are explicit. **STOP: no C1/B0 fit, C2 or later objective launched.**
