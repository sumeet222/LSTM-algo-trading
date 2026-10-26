# HF20 S1 + S2 preparation: source and scientific reconciliation

Stage 0 **QUALIFIED**; Stage 1 **PASS**; Stages 2–5 **NOT_RUN**. No real-data supervised fitting, prefix-recipe estimation, real model optimizer updates/checkpoints or journal starts occurred. Ledger **62/200**. All 2026 numerical data remained unopened in this session. Proposed settings require live approval.

The design record supplied in `docs/track_a/` was read in full and matches SHA256 `f676ca3c0690a06e66a47a6769f82d1e94d5d755e550387ed226db36892883d1`. The comprehensive and focused plans match their exact submitted hashes. The completed October25 dossier, P019B/P020 contracts, executors and corrected P028 journal were inspected; see [source references](preflight_source_refs.json) and [preservation manifest](preservation_manifest.json).

## Reconciliation requiring the proposed signoff

The six directional choices do not authorize numerical settings or starts. The latest brief supersedes the record's older B1-then-B2 review sequence with one combined S1/S2 approval. “No newly learned scaler” means no alternative scaler family; the record's own prefix-fitting rule and latest brief require eight newly estimated inner/refit recipes using the original P020 definitions. Reusing the archived 2023/2025 scalers would leak future information. These eight unsupervised preprocessing jobs are explicitly within the proposed approval; their numerical values and hashes do not yet exist and are not claimed verified.

Archived T2 was fitted into2025 and is contextual only. No valid saved four-fold earlier-cutoff counterpart was found. T2R is a new fold-specific T2-objective control, selected by daily Rank IC rather than historical D6g MSE. All three new families use the identical architecture, information, seed and selection opportunity. Prior D6g definitions/results remain intact.

The existing200 ceiling counts neural calibration-plus-fresh-refit lifecycles, including failed starts. S1 is separately and explicitly budgeted: P8 + LR28 + LP28 = **64 supervised coefficient/profile fits**, plus **eight prefix recipes**. There is no claim that baseline fitting is authorized or unrecorded/free. Proposed12 neural starts would charge62→74, with no retries. The original P028 executed-code identity and its reporting-only correction are preserved, never retrospectively rewritten.

## Exact folds and support

| Fold | Inner fit through | Selection starts (nominal) | Refit through | Inner / validation origins | Refit / OOS origins | OOS sessions |
|---|---|---|---|---|---|---|
| F21 | 2020-06-30 | 2020-07-01 | 2020-12-31 | 3510 / 197 | 3720 / 293 | 177 |
| F22 | 2021-06-30 | 2021-07-01 | 2021-12-31 | 3890 / 137 | 4027 / 364 | 203 |
| F23 | 2022-06-30 | 2022-07-01 | 2022-12-30 | 4245 / 143 | 4403 / 284 | 172 |
| F24 | 2023-06-30 | 2023-07-03 | 2023-12-29 | 4578 / 111 | 4701 / 308 | 185 |

Populations derive from actual canonical XNYS grid sessions, matured endpoints, inherited source/label eligibility and the48-step input embargo, not approximate date strings. Both original slots and all20 stocks are retained. The first actual OOS dates are2021-01-14,2022-01-13,2023-01-13,2024-01-12. Inner validation sessions are115/87/80/74; each has at least25 origins per slot and50 sessions. [folds.json](folds.json) records scheduled candidates, embargo exclusions, source/label exclusions, exact first/last dates and counts. Sixteen `F21..F24_<role>_indices.csv` files bind complete role keys. No rare-outcome rejection was added.

Independent source-close reconstruction matched137,200 existing historical target rows (`rtol1e-14, atol1e-16`). Rank(R), rank(TG20) and rank(asinh(TG20)) matched across tested admitted historical populations. The source calendar dates match installed XNYS. Four bounded real2020 inputs (20×48×16 each) match the archived P020 sampler bit-for-bit; that archival recipe was used only to check the sampler, never as an annual input. See [numerics](preflight_numerics.json), [source reconstruction](independent_source_preflight.json) and [adapter equivalence](bounded_archive_adapter_equivalence.json).

