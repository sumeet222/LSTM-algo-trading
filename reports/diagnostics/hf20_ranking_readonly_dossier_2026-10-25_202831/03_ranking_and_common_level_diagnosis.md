# 03 — Ranking and common-level diagnosis

**PASS exact decomposition and saved-output ranking measures; QUALIFIED evidence for prolonged robustness.**

All findings are descriptive. Inner training/refit are in sample; inner validation is selection-influenced; development is 109 repeatedly inspected sessions, not confirmation. No new model, objective fit, labels, inference or trading.


## The common-level explanation is refuted for the development MSE gain

| model | mse | common | centered | delta_common | delta_centered | daily_ic | concordance | top4 | bottom4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T2_S42 | 3.106560016 | 0.09361007099 | 3.012949945 | 0 | 0 | 0.07555944626 | 0.5279285114 | 0.2591743119 | 0.2763761468 |
| A7 | 3.105712862 | 0.09457237928 | 3.011140482 | 0.0009623082945 | -0.001809462243 | 0.06053632545 | 0.5214361081 | 0.248853211 | 0.252293578 |
| A12 | 3.105433252 | 0.09457771059 | 3.010855541 | 0.0009676396033 | -0.002094403159 | 0.06569613042 | 0.5236829331 | 0.253440367 | 0.2798165138 |


For A7, common-level error worsens+0.0009620 while centered error improves−0.0018092, net−0.0008472. For A12, common-level worsens+0.0009676 and centered improves−0.0020944, net−0.0011268. The improved original MSE is therefore **not** explained by better common-level forecasting. Centered squared-error improvement does not imply better ordering: both candidates have lower IC and pairwise concordance. Full-period refit components differ from development and are in sample.

At every full20-stock origin MSE=(mean(Y)−mean(p))²+mean(((Y−mean(Y))−(p−mean(p)))²); checked at1e−13. TG20 has median0, not necessarily mean0. [origin_ranking_and_decomposition.csv](origin_ranking_and_decomposition.csv) retains per-origin components, signed candidate−T2 deltas, IC, concordance, normalized rank MAE/MSE, retrieval, score SD, ties and score gaps. [component_by_target_cohort.csv](component_by_target_cohort.csv) retains the cross term for top-target subsets: common+centered alone need not equal subset loss, because the cross term cancels only over the complete origin.

`four_role_metrics.csv` also records forecast energy E[p²], alignment E[Yp] and ZERO MSE. Their identity MSE−ZERO=energy−2alignment is independently checked at closeout. No calibration slope/map is fitted in this phase; existing archived calibration diagnostics are descriptive only.

## Ranking conventions

Ascending midranks and Pearson correlation of rank vectors implement Spearman. Constant score vectors have undefined IC; ZERO is not assigned0. For190 unordered pairs, tied predictions receive half-credit against non-tied actual outcomes; actual ties are excluded and the valid count governs each origin. These are190 dependent pairs, not190 dates. Rank errors are divided by19. Top/bottom4 retrieval gives fractional membership to a tie spanning a boundary; this explicit tie rule can differ slightly from earlier deterministic-selection retrieval while preserving exact IC/MSE. Neither convention adds random jitter.

Daily mean first averages admitted origins within each session, then sessions equally. Unweighted origin mean is a separate descriptive quantity, never a substitute for the primary daily measure. `ranking_periods.csv` contains month/year/slot results across all roles. `ranking_quality_stock_strata.csv` contains cross-sectional ticker/quality/state contributions and rank errors; ticker contributions are not stockwise time-series correlations.

## Fixed feature shortlist and time variation

M1, M2, Q1 and V1 were fixed from the feature dictionary before this outcome-association calculation; no combination, fitted coefficient, development threshold or winner is selected. `feature_rank_associations.csv` reports within-origin endpoint feature-midrank versus realized-outcome-midrank associations, by role/year/slot, aggregated by day. Development daily associations are M1+0.004798, M2−0.060475, Q1+0.009959 and V1−0.045062. These are reused-period descriptive associations, not new candidate forecast exports or evidence that reversing M2 is a validated strategy.

No legitimate historical stock-profile fitted score, full-history ridge/rank-linear or nonrecurrent matched control was identified in the current-HF20 result inventory. Such missing controls remain unavailable; none was fitted. Earlier years of refit predictions remain in sample even when sliced by year. Rolling48-step inputs are not rolling model fitting.

The archived P028 own-input-fixed state-shift control and mechanism evidence are reused by reference: [P028_MARKET_STATE_MECHANISM_FALSIFICATION.md](../../../reports/experiments/ta028_market_state_2026-10-24_064442_execution_v1/checkpoint_completion_v2/P028_MARKET_STATE_MECHANISM_FALSIFICATION.md), scientific_closeout_v1/state_shift_control.csv. Functional rank changes do not establish useful alpha or a valid permutation null. No new LSTM forward, perturbation campaign, hidden-state replay or planted-fit experiment ran.
