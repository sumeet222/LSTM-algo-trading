# Package 018D — final human review

**COMPLETE_WITH_QUALITY_FLAGS. NOT TRAINING_READY.**

The human amendment is applied: **July 1, 2010–March 31, 2026**, all **189** pinned monthly files and the exact ordered 20 stocks. No earlier source content was read after the amendment. The 28 completed older months plus the interrupted older month remain preserved outside the active dataset; their 412 data files (100,819,006 bytes) still count toward storage. March 2026 is referenced in place from 018C; no repeated download.

Source: `mito0o852/OHLCV-1m`, revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`, namespace `HF20_HF1M_LONG_v1`. [Identity](dataset_identity_preflight_018D.md), [scope](active_scope.json), [complete file allowlist](complete_acquisition_manifest.json).

|Result|Count|
|---|---:|
|Immutable selected raw rows, including extended hours and conflicts|36,462,461|
|Referenced compressed raw bytes, including reused March|645,966,680|
|Canonical unique valid source rows|36,461,605|
|Conflicting records / distinct conflicting keys|856 / 406|
|Absent expected RTH stock-minute slots|279,180|
|Separate cap-5 price proxies, volume unknown|226,423|
|Hourly and separate stub rows|552,500|
|Bins with no genuine minute, retained as missing|532|
|Apparent action/scale jumps, preserved without adjustment|13|
|Independent raw reconstruction checks passed|97|

All 552,500 bins passed timing, count, OHLC and observed-volume conservation checks. Cap 2 produces 202,794 proxies; cap 5 produces 226,423. These are source diagnostics, never final model masks. [Sensitivity](fill_sensitivity_summary.csv), [hourly QA](hourly_qa_report.md), [issue register](data_quality_issue_register.md), [issue totals with count units](issue_counts_by_type.csv).

## Coverage decision remains open

No tested quality standard supports an **uninterrupted all-20 14-year-9-month** sequence of expected full-hour positions. Even the broad source-present standard's longest run is 7,455 full hours / 1,811 calendar days. A date hull is not continuity proof.

The **unselected** latest-15-year diagnostic interval is March 31, 2011 14:30 ET through March 31, 2026 15:30 ET (outward snapped to actual full-hour boundaries):

|Standard|All-20 retained full hours / 22,528|Fraction|
|---|---:|---:|
|All minutes genuine, complete observed volume, action flags excluded|2,636|11.7010%|
|Bounded price proxies, genuine endpoints, action flags excluded|17,283|76.7179%|
|Partial genuine source presence, action flags excluded|22,465|99.7203%|
|Partial genuine source presence, rare action flags retained|22,477|99.7736%|

The broadest interval still loses 51 full-hour positions. No window or stock was selected/replaced. [All candidate intervals and longest runs](historical_coverage_and_15y_candidates.md).

MA (95.7079%) and AVGO (95.8010%) have the lowest full-history unique-valid RTH minute fractions. Important locations include MA 2013 (81.1172%) / 2025 (90.4425%), AVGO 2023 (89.8610%), and TSLA July–December 2010 (77.5633%). These are source-completeness findings, not independent liquidity or issuer judgments. See [stock summary](ticker_source_quality_summary.csv) and [year detail](ticker_year_coverage.csv).

The [March 2020 halt context](market_halt_context_2020_03.md) and [September 2022 shared-gap detail](large_shared_gap_2022_09.json) distinguish documented market structure from unresolved shared absence. No missing prices or traded volumes were invented for long gaps. All rare observed candles remain recoverable.

## Resources, preservation and next decision

At the resource receipt, maximum measured logical task storage was: 1,571,176,886 bytes. Conservative peak bound including reservations and filesystem padding: **2,173,868,560 bytes**, below 10,000,000,000. Native instrumented response bodies: **34,125,064,103 bytes** (33,284,003,156 active; 840,902,137 preserved legacy; 158,810 metadata). This excludes unmetered redirect bodies/transport/web-research overhead and is not total wire traffic. Peak recorded source-worker RSS: 724,877,312 bytes; final-report RSS: 589,266,944 bytes. Final small receipts/inventory are covered by the reserved 10 MB; end-of-closeout bytes are in final_closeout_receipt.json. [Resource receipt](resource_summary.json).

All 4,601 protected preexisting files / 460,380,048 bytes are hash-identical. All active months use the same QA arithmetic engine. The first final audit child completed; its timing wrapper encountered a sandbox sysctl denial. The native offline replay exited zero, with no downloads. Repeated register summaries are verification receipts, not additional defects.

39 focused tests pass; full basic-severity Pylance/Pyright parity is 274 files, zero errors/warnings; Ruff and Git whitespace checks pass. Editor refresh remains human-confirmed. [Verification](tests_and_static_receipt.json), [execution code binding](execution_code_receipt.json), [preservation](preservation_after.json).

No features, labels, fitted scalers/epsilon, final chronology, forecasts, models, backtests or trading were created. Ledger remains **32/200**, with zero new starts. Old Alpaca, Twelve Data and model outcome stores are unchanged. New-source quality was inspected retrospectively, including overlapping dates; no pristine-unseen raw-data claim is made.

Human review must choose whether and how to tolerate missingness, incomplete observed volume, action/adjustment and issuer uncertainty before a separately scoped feature/target and training task. User-reported maintainer permission remains **HUMAN_REPORTED_MAINTAINER_PERMISSION_FOR_PRIVATE_RESEARCH**, not independent licensing or redistribution certification. All numerical stores, price cursors and examples remain local/ignored.

## Paths, sizes and checksums

The raw/derived file allowlists carry every active numerical path, row count, byte size and SHA256; never glob physical roots containing preserved older files. `artifact_inventory.csv` inventories the whole package, with Git intent and legacy hashes reused from old receipts rather than reading older source content. The inventory does not self-hash; `final_closeout_receipt.json` binds it and this card.

|Review artifact|Bytes|SHA256|
|---|---:|---|
|[active_scope.json](active_scope.json)|1,424|`58962ddf19face3bd39a0e4888e9ed002168f608c53ff167efc92009f0fd2e01`|
|[complete_acquisition_manifest.json](complete_acquisition_manifest.json)|676,192|`2b8f9165b0387acaf650d1f1514afb8b41d081aacc9b2056b2f6efa496adf40c`|
|[execution_code_receipt.json](execution_code_receipt.json)|1,555|`0308e9488ebd463d79d8becc28d2794c562f88538bfa58dbfd7833d5c6559fde`|
|[resource_summary.json](resource_summary.json)|1,751|`2329f09ec01781d7f5a3b413fa8736eddac977cce0f5aa16bd764f9bcc743967`|
|[historical_coverage_and_15y_candidates.md](historical_coverage_and_15y_candidates.md)|6,006|`24e497bf683e1f369d4cb59d5ab085577e87d02ac58e27830a5900f306834f1a`|
|[hourly_qa_report.md](hourly_qa_report.md)|1,516|`411d2cac790d13c8b4dbd631d95a322e9e6c4018cbc88470c76d72025b8373b7`|
|[data_quality_issue_register.md](data_quality_issue_register.md)|106,129|`8bd61716bedbc99552954a92506b880011ff98484499bd0d7c112125b0e3245b`|

[Reproduction and resume handbook](../../../docs/track_a/HF1M_LONG_SOURCE_018D.md). Session handoff: `reports/codex_sessions/2026-10-22_184817_ta018d_hf1m_long.md`. All task changes remain uncommitted; no Git index, branch, integration or push mutation.
