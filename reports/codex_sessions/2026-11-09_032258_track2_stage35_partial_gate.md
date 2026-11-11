# Codex Session Report

## 1. Session metadata

- Date/time:2026-11-09T03:22:58.584227+00:00;Codex root.
- Task:implement HF20 Track2 Stages3–5,synthetic economics and bounded source-only expansion;no historical financial authority.
- Branch:feat/track-a-data-intake;starting/ending HEAD8061483cb65d03264a7836b8b882123f67cbe4ad,no commit.
- Start dirty/untracked:replication/,both prior Stage012 reports,src/lstm_data/trading/,tests/track2_stage012/,trading/.All preserved.
- End:these prior files plus new Stage35 namespaces/tests/reports;no tracked predecessor diff or frozen byte changes.
- Git fetch --all --prune succeeded;upstream0 ahead/0 behind. No pull/merge/stash/rebase/push/PR.

## 2. Executive summary

STAGE3_5_PARTIAL_WITH_EXPLICIT_HOLDS. Additive strategy/risk/accounting/execution kernels and fail-closed human gate implemented.87 tests pass(52 preserved Stage012+26 Stage35+9 neural regression);Ruff E/F/I pass;full Pylance basic626 files has0 owned errors/0 warnings and27 inherited frozen-replication errors.16 real source-only signals/intents across4 original annual bundles;no historical orders/fills/positions/P&L. Synthetic books reconcile physical/virtual shares,cash,NAV and realization/basis under crosses/actions/costs. Historical raw/action/internal-reference/short/controls/due-event policies remain HOLD. No financial backtest was run.

## 3. Research/protocol impact

No neural fit/refit/calibration/weights/FT16/CLOCK/C3,target,horizon,universe,split or search change. Original annual models only;Phase2 never inference;Phase3 mismatch preserved. Stage012 frozen candidate2019 b/floor consumed,not refitted. New candidate EQUAL/rolling/EWMA/S2C kernels and gross/name/vintage/current-capital policy documented;unvalidated economically. New5min mark-age proposal corrects receipt-vs-staleness integration,explicit human review required. Caps,sign,clip,receipt2 and entry5min unchanged. No Stage6 statistical/financial audit or TrackA scientific gate cleared;P2 deferred register16 entries verified,unchanged. Dynamic resize disabled.

## 4. Files created

All paths below are new code/test/config/doc/receipt artifacts;source/weights not copied. Source modules implement typed kernels;test files cover synthetic invariants and bounded signal/provenance receipts;docs/configs define proposals/HOLD;audits retain commands,failures,integrity and source-only evidence. Manifest binds each purpose/path/hash/bytes.

