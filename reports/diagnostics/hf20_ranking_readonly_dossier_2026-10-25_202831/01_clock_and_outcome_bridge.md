# 01 — Clock and outcome bridge

**QUALIFIED: present-contract arithmetic/geometry PASS; historical publication timing remains unverified.**

All findings are descriptive. Inner training/refit are in sample; inner validation is selection-influenced; development is 109 repeatedly inspected sessions, not confirmation. No new model, objective fit, labels, inference or trading.


| role | first_session | last_session | origin_count | session_count | earliest_origin | latest_maturity | target_operands | clock |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | 2011-04-01 | 2023-01-23 | 4428 | 2513 | 2011-04-01 14:30:00+00:00 | 2023-01-23 20:32:00+00:00 | PASS 20-return median/MAD/numerator | PASS exact scheduled geometry |
| inner_validation | 2023-02-03 | 2025-06-30 | 766 | 459 | 2023-02-03 15:30:00+00:00 | 2025-06-30 19:32:00+00:00 | PASS 20-return median/MAD/numerator | PASS exact scheduled geometry |
| refit | 2011-04-01 | 2025-06-30 | 5210 | 2980 | 2011-04-01 14:30:00+00:00 | 2025-06-30 19:32:00+00:00 | PASS 20-return median/MAD/numerator | PASS exact scheduled geometry |
| development | 2025-07-15 | 2025-12-31 | 183 | 109 | 2025-07-15 15:30:00+00:00 | 2025-12-31 20:32:00+00:00 | PASS 20-return median/MAD/numerator | PASS exact scheduled geometry |

The contract is [model_input_contract.json](../../../reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122/model_input_contract.json); clock semantics and original source assumptions are in [P020_TARGET_TG20_AND_CLOCK_AUDIT.md](../../../reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122/P020_TARGET_TG20_AND_CLOCK_AUDIT.md), [P020_IDENTITY_AND_FROZEN_SPLITS.md](../../../reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122/P020_IDENTITY_AND_FROZEN_SPLITS.md) and `src/lstm_data/hf1m_ft16_prepare.py`. Exact hashes are in input_manifest.json.

For every admitted origin, the input ends at 10:30 or 11:30 ET, issuance is 10:32 or 11:32, the original label starts at 10:30 or 11:30 and ends at 14:30 or 15:30, and maturity is two minutes after the exit endpoint. Both endpoint closes must be genuine and in compatible price units for all20 stocks. No forward-filled target, overnight horizon or stub label is permitted. The source available_at field is literally UNKNOWN_ASSUMED_END_PLUS2_ISSUANCE; the two-minute lag is an assumption, not an independently measured publisher timestamp.

**Interpretation:** two minutes of the reference price-only label interval have elapsed by modeled issuance. We have not calculated an alternative entry return. These outcomes remain useful for the declared historical forecast task, but are not automatically returns achievable by a post-issuance trade. This is a disclosed target/issuance convention, not a reproduced violation of a frozen code invariant. A future genuinely post-issuance ranking interval needs explicit endpoints and approval before labels/fits; no silent historical repair.

[clock_cases.csv](clock_cases.csv) contains both morning slots with all48 UTC clocks, publication assumption, issuance, endpoint and maturity. [calendar_edge_cases.csv](calendar_edge_cases.csv) adds predeclared first early-close/holiday/weekend input cases in each role; 2011-11-28 includes the genuine 2011-11-25 short session. [preserved_source_witness_checks.csv](preserved_source_witness_checks.csv) reconciles all22 existing source examples:52 candles each,48 input+4 future and20 target return operands. Original price factors/source row hashes and native/fallback values remain in the referenced private stores, not copied. A7/A12 use the same22 events.

A first development origin at11:30 on2025-07-15 has a48-step window crossing a94-hour holiday/weekend gap. Scheduled adjacency therefore is not wall-clock adjacency. Nov2015 minute witnesses explicitly use UTC−05 after DST; July2025 uses UTC−04. Pre2026 inner-validation and development embargoes retain48scheduled full hours; maturity and admitted-role dates were checked separately. Refit includes earlier validation dates and is not a fourth independent test.

## Feasibility matrix — architecture-free, no new target calculations

| Candidate | Price/input support | Required decision and purge | Status |
| --- | --- | --- | --- |
| Current4h,10:30/11:30 endpoints | genuine hourly closes;48scheduled history | preserve current issuance/price-only qualification | VERIFIED_CURRENT_CONTRACT |
| 1h/2h at later full-hour endpoints | canonical historical hourly endpoints and minute support exist; per-origin/stock validity not built | freeze origins, post-availability start, early-close rules; purge actual matured horizon | DESIGN_FEASIBLE_CONDITIONAL |
| Later4h same-session origins | only origins with four genuine remaining full hours qualify; afternoon origins cannot all satisfy this | no compressed clock, close/stub or overnight substitution | LIMITED_SAME_SESSION_SUPPORT |
| Current-session remainder | endpoint may need genuine16:00/13:00 stub close | variable duration and exact close observations; later maturity | UNFROZEN |
| Next-session same clock | requires overnight gap and next actual session | specify calendar, action units, dividends and overnight semantics; longer purge | SOURCE_VINTAGE_UNVERIFIED |
| Next open/close |15:30 surrogate is not16:00 official close; hourly open is first source minute reference | verify exact opening/closing observations and availability; no invented close | UNFROZEN_SOURCE_CONDITIONAL |
| Multi-session | changing actions, exits, missing outcomes and overlapping maturities | freeze endpoint/maturity before any fit; protected2026 endpoints remain forbidden even from late2025 origins | REQUIRES_SEPARATE_LABEL_AUTHORITY |

Minute resolution, hourly forecast cadence, outcome horizon and eventual holding time are separate axes. This matrix is not a coverage census, label set, trade/fill model or authorization.
