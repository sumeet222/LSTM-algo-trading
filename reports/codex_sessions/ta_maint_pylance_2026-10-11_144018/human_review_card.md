# TA-MAINT-PYLANCE-001 review card

No code patches: Gate A blocked on reproducible editor diagnostics. Do not infer zero errors from absent CLI output.

1. `pyproject.toml:20` development dependencies contain pytest/Ruff, no static checker; observed VS Code user basic setting is not the resolved workspace/profile configuration. Paste Problems diagnostics with selected interpreter and effective severity/mode to resume; no settings/tool install performed.
2. `src/lstm_data/clocks.py:session_clock:46` / `execution_plan:86`: protected normal/early-close schedules, DST and240min. Quick `python -m pytest tests/test_clocks.py -q`.
3. `src/lstm_data/labels.py:label_sample:262` / `src/lstm_data/hourly_proxy.py:proxy_label_sample:213`: preserve minute/proxy version meaning, C01 and maturity. Quick `python -m pytest tests/test_labels.py tests/test_hourly_proxy.py -q`.
4. `src/lstm_data/corporate_actions.py:apply_action:365` / `snapshot:506`: preserved signed split/wealth and missing NAV semantics. Short4:1 split synthetic retains10000 equity; no accounting change.
5. `src/lstm_data/m2.py:window_quality:119` / `historical_return:215` / `evaluate_m2:378`: preserved239/240 missing-cell mask, split return and source/action hashes. Floor-vs-step.information_cutoff review remains separately deferred; no causal logic correction hidden here.
6. `src/lstm_data/audit.py:protocol_check:121` / `reports/audit/track_a_events.jsonl`: same five governing hashes/pointer and23event full-file hash, seven historical blockers and0/40 neural pairs. No ledger append/rewrite.
7. Integration manifest: CA/R1/M2 are already committed at starting HEAD. Only five new maintenance reports are untracked; no historical dependencies/ledger need restaging. Current baseline `python -m pytest -q`:220passed44.89s;31project Python files parsed. All70protected hashes and synthetic before/after snapshots match.
