# S2-C / S2-D read-only source-coverage and selector feasibility audit

**Audit status: COMPLETE with explicit evidence limits. Original S2-C and S2-D remain BLOCKED under their unchanged fixed protocols.** No experiment was rescued, fitted, calibrated, selected or scored. Ledger remains **158/300**, zero starts consumed.

| Question | Read-only finding | Proposed decision, not adopted |
| --- | --- | --- |
| S2-C complete-triple stock masking (C-A) | Every original overnight origin has at least one supported triple; 95.43–99.74% of stock-origin cells survive in selectors, about99% in restricted prefixes. Primary four-hour panel need not shrink. | Consider one prospective C-A amendment with fixed auxiliary-mask weights; keep primary loss and all evaluation keys unchanged. |
| S2-C independent-head masking (C-B) | All three saved auxiliary validity masks exactly equal the complete-triple flag. No additional independently stored signed labels are available. | Prefer C-A for the smallest change. Genuine independently materialized heads would require a separately approved definition/materialization, not arithmetic recovery in this audit. |
| S2-D strict20 longer selectors | F22 reaches66 sessions from March2021 and F23 reaches65 from May2022, but deficient months persist. | Extension alone does not unblock either fold. Preserve50 and monthly5 unless a different prospective protocol is approved. |
| S2-D stock-masked panel | Current-window sensitivity ≥10 valid stocks yields56/56/56/66 selector sessions; every selector month≥5, and all other role count gates pass. | A genuine masked-panel task is feasible in availability counts, subject to a fixed panel rule, per-stock label verification and matched gap controls. No threshold is approved or optimized here. |

No statistical performance conclusion follows from coverage. The original four-hour CLOCK-C3 reference and all deferred routing/intraday preferences remain untouched. These repeatedly inspected years remain exploratory/post-search even after a later authorized fit.

## Sources, permissions and method

The authoritative source is `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/opening_reaudit_v2/`:

- `S4_ORIGIN_SOURCE_ELIGIBILITY.parquet`: saved origin/session/slot/category/regular-session/input/first-step/label-maturity booleans and timestamps.
- `S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet`: canonical keys, explicit `decomposition_supported`/status, and existing null-validity bitmaps. No scalar price, signed component, target or forecast values are inspected or reported. Parquet necessarily decodes projected columns internally; only `is_valid` is evaluated on their buffers, never numerical payloads. No log return or missing component is reconstructed.
- `S4_SOURCE_POLICY.json` and executed `src/lstm_data/hf20_s4_preflight.py` / `hf20_s4_clock.py`: adjusted, quarantine-filtered final-minute close at actual session close−1minute and genuine next-session09:30 minute open; no15:30 close substitute or hourly proxy. Existing adjustment/source-quality rules are inherited, not recomputed.
- Exact chronology: `reports/experiments/hf20_s9_mag_stage1_session2b_fourfold_2026-10-27/role_counts.csv` and `reports/experiments/hf20_s9_mag_stage1_session3_o1_2026-10-28/role_indices.npz`. Input-grid **date metadata only** is projected from the existing input contract. All20 original role arrays exactly match the executed maturity/first-step derivation; all valid windows span48 scheduled full steps. Tensor order is the20-name saved card order, not alphabetical.
- Binding frozen specifications: prior combined `planning_receipt_v2.json`, C `protocol.json`, D `protocol_v2.json`; archived C/D coverage and `source_validation.json`. The required prior B/C/D reports and Codex handoff were read for context; no forecast Parquet or performance CSV was opened for this audit.

The single component table only has one triple-valid flag; separate stock-level close/open booleans are not stored. Their **null-validity bitmaps** are therefore extracted from the existing saved fields. `true_session_close_complete20` equals the all20 close bitmap exactly. Finite/positive prices and vendor/action semantics are inherited from the already executed source validation; no new numerical price validation is claimed. Every prior strict20 count in all20 fold/role combinations reproduces exactly. A future partial-label materialization must explicitly verify positive finite per-stock source prices and action validity, since null validity alone is not a fresh numerical certification.

