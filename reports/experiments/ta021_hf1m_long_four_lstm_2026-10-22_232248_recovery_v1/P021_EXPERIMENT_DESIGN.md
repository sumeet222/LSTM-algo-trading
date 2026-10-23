# P021 frozen experiment design

| run_id | seed | arm | calibration_epochs | refit_epochs | calibration_steps | refit_steps |
| --- | --- | --- | --- | --- | --- | --- |
| HF1M-LONG-TM0-C0-S42-DEV1 | 42 | C0 | 12 | 1 | 1896 | 187 |
| HF1M-LONG-TM0-T2-S42-DEV1 | 42 | T2 | 17 | 7 | 2686 | 1309 |
| HF1M-LONG-TM0-C0-S123-DEV1 | 123 | C0 | 12 | 1 | 1896 | 187 |
| HF1M-LONG-TM0-T2-S123-DEV1 | 123 | T2 | 12 | 1 | 1896 | 187 |

One shared stock-only TM0: `LSTM(16,32,num_layers=1,batch_first=True)`, output-hidden `Dropout(0.10)`, linear32→1 signed head. Actual 6,433 parameters =4×32×(16+32+2)+33. Recurrent dropout is0. Fresh zero hidden/cell state per stock sequence.

Each origin supplies20×48×16 float32 inputs. A batch samples16 complete eligible sessions, keeps all admitted origins and all20 stocks, and retains the smaller last batch. Loss is equal-stock within origin, equal-origin within session, equal-session across the epoch. Missing scheduled positions are never compressed.

AdamW lr0.001, betas(0.9,0.999), eps1e-8, matrix decay0.01/bias decay0, no schedule; global L2 clip cap1. D6g minimum12/maximum60/patience10; qualification is strictly `loss < 0.999*qualifying_best` on original-TG20 inner-validation MSE. Raw minimum, qualifying selection, patience and actual stop are separate. Epoch1 can be selected despite running at least12 epochs.

C0 objective is original TG20 MSE, inverse identity. T2 objective is MSE in `z=asinh(TG20/s_phase)` with saved s_inner=0.906406830018944, s_refit=0.9057319697455458. Inverse `s*sinh(z)` exactly once before comparable metrics. Checkpoint scale metadata records the phase's saved T2 scale; C0 remains identity. No new scale fitting or clipping.

Calibration uses inner preprocessing; fresh same-seed full-prefix refit uses refit preprocessing for exactly the selected epochs. No weights or optimizer state transfer across phases/arms. Python/NumPy/Torch seeded, deterministic algorithms, SHA(seed:epoch) session shuffle, CPU4 threads/interop1, no workers. Same-device reload equality; no cross-platform bitwise promise.

| partition | origins | stock_rows | sessions | first | last | fit |
| --- | --- | --- | --- | --- | --- | --- |
| development | 183 | 3660 | 109 | 2025-07-15 | 2025-12-31 | refit |
| inner_train | 4428 | 88560 | 2513 | 2011-04-01 | 2023-01-23 | inner |
| inner_validation | 766 | 15320 | 459 | 2023-02-03 | 2025-06-30 | inner |
| refit | 5210 | 104200 | 2980 | 2011-04-01 | 2025-06-30 | refit |

Nominal fitting prefix: April2011–June2025 (14years3months), preceded by July2010–March2011 warmup. Inner validation nominally begins January24,2023; development July1,2025. The48-complete-hour embargo and exact admitted IDs yield the actual dates above. Inner validation selects checkpoints; refit includes its historical dates and is in-sample. Development is post-fit exploratory. Confirmation stays locked.
