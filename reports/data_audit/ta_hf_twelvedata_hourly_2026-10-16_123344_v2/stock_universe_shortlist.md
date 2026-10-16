# Hourly source universe shortlist

**Technical primary20, conditional on unresolved source/rights/methodology:** VZ, COP, BAC, BA, AAPL, PEP, MRK, SBUX, CVX, MS, AMD, KO, JNJ, AMZN, XOM, WFC, AVGO, TSLA, MA, CSCO.

Backups in deterministic order: NKE, V.

Coverage thresholds were declared before the census in v1; v2 adds the disclosed issuer-caution exclusion: at least99.5% valid canonical full-hour coverage, no missing entire aligned sessions, maximum2consecutive missing scheduled hours, no invalid/duplicate source rows. Search all month-boundary intervals; choose longest, latest end as tie break. Within that interval use static publisher-sector ETF round robin, missingness then alphabetical ties. No return/target/model metric selected the cohort. The publisher's large-cap description is a broad liquidity proxy, not independent liquidity/market-cap certification. Current surviving symbols and full-history quality selection create explicit survivorship/retrospective-selection bias. Static sector ETF labels are not PIT membership.

Original candidate names present: AAPL, COST, SBUX; absent: CMCSA, CME. This does not change production D1 or the accepted five-stock source.

Common interval 2022-06-01 through 2026-10-15: 131,214 usable of131,220 expected stock-hours; 6 missing/invalid (0.004572%).

|Partition|Start|End|Calendar sessions|48h+4h complete common origins|
|---|---|---|---:|---:|
|train|2022-11-30|2025-03-28|583|1075|
|development|2025-03-31|2026-01-06|194|382|
|held_out|2026-01-07|2026-10-15|195|390|

Warmup reserved 2022-06-01–2022-11-29 (126exchange sessions). This is a methodology proposal; original FT0 long daily/EMA warmups and action treatment need a new audited version. Origin counts are conditional presence/quality geometry, not actual FT0/TG0 eligibility or target observations. Raw vendor-held-out files were audited for source quality; no held-out model outcomes/targets were calculated. Freeze these dates before any future modeling; do not use held-out outcomes for selection.

Numerical year matrix: hourly_coverage_by_year.csv; exact per-name ranges/denominators: hourly_symbol_census.csv and per_symbol_coverage.json.
