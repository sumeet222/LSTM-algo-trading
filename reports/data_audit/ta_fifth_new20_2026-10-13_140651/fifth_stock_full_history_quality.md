# Fifth-stock full native source quality

**FIFTH_STOCK_FULL_SOURCE_QA_PASS — HUMAN_REVIEW_REQUIRED; SCIENTIFIC_HOLD.**

**CME: 16,261/16,261 expected five-year RTH candles (100.00000%).** 0 missing, 0 runs, maximum 0 half-hours, 0 missing terminal stubs. All 1255 main-period sessions were measured; no unrequested interval is counted as complete.

Prehistory 2019-12-18–2020-06-30: 1,736/1,736, 0 absent in 0 runs across 134 sessions. Dynamic dependency analysis is [hash-bound separately](dependency_prehistory.json); no indicator or label was fitted.

|Year/window|Expected|Observed|Missing|Coverage %|95% guard|
|---|---:|---:|---:|---:|---|
|2020 JUL_DEC|1652|1652|0|100.00000|True|
|2021 FULL_YEAR|3270|3270|0|100.00000|True|
|2022 FULL_YEAR|3257|3257|0|100.00000|True|
|2023 FULL_YEAR|3238|3238|0|100.00000|True|
|2024 FULL_YEAR|3258|3258|0|100.00000|True|
|2025 JAN_JUN|1586|1586|0|100.00000|True|

Overall 98%: True; yearly 95%: True. Main run lengths 1 / 2 / ≥3: 0 / 0 / 0. Prehistory: 0 / 0 / 0. Duplicate, malformed and off-grid RTH records: 0 each after fail-closed schema and key checks. 3864 extra source keys outside audited RTH are preserved, excluded from the grid, not inferred gaps.

## Largest missing runs

|Period|Date ET|Start UTC|End UTC|Half-hours|Terminal|
|---|---|---|---|---:|---|
No missing runs.

## Complete missing-candle inventory

Every missing main or prehistory half-hour follows, grouped by actual Eastern session. This inventory is untruncated. CSVs retain the same maximal run IDs and original source lineage.

No absent expected keys in either full measured interval; the missing-candle, cluster and terminal CSVs contain headers and zero data rows.

Reconciliation: expected − observed = 0 = missing CSV rows (0) = sum of maximal cluster sizes (0). [Per-session prehistory](fifth_stock_prehistory_qa.csv), [exact main/prehistory absences](fifth_stock_missing_candles.csv), [clusters](fifth_stock_gap_clusters.csv), [terminal closes](fifth_stock_terminal_closes.csv), [source signatures](fifth_stock_source_manifest.json).

## Formation and adjustment limitations

The raw genuine 60-session formation proxy is $413,761,647.02/day, passing $50m. [2020 issuer cover](https://www.sec.gov/Archives/edgar/data/1156375/000115637520000039/cme-202033110q.htm) identifies CME Class A/Nasdaq; [June 30 Financial-sector holdings](https://www.sec.gov/Archives/edgar/data/1064641/000175272420177268/NPORT_14151413281152992.htm) corroborate sector and membership, together with the issuer’s earlier S&P addition. This is a retrospective documentary inference, not a July 1 official constituent certificate or then-published availability assertion.

Split adjustment and share-volume identity are exactly those declared in each SIP request. The known five-for-one 2012 action predates required prehistory; exhaustive subsequent action history, action vintage, raw proxy conversion and payment dates are unverified. No numerical raw/split conversion is fabricated from the split archive.

Only completed source intervals and candle keys were audited over 2024-07–2025-06 after the training selection was frozen. No confirmation features, labels, returns or outcomes were accessed for selection, and no second candidate was chosen after opening that horizon. Source clock available_at remains UNKNOWN. Full 48×16 FT0, TG0, M2 and the ≥1352/1502 retention gate remain NOT_MEASURED; source presence alone proves none of them. Original universe and all scientific gates remain unchanged.
