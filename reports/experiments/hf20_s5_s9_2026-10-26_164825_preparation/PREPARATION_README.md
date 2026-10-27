# HF20 S5 + S9 preparation

Preparation is complete; actual training is awaiting the single live-fit response. No campaign result is represented. Start at [approval card](LIVE_FIT_APPROVAL_CARD.md), [complete diagnostic map](S5_S9_DIAGNOSTIC_INDEX.md), [metadata](S5_CAUSAL_METADATA_MANIFEST.md), [targets/controls](S9_TARGET_AND_BASELINE_CONTRACT.md), and [preflight](PREFLIGHT.json).

Four role populations and candidate slots are in S5_S9_ROLE_COUNTS.csv and S5_CAUSAL_COVERAGE_AND_DIAGNOSTIC_STRATA.csv. Final browser preview is preflight_v2/S5_S9_VISUAL_DIAGNOSTICS.html; all visible models are untrained rehearsal examples, not actual starts.

After actual approval is recorded in LIVE_AUTHORITY.json with the exact proposal/code hashes, ordered16 run IDs,64 controls,32 recipes and caps, execute from the repository root:

```bash
.venv/bin/python -u -m lstm_data.hf20_s5s9_run --out reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation
.venv/bin/python -m lstm_data.hf20_s5s9_visual --out reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation --render
```

Do not manufacture the approval file from this proposed card. A serious failure consumes any charged start; no resume/retry is authorized. Preserve failed output and seek the required continuation authority. Real numerical source reads remain bounded before I/O to the existing pre2025 monthly sources. No credential or network access is needed.

Reproduce preparation only into a new nested directory (never overwrite prior evidence):

```bash
.venv/bin/python -m lstm_data.hf20_s5s9_prepare --out reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation/preflight_reproduction
.venv/bin/python -m pytest tests/test_hf20_s4_readonly.py tests/test_hf20_s5s9.py -q
.venv/bin/ruff check .
```

The preparation command makes no optimizer update or new historical-target/control fit; it uses explicitly toy rehearsal recipes for the new targets. Private checkpoints/score stores and offline HTML remain ignored; compact contracts/tests/summary receipts can be reviewed for a future separately authorized commit. No source prices or model/data redistribution permission is implied.