Allowed market-source footprint ends2024. XNYS schedule-only lookup extends to January2025 to resolve the next scheduled opening; it reads no2025 market values. No2026 path, contents, hashes or numerical record is accessed. No minute store, provider/network, FT16 rebuild, price acquisition, baseline, target scale, threshold, model/checkpoint or calibrator execution occurs. Git fetch was deliberately omitted under the current no-network instruction; no repository history or registry is changed.

## Archived facts reproduced

All20 original C role counts and all20 original strict20 D role counts MATCH. No discrepancy in blocked totals or frozen definitions was found.

### C: OOS original overnight panel and stock-cell availability

| fold | original_overnight_origins | all20_triple_origins | failed_all20_origins | valid_complete_triples | triple_fraction | one_missing_stock_origins | all20_missing_origins |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 533 | 421 | 112 | 10465 | 98.171% | 72 | 0 |
| 2022 | 665 | 570 | 95 | 13167 | 99.000% | 89 | 0 |
| 2023 | 505 | 389 | 116 | 9978 | 98.792% | 110 | 0 |
| 2024 | 570 | 433 | 137 | 11251 | 98.693% | 125 | 0 |

`failed_all20_origins` counts origins, not missing stock cells. For example, F21 loses112 complete-panel origins but only195 of10,660 stock-origin triples; F24 loses137 origins but only149 of11,400 triples. No original overnight origin has all20 triple labels missing. The count of origins with exactly one missing stock is72/89/110/125 in OOS; missingness is largely sparse within otherwise usable origins.

### D: selectors under the original chronology, descriptive masks only

| fold | panel_rule | eligible_sessions | monthly_minimum | deficient_months | all_frozen_count_and_chronology_gates_pass |
| --- | --- | --- | --- | --- | --- |
| 2021 | partial_ge1_COUNTERFACTUAL | 56 | 15 | — | True |
| 2021 | partial_ge10_COUNTERFACTUAL | 56 | 15 | — | True |
| 2021 | partial_ge18_COUNTERFACTUAL | 56 | 15 | — | True |
| 2021 | partial_ge19_COUNTERFACTUAL | 56 | 15 | — | True |
| 2021 | strict20 | 53 | 15 | — | True |
| 2022 | partial_ge1_COUNTERFACTUAL | 56 | 7 | — | True |
| 2022 | partial_ge10_COUNTERFACTUAL | 56 | 7 | — | True |
| 2022 | partial_ge18_COUNTERFACTUAL | 48 | 4 | 2021-07:4 | False |
| 2022 | partial_ge19_COUNTERFACTUAL | 43 | 3 | 2021-07:3 | False |
| 2022 | strict20 | 31 | 3 | 2021-05:3;2021-06:4;2021-07:3 | False |
| 2023 | partial_ge1_COUNTERFACTUAL | 57 | 7 | — | True |
| 2023 | partial_ge10_COUNTERFACTUAL | 56 | 6 | — | True |
| 2023 | partial_ge18_COUNTERFACTUAL | 56 | 6 | — | True |
| 2023 | partial_ge19_COUNTERFACTUAL | 56 | 6 | — | True |
| 2023 | strict20 | 48 | 4 | 2022-09:4 | False |
| 2024 | partial_ge1_COUNTERFACTUAL | 66 | 14 | — | True |
| 2024 | partial_ge10_COUNTERFACTUAL | 66 | 14 | — | True |
| 2024 | partial_ge18_COUNTERFACTUAL | 66 | 14 | — | True |
| 2024 | partial_ge19_COUNTERFACTUAL | 64 | 13 | — | True |
| 2024 | strict20 | 52 | 9 | — | True |

Strict20 F22 deficient months are **May2021:3, June2021:4, July2021:3**; strict20 F23 is **September2022:4**. The original report described at least one deficient month; this audit identifies all of them. Monthly totals use every nominal month including zero-count months. Prefix roles do not have a monthly5 gate, and OOS requires all12 months, not5 sessions in each month.

## S2-C: masking evidence and limits

