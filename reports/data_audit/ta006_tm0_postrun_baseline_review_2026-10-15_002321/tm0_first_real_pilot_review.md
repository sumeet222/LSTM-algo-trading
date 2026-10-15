# First real TM0 pilot — ACCEPT_WITH_G6_WARN

The one candidate-only TM0 seed 42 June 2023/WF1 pair is a valid **descriptive pilot with a G6 warning**. Recorded selection/fresh refit and checkpoint hashes pass. No critical leakage/calculation defect was discovered in this review. The historical 14/4 epochs, 602/188 updates, selected epoch 4 and original raw G6 PASS remain unchanged; the effective health disposition remains WARN. Neural registry stays 1/40.

| Scope / checkpoint | Sessions / origins | MSE | daily Rank IC | score SD |
|---|---:|---:|---:|---:|
|Inner validation, selected calibration epoch 4|55 / 110|4.704614528|0.005454545|0.114574|
|In-sample, final fresh refit epoch 4|751 / 1502|7.316591861|0.071105193|0.113925|
|Held-out WF1, final refit epoch 4|116 / 232|5.438829600|0.034913793|0.112073|


These review MSEs use float64 aggregation of the exact actual float32 targets/predictions; they reproduce original session-weighted float32 worker values within 2e-6 (observed differences below 5e-8). Original WF1 MSE 5.438829636 and IC 0.034913793 are frozen. Package005 did not save per-origin forecasts. Package006 performed frozen-weight inference only and saved permitted_prediction_snapshot.csv; no neural fitting or outcome access after June 2024 occurred. Each partition uses its proper selected-calibration or final-refit checkpoint/preparation. Calibration training epoch 4 is dropout-on training telemetry, not an out-of-sample evaluation.

There are no tied or constant TM0 forecasts in any reviewed partition;1160 finite WF1 stock scores. Defined-only IC equals project-convention IC. Per-origin and daily details are in pilot_metrics.json: WF1 origin 1 MSE 5.127638 / IC 0.044828; origin 2 MSE 5.750021 / IC 0.025000. Daily IC ranges -0.85 to0.90, illustrating noisy five-name ranks. No significance/alpha or trading claim is made.

| WF1 month | Sessions | MSE | daily IC |
|---|---:|---:|---:|
|2023-07|11|5.513655|-0.077273|
|2023-08|23|5.770336|0.067391|
|2023-09|20|3.583275|0.040000|
|2023-10|22|6.402223|0.018182|
|2023-11|20|6.054412|0.122500|
|2023-12|20|5.196683|-0.015000|


The last 63 calendar-session tail starts2023-03-31; the unchanged scaler-own-step guard excludes the first 8 days / 16 origins, leaving55 eligible sessions/110 origins,55 at each origin. Inner training688 sessions / 1376 origins; full refit751 / 1502. Checkpoint selection used only those inner-validation MSEs; unchanged source control flow and chronological boundaries separate WF1 until after refit. The fresh-initialization/empty-optimizer records and exact 14/4 trace counts are preserved. This review can inspect records and current code, not retrospectively observe the prior in-memory optimizer.

Clipping warnings occur in calibration 5, 7–14;11–14 clip 100% of batches. Selected4 clips 30.23% and precedes every warning; fresh refit has no sustained warning and all gradient nonfinite counts are0. See clipping_by_epoch.csv for median/p90/p95/p99/max and scale multipliers per epoch. Inner-validation MSE deteriorates from 4.704614488 at epoch 4 to 4.777490196 at epoch 14 (+1.549%). This is consistent with later optimization/overfitting stress; the frozen patience rule selected earlier weights correctly. No clip/target/optimizer/epoch rescue is made.

Actual float32 full-train TG0 min-32.425587,p01-7.953401,median0,p99 7.348948,max82.028046; WF1min-24.399897,p01-7.601656,p99 6.325568,max15.961744. Historical raw double target max82.0280428 is unchanged. The top 1% / 10% training sessions contribute 25.49% / 55.66% of squared loss, WF1 top 10% 44.62%. Existing loss shares were independently reproduced from frozen predictions; largest affected days are in training_health_review.json. Labels/errors remain unclipped.

Large targets and concentrated loss are compatible with the clipping, but per-batch/per-example gradients were not persisted, so they do not establish causation. No accumulation bug is visible: zero_grad → backward → one global clip → step occurs once per batch. Prefix-only recipes/view IDs reproduce old metrics; no normalization defect was found. One bookkeeping defect is established: the raw G6summary omitted calibration clipping. The future-only fix covers both passes and keeps this pilot's WARN visible.

| Model | WF1 MSE | daily IC | Origins / days |
|---|---:|---:|---:|
|TM0|5.438829600|0.034913793|232 / 116|
|ZERO|5.427531844|0.000000000|232 / 116|
|M1|12.691976309|-0.021982759|232 / 116|
|RIDGE_OWN_112|5.465518006|-0.022844828|232 / 116|


TM0's positive IC 0.0349 is descriptive and its MSE is slightly worse than the zero-score reference. It does not establish useful predictive advantage. Negative baseline ICs do not establish an LSTM win or justify tuning on WF1. The roadmap treats market information as an independent next hypothesis, not a reward for beating ridge. Recommend accepting this completed pilot with G6 WARN; any MC0 run still needs its explicit scope and safe candidate executor/accounting extension. No TM0 retry is recommended or authorized.
