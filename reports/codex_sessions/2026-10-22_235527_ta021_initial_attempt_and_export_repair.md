# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-22T23:55:27.577135-04:00.
- Contributor/session: Codex, Package021 initial approved attempt and export-repair precheck.
- Task: four matched HF1M-LONG TM0 C0/T2 × seeds42/123 plus existing research explorer.
- Branch: feat/track-a-data-intake. Starting/ending HEAD: 47b7e7c2e1333f484a9b862bef00c7e81a323bcf; no commits.
- Start clean, upstream0/0 after git fetch --all --prune. Current task changes remain uncommitted.
- No issue/PR or Git index/push/integration action.

## 2. Executive summary

PARTIAL_TRAINING. One actual start charged32→33/200. C0/42 ran12calibration epochs,
1,896optimizer steps; selected epoch1, saved calibration checkpoint. Prediction export failed
because MultiIndex reset_index lost the ticker level name. FAILED_AFTER_START is preserved.
No refit or other start. Fixed serialization passed a full zero-step real export of88,560/15,320rows.
Separate concrete continuation proposal awaits a live response; original code/hash is preserved.
The new history/target/quality/guide dashboard routes are implemented and focused component-state
checks pass; model-dependent completion is pending. This report is an interim handoff, not final021PASS.

## 3. Research/protocol impact

Frozen FT16/TG20, source revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56, all20stocks,
48steps, splits, train-only recipes, AdamW/D6g/seed design unchanged. Original P2 deferred register
verified with load_deferred_work; no original scientific gate is cleared. The original live approval
bound proposal5b6cfd698f6fc741e42be799642f5f447bbe6b11e8c0fc06b34ab0bd6fe31803 and execution
4aca06f65c720783ab047cce5c22d03deae2f9e8bf11386094256764291de353. It cannot silently authorize
changed code or retry after failure. No2026numerical access, trading, legacy numerical reuse or newdata.
A linked registryv8 was activated at actual start33; v9 is only a proposed continuation definition.

## 4. Files created

- src/lstm_data/hf1m_training_data.py: source-only whole-session adapter and indexed batch parity.
- src/lstm_data/hf1m_training_authority.py: exactly4start, linked32prefix authority/journal validation.
- src/lstm_data/hf1m_training_run.py: frozen executor, checkpoints, predictions and epoch/gradient telemetry.
- src/lstm_data/hf1m_training_diagnostics.py: independent weightedZERO decomposition, dailyIC and groups.
- src/lstm_data/hf1m_training_recovery.py: proposed explicitly gated existing-start continuation; unexecuted.
- src/lstm_data/visualization/hf1m_long.py: allowlisted bounded history/target/feature/run readers.
- src/lstm_data/visualization/hf1m_long_ui.py: six read-only research subviews and actual click guide.
- scripts/prepare_hf1m_training.py: zero-step protocol precheck and sealed original proposal.
- scripts/update_hf1m_viewer_bindings.py: snapshot/additive reader binding update, numerical evidence invariant.
- tests/test_hf1m_training.py and tests/test_hf1m_long_visualization.py: research/authority/UI oracles.
- configs/track_a_candidate_experiment_registry_v8_p021.json and v9_p021_recovery.json: exact definitions.
- configs/track_a_hf1m_long_visualization_v1.json: isolated study binding.
- reports/audit/track_a_real_pairs_v8.jsonl: actual STARTED/CALIBRATED/FAILED_AFTER_START events.
- reports/experiments/ta021_hf1m_long_four_lstm_2026-10-22_232248: exact prompt, identity/prechecks/approval/design, progress/failure/repair receipts, review and snapshots.
- reports/experiments/ta021_hf1m_long_four_lstm_2026-10-22_232248_recovery_v1: concrete changed-code continuation design, pointer snapshot, precheck. No approval/fit.
- artifacts/hf20_hf1m_long_v1/ta021_hf1m_long_four_lstm_2026-10-22_232248: ignored calibration checkpoint/manifest and repaired inference-only stores.
- This session report. Detailed task artifact inventory remains to be sealed after continuation decision.

