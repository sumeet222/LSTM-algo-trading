# Stage35 human review

**STAGE3_5_PARTIAL_WITH_EXPLICIT_HOLDS. No historical trading P&L/backtest was run.** Current authority covers implementation,synthetic economics,and the sealed input-only expansion only. BACKTEST_READINESS_GATE.json is HOLD;G_HUMAN=NOT_APPROVED. No live/paper orders,broker/provider calls,financial scenario sweep or optimization.

## What exists and what remains blocked

Additive `src/lstm_data/trading/track2/stage35/` now provides typed strategy intents,all sizing kernels,current-vintage allocation,atomic physical/virtual accounting,internal-cross allocation,synthetic corporate actions/borrow/financing,receipt/expiry scheduling,bar-open proposal adapter and a fail-closed gate. Frozen Stage012 is reused as-is. This is not a complete historical financial simulator:raw/action/short source certification,bar-only transfer/resting-order policy,and complete historical due-event/control tapes remain blocked. NULL is disabled pending Stage6 design. Unresolved exposure is retained,not dropped.

## Provenance and real signal coverage

395 original/model/Phase2/Phase3/Stage012 objects remain identical in SHA256 AND mtime.124 original transitive helper hashes match the Stage012 receipt.200 source partitions match predeclared original hashes after reading. No Stage012 byte or original recipe/checkpoint/C3 changed. New files only under Stage35/test namespaces plus a new session report. Original6572-parameter annual bundles F21/F22/F23/F24 loaded eval-only/no-gradient;no auxiliary head used for alpha. The Phase3 MATERIAL_NUMERICAL_OR_METHODOLOGICAL_MISMATCH remains frozen;no Phase2 inference. Stage012's original archive parity status remains scoped HISTORICAL_PREDICTION_PARITY_NOT_COMPARABLE,not equality.

H4 planSHA `2aa79b8c7b9dca0eef1d1300d138672d935d60702d15f4d7f2eefd3820e9e478` was sealed before reads:16 keys,AAPL/COP,one10:30 normal origin and one09:30 half-day origin in each fold. Dates are calendar-selected,not archive/return-selected.173 hourly partitions projected to2 stocks preserve genesis EMA/Wilder ancestry;27 minute partitions hold bounded M2/opening anchors. Hourly rows returned:50626;minute rows returned:2156.16/16 source-eligible signals and intents,0 real abstentions,0 orders/fills/positions/P&L. All140 normal/80 half-day20-name opportunities and all7 origins×4 folds are tested synthetically;this is NOT full20-name historical coverage. Full140,280-opportunity proposal is disabled and requires reviewed source/resource plan;rough1–3GB signal-lineage output and24–200h naive replay extrapolation are unbenchmarked,not a run promise.

|Fold|Session / slot ET|Stock|Magnitude C3|Sign|Candidate g|Intent|
|---|---|---|---|---|---|---|
|F21|2021-01-08T10:30:00-05:00|AAPL|0.00860412739519|-1|0.5|yes|
|F21|2021-01-08T10:30:00-05:00|COP|0.0120970431389|1|0.5|yes|
|F21|2021-11-26T09:30:00-05:00|AAPL|0.0130022218192|1|0.5|yes|
|F21|2021-11-26T09:30:00-05:00|COP|0.0160954196578|1|0.5|yes|
|F22|2022-01-10T10:30:00-05:00|AAPL|0.00827687843817|-1|0.5|yes|
|F22|2022-01-10T10:30:00-05:00|COP|0.00747817003727|1|0.611369508|yes|
|F22|2022-11-25T09:30:00-05:00|AAPL|0.0176356520893|1|0.5|yes|
|F22|2022-11-25T09:30:00-05:00|COP|0.0185528039398|-1|0.5|yes|
|F23|2023-01-09T10:30:00-05:00|AAPL|0.00897758439515|-1|0.5|yes|
|F23|2023-01-09T10:30:00-05:00|COP|0.00876368077158|1|0.521690059|yes|
|F23|2023-11-24T09:30:00-05:00|AAPL|0.00917046271173|1|0.641286347|yes|
|F23|2023-11-24T09:30:00-05:00|COP|0.0132042435268|-1|0.52972485|yes|
|F24|2024-01-08T10:30:00-05:00|AAPL|0.00599848214485|-1|0.634175181|yes|
|F24|2024-01-08T10:30:00-05:00|COP|0.00783939505666|-1|0.583198717|yes|
|F24|2024-11-29T09:30:00-05:00|AAPL|0.0100549070118|1|0.584877863|yes|
|F24|2024-11-29T09:30:00-05:00|COP|0.012919845988|-1|0.541385395|yes|


