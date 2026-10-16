# Hourly universe shortlist

**Technical primary20, subject to independent rights/adjustment holds:** VZ, COP, BAC, BA, AAPL, PEP, MRK, SBUX, CVX, MS, AMD, KO, JNJ, AMZN, XOM, WFC, AVGO, TSLA, MA, CSCO.

Backups: NKE, V.

Coverage criteria were declared before the census in v1: >=99.5% valid canonical full-hour coverage, no missing entire aligned sessions, max2consecutive scheduled missing hours, no invalid/duplicate rows. V2 excludes explicit issuer-history cautions after the initial census; v3 reserves126complete regular sessions rather than126calendar sessions. this conservative clarification is disclosed, with no return/model criterion. The longest month-boundary interval wins, latest end on ties. Then use publisher-sector ETF round robin, missingness and alphabetical ties. The publisher large-cap claim is a broad unverified liquidity proxy. This surviving-symbol/history-quality selection is retrospective, not PIT membership, sector or issuer certification.

Original candidate names present: AAPL, COST, SBUX; absent: CMCSA, CME. See hourly_symbol_census.csv, hourly_coverage_by_year.csv and per_symbol_coverage.json for ranges and denominators.

Common interval 2022-06-01 through 2026-10-15: 131,214 usable of 131,220 expected stock-hours; 6 missing/invalid (0.004572%).

|Partition|Start|End|Calendar sessions|48h+4h common origins|
|---|---|---|---:|---:|
|train|2022-12-01|2025-03-28|582|1073|
|development|2025-03-31|2026-01-06|194|382|
|held_out|2026-01-07|2026-10-15|195|390|

Warmup reserved 2022-06-01–2022-11-30 (127exchange sessions, 126complete regular sessions). These are conditional row-presence/quality counts, not actual FT0/TG0 eligibility. Original daily/EMA warmups and corporate actions require a separately approved hourly-native methodology. Raw held-out source quality was inspected; model outcomes/targets were never calculated. Freeze held-out dates before modeling and keep them out of selection.
