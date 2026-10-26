# Four-year primary comparison

Equal origin within session, equal sessions within year, then equal weight to2021/22/23/24. PW is incomplete; no three-year mean is substituted. N0 constant-score IC is mathematically undefined.

| model | available_years | daily_ic | pair_concordance | top4 | bottom4 |
| --- | --- | --- | --- | --- | --- |
| LR | 4 | 0.00604246 | 0.5020331 | 0.2014912 | 0.2294104 |
| N0 | 4 | UNDEFINED | 0.5 | 0.2 | 0.2 |
| N1 | 4 | 0.01172550 | 0.5047426 | 0.2189689 | 0.2047768 |
| N2 | 4 | -0.01172550 | 0.4952574 | 0.1951673 | 0.2181753 |
| NR | 4 | 0.00236953 | 0.5001135 | 0.2066117 | 0.2136037 |
| P | 4 | 0.00063509 | 0.5004162 | 0.189473 | 0.21396 |
| PW | 3 | UNAVAILABLE (F21 failed) | nan | nan | nan |
| T2R | 4 | 0.00767329 | 0.5021379 | 0.2225849 | 0.2078916 |

Per-year values and missing-arm status are in S1_FOUR_FOLD_RANKING_BASELINES.md and S2_FOUR_FOLD_LSTM_RANKING_COMPARISON.md. Pairwise concordance/top4/bottom4 are tie-aware diagnostic fractions, not trading returns. N0 normalized-rank error is a degenerate midrank score error, not evidence it can order stocks.
