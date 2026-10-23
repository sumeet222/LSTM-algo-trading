# P024 LRLOW result — exploratory, completed

Run HF1M-LONG-TM0-LRLOW-S42-DEV1, start45. Only lr0.001→0.0003changed. Calibration16epochs; qualifiedselected6/rawbest7; fresh refit6epochs.2528calibration+1122refit=3650optimizer updates,255.364s,peakRSS521,781,248bytes. Effective lr verified exactly from all update records and both optimizer states. Source/features/TG20/recipes/weights unchanged.

Development183origins/3660rows/109sessions:

|Model|Original TG20 MSE|Daily Rank IC|
|---|---|---|
|LRLOW/42|3.1104042731|0.0716410258|
|SavedT2/42|3.1065600156|0.0755594463|
|ZERO|3.1165604395|undefined|

Paired difference vsT2/42:MSE+0.0038443(one-month95%exploratory interval[−0.000897,0.008564],two-month[−0.001283,0.007389]); IC−0.0039184(one-month[−0.023836,0.021826],two-month[−0.026718,0.007499]). No positive point-estimate LRLOWsignal; uncertainty includes zero. This does not prove irreducibly weak predictability or an optimizer defect.

Actual final-checkpoint refit z-MSE concentration: top|TG20|1%=1042rows,7.193844%weighted loss; top5%=5210rows,24.453900%. Both≥0.99M/≥0.95Mtraining-maximum ranges contain1row each,0.027431%loss. These are loss-accounting diagnostics, not forecasting success. Numerator/MAD disjoint groups, source-quality flags and exact22source witnesses remain in LRLOW_diagnostics_v1. Fixed-checkpoint objective and once-only inverse agree independently; all20genuine endpoints reconstruct targets.

Core and corrected supplemental diagnostics pass. Initial supplemental failure was pandas nested-float decoding changing0.0003byoneULP; raw JSON and saved optimizers were correct. See recovery_preparation_v1/REHEARSAL_AND_PARSER_VERIFICATION.md for the verified correction. No LRLOWrerun is proposed.
