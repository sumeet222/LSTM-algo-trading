# P3 engineering-only handoff — P2 version1

No P3 implementation is authorized by this package. Before any later P3/P4 or scientific-gate work, read [the register](p2_deferred_work_register.json), [the readable index](../../../docs/track_a/P2_DEFERRED_WORK_REGISTER_v1.md), and [the SHA-bound config](../../../configs/track_a_p2_engineering_handoff_v1.json). Call `src/lstm_data/p2_closure.py:312`; a missing/altered register, lost seed ID or empirical-permission claim fails validation. Legitimate status changes require a new append-only version.

| Upstream type/API | Consumable fields and invariant | Never infer |
|---|---|---|
| ScheduledStep / ExecutionPlan |session,origin,start,end,information_cutoff; plan.cutoff,issuance,issuance_kind,entry,exit,reason; complete XNYS steps only|A planned event is not a fill; issuance cannot extend original cutoff|
| ForecastEvidence / CausalEligibility |issuable,cutoff,input_symbols,basis,evidence_ref; forecast_issuable,entry_eligible,reasons/source IDs; scope is source-clock-reference-only|No portfolio risk admission or exit guarantee from these flags|
| ExecutionReference |symbol,side,scheduled_event_at,expected_period_end,row,lag_seconds,valid_at_event,reason,execution_version|price alone does not prove availability, execution or raw-share epoch|
| ProxyLabelSample vs minute LabelSample |distinct execution/target/M2 versions; raw_returns, validity, maturity, references, action scope and purge rules|label_valid cannot admit an entry, prove a fill or settle a position|
| StockTensor / stock_window |symbols/ORDER,steps,5×48×16 values/mask/reasons/lineage; floor/M2/scaler refs, source/action bindings,context,source_only,synthetic,input_eligible|Missing cells are not0; HISTORICAL_TRAINING is not a live forecast state|
| MarketWindow / window_from_history |48×5 values,48 valid-vector mask,48×5 cell_mask,ends,source IDs/reasons/ages,floor/scaler refs,context,source_version|period_end/retrieval cannot prove available_at;0 after scaling is not an observed raw price|
| MarketAssembly |mc0_values5×48×21, same direct_market48×5 for future MC1,mask,ends,stock/market lineage,cert refs;model_wiring=NOT_BUILT|SPY is not stock6,a target or a holding; masks are not added learned channels|
| Action/Account primitives |event IDs,known_at/basis,effective boundary,raw share epoch,rate,dividend claim/receivable or liability,actual cash settlement|Unknown pay date is not guessed; a mark missing is not a0 price or a flat position|

Exact API locators and shape/version keys are in [interfaces.json](interfaces.json). Action helpers `src/lstm_data/corporate_actions.py:365` and `src/lstm_data/corporate_actions.py:439` preserve physical share/cash identities; they are reusable primitives, not a portfolio replay engine. Market ACTION_VERSION is a scope-assertion interface tag, not independently certified historical action-vintage evidence.

The nominal origin1 uses10:30 input/reference,10:32 planned issuance,10:33 entry and14:33 exit; hourly exit proxy ends14:30. Origin2 uses11:30/11:32/11:33/15:33 with15:30 proxy. Both intended event holds are240 continuous minutes. Reference time and event time remain distinct, including delayed issuance and actual proxy age. Minute and hourly-close returns/floors must never share target versions.

A synthetic source→step→tensor trace appears in [p2_4_market_trace.json](p2_4_market_trace.json); a full FeatureCalculator→stock→D7→MC0 test supplements the small hand-constructed tensor demonstration. The same market histories feed future MC0 and MC1; no gate/LSTM is implemented. Full own-step source/floor/scaler availability and complete-case stock/masked market invariants precede any admission. `src/lstm_data/ft0_tensor.py:209` takes no future exit or fill; future label changes must not alter forecast/entry population.

## Designed later admission contract (not executed)

| Future phase | Synthetic engineering prerequisites | Real-history rejection conditions |
|---|---|---|
| P3.1 event schema/ledger |New prompt explicitly authorizes synthetic-only mode; isolated synthetic identities, fixed hand cash/share cases|Current handoff hasempirical_work_authorized=false; reject real historical replay and undocumented action/source clocks|
| P3.2 PolicyA sleeves/netting |Explicit synthetic forecasts/entries, canonical timing and independently hand-balanced physical exposures|Do not admit from future label validity; no source/action/raw-conversion/retention/gate bypass|
| P3.3 PolicyB/costs |Whole-pair veto and physical external costs once, declared0/2/5/10bps and borrow scenarios; no new fit|No strategy scoring/backtest or fitted forecast until all real scientific prerequisites and authority pass|
| P3.4 exceptions/risk |Preserve actual outstanding physical shares/uncertain valuation in synthetic cases; later policy decision required for hourly-only event observations|DEF015 blocks claiming minute retries/emergency monitoring or09:30/15:59 benchmark references from hourly closes|

Actual activation later requires genuine source/action/clock evidence, compatible raw proxy conversion, legally available true fitting certificates and approved training population; fixed complete-case/market/retention/regime and mature-label inner-tail guards; attributable joint/course/proxy/SPY approval; separately authorized scientific gate resolution and empirical scope. Reading this handoff or marking all code testsPASS cannot grant that authority. No failed future exit may retroactively delete an entry; missing valuation remains unknown until a genuine permitted mark. Separate scoring labels from physical portfolio outcomes.