Four F24 overlapping keys exactly match prior Stage012 magnitudes/signs/g (adapter regression only,not archived OOS parity). All other real witnesses are new cross-fold source-only signals. Per-field lineage and source receipts are in audits/H4_signals_v1. No current/future target/label/endpoint-price or F09 table enters the inference/intent path. Genuine missing inputs yield explicit abstention,never a future-complete universe. Recursive original COP/Q2 and original price basis preserved. Model-input adjusted prices never enter cash accounting.

## Allocation and sizing policy

All arms require the same causal signal/sign/reference eligibility. EQUAL g1;ROLLING_RISK median last60 nonnegative matured240-minute magnitudes,min40;EWMA_RISK RMS with.94 decay,initialized first window square,min40;S2C_RISK frozen2019 b/max(mhat,m_floor),clip.5–1.5. Classical rows must match fold/ticker/slot/horizon/units,be received before decision,and have no known missing value in window. Historical classical-control source panels remain unprepared (S35-003). Different empirical statistics are dimensionless proxies,not equivalent conditional sigma or E|R|. NULL interface rejects;seed35/within-fold-session-slot reassignment is a proposal for Stage6 review only. Existing2019 reference560 groups/checksum5c453193572a2e428c561249c842c90a3d36041736183195f3e1dc6a350b6681 was consumed,never re-fitted.

New budget B=min(.20NAV,NAV−existing virtual gross,own capacity).Targets=min(B*g_i/sum current eligible g,.10NAV−existing name gross).One common conservative net scale;whole-share rounding toward0,no redistribution after caps;idle stays cash. One arm per account/vintage;stable ticker/cohort ordering. Physical net<=NAV,virtual gross inclpending<=NAV,name<=.10NAV,vintage<=.20NAV. Mark breaches are journaled and block new reservations;old cohorts are not secretly resized. Existing target endpoints remain fixed;only explicit synthetic forced-buy-in/risk-liquidation causes can bypass scheduled exit,subject to later policy approval.

## Exact economic convention and synthetic evidence

Decimal(default28-digit context),USD. Cash C includes restricted physical short sale proceeds R once. NAV=C+signed physical marked inventory+signed accrued claims. R=sum short physical shares*physical short entry basis;spendable cash=C−R. Virtual gross+pending also uses own-capital capacity min(C−R,NAV−virtual gross−pending). Off-balance restrictions are not extra NAV assets. Physical position per ticker equals summed virtual shares. Every transaction checks cash attribution,NAV attribution,and both physical/virtual basis-realization identities. Duplicate IDs/out-of-order events reject;compute-and-validate immutable copies before committing. Current Cohort definitions and original requested sizing are retained;no reopening/resizing on later forecasts.

Sorted internal buys/sells match at one synthetic contemporaneous public reference,known by execution;internal cash cancels with0 external spread/commission. Residual is one physical net fill at its own modeled price;fees allocated once with deterministic residuals. Partial external fills conserve both share and fee totals. CommissionState carries cumulative minimum across partials of ONE external order;new IOC orders have new minima. Internal transfer attribution may change realized versus unrealized components,never aggregate cash/NAV. Different transfer/external prices and zero-net/nonzero-gross are tested,including50 seeded randomized cases(seed35).

Golden SYNTHETIC ONLY:initialcash100000,+10/−6 virtual fills at100,externalnet+4,fee1→cash99599,NAV99999,virtualgross1600. Old+10 exits at110,externalnet−10→physical−6,cash100699,restricted660,NAV100039. These are hand-computable fabricated prices,not historical profits. Reverse split3long shares at100 to1.5 at200,aggregate CIL.5 at200→1physical share,cash99800,NAV100000. Long/short dividend claims accrue at ex-date,settle only when due;raw ex-mark plus claims prevents adjustment double counting. Negativecash financing is disabled;borrow/funding are explicit liabilities/settlements. Calendar charge=end-reference notional*supplied annual rate*actualseconds/(365*86400),not an observed broker fee. Known increasing rates require segmented events;unknown never0. Fresh short mark with overdue carry sets CARRY_PENDING until explicit accrual. No historical due-event tape/autonomous liquidation/recovery activated. Missing recall/exit prices retain shares UNRESOLVED.

