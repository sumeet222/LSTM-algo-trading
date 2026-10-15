# Consolidated human review — 15 checks

**Readiness packet complete; scientific HOLD. D1 is proposed, no activation or training.** Review this card and the focused D1 question; no other consolidated card is generated.

| # | Human check | Observed / disposition | Evidence |
|---|---|---|---|
|1|D1 proposal|Original AAPL/JPM/JNJ/WMT/CAT preserved. Proposed AAPL/COST/CMCSA/SBUX/CME, pending accept/reject/conditional decision; selected 2026-10-13, historical formation 2020-07-01.|D1_Amendment_Proposal.md; D1_decision_card.md|
|2|AAPL and COST native source QA|Each 16,261/16,261 main +1,736/1,736 prehistory. PASS_KEYS; numeric QA through 2024-06, confirmation numeric result inherited only.|five_stock_native_quality.csv; complete_five_stock_qa.json|
|3|CMCSA, SBUX and CME native source QA|Same exact counts each. All 201 archive/manifest pairs verified; all five annual key guards pass;9 main early closes+1 prehistory early close each.|source_hash_verification.json; complete_five_stock_qa.json|
|4|Zero inserted candles|0 missing,0 fills,0 unresolved; current bound engineering CSVs referenced, not regenerated or promoted.|overlay_reconciliation.json|
|5|Formation/provenance/rights|Exact60 preceding sessions; all raw daily liquidity means > $50m. Retrospective proxy only; membership/security-class/sector completeness and scientific-use/reproduction rights HOLD.|formation_liquidity_qa.json; formation_identity_evidence.json|
|6|Corporate actions and units|AAPL genuine split and dividends sampled; 4× volume exact, raw price discrepancies up to$0.02. COST one equal raw/split candle; four new-name complete action histories absent.|corporate_action_unit_samples.json|
|7|Stock publication|Native archived schema has no historical available_at; UNKNOWN. A caller's arbitrary DOCUMENTED assertion cannot authenticate a publisher.|source_and_clock_status.json|
|8|SPY versus course|Same11 SPY SIP raw30Min archives,17,197/17,197 RTH keys. SOURCE_SELECTED engineering proxy, not sixth stock/course certificate. Shared/course/publication approvals pending.|spy_source_identity.json; ledger_reconciliation.json|
|9|Minute execution|AAPL has 10 required-clock records across3 raw sample days; COST/CMCSA/SBUX/CME 0. Incomplete coverage; no actual fill inference.|minute_reference_inventory.json|
|10|G2 chronology and C01|Ordinary/DST/early-close/split and cross-session lag examples. Calendar PASS; source/maturity HOLD. Issuance/entry/label/exit remain separate.|audit_chronology.csv; audit_chronology.md|
|11|G3 real disposition|NOT_RUN/BLOCKED. No canonical real FT0/TG0/M2/market features, scalers/floors/target/prediction artifacts. Existing guards preserved.|g3_retention_status.json|
|12|Retention honesty|1,502 train and248 per WF are upper bounds; genuine eligible numerator unknown.1352minimum meaningful only once this denominator and exact source/target/population are approved.|calendar_source_upper_bound.json; g3_retention_status.json|
|13|Storage / no duplicate|599raw files19,232,923bytes conserved; no newParquet/checkpoints/price panels or source copies. Exact package/disk delta and inventory sealed at closure.|protection_and_resources.json; changed_paths_sha256.csv|
|14|Confirmation protected|Only schema/keys and byte hashing full horizon; numeric source audit ends2024-06-30. No confirmation features/labels/returns/predictions/selection/economics.|protection_and_resources.json; reproduction.md|
|15|Git/tests/ledgers|Clean aligned start atbb654a8; reports only uncommitted.218 fresh focusedPASS, types 155 files0 errors / 0 warnings, Ruff PASS.703 full PASS inherited on identical code hash.16P2/33P3/7blockers/0 pairs unchanged.|checks.json; inherited_full_suite_binding.json; mandatory session report|

Decision: approve / correct / hold this audit packet, and answer the explicit ACCEPT / REJECT / CONDITIONALLY ACCEPT D1 question. **Recommendation: conditionally accept the proposed candidate universe while keeping production inactive until the stated evidence and migration conditions are satisfied.** No signature is recorded.

What Codex needs next: a scoped D1 decision and separate versioned registration authority, followed by independently supported source/action/publication/rights and shared/course/proxy evidence. Then authorize a genuine, guarded canonical G3/fitted-transform package and audit actual retention; after applicable G0–G5 prerequisites and engineering review, separately authorize exactly the first seed42 June2023 P4.3 pair. D1 acceptance alone authorizes none of those scientific steps. No new provider access, model pair, conditional branch, confirmation access or Git integration is requested by this card.
