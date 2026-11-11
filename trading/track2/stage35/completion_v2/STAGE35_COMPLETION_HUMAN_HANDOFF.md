# Track2 Stage35 completion handoff — V2

**STAGE35_PARTIAL_EVIDENCED_SOURCE_OR_POLICY_BLOCKER**

**No historical trading P&L/backtest was run.** No live/paper/broker orders. The full historical original-model signal/control pass completed; material action-source and financial-loader certification holds remain. Independent financial certification and G_HUMAN have not occurred. This is not backtest-ready or a claim of profitability/live deployability.

## Actual completed evidence

|Evidence|Actual result|
|---|---|
|Universe/folds|Original20 stocks, F21/F22/F23/F24,2021–2024|
|Calendar coverage|1005 sessions,7014 valid nominal origins,140,280 opportunities|
|Original-model forecasts|131,111 input-eligible original C-A/O1/CLOCK/C3 main-head forecasts;9,169 explicit unavailable-input rows|
|Sign/risk eligibility|128,192 EQUAL/S2C candidates;87,557 rolling/EWMA/four-arm matched candidates|
|Historical source access|227 distinct partitions:174 hourly,53 bounded minute projections;509,140 hourly and236131 minute-anchor rows returned|
|Small raw/action fixture|8 genuine OHLCV rows;AAPL2020 verified4:1 split boundary;source-level only|
|Cache parity|12 predeclared AAPL/COP cross-fold normal/opening/late/half-day keys:exact FT16/CLOCK equality,forecast tolerance met|
|Earlier H4 retention|All16 keys within predeclared tolerance,max magnitude difference2.616e-9;not original archived forecast parity|
|Integrity|568 protected objects and227 source partitions:SHA256 andmtime unchanged|
|Tests|121 passed:52Stage012+26priorStage35+34 new completion+9 neural IO/regressions|
|Ruff|E/F/I all pass|
|Static|16 new owned Python files:0 errors/0 warnings;full 642 files:27inherited frozen-replication errors,0 new errors|
|Real shadow|Actual source→original signal→mature controls→price-free intent→dimensionless allocator→financial gate refusal;0orders/fills/positions/cash/NAV/P&L|
|Synthetic economics|20-name intent/reservation/fill/fixed-exit roundtrip;opposed crosses/partials;fees;dividends/splits;weekend/rate-segment carry;gap debt/repayment;prospective liquidation/failed closeout;known-remainder expiry|

Only matured historical endpoint movements were computed for authorized risk controls, not strategy trade returns or portfolio performance. Full authority is `audits/full_run_release/FULL_SIGNAL_COVERAGE_REPORT.json` and `audits/signals_release/`; initial root and intermediate full-run reports are retained superseded witnesses. The first full pass's first-eligible sign timestamp was corrected, then a type-safe timestamp revision was rerun. Unique coverage above is not summed across reruns. No results-driven key/model selection occurred.

## Gates and remaining blockers

|Gate|State|Evidence/meaning|
|---|---|---|
|G_PROVENANCE|PASS|568 protected objects/227 partitions;all original associations retained;Phase3 MATERIAL_NUMERICAL_OR_METHODOLOGICAL_MISMATCH remains frozen|
|G_SIGNAL_CAUSAL|PASS within inherited dataset|48scheduled slots,seven M2 contexts,10CLOCK;source frontier;session-frozen D[-1]/D[-6];no View/F09/future endpoint selection|
|G_CONTROL / G_DATA_COVERAGE|PASS|All 20/four-fold input-only pass;strict matured controls;own and matched universes explicit|
|G_ACCOUNTING|HOLD|Synthetic reconciliations pass;complete verified historical dividend/special-action/pay-date feed missing|
|G_EXECUTION|HOLD for financial certification|V2 causal kernel/portfolio orchestration pass synthetic tests;complete raw/action financial loader/replay not certified|
|G_PRICE_BASIS|HOLD|Bounded raw-share split fixture established;whole-period action economics not complete/certified|
|G_SHORT|Conditional implementation approved|2% ACT/365 assumption;strict observed-locate certification still unavailable,not waived|
|G_RISK|PASS synthetic scope|20/10/100caps,pending gross,restricted proceeds,expense reserve,marked breach/liquidation andfixed exits|
|G_REPOSITORY|Owned PASS/global HOLD|0 new diagnostics;27 frozen errors remain T2-010;editor refresh needs human confirmation|
|G_HUMAN|NOT_APPROVED|No external approval ID/signature/registered reviewer key;implementation defaults do not authorize finance|

