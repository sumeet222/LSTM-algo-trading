# HF20 monthly stability and recent36 linear screen — complete

**28/28 authorized linear fits succeeded; zero new neural starts or inference. Ledger remains74/200.** GateA/B, all4 per-fold GateC and independent final reconciliation pass. Recent36 IC improves in2/4 years, with mixed monthly/selection-tail evidence and uncertainty spanning zero. No further fitting is authorized by this package.

## Readable reports and offline figures

1. [PREFLIGHT.md](PREFLIGHT.md): exact authority, phase cutoffs, fixed36-month rule, recipe reuse, estimates and source qualifications.
2. [MONTHLY_IC_DIAGNOSIS.md](MONTHLY_IC_DIAGNOSIS.md): 2021–2024 M1/LSTM/linear temporal stability, explicit PW2021 unavailable/N0 undefined and competing explanations.
3. [RECENT36_VS_EXPANDING_LINEAR.md](RECENT36_VS_EXPANDING_LINEAR.md): primary matched history-span contrast, actual penalties, all4 roles, fit support and reliability limits.
4. [OBJECTIVE_AND_EXTREME_COHORT_DIAGNOSTICS.md](OBJECTIVE_AND_EXTREME_COHORT_DIAGNOSTICS.md): exact normalized-rank objective, original-TG20 extremes/signs/NUM–MAD/complements, pair endpoint attribution and bounded examples.
5. [FINAL_NONSTATIONARITY_DECISION.md](FINAL_NONSTATIONARITY_DECISION.md): concise research interpretation; no rolling-LSTM authority.
6. [WORK_SESSION_REPORT.md](WORK_SESSION_REPORT.md): commands, errors/corrections, tests/static checks, resources, preservation and Git handoff.
7. [Saved monthly timeline](MONTHLY_RANKING_STABILITY.html) and [matched recent/expanding timeline](RECENT36_VS_EXPANDING_MONTHLY.html): portable offline Plotly, no UI/server or network required.

## Complete useful data/diagnostic map