[Source quality by role](source_quality_by_fold_role.csv) reports missing/proxy counts for each fold/role without changing eligibility. [Defined-IC source feasibility](defined_ic_source_feasibility.csv) found zero origins forced constant by all20 M1 fallback/native-zero values in all four OOS years. This is an availability test, not a forecast-performance or guaranteed99%-IC result. N0 is explicitly exempt and undefined, never assigned IC0.

[Source witnesses](shared_source_case_keys.csv) bind22 genuine52-hour stock windows spanning22 origins,12 sessions and13 tickers, both slots/all four years. Each uses genuine opens/closes and complete extrema. Fixed origin keys and canonical ticker rotation were chosen by availability only, before forecasts. The same22 cases will be replayed for T2R/NR/PW;66 model replays are not66 independent events. Endpoint closes and reconstructed returns are included; no bulk candle duplication.

## Frozen statistical and optimization proposal

P is a prefix-only mean normalized-rank profile. LR/LP share chronological48×16=768 covariates and the same float32 FT16 information; solvers use float64. LR minimizes weighted-mean rank MSE +λ||w||² with a free intercept; LP uses a mean of untied pair logistic terms +λ||w||², no intercept. Grid1e-4,1e-3,1e-2,.1,1,10, selected only by inner dailyIC with largerλ for exact ties. Matrix-free LP has100 L-BFGS iterations/125 closure calls, gradient tolerances1e-7 during solve and1e-5 required final maximum, change tolerance1e-12. Nonconvergence stops, not an adaptive solver extension.

Neural architecture: existing6433-parameter SharedLSTM, one hidden32 layer,48×16 own-stock input, final-hidden dropout.1, recurrent dropout0, unrestricted scalar output. AdamW lr.001, betas(.9,.999), eps1e-8, weight matrices decay.01/biases0, clip1.0,16 whole sessions per batch, CPU float32, seed42, threads4/1, loader workers0. NR uses midrank q in[-1,1]; PW uses pure τ1 untied pair softplus with half-to-each endpoint allocation; T2R retains the phase-specific asinh objective and once-only inverse.

Selector: dropout-OFF validation dailyIC, strict `IC > qualified_best + .001`; raw maximum separate; observe at least12 epochs, maximum60, patience10. A selected checkpoint can precede epoch12. Refit independently resets seed42/model/optimizer and runs exactly that selected count. Maximum211,860 neural updates if every calibration/refit reaches60 epochs. No extra seeds, folds, controls or combinations.

Primary: equal origins within day, equal days within year, then equal mean of four annual dailyIC means. Constants undefined; average ranks/no jitter. At least99% defined OOS origins except N0. Paired comparisons match keys;400 whole-calendar-month resamples use daily sums/counts and are descriptive sensitivity, not significance. All20 stocks/pairs are dependent observations.

## Limits and remaining decisions

Only the pending live-fit signoff is needed for the proposed campaign. Source rights, publication/action vintage, retrospective survivor selection and historical2-minute outcome/issuance mismatch remain **QUALIFIED**, not certified. The label is historical price-only ordering, never executable strategy or profitability. No2025 tuning,2026 numerical access, downloads, credential use, other features or trading.

Planning estimate2–8 hours for the combined campaign, not a real-data benchmark or promise; runtime depends on selected epochs/LP convergence. Resource caps2GB process RSS,1GB task additions and10GB project use stricter decimal units; fixed epoch/iteration caps bound work. A lightweight metadata process measured292,814,848-byte peak RSS and about6.864GB projected project size including16MB journal reserve. These are not training measurements. Estimated training RSS0.8–1.7GB and additions0.3–0.8GB remain forecasts. No source/window replicas are planned.

Proposal SHA256 `7d47e5e893e2450b63d348f9c539df7c6ac2790b07b0d94ecaaee02acbe9b04a`; execution `9185edba7e01e2fa6d7ea0d519fdfa60fc818fdc548215cc1c986439403b3660`. See [live approval card](LIVE_FIT_FREEZE_AND_APPROVAL_CARD_PROPOSED.md).
