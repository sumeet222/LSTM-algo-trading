# S4-A complete diagnostics and plots

Current status: **8/8 complete; ledger 114/200; final numerical, browser and static checks PASS**. This index distinguishes final analysis from preserved preparation evidence.

## Main research and detailed diagnostic reports

- [S4_FINAL_RESEARCH_DECISION.md](S4_FINAL_RESEARCH_DECISION.md) — Scientific conclusion, annual/control/category comparisons and limitations.
- [S4_DETAILED_TRAINING_VALIDATION_REFIT_OOS.md](S4_DETAILED_TRAINING_VALIDATION_REFIT_OOS.md) — All eight models × four roles; every epoch, selection, refit and gradients.
- [S4_EXTREME_OBJECTIVE_NUMERATOR_MAD_DIAGNOSTICS.md](S4_EXTREME_OBJECTIVE_NUMERATOR_MAD_DIAGNOSTICS.md) — All roles: original TG20 extremes, actual-objective tails, complements, NUM/MAD and energy.
- [S4_VISUAL_AND_SCIENTIFIC_DIAGNOSTICS.md](S4_VISUAL_AND_SCIENTIFIC_DIAGNOSTICS.md) — Collective numerical/visual summary.
- [HISTORICAL_S1_S2_RANKING_VISUAL_DIAGNOSTICS.md](HISTORICAL_S1_S2_RANKING_VISUAL_DIAGNOSTICS.md) — Separate saved S1/S2 analysis; original diagnostic links and failures.
- [DIAGNOSTIC_FILE_INDEX.csv](DIAGNOSTIC_FILE_INDEX.csv) — Every task artifact with byte count, SHA256, stage and privacy classification.
- [HISTORICAL_COMPLETE_DIAGNOSTIC_FILE_INDEX.csv](HISTORICAL_COMPLETE_DIAGNOSTIC_FILE_INDEX.csv) — Every referenced archived S1/S2 diagnostic/analysis file.
- [S4_LIVE_FINAL_VERIFICATION.json](S4_LIVE_FINAL_VERIFICATION.json) — Final actual completion, source/ledger/resource/browser/static evidence.
- [WORK_SESSION_REPORT_v2.md](WORK_SESSION_REPORT_v2.md) — Current 17-section session handoff.

## All eight actual trained model views

| Run | Detailed file map | Dashboard | PNG |
| --- | --- | --- | --- |
| HF20-S4A-F21-H4-NR-S42 | [Every role and artifact](HF20-S4A-F21-H4-NR-S42/RUN_DIAGNOSTICS.md) | [View](plots/s4_a_rankings.html?view=2021%7CNR) | [Image](plots/HF20-S4A-F21-H4-NR-S42.png) |
| HF20-S4A-F21-H4-T2R-S42 | [Every role and artifact](HF20-S4A-F21-H4-T2R-S42/RUN_DIAGNOSTICS.md) | [View](plots/s4_a_rankings.html?view=2021%7CT2R) | [Image](plots/HF20-S4A-F21-H4-T2R-S42.png) |
| HF20-S4A-F22-H4-NR-S42 | [Every role and artifact](HF20-S4A-F22-H4-NR-S42/RUN_DIAGNOSTICS.md) | [View](plots/s4_a_rankings.html?view=2022%7CNR) | [Image](plots/HF20-S4A-F22-H4-NR-S42.png) |
| HF20-S4A-F22-H4-T2R-S42 | [Every role and artifact](HF20-S4A-F22-H4-T2R-S42/RUN_DIAGNOSTICS.md) | [View](plots/s4_a_rankings.html?view=2022%7CT2R) | [Image](plots/HF20-S4A-F22-H4-T2R-S42.png) |
| HF20-S4A-F23-H4-NR-S42 | [Every role and artifact](HF20-S4A-F23-H4-NR-S42/RUN_DIAGNOSTICS.md) | [View](plots/s4_a_rankings.html?view=2023%7CNR) | [Image](plots/HF20-S4A-F23-H4-NR-S42.png) |
| HF20-S4A-F23-H4-T2R-S42 | [Every role and artifact](HF20-S4A-F23-H4-T2R-S42/RUN_DIAGNOSTICS.md) | [View](plots/s4_a_rankings.html?view=2023%7CT2R) | [Image](plots/HF20-S4A-F23-H4-T2R-S42.png) |
| HF20-S4A-F24-H4-NR-S42 | [Every role and artifact](HF20-S4A-F24-H4-NR-S42/RUN_DIAGNOSTICS.md) | [View](plots/s4_a_rankings.html?view=2024%7CNR) | [Image](plots/HF20-S4A-F24-H4-NR-S42.png) |
| HF20-S4A-F24-H4-T2R-S42 | [Every role and artifact](HF20-S4A-F24-H4-T2R-S42/RUN_DIAGNOSTICS.md) | [View](plots/s4_a_rankings.html?view=2024%7CT2R) | [Image](plots/HF20-S4A-F24-H4-T2R-S42.png) |