## 5. Files modified

apps/track_a_dashboard.py adds isolated HF1M navigation before legacy loading plus StartHere link.
configs/track_a_visualization_v1.json updates only app reader hashes and an additive compatibility note;
original bytes preserved in visualization_config_before_p021.json. All legacy data/model/scaler references
are invariant. configs/CURRENT_EXPERIMENT_REGISTRY.json now points to actualv8charged journal.
New code was iterated; approved executor bytes preserved before changing the exporter and adding explicit
authority injection for a separately approved continuation. No old numerical implementation changed.

## 6. Files deleted, renamed, or moved

None. No raw/unknown local work deleted or overwritten.

## 7. Critical functions, classes, variables, and config keys

TrainingView.origin_batch/batch gather20×48×16 indexed windows and pad absent origins within each
session only; canonical labels remain originalTG20 and LossPolicy applies asinh once. Equal-session
then equal-origin/stock loss matches the reviewed engine. epoch_pass measures original MSE/MAE and
pre/postclip distributions; objective units and online/dropout context are explicit. predictions keeps
raw network units and named origin_id/ticker join keys. run requires exact approved authority before
optimization; failed starts never refund. Proposed continue_first cannot rerun calibration and requires
exact saved checkpoint,12selected1trace and fresh42initial hash; only its187step refit is proposed.
LongStudy readers enforce date/role barriers before numerical access and exact allowlists; select_events
filters/sorts full populations before pagination, deduplicating smallestMAD origins. summary uses exact
matching weights for MSE−ZERO=p²−2yp; constant forecast IC is undefined. No weights enter dashboard.

## 8. Data/schema/provenance changes

No vendor/source changes. P020 all10private files and189parent hourly binary hashes verified; protected
files may be hashed but never decoded. Original P020 source/recipe hashes unchanged. New private forecast
rows are keyed by origin_id,ticker,run,seed,arm,phase,partition,fit_version and checkpoint SHA; original64
TG20 targets retained alongside float32 model outputs, once-inverted canonical predictions and errors.
The missing ticker export key is fixed and independently tested. Rights remain human-reported maintainer
permission for private research, not independent legal certification; clock/dividend/action limitations persist.

## 9. Dependency/environment changes

None. Repository.venv Python3.14.6/Torch2.10.0 CPU4threads; no workers, installs, environment secrets or.env reads.
No new external HTTP market-data requests. Native UI tool available only via Firefox; AppTest validates
actual component states. One existing dashboard process on8501; no duplicate server started.

## 10. Commands and tests run

- Git status/branch/HEAD/remotes and git fetch --all --prune: clean initial0/0, HEAD47b7e7c2e1333f484a9b862bef00c7e81a323bcf.
- .venv/bin/python scripts/prepare_hf1m_training.py --out reports/experiments/ta021_hf1m_long_four_lstm_2026-10-22_232248: zero optimizer steps, all counts/batch/T2/seed/params checksPASS;3.311s,651,886,592peakRSSbytes.
- .venv/bin/python -m lstm_data.hf1m_training_run --plan reports/experiments/ta021_hf1m_long_four_lstm_2026-10-22_232248/experiment_design.json --approval reports/experiments/ta021_hf1m_long_four_lstm_2026-10-22_232248/live_four_run_approval.json --run-id HF1M-LONG-TM0-C0-S42-DEV1: exit1 after12calibration epochs at export; no refit.
- Full read-only repaired export from saved checkpoint:88560/15320rows, exactsource targets, zero optimization.
- .venv/bin/python -m pytest tests/test_hf1m_training.py tests/test_hf1m_long_visualization.py -q:27passed in51.87s. Earlier test fixture relative app path failed and was corrected; earlier versions retained in temporary logs.
- .venv/bin/ruff check .: All checks passed after repair formatting.
- Exact static command: .venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist.303project files,0errors,0warnings,51.503s. Subsequent only string wrap pending final full recheck.
- ./scripts/run_track_a_dashboard.sh --check:900legacy dependenciesPASS before UI change; additive reader binding updated after browser exposed stale app hash. Recheck/final smoke pending.
- Actual AppTest states cover20tickers,16channels,4roles, all6views, fullrefit104200rows, dev3660rows, distinct smallMAD selection,48×16matrix and forced2026URL denial beforedata.
- Arrow sandbox sysctl cache/NEON probe warnings only; reads/tests completed. Native Firefox rendering exposed stale legacy app hash, now repaired with snapshot. Native complete final navigation unverified; use AppTest component evidence until final integration.
- ps initially denied in sandbox then approved native inspection found existing StreamlitPID33343 on8501.
- No100minute broad model suite. No unapproved neural step after failure.

