# Codex Session Report

## 1. Session metadata

- Recovery inventory time: 2026-11-10 12:47 UTC; owner-reported transport disconnect.
- Task: read-only safe-state inspection, preserve active V5 study and continue only from verified state.
- Branch: `feat/track-a-data-intake`; starting/unchanged HEAD `8061483cb65d03264a7836b8b882123f67cbe4ad`.
- Pre-existing untracked replication, trading code/tests/docs and reports preserved. Tracked diff empty. No commit/push/pull/reset/stash/clean, kill or replay restart. A later bounded SIGCONT continuation is documented below.
- Dedicated recovery namespace: `trading/track2/stage35/final_backtest_v5/recovery/20261110T124734Z/`.

## 2. Executive summary

Recovery case A: the original orchestrator PID 61526, four running workers, four intentionally resource-paused workers and the existing resume guard PID 62477 remained alive. Logs/checkpoints advanced during inspection. No duplicate backtest, pilot, source acquisition or model inference was launched. At the independently verified inventory snapshot: 8/24 scenarios complete, 8 active (including four paused), 8 queued. This is not yet a complete study. Final actual completion status will be linked in the recovery handoff; no transport error was relabeled a scientific/data failure.

## 3. Research/protocol impact

None. Existing owner-approved V5 next-valid-observed-bar policy, four original models, 20 survivors, 2021–2024, frozen signs/controls, fixed horizons, budgets and cost/borrow/action assumptions unchanged. The sealed grid is 24 total scenarios including baseline; no twenty-fifth scenario was invented from ambiguous continuation wording. No RSA/external signer or renewed owner approval required when actual substantive gates pass. No Stage 6 audit, tuning, live/paper orders, 2025+ prices or neural fitting.

## 4. Files created

- Recovery inventory JSON and Markdown: exact process identities/states, last sealed checkpoint cursors, all 24 statuses, independent completed-output hash checks, prior evidence/protocol authority and next safe action.
- Recovery command stdout/stderr and machine-readable validation receipts: fresh unit/Ruff/type checks without altering original engineering receipts.
- This session report, and later additive progress/recovery handoff manifests. Individual exact files/hashes belong to the final recovery manifest.

## 5. Files modified

No existing execution code, config, source, model, V4/V5 sealed evidence or financial output was modified for recovery. Active processes continue writing their own previously authorized outputs. Recovery-only documents/status receipts are additive. Earlier V5 implementation work is recorded in `2026-11-10_track2_v5_next_valid_bar.md`.

## 6. Files deleted, renamed, or moved

None. Open journals, old failed attempts, checkpoints and untracked collaborator work preserved.

## 7. Critical functions, classes, variables, config keys

No public interface changed. Existing `fingerprint`, `protected_files`, typed checkpoint `unseal`, original completion-receipt file hashes and last-session receipts were used read-only. All execution source/tests still match fingerprint `9e093b3f6a62`. Existing live workers are owned by the same parent and source/version definitions; no guessed state resume or journal concatenation.

## 8. Data/schema/provenance changes

None. SHA256 and mtime verified for 10,410 protected objects and 227 source partitions; zero discrepancies. Completed scenario receipts verify every bound output, 1,005 sessions, 140,280 opportunities, eight accounts, no terminal pending/unpriced/incomplete state and maximum balance residual <=1e-8. Active compressed journals remain incomplete/open and were not treated as complete. Sealed daily checkpoints are checksum-valid and retain cursor, accounts, carry/actions, reservations and producer identity.

## 9. Dependency/environment changes

None. Existing `.venv`, existing installed Pylance distribution resolved locally. No package install, credential, external market request or source download. OS process/open-file inspection was read-only and limited to owned V5 processes. After 17 cases completed and a fresh PID/queue check showed only three computing workers, SIGCONT resumed existing paused PID 62148 at 2026-11-10 15:58:47 UTC. The maximum remained four computing workers. This was a resource continuation, not a new backtest or account restart; code/config/source/cash state unchanged. The original guard was not edited. Exact before-state, stable PID selection and authorization are in FREE_COMPUTE_SLOT_DECISION.json and RESOURCE_PROGRESSIVE_RESUME_62148.json.

## 10. Commands and tests run

Read-only: `pwd`, Git status/branch/HEAD/diff-stat, scoped `ps` and `lsof`, original V4/V5 policy/blocker/report reads, protected SHA/mtime, checkpoint checksums and completed-output hashes. The predecessor prompt file was absent; full owner instructions remain in conversation and sealed V5 protocol, not inferred from a missing file.

Fresh recovery regression command:

```sh
.venv/bin/python -m pytest tests/track2_stage012 tests/track2_stage35 tests/track2_stage35_completion_v2 tests/track2_stage35_completion_v3 tests/track2_stage35_v4 tests/track2_stage35_v5 tests/test_hf20_s2c_ca.py tests/test_hf20_mag_c3_io.py -q
.venv/bin/ruff check src/lstm_data/trading/track2/stage35/final_backtest_v5 tests/track2_stage35_v5 --select E,F,I
.venv/bin/pyright src/lstm_data/trading/track2/stage35/final_backtest_v5 tests/track2_stage35_v5 --pythonpath .venv/bin/python --outputjson
```

