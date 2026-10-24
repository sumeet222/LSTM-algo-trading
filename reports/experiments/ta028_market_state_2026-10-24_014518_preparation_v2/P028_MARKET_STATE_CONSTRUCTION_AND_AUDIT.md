# P028 market-state construction and audit — complete preparation

These are exactly the two authorized **panel-derived proxies**, including each focal stock. They are not independent market-index data. Stock FT16/TG20/source/phase recipes/fallbacks/eligibility remain unchanged; no additional model feature, new source, new scaler/floor or learned state filter is introduced. Diagnostic regime labels and summaries are not additional model inputs. No training or candidate prediction is authorized or produced. Ledger59/200 remains unchanged.

Formula at each historical step: m1=mean20(existing phase-scaled/fallback M1); m2=median20(existing phase-scaled/fallback V1). Median of20 means average of sorted positions9/10 (zero-based). All20 finite original scaled inputs required; no changing ticker pool or second imputer. Canonical stocks/channels are bound by the unchanged P020 contract. State pooling is invariant to simultaneous stock-coordinate permutation, verified over every decoded historical prefix. Independent sum/sorted-midpoint oracles reproduce state values exactly.

| role | origins | sessions | retained | M1_fallback_cells_pct | V1_fallback_cells_pct | windows_crossing_vol_cut_pct |
|---|---|---|---|---|---|---|
| inner_train | 4428 | 2513 | 100% | 2.69587 | 4.8569 | 62.6016 |
| inner_validation | 766 | 459 | 100% | 4.78691 | 6.25462 | 87.859 |
| refit | 5210 | 2980 | 100% | 2.99712 | 5.05852 | 66.3532 |
| development | 183 | 109 | 100% | 2.99693 | 3.70048 | 94.5355 |


Timing PASS is conditional on the existing P020 source/publication assumptions, not independent verification of vendor available_at. Every used historical key ends by the origin; issuance is exactly origin end+2 minutes, and48 scheduled steps include actual overnight/holiday wall-time gaps. No bar retiming or overnight fill was added. Native→original fallback→original scaler reconstructs both channels exactly in each phase; the existing float32 stock inputs are pooled in float64 then rounded once to float32. Training uses its existing retrospective prefix-fitted scaler; this does not claim that those later fitted training parameters existed at every earlier training date. Validation uses the inner train recipe (cutoff2023-01-23), development the refit recipe (cutoff2025-06-30); neither fits a transform on its outcomes.

Retention is against the existing frozen role populations, not a new point-in-time membership certification. State construction runs over the historical source prefix independently of labels; only afterward are the fixed admitted windows selected for coverage. All20 input stocks remain present regardless of their future returns. No target Parquet was numerically decoded, no future endpoint close/return/MAD/target or label flag enters either proxy, and no protected2026 feature prefix was decoded. The unchanged target/confirmation files were checked as bytes only. Existing retrospective action/quarantine/population-selection caveats remain.

Fallback cell percentages above use origins×48×20, not the fraction of windows. A window can contain a small number of original fallback cells: inner train M1/V1 windows4160/4228 of4428; validation762/757 of766; refit4938/5001 of5210; development151/155 of183. This is inherited missingness exposure, not permission to remove those windows, infer observed values, or add mask channels.

Both channels vary within windows: mean within-window SDs (M1,V1) are inner(.98560,.37393), validation(.85767,.35866), refit(.97165,.37406), development(.74186,.36367), in their phase-scaled units.63–95% of windows cross the proposed volatility cut depending on role (see exact table). This flags endpoint-reinterpretation versus stepwise-state differences but does not choose MC2 or authorize an extra fit. MC1 remains the proposed single A7 variant. Raw state/endpoint distributions, endpoint-minus-first movement, clock ages and self-inclusion differences are recorded in the machine audit/private stores.

Mean20 self inclusion gives each own M1 a1/20 contribution. Median20 self inclusion is order-dependent, not a constant1/20 derivative. Leave-one-out differences are audit-only calculations; they are not replacement input channels. A7/A8/A12 therefore receive extra compressed peer information relative to stock-only T2. No independent market-state or causal stock-to-stock interpretation follows.

Proposed A12 support uses the first available origin per session (10:30 if available, otherwise11:30), and LOW≤training-session median of proxy2/HIGH>cut. Exact original exchange-session adjacency breaks runs at missing eligible sessions; maximal runs are never split into falsely independent episodes. Inner median−.06340353935956955, refit median−.03880869597196579. Inner cut stays fixed for validation; refit cut stays fixed for development. These are phase-specific scaled-volatility thresholds, not economic bull/bear labels or expert identities.

| role | threshold | state | sessions | runs_at_least5 | longest_run | policy_result |
|---|---|---|---|---|---|---|
| inner_train | -0.0634035 | HIGH | 1256 | 61 | 96 | PASS_UNAPPROVED_RULE |
| inner_train | -0.0634035 | LOW | 1257 | 81 | 50 | PASS_UNAPPROVED_RULE |
| inner_validation | -0.0634035 | HIGH | 309 | 24 | 21 | PASS_UNAPPROVED_RULE |
| inner_validation | -0.0634035 | LOW | 150 | 5 | 7 | PASS_UNAPPROVED_RULE |
| refit | -0.0388087 | HIGH | 1490 | 83 | 96 | PASS_UNAPPROVED_RULE |
| refit | -0.0388087 | LOW | 1490 | 94 | 50 | PASS_UNAPPROVED_RULE |
| development | -0.0388087 | HIGH | 74 | 8 | 13 | DESCRIPTIVE_ONLY |
| development | -0.0388087 | LOW | 35 | 1 | 5 | DESCRIPTIVE_ONLY |


All three training/selection roles satisfy the **previously proposed, still unapproved** support policy (fitting≥50 sessions/≥5 maximal runs of≥5 sessions per state; validation≥20 sessions/≥2 runs per state). Development's low state has35 sessions but only one qualifying run. Its74/109 high-state occupancy and validation309/459 high occupancy, versus roughly50% at fitting, show drift/support limitations. Development is descriptive only and cannot activate/deactivate A12 or change thresholds. Episode counts are not independent statistical samples or evidence of predictive regimes; router/expert exposure must still be checked after any separately approved fit.

First audit passed numerics but the static checker found four inferred-type diagnostics in a heterogeneous support dictionary. Typed local state counters fixed them without changing formulas. A stronger full-prefix permutation assertion and recipe/source hash binding were added. A new immutable audit namespace passed and all role state fingerprints match the first run exactly. Both versions/logs remain. The final current-code audit receipt/cache references below are authoritative; no model run, retry or research start occurred.

Current proof: `ta028_market_state_2026-10-24_014518_preparation_v2_verified_audit_v2/market_state_audit.json`. Private state files contain only authorized proxies and origin/clock metadata, not copied raw-minute prices or targets. Source/model code/journal and all5,089 prior sealed inventory entries still match. There is no feature or outcome certification beyond the stated source assumptions.