Editor verification: select repository.venv/bin/python, restart Pylance, refresh Problems and confirm0project
error diagnostics. CLI parity passed; editor refresh remains human-confirmed.

## 11. Experiment/results summary

HF1M-LONG-TM0-C0-S42-DEV1 only:12calibration epochs, selected1, raw-best3,
selected original equal-session inner-validation MSE3.658381302112588; this is checkpoint
selection, not independent OOS.1896steps. Calibration checkpoint preserved; refit0steps; no development
model result or trading metric. T2/42,C0/123,T2/123unstarted. Do not label FOUR_RUNS or ledger36PASS.

## 12. Reproduction instructions

Use documented repository.venv and legitimate private P020 stores; no new credentials/provider. Clone/setup
must provision exact source manifests/contracts under their relative paths. Run the focused tests above.
Use existing dashboard launcher and HF1M Long navigation. Original failed executor is not rerunnable;
authority rejects changed code and immutable output. Read the recovery proposal for an exact separately
approved continuation. Do not fabricate approval files, fresh starts or rewrite the failed journal.

## 13. Git / collaboration status

Branch unchanged; no commits/staging/push/merge/rebase/reset. Protect all task untracked sources/configs/
reports and ignored checkpoint/inference stores before integration. Remote fetched at start, initially0/0.
Conflict surfaces: dashboard app and legacy reader config; active experiment pointer. Separate focused
review/commit/PR only if authorized; exclude ignored source/forecast/checkpoint data and secrets.

## 14. Known issues, risks, and limitations

Training is incomplete after a real charged failure. Repaired export and proposed continuation are ready
for a separate live response. Per-batch calibration telemetry was in memory and lost; epoch summaries and
selected checkpoint survived. No silent fitting replay. Full model comparisons, final UI metrics/gradient
artifacts, final smoke/static/inventory/resource/preservation receipts remain outstanding. Strict source
rights/publication/fill limitations persist. No model performance conclusion is supported by this partial run.

## 15. Decisions requiring human or teammate review

Approve or decline the exact proposed continuation from saved calibration, no recalibration and only3new
starts to36. Required because Package021 forbids silent retry after error and original live approval binds
an execution hash that has changed. The failure event and telemetry limitation must remain disclosed.

## 16. Next recommended steps

After exact live continuation approval, run existing-start33fresh1epoch refit, T2/42 and pairaudit, then
C0/123,T2/123 and pair/four-run audit. Finish original-scale diagnostics, model UI completeness, actual
component checks, launcher smoke, preservation/resources/inventory and a new final session report.
If declined, retain PARTIAL_TRAINING at33and all saved evidence; do not advance ledger or claim completion.

## 17. Artifact inventory

Public review metadata under reports/experiments/ta021_hf1m_long_four_lstm_2026-10-22_232248 and recovery_v1 is uncommitted. Detailed calibration checkpoint and
88560/15320repaired predictions are ignored/local under artifacts/. Source OHLCV/P020stores remain local
and unchanged. Full inventory and final closeout will follow the continuation decision. No final model,
newlabel/feature store, final confirmation forecast or P&L artifact exists.