C's primary task remains the original absolute240-trading-minute endpoint return. Complete-triple flags were computed on genuine signed pre-close/gap/post-open references. Saved code writes **all three signed component fields only when `decomposition_supported=True`**. Thus C-A and stored-label C-B retain exactly the same cells in every role; independent head masking gives no incremental saved supervision. `pre_reference_pair_present`, `gap_reference_pair_present`, `post_reference_pair_present` in the CSV are only presence counts of primitive reference pairs. They are not materialized genuine signed returns and must not be treated as additional valid head labels or used to infer a missing component from total/other legs.

| fold | role | original_overnight_origins | valid_complete_triples | triple_fraction | min_stock_valid | median_stock_valid |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | inner_train | 6474 | 128566 | 99.294% | 6154 | 6457.0 |
| 2021 | selector | 195 | 3890 | 99.744% | 189 | 195.0 |
| 2021 | restricted_refit | 6697 | 133012 | 99.307% | 6377 | 6680.0 |
| 2021 | calibration | 165 | 3256 | 98.667% | 142 | 165.0 |
| 2021 | oos | 533 | 10465 | 98.171% | 485 | 527.0 |
| 2022 | inner_train | 7103 | 141061 | 99.297% | 6783 | 7084.5 |
| 2022 | selector | 152 | 2901 | 95.428% | 131 | 146.5 |
| 2022 | restricted_refit | 7286 | 144561 | 99.205% | 6960 | 7260.5 |
| 2022 | calibration | 137 | 2729 | 99.599% | 131 | 137.0 |
| 2022 | oos | 665 | 13167 | 99.000% | 614 | 663.0 |
| 2023 | inner_train | 7793 | 154640 | 99.217% | 7467 | 7767.5 |
| 2023 | selector | 177 | 3477 | 98.220% | 161 | 175.0 |
| 2023 | restricted_refit | 7998 | 158667 | 99.192% | 7670 | 7970.5 |
| 2023 | calibration | 139 | 2763 | 99.388% | 134 | 139.0 |
| 2023 | oos | 505 | 9978 | 98.792% | 443 | 505.0 |
| 2024 | inner_train | 8380 | 166238 | 99.187% | 8052 | 8352.5 |
| 2024 | selector | 167 | 3291 | 98.533% | 136 | 167.0 |
| 2024 | restricted_refit | 8578 | 170146 | 99.176% | 8250 | 8550.5 |
| 2024 | calibration | 90 | 1782 | 99.000% | 78 | 90.0 |
| 2024 | oos | 570 | 11251 | 98.693% | 489 | 570.0 |

All retained cells in C-A are also available to all3 C-B heads. Every original overnight origin has some auxiliary supervision and therefore every originally represented overnight session remains represented. Full monthly, all20 stock, slot and normal/early-close marginals are in `S2C_MASKING_COVERAGE.csv`; wide head columns avoid duplicating identical masks. `scope=STOCK` has a one-stock denominator, `scope=MONTH/SLOT/CALENDAR/ALL` has a20-stock denominator. Expanding train/refit populations overlap across folds and must not be summed as independent observations.

### Missing source causes, co-occurrence and concentration

The next table uses mutually exclusive **stock-cell** causes. Its last column separately counts origins having both kinds of failure, possibly on different stocks; it cannot be added to the cell columns.

| fold | close_only_missing | open_only_missing | both_missing | other_missing | origins_missing_both_close_and_open |
| --- | --- | --- | --- | --- | --- |
| 2021 | 122 | 68 | 5 | 0 | 8.0 |
| 2022 | 8 | 125 | 0 | 0 | 0.0 |
| 2023 | 0 | 122 | 0 | 0 | 0.0 |
| 2024 | 0 | 149 | 0 | 0 | 0.0 |

For every role, complete triples + close-only missing + open-only missing + both missing + other missing equals original overnight stock cells exactly. Other unexplained cell failures are0 on these original eligible four-hour keys. Original origin-level close/open receipt counts overlap: e.g.F21 OOS52+68−112=8 origins have both kinds of failure. No failure was double-counted as two missing labels.

OOS source shortfalls concentrate in MS and MRK: together379 of599 missing stock-origin triples across the four separate annual OOS populations (63.27%). Prefix history also has persistent MA missingness; restricted-refit MA coverage is95.22/95.53/95.90/96.18%. Consequently, high aggregate coverage does not imply uniform information across names or missing-at-random labels.

