# P4.11 full-peer / SP3 — consolidated human review

**P4_11_SYNTHETIC_ENGINEERING_PASS — HUMAN_REVIEW_REQUIRED; SCIENTIFIC_HOLD.**

| # | Check | Expected / actual | Evidence / code / tests |
|---|---|---|---|
|1|Authorization|Synthetic-only; no new fullpeer/SP3 fits, 0/40 genuine pairs|activation_matrix.json; fullpeer.require_mode; test_operator_audit_cannot_promote_mode_or_overwrite|
|2|Full-peer order|5×48×85; own21 exactly unchanged; four16-channel histories exclude target|fullpeer.fullpeer_values; test_full_85_hand_sentinels_all_steps_exclusion_and_exact_21_prefix; hand_oracles.json|
|3|Parameter inventories|FULLPEER15265; SP3 core7073+mixer20=7093|neural_engine.SharedLSTM; spatial_operator.SpatialLSTM; hand_oracles.json parameters|
|4|Shared source integration|Same actual canonical tables, D7 prefix, masks and mature target rows|operator_release/source_integration.json; fullpeer.operator_batch; indexed-view test|
|5|Frozen mixer math|LN32/eps1e-5 non-affine; GELU; bias-free K2 residual; manual error<1.2e-15|spatial_operator.StockMixer; fullpeer_sp3_audit.manual_mixer; hand_oracles.json|
|6|Zero initialization|M2 exactly0; matched-layout MC0 scores/hidden error0; M1 seeded standard Linear-style initializer|fixture_design.json; operator_oracles; zero_M2 fields|
|7|Eventual gradient flow|Initial M1 grad0/M2 grad2.6060; nonzero M2 yields M1 grad0.29068|hand_oracles.json initial/nonzero_m2 gradients; independent oracle test|
|8|Peer-transfer law|Fixed0.4*GELU(0.7*LN(sender)[0]) observed by recipient head; FD error1.25e-13|fixture_design.json; hand_oracles.json; fullpeer_sp3_audit.planted/manual_mixer|
|9|Sensitivity controls|MC0 different-stock gradient0; full-peer/SP3 peer-input gradients positive finite|hand_oracles.json; operator_oracles; no financial causal interpretation|
|10|Axis/permutation identity|M1P^T/PM2 gives error0; input-only reorder differs0.44729 and bound model rejects reordered identities|operator_oracles; BoundOperator; artifact order-negative tests|
|11|Causal source contracts|Unknown/NaT/future/stale publication, unknown/missing stock masks, partial panel, source-only/real flags, stale certificates, duplicate/stub/order rejected|test_strict_upstream_causality_and_policy_negatives; DST/early-close test; operator_release/source_integration.json|
|12|Whole-session computation|Exact session7 vs pooled6,16+3 sampler,1/2 origin masks, no cross-origin mixing; original dropout/AdamW/clip|hand_oracles.json; grouped-origin test; existing test_neural_engine.py|
|13|Artifact authority|Isolated untrained/operator stage, exact reload; stale source/prep/target/code/order/hash/architecture denied; no REFIT_FINAL promotion|operator_artifacts.py; test_bound_inputs_untrained_artifact_and_source_order_stage_rejections|
|14|Conservation|1530 starting tracked/599 raw files conserved except3 permitted adapters;74 E5 payloads and all old initial weights/scores exact; P4.9 unchanged|preservation.json; prior_artifact_reconciliation.json; old_models_before/after.json|
|15|Release verification|703 full tests PASS on unchanged final code;155 types0/0; Ruff/diff PASS;43 focused PASS|checks.json; full_pytest.txt; focused_final.txt; types_final.txt; ruff_final.txt|
|16|Activation boundary|Scientific G0–G4 HOLD/16P2/33P3/7 blockers; four-family conflict unresolved; P4.10/12/13 inactive|activation_matrix.json; preservation.json; no empirical comparison/RankIC/P&L|

Decision: accept/correct/hold this synthetic operator-readiness package. Acceptance does not activate any historical fit, scientific source/universe, fourth family, confirmation or Git integration. SP3 and full-peer are same-source-information controls with different computational access and capacities; neither historical result is measured. Prior E5 v1/256 failures and D6g cap/underfit warning stay unchanged. Upstream human acceptance is not inferred. STOP.
