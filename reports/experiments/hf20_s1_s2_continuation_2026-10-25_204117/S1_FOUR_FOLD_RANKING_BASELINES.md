# S1_FOUR_FOLD_RANKING_BASELINES

Retrospective OOS. LP DEFERRED_AFTER_PRIOR_FAILURE; constants undefined.

| year | model | daily_ic | pair_concordance | normalized_rank_mse | defined_origin_fraction |
| --- | --- | --- | --- | --- | --- |
| 2021 | LR | 0.0215872 | 0.5081673 | 0.7209306 | 1 |
| 2021 | N0 | nan | 0.5 | 0.3684163 | 0 |
| 2021 | N1 | 0.01910849 | 0.5079405 | 0.7227162 | 1 |
| 2021 | N2 | -0.01910849 | 0.4920595 | 0.7508741 | 1 |
| 2021 | P | -0.02827002 | 0.4910265 | 0.7576678 | 1 |
| 2022 | LR | -0.002914377 | 0.49776 | 0.7389872 | 1 |
| 2022 | N0 | nan | 0.5 | 0.3684183 | 0 |
| 2022 | N1 | 0.002619969 | 0.5011421 | 0.7335043 | 1 |
| 2022 | N2 | -0.002619969 | 0.4988579 | 0.736894 | 1 |
| 2022 | P | -0.007668944 | 0.4963175 | 0.7424901 | 1 |
| 2023 | LR | 0.01286957 | 0.504155 | 0.7273586 | 1 |
| 2023 | N0 | nan | 0.5 | 0.3684202 | 0 |
| 2023 | N1 | 0.01673101 | 0.5060285 | 0.7242004 | 1 |
| 2023 | N2 | -0.01673101 | 0.4939715 | 0.7489636 | 1 |
| 2023 | P | 0.01836232 | 0.5071697 | 0.7233114 | 1 |
| 2024 | LR | -0.007372565 | 0.4980502 | 0.742273 | 1 |
| 2024 | N0 | nan | 0.5 | 0.3684195 | 0 |
| 2024 | N1 | 0.00844253 | 0.5038594 | 0.7305098 | 1 |
| 2024 | N2 | -0.00844253 | 0.4961406 | 0.7429438 | 1 |
| 2024 | P | 0.02011702 | 0.5071512 | 0.7220169 | 1 |

## Fit accounting, exact reuse and interpretation

The original8 attempts remain7 successes plus failed LP#8. This continuation made29 new P/LR attempts, all completed: cumulative37 baseline attempts,36 successful P/LR fits plus1 failed LP, no refunds/repeats. F21's static profile and all six accepted ridge candidates, selected lambda.01, original inner predictions and original2020-06-30 recipe are hash-reused. Original eight-attempt journal is immutable. F21's two full-prefix fits and all27 F22–F24 P/LR fits are new, separately logged. Seven same-formula prefix recipes are new; one is reused.

| fold | selected_lambda | inner_selection_IC | F21_reused |
| --- | --- | --- | --- |
| F21 | 0.01 | 0.03894013 | True |
| F22 | 0.001 | 0.01343736 | False |
| F23 | 0.0001 | 0.001847365 | False |
| F24 | 1 | 0.02566552 | False |

All selection ICs above are inner, selection-influenced quantities, not OOS gains. Four-year primary IC: M1+0.01172550, LR+0.00604246, P+0.00063509, reversal−0.01172550; N0 undefined. M1 is positive in all four years, but these small retrospective point estimates do not establish economically useful alpha or significance. LR is positive in2021/2023 and negative in2022/2024. Static P is negative in2021/2022 and positive in2023/2024, so a fixed security profile is not stable evidence of dynamic prediction.

LR gets all768 FT16 lag covariates, with no ticker IDs, same source/scalers/clock/populations as the LSTMs. P is a fitted stock-identity reference; M1/reversal use less information. They are not full-information architecture controls. LP remains DEFERRED_AFTER_PRIOR_FAILURE with no retrial/substitute/zero-IC placeholder. Missing LP limits a clean same-loss linear-versus-PW architecture interpretation.

See PRIMARY_RESULTS.md, baseline_continuation_events.jsonl, STAGE_B_HANDOFF.json, ACCEPTED_BASELINE_PRESERVATION.json, and original per-fold selection/coefficient/role diagnostic files. The diagnostic file index enumerates them all.
