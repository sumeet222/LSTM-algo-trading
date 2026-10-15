# Package005 — TRAINING_AUTHORIZED_AND_ONE_PAIR_COMPLETED

The approved candidate-only **TM0 seed42 WF1 pair completed exactly once**, under proposal `713dd50a2f9919b58bec9a314b02497128170fe1d541825850d159a79b0a4615`. The linked canonical registry now counts **1/40**; the immutable legacy event ledger still records its historical0/40. **No retry, second pair, additional seed/fold/model, economic replay, production D1 migration or confirmation outcome access occurred.** The single-run permission is consumed.

Your actual instruction to rely on your word for privacy and the explicit “Yes—approve that exact conditional pair” are bound in researcher_privacy_attestation_v1.json. Versioned TA-G0-005-RESEARCHER-ATTESTATION-v1 accepts researcher-attested rights/clock approvals for this one pilot. Private email contents and third-party signatures were not inspected or invented; the earlier demand for email access is superseded within this scope. Rights are not independently certified, and redistribution/teammate transfer remains unapproved. The technical proposal, inputs and code are unchanged.

Calibration ran **14 epochs /602 optimizer steps**, stopped by the frozen10-epoch patience rule and selected **epoch4** using only inner-validation MSE (**4.704614488**). Fresh model and optimizer were reinitialized at seed42; the distinct immutable full-prefix recipe supplied the exact **4-epoch /188-step refit**. Total790 optimizer steps. Checkpoints are finite CPUfloat32 with6433 parameters; selected/final checkpoint identities and reload verification are preserved.

| Actual elapsed phase | Seconds | Minutes |
|---|---:|---:|
| Calibration neural training | 39.663 | 0.661 |
| Inner-validation evaluation | 1.064 | 0.018 |
| Fresh refit neural training | 12.977 | 0.216 |
| **Neural fitting total** | **52.639** | **0.877** |
| Full worker end to end | 76.120 | 1.269 |
| Supervised command wall | 79.576 | 1.326 |

The outer command wrapper measured82.729s including process startup. CPUarm64,1 PyTorch thread,8 logical CPUs; peak whole-process RSS603,750,400 bytes. Source loading, inner/full-prefix recipe application, selection/checkpoint, predictions and all other measured phases are separately recorded in first_tm0_seed42_WF1/training_actual_runtime.json. Existing train-only recipes were reused; these preprocessing times are applications, not newly fitted scaler construction. First actual calibration epoch2.868s; its clearly labeled maximum-pair projection364.75s was a budget check, not actual fitting time. Actual fit was safely below4h/hard4.5h.

Descriptive full-prefix training evaluation: MSE **7.316592**, daily Rank IC **0.071105**. Held-out WF1 July–December2023: **232 origins /116 sessions**, MSE **5.438830**, equal-day Rank IC **0.034914**. Per-origin MSE/IC and constant-case counts are recorded; no constant forecasts or targets occurred. This one pilot establishes no statistical, comparative or trading benefit. No cost/economic metrics exist.

**Effective G6: WARN — investigate calibration clipping.** The immutable raw runner result says PASS_PER_RUN_TELEMETRY because its summary checks only refit clipping. The independent addendum corrects this: calibration epochs5,7–14 flagged sustained clipping; epochs11–14 clipped100% of batches. Epoch4 was selected before those warning epochs, and all4 fresh refit epochs were finite without sustained-clipping warnings. No gradient nonfinite values occurred. No training settings or results were rewritten and no retry ran. Training top1% sessions contribute25.49% of squared loss; top10%55.66%. WF1 top10% contributes44.62%. Large TG0 tails remain unclipped. These are material health/concentration limitations for review.

**119 fresh focused tests PASS;169 owned Python files,0 errors/0 warnings; Ruff PASS.** Postrun read-only audit verifies the exact D6g trace, session/step conservation,6433 finite checkpoint tensors, fresh initialization evidence, journal chain and all2454 protected source/protocol/data bytes unchanged. Full new regression NOT_RUN under the approved lean policy; prior004728 PASS is inherited only for unchanged frozen producer/engine code. No source/bridge/model math changed in this run.

The active engineering binding remains `reports/data_audit/ta_real_input_bridge_005_2026-10-14_215455/final_v2/dataset_input_binding.json`; its historical fitting-false flags are superseded only for this consumed pair by dataset_readiness_addendum_v1.json. New approval_and_gate_matrix.json and postrun_independent_audit.json govern current authorization/health. Old reports and failed evidence remain immutable. All work is uncommitted; no Git staging, commit, push, cleanup or source GET occurred. **Stop here.** See human_review_card.md and next_action.md.