**Smallest source blocker:** the retrieved Apple May2,2024 issuer release gives $.25 dividend, recordMay13 and payMay16, but does not state the ex-date. The local nine-split facts file is not a comprehensive action feed. The single predeclared Yahoo dividend CSV probe returnedHTTP429;no retries/accounts/current quotes were used. All 20 dividend/pay-date completeness remains NOT_ESTABLISHED. This does not prove no free source exists; it is the precise current evidence gap. Unknown pay dates retain signed undated claims; unknown CIL/special actions/late corrections retain explicit unresolved exposure and require source/replay resolution. They are never zeroed.

T2-003/S35-001 andS35-006 have new implemented synthetic conventions. S35-003 now has an actual full mature control panel. T2-009 marked allocation is integrated synthetically. T2-004/S35-002/S35-007 financial source/certification holds remain. T2-006 conditional branch is approved;actual locates remain unverified. T2-005/007 andT2-010 remain qualifications/holds. S35-V2-003 records the historical raw/action loader-certification gap; no claim of a fully certified end-to-end economic history loader is made.

## Code, data and accounting conventions

New additive namespace: `src/lstm_data/trading/track2/stage35/completion_v2/`. No old Stage012,Stage35V1,original,Phase2/3 bytes or frozen manifests were edited. All checkpoints load through the original registry:6,572 parameters,48x16+10CLOCK,eval/inference_mode,annual recipe/target scale/C3;auxiliary signed heads never supply alpha. Original COP mask-before-floor andoriginalQ2 semantics are reused,not refitted. Risk checksum remains5c453193572a2e428c561249c842c90a3d36041736183195f3e1dc6a350b6681(560 groups,2019prefix). Original fitted cutoffs remainF21:2020-09-30,F22:2021-09-30,F23:2022-09-30,F24:2023-09-29;no OOS fit/recalibration.

Cache/source lineage and source plans are linked in FULL_SIGNAL_CACHE_PARITY_AND_RESOURCE_REPORT.md. Actual final inference/control pass288.643s;cache construction234.193s;12-key parity75.540s. Derived cache208105716 bytes;final signal partitions/receipts50554023 bytes. Peak RAM was not measured. No full raw dataset copy or dependency installation. Large caches/price fixtures/signals remain local/ignored;hash manifests are reviewable. Identical code/source values are deterministic;elapsed time metadata is not.

V2 expiry is+10 wall minutes;V1+5 is unchanged. Decisions use assumed+2 receipt,zero inference duration andlater actual dependency readiness. A submitted order precedes a modeled minute start;its raw open is learned aftercompletion/receipt and then posted. Internal opposing legs settle at that same ex-post reference withzero external costs;only physical netfills pay adverse spread/impact/commission once. Cumulative minimum is per external order acrosspartials. A known capped partial leaves unsubmitted target remainder;expiry releases only that known remainder. Missing execution leaves uncertain pending status,reservations andinventory;no broker cancellation is asserted.

NAV=C+physical signed marked inventory+accruals;restricted short proceeds are a subset ofC,not a second asset. Gross risk counts virtual lots andpending quantities even at physical netzero. Borrow charges actual physical netshort once,using previous known marks and ACT/365 calendar time,segmented before mark/trade/action/rate changes. Synthetic gapfills are never retrospectively rejected;explicit funding claims conserve cash/NAV andblock new risk untilrepaid. Prospective liquidation requests require a new subsequent valid event;halted closeouts retain exposure. Splits transform share/basis/pending units;unknown fractions/actions stay unresolved. No discretionary leverage or assumed broker margin certification.

Classical controls use last60 scheduled mature same-slot movements,min40,strict known-missingness;rolling median andEWMA RMS(.94,earliest squared initialization). Their scales differ conceptually from the S2C endpoint absolute-return proxy. All use frozen positive2019 b/floor andclip[.5,1.5]. No volatility/option IV/minimum-variance claim. NULL interface remains deferred. No stop-loss/alpha optimization or dynamic forecast resizing.

## Exact commands and receipts

Run from repository root with the existing `.venv` and original private source/model artifacts identified by saved hashes. No API key/new dependency is required. OpenSSL is needed only for a future independently authorized signature-verification path;no key was generated here.