| fold | ticker | original_stock_cells | valid_complete_triples | triple_fraction |
| --- | --- | --- | --- | --- |
| 2021 | MS | 533 | 485 | 90.99% |
| 2021 | MRK | 533 | 510 | 95.68% |
| 2022 | MRK | 665 | 614 | 92.33% |
| 2022 | MS | 665 | 634 | 95.34% |
| 2023 | MRK | 505 | 443 | 87.72% |
| 2023 | MS | 505 | 466 | 92.28% |
| 2024 | MS | 570 | 489 | 85.79% |
| 2024 | MRK | 570 | 526 | 92.28% |

The poorest selector-month retained fraction is90.29% in July2021; September2022 is90.83%. The four ordinary late-clock OOS fractions range97.68–99.25%; late15:30 is98.53/98.78/98.78/98.94%, so the source issue is not confined to15:30. Saved early-close overnight origins are retained by their actual endpoint category, including morning slots:4/3/3/4 OOS origins, triple coverage100/100/100/97.5%. These small strata are not independent replications or proof of causal usability.

### Identity, maturity, weighting and proposed C-A gate

The existing `source_validation.json` reports supported signed additivity maximum absolute error **4.2500725161431774e−16**, tolerance atol1e−12/rtol1e−11. This is **archived identity evidence**, not a recomputation on held-out numerical labels. No unsupported label is inferred. Absolute magnitudes do not add; neither a sum of component magnitudes nor an absolute sum of predicted signed means becomes an expected absolute total.

Original four-hour maturity is endpoint+2min. On supported one-closure overnight paths this is no earlier than component completion; retain the original role maturity/purge and48-step embargo for auxiliary use as well. Input eligibility remains known before labels. Existing adjusted genuine references, quarantine and COP action-basis exclusions remain binding. The mask may affect **training-label loss only**, never neural inputs, routing, primary sample admission, source-quality features or primary scoring. Availability is retrospective label support, not a predictor known at forecast issuance.

A prospective stable convention for discussion: retain the complete20 primary M loss and original hierarchy unchanged. For each auxiliary head, start with original overnight conditional base weights `w=1/(N_sessions * N_origins_in_session *20)`, multiply by its genuine-label mask, and divide by the **global phase sum of masked base weights**. Do not replace missing labels by zero; do not give a stock/session full weight merely because only one label survives. Minibatches would need the declared global denominators and unbiased session sampling; skip missing-label terms. Keep the approved auxiliary coefficient fixed unless separately amended. This convention reduces sparse-cell weight amplification but still estimates a source-selected available-label risk. It does not resolve selection bias or establish improvement.

**C-A coverage is feasible as a proposed new protocol**, preserving every original primary key; the original all20-aux fixed experiment remains BLOCKED. The smallest future decision is explicit approval of C-A, mask normalization and source-label validity checks. C-B's incremental use of primitive pairs remains UNAVAILABLE AS SAVED SIGNED LABELS and would need a separate authorized materialization/provenance decision. No such decision or implementation occurs here.

## S2-D: stock-day coverage, roles and selector-only sweep

D is a separate genuine close-to-next-open gap-magnitude target, one normal full-session15:30 origin per day. Early closes are excluded by calendar, not remapped. The table's close is the adjusted15:59 minute close for a16:00 session end, not a15:30 close. The next opening is genuine09:30; maturity is next-open+2min. A15:32 prediction precedes its holding interval; these are not verified execution fills or P&L.

Stock availability requires both saved reference bitmaps and the original action-basis compatibility. The COP2012-05-01 crossing is excluded for that ticker; strict20 therefore excludes the entire date. Other tickers are only counterfactually available. Crucially, the original **all20 input eligibility flag** still applies to any admitted date; this audit has no per-stock FT16 eligibility flag and never claims to rescue input-ineligible dates. Gap admissions do not borrow four-hour-label eligibility or maturity.

### Current chronology: sessions / retained stock-days

Threshold10 is shown solely as a requested sensitivity example; thresholds1/10/18/19/20 are all saved and none is approved. It is not a selected experimental cutoff.

