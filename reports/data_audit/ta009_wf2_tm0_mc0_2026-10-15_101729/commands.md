# Package009 reproduction and read-only review

Use the repository setup in README and the repository `.venv`. Source archives and the qualified local-use authority must be available through the documented data configuration. No secrets or raw archives are included in this packet. Relative paths below assume the repository root. The proposal, source hashes, new recipes and input binding are immutable evidence of this execution.

Preparation entry point: `.venv/bin/python -B -m lstm_data.wf2_replication --prepare --output <new-empty-packet>`. It reconstructs the longer-prefix recipes from the existing component stores; it does not fit a neural model. New wall-clock construction timestamps are expected to change recipe identities; historical information boundaries remain fixed. The prepared packet then needs an exact new code/input/run-bound approval before any genuine fit. Do not reuse this consumed approval for a reproduction fit.

The exact current plan can be inspected without training:

```sh
.venv/bin/python -B -m lstm_data.wf2_replication --dry-run --plan reports/data_audit/ta009_wf2_tm0_mc0_2026-10-15_101729/wf2_two_pair_proposal_corrected.json --output reports/data_audit/ta009_wf2_tm0_mc0_2026-10-15_101729
```

The final authorized execution command is recorded in `batch_execution_absolute_command.json`, using `wf2_two_pair_proposal_corrected.json` and the actual attributable response in `authority_corrected.json`. Its scientific queue is TM0 then MC0, seed42, each calibration and independent fresh refit. The journal refuses repeated consumed run IDs. Neural execution requires an absolute output path; use `--output "$PWD/reports/data_audit/<packet>"` from the repository root. The actual invocation's machine path is recorded only as runtime evidence. `batch_execution_command.json` and `batch_execution_corrected_command.json` preserve two pre-STARTED launch failures. `authority.json` belongs to the first code binding; it does not authorize the corrected code. The earlier `_PENDING` file and draft proposal are historical preparation evidence and grant no authority.

Read-only result verification, once both results exist, uses:

```sh
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python -B -m lstm_data.wf2_review --package reports/data_audit/ta009_wf2_tm0_mc0_2026-10-15_101729 --plan reports/data_audit/ta009_wf2_tm0_mc0_2026-10-15_101729/wf2_two_pair_proposal_corrected.json --approval reports/data_audit/ta009_wf2_tm0_mc0_2026-10-15_101729/authority_corrected.json
```

This safely reloads final CPU float32 weights, recomputes the whole matched WF2 forecast panel, verifies targets and telemetry conservation, and writes compact summaries. Outputs use exclusive creation, so choose a documented fresh review location/code path for a second export instead of overwriting this evidence packet.

Checks run before authorization:

```sh
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python -B -m pytest tests/test_wf2_replication.py tests/test_real_bridge.py tests/test_real_multimodel_batch.py tests/test_neural_health.py -q
.venv/bin/ruff check .
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
git diff --check
```

The Pylance extension path above records this machine's actual check invocation. On another machine, supply its installed Pylance extension `dist` path; no production code depends on that path. Select `.venv/bin/python` in VS Code, reload the language server and refresh Problems. Final editor parity is human-confirmed.

Compatibility: WF1 defaults remain in `BatchInputs`, but existing Package007/008 entry points intentionally bind their original execution source hashes and fail closed with the extended bridge source. Use commit `bbb8d223650dbc42a744fd910b76e30ffe3f04a8` plus the historical packet for their original reproduction. Do not weaken those guards. Original modified-source bytes are preserved in `historical_source/` here. Package009 validates historical producer/journal identity and separately binds its new execution code.

The reproducible one-shot narrative/scalar-table exporter is `.venv/bin/python -B scripts/build_ta009_review_packet.py --package <completed-reviewed-packet>`. It consumes the sealed inference/epoch tables, uses exclusive creation and must run before those derived filenames exist. It never fits or changes a journal. The original export used an equivalent temporary script; the portable script is now included and passes the186-file static check and --help smoke. Later report appendices record the final check/clock snapshot.