- `src/lstm_data/trading/track2/stage35/__init__.py`
- `src/lstm_data/trading/track2/stage35/accounting.py`
- `src/lstm_data/trading/track2/stage35/arms.py`
- `src/lstm_data/trading/track2/stage35/borrow_financing.py`
- `src/lstm_data/trading/track2/stage35/common.py`
- `src/lstm_data/trading/track2/stage35/corporate_actions.py`
- `src/lstm_data/trading/track2/stage35/execution_clock.py`
- `src/lstm_data/trading/track2/stage35/execution_model.py`
- `src/lstm_data/trading/track2/stage35/gate.py`
- `src/lstm_data/trading/track2/stage35/intents.py`
- `src/lstm_data/trading/track2/stage35/internal_cross.py`
- `src/lstm_data/trading/track2/stage35/policy_config.py`
- `src/lstm_data/trading/track2/stage35/portfolio_allocator.py`
- `src/lstm_data/trading/track2/stage35/signal_expansion.py`
- `src/lstm_data/trading/track2/stage35/synthetic_smoke.py`
- `tests/track2_stage35/test_accounting.py`
- `tests/track2_stage35/test_execution_and_gate.py`
- `tests/track2_stage35/test_integrity_and_coverage.py`
- `tests/track2_stage35/test_strategy.py`
- `trading/track2/stage35/BACKTEST_PROTOCOL_PROPOSAL_NOT_AUTHORIZED.md`
- `trading/track2/stage35/BACKTEST_READINESS_GATE.json`
- `trading/track2/stage35/FULL_SIGNAL_EXPANSION_REVIEW_PROPOSAL.json`
- `trading/track2/stage35/H4_SIGNAL_PLAN_v1.json`
- `trading/track2/stage35/H4_SIGNAL_PLAN_v1.seal.json`
- `trading/track2/stage35/OPEN_ISSUES_STAGE35.md`
- `trading/track2/stage35/STAGE35_DESIGN_AND_GATE_SPEC.md`
- `trading/track2/stage35/STAGE35_HUMAN_REVIEW.md`
- `trading/track2/stage35/audits/H0_before.json`
- `trading/track2/stage35/audits/H1_tests.txt`
- `trading/track2/stage35/audits/H2_tests_v1.txt`
- `trading/track2/stage35/audits/H2_tests_v2.txt`
- `trading/track2/stage35/audits/H3_tests_v1.txt`
- `trading/track2/stage35/audits/H3_tests_v2.txt`
- `trading/track2/stage35/audits/H3_tests_v3.txt`
- `trading/track2/stage35/audits/H4_command.json`
- `trading/track2/stage35/audits/H4_execution.log`
- `trading/track2/stage35/audits/H4_signals_v1/coverage.json`
- `trading/track2/stage35/audits/H4_signals_v1/feature_lineage.json`
- `trading/track2/stage35/audits/H4_signals_v1/signal_intents.json`
- `trading/track2/stage35/audits/H4_signals_v1/source_reads.json`
- `trading/track2/stage35/audits/checksum_fix_validation.json`
- `trading/track2/stage35/audits/default_gate_denial.json`
- `trading/track2/stage35/audits/first_checksum_witness.json`
- `trading/track2/stage35/audits/full_tests_checksum_fix.txt`
- `trading/track2/stage35/audits/full_tests_completion.txt`
- `trading/track2/stage35/audits/full_tests_final.txt`
- `trading/track2/stage35/audits/full_tests_final_audit.txt`
- `trading/track2/stage35/audits/full_tests_release.txt`
- `trading/track2/stage35/audits/full_tests_v1.txt`
- `trading/track2/stage35/audits/golden_synthetic_v1.json`
- `trading/track2/stage35/audits/golden_synthetic_v2.json`
- `trading/track2/stage35/audits/golden_synthetic_v3.json`
- `trading/track2/stage35/audits/original_dependency_integrity.json`
- `trading/track2/stage35/audits/protected_integrity_after.json`
- `trading/track2/stage35/audits/protected_integrity_release.json`
- `trading/track2/stage35/audits/ruff_completion.txt`
- `trading/track2/stage35/audits/ruff_release.txt`
- `trading/track2/stage35/audits/source_integrity_after.json`
- `trading/track2/stage35/audits/source_integrity_release.json`
- `trading/track2/stage35/audits/stage012_signal_overlap.json`
- `trading/track2/stage35/audits/stage35_tests_v4.txt`
- `trading/track2/stage35/audits/stage35_tests_v5.txt`
- `trading/track2/stage35/audits/static_completion.json`
- `trading/track2/stage35/audits/static_final_delivery.json`
- `trading/track2/stage35/audits/static_release.json`
- `trading/track2/stage35/audits/tests_delivery.txt`
- `trading/track2/stage35/audits/tests_release.txt`
- `trading/track2/stage35/protocol_stage35_candidate_v1.json`
- `reports/codex_sessions/2026-11-09_032258_track2_stage35_partial_gate.md`:mandatory session report.
- `trading/track2/stage35/stage35_manifest.json`:self-excluded delivery inventory linked to both Stage012 manifests.

## 5. Files modified

No pre-existing file modified. Stage012,original/Phase2/Phase3 and prior reports remain unchanged. Only this session's new files revised/formatted;OPEN_ISSUES_STAGE35 records successor dispositions without altering old OPEN_ISSUES. No dependency/setup/registry changes.

## 6. Files deleted/renamed/moved

None.

## 7. Critical interfaces