255 tests PASS in 190.72 seconds under concurrent authorized financial work. Ruff PASS. Owned basic types 13 files / zero errors / zero warnings. Fresh full-project installed Pylance: 694 files, 30 errors, zero warnings, 436.543 seconds. Diagnostics are identical to the prior check: 27 frozen replication plus three pre-existing unmodified Plotly viewer-test diagnostics; zero added diagnostics. It must not be called globally clean. No skip/XFAIL/suppression or frozen repair. Exact resolved full-type argv and return code belong to `RECOVERY_VALIDATION_COMMANDS.json` when finished.

## 11. Experiment/results summary

No new financial experiment was started by recovery. The existing study continued; eight cases were independently verified complete at G0, with the remaining queued/active. Completed baseline results exist under `BASELINE_FOUR_ARM_RESULTS/baseline_v5_r2/`; they are exploratory and strongly negative. Partial running journals are not aggregate financial results. The initial failed `baseline_v5_r1` remains preserved separately and is not counted among current-grid completed cases.

## 12. Reproduction instructions

Read the new recovery inventory first. Inspect actual PID/command identity and fresh logs before attempting any runner command. If PID 61526 still owns live workers, observe rather than launch a duplicate. Reuse completed receipts; verify their hashes and terminal state. If stopped, inspect the typed checkpoint/restart contract, producer/source bindings and committed journal frontier before any new immutable recovery run. Never reset cash or concatenate divergent histories. The existing suite script continues baseline then the fixed remaining cases automatically; no new run command is required while it lives.

## 13. Git / collaboration status

HEAD/branch unchanged; all old untracked/dirty work preserved. No commits, pushes, merges, stashes, checkout or destructive commands. The original session fetched remote and reported 0 ahead/behind at that fetch; recovery did not integrate remote work. New recovery report/status files are uncommitted. Review only intended small source/config/metadata for a future focused PR; large proprietary journals and payloads remain intentionally local/ignored.

## 14. Known issues, risks, limitations

Full study pending until all 24 actual cases and reconciliations finish. Four workers are deliberately paused by the prior resource plan, not failed; guard must resume them and final status must confirm this. A transport disconnect alone says nothing about financial validity. Ordinary-action confidence, conditional locates/costs/latency/CIL, survivor/retrospective bias and repeated-use period remain. Global repository diagnostics remain qualified. No assertion of independent significance or deployment readiness.

## 15. Decisions requiring review

No renewed generic research approval or RSA required. Any actual material source/causal/accounting failure still blocks affected performance. Do not tune financial parameters from observed returns, change the grid, overwrite old receipts or treat process liveness as completion. Stage 6 is separately scoped.

## 16. Next recommended steps

Observe the existing run to a verified terminal state; independently verify newly completed scenarios and guard resumption. Create missing descriptive tables and final handoff from sealed results only. Perform final protected/source integrity and report exact completed/failed/not-run counts. If interrupted again, start with this inventory and current native process/log evidence rather than rerunning.

## 17. Artifact inventory

Recovery inventory and validation receipts: dedicated recovery namespace above. Original source/pilot/test/release/run evidence remains in the existing V5 tree. No new raw dataset, learned model, checkpoint recipe, broker account or signing key created. Final child/recovery manifests will bind new reports and existing completed outputs with explicit self-exclusion.

### Additional bounded resource continuations

At 2026-11-10 16:33:04 UTC, a fresh live-state check found only two computing workers after the joint-adverse and MRK restriction cases closed. Existing paused PIDs 62149 (`fee_0`) and 62150 (`fee_0.01`) received SIGCONT, in stable PID order; active count returned to four. No process/account was recreated and no source, protocol or execution code changed. The original guard is untouched. Receipts: `RESOURCE_PROGRESSIVE_RESUME_62149.json` and `RESOURCE_PROGRESSIVE_RESUME_62150.json` in the recovery namespace.


## Final actual verified frontier (2026-11-10T18:17:04.080353+00:00)

STAGE35_V5_FINANCIAL_BACKTEST_COMPLETE_EXPLORATORY. Actual24/24 sealed cases (baseline +23 variants), each1005 sessions/140280 calendar opportunities/eight independent arm-population accounts, completed and reconciled. Fresh tests255/Ruff/owned-types pass; global30 inherited diagnostics remain. Final integrity:10410protected objects +227source partitions SHA/mtime unchanged. No Stage6 audit, model/source change, live/paper trading, post2024price or performance-driven tuning.

Initial8/8/8 is the immutable recovery-time snapshot, not the final census. All original processes have now completed; no duplicate job or guessed state restart. Companion machine final recovery manifest enumerates all24 statuses and parent receipt SHA256. Final matched baseline NAV/returns and every adverse scenario are published without outcome selection. See `trading/track2/stage35/final_backtest_v5/STAGE35_V5_FINAL_HANDOFF.md`, immutable native master and both final presentation directories. The source/pilot/code/gate certificates and original failure history are retained. No new conversational/RSA approval is needed for the already authorized completed research; Stage6 remains separate.
