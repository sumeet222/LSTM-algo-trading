# Actual HF20 retention

The denominator is the fixed source/clock structural grid, independent of future outcome availability. The original v1 full-training result822/1154=71.2305% failed90%; it is preserved in real_preparation_v1. V2 changes only daily-close validity and explicitly approved acceptance, with no repair/imputation. Both the v2 first build and final reproduction produce identical counts.

|Population|Structural origins|Source ready|Feature ready|Forecast issuable|Label ready|Supervised ready|Retained|Sessions|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|inner:inner_train|1028|948|873|873|1022|872|84.8249%|436|
|inner:inner_validation|126|126|126|110|126|110|87.3016%|55|
|refit:train|1154|1074|999|999|1148|998|86.4818%|499|
|refit:development|382|382|382|366|382|366|95.8115%|183|

Feature exclusions are linked by origin/stock/channel and invalid historical-step span in released_preparation/feature_exclusion_dependencies.csv. Full target and forecast masks remain independent in each origin table. The first usable training origin is2022-12-13: the126-session daily warmup does not instantly provide48 already-valid M4 feature steps. Frozen train dates are not shifted to hide this loss. Development first usable origin is2025-04-10 because fit availability is required at every historical input step. Inner tail starts2024-12-26; usable origins begin2025-01-08 and span55sessions.

V2 source masks predict998/872/366/110 admissions, exactly reproduced by fresh full preparation. Original source-only geometry1073/382 was never used as FT1 certification. This implementation has1074 source-window-ready training origins and1148 label-ready structural origins; their intersection is1073, explaining the inherited upper bound. No new held-out eligibility/target values were computed. Threshold changes are attributed to actual human approval, not inherited from the five-stock protocol.
