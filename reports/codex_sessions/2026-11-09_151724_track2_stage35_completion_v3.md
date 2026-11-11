# Codex Session Report

## 1. Session metadata

- UTC: 2026-11-09T15:17:24.124150+00:00; contributor:Codex implementation session.
- Task:continue Stage35V3 free-action reconciliation,ordinary conditional policy,
  raw/event/ledger integration,nonperformance witness and financial review gate.
- Branch:feat/track-a-data-intake;starting/ending HEAD:
  8061483cb65d03264a7836b8b882123f67cbe4ad;no commit.
- Tree began dirty/untracked with all earlier replication/trading/session work.
  Existing work preserved;new V3 paths and this report remain uncommitted.
- Remote fetched safely;HEAD/upstream0ahead/0behind;no pull/merge/rebase/push.

## 2. Executive summary

Conditional ordinary-action engineering is implemented.267 unique cash events,
3splits,1unpriced MRK spin-off hold,18acquirer notices,1voluntary exchange and8
verified-zero coverage rows give298 canonical rows. Eight AMD/AMZN payer-years
remain UNKNOWN,not silently zero. Full financial release remains HOLD because
MRK/OGN valuation/CIL/special basis is unresolved and no independent human signed
release exists. No historical financial backtest/investment P&L/NAV ran.

## 3. Research/protocol impact

Original hypothesis,20stock axis,five-session sign,all origins,240scheduled-minute
endpoints,original C-A/O1/CLOCK/C3,2019b/floor,rolling/EWMA andfixed holding are
unchanged. No hyperparameter,training,neural/C3 fitting,test selection or Phase3
repair. New versioned ordinary A–G assumptions implement this task's approved
policy;2%conditional shorting/costs remain candidate scenarios. No test-profit
selection,returns or strategies were evaluated.

## 4. Files created

All reusable sources are new under src/lstm_data/trading/track2/stage35/completion_v3:
- __init__.py:package;acquire.py:bounded/redacted free HTTP;actions.py:typed facts/truth.
- inventory.py:cached observed reconciliation/coverage,not a market-value reader.
- fallback.py,conditional.py:ordinary rules and separate sensitivity populations.
- event_ledger.py:isolated claim/share consistency with no trade/NAV/P&L interface.
- raw_source.py,tapes.py:sealed raw projection and chronological action/due tape.
- book_bridge.py,engine.py:non-price action transactions/automatic carry onV2 book.
- release.py:external signature/exact-hash guard,empty reviewer anchor.
- restart.py,restart_schema.py:allowlisted explicit JSON state/resume contracts.
- witness.py:actual source+synthetic endowments,original-signal unit-fraction shadow.
- certify.py:protected hashes/static-baseline checks and NOT_APPROVED review packet.

New tests/track2_stage35_completion_v3 files:
test_actions_and_fallback.py,test_acquisition_and_inventory.py,
test_event_and_book_integration.py,test_release_and_historical_witness.py.

New docs/data/evidence under trading/track2/stage35/completion_v3 include design,
source acquisition/reconciliation,fallback JSON/MD,raw-share certification,
historical integration report,issues,test matrix,release packet,completion handoff,
canonicalCSV/provenance/prefix/assumptionJSONL,80row coverage,557due-event tape,
529consolidated assumptions,2922standalone proxy templates,source plans/seals,
provider receipts/local payloads,validation/integrity and hash manifests. The final
child manifest enumerates every path/hash;all output schemas are inspectable.
The payload subdirectory is Gitignored:local data inputs,not a redistribution claim.

## 5. Files modified

No pre-existing project/source/model/audit bytes changed. New owned V3 drafts were
fixed incrementally;failed/draft receipts were preserved with explicit names.
Final code is additive. The H0 receipt plus final6733-object SHA/mtime audit is
the precise old/new boundary,including prior untracked work.

## 6. Files deleted,renamed or moved

