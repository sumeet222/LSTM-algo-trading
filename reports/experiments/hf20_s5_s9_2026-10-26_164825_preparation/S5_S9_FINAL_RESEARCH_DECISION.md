# S5 + S9 final research decision

**TECHNICAL_PASS:16/16 lifecycles,32 prefix recipes and64 fitted controls completed. Ledger114→130/200;0 failures/retries.** Fixed20 stocks,48 completed steps,seven candidate origins, frozen F21–F24 populations and all source/timing qualifications remain. Protected2026 contents and hashes stayed closed. These repeatedly inspected years provide **exploratory, post-search evidence**.

All results below equally weight the four OOS years. Brackets are descriptive95% whole-month bootstrap intervals for the paired difference, not confirmatory significance.

| Family | Completed | Primary OOS result and matched comparison | Scientific conclusion |
| --- | --- | --- | --- |
| S5 META-T2R |4/4 PASS|Daily RankIC0.008904; versus frozen S4-T2R Δ+0.002983 [−0.010230,+0.014905], positive3/4 years|**INCONCLUSIVE:** no reliable incremental ranking advantage.|
| S9 MAG |4/4 PASS|log1p-magnitude MSE0.232454; versus stock control Δ−0.036929 [−0.042946,−0.031723], **13.7% lower**, better4/4 years. Versus trailing-volatility control Δ−0.035812 [−0.040886,−0.031409],13.3% lower, better4/4|**QUALIFIED:** useful conditional movement-size information within this exploratory source/sample.|
| S9 EVENT |4/4 PASS|Three-class CE0.202028 versus stock-prior0.196030: Δ+0.005998 [+0.002984,+0.009021], worse4/4 years. ANY AP0.1442 versus stock-prior0.1493|**NO_EDGE beyond stock controls:** discriminates tails better than pooled prevalence, but stock priors are stronger.|
| S9 QUANTILE |4/4 PASS|Mean Z-pinball0.230705 versus stock quantiles0.230242: Δ+0.000464 [+0.000035,+0.000914], worse3/4 years|**NO_EDGE beyond stock controls:** outer-distribution information relative to pooled controls, without beating stock-specific quantiles.|

MAG raw-|R| MAE is0.006505 versus stock-level0.006903 and volatility0.006992; its movement-size rank association is0.408. These are price-only endpoint magnitudes, not signed ranking, intrapath volatility, executable returns or a trading strategy. Mean predicted|R|0.00836 remains below observed0.01031; raw-scale calibration is incomplete. The inverse of the transformed prediction is not certified E[|R|]. Equal-year proper loss improves for all20 stocks; stratum estimates remain descriptive. Constant controls optimize the transformed objective; their raw-scale errors are not optimal raw-MAE/MSE benchmarks.

EVENT improves on the pooled prior (CE0.220307; ANY AP/prevalence0.04646), but its ANY Brier0.042775 and log loss0.169894 also trail stock priors0.041273/0.163901. A large AP/prevalence ratio therefore does not establish incremental history-based probability skill. Original E1 labels are retained with the explicitly approved natural unweighted CE.

QUANTILE beats pooled pinball0.234292, mainly in outer quantiles. Its90% interval covers91.86% versus stock-control90.03%, with wider Z intervals3.755 versus3.598. Median daily RankIC averages only0.00128 with mixed annual signs. Width and coverage do not establish directional alpha. Loss is the executed QR1 asinh-unit pinball; original TG20 quantiles are inverted once.

S5 uses six verified clock channels, not unverified historical quality/age flags. Its comparison tests the training-with-clock package, not causal missingness attribution. Actual publication/fills, source/action vintage and fixed-survivor limitations persist. No other experiment, fusion, seed, confirmation or trading activation follows. Whether the magnitude result survives independent evaluation remains unresolved.

[Annual paired effects and uncertainty](S5_S9_PAIRED_OOS_UNCERTAINTY.csv) · [All role/model/control metrics](S5_S9_MODEL_METRICS.csv) · [Detailed training/extreme diagnostics](S5_S9_DETAILED_TRAINING_AND_EXTREME_DIAGNOSTICS.md) · [Offline dashboard](S5_S9_VISUAL_DIAGNOSTICS.html) · [Complete analysis file index](S5_S9_DIAGNOSTIC_INDEX.md).