## Complete diagnostic families

Every run's file map links all actual files. For each of `inner_train`, `inner_validation`, `refit`, `oos`:

- `*_scores.parquet`: private exact keyed scores, source/recipe/checkpoint bindings, original target, objective labels, clocks and endpoint components.
- `*_metrics.json`, `*_origins.csv`, `*_slot.csv`, `*_month.csv`: complete role and origin/session/month/slot ranking metrics, retrieval, score spread, ties and margins.
- `*_cohorts.csv`: original target extremes, actual-objective error-ranked cohorts, complements and positive/negative cases.
- `*_energy_and_objective_cohorts.csv`: original TG20-event actual loss, numerator/MAD partitions and T2R original-Y energy/common/centered/cross terms.
- `*_thresholds.json`: phase training-only thresholds. `*_paired_cohort_difficulty.csv`: private exact saved event witnesses.
- `*_error_ranked_cohorts.csv`: legacy filename containing extreme-pair difficulty categories; actual objective-error-ranked rows are in `*_cohorts.csv`.
- `*_stock_quality.csv`, `*_stock_month_sector_quality.csv`: stock/source/fallback and static publisher-sector proxy strata.
- `*_matched_category_sessions.csv`, `category_and_anchor_metrics.csv`: matched-session intraday/overnight contrasts and all origin-category/old-anchor results.
- `calibration_*.json`, `refit_*.json`, `*_batches.csv`, `*_gradients.csv`: every epoch and batch, dropout-ON/OFF distinction, pre/postclip gradients, parameter incidence and updates.
- Configuration/binding JSON, selected calibration and final refit checkpoints, numerical/visual receipts and `PASS.json`: exact lifecycle identity and independent checks.

`S4_ALL_ROLE_METRICS.csv`, `S4_ALL_ROLE_EXTREME_OBJECTIVE_NUM_MAD_ENERGY.csv` and `S4_COMPLETE_TRAINING_TRACE.json` collect all eight runs. The `S4_EQUAL_YEAR_*` tables give absolute, control-paired and matched-category intervals. `S4_ANNUAL_NEURAL_AND_BASELINE_METRICS.csv` includes all four years and N0/N1/N2/P. `S4_MATCHED_BASELINE_AND_ARCHIVE_COMPARISONS.csv` separates archival comparisons. `S4_RANK_STABILITY_AND_SELECTION_CHURN.csv` retains within-session, missing-slot and across-session transitions. `S4_COMPLETE_LIFECYCLE_SUMMARY.csv` links selections, updates and checkpoint hashes.

All 16 no-fit/fitted baseline folders `F21`–`F24` × `S4_N0/N1/N2/P` retain four role exports and diagnostics; only P consumes the eight authorized non-neural fits. LR was optional and omitted. No LP/PW rescue fit occurred.

The opening/source/eligibility/scalar/tensor witness reports live in `opening_reaudit_v2/`; source clocks and exclusions are summarized in `S4_CLOCK_AND_ELIGIBILITY_AUDIT.md`. `untrained_visual_preview_v1/`, rehearsal outputs, old NOT_RUN cards and preparation receipts are historical, not actual trained-model results. The complete CSV index labels their stage. Bulk source data were not copied into the campaign.

## Rebuild from saved outputs only

From repository root with the documented `.venv`, run `scripts/summarize_hf20_s4.py --out <campaign>` using `.venv/bin/python` for the numeric summaries/detailed reports. Use `scripts/render_hf20_s4.py --out <campaign>` for all eight actual PNGs and browser QA with an existing Chromium/Chrome. No model fits, downloads or protected data are required. The offline HTML already exists and opens directly in a local browser.