No old files deleted/renamed. Newly generated draft coverage,witness and first
validation receipts were retained under labelled audit names when corrections
were required;no old source or report was overwritten.

## 7. Critical interfaces and invariants

Action validates issuer role/raw units/truth;observed reconciliation rejects
conditional upgrades. complete_ordinary/carry_amount/recurring_candidates retain
prior documentary lineage and use no future payouts. ProxyPeriod is never a cash
action/pretrade NAV input. ClaimShareBook applies entitlements/payment/splits and
unpriced special claims to synthetic endowments only. EconomicReplayV3 wrapsV2
chronological fills with non-price due events/carry;physical shares remain sum of
virtual shares,claims transfer into cash once,short proceeds are restricted and
carry charges physical net short. apply_action requires synthetic://fixture
sources or a verified historical release. historical_entry_v3 verifies before
loader/mkdir/output;changing flags,owner,source label orenvironment is insufficient.
Checkpoints are explicit JSON,not pickle/eval;historical restore needs fresh release.

## 8. Data/schema/provenance

28HTTP attempts/29receipts;actual Alpaca market-data access worked with existing
credentials. Nasdaq ignored date filters;its unused future metadata is quarantined
and probe not expanded. Apple issuer/exchange/provider corroborateMay10ex/May13
record/May16pay2024$.25. Source270cash/split publication times are not measured.
251single-provider cash events retain USD denomination assumptions. Provider
success is not full coverage:MRK Organon is missing fromAlpaca but primary terms
exist. Tesla/Boeing zero assertions use actual SEC evidence;AMD/AMZN remainUNKNOWN.
No2025+market prices were read;2December2024 events retain January2025payments.
11projected actual raw minutes/5partitions passed;48OOS raw identities verified.
Raw canonical precedes adjust_prices;model-adjusted hourly prices never enter cash.
No source mutation/new cleaning. Original quarantine/PIT/survivor limits retained.

## 9. Dependency/environment

Existing.venv/Python3.14.6;no installs/updates or new accounts. requests,dotenv,
pandas,pyarrow,torch,numpy,exchange_calendars,Ruff,Pyright already installed.
Secrets used only fromexisting environment/.env;no values logged. The new scope
scan found zero known credential leaks. Network-enabled execution was approved
for the declared free-source requests after sandbox DNS failure;not a provider
availability conclusion. No broker endpoint or live/paper account accessed.

## 10. Commands/tests

Baseline121passed37.35s. Final197passed107.73s(all121old+76new),zero skip/XFAIL.
Exact command:
`.venv/bin/python -m pytest tests/track2_stage012 tests/track2_stage35 tests/track2_stage35_completion_v2 tests/track2_stage35_completion_v3 tests/test_hf20_s2c_ca.py tests/test_hf20_mag_c3_io.py -q`

`.venv/bin/ruff check --select E,F,I src/lstm_data/trading/track2/stage35/completion_v3 tests/track2_stage35_completion_v3`:PASS.
`.venv/bin/pyright src/lstm_data/trading/track2/stage35/completion_v3 tests/track2_stage35_completion_v3 --pythonpath .venv/bin/python --outputjson`:20files,0errors/0warnings.
Full command:`.venv/bin/python scripts/check_python_types.py --pylance-dist <locally resolved installed ms-python.vscode-pylance-*/dist>`:
662files,27inherited errors,0warnings;exactV2baseline match,repositoryHOLD.
The actual resolver uses Path.home().glob('.vscode/extensions/ms-python.vscode-pylance-*/dist')
andchecks bundled/stubs/typeshed-fallback;not a portable dependency onthis host's
absolute path. Editor:select.venv,basic severity,refresh Problems;human verification pending.

`python -m lstm_data.trading.track2.stage35.completion_v3` suffix commands inventory,
tapes,conditional,raw_source,witness,certify(--integrity-only) are the executed
bounded preparation/audit entry points. Receipts retain exact failures/fixes:
calendar scope,pandas stubs,HTML footer classification,duplicate coverage counting,
split pay-before-ex witness omission and restart field types. No weakening or
archive edit. Arrow's sandbox sysctl cache warnings were nonfatal and retained.

