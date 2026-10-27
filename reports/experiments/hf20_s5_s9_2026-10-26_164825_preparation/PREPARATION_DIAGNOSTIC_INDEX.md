# S5 + S9 complete diagnostic and analysis map

**PREPARATION ONLY: all16 actual starts NOT_RUN, ledger114/200.** There are no trained S5/S9 scientific results yet. This map lists every analysis family and its existing/prepared location; future filenames below are explicitly planned, not claimed artifacts.

## Existing preparation evidence

| File | Contents |
| --- | --- |
| [LIVE_FIT_APPROVAL_CARD.md](LIVE_FIT_APPROVAL_CARD.md) / [design.json](design.json) | Exact proposed science, hashes, budgets, authority boundary |
| [S5_CAUSAL_METADATA_MANIFEST.md](S5_CAUSAL_METADATA_MANIFEST.md) | FT16/metadata dictionary, timing, excluded historical-quality inputs |
| [S9_TARGET_AND_BASELINE_CONTRACT.md](S9_TARGET_AND_BASELINE_CONTRACT.md) | E1/QR1/DM1 reconciliation, proper losses/units/controls |
| [S5_S9_ROLE_COUNTS.csv](S5_S9_ROLE_COUNTS.csv) | Actual original S4 year/role counts and identities |
| [S5_CAUSAL_COVERAGE_AND_DIAGNOSTIC_STRATA.csv](S5_CAUSAL_COVERAGE_AND_DIAGNOSTIC_STRATA.csv) | Actual clock/source/fallback/age coverage |
| [S4_REUSED_RECIPES.json](S4_REUSED_RECIPES.json) / [REFERENCE_IDENTITIES.csv](REFERENCE_IDENTITIES.csv) | Reused phase recipe and reference SHA identities |
| [PREFLIGHT.json](PREFLIGHT.json) / [PRESEAL_INTEGRITY.json](PRESEAL_INTEGRITY.json) | Consolidated prep, unchanged ledger/source authority, resources |
| [preflight_v2/SOURCE_AND_REHEARSAL.json](preflight_v2/SOURCE_AND_REHEARSAL.json) | Four untrained workflows,16 role exports,0 steps/starts/fits |
| [S9_SAVED_CONTROL_LOSS_RECONCILIATION.csv](S9_SAVED_CONTROL_LOSS_RECONCILIATION.csv) |120 saved-score proper/raw loss comparisons |
| [tests_sealed.txt](tests_sealed.txt) / [static_check_complete.json](static_check_complete.json) |34 tests,495 files0 static errors/warnings |
| [preflight_v2/REHEARSAL_BROWSER_QA.json](preflight_v2/REHEARSAL_BROWSER_QA.json) |4 views ×4 roles |
| [preflight_v2/S5_S9_VISUAL_DIAGNOSTICS.html](preflight_v2/S5_S9_VISUAL_DIAGNOSTICS.html) | Offline **untrained** family preview |

Existing family evidence (every family has inner_train, inner_validation, refit, oos `_scores.parquet`, `_metrics.json`, `_strata.csv`, `_cohorts.csv`, toy phase recipes, checkpoint bindings, and REHEARSAL.json under its rehearsal directory):

- **META-T2R:** [untrained diagnostic narrative](preflight_v2/rehearsal/META-T2R/RUN_DIAGNOSTICS.md) · [PNG](preflight_v2/plots_final/META-T2R.png).
- **MAG:** [untrained diagnostic narrative](preflight_v2/rehearsal/MAG/RUN_DIAGNOSTICS.md) · [PNG](preflight_v2/plots_final/MAG.png).
- **EVENT:** [untrained diagnostic narrative](preflight_v2/rehearsal/EVENT/RUN_DIAGNOSTICS.md) · [PNG](preflight_v2/plots_final/EVENT.png).
- **QUANTILE:** [untrained diagnostic narrative](preflight_v2/rehearsal/QUANTILE/RUN_DIAGNOSTICS.md) · [PNG](preflight_v2/plots_final/QUANTILE.png).

Initial failed S5 export-adapter evidence is preserved in preparation.log and rehearsal/META-T2R. It was a zero-update rehearsal, not a model start. Earlier static/browser drafts and failed receipts remain clearly preliminary; only PREFLIGHT.json and its sealed evidence define readiness.

## Complete planned training diagnostics after approval