| fold | stock_threshold | inner_train | selector | restricted_refit | calibration | oos | all_current_role_count_gates |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 20 | 1773 / 35460 | 53 / 1060 | 1833 / 36660 | 43 / 860 | 145 / 2900 | True |
| 2021 | 10 | 2080 / 41274 | 56 / 1117 | 2144 / 42550 | 54 / 1068 | 183 / 3591 | True |
| 2022 | 20 | 1948 / 38960 | 31 / 620 | 1984 / 39680 | 44 / 880 | 176 / 3520 | False |
| 2022 | 10 | 2278 / 45208 | 56 / 1068 | 2342 / 46431 | 47 / 937 | 205 / 4070 | True |
| 2023 | 20 | 2124 / 42480 | 48 / 960 | 2178 / 43560 | 40 / 800 | 147 / 2940 | False |
| 2023 | 10 | 2500 / 49573 | 56 / 1112 | 2564 / 50842 | 46 / 914 | 186 / 3676 | True |
| 2024 | 20 | 2282 / 45640 | 52 / 1040 | 2341 / 46820 | 32 / 640 | 154 / 3080 | True |
| 2024 | 10 | 2692 / 53375 | 66 / 1304 | 2766 / 54838 | 38 / 754 | 202 / 3988 | True |

Frozen gates: initial/refit≥252 sessions; selector≥50 and each nominal selector month≥5; calibration≥25 and each Oct–Dec month≥5; OOS≥100 and all12 months. These are aggregate availability gates, not proof that every individual stock has enough mature history for a new gap baseline. All20 stock-month counts are provided for selector/calibration/OOS; prefix stock marginals and pooled monthly counts avoid repeating the same long history20 times.

### Selector stock-count distribution after input, embargo and maturity

| fold | 0 | 1-9 | 10-14 | 15-17 | 18-19 | 20 |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | 0 | 0 | 0 | 0 | 3 | 53 |
| 2022 | 0 | 0 | 1 | 7 | 17 | 31 |
| 2023 | 0 | 1 | 0 | 0 | 8 | 48 |
| 2024 | 0 | 0 | 0 | 0 | 14 | 52 |

This is why a one-missing-name rule alone is insufficient for F22:7 eligible dates have15–17 valid names and one has14. ≥19 has43 sessions/minimum3; ≥18 has48/minimum4. A prospective whole-stock masked panel could retain56 dates with1,068 stock-days, including these partial dates, rather than throwing away every partially observed day. That is a changed population/score definition requiring approval, not a relaxation already in effect. F23 has one date with only2 source-supported labels; retaining it under≥1 versus excluding under≥10 changes57 to56 sessions, both meeting aggregate gates. A single shared rule must be chosen prospectively, not separate favorable thresholds by year.

### Are labels present but other gates exclude dates?

The following exclusions are sequential, mutually exclusive at the date level: input failure first; then embargo among input-valid dates; then next-open maturity among input+embargo-valid dates. `eligible_sessions` here means any genuine stock gap after all these gates, not strict20.

| fold | candidate_normal_1530_sessions | no_input_sessions | embargo_sessions_among_input | immature_sessions_after_input_embargo | eligible_sessions | retained_stock_days |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | 64 | 0 | 7 | 1 | 56 | 1117 |
| 2022 | 106 | 42 | 7 | 1 | 56 | 1068 |
| 2023 | 85 | 21 | 7 | 0 | 57 | 1114 |
| 2024 | 83 | 10 | 7 | 0 | 66 | 1304 |

F22 loses42 of106 nominal full-session dates because original FT16 panel input eligibility fails, not because every genuine gap is absent. June/July2021 lose12/14 input-ineligible dates. F23 loses21 of85, including14 in September2022; the remaining September genuine-panel count is what leaves strict20 at4 versus7 dates with some genuine stock gaps. Normal source/action/maturity exclusions remain mandatory in all alternatives. This audit cannot distinguish which ticker/channel caused an original input flag failure without new input-level evidence, and does not rebuild it.

### Strict20 month-extension sweep (all alternatives unimplemented)

Initial-training cutoff is the last scheduled session strictly before each nominal selector start. The earlier prefix must independently refit its own FT16/target recipes in any later approved experiment; this audit fits none. The selector ends at the saved September cutoff, first-of48 input-step date must exceed the new initial cutoff, and gap labels mature before the exact saved20:00ET role boundary. September refit, Oct–Dec calibration and next-year OOS roles remain fixed.

