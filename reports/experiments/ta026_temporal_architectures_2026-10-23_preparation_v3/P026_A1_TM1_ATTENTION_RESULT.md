# P026 A1 TM1_ATTENTION

Scope: RESEARCH_CANDIDATE. Run HF1M-LONG-TM1_ATTENTION-T2-S42-DEV1; seed42; 6466 parameters.

Calibration selector (strict original-TG20 MSE): `{"best": 3.652151579560797, "epoch": 17, "patience": 10, "raw_epoch": 7, "raw_min": 3.652151579560797, "selected": 7, "status": "PATIENCE_STOP"}`. Fresh refit initialization equals initial calibration initialization. No baseline refit.

| role | MSE | IC | prediction_SD | actual_objective_z_MSE |
|---|---|---|---|---|
| inner_train | 4.14159 | 0.0679147 | 0.0532862 | 1.32784 |
| inner_validation | 3.65215 | 0.0140402 | 0.050275 | 1.31286 |
| refit | 4.05507 | 0.0681036 | 0.0535979 | 1.32394 |
| development | 3.1063 | 0.075801 | 0.0497437 | 1.28096 |


Actual z-MSE, original-TG20 MSE and historical online dropout-ON objectives are separate records. Matched T2/42, T2/123 and ZERO are in role metrics. Full update/parameter-gradient telemetry and immutable epoch receipts are bound in the run result; gamma/query trajectory applies to A1. Mechanism tables measure actual saved models. GRU gates are unobserved.

Development reuses183 origins/109 sessions in research scope. Paired400 one/two-month sensitivities are exploratory, not independent confirmation. Module use and amplitude changes are not predictive skill. No automatic promotion or additional training.