| File | Purpose |
|---|---|
| MONTHLY_IC_BY_MODEL.csv |384 month/model cells; model/month status, eligible sessions/origins/rows, daily/origin IC/distribution, positive-day fraction, concordance, ties and constants; PW2021 unavailable |
| MONTHLY_PAIRED_IC.csv | Five requested saved-model IC contrasts and actual PW pairs, with same-session pair/retrieval/loss differences |
| SAVED_ORIGIN_METRICS.csv; SAVED_DAILY_METRICS.csv | All saved31 OOS cells' original origin and equal-session records; no checkpoint replay |
| SAVED_ANNUAL_RECONCILIATION.csv; MONTHLY_STABILITY_COUNTS.csv | Independent published annual reproduction and month sign/range/support counts |
| RECENT36_FOLD_RESULTS.csv | All4 accepted primary annual contrasts, selected penalties, IC/concordance/top-bottom/ordinal-error/actual-loss differences and matched-recipe coefficient norms/cosines |
| RECENT36_INNER_SELECTION.csv | All24 inner candidates: actual train/validation loss, IC, λ, penalty/objective, numerical residual, norm/hash/status and solve-only timing |
| RECENT36_ROLE_SUPPORT.csv; FOLD_SOURCE_RECIPE_MANIFEST.csv | All16 role and8 fit-population origin/session/row counts, exact36-month bounds, feature/maturity endpoints and original recipe references |
| RECENT36_MONTHLY_PAIRED.csv; RECENT36_ORIGIN_METRICS.csv; RECENT36_DAILY_METRICS.csv | Exactly matched new-versus-saved monthly contrasts and underlying origin/day records |
| COMBINED_MONTHLY_IC.csv; COMBINED_ANNUAL_IC.csv; COMBINED_EQUAL_YEAR_IC.csv | All saved/new comparisons, no four-year PW substitution or constant zero IC |
| RECENT36_ALL_ROLE_METRICS.csv | Recent training/selection-validation/refit/OOS, with in-sample vs OOS meaning preserved |
| RECENT36_SLOT_COMPARISON.csv; RECENT36_QUALITY_STOCK_ATTRIBUTION.csv | Existing slot and source-quality/fallback/ticker/static-sector strata; partial-row IC is additive attribution, not a correlation |
| OBJECTIVE_AND_EXTREME_COHORTS.csv; MATCHED_COHORT_RANK_ERROR_DIFFERENCES.csv | Common original-target extreme/event/sign/NUM–MAD cohorts, actual rank-loss and ordinal-error mass, pair endpoint credit and conservation |
| COHORT_THRESHOLD_PROVENANCE.csv; BOUNDED_MATCHED_EXTREME_EXAMPLES.csv |16 exact saved train-threshold references and8 genuine keyed extreme/ordinary row comparisons; no copied raw candles |
| MONTH_BLOCK_SENSITIVITY.csv | Canonical400 whole-month paired sensitivity; independent year draws for equal-year aggregate; no formal/significance-adjusted claim |
| F21/F22/F23/F24_RECENT36_LR/selection.json | Candidate IC selection, exact tie rule and penalty |
| Each F*_RECENT36_LR/inner_*.npy and refit_coefficients.npy | Six inner coefficients plus1 fresh refit/fold; finite and exact checksum reload |
| Each F*_RECENT36_LR/{inner_train,inner_validation,refit,oos}_scores.parquet | New private keyed forecasts/outcome operands, source/recipe/coeff hashes and hierarchical weights; rank-only units |
| Each F*_RECENT36_LR/objective_cohorts.csv; GATE_C.json | Full4-role cohort conservation, coefficient/reload/key/selection support; must pass before next fold |
| nonneural_attempts.jsonl; FIT_COMPLETION.json | Exactly28 charged non-neural starts/completions;0 failures; independent of neural ledger |
| AUTHORIZED_LINEAR_PLAN.json; submitted_instruction.txt | Direct task authority, six penalties/fourfolds/onewindow, exact execution hashes and scope |
| INPUT_PRESERVATION.json; PREFLIGHT_LINEAR_REPLAY.csv |5721 source/prior/checkpoint/config byte references and16-role no-fit replay |
| GATE_A.json; GATE_B.json; GATE_D_ANALYSIS.json; FINAL_INDEPENDENT_VERIFICATION.json | Sequential scientific checks, independent ranks/weights/objectives/populations/counter/preservation reconciliation |
| *_RECEIPT.json | Per-stage measured wall/RSS,0 AdamW/forward/scaler-fit calls and preservation |
| READONLY_REPORTING_FOLLOWUP.json; analysis_executed_v1.py.txt; MONTH_BLOCK_SENSITIVITY_v1_retained.csv | Disclosed post-fit type annotation and corrected equal-year resampling dependence; all21 other CSVs/point metrics unchanged, no new fit |
| final_tests_v2.txt; final_ruff_v2.txt; final_static_v2.json | Canonical final checks; earlier attempts/logs retained for traceability |
| artifact_inventory.csv | Every new artifact/source/test/session path, bytes/SHA256/type/Git intent; excludes self and closure receipt |

Old S1/S2 reports/coefficients/recipes/failures remain at [the authoritative prior index](../hf20_s1_s2_continuation_2026-10-25_204117/README.md); old T2R-only z/original error and gradient diagnostics are linked there. They were not recomputed by neural inference. Initial monthly directory-glob mistakes failed before any fitting and were corrected by inspecting actual31 saved paths; logs remain. No old scientific output was repaired or rewritten.

## Safeguards and reuse

No source/stock/task/horizon/recipe changes,2025 tuning, protected2026 numerical reads, downloads/install/secrets/trading/Git commit or push. Source publication/action vintage, historical two-minute issuance/label-start mismatch, survivor/PIT and bounded private-use qualifications persist. Earlier permitted observations remain in shared scalers. Source-quality masks are retrospective descriptions, not certified point-in-time publication records.

Use existing documented.venv/dependencies and legitimately checksum-matched private artifacts. Read-only metrics can be reproduced from listed saved scores with `origin_panel`/`monthly`/`reconcile` in `lstm_data.hf20_recent_analysis`; no checkpoint forward or fit is needed. Do not rerun `--run` into this namespace or reuse the exhausted28-fit authority. The immutable executed helper snapshot plus post-fit follow-up distinguishes execution from later reporting code. A future empirical replay needs its own allocation/authority. Row stores and coefficients remain private/local; no redistribution or clone-only data portability certification is implied. No follow-up experiment starts automatically.