| fold | selector_start | initial_training_cutoff | eligible_sessions | monthly_minimum | deficient_months | all_frozen_count_and_chronology_gates_pass |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | 2020-07-01 | 2020-06-30 | 53 | 15 | — | True |
| 2021 | 2020-06-01 | 2020-05-29 | 74 | 15 | — | True |
| 2021 | 2020-05-01 | 2020-04-30 | 94 | 13 | — | True |
| 2021 | 2020-04-01 | 2020-03-31 | 115 | 14 | — | True |
| 2021 | 2020-03-01 | 2020-02-28 | 136 | 14 | — | True |
| 2021 | 2020-02-01 | 2020-01-31 | 153 | 10 | — | True |
| 2022 | 2021-05-01 | 2021-04-30 | 31 | 3 | 2021-05:3;2021-06:4;2021-07:3 | False |
| 2022 | 2021-04-01 | 2021-03-31 | 47 | 3 | 2021-06:4;2021-07:3 | False |
| 2022 | 2021-03-01 | 2021-02-26 | 66 | 3 | 2021-06:4;2021-07:3 | False |
| 2022 | 2021-02-01 | 2021-01-29 | 76 | 3 | 2021-06:4;2021-07:3 | False |
| 2023 | 2022-06-01 | 2022-05-31 | 48 | 4 | 2022-09:4 | False |
| 2023 | 2022-05-01 | 2022-04-29 | 65 | 4 | 2022-09:4 | False |
| 2023 | 2022-04-01 | 2022-03-31 | 85 | 4 | 2022-09:4 | False |
| 2023 | 2022-03-01 | 2022-02-28 | 105 | 4 | 2022-09:4 | False |
| 2023 | 2022-02-01 | 2022-01-31 | 117 | 4 | 2022-09:4 | False |
| 2024 | 2023-06-01 | 2023-05-31 | 52 | 9 | — | True |
| 2024 | 2023-05-01 | 2023-04-28 | 70 | 12 | — | True |
| 2024 | 2023-04-01 | 2023-03-31 | 85 | 10 | — | True |
| 2024 | 2023-03-01 | 2023-02-28 | 86 | 0 | 2023-03:0 | False |
| 2024 | 2023-02-01 | 2023-01-31 | 100 | 5 | — | True |

**Reaching50 is not passing the monthly gate.** F22 March/February extensions reach66/76 sessions, but June2021:4 and July2021:3 persist. Moving before May can remove the May startup embargo deficit; it cannot fix the later deficient months. F23 May extension reaches65, but September2022:4 persists through February. Therefore no tested strict20 extension unblocks F22/F23. F24 March-start itself has a zero March after source/embargo filtering, despite86 total sessions; extending further to February changes the startup embargo and passes. More months do not imply monotonic qualification of every-month coverage.

The full two-dimensional current/extended × strict20/partial-threshold matrix is `S2D_SELECTOR_FEASIBILITY.csv`. Each row separately states50-session pass, monthly5 pass, initial-training≥252 and other frozen role gates, valid stock-days and exact exclusion counts. `all_frozen_count_and_chronology_gates_pass` is a **counterfactual count/chronology result**, not source re-certification or authority to fit. For current chronology, a single descriptive≥10 availability rule passes all role counts in all four folds; ≥18/≥19 do not solve F22. All four current strict20 calibration/OOS/prefix roles already pass; only F22/F23 selectors fail. The partial alternatives also require a prospective matched-panel calibration/weight/baseline definition.

### Minimum prospective changes and later go/no-go