## 11. Experiment/results

No strategy experiment.131111original forecasts and87557matched controls retained,
not recomputed.2cached original signals and8dimensionless allocations reused.
Actual source/action witnesses use synthetic endowed quantities;no historical
investment returns,cost drag or economics ranking. Funded accounting tests use
fabricated prices only. Exact archived original forecast parity remains NOT_COMPARABLE;
Phase3 mismatch remains frozen. No untouched/live/PIT/shortability claim.

## 12. Reproduction

Use documented existing.venv and authorized original data/model/cache bundle.
Transfer permitted cached payload bytes with hashes oracquire a separately
versioned source vintage;never overwrite old receipts. Run the entry points and
commands in STAGE35_COMPLETION_HANDOFF_V3.md. Source-backed tests require those
local datasets;mocked HTTP/fallback tests do not use network. No clean-machine
rehearsal was claimed. certify writes an immutable review packet,not approval.

## 13. Git/collaboration

Branch/HEAD unchanged;remote fetched,0ahead/0behind. No commits/push/stash.
Original untracked replication,trading,Stage012/V1/V2 code/tests andreports kept.
Only new V3 namespaces,new docs/cache/evidence andthis report added. gitdiff--check
passed;tracked gitdiff is empty because relevant work was already untracked.
Before any future commit,stage only intended reviewed files and this report;
keep large data/payload caches out,coordinate with teammate and do not pull over
unknown work. No commit/push is authorized by this session.

## 14. Known issues/limitations

V3-ACTION-001:MRKJun3,2021 requires OGN value/CIL/special basis/due-bill handling.
267cash events are not globally verified/exhaustive:251remain single-provider,
8AMD/AMZN payer-years unknown;ordinary proxies are separate conditional templates.
270date-only availability assumptions are not feed receipts. Strictlocates/NBBO
unavailable;borrow2%is assumed. Survivor20,retrospective action/quarantine,
overnight andnominal-target/actual-holding mismatch remain. T2-010's27frozen errors
are repositoryHOLD;owned0. New checkpoint requires original float Cohortmetadata
andDecimal monetary lots;unsupported legacy metadata fails closed.

## 15. Human/teammate review

Resolve/review material special action without ordinary imputation or outcome-based
exclusion. Review ordinary conditional populations,USD units,date-only availability,
short/OHLCV assumptions andsource rights. Independent trusted review+exact hashes,
ID/time/signature and separate later financial-run authorization are required.
No executing-agent reviewer key,approval ID or signature was issued.

## 16. Next steps

Complete special asset/CIL/basis handling orreview an honest prospective policy;
review V3 gate/packet andsource uncertainties;obtain independent financial release.
Only after separate authorization run exploratory2021–24EQUAL/ROLLING/EWMA/S2C
financial simulation. Stage6independent statistical audit remains separate.

## 17. Artifact inventory

Core human document:trading/track2/stage35/completion_v3/STAGE35_COMPLETION_HANDOFF_V3.md.
Gate:BACKTEST_READINESS_GATE_V3.json(overallHOLD,humanNOT_APPROVED,no financial run).
Complete new code/doc/test/evidence hash inventory:stage35_completion_v3_manifest.json,
content-binds parentV2manifest andall inputs;self-exclusion explicit. Source/action
inventorySHA256:58122842c19dc64fc46ed692fe6cf886c0cc36a1469170cea32b3a6b0fae388b. Finalintegrity:6733protectedobjects+227partitions
unchangedSHA/mtime. Local payloads include a69MBunparsed PDF capture,not used as
factual evidence;ignored fromGit andretained only as an acquisition receipt.
No plots,trained checkpoints,historical financial outputs or new models created.