```sh
.venv/bin/python -m pytest tests/track2_stage012 tests/track2_stage35 tests/track2_stage35_completion_v2 tests/test_hf20_s2c_ca.py tests/test_hf20_mag_c3_io.py -q
.venv/bin/ruff check --select E,F,I src/lstm_data/trading/track2/stage35/completion_v2 tests/track2_stage35_completion_v2
.venv/bin/pyright src/lstm_data/trading/track2/stage35/completion_v2 tests/track2_stage35_completion_v2 --pythonpath .venv/bin/python --outputjson
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
```

Receipts:`audits/validation_release_v2/pytest.txt,ruff.txt,owned_types.json,repository_types.json`. Full checker exits1 for the27 inherited errors;do not call it globally green. On another machine resolve the installed Pylance dist locally;keepbasic severity/.venv and refresh editor Problems using that interpreter. Editor confirmation is pending.

```sh
.venv/bin/python -m lstm_data.trading.track2.stage35.completion_v2.audit_completion --signals trading/track2/stage35/completion_v2/audits/signals_release --report trading/track2/stage35/completion_v2/audits/full_run_release/FULL_SIGNAL_COVERAGE_REPORT.json --output trading/track2/stage35/completion_v2/audits/FINAL_PROTECTED_INTEGRITY_RELEASE.json
.venv/bin/python -m lstm_data.trading.track2.stage35.completion_v2.synthetic_smoke --output trading/track2/stage35/completion_v2/audits/GOLDEN_SYNTHETIC_FINAL_V2.json
.venv/bin/python -c 'from lstm_data.trading.track2.stage35.completion_v2.source_audit import shadow_release; shadow_release()'
```

Synthetic golden publication was repeated identically. Shadow refusal is FINANCIAL_GATE_HOLD,with no prohibited output. Source plan/cache command is preserved in audits/cache_command.json. Full inference command actually executed:

```sh
.venv/bin/python -m lstm_data.trading.track2.stage35.completion_v2.signals run --plan trading/track2/stage35/completion_v2/FULL_SIGNAL_EXPANSION_PLAN_V2.json --hash 948e0a8f03dfcc9f802d09b70ecd5ab043250ee9a54108cd17a4579864e8d79d --cache trading/track2/stage35/completion_v2/audits/cache --parity trading/track2/stage35/completion_v2/audits/CACHE_PARITY_V2.json --output trading/track2/stage35/completion_v2/audits/signals_release --report-root trading/track2/stage35/completion_v2/audits/full_run_release
```

Completed report publication intentionally refuses overwrite;use the auditor now. For a fresh reproduction choose new empty output/report/cache paths andrun cache build→parity→run with the same plan/hash. Incomplete sealed-day runs resume underidentical binding. An unsealed parquet refuses for review,rather than silently replacing evidence. Source hashes must match;no download/cleaning fallback orPhase2 substitution.

## Review packet and next permitted work

Protocol,source/action audit,controls/resource reports,internal-cross/short specs,issue register,test matrix,BACKTEST_READINESS_GATE_V2.json,RELEASE_CODE_SCOPE_MANIFEST_V2.json andstage35_completion_manifest_v2.json are the review set. Release code-scope checksum:f33cfec34d3fa400bf055221e9914ac9e7dd8cbf483938548b181dd4b3be228e. BaseGit8061483cb65d03264a7836b8b882123f67cbe4ad;new code is uncommitted and content-hash-bound,not represented as that old commit. No commits/push/pull/merge/rebase. Initial unrelated dirty/untracked work remains preserved;branchupstream is0ahead/0behind after fetch.

Next:obtain/verify complete authorized raw-share action ex/pay/special-event coverage;finish/certify the economic source-loader/due/replay integration with those records;independent human review of exact policy/source/code/checkpoints andconditional-short/OHLCV assumptions;then register an independently controlled reviewer public key in a separately reviewed successor andissue a hash-bound external approval ID/signature. All gates must pass **before** any financial source loader/output. Generic flags,owner labels andenvironment variables cannot release it. No agent self-signing is accepted.

Any future study must be called retrospective exploratory OHLCV-proxy long/short simulation with assumed borrow availability/costs. Predeclare allarms,paired/attainable sets,capital,fees,borrow/latency grids andunresolved-exit treatment. P&L/Sharpe/turnover/drawdown/statistical tests andStage6 independent financial/statistical audit remain separately authorizable. No strategy results were produced here.