- **F21/F24 D:** original strict20 current selector and all role counts pass; no selector change is required. Any future common masked-panel rule would still change their task population and must apply consistently.
- **F22 D:** extension alone fails. Either obtain additional genuinely documented already-authorized source/eligibility support in deficient months (not done here), or prospectively approve a stock-masked panel. If strict20 is retained and no extra genuine data become available, both a longer selector (March2021 is the shortest tested to reach50) **and** a justified monthly-coverage protocol change would be necessary. The evidence does not warrant lowering50.
- **F23 D:** extension alone fails. Prospectively masked-panel eligibility can meet counts in the current June window; strict20 otherwise requires a May-or-earlier selector **plus** a separately justified September monthly gate decision/source remedy. No rule is lowered here.
- A common masked-panel amendment could keep all existing chronology and frozen50/monthly5 requirements; the threshold/panel acceptance rule is still a human choice. Review stock representation and the2-stock date before deciding. Do not choose using OOS errors or reuse total4h baselines as gap controls.

If later approved, forecast every input-admissible scheduled15:30 origin without using that night's future label support. Score only genuine stock-day labels under the prospectively fixed evaluation mask, with equal available-stock weight within a session and equal session/year weight; disclose changing cohorts and label-selected missingness. Gap LSTM/raw/smear, stock historical mean/median and matured recent20-gap baselines must have **identical evaluated stock-day keys**. Each baseline may use only each stock's historically matured genuine gaps (next-open+2min before forecast), with a fixed minimum-history/missing-baseline rule established before fitting. All stocks/overlapping blocks remain together for later uncertainty. Report per-stock counts; do not use eventual label existence as an inference feature or calibrate on OOS. No gap scale, baseline moment/median, recent-gap statistic, calibration coefficient, threshold or score was computed here.

Future fitting is NO-GO until the researcher separately approves the exact C-A mask/loss normalization and/or D panel/chronology/gates/baseline design, all new per-phase recipes are causal, genuine per-stock label validity and adequate per-stock baseline history are verified, and frozen roles/calibration are disjoint. Do not treat a source-availability audit as validation of a formerly blocked scientific specification.

## Files, checks and handoff

`S2C_MASKING_COVERAGE.csv` gives C all-role, monthly, all20 stock, slot and early-close marginals with explicit C-A/C-B saved-label counts, primitive-reference presence and exclusive causes. `S2C_ROLE_SUMMARY.csv` adds compact original-panel reconciliation and origin cause co-occurrence. `S2D_STOCK_MONTH_COVERAGE.csv` gives D source/temporal and stock/month coverage; `S2D_ROLE_GATES.csv` gives every role/threshold gate; `S2D_SESSION_COUNT_DISTRIBUTION.csv` gives0/1–9/10–14/15–17/18–19/20 distributions before and after temporal/input gates; `S2D_MONTH_THRESHOLD_COUNTS.csv` gives all monthly thresholds; `S2D_SELECTOR_FEASIBILITY.csv` gives the full selector sweep. No per-cell dump or future price/target/forecast export is written.

Focused checks passed: canonical unique origin×stock keys/order; exact20 original role arrays;48-input step lengths;20 C and20 D archived counts; component masks equal stored support; all20-close flag identity; exclusive missing-cell cause accounting and overlapping origin-cause accounting; current selector/sweep count identity; calendar-only next-session maturity and normal15:30 uniqueness; unchanged registry/journal/source/protocol/code hash+mtime bindings. The old signed identity check is referenced only, not rerun. The script imports no repository training module, model, optimizer, scorer or calibration helper. No test-suite or full-repo type scan was run, as instructed for this count-only read-only audit; no project Python file changed. Prior510-file zero-error static result is historical context only, not a new check.

Inspection commands used the repository `.venv/bin/python -B`, a bounded ephemeral script `/private/tmp/hf20_coverage_audit.py` and `/private/tmp/hf20_coverage_report.py`, plus explicit-path `sed`/`rg`, schema/null-count inspection and `git status`/`git diff --check`. Count replay is defined by the receipt's exact source paths/projections, the saved role NPZ, masks and equations above; the ephemeral scripts are not required project code. `audit_receipt.json` records versions/hashes and unchanged158/300 metadata. A short `SESSION_HANDOFF.md` is saved **inside this audit namespace**, honoring the current instruction that no other repository writes are permitted instead of creating a file under reports/codex_sessions.

No preexisting file was amended. No commit/push, no protocol amendment, no model/baseline/calibrator fit or selection, no forecast scoring, no source acquisition/repair, no protected2026 or2025 market read, no deferred route. Original C/D BLOCKED reports remain authoritative. **STOP for researcher review.**
