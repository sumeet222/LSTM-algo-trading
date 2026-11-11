# Codex Session Report

## 1. Session metadata

- Authorization: current owner V5 prompt, following 2026-11-09 research approval; no RSA or renewed generic permission required.
- Session spans 2026-11-09/10 America/New_York. Exact start UTC in audits/H0_PROTECTED_V5.json; final time/result in final manifest.
- Branch: feat/track-a-data-intake; starting HEAD: 8061483cb65d03264a7836b8b882123f67cbe4ad. No commits/pushes authorized or performed.
- Starting tree: pre-existing untracked replication, trading code/tests/docs and previous reports; preserved. Git fetched; upstream0ahead/0behind. No pull/reset/stash/rebase/clean.
- Task: general next-valid observed-bar policy, full engineering certification, authorized exploratory four-arm2021–2024 study only after mandatory gates.

## 2. Executive summary

STAGE35_V5_FINANCIAL_BACKTEST_COMPLETE_EXPLORATORY. Actual24/24 sealed cases (baseline +23 variants), each1005 sessions/140280 calendar opportunities/eight independent arm-population accounts, completed and reconciled. Fresh tests255/Ruff/owned-types pass; global30 inherited diagnostics remain. Final integrity:10410protected objects +227source partitions SHA/mtime unchanged. No Stage6 audit, model/source change, live/paper trading, post2024price or performance-driven tuning. The additive V5 policy resolves the V4 AVGO missing-minute mismatch without inventing a bar, broker cancellation, trade-print open or source value. All five current-code historical pilots and the pre-June9restart pass. The source-bound original cached forecasts/control/reference artifacts are reused. The funded baseline and all frozen variants are now complete; no incomplete run is presented as a headline result. No Stage6 independent audit, model refit, live/paper order, post2024market price or strategy optimization.

## 3. Research/protocol impact

Only the owner-approved execution convention changes: a previously standing modeled order awaits the actual next valid RTH opening bar, retaining original submitted quantity/prior-volume capacity and endpoint. Entry effective time<=nominal+10wallminutes; later expiry is explicit simulation nonfill, not broker cancellation. Exits have no entry expiry; inventory, carry, claims and reservations persist. V4 strict-minute artifacts remain unchanged/NOT_COMPARABLE if unresolved. Same four original annual models,20survivors,48x16FT16+10CLOCK, own O1recipe/C3, five-session signD[-1]/D[-6], seven valid origins,240scheduled-minute target, fixed cohorts,2019sizing reference, caps, costs, academic borrow and24sealed scenarios. Same100000USD initial independent accounts, both matched/attainable, continuous across annual model switches. No final-period tuning or neural training.

## 4. Files created

Reusable Python modules/tests:

- `src/lstm_data/trading/track2/stage35/final_backtest_v5/__init__.py`: bounded additive package.
- `src/lstm_data/trading/track2/stage35/final_backtest_v5/analysis.py`: gated descriptive complete-ledger reporting; no Stage6 inference.
- `src/lstm_data/trading/track2/stage35/final_backtest_v5/book.py`: unchanged V4 accountant subclass with policy tag in every hash-chain event.
- `src/lstm_data/trading/track2/stage35/final_backtest_v5/checkpoint.py`: explicit typed deterministic gzip snapshots and producer-bound restart.
- `src/lstm_data/trading/track2/stage35/final_backtest_v5/driver.py`: additive next-valid replay and scoped action integration; no frozen source edits.
- `src/lstm_data/trading/track2/stage35/final_backtest_v5/execution.py`: pure causal standing-order disposition and entry expiry.
- `src/lstm_data/trading/track2/stage35/final_backtest_v5/paths.py`: project-relative V5 namespace and immutable publication helpers.
- `src/lstm_data/trading/track2/stage35/final_backtest_v5/protocol.py`: immutable approved economic grid and V5 policy verification.
- `src/lstm_data/trading/track2/stage35/final_backtest_v5/release.py`: owner-authorized hash-bound research admission, current tests/pilots, no RSA/force.
- `src/lstm_data/trading/track2/stage35/final_backtest_v5/run.py`: gated pilot/baseline/scenario CLI and preserved runtime failures.
- `src/lstm_data/trading/track2/stage35/final_backtest_v5/special.py`: exact signed virtual OGN allocation in attoshare units; unchanged physical terms.
- `src/lstm_data/trading/track2/stage35/final_backtest_v5/witness.py`: actual pre-AVGO checkpoint replay and raw-bar forensic extraction.
- `tests/track2_stage35_v5/test_next_valid_execution.py`: research-critical regression test

