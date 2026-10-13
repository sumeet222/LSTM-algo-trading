# Human review — ranking authority

**NO_VERIFIED_FIVE_STOCK_UNIVERSE — Gate1 HOLD.** No new Alpaca requests.
AAPL remains the required planned anchor; four other names have not been selected.

|Check|Evidence|Disposition|
|---|---|---|
|1. Requested rank source|[audit](rank_source_audit.md).No certified historical constituent float/market-cap ordering with required identity/sector fields was authenticated.|HOLD before acquisition|
|2. Authentic dated alternative|[source evidence](ranking_source_evidence.json).SPY snapshot March31,2020; SEC filed June1,2020, before July1 formation.92-day-old snapshot, not June30 weights.|Historical fallback only|
|3. Exact extraction|505 unique security names; sum $235,256,200,309 exactly equals disclosed common-stock total; publisher PDF185281bytes with SHA.|PASS factual extraction|
|4. Deterministic proposed order|[checks](rank_extraction_checks.json).Independent Python/Pandas sort and input-order reversal agree.USD value descending, exact-name tie.|PASS proposal arithmetic; not approved S&P rank|
|5. Share classes|[full CSV](ranked_formation_constituents.csv).Proposed greater-valued class per named issuer yields500 issuers.Original505 facts retained; excluded weights not renormalized or aggregated into retained class.|Rule requires approval|
|6. Mapping and membership|Ticker/ID/per-security GICS not in report; March holdings do not certify July1 membership.Only user-fixed AAPL label supplied. Later delisted/renamed names retained.|NOT_VERIFIED; no current fill-ins|
|7. Scope of weights|Fund holding value/full equity total is a fund-weight proxy; no issuer float shares or issuer market cap supplied. No certified S&P weight claim.|HOLD on requested ranking criterion|
|8. Greedy and cleanup branches|[trace](greedy_selection_trace.json).0 visited/accepted candidates; empty Gate2 CSVs mean NOT_STARTED.1–2-candle branch not activated; terminal T2 and>=3 major-gap rules preserved.|No inferred native/FT0 pass|
|9. Baseline conservation|[source manifest](immutable_source_manifest.json).Original168/15 and inactive1183/1502 inherited; prior1340/1502 bound only for29-name pool, not every S&P stock.|Not fresh metrics or broad impossibility claim|
|10. Resources and confirmation|0/1000 Alpaca attempts;0 new stock-archive bytes; public PDF temporarily185281bytes. No credentials, source OHLCV acquisition, labels, fitting, economics or confirmation analysis.|Within caps; science HOLD|
|11. Engineering/Git conservation|[checks](checks.json), [preservation](preservation.json).Fresh121-file Pyright0errors/0warnings; Ruff PASS; prior584 tests bound to identical code/test hashes, not redundantly rerun. 1348 original files unchanged;16 P2/33 P3/7 blockers/0-40 preserved. No production Python/config edits or Git integration.|PASS documented limited scope|
|12. Human decision|[specific proposals](fallback_proposal.md).Approve historical March31 fund-weight sensitivity, hold for qualified historical index data, or explicitly approve separate current-rank sensitivity. Neither approves cleanup or a stock switch.|Required by prompt §1.2|

Your prompt §1.2 says: “If no defensible historical constituent ordering can be
established” then “STOP before live rank-led acquisition and request human approval
of a specific fallback.” We have authentic historical holdings, but not the
specified float/market-cap data. Adopting their fund-weight order changes the
ranking criterion and requires this decision. The next session should reuse the
hash-bound proposal and preserve all scientific holds.
