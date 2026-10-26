# Detailed training, selection, fresh-refit and failure trace

**12 starts,11 completed,1 failed. Final ledger74/200.** The original LP failure is separate baseline attempt#8, not a neural debit. All start IDs and actual terminal statuses are listed below; no failed start is refunded, renamed into a retry or completed after the fact.

| start | run_id | status |
| --- | --- | --- |
| 63 | HF20-S1S2-F21-T2R-S42 | COMPLETED |
| 64 | HF20-S1S2-F21-NR-S42 | COMPLETED |
| 65 | HF20-S1S2-F21-PW-S42 | FAILED_CALIBRATION_NO_REFIT |
| 66 | HF20-S1S2-F22-T2R-S42 | COMPLETED |
| 67 | HF20-S1S2-F22-NR-S42 | COMPLETED |
| 68 | HF20-S1S2-F22-PW-S42 | COMPLETED |
| 69 | HF20-S1S2-F23-T2R-S42 | COMPLETED |
| 70 | HF20-S1S2-F23-NR-S42 | COMPLETED |
| 71 | HF20-S1S2-F23-PW-S42 | COMPLETED |
| 72 | HF20-S1S2-F24-T2R-S42 | COMPLETED |
| 73 | HF20-S1S2-F24-NR-S42 | COMPLETED |
| 74 | HF20-S1S2-F24-PW-S42 | COMPLETED |

## Complete neural selector/refit receipts

| run_id | observed_epochs | selected | raw_epoch | best | raw_best | refit_optimizer_steps | seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HF20-S1S2-F21-NR-S42 | 13 | 3 | 3 | 0.02346872 | 0.02346872 | 396 | 104.4845 |
| HF20-S1S2-F21-T2R-S42 | 22 | 12 | 12 | 0.03477992 | 0.03477992 | 1584 | 230.593 |
| HF20-S1S2-F22-NR-S42 | 12 | 1 | 1 | 0.06475674 | 0.06475674 | 144 | 104.1591 |
| HF20-S1S2-F22-PW-S42 | 12 | 1 | 1 | 0.06488615 | 0.06488615 | 144 | 106.3916 |
| HF20-S1S2-F22-T2R-S42 | 28 | 18 | 18 | 0.09080591 | 0.09080591 | 2592 | 258.5074 |
| HF20-S1S2-F23-NR-S42 | 14 | 4 | 4 | 0.04473229 | 0.04473229 | 628 | 127.894 |
| HF20-S1S2-F23-PW-S42 | 16 | 6 | 6 | 0.02988238 | 0.02988238 | 942 | 141.5787 |
| HF20-S1S2-F23-T2R-S42 | 14 | 4 | 4 | 0.02921098 | 0.02921098 | 628 | 117.9556 |
| HF20-S1S2-F24-NR-S42 | 12 | 2 | 2 | 0.006797399 | 0.006797399 | 336 | 100.4028 |
| HF20-S1S2-F24-PW-S42 | 12 | 2 | 2 | 0.0002133713 | 0.0002133713 | 336 | 107.7097 |
| HF20-S1S2-F24-T2R-S42 | 12 | 2 | 2 | 0.02920138 | 0.02920138 | 336 | 99.66548 |

For every completed arm, an independent replay of epoch IC receipts reconstructs both raw maximum and qualified best, strict improvement>.001, min12 observed/max60/patience10. All observed raw/qualified maxima coincide here; that is an observation, not omission of the two fields. The refit runs selected epochs, so selected1/2/3 is valid even though calibration observed at least12. Negative/weak validation IC was not a stop condition.

The one-layer hidden32/6433-parameter architecture, final-hidden dropout.1/recurrent dropout0, AdamW.001/(.9,.999)/eps1e-8, weight matrix decay.01/bias0, clip1,16 whole sessions, CPUfloat32 and seed42 were verified from actual parameter groups/configuration receipts. Every refit resets model/seed/optimizer, matches the original initial-weight hash and starts with empty optimizer state. Saved final optimizer step IDs equal selected_epochs×ceil(refit_sessions/16), and batch telemetry counts agree. No later-cutoff pretrained weights or archived2025T2 substitute.

