# Package011 human review card

**TA011_CONTROLLED_BATCH_COMPLETED —18/18 started and completed, 0 failed; canonical ledger6→24/40.** Engineering/identity checks pass. Candidate evidence stays **ASSUMPTION_CONDITIONAL**; G6 warnings remain genuine.

| Arm / seed | WF1 ΔMSE / ΔIC | WF2 ΔMSE / ΔIC | G6 WF1/WF2 | Pairs | Fit s |
|---|---:|---:|---|---:|---:|
| H1 / 42 | -0.007828 / +0.00172 | +0.003338 / -0.02457 | P/P | 2 | 124.6 |
| H1 / 123 | +0.000789 / -0.01767 | -0.008775 / -0.00043 | P/P | 2 | 89.7 |
| T1 / 42 | -0.002160 / +0.00043 | -0.006092 / +0.01810 | W/W | 2 | 106.1 |
| T1 / 123 | +0.000742 / -0.00517 | -0.004716 / +0.00603 | W/W | 2 | 86.3 |
| T2 / 42 | -0.011421 / +0.01509 | -0.011104 / +0.01552 | P/P | 2 | 119.7 |
| T2 / 123 | -0.003009 / -0.00388 | -0.010273 / +0.00603 | P/P | 2 | 89.6 |
| O1 / 42 | +0.000396 / -0.00733 | +0.005706 / -0.00431 | W/W | 2 | 111.8 |
| O1 / 123 | +0.003331 / -0.00948 | +0.004850 / -0.00905 | W/W | 2 | 91.1 |

Δ = treatment−same-seed/fold C0; MSE lower and IC higher are favorable. Fit seconds sum calibration+fresh-refit epoch time, excluding loading/validation. Each row contains two pairs; two additional C0 seed 123 pairs use91.9s. Original C0 seed 42 both-pass G6 isW in each fold.

All four arms are **MIXED_OR_INCONCLUSIVE**. T2 improves MSE in 4/4 cells and IC in 3/4; every IC interval spans zero. H1 has no sustained clipping warning but favorable paired MSE+IC in only 1/4 cells. T1 has favorable paired point estimates in 3/4, with warnings retained and a reversal at seed 123/WF1. O1 has worse MSE and IC point estimates in 4/4 cells despite much less applied clipping at cap5; these are valid poor scores, not invalid runs. No numerical/integrity failure or automatic finalist promotion occurred.

H1/T2 G6 changes **W→P in both folds at both seeds**; T1/O1 remain W. P means both-pass telemetry PASS, W means warning from at least one epoch/pass. For O1 the historical norm>1 warning remains separate from its actual cap5. Calibration applied clipping is 0–0.19% for H1 and 0.49–2.94% for T2; their refits have 0%. O1 calibration actual clipping is 0.16–1.00% and refit 0%, but its predictions worsen. See target_tail_and_clipping.csv for all actual fractions and the explicitly missing historical WF1 batch summaries. Lower norms can follow a smaller derivative or changed units; causation is not established.

ZERO remains competitive: seed 42 T1/WF2 and T2/both folds beat ZERO on MSE; no intervention beats ZERO at seed 123. Every model uses the same 232 origins/116 days/1,160 stock scores per fold. All 23,200 saved scores are finite with no forecast constants/ties. Original TG0 extremes remain: up to 84.416 in full training and 39.403 in development. The original seed 42 controls are reused, never refitted.


| C0 seed / fold | MSE | Daily IC | ZERO MSE |
|---|---:|---:|---:|
| 42 / WF1 | 5.438829600 | +0.034913793 | 5.427531844 |
| 42 / WF2 | 7.631510203 | +0.050862069 | 7.628119050 |
| 123 / WF1 | 5.430641226 | +0.056896552 | 5.427531844 |
| 123 / WF2 | 7.639672321 | +0.046551724 | 7.628119050 |


| Arm / seed | WF1 planned→started→valid | WF2 planned→started→valid |
|---|---|---|
| H1 / 42 | 1→1→1 | 1→1→1 |
| T1 / 42 | 1→1→1 | 1→1→1 |
| T2 / 42 | 1→1→1 | 1→1→1 |
| O1 / 42 | 1→1→1 | 1→1→1 |
| C0 / 123 | 1→1→1 | 1→1→1 |
| H1 / 123 | 1→1→1 | 1→1→1 |
| T1 / 123 | 1→1→1 | 1→1→1 |
| T2 / 123 | 1→1→1 | 1→1→1 |
| O1 / 123 | 1→1→1 | 1→1→1 |


Full IDs/statuses: [experiment_registry.csv](experiment_registry.csv). Paired5-session exploratory intervals, monthly contrasts and seed/fold variation: [paired_fold_seed_comparison.csv](paired_fold_seed_comparison.csv), [monthly_paired_differences.csv](monthly_paired_differences.csv), [seed_variability_within_fold.csv](seed_variability_within_fold.csv), [temporal_variability_within_seed.csv](temporal_variability_within_seed.csv). No full selection-adjusted G8 or decisive p-values.

Measured new neural fitting **910.756 s**; supervised sequential pair wall **1465.818 s**. Elapsed since recorded task clock at this seal **59.50 min**; maximum fitting-worker RSS **708.41 MiB**, CPU/one thread. Timer caveats and every actual phase are in [resource_and_elapsed.json](resource_and_elapsed.json).

**72 tests pass;200 owned Python files,0 installed-Pylance errors/warnings; Ruff/owned diff pass.** Dashboard54 adapter checks/15 AppTest cases and HTTP health/HTML200/clean shutdown pass. Raw vendor data and historical checkpoints are unchanged. One external Finder `.DS_Store` change triggered a pre-STARTED launcher stop; its narrowly corrected binding was actually reapproved. No optimizer or budget was spent by that first launcher. The concurrent human RandomNotes edit and OS metadata were preserved.

Private rights/clock attestation, retrospective universe/actions, idealized period-end inputs and hourly-close price proxy remain assumptions. Strict observed-causality certification remainsfalse. No independent license/publication/action/PIT certification, executable fills, alpha, economics, course substitution, production migration or confirmation access. No new approval is pending for this completed scope; editor Problems refresh remains human-confirmed.

Next research decisions: (1) retain C0/ZERO/ridge references and record all arms inconclusive; (2) decide whether unchanged T2 versus C0 merits a separately registered independent development follow-up, without retuning on these folds; (3) keep confirmation locked until a distinct frozen manifest and authorization. No next experiment is activated here.

Open the existing app using the [five-step guide](HOW_TO_VIEW_PACKAGE_011.md). Details: [package report](package_report.md), [checks](checks.json), [artifact inventory](artifact_inventory.csv).