New configuration/docs/evidence under trading/track2/stage35/final_backtest_v5: execution_policy_v5.json, EXECUTION_POLICY_NEXT_VALID_BAR_V5.md, FINAL_CONSOLIDATED_PROTOCOL_V5.json +seal, BACKTEST_SCENARIO_GRID_V5.json, SOURCE_ACCESS_PLAN_V5.json, SPECIAL_ALLOCATION_ARITHMETIC_V5.json, V4_TO_V5_EXECUTION_DELTA.md, AVGO_2021_06_09_V5_ORDER_RECONCILIATION.md, OGN_ROUNDING_CORRECTNESS_DELTA_V5.md, source/pilot/release/test/coverage/final reports. Complete individual file/hash inventory will be in the V5 child manifest rather than thousands of repeated run rows here. .gitignore excludes large local pilot/baseline/sensitivity outputs. Command reproduction helpers under audits are receipts for gated CLI orchestration, not alternate finance implementations.

## 5. Files modified

No pre-existing original/Phase2/Phase3/Stage012/V1–V4 bytes changed. Intentional iterative fixes confined to new V5 files. Exact pre-correction code/test bytes5899f5a9865c archived under audits/code_archive/ with hashes. FinancialR1was preserved at its104completed sessions throughJune2; its spinoff assertion was not suppressed. New V5 source-only precision correction is versioned and requires fresh tests/pilots/release. Legacy tests may append new denial receipts in old audit directories; no old receipt overwritten.

## 6. Files deleted, renamed, or moved

None. No raw partition, previous code/model/audit, unknown untracked work or prior failed output removed.

## 7. Critical functions, classes, variables, config keys

- execution.disposition(Order,start,received,lag,valid_bar): no price or fill-bar volume input; WAIT/EXECUTE/EXPIRE only with standing-order and completed/received clocks valid.
- Driver.attempt/expire: use actual later raw bar time/price, preserve pre-event requests and capacity, include missing attempts and source hashes; expire only after last eligible receipt; retain exit quantities and new prospective exit requests. Known pending nonfill alone does not erase known marked inventory.
- Account: inherits exact physical/virtual/cash/cost/claim/borrow invariants from V4; policy variant added before journal hash. Physical net shares=sum virtual shares. No internal exchange fees, no duplicated short cash, frozen held cohorts.
- distribution/cross_exact/settle_whole:1:10signed MRK/OGN remains; virtual share allocation uses integer1e-18share units and stable residuals. Whole physical external shares, exact cash/fees; no tolerance weakened. Source/bar/cost/tax terms unchanged.
- Driver.checkpoint/restart: every daily state, lossless deterministic zero-mtime gzip, atomic write, checksum, producing-code fingerprint; changed-code state cannot silently resume.
- create_release/check_admission: recompute protected hashes/mtimes, source/control/protocol/env/code/test bindings, live witnesses, all5historical pilots and actual restart. No force/env/status-flag bypass. A known failed same-code baseline blocks financial admission.
- run.financial: preserves/raises invariant failures and closes partial journals; no headline metrics for incomplete/unresolved run. Sensitivities require a sealed complete baseline.
- analyze: descriptive daily portfolio/annual/paired outcomes and source journals;255test receipt/code bindings guard entry. No cluster/bootstrap/null/Stage6 inference.

## 8. Data/schema/provenance changes

No new external market acquisition; existing raw canonical before adjust_prices +sealed V4exact-gap supplement used read-only. Source plans remain2021–2024and calendar geometry beyond only. Original48OOSminute partitions within227source receipts; original counts140280opportunities/131111forecasts/9169unavailable/128192EQ-S2Ccandidates/87557matched reused. Source cells7813800:7714752valid/99048missing-invalid;88674recoveredV4bars;10374residualholes are classified against actual orders, not treated as input-universe filtering.

AVGOJune9intended16:33UTC absent. Conditional V5 uses genuine16:34UTC raw464.965, externally adverse sell464.50and1USDfee per order. Fresh June pilot signed requests-2/-3 change physical-8→-10and-10→-13; expiry16:40, posting16:37. Actual pre-June9checkpoint replay byte-equal in uncompressed events/daily/cohorts. Source row/partition hashes in sources/AVGO_NEXT_BAR_SOURCE_WITNESS_V5.json.

