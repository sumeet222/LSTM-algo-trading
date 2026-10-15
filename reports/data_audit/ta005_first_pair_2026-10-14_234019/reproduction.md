# Read-only verification and historical reproduction

Use the README environment and repository `.venv/bin/python`; no dependency changes. The exact historical training command, thread environment, start/end timestamps, exit0 and code fingerprint are in one_pair_execution_command.json. **Do not rerun it:** exactly one approved attempt has completed, and the journal rejects a second pair. A new research run requires separate authority.

Original inputs, complete ordered feature/window/preprocessing identities and numerical hand checks remain in `reports/data_audit/ta_real_input_bridge_005_2026-10-14_215455/final_v2`; this packet reuses them by hash without source/dense-window copies. Dataset input ID `0d84401fe990f2f5a0c3f0191272f9cfb5b54f75d6b4db2c94c62ccb03798ef8`. Source/model/bridge code is unchanged at `0bfddaf21c96ef714d8c5524716ca7e2c8c96b03d3b8c733a4a26b63bd909308`, GitHEAD831d9eb1e8acbd2734e1a979568314fcbc0d501f plus the reviewed uncommitted bridge files in the prior inventory. No clean-clone/data-sharing rehearsal is certified.

Fresh QA commands:

```sh
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python -B -m pytest tests/test_real_bridge.py tests/test_pretraining_candidate.py tests/test_neural_engine.py tests/test_hourly_proxy.py tests/test_labels.py -q
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
.venv/bin/ruff check .
git diff --check
```

On another machine supply its matching installed Pylance distribution; keep basic severity and repository interpreter. Human editor Problems refresh is still human-confirmed.

Read-only audit: load journal with `lstm_data.real_bridge_run.journal_rows`, replay `neural_lifecycle.EarlyStop.observe` on the14 recorded inner-validation MSE values, verify14/4 trace counts and602/188 steps, load both checkpoints with `torch.load(..., map_location="cpu", weights_only=True)` and verify their manifests. No optimizer step or prediction recalculation is needed. Effective G6 also examines every calibration and refit `gradients.sustained_clipping_warning`; its warning addendum supersedes the raw runner's incomplete PASS summary. Small per-origin metrics and recorded session loss shares are already in the result.

Local-use and shared-clock approvals are researcher-attested per the actual privacy instruction; no private email contents are present. Source/data/checkpoint transfer is not separately licensed or authorized by this packet. Canonical registry/journal and both authority/result inventories must travel together through any later legitimate handoff.
