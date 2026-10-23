# Codex Session Report

## 1. Session metadata

Package021B: read-only seed42 T2 transformed-objective tail attribution and20exact top-loss cases. Date 2026-10-23T02:19:55.617872-04:00. Branch feat/track-a-data-intake; starting/ending HEAD c8a7024a04e0febbbb4b2ebf20827dc3e0ef78e7. Existing untracked P021A script, session report and private report ignore policies preserved. Upstream0/0 after fetch. No issue/PR/commit.

## 2. Executive summary

Completed transformed-space cohort tables, both percentile-level four-way mechanism decompositions and within-tail cross-tabs; exactly5highest weighted transformed-loss events each AAPL/AMZN/TSLA/SBUX. All20 detailed operand tables in main report and20complete52-row exact candle windows in annex (1040candles,400genuine endpoint-return rows). New authoritative private namespace: reports/experiments/ta021_hf1m_long_four_lstm_2026-10-22_232248_recovery_v1/p021b_transformed_tail_2026-10-23_final/ (P below). First same-date namespace is preserved preliminary output.

Weighted final-checkpoint z-MSE1.3240155222676186; unweighted1.3265117236294104. Original-target top1/5% contribute7.1633702441231355/24.377260354794917%weighted z-loss,7.206767613964785/24.525469122376386%unweighted. Numerator top1/5%:5.479369392249402/20.27931076900692%weighted,5.65422287262995/20.764820012823492%unweighted. MAD smallest1/5%origins:1.2408077066764613/6.3083652916806665%weighted,1.2581098264135748/6.089446911939286%unweighted. Matching intersections:.02075951698901236/.7327945968422918%weighted,.023703242794503608/.7139816382454365%unweighted. Neither dominates total transformed objective at both declared percentile thresholds; conditional concentration and tail membership are separate quantities.

## 3. Research/protocol impact

No model training/refit/inference, optimizer steps, gradients, data acquisition/repair, dashboard change, parameter selection, backtest or2026 numerical access. Ledger36/200 unchanged. Only fixed final7epoch refit checkpoint HF1M-LONG-TM0-T2-S42-DEV1. This is final-checkpoint in-sample eval/dropout-off loss, distinct from historical online changing-weight/dropout-active optimization. Existing frozen protocols/P019B/P020/P021/P021A untouched; P2 deferred register verified16entries.

## 4. Files created

scripts/p021b_transformed_tail.py: deterministic producer using sealed source-only LongStudy, saved raw-z outputs, float64 transforms and weighted losses, exact stable ranks and unique-origin MAD ranks, disjoint cross-tabs, NumPy rank/sum oracles, exact20source windows and private report writer. No new dependencies or source imports for training execution.

P contains P021B_T2_S42_TRANSFORMED_TRAINING_TAIL_ATTRIBUTION.md, P021B_T2_S42_TOP20_EXACT_CANDLE_ANNEX.md, P021B_HUMAN_REVIEW.md; requested Section1/Section2 cohort/cross-tab/error-ranked CSVs; top20_loss_events.csv, top20_exact_hourly_candles.csv, top20_all_stock_forward_returns.csv; distribution_compression.csv; preflight.json, objective_reconciliation.json, independent_verification.json, NO_RETRAINING_AND_PROTECTION_RECEIPT.json; release_independent_checks.json, types_release.json, focused_tests.txt and final inventory/receipt. Nested .gitignore keeps every numerical artifact private while exposing only the ignore policy. Preliminary namespace retained; this session report is additional Git-safe aggregate handoff.

## 5. Files modified

No pre-existing tracked/source/model/report/registry file modified. Existing untracked P021A also unchanged. New final report headers explicitly label legacy original-TG20 error context; this presentation-only clarification changed no numeric value. Producer mirrors those column names. New final metadata includes exact entry/exit prices/source IDs, ET/UTC clocks and input quality/fallback counts.

## 6. Files deleted, renamed, or moved

None. Earlier P021B preliminary outputs preserved. No raw or model files overwritten.

## 7. Critical functions, classes, variables, and config keys

analyze(out: Path) requires new output directory; verifies source/checkpoint/prediction identities,20-name order,104200unique rows/5210origins/2980days. Native saved raw_net_output is z_hat; residual=z-z_hat, loss=residual², wl=w*loss. stats reports global weighted/unweighted contribution and subgroup-renormalized MSE/RMSE. Stable ranks use origin/canonical-stock ties; MAD ranks unique origins then expands20stocks.20cases selected w*loss descending, raw loss descending, origin ascending. All20return-vector/candle reconstructions independently verify original r/median/MAD/y/z and transformed loss/weights.

## 8. Data/schema/provenance changes

None upstream. Pinned mito0o852/OHLCV-1m revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56, P019B adjusted source→P020FT16/TG20/model contract7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5. s/epsilon loaded from refit recipe; checkpoint/prediction SHA and exact dates in preflight.json. Source masks/time grid preserve48full-hour input steps+4outcomes and explicit overnight breaks; closing stubs are outside model/target. All20entry/exit closes genuine. Price-adjusted/report-share-volume units, missingness, feature-only assumed-zero volumes, proxy/quarantine flags remain explicit. No protected numerical file decoded.