Completed-model logs contain24,028 calibration and8,066 refit optimizer steps. There are29 calibration and12 refit clipped batches; all recorded gradients/updates/weights finite, maximum preclip norm3.357188 and maximum postclip≈1.0. See final_gradient_update_counts.csv and gradient_clip_update_summary.csv for every phase/model, not only these totals. Healthy gradients and rare clipping do not establish predictive information.

Online dropout-ON objective histories average changing weights/noise; four-role metrics use dropout-OFF selected calibration/final-refit checkpoints. Loss units are retained per objective, not compared as interchangeable scales. complete_epoch_trace.csv and every calibration_NNN.json/refit_NNN.json plus *_batches.csv preserve the full trace. Original calibration and refit checkpoints and configuration/binding receipts are indexed by the diagnostic file map.

## Permanently failed start65 and the prospective validation correction

F21 PW saved7 complete calibration epochs (868 logged updates) and their checkpoints, then failed during epoch8 before that epoch's batch telemetry/weights/optimizer state were saved. The number of additional epoch8 updates is unavailable. Do not represent868 as the complete failed-start update count or reconstruct lost state by fitting. No fresh full-prefix refit or OOS forecast exists. Its FAILED event and original FATAL_STOP remain unchanged.

The detached float32 pair-conservation assertion differed by2.3841858e-7 at one origin. A small tied-outcome synthetic case reproduced a false assertion. Promoting only detached audit sums/normalization tofloat64 passed the **same** rtol3e-7/atol1e-8, while actual returned float32 pair terms, endpoint allocations, loss and score gradients were bit-identical. No optimized operation, scalar, objective, source, selection rule or tolerance was retuned. The actual failed batch's score/RNG state is not recovered or invented.

PAIR_GUARD_RESOLUTION.md and PAIR_GUARD_PROSPECTIVE_AMENDMENT.json record this validation-only fix under the user's continuation/common-readiness repair authority. Original execution code/source bytes remain immutable. Version20 links unchanged version19's65 and permits only the9 unstarted F22–F24 arms;66–74 all completed. Failed65 was not retried. New output provenance explicitly records the amended executor; historical PASS files retain their actual original executor.

45 targeted tests pass, including the exact false-positive regression, bit-identical forward/gradient comparison, nonfinite/tie rejection, actual synthetic optimizer/checkpoint reload and successor-journal no-retry/hash gates. final_static_check.json reports450 files0 errors/warnings. No diagnostic was suppressed or tolerance weakened.

## Baseline attempts and recipe accounting

Original eight attempts remain7 accepted F21 inner P/LR fits plus failed LP. New29 P/LR attempts all succeeded, cumulatively37 attempts/36 successful coefficients/1 LP failure. Old F21 inner selection and predictions are referenced by path/hash; not re-created by fitting. New F21 two full-prefix fits plus27 F22–F24 P/LR fits completed. LP's27 other planned fits remain unattempted/deferred, not silently completed. One prior prefix recipe is reused;7 are newly fitted with the unchanged P020 family/cutoffs.

Separate immutable baseline_continuation_events.jsonl and the old baseline_fit_jobs.jsonl reconcile these attempts. They do not consume the neural-start ledger. STAGE_B_HANDOFF.json verifies44 accepted baseline-role outputs with no LP/IC-performance gate before neural starts. Original LP solver state/residual remains unavailable, as documented in LP_FAILURE_READONLY_DIAGNOSIS.md.

## Execution identities and resource limits

CONTINUATION_AUTHORITY_AND_RUN_MANIFEST.json is the direct prospective user authority record; the old live approval is historical only. Initial executorfd244c2… ran F21; audit-precision executore4d464f… ran only the9 unstarted arms. Both prior code and journals are preserved. The live registry points tov20, with prior pointer snapshots retainingv18/v19 identities.

Sum of11 successful lifecycle timings is1499.34s (about25.0min), including immediate numerical exports/checks; failed fit, source/preparation, audit repair and collective analysis are additional. No full-package duration or per-fit CPU time is inferred from that sum. Successor process peak RSS through end of fitting was1,235,959,808bytes, below2GB. This is not a measurement of the first stopped process or all later postprocessing. Its task-byte reading before collective tables was251,506,414; final storage is separately recorded in the session report. No large raw/window store copies, installs or downloads.
