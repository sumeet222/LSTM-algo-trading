# P019 reproduction and dashboard handoff

Use the repository's documented .venv setup and dependencies. No new dependency,
credential or provider access is required. An authorized private machine needs the
018D exact allowlisted source files; do not copy licensed candles to a teammate
without separate rights. Missing or changed files fail identity, with no downloader
or fallback in these CLIs. Public sources are event facts, never replacement OHLC.

From the project root, choose a NEW output directory:

```bash
.venv/bin/python -B -m lstm_data.hf1m_action_audit --out reports/data_audit/p019_reproduction
```

Archive the reviewed external_search_receipt.json and config event facts with the
new packet; external evidence is an explicit researcher review, not auto-certification.
Then run:

```bash
.venv/bin/python -B -m lstm_data.hf1m_action_review --out reports/data_audit/p019_reproduction
.venv/bin/python -B -m lstm_data.hf1m_action_review --verify-raw --out reports/data_audit/p019_reproduction
.venv/bin/python -m pytest tests/test_hf1m_action_audit.py tests/test_hf_minute_long.py -q
.venv/bin/ruff check .
```

Publication refuses existing JSON outputs. Use a new directory for another review;
do not rewrite a prior gate. Current expected gate is STOP_ACTION_UNVERIFIED,
67 candidate minutes including 13 prior records, 46 blockers, zero model starts.

For a future GUI, consume the compact candidate/evidence/gate JSON and source QA
counts. Private event_inventory.parquet and source_hour_event_contexts.parquet
hold actual candles and flags; their directory is in scan_receipt.json. These
are not feature tensors or trainable data. Show STOP visibly; do not register an
old HF20 run, import old source readers or display invented fit/forecast panels.
No dashboard code or source binding was changed here.

Scientific downstream tests (TG median/MAD/epsilon, train-only fitting, matching
C0/T2 masks/inverse, gradient telemetry) are NOT RUN because their inputs are gated.
Passing scanner tests does not clear these later requirements.