Each actual run directory below will contain RUN_DIAGNOSTICS.md; calibration/refit bindings and saved checkpoints; phase target/control recipes; immutable epoch JSON, batch CSV and gradient CSV; all four saved role scores/metrics/strata/cohorts; model_and_control_metrics.csv and matched_baseline_differences.csv; final PASS or explicit failure. **No actual PASS files exist now.**

Training, validation, refit and development/OOS details: epoch curves, raw-best/qualifying-selected checkpoint, dropout-ON online vs dropout-OFF full-prefix/validation losses, true optimizer counts/nonzero gradients/clipping, fresh same-seed refit and reload identity.

Extreme-value details: per-role task-optimized tail shares and complements, TG20 positive/negative and training-frozen extremes, numerator/MAD provenance/decomposition, separate original-scale errors. S5 additionally reuses full S4 ranking/cohort/energy exports under `ranking/`. MAG reports raw |R| and transformed m; EVENT CE vs ANY BCE/Brier/AP/calibration; QUANTILE Z pinball by alpha, Y/Z coverage, width, misses and crossing. These are distinct losses and must not be compared numerically across tasks.

Source/other details: per-origin/session/month/stock/slot, intraday/overnight/opening, fallback/missingness/terminal-age strata; retrospective group sensitivity; exact keys/cohort counts; full-role proper metrics, fixed-rule examples and saved-output trajectories. S5 adds matched S4/M1/P ranking, top/bottom retrieval/churn/common-centered energy.

| Run ID (in execution order) | Status | Planned narrative |
| --- | --- | --- |
| `HF20-S5-F21-H4-META-T2R-S42` | NOT_RUN | `HF20-S5-F21-H4-META-T2R-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S5-F22-H4-META-T2R-S42` | NOT_RUN | `HF20-S5-F22-H4-META-T2R-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S5-F23-H4-META-T2R-S42` | NOT_RUN | `HF20-S5-F23-H4-META-T2R-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S5-F24-H4-META-T2R-S42` | NOT_RUN | `HF20-S5-F24-H4-META-T2R-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S9-F21-H4-MAG-S42` | NOT_RUN | `HF20-S9-F21-H4-MAG-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S9-F22-H4-MAG-S42` | NOT_RUN | `HF20-S9-F22-H4-MAG-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S9-F23-H4-MAG-S42` | NOT_RUN | `HF20-S9-F23-H4-MAG-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S9-F24-H4-MAG-S42` | NOT_RUN | `HF20-S9-F24-H4-MAG-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S9-F21-H4-EVENT-S42` | NOT_RUN | `HF20-S9-F21-H4-EVENT-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S9-F22-H4-EVENT-S42` | NOT_RUN | `HF20-S9-F22-H4-EVENT-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S9-F23-H4-EVENT-S42` | NOT_RUN | `HF20-S9-F23-H4-EVENT-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S9-F24-H4-EVENT-S42` | NOT_RUN | `HF20-S9-F24-H4-EVENT-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S9-F21-H4-QUANTILE-S42` | NOT_RUN | `HF20-S9-F21-H4-QUANTILE-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S9-F22-H4-QUANTILE-S42` | NOT_RUN | `HF20-S9-F22-H4-QUANTILE-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S9-F23-H4-QUANTILE-S42` | NOT_RUN | `HF20-S9-F23-H4-QUANTILE-S42/RUN_DIAGNOSTICS.md` |
| `HF20-S9-F24-H4-QUANTILE-S42` | NOT_RUN | `HF20-S9-F24-H4-QUANTILE-S42/RUN_DIAGNOSTICS.md` |

## Planned collective outputs

After actual attempted training the root will contain all nine requested artifacts: S5_S9_FINAL_RESEARCH_DECISION.md, S5_S9_MODEL_METRICS.csv, S5_S9_MATCHED_BASELINE_DIFFERENCES.csv, S5_S9_TRAINING_TRACE.csv, the two existing manifests, S5_S9_VISUAL_DIAGNOSTICS.html, this index, and S5_S9_VERIFICATION.json. Supporting OOS paired-session differences/month-block uncertainty, run inventory and numerical verification remain linked. Per-run plots are `plots/<run>.png`; the single offline HTML selects run/fold/role/ticker/date and links old dashboards. Nothing here represents completed fitting.

Ledger journal remains `reports/audit/track_a_real_pairs_v22_hf20_s4a.jsonl`; proposed v23 does not exist. Private forecasts/checkpoints/HTML stay local and ignored. [Session report](WORK_SESSION_REPORT.md) documents all source/code changes and verification.
