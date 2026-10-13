# Human review card — new fifth-stock source QA

**FIFTH_STOCK_FULL_SOURCE_QA_PASS — HUMAN_REVIEW_REQUIRED; SCIENTIFIC_HOLD.**

CME is a defensible provisional fifth-stock source candidate: **16,261/16,261 five-year native RTH keys and 1,736/1,736 required prehistory keys**, with zero missing candles, maximal missing runs or terminal stubs. The proposed panel remains incomplete because COST/CMCSA/SBUX full archives are partial. The original universe has not changed.

|Review check|Measured evidence / boundary|Disposition|
|---|---|---|
|1. Exactly twenty new names|Frozen prescribed pool/order, no overlap with earlier 49 + 15; no extra candidate|PASS|
|2. Training-only selection|Five fixed TRAIN dates; 1,300 expected keys, 707 present, 593 absent in 53 runs; five clean names. CME is first clean priority 9; earlier eight fail source screen irrespective of unresolved eligibility|PASS|
|3. Formation dollar liquidity|All twenty have 60 actual raw daily sessions; CME mean $413,761,647.02/day ≥$50m|Retrospective proxy PASS; release timing HOLD|
|4. CME historical security / sector / membership|2020 SEC issuer cover + June30 Financial-sector index-fund holding + issuer S&P addition triangulate CME Class A and Financials; documentary inference explicitly disclosed|Provisional QA qualified; official July1/PIT certification and human universe amendment HOLD|
|5. Full source grid|1,255 main + 134 prehistory sessions; all years100%; no missing/bad/duplicate/off-grid RTH keys; 3,864 extra-session source keys separately excluded|PASS|
|6. Source identity / pagination / resume|SIP USD split30Min asof2025-06-30; raw1Day formation asof2020-07-01. All 73 source pairs terminal/SHA verified; actual zero-GET resume|PASS; publication/action vintage HOLD|
|7. Resource and preservation|73 new +26 carried=99/1000 attempts; no failures/retries/429; 1,798,897 archive bytes before final reports, below256MiB; all 1,527 protected files unchanged|PASS|
|8. Engineering regression|129 Python files:0 basic errors/0 warnings; RuffPASS; focused57PASS; full 613 passed in 1330.95s (0:22:10)|PASS|
|9. Complete provisional panel|AAPL earlier full evidence complete; CME newly complete; COST/CMCSA/SBUX each64 required months unverified. No new acquisition for retained names|INCOMPLETE; separate completion task needed|
|10. Scientific readiness|Full 48×16 FT0/M2/TG0 and ≥1352/1502 retention NOT_MEASURED; source available_at, actions/raw execution, floors/scalers, course/shared signoff HOLD. P2=16, P3=33, seven blockers,0/40; no fitting/performance/Git integration|SCIENTIFIC_HOLD unchanged|

Recommended human decision: accept CME's **provisional source-coverage evidence** and separately scope completion of the three retained archives. Any canonical five-stock amendment and scientific gate clearance require their own reviewed decision. This card authorizes neither. No further candidate was downloaded or compared after opening CME confirmation-era source keys.

[Detailed twenty-name disposition](candidate_20_disposition.md) · [Full candle QA](fifth_stock_full_history_quality.md) · [Five-stock readiness](provisional_five_stock_readiness.md) · [Checks](checks.json) · [Exact provenance](fifth_stock_source_manifest.json).
