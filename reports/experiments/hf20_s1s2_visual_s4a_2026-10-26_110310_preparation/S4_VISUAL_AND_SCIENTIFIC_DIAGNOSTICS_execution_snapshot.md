# S4-A: all-eight-run diagnostic review

Eight numerical/visual payload stage gates passed; final browser QA is separately required.

| run_id | year | role | model | origins | sessions | rows | daily_ic | defined_origin_fraction | defined_ic_sessions | origin_ic | pair_concordance | normalized_rank_mse | top4 | bottom4 | score_sd | pair_tie_rate | actual_objective | score_units | phase | original_TG20_mse | inverse_count | original_common_mse | original_centered_mse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HF20-S4A-F21-H4-NR-S42 | 2021 | oos | NR | 955 | 188 | 19100 | -0.005321352 | 1 | 188 | -0.004280598 | 0.4980865 | 0.7407614 | 0.1998005 | 0.2100557 | 0.02126692 | 0 | 0.3690579 | ordinal score; no return calibration | refit | nan | nan | nan | nan |
| HF20-S4A-F21-H4-T2R-S42 | 2021 | oos | T2R | 955 | 188 | 19100 | 0.01520458 | 1 | 188 | 0.006296306 | 0.5050957 | 0.7256372 | 0.2218592 | 0.2090267 | 0.04662139 | 0 | 1.30277 | asinh TG20 | refit | 3.443372 | 1 | 0.1241695 | 3.319203 |
| HF20-S4A-F22-H4-NR-S42 | 2022 | oos | NR | 1180 | 210 | 23600 | 0.01059864 | 1 | 210 | 0.008660502 | 0.5039601 | 0.7290317 | 0.2274065 | 0.2096173 | 0.02194581 | 0 | 0.3684956 | ordinal score; no return calibration | refit | nan | nan | nan | nan |
| HF20-S4A-F22-H4-T2R-S42 | 2022 | oos | T2R | 1180 | 210 | 23600 | 0.01614774 | 1 | 210 | 0.01462595 | 0.5057282 | 0.7249429 | 0.2443963 | 0.182157 | 0.02952683 | 0 | 1.346568 | asinh TG20 | refit | 3.814034 | 1 | 0.1424568 | 3.671577 |
| HF20-S4A-F23-H4-NR-S42 | 2023 | oos | NR | 887 | 187 | 17740 | 0.009054869 | 1 | 187 | 0.02245382 | 0.5038624 | 0.7301695 | 0.2349758 | 0.1921473 | 0.02093716 | 0 | 0.3689495 | ordinal score; no return calibration | refit | nan | nan | nan | nan |
| HF20-S4A-F23-H4-T2R-S42 | 2023 | oos | T2R | 887 | 187 | 17740 | 0.0041718 | 1 | 187 | 0.005703821 | 0.5007628 | 0.7337672 | 0.2467596 | 0.2128788 | 0.1388507 | 5.629046e-06 | 1.345839 | asinh TG20 | refit | 3.865238 | 1 | 0.1466155 | 3.718622 |
| HF20-S4A-F24-H4-NR-S42 | 2024 | oos | NR | 991 | 208 | 19820 | 0.0009395374 | 1 | 208 | -0.005236506 | 0.501 | 0.7361492 | 0.2057063 | 0.2084936 | 0.02071469 | 0 | 0.3689281 | ordinal score; no return calibration | refit | nan | nan | nan | nan |
| HF20-S4A-F24-H4-T2R-S42 | 2024 | oos | T2R | 991 | 208 | 19820 | -0.01184016 | 1 | 208 | -0.01406181 | 0.4959342 | 0.7455658 | 0.2074548 | 0.2227278 | 0.06905828 | 0 | 1.400496 | asinh TG20 | refit | 4.755932 | 1 | 0.1931254 | 4.562807 |


Equal-year metrics (only complete four-fold arms):

| model | daily_ic | top4 | bottom4 | pair_concordance |
| --- | --- | --- | --- | --- |
| NR | 0.003817924 | 0.2169723 | 0.2050785 | 0.5017273 |
| T2R | 0.00592099 | 0.2301175 | 0.2066976 | 0.5018802 |


[All eight run reports](S4_EIGHT_START_DIAGNOSTIC_INDEX.csv) · [Complete file index](DIAGNOSTIC_FILE_INDEX.csv) · [Interactive dashboard](plots/s4_a_rankings.html).

The matched-baseline table reports identical-key N1/N2/P differences and whole-month descriptive intervals. Archived S2 comparisons use common morning keys with verified returns but different fitting populations; they do not isolate one causal effect. The primary estimate weights sessions equally, then years equally; category-balanced and paired-session contrasts remain secondary. All intervals are exploratory, with shared overnight episodes and uncorrected research search. No trading-profit claim.

The extreme-objective table retains every role and original TG20 event cohort, actual optimized loss, numerator/MAD decomposition and energy identities. Do not compare NR loss magnitudes against T2R loss. See all eight individual reports for checkpoint, gradient, fallback, tail and exact source-provenance files.