## 9. Dependency/environment changes

None. Existing .venv Python, pandas/NumPy/Arrow and sealed readers. No credentials/.env reads. Project-relative/config-bound implementation. Local Pylance path is verification tooling only.

## 10. Commands and tests run

- git status --short --branch; git branch --show-current; git rev-parse HEAD; git remote -v; git fetch --all --prune; upstream0/0. Dirty prior P021A preserved. No index/integration operations.
- .venv/bin/python scripts/p021b_transformed_tail.py --out reports/experiments/ta021_hf1m_long_four_lstm_2026-10-22_232248_recovery_v1/p021b_transformed_tail_2026-10-23_final: PASS_IDENTITY, PASS_OBJECTIVE_RECONSTRUCTION, PASS_TAIL_ATTRIBUTION, PASS_EXACT_CANDLES, PASS_REPORT_COMPLETENESS. Preliminary output also preserved. Full aggregate MSE/ZERO context matches P021; transformed loss independently equal-day averaged.
- Independent NumPy lexsort reproduces all target/numerator/MAD ranks and separate dot products reconcile sums; monotonic |y|/|z| cohorts exactly equal. Scalar source replay all20cases passes; separate release verifier reproduces each stock's weighted top5, all cross-tab100% totals and20MDoperand/annex sections.
- .venv/bin/python -m pytest tests/test_hf1m_long_visualization.py -q:17passed26.56s. Includes protected-date and identity negatives. No slow full suite.
- .venv/bin/ruff check scripts/p021b_transformed_tail.py: passed after new-script formatting/unused variable cleanup. git diff --check passed.
- Exact static command: .venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist.306files,0errors/0warnings (exact final JSON P/types_release.json). No suppressions/exclusions/severity changes. Human editor verification: select repository.venv/bin/python, restart Pylance, refresh Problems and confirm0project errors. CLI parity passed; editor state not asserted.
- Benign Arrow sandbox sysctl/NEON probe warnings; no numerical failure. No training/retry/download.

## 11. Experiment/results summary

Read-only analysis, no new experiment. Primary transformed squared loss, not P021A original-scale error. Exact weighted/unweighted shares for targets, numerator, unique-origin MAD, intersections/unions, complements and disjoint classes are in the final tables. Top |z|=asinh(|y|/s) is strictly increasing, so top1/top5 memberships are identical. MAD1% selects52origins1040rows; MAD5% selects260origins5200rows, floor topK with threshold-based counts separately recorded. Neither class carries most total z-loss; large-numerator cohorts have greater loss concentration per row but are much smaller. No causal/predictability/gradient claim.

## 12. Reproduction instructions

Use documented repository .venv and legitimately provisioned exact P019B/P020/P021 private stores. Execute the analysis command above with a NEW directory. Source/model files are never fitted or modified. Open P main report then all20annex case links; no dashboard interaction required. Final original-scale legacy error context headers are explicit and numeric content unchanged. Missing source/identity/count mismatch stops rather than falls back.

## 13. Git / collaboration status

Branch/SHA unchanged, upstream0/0; no Git staging/commit/push/merge/rebase. Pre-existing P021A remains untracked. New P021B script, ignore policies and this report untracked; private exact MD/CSV/JSON ignored. No current registry/anomaly register edits. Review only producer/ignore/session metadata for any future separately authorized commit; never include exact private candles/reports by default.

## 14. Known issues, risks, and limitations

Fixed final-checkpoint loss is not historical online training loss. Same mathematical session objective but optimizer uses shuffled minibatch updates/dropout; short last batch affects update weighting. asinh compresses magnitudes without altering observed returns. Threshold flags are ex-post diagnostics; high loss does not establish tradability/learnability. MAD shared across20stocks. Fixed cohort survivorship and conditional private rights/publication/action/dividend/volume assumptions persist. No failing focused/static check; editor refresh human. Exact prices are stored source values, no screenshot estimates/interpolation. No new resource-heavy data copies; only compact1040candles/400returns and reports.

## 15. Decisions requiring human or teammate review

No further approval needed for this task. Any training, new experiment, source sharing/publication or confirmation access requires separate scope/rights/budget. No automatic model or improvement selection.

## 16. Next recommended steps

Read executive transformed-space shares, inspect the Section1 four-way tables and raw-vs-transformed rank identity, then the20exact weighted-loss cases. Compare to P021A only with explicit original-vs-transformed loss distinction. Preserve36/200ledger and immutable source/model artifacts.

## 17. Artifact inventory

P/artifact_inventory.csv contains producer, session report and both new output namespaces, bytes/SHA256/purpose/Git intent; excludes itself and final_receipt.json. Final receipt binds inventory/report/static evidence. Existing P021/P021A/source/model/registry files are pre/post hashed in NO_RETRAINING_AND_PROTECTION_RECEIPT.json and checked again at release. No sharing authorization inferred.
