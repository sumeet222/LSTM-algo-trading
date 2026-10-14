# E5 synthetic engineering — human review

**P4_8_SYNTHETIC_ENGINEERING_PASS — HUMAN_REVIEW_REQUIRED; SCIENTIFIC_HOLD.**

Review these 14 checks. The original failure is not erased; the short D6g calibration remains underfit at its cap.

| # | Review check | Independently inspect | Disposition |
|---|---|---|---|
|1|Original failure stays failed|original_failure_oracle.json; original_failure_analysis.md; src/lstm_data/e5_deep_audit.py:40|FAIL preserved;0 new v1 updates|
|2|V1 TG0/ranking algebra and graph|hypothetical centered identity <1e-14; finite difference <1e-7; 48 nonzero peer-gradient steps; tests/test_e5_fixture_v2.py:18|Independent oracle PASS; no TG0 in v1|
|3|Prospective fixture/horizon decisions|fixture_v2_config.json; E5_HEALTH_FIXTURE_v2_DESIGN.md; extension_1024/ counterparts; SHA-bound reservations|256 FAILED, one 1024 extension PASS; no retuning|
|4|Causal future-law TG0 oracle|fixture_v2_oracle.json; src/lstm_data/e5_fixture_v2.py:46|median/MAD 0; epsilon 1e-4; error<9.4e-12; maturity 4h03m|
|5|Honest conditional peer information|same own input targets+2.5/-2.5; population Bayes own MSE 0.05 vs peer oracle 0; tests/test_e5_fixture_v2.py:32|PASS; changes ordering, no common-offset ranking claim|
|6|Primary vs own-only fitted control|E5 held-out 0.00188213; MC0 0.07504877; zero 0.05603208; extension_1024/*PLANTED.json|PASS; disclose 7073/7329 capacities|
|7|Null/repeat/coordinate controls|null held-out 0.08145031, reference 0.06208234; repeat state/scores exact; tests/test_e5_fixture_v2.py:73|PASS; no permutation p-value|
|8|Geometry, four-peer divisor, gradients|5×48×23; exact 21 prefix; divisor 4; 7329 parameters; src/lstm_data/peer_inputs.py:26; src/lstm_data/neural_engine.py:28|PASS; finite positive peer paths; no clipping|
|9|Session loss and clocks|7 vs pooled 6; actual 19-session epoch 9 vs naive 12.25; tests/test_neural_engine.py and test_neural_lifecycle.py; existing NaT/future/missing population cases|PASS; full pytest, no weakened tests|
|10|Actual fixed validation/selection|seed 42_pair/selection_trace.json; 63-calendar tail,55 valid days/55 per origin,16 exclusions; src/lstm_data/neural_lifecycle.py:235|PASS with cap/underfit WARN; 60 epochs/select 59|
|11|One genuinely fresh refit|seed 42_pair/refit_trace.json and pair_result.json; fresh init equality/empty optimizer; distinct preprocessing; 413 updates/59 epochs|PASS; no script monitor or warm start|
|12|SHA/stage/registry/restart/tamper|lifecycle_evidence.json negative_cases; src/lstm_data/neural_artifacts.py:132; existing restart/race tests|PASS; exact CPU reload, final-only forecast|
|13|Actual P3 forecast and source invalidation|lifecycle_evidence.json forecast/replacement; src/lstm_data/neural_lifecycle.py:485; src/lstm_data/e5_lifecycle_audit.py:29|five finite ordered scores, no target/exit input or replay; new prep/input rebuild, new weights NOT_FITTED|
|14|Preservation, scope and final checks|preservation.json, P49_preservation.json, checks.json; 1454 tracked/599 raw hashes; 677 tests; 150 types0/0; Ruff PASS|PASS engineering; G0–G4 HOLD,16/33/7,0/40; no Git integration|

Decision: accept/reject the scoped synthetic engineering closure and its cap/zero-MAD limitations. This does not approve real E5, source/action/publication/formation gates, the provisional historical universe, P4.3/P4.10–P4.13, trading, confirmation or Git integration. Upstream review statuses remain independently pending where recorded.

All source, function and test references are repository-relative; open the named JSON/MD files from this directory. The APIv3 and coding-session report give portable commands. No further task was launched.