Unchanged action confidence:267cash events(16supported/251single-provider observed),3splits,8verified-zero and8unknownsecurity-years; no confidence promotion. MRK/OGN primary terms, actual842OGNbars, conditional CILprice/date and signed liabilities retained. Unknown AMD/AMZN basezero-recorded events plus standalone0/1.5/3%yield sensitivity never double-paid with observed events. No2025prices;2025known pay metadata for2024claims retained.

## 9. Dependency/environment changes

None. Existing .venv; no install, account, credential or paid data. Environment versions bound to V4ENVIRONMENT_V4.json; owner research release binds current package/Python build. Machine-relative project paths. Source/API requestsV5=0; Git fetch separate. New environment must rebuild and certify its own compatible release; no portability rehearsal claimed.

## 10. Commands and tests run

```sh
.venv/bin/python -m pytest tests/track2_stage012 tests/track2_stage35 tests/track2_stage35_completion_v2 tests/track2_stage35_completion_v3 tests/track2_stage35_v4 tests/track2_stage35_v5 tests/test_hf20_s2c_ca.py tests/test_hf20_mag_c3_io.py -q
.venv/bin/ruff check src/lstm_data/trading/track2/stage35/final_backtest_v5 tests/track2_stage35_v5 --select E,F,I
.venv/bin/pyright src/lstm_data/trading/track2/stage35/final_backtest_v5 tests/track2_stage35_v5 --pythonpath .venv/bin/python --outputjson
.venv/bin/python -m lstm_data.trading.track2.stage35.final_backtest_v5.run pilot --version pilot_v5_r3
.venv/bin/python trading/track2/stage35/final_backtest_v5/audits/EXECUTE_FROZEN_SUITE_V5.py.txt
```

Initial unchanged baseline234PASS. Final code9e093b3f6a62:255PASS, Ruff E/F/Iclean,13owned files0errors/0warnings. Full installed Pylance basic694files:30errors =27frozen replication +3pre-existing unmodified Plotlyviewer-test errors,0newV5errors/0warnings. Earlier full attempt reported27; all receipts retained. No globally clean claim, no suppressed diagnostics or skip/XFAIL. Exact installed-dist command stored POST_OGN_FULL_TYPE_COMMAND_V5.json; resolve locally rather than copy developer absolute path. Editor select .venv/basic,restart Pylance/refresh Problems; human UI verification pending.

## 11. Experiment/results summary

All24 cases completed. Matched final NAV from $100000: EQUAL $2222.13; ROLLING $1840.62; EWMA $2008.24; S2C $1926.90. All baseline net returns are around -97% to -98%; S2C has no consistent useful incremental benefit. Full scenario/annual/cohort/cost/exposure tables are linked from the final handoff. Owner-approved exploratory research only. All5current-code source pilots+preAVGOrestart PASS,26sessions/3580calendar opportunities/eight accounts; maximum residual below1e-8. Earlier R1full baseline completed104sessions then failed repeating-Decimal OGNassertion; exact faulty inputs/oldcode preserved. Correction reproduces/fixes four failing classical-arm population cases without market-return fitting. Recoverable earlierR1prefix matches522866event/832daily/89663cohortrows; oldcrashgzipendmarker absent, preserved unrepaired, never used as complete performance result.

## 12. Reproduction instructions

Use repository .venv and documented authorized local models/source/cache. Run from project root. Source plans/manifests list exact files/bases; no PYTHONPATH or developer path required. Run tests then fresh unique pilot/release versions. Current producing-code snapshots only; never rename oldfailed state asnew. Official gatedCLI supports baseline/sensitivities; fixed suite orchestrator launches baseline first, then23additional predetermined variants, up to8independent processes/accounts with disk checks. No force/signature/newchat needed when substantive gatesPASS. Old strict mode remains diagnosticNOT_COMPARABLE.

## 13. Git / collaboration status

Branch/head unchanged from H0; remote fetched,0/0ahead/behindatstart; no commits/pushes/pulls/merges/stashes/deletions. Prior untracked work preserved; new V5source/tests/docs/report remain uncommitted. Do not blanket-add large local/vendor outputs. Review small code/config/metadata and include this report in a future focused commit/PR. No Stage012/frozen repair requested.

## 14. Known issues, risks, limitations