Journal has event,observation,available,processing times,cohort legs,currency,raw basis,reference source/price,action/rate details and before/after economic-state checksums. S35-005 initial v1 checksum defect was found in review:after hash preceded journal-ID append. Witness retained;state digest now excludes journal,full journal is artifact-hashed,and adjacent before/after chain plus final state tests pass. v3 includes explicit reference/action payloads. No economic cash/share imbalance was concealed. H3 initially failed one integration test because1min mark-age was shorter than1min bar completion+2min delivery;candidate mark-age5 wall minutes is an explicit new human-review assumption,not performance tuning.

## Execution and limits of free OHLCV

Default nominal10:30ET→assumed decision10:32→first later minute10:33;endpoint14:30→exit decision14:32→first later minute14:33. Exchange-minute arithmetic handles half days,weekends,DST,Sandy,2018closure.2024-11-27 15:30ET endpoint is half-day11-29 13:00ET;exit decision after close waits until12-02 09:30ET.5min receipt plus later minute cannot meet5min expiry;abstain rather than backdate. Zero feature/inference duration is a scenario,not measured latency. Model target still starts nominal t;no exact conversion to economic return by shifting/subtracting absolute segments.

Synthetic bar-open proxy requires order before bar start and books only after bar received;prior-volume cap1percent uses volume available before submission,not full future fill-bar volume. Fees/spread/impact are candidate stress assumptions,not NBBO. Partial/missing/halt/expiry paths preserve conservation. An observed adverse mark is retained even if the proposed fill fails;state becomes UNRESOLVED,not factual broker cancellation. Bar-only contemporaneous internal crossing cannot satisfy chosen policy;G_EXECUTION/G_ACCOUNTING HOLD. Synthetic engine rejects HISTORICAL price tapes and the historical runner is unactivated even if gate flags are edited. No quote/locate/fee data was scraped or invented.

## Financial readiness gate

|Gate|State|Reason / evidence|
|---|---|---|
|G_ACCOUNTING|HOLD|synthetic conservation passed;bar-only internal reference and action-source policies unapproved|
|G_EXECUTION|HOLD|synthetic boundaries tested;bar-only contemporaneous references and proposed gap-fill/risk decisions not financially certified|
|G_PRICE_BASIS|HOLD|raw historical vendor/action effective and payment-date contract not certified;synthetic raw actions only|
|G_SHORT|HOLD|identity/source receipts|
|G_RISK|HOLD|synthetic allocator/caps pass;classical source panel and due-event integration not financially certified|
|G_PROVENANCE|PASS|identity/source receipts|
|G_HUMAN|NOT_APPROVED|current prompt authorizes implementation only;no financial approval inferred|
|G_REPOSITORY|PASS|owned-code only|


Strict short mode requires ticker/quantity/time-bound evidence;none exists here. Conditional synthetic fixtures are permitted unit tests,not human-approved historical short assumptions. G_REPOSITORY PASS is OWNED scope only;repository T2-010 remains HOLD with27 inherited errors. G_HUMAN is not approved by this execution task. Default start was tested and refused BACKTEST_HOLD:G_ACCOUNTING before any output directory. No executing-agent approval can activate the runner.

## Validation matrix

