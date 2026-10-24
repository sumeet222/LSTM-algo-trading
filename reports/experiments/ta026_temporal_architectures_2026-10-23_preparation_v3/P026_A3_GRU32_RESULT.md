# P026 A3 GRU32

Scope: RESEARCH_CANDIDATE. Run HF1M-LONG-GRU32-T2-S42-DEV1; seed42; 4833 parameters.

Calibration selector (strict original-TG20 MSE): `{"best": 3.6549491583651705, "epoch": 13, "patience": 10, "raw_epoch": 6, "raw_min": 3.6534004620477263, "selected": 3, "status": "PATIENCE_STOP"}`. Fresh refit initialization equals initial calibration initialization. No baseline refit.

| role | MSE | IC | prediction_SD | actual_objective_z_MSE |
|---|---|---|---|---|
| inner_train | 4.14821 | 0.0452136 | 0.0404204 | 1.33144 |
| inner_validation | 3.65495 | 0.0044738 | 0.0459661 | 1.31376 |
| refit | 4.06286 | 0.0514207 | 0.0363007 | 1.32751 |
| development | 3.11474 | 0.012118 | 0.0348634 | 1.28743 |


Actual z-MSE, original-TG20 MSE and historical online dropout-ON objectives are separate records. Matched T2/42, T2/123 and ZERO are in role metrics. Full update/parameter-gradient telemetry and immutable epoch receipts are bound in the run result; gamma/query trajectory applies to A1. Mechanism tables measure actual saved models. GRU gates are unobserved.

Development reuses183 origins/109 sessions in research scope. Paired400 one/two-month sensitivities are exploratory, not independent confirmation. Module use and amplitude changes are not predictive skill. No automatic promotion or additional training.
