# P4.1–P4.2 combined package report

**P4_1_P4_2_SYNTHETIC_ENGINEERING_COMPLETE — HUMAN_REVIEW_REQUIRED; SCIENTIFIC_ACTIVATION_HOLD.**

Implemented the real typed PyTorch TM0 engine, whole-session loss/sampler/AdamW/clip,
P2-certified indexed synthetic views, strict D6g selection and fresh refit, safe immutable
checkpoints, isolated finite-state pair guards and a model-to-P3 score adapter.
No actual historical model, trading replay, provider request or scientific activation ran.

|Hand check|Expected|Actual|
|---|---:|---:|
|Trainable parameters|6433|6433|
|Session losses (two origins 2/6, one origin 10)|4 / 10|4 / 10|
|Equal-session MSE|7|7|
|Wrong pooled-origin alternative|6|rejected|
|19-session eval,16+3 batches|9|9; naive batch mean 12.25 rejected|
|Selected epoch/refit duration|strict D6g|60 /60, MAX_EPOCHS_REACHED|
|Same-CPU final reload max error|0|0|

The independent scripted timeline 1,.9995, then1 selects epoch 1, records raw minimum
epoch 2 and stops at 12. The actual planted seed42 run reaches the 60-epoch cap with
validation MSE falling from 1.67015816
to 0.000170446132. Training mean-session MSE
falls from 1.71170464 to
0.0089524042; refit last training MSE is
0.00808296124. These are fabricated G5 signals, not alpha.

Calibration has 37 sessions/180 optimizer updates; fresh full-prefix refit has 100
sessions/420 updates. Inner validation remains the fixed 63 XNYS sessions from
2023-03-31; 55 sessions/55 each origin pass the inherited ASOF per-step normalization
clock. The first 8 sessions are explicitly excluded; no backward shift or shorter
48-step windows. Fitting cutoff is 2023-07-01T04:00Z. Mature TG0, feature/floor/scaler
math, masks, clocks and full-population ordering reuse the existing P2/P3 contracts.
Unknown/NaT clocks fail before preprocessing.

Fresh calibration/refit initial weights match the reset seed; the optimizer is new and
empty. Actual fitted preparation IDs differ:
- calibration `d224d947d3f17cae19f76932a1cb0412a2d262a4eb95db312f7518b512e83315`;
- refit `3c87e262061fbd16c338a700e9ab4c01b291a96f072f60e29bfd6273bb236faa`.

The final forecasting checkpoint is refit_final.pt, SHA `65ad8c3aa02b66c5581b2d18d69eb82bc832144ecb3fcd2d1d0393f02d67bbfb`;
calibration_selected.pt is audit-only, SHA `b01411e33315a68025baccd8515fe52cd60e677ec1166f0bee8c0f220e6dea46`.
They contain 54737 and 72593
bytes respectively. Data/order/target/floor/cutoff/code/config changes invalidate reuse.
Resume is same-CPU at an explicitly complete epoch boundary with optimizer and used
Torch RNG; no mid-epoch resume or cross-device bitwise claim. Interrupted full lifecycle
runs refuse an existing directory and require a distinct attempt; incomplete/failed
calibration cannot unlock an authoritative refit.

Release fixture/audit elapsed 164.78s, of which recorded
calibration/refit stages are 11.60s/14.93s.
Peak process memory 372,981,760 bytes; machine RAM 8GiB.
One shared indexed table has 3215×16 rows/channels and200 origin index records;
no per-seed48-step archive. Illustrative linear scaling to1502 origins is explicitly
non-binding; no measured real-data runtime/retention is claimed. PyTorch 2.10.0 was
installed only after explicit user approval and pinned in the optional neural extra.

Fresh release full suite: **489 PASS** (704.29s). Basic parity:
**107 files, 0 errors/0 warnings**. Ruff, AST, diff and source conservation PASS.
Earlier full baselines468/473/484 and the superseded pre-clock-guard489 PASS are
retained; release_pytest and release_types are authoritative for delivered code.

All 1028 starting protected files are preserved except the intended README/pyproject
updates; source Parquets/manifests, P2/P3 public code, frozen pointers/registers and
append-only history are unchanged. Scientific use stays 0/40, G0–G4 HOLD, P4.3 BLOCKED.
Original 168/15 native gaps and inactive 1183/1502 retention remain deferred evidence.
No source correction, historical fitted floor/scaler, execution/source/action approval,
confirmation outcome or larger/market/peer model experiment is implied.

Review [the API](../../../docs/track_a/P4_NEURAL_ENGINE_API_v1.md), [checks](checks.json),
[release evidence](synthetic_g5_release/synthetic_evidence.json) and [human card](human_review_card.md).
STOP after one consolidated human review; no P4.3 progression or Git integration.
