# P024 execution handoff — awaiting live approval

Do not train before the exact sealed proposal/code approval is recorded. The prompt itself is not approval (Package024 Stage2). Current ledger44/200; proposed starts45–50 only. Current v12pointer and all earlier failures remain immutable until the first approved start activates the v13successor.

After approval, record the exact live response in a NEW live_approval.json with status=APPROVED, actor_type=human, response_provenance=LIVE_USER_RESPONSE_IN_THIS_SESSION, response_text verbatim, approved_runs equal to the six frozen run IDs, proposal_sha256 matching experiment_design.json and execution_sha256 matching the frozen execution binding. Do not invent an approval or reuse old P023approval.

Run one arm at a time, then independently verify its immediate diagnostics before the next start. Example for the first arm (from repository root):

```bash
.venv/bin/python -u -m lstm_data.optimization_screen_run --plan reports/experiments/ta024_hf1m_long_optimization_2026-10-23_preparation_v3/experiment_design.json --approval reports/experiments/ta024_hf1m_long_optimization_2026-10-23_preparation_v3/live_approval.json --run-id HF1M-LONG-TM0-LRLOW-S42-DEV1
.venv/bin/python -m lstm_data.optimization_screen_diagnostics --plan reports/experiments/ta024_hf1m_long_optimization_2026-10-23_preparation_v3/experiment_design.json --arm LRLOW --out reports/experiments/ta024_hf1m_long_optimization_2026-10-23_preparation_v3/LRLOW_diagnostics_v1
```

Review run_result, actual optimizer/epoch receipts, four complete prediction exports, genuine source/label identities, fixed-checkpoint objective and ZERO identities, cohorts/22source witnesses, matched daily comparisons and the PASS_LRLOW receipt. Verify global count45before proceeding with DROP0/42→WD0/42→ES025/123→H64/42→L2H32/42. Do not wrap all starts in an unconditional shell loop.

An error or missing scientific gate stops the package. Preserve charged starts and every partial output. No repeat or output-directory replacement is authorized. Read-only export corrections must have a new hashed correction receipt; empirical changed-code continuation requires a new live response.

After all six genuine stages PASS, complete the collective mechanism comparison and additive existing Streamlit P024route, source-safe interactive/full-history tests, launcher --check/smoke and final QA/inventory/report. These later deliverables are pending, not represented as completed during preparation. Final PASS_P024_COMPLETE requires actual six-start journal50/200 and all fit/diagnostic/UI gates. No seed123replication beyond ES025, combinations, protected2026outcomes, new data, trading or Git publication.

Keep E1/QR1replications, QR1state-dependence, broader10+3backlog, walk-forward/permutation and final-confirmation holds intact. Verify editor parity manually: select .venv/bin/python, restart Pylance, refresh Problems and confirm zero project-owned errors; CLI parity does not assert the editor was refreshed.
