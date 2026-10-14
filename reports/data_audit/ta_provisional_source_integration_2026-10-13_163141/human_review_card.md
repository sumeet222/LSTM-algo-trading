# Human review — provisional five-stock source and candle engineering

**NATIVE SOURCE COMPLETE; ENGINEERING VIEW COMPLETE; HUMAN REVIEW REQUIRED; SCIENTIFIC G0–G4 HOLD.**

Proposed order: **AAPL, COST, CMCSA, SBUX, CME**. Each has16,261/16,261 main RTH candles plus1,736/1,736 prehistory candles. All five combined:89,985/89,985, **zero genuine gaps, clusters or longest runs; zero synthetic insertions; zero unresolved candles**. No all-gap placeholders were needed on real data. Primary D1 remains AAPL/JPM/JNJ/WMT/CAT.

|Review|Evidence to inspect|Disposition|
|---|---|---|
|1. Starting ownership|Clean tree at5c0455cdccaf03ae2c6834d8cdaa7dc3115f6c27; prior15/20-name packages committed and SHA-protected|PASS|
|2. Old HOLD authorization|Exact March three-symbol replacement explicitly approved; old four-name HOLD and99 charges untouched|PASS|
|3. Bounded completion|64 new month pairs,193HTTP200 pages, zero failures/retries/429; cumulative292/1000; all64 pairs actual zero-GET resumed|PASS|
|4. Main population|5×16,261=81,305 true RTH keys; every year100%; zero absent/duplicate/malformed/off-grid RTH keys|PASS native presence only|
|5. Prehistory population|5×1,736=8,680 keys across134 sessions per stock; original first three retained month pairs reused|PASS|
|6. Hand-count calendars|1255×13−9×6=16261;134×13−1×6=1736; real early-close/DST controls match allfive|PASS|
|7. Raw conservation|Independent direct Parquet read equals all89,985 materialized OHLCV/trade-count/VWAP records numerically; original ParquetSHA unchanged|PASS|
|8. Actual overlay|Sparse header-only fill/unresolved files; source grid was fully measured before these zero counts|PASS identity view|
|9. Any-length gap cases|Injected1/2/3/12/13/26/39 runs, whole/first sessions, mixed/reordered/larger universes, early close/DST, no future/imputed anchor|PASS synthetic tests|
|10. Unknown volume / terminal / halt|Synthetic volume, trade count and VWAP null; observed zero remains observed; terminal and halt placeholders cannot become genuine T2/execution|PASS guards|
|11. Split and anchor hand case|Unknown/crossed unit epochs unresolved; synthetic7-slot early-close day uses prior genuine anchor, wallage2490min versus marketages0..180|PASS engineering case; real units/vintage HOLD|
|12. Integration and stale identities|Explicit engineering mode only; P3/P4 UniverseSpec geometry compatible, data conversion blocked; source/policy/order/code/floor/target/preparation identities bound|PASS engineering isolation|
|13. Verification|134 Python files:0 basic errors/0 warnings; RuffPASS; focused88PASS; full635 passed in 1428.85s (0:23:48). Original tests preserved|PASS|
|14. Scientific and primary decisions|16P2/33P3 deferrals, seven blockers,0/40 preserved. FT0/48-step/T2/TG0/M2 actual admission and train retention NOT_MEASURED; formal D1 amendment/course/collaborator/publication/actions/raw execution/fitting approvals pending|SCIENTIFIC_HOLD|

Review the native archive and isolated engineering API. Any primary universe activation, fabricated-data scientific admission, real floors/scalers/features/targets, forecasts/fits/trading and scientific gate transitions need separate explicit decisions. [The draft amendment](../../../docs/track_a/decisions/Track_A_Provisional_Universe_Engineering_Amendment_DRAFT_v1_2026-10-13.md) changes no frozen protocol.

[Source QA](genuine_source_qa.md) · [Cleanup summary](candle_cleanup_summary.md) · [Fills](candle_fills.csv) · [Unresolved](unresolved_candle_gaps.csv) · [Genuine source lineage](complete_genuine_source_manifest.json) · [Overlay binding](candle_overlay_binding.json) · [Checks](checks.json).