- SignalIntent/from_signal:price-free immutable per-origin strategy candidate;original annual hash/fold/recipe/C3 guards,deadline/sign/reference/lineage;wraps Stage012 Cohort definitions only when quantity later provided. Unsafe float roundtrip to legacy requested size rejects.
- size_multiplier/MaturedRisk:EQUAL,rolling60median/EWMA .94RMS min40 strict past240-minute metadata,existing S2C reference;NULL raises. Historical classical control panel intentionally not inferred from OOS outcomes.
- allocate/Capacity:current eligible denominator,vintage.20,name.10,gross/net1 caps,own cash,whole-share rounding,no waterfill;existing lots fixed. LIMITS frozen candidate parameters in policy_config,mirrored protocol JSON.
- Book/Lot/Physical/Journal:immutable synthetic accountant around original Cohort definitions. Cash includes restricted proceeds once;marked physical shares=sum virtual;exact cash/NAV/realized-basis attribution,atomic commits,unique IDs,time order,state checksums and explicit reference/action payloads. No HISTORICAL economic Price accepted.
- cross/Leg:sorted internal matching at one reference then stable partial external allocation with fee residuals;different internal/external prices conserve aggregate equity. Bar reference received too late fails closed.
- corporate_actions:ex/pay dividend claims,long credits/short debits;split/reverse aggregate CIL with raw observed price,pending share adjustment;financing accrual. Unknown action/closeout remains unresolved,not fabricated.
- BorrowEvidence/Provider:UNKNOWN,CERTIFIED_OBSERVED,CONDITIONAL_SCENARIO;certified requires ticker/quantity/time/expiry binding. Fixtures cannot certify history. ACT365 explicit-rate accrual;fresh short mark with overdue carry freezes capital,CARRY_PENDING.
- window/schedule/propose_fill/apply_synthetic:original calendar,source/decision/submission/later-minute/expiry,synthetic bar-open proxy,prior received volume,partial fills,mark retention and unresolved failures. CommissionState tracks cumulative per-order minimum;no duplicate internal fee.
- require_backtest_approval/historical_start:all subgates required,agent approval refused;historical runner remains unactivated even if flags edited;no output created before checks.
- signal_expansion CLI:16-key sealed original source-only fold witness;no accountant/execution import,full expansion hard-disabled pending review.

## 8. Data/schema/provenance

200 source partitions(173 hourly projected to AAPL/COP,27 bounded genuine-minute) remain at original allowlist hashes. Full source values/data not copied.16 signals/intents,0 abstentions,4folds,8sessions;no future labels/F09 source selection andno2025+ market observations. Raw source-action conversion for neural inputs is inherited Stage012;economic raw/action contract NOT established.395 protected objects match SHA/mtime;124 transitive original helper hashes match predecessor closure. New source planSHA2aa79b8c7b9dca0eef1d1300d138672d935d60702d15f4d7f2eefd3820e9e478. Four F24 shared keys match prior Stage012 exactly,adapter regression only. Prior archived OOS same-key parity finding remains NOT_COMPARABLE for its original22keys. No new exact original replication claim.

New schemas:SignalIntent,Decimal synthetic Book and Journal with explicit clocks/legs/ref/action payloads,gate substatus,source-only coverage. Nominal240-minute target distinct from actual later fills;no target shifting. Whole20 source/history not ingested;all20×7×4 stress is synthetic. Full140,280-opportunity expansion proposal is disabled,not executed.

## 9. Dependencies/environment

Existing .venv only;Python3.14.6,torch2.10.0,pandas3.0.6,exchange_calendars4.13.2. No dependency install/specification change,credentials or provider/broker network. Decimal context default28 and EPS1e-18 are synthetic accounting convention;no float cash arithmetic. No machine-specific runtime paths;local checker path is a receipt only.

## 10. Commands/tests and failures

- Required Git status/branch/SHA/remotes/fetch;0/0 upstream. No integration.
- `.venv/bin/python -m pytest tests/track2_stage012 tests/track2_stage35 tests/test_hf20_s2c_ca.py tests/test_hf20_mag_c3_io.py -q`:87 passed in147.68s;audits/tests_release.txt,no skips/XFAIL.
- `.venv/bin/ruff check src/lstm_data/trading/track2/stage35 tests/track2_stage35`:All checks passed;ruff_release.txt. New files only formatted/import-cleaned;no frozen file touched.
- `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist`:626 files,27 inherited errors,0 owned errors/0 warnings;static_final_delivery.json. One intermediate optional-price type error fixed by explicit narrowing;no suppressions,exclusions or lowered severity.
- `.venv/bin/python -m lstm_data.trading.track2.stage35.signal_expansion --prepare-plan trading/track2/stage35/H4_SIGNAL_PLAN_v1.json`:calendar/metadata only,sealed before source reads.
- Exact real input-only CLI:audits/H4_command.json;exit0,16 keys/16 signals/16 intents,orders/fills/positions/PnL0. Source warnings:4 Arrow sandbox sysctl CPU capability messages;reads completed.
- Synthetic smoke CLI ran to new golden_synthetic_v1/v2/v3.json;no market source reads. v1 checksum defect retained as first witness;v3 has corrected chain and reference/action payloads. Assertions/cash values are fabricated synthetic examples only.
- H3_tests_v2 initially1 failed17passed:normal received bar was wrongly treated stale under1min mark-age. Explicit5min candidate policy replaces it;6min stale test and receipt coupling tested. No historical return informed change.
- Manual review found S35-005 after-hash/journal append mismatch;first_checksum_witness preserved,checksum_fix_validation andchain tests prove fix. Monetary balances were not hidden. Proposed failed fill now retains adverse observed mark and UNRESOLVED,not asserted cancelled broker fill.
- Gate default call refused BACKTEST_HOLD:G_ACCOUNTING before directory creation;default_gate_denial.json. All-PASS/self-approved fixtures also refuse historical activation.
- git diff --check and new-file review:passed. No secrets/large raw payloads;bounded metadata inventory sealed.

