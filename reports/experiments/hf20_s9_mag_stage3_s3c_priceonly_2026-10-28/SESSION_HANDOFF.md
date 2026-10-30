# S3-C price-only completion handoff

Status: COMPLETE 4/4; scientific verdict no incremental evidence versus CLOCK-C3. Existing process/session61912/PID68169 was supervised through its final F24 refit and output writes; training was never restarted. All four result.json records say COMPLETED; verification.json is PASS. Ledger170→174/300, four pairs/eight phases, no retries. No background training remains associated with this completed managed execution session.

Read S3C_PRICE_ONLY_RESULTS.md first, then SCIENTIFIC_SUMMARY.md. Primary equal-year MSE is 0.000106739896737, +0.069329% versus CLOCK-C3; paired95% interval includes zero. Selected epochs F21/F22/F23/F24:29/13/22/16. Preserve all outputs including the near-tied/negative evidence.

## Commands actually used

From the repository root, with its existing .venv:

```sh
.venv/bin/python -B -m lstm_data.hf20_s3c_priceonly --source
.venv/bin/python -B -m lstm_data.hf20_s3c_priceonly --prepare
.venv/bin/python -u -B -m lstm_data.hf20_s3c_priceonly --run
.venv/bin/python -B -m lstm_data.hf20_s3c_price_report
.venv/bin/python -m pytest tests/test_hf20_s3c_priceonly.py tests/test_hf20_minute_inputs.py tests/test_hf20_stage2_bcd.py tests/test_hf20_mag_c3_io.py -q
.venv/bin/ruff check src/lstm_data/hf20_s3c_priceonly.py src/lstm_data/hf20_s3c_price_report.py tests/test_hf20_s3c_priceonly.py --output-format concise
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
```

The first three commands are the original single-use execution history, NOT resume commands. DO NOT run them against this completed namespace. Report generation only reads saved predictions but would replace generated numerical tables; no rerun is needed. The local editor extension path above records this machine's executed static check, not a code dependency; another machine must supply its own installed matching Pylance dist. Score/checkpoint reproduction requires the pinned authorized external local source/phase artifacts and a separately approved fresh run; no implicit retraining permission.

Focused tests23pass; Ruffpass; fulltype522files0errors0warnings. A bounded ephemeral saved-artifact verifier (/private/tmp/verify_s3c_price.py) produced verification.json without new inference. Numeric kernel/report/test code hashes stayed frozen after preflight. Saved independent reload differences are zero. Editor verification: select repository .venv/bin/python, retain basic severity, reload VSCode/Pylance and confirm Problems shows zero errors; this last visual confirmation is human work.

## Files and preservation

New code: src/lstm_data/hf20_s3c_priceonly.py; src/lstm_data/hf20_s3c_price_report.py; tests/test_hf20_s3c_priceonly.py. New report/cache namespace is this directory. Large .pt/.parquet/.npy files are ignored; no old score/source copies. Per-fold selected/restricted checkpoints, phase recipes and own scores are retained. artifact_inventory.csv inventories this namespace excluding itself/final manifest to avoid recursive hashes.

Only existing modified file is configs/CURRENT_EXPERIMENT_REGISTRY.json (authorized successor from opening schema32 to33; inherited dirty predecessor changes remain). No old source/model/kernel/dashboard/report/journal was rewritten; bound old hashes passed. Preserve all unrelated dirty S2D and Stage3 Session1/2 work. Branch feat/track-a-data-intake, HEAD997b30cff98785911b0e33b7e3d2e72f61b8270b; no commit/push/fetch/network. Cached upstream ahead/behind0/0, not freshly fetched.

## Limitations and STOP

Approximately+2min source-publication proxy, revised action/source vintage and fixed survivor universe remain. New minute branch reads no volume, but original FT16 hourly volume remains. No2025market/protected2026access. Masks and488added parameters confound pure ordering attribution; S3B uses48hours of summaries, C usesonehour of fine detail. No separately authorized latest-hour fitted control. Repeatedly studied2021–24 years, descriptive intervals conditional on selection/calibration. No trading/option or live-latency claim.

STOP for researcher review. No S3B rerun, S3D/E, Stage5, traditional-volatility benchmark, new calibrator, extra seed or protected release.

Standard session report: reports/codex_sessions/2026-10-28_232241_hf20_s3c_priceonly_completion.md
