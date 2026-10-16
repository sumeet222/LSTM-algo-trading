# HF20 hourly-native preparation and no-fit loader

This is a separate source-specific20-stock candidate, not a legacy D1/FT0/TG0 migration. The approved methodology is `reports/data_audit/ta_hf20_pretraining_2026-10-16_160248/HF20_HOURLY_NATIVE_METHODOLOGY.md`; actual decisions/rights and exact transcript hashes are in the same report. Default code does not grant training authority. The final active entry point is `reports/data_audit/ta_hf20_pretraining_2026-10-16_160248/training_ready_input_contract.json`.

```python
from pathlib import Path
from lstm_data.hf20_loader import load_hf20_train_data
view = load_hf20_train_data(Path("reports/data_audit/ta_hf20_pretraining_2026-10-16_160248/training_ready_input_contract.json"), split="development", recipe="refit")
batch = view.batch((0, len(view.rows)//2, len(view.rows)-1))
assert batch.x.shape == (3, 20, 48, 16)
```

Use inner_train/inner_validation with recipe=inner, refit/development with recipe=refit. Forecast-only development is available as forecast_development and keeps label masks separate. Group origins by batch.sessions for later equal-day weighting; do not shuffle stocks/historical steps. No old five-stock checkpoint acceptance or training API is exposed. Held_out, confirmation and legacy splits fail before store loading.

Reproduction requires the existing repository .venv and documented dependencies, the exact three pinned HF Parquets in their manifest-bound one-copy cache, and legitimate actual approval/rights receipts. Code/config/test/docs are portable; the licensed numerical store is intentionally not in Git. A clean machine needs independently authorized data/receipt handoff; copying only the repo does not transfer vendor rights.

```bash
.venv/bin/python -m lstm_data.hf20_prepare --out reports/data_audit/hf20_reproduction_NEW --approval reports/data_audit/ta_hf20_pretraining_2026-10-16_160248/human_approval_transcript.json --config configs/hf20_hourly_native_v2.json --amendment reports/data_audit/ta_hf20_pretraining_2026-10-16_160248/human_amendment_v2_approval.json
.venv/bin/python -m lstm_data.hf20_loader --contract reports/data_audit/ta_hf20_pretraining_2026-10-16_160248/training_ready_input_contract.json --split development --recipe refit
.venv/bin/python scripts/audit_hf20_inputs.py --contract reports/data_audit/ta_hf20_pretraining_2026-10-16_160248/training_ready_input_contract.json --out reports/data_audit/hf20_floor_reproduction_NEW
.venv/bin/python scripts/check_hf20_loader.py --contract reports/data_audit/ta_hf20_pretraining_2026-10-16_160248/training_ready_input_contract.json --out reports/data_audit/hf20_loader_reproduction_NEW.json
.venv/bin/python -m pytest tests/test_hf_hourly.py tests/test_hf20_pretraining.py -q
.venv/bin/ruff check .
```

Use a new output directory for each preparation/audit. Exact cached deterministic preparation IDs must be preserved; an already-existing immutable store fails closed instead of overwriting it. If reproducing on the same machine, first reuse the sealed existing contract; a new report name alone does not authorize overwriting a matching component store. No destructive cleanup is implied. Final store uses common15hour channels and separate origin-matched M2day rows, so dense48-step windows exist only for a requested batch. Targets and recipe files are separate, with no per-model/seed data copies. Preliminary v1/v2 datasets are preserved as failed/amended/build-validation evidence; only released_preparation is the released preparation.