Editor verification:select repository.venv/bin/python,restart matching installed Pylance,refresh Problems at basic severity. Final human editor confirmation pending;27 inherited frozen replication diagnostics keep repository HOLD. No archive repair authorized.

## 11. Experiment/results

No historical financial experiment,profits,Sharpe,turnover/drawdown,performance test or optimization. Real-source outputs are original forecasts/sign/size candidate intents only. All4 annual bundle families exercised;AAPL/COP source coverage only. Synthetic accounting includes +10/−6→+4 and old exit→−6,zero-net/nonzero-virtual-gross,50 seeded randomized conservation cases,partial fees,ex/pay dividends,split/reverse/CIL,weekend carry,adverse gap/unresolved andno known-short-evidence default. These are not actual equity strategy results.

## 12. Reproduction

Use existing documented setup incl original external source/model archives and neural/dev extras already installed. Run combined tests and Ruff commands. Replay H4 exact plan/hash/command to a NEW output folder;never overwrite plan/receipts. Run synthetic_smoke --output NEW.json for arithmetic witness. Read STAGE35_HUMAN_REVIEW and gate before any future work. No financial runner activated. Config/SourceStore blocks unrestricted large signal expansion. No API keys needed.

## 13. Git/collaboration

Branch/HEAD unchanged,no commit/push. Prior untracked work preserved,Stage012/frozen artifacts byte-and-mtime unchanged. New Stage35 source/tests/docs and this report are uncommitted. Review exact paths;do not stage unrelated replication or raw data. Suggested later staging:git add -- src/lstm_data/trading/track2/stage35 tests/track2_stage35 trading/track2/stage35 plus this report;coordinate parent Stage012 delivery commit if not already recorded. Fetch/review before any separately authorized push. No rebase/reset/clean.

## 14. Known issues/risks

T2-003/004/006 andS35-001/002/003/006/007 keep financial gates HOLD:bar-only internal-reference/gap-fill ambiguity,unknown raw/action/payment contract and locates,historical classical control source/due-event orchestration missing. Unknown borrow not0;no negative-cash financing or invented forced exits. Synthetic collateral convention is not broker margin. T2-009 only synthetic engineering resolved;marked breaches block new entries,not secretly resize old lots. Mark-age5 candidate unapproved;latency5 structurally missesentry5 expiry. Inherited survivor/retrospective source andnominal-target/actual-trade mismatch retained.27 inherited static errors remain. No known failing final tests;earlier witnesses preserved.

## 15. Human decisions

G_HUMAN NOT_APPROVED. Review candidate sign/reference/classical mappings,caps,mark-age,transfer pricing,raw/action/CIL/dividends,borrow/financing andcost/participation scenarios. Future historical financial protocol/runner needs separate explicit authorization AFTER conditions close,not generic coding approval. No real shortability evidence exists. Stage6 independent statistical/financial audit later. Do not repair frozen replication without separate approval.

## 16. Next recommended steps

Read gate/review/issues;close raw/action/short/transfer/gap/due-event/control sources without PnL. Human reviews fixed candidates and source scope. Full signal expansion needs reviewed resource/source plan and optimized causal state reuse. Only future approved version may run controlled conditional long/short historical finance,all origins/costs/overnight andfair controls;then Stage6 audit/inference. No dynamic resize/options/broad allocation optimizer.

## 17. Artifact inventory

New-file listsection4 includes all code/docs/config/tests,audits(positive and negative),seals and synthetic/source-only receipts. stage35_manifest links both Stage012 manifests andbinds hashes/bytes,self/caches excluded. No market datasets/checkpoints copied. Source200 hashes,395 before-after protected hashes/mtimes,124 helper identities,reconciled golden synthetic and87/27/0 validation retained. All new outputs currently untracked/reviewable. No historical financial artifacts.
