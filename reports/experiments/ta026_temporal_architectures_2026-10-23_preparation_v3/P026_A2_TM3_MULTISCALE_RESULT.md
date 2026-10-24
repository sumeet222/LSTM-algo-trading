# P026 A2 TM3_MULTISCALE

Scope: RESEARCH_CANDIDATE. Run HF1M-LONG-TM3_MULTISCALE-T2-S42-DEV1; seed42; 7217 parameters.

Calibration selector (strict original-TG20 MSE): `{"best": 3.6508988282259773, "epoch": 17, "patience": 10, "raw_epoch": 7, "raw_min": 3.6508988282259773, "selected": 7, "status": "PATIENCE_STOP"}`. Fresh refit initialization equals initial calibration initialization. No baseline refit.

| role | MSE | IC | prediction_SD | actual_objective_z_MSE |
|---|---|---|---|---|
| inner_train | 4.1411 | 0.0714076 | 0.0571736 | 1.32743 |
| inner_validation | 3.6509 | 0.0164947 | 0.0541376 | 1.3128 |
| refit | 4.05602 | 0.0693395 | 0.052768 | 1.3241 |
| development | 3.10866 | 0.0595961 | 0.0480931 | 1.28276 |


Actual z-MSE, original-TG20 MSE and historical online dropout-ON objectives are separate records. Matched T2/42, T2/123 and ZERO are in role metrics. Full update/parameter-gradient telemetry and immutable epoch receipts are bound in the run result; gamma/query trajectory applies to A1. Mechanism tables measure actual saved models. GRU gates are unobserved.

Development reuses183 origins/109 sessions in research scope. Paired400 one/two-month sensitivities are exploratory, not independent confirmation. Module use and amplitude changes are not predictive skill. No automatic promotion or additional training.