|ID|Result|Witness|
|---|---|---|
|V01|PASS|original fold/checkpoint/recipe/C3 negatives;source-hash guard reused|
|V02|PASS scoped|52 preserved source/label mutation tests and price-free intent schema;no F09 reader|
|V03|PASS scoped|delay,opening,half-day,holiday,DST/Sandy/2018 closure tests preserved|
|V04|PASS synthetic/Stage012|all20×7×4 synthetic axes;original session sign cache preserved|
|V05|PASS synthetic|+10/−6→physical+4;old+10 exit→−6|
|V06|PASS synthetic|stable partial/cancel/fee residuals,cumulative minimum per external order|
|V07|PASS synthetic|different internal/external prices change attribution,not aggregate equity at same mark|
|V08|PASS synthetic|cash includes restricted proceeds once;virtual gross remains reserved|
|V09|PASS synthetic|long/short ex/pay,split/reverse,CIL,adjusted-price trap|
|V10|PASS synthetic|Fri–Mon ACT365,explicit rates/funding,CARRY_PENDING guard|
|V11|PASS synthetic|missing/halts/expiry/exit unresolved;no invented fill|
|V12|PASS synthetic|mark shock journal records hold;proposed failed fill keeps observed mark|
|V13|PASS synthetic|20-name current-vintage allocation,rounding,cash,caps|
|V14|PASS synthetic|physical0 withvirtualgross>0 uses own capital|
|V15|PASS synthetic;bounded real|all20 source axes synthetically;real2 stocks only,typed abstentions|
|V16|PASS synthetic|fees/slippage monotonic on identical fills,internal fees0|
|V17|PASS schema/HOLD facts|unknown borrow and uncertain actions fail;no real locate approval|
|V18|PASS|new forecasts do notresize old lot;REBALANCE/RESIZE reject|
|V19|PASS|default gate refused before output creation;agent selfapproval rejected|
|V20|PASS integrity/HOLD repo|395 objects unchanged,124 original helper hashes unchanged;27 inherited diagnostics retained|

## Commands and environment

```
.venv/bin/python -m pytest tests/track2_stage012 tests/track2_stage35 tests/test_hf20_s2c_ca.py tests/test_hf20_mag_c3_io.py -q
.venv/bin/ruff check src/lstm_data/trading/track2/stage35 tests/track2_stage35
.venv/bin/python -m lstm_data.trading.track2.stage35.synthetic_smoke --output <NEW synthetic receipt.json>
.venv/bin/python -m lstm_data.trading.track2.stage35.signal_expansion --plan trading/track2/stage35/H4_SIGNAL_PLAN_v1.json --plan-sha256 2aa79b8c7b9dca0eef1d1300d138672d935d60702d15f4d7f2eefd3820e9e478 --output trading/track2/stage35/audits/H4_signals_v1
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-pylance>/dist
```

87 passed(52 prior+26 Stage35+9 neural),no skips/XFAIL;Ruff full configured E/F/I checks pass on new namespace;full basic626 files,27 inherited errors,0 owned errors/0 warnings. Earlier optional-price type narrowing and new-file lint issues were fixed without suppressions. Final exact receipts:tests_release.txt,ruff_release.txt,static_final_delivery.json. Original no-source-value violations;4 Arrow sandbox CPU-sysctl warnings did not fail reads. Existing.venv/dependencies only,no installs. Select repository.venv/bin/python,restart matching installed Pylance,and refresh Problems;final editor confirmation is human-pending. No commits/pushes;dirty prior work preserved. Reproduce H4 only with exact seal and a NEW output dir;do not overwrite existing plans/receipts. Tests need original external archives;new metadata is small,source data/weights not copied.

## Human review and next separately authorized work

Review OPEN_ISSUES_STAGE35,all candidate policy/cost/borrow/mark-age defaults,transfer reference,gap/resting-order treatment,raw/share/action contract and classical/due-event sources. T2-003/004/006 andS35-001/002/003/006/007 keep financial use blocked;T2-009 only synthetic-engineering resolved;T2-005/007/010 retained. Full historical opportunity generation needs separate source/resource review. BACKTEST_PROTOCOL_PROPOSAL_NOT_AUTHORIZED.md proposes future controlled EQUAL/ROLLING/EWMA/S2C plus costs/borrow/latency,all origins/overnight,full cash/actions and later Stage6 clustered/blocked inference. No P&L/Sharpe/turnover/financial null trials ran.2021–24 remain exploratory,with survivor/retrospective-source bias and unknown live feasibility. Stage6 independent financial/statistical audit is later,not this self-review.

Manifest stage35_manifest.json links both protected Stage012 manifests and content-binds new code/config/tests/evidence plus session report,self/caches excluded. Integrity395 protected objects+124 transitive original helpers unchanged;200 source hashes match original allowlist. No Stage012,original/Phase2/Phase3/data mutation. No historical trading P&L/backtest was run.

Final audit refinements:received marks are committed even on failed proposed fills;unresolved gap proposals are not asserted broker cancellations. CARRY_PENDING blocks new capital until explicit known-rate accrual catches up with a fresh short mark. Automated historical due-event ingestion remains S35-007 HOLD. Final configured Ruff E/F/I check passes;only new Stage35 files were formatted. No frozen source was reformatted.
