# P020 untrained matched-pair handoff

**FEATURE_READY_FOR_TRAINING. Dataset preparation only; neural training is not authorized.**

Frozen chronology: warmup2010-07-01–2011-03-31; research train2011-04-01–2025-06-30; inner train ends2023-01-23; nominal inner validation2023-01-24–2025-06-30; development2025-07-01–2025-12-31; protected confirmation2026-01-01–2026-03-31 (keys/calendar/source quality only). First48complete-hour contexts after fit cutoffs are embargoed. All horizons mature within the same session; no crossing labels survive. The nominal15calendar-year research/confirmation span contains14years3months of fitted training history plus9months earlier startup. Missing dates and hourly positions never compress.

| Split | Admitted origins | Stock rows | First/last admitted date |
| --- | --- | --- | --- |
| inner_train | 4428 | 88560 | 2011-04-01 / 2023-01-23 |
| inner_validation | 766 | 15320 | 2023-02-03 / 2025-06-30 |
| refit | 5210 | 104200 | 2011-04-01 / 2025-06-30 |
| development | 183 | 3660 | 2025-07-15 / 2025-12-31 |

**No model has been trained in Package 020**. No optimization, checkpoint access, inference, portfolio or final-test work occurred. The next task must separately approve the exact matched C0→T2 seed42 pairs and any ledger amendment before reservation/start. This file grants none.

Read release_gate.json, model_input_contract.json and next_training_manifest_NOT_AUTHORIZED.json. Use lstm_data.hf1m_ft16_loader.load_model_input(contract,split=...,fit_version=...). The only splits are inner_train/inner_validation/refit/development, with inner/inner/refit/refit recipes. batch(positions,target_mode="C0" or "T2") returns finite float32 X[B,20,48,16], Y[B,20]. Flatten only stock examples within eligible sessions for the shared LSTM; preserve equal-session/origin/stock loss and absent-origin padding masks. Original/older HF20 loaders cannot consume these new data; do not call them or copy their hard-coded counts.

TM0 compatibility is code-reviewed: one layer,width32,dropout0.10,6,433parameters (4*32*(16+32+2)+33), AdamW lr0.001,betas0.9/0.999,eps1e-8,weight decay0.01matrix/0bias, globalL2clip1,16sessions/batch. D6gmin12,max60,patience10,qualifying0.1%improvement. Calibrate using inner-only preprocessing and original-scale validation MSE for both arms; then fresh same-seed refit on full prefix with its own recipe for the selected epoch count. C0 original TG20; T2 asinh with saved fit scale; invert once before original-scale selection and development diagnostics. No parameter or architecture search.

Frozen source, cohort, dates, feature definitions, fallbacks, scalers, target and T2 metadata are ready to load; do not choose them again from model outcomes. Preserve the10+3later hypotheses. Known limitations remain conditional source latency/rights, retrospective survivorship selection, price-only dividends,15:30daily surrogate, observed-range and incomplete-volume lower bounds, local quarantine and channel fallback.