Fixed survivors, retrospective action/QA/provider vintages, assumed latency/borrow/funding/spread/impact, no NBBO/actuallocates/brokercancellations, nominal magnitude target vs delayed economic holding. Initial100000 and whole shares/order minima can materially affect investability/idle cash; not optimized after results. V4strict cannot yield valid whole-study performance when unresolved. Stage6independence absent. Fullglobaltyping qualification remains. Journal attribution/physical cash presentations are two views, not duplicate cash legs; marked daily valuations are the certified performance series. Interim transaction-leg rows must be grouped correctly for an independent event-level ledger reconstruction.

## 15. Decisions requiring review

No renewed generic financial approval or RSA credential required. Owner V5policy alreadyauthorizes nextvalidsimulatedbar. No future agent may change risk/alpha/cost/source parameters based on these outcomes. Any new material source/price/accounting failure requires explicit evidence and versioned correction, never dropped trades or invented marks. Independent Stage6audit remains separately scoped.

## 16. Next recommended steps

The frozen study is complete. Next work is separately authorized Stage6 independent verification, not rerunning or tuning this study. IndependentStage6should recompute ledger/actions/fees/borrow, verify source/PIT and code/data hashes, test dependence/selection/nulls/walkforward/prospective confirmation. No live deployment follows from this study.

## 17. Artifact inventory

V5child manifest will enumerate every new code/config/test/doc/source witness/audit/release/run output with hashes,self-exclusion. Large runjournals/checkpoints and vendor data staylocal/ignored with reproducible identities; no duplicate historical dataset. No new learned checkpoint, training artifact, option-chain, broker account or signed approval key. Actual final run/status/report paths will be appended below.


## Final actual outputs and recovery frontier

STAGE35_V5_FINANCIAL_BACKTEST_COMPLETE_EXPLORATORY. Actual24/24 sealed cases (baseline +23 variants), each1005 sessions/140280 calendar opportunities/eight independent arm-population accounts, completed and reconciled. Fresh tests255/Ruff/owned-types pass; global30 inherited diagnostics remain. Final integrity:10410protected objects +227source partitions SHA/mtime unchanged. No Stage6 audit, model/source change, live/paper trading, post2024price or performance-driven tuning.

Native master: `trading/track2/stage35/final_backtest_v5/BACKTEST_RUN_MANIFEST_V5_9e093b3f6a62.json`; SHA256 `7dfa9eb90ec546101c170b8d67f8763c059ac403a16052e66aedf12c060c241b`. Final report: `STAGE35_V5_FINAL_HANDOFF.md`; scenario tables: `presentation/FINAL_TABLES_V5/`; annual costs/exposures/holding times and identity checks: `presentation/ADDITIONAL_DESCRIPTIVE_TABLES_V5/`; standalone chart `presentation/BASELINE_NET_NAV_FINAL_V5.html`. Existing earlier chart preserved; consistent colors only. Recovery final handoff/manifest live in `recovery/20261110T124734Z/`. Child manifest self-excludes its own bytes/seal and binds the report/code/config/tests/results.

No commit/push. Git status remains pre-existing untracked project work plus new V5 source/tests/docs/results metadata and two session reports; no tracked-file diff. Do not blanket-add local vendor/journal/checkpoint data. Recovery read-only inventory verified the original jobs; only three resource-paused workers received SIGCONT in free slots, original guard resumed the last. No new financial job, state-level resume, account reset or scenario restart during recovery.

Final exact report commands (no finance rerun):
```sh
.venv/bin/python trading/track2/stage35/final_backtest_v5/recovery/20261110T124734Z/VERIFY_NEW_COMPLETIONS.py.txt
.venv/bin/python trading/track2/stage35/final_backtest_v5/audits/VERIFY_FINAL_IDENTITIES_V5.py.txt
.venv/bin/python trading/track2/stage35/final_backtest_v5/audits/BUILD_FINAL_RESULT_TABLES_V5.py.txt
.venv/bin/python trading/track2/stage35/final_backtest_v5/audits/ADDITIONAL_DESCRIPTIVE_TABLES_V5.py.txt
.venv/bin/python trading/track2/stage35/final_backtest_v5/audits/ASSEMBLE_FINAL_HANDOFF_V5.py.txt
.venv/bin/python trading/track2/stage35/final_backtest_v5/audits/FINALIZE_DOCUMENTATION_AND_INDEX_V5.py.txt
```
