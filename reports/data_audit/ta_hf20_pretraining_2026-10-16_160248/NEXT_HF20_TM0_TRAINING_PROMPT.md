# Future separately authorized HF20 TM0 training request

Dataset preparation is **HF20_TRAIN_INPUT_READY_CONDITIONAL**. This file is a proposed next request, not authorization to fit.

Use `reports/data_audit/ta_hf20_pretraining_2026-10-16_160248/training_ready_input_contract.json`, SHA256 `4be39c0e85fc390766331ecb19e2a24721399f1e201de864eabe8eeed49add1c`, preparation `HF20_PREP:21cd2432a8944dce5edcf7c78a3e2f806e90a15e944cbf6db78c43a4a3982ff2`. Load only through `lstm_data.hf20_loader.load_hf20_train_data`; use inner/inner_train and inner/inner_validation for calibration, refit/refit for fresh training, refit/development for exploratory evaluation. No more data cleanup, source sweep or normalization selection is required by this handoff.

Before fitting, the researcher must supply/approve the exact first one-pair run scope: model/loss/optimizer/learning rate/seed, two-pass epoch-selection rules, compute wall-clock cap and a new source-specific run/budget record. A compact shared stockwise reference can reuse the one-layer hidden32, dropout0.1,16-channel, scalar-head6433-parameter architecture; those future training choices are not selected or activated in this package. The existing five-stock training session schema assumes five stocks: implement an additive HF20 session grouping adapter over this ready20-stock loader, preserving equal-stock/origin/session weighting; do not mutate historic batches/checkpoints. Model/seed choice and fitting remain a new explicit task, not permission inferred from the data contract.

Required preflight is hash/approval/contract verification and a no-fit loader sample. Then run exactly the newly authorized calibration/refit pair, report actual data-loading/calibration/refit/inference/wall-clock time, hardware, epochs and updates; no automatic second run. Keep the existing historic ledger28/200 unchanged unless its amendment is explicitly part of that future run authorization. HF20 currently has zero fits. Never read2026-01-07–2026-10-15 confirmation or the original project's separate protected source; no paid acquisition or redistribution.

```bash
.venv/bin/python -m lstm_data.hf20_loader --contract reports/data_audit/ta_hf20_pretraining_2026-10-16_160248/training_ready_input_contract.json --split development --recipe refit
```

Expected no-fit smoke:366 origins, finite sample shape3×20×48×16, preparation ID above. All six missing source hours stay masked, and as-reported price/share-volume, publication, daily proxy, retrospective cohort and researcher-attested rights limitations travel with every future artifact.
