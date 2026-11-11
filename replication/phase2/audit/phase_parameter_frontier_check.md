# Supplemental phase-parameter frontier check

**PASS. This post-prefit completeness verification ran while real fits were already running. It was NOT part of the prefit64 fixtures.**

Existing inspected fixtures perturb future labels for feature/recipe frontiers and frozen calibration. No direct before/after external-future perturbation of phase target scale and auxiliary weights was found.

Only synthetic parameter arrays were used. No model was constructed, fit or evaluated, no real data/outcomes were opened, and no numerical code or test file was edited.

| Quantity | Expected | Before | After |
|---|---:|---:|---:|
| s_phase | .02 | 0.02 | 0.02 |
| S | 3 | 3 | 3 |
| S_N | 2 | 2 | 2 |
| Z | .875 | 0.875 | 0.875 |
| Maximum auxiliary-weight change | 0 | 0 | 0 |

Expected supported origin masses are [0,1/7,2/7,4/7]. All phase labels, masks, base weights and normalized weights are unchanged; normalized weights are byte-identical. Future R changes from .005 to 1,000,000 through 1,000,059; future support is removed and auxiliary labels become NaN. Only lawful indices [0,1,2,3] enter estimators.

A deliberately unsliced synthetic sensitivity control changes s from 0.01 to 0.04 and Z from 0.9374999999999998 to 0.4375. This confirms the perturbation matters if future rows are wrongly admitted. No model fit is involved.

This checks admitted-role API isolation. It does not replace role-generation/maturity tests or retrospectively change the prefit fixture count.

Executed UTC: 2026-11-02T23:49:38.067587+00:00 through 2026-11-02T23:49:38.085828+00:00. JSON contains expected/actual results, exact executed source and identical before/after frozen source hashes.

Reproduction: from a clean directory use the existing interpreter with -I, define audit_source as this source text and execute it with the repository path as argv[1]. Output creation is exclusive and will refuse to overwrite this completed receipt.

```python
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "replication/phase2/code"))
import boundary
boundary.install()
import numpy as np
import model
started = datetime.now(timezone.utc).isoformat()
files = ["replication/phase2/code/model.py", "replication/phase2/code/features.py",
         "replication/phase2/tests/test_model.py", "replication/phase2/tests/test_frontiers_review.py",
         "replication/phase2/tests/test_evaluation.py"]
hashes_before = {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in files}
sessions = np.array(["A", "B", "B", "C", "D", "D", "E"])
lawful = np.array([0, 1, 2, 3], dtype=np.int64)
future = np.array([4, 5, 6], dtype=np.int64)
returns = np.repeat(np.array([.01, .02, .02, .04, .005, .005, .005])[:, None], 20, axis=1)
overnight = np.array([False, True, True, True, True, True, True])
mask = np.ones((7, 20), dtype=np.bool_)
mask[0] = False
mask[1, 10:] = False
auxiliary = np.repeat((returns/3)[..., None], 3, axis=2)
auxiliary[~mask] = np.nan
def forbidden_inputs(indices):
    raise AssertionError("No windows or inference permitted in this parameter-only check.")
def snapshot():
    role_sessions = sessions[lawful].tolist()
    scale = model.fit_scale(returns[lawful], role_sessions)
    phase = model.PhaseData(role_sessions, returns[lawful], overnight[lawful],
                            auxiliary[lawful], mask[lawful], forbidden_inputs, scale)
    weights = model.auxiliary_weights(phase.sessions, phase.overnight, phase.auxiliary_mask)
    return phase, weights
before_phase, before = snapshot()
unsliced_s_before = model.fit_scale(returns, sessions.tolist())
unsliced_z_before = model.auxiliary_weights(sessions.tolist(), overnight, mask).mass
returns[future] = 1_000_000 + np.arange(60, dtype=np.float64).reshape(3, 20)
mask[future] = False
auxiliary[future] = np.nan
after_phase, after = snapshot()
unsliced_s_after = model.fit_scale(returns, sessions.tolist())
unsliced_z_after = model.auxiliary_weights(sessions.tolist(), overnight, mask).mass
expected_weights = np.zeros((4, 20), dtype=np.float64)
expected_weights[1, :10] = 1/70
expected_weights[2] = 1/70
expected_weights[3] = 1/35
assert before_phase.scale == after_phase.scale == .02
assert before.mass == after.mass == 7/8
assert before.sessions == after.sessions == 3
assert before.overnight_sessions == after.overnight_sessions == 2
np.testing.assert_array_equal(before_phase.signed_returns, after_phase.signed_returns)
np.testing.assert_array_equal(before_phase.auxiliary_returns, after_phase.auxiliary_returns)
np.testing.assert_array_equal(before_phase.auxiliary_mask, after_phase.auxiliary_mask)
np.testing.assert_array_equal(before.base, after.base)
np.testing.assert_array_equal(before.values, after.values)
np.testing.assert_allclose(before.values, expected_weights, atol=1e-15, rtol=1e-15)
assert unsliced_s_before != unsliced_s_after
assert unsliced_z_before != unsliced_z_after
hashes_after = {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in files}
assert hashes_before == hashes_after
completed = datetime.now(timezone.utc).isoformat()
receipt = {
    "status": "PASS",
    "timing": "Supplemental post-prefit completeness audit while real fits were already running. NOT part of prefit64.",
    "started_utc": started, "completed_utc": completed,
    "no_model_constructed_or_fit": True, "no_inference_or_input_access": True,
    "no_real_data_or_outcomes_accessed": True,
    "frozen_code_tests_unchanged": True,
    "hashes_before": hashes_before, "hashes_after": hashes_after,
    "existing_coverage_review": {
        "test_frontiers_review.py::test_future_source_and_labels_leave_prior_features_and_phase_recipe_invariant":
        "Future source/R perturbation checks prior features and recipe, not target scale or auxiliary weights.",
        "test_evaluation.py::test_future_oos_labels_cannot_change_frozen_coefficients":
        "Future A perturbation checks frozen C3 and decoded forecasts, not target scale or auxiliary weights.",
        "test_model.py":
        "Scale arithmetic, auxiliary hierarchy and inference label/mask invariance are covered separately; no direct external-future perturbation of phase scale/weights found."
    },
    "fixture": {"lawful_indices": lawful.tolist(), "external_future_indices": future.tolist(),
                "sessions": sessions.tolist(), "future_R_before": .005,
                "future_R_after": "1000000 through 1000059",
                "future_mask_after": False, "future_auxiliary_after": "NaN"},
    "expected": {"s": .02, "S": 3, "S_N": 2, "Z": .875,
                 "auxiliary_origin_masses": [0, 1/7, 2/7, 4/7],
                 "weight_max_absolute_change": 0, "phase_arrays_unchanged": True},
    "actual": {"s_before": before_phase.scale, "s_after": after_phase.scale,
               "S_before": before.sessions, "S_after": after.sessions,
               "S_N_before": before.overnight_sessions, "S_N_after": after.overnight_sessions,
               "Z_before": before.mass, "Z_after": after.mass,
               "origin_masses_before": before.values.sum(axis=1).tolist(),
               "origin_masses_after": after.values.sum(axis=1).tolist(),
               "weight_max_absolute_change": float(np.max(np.abs(before.values-after.values))),
               "weights_hash_before": hashlib.sha256(before.values.tobytes()).hexdigest(),
               "weights_hash_after": hashlib.sha256(after.values.tobytes()).hexdigest(),
               "phase_arrays_unchanged": True, "weights_bitwise_identical": True},
    "deliberately_unlawful_unsliced_synthetic_sensitivity_control": {
        "s_before": unsliced_s_before, "s_after": unsliced_s_after,
        "Z_before": unsliced_z_before, "Z_after": unsliced_z_after,
        "purpose": "Demonstrate that the changed external cells affect estimators if wrongly admitted; no fit performed."
    },
    "limitation": "Fixed lawful slice verifies estimator input isolation. It does not replace role-generation, maturity, real-run or causal-vintage tests.",
    "exact_executed_source": audit_source
}
audit = root/"replication/phase2/audit"
with (audit/"phase_parameter_frontier_check.json").open("x", encoding="utf-8") as stream:
    json.dump(receipt, stream, indent=2, allow_nan=False)
    stream.write("\n")
summary = [
    "# Supplemental phase-parameter frontier check", "",
    "**PASS. This post-prefit completeness verification ran while real fits were already running. It was NOT part of the prefit64 fixtures.**", "",
    "Existing inspected fixtures perturb future labels for feature/recipe frontiers and frozen calibration. No direct before/after external-future perturbation of phase target scale and auxiliary weights was found.", "",
    "Only synthetic parameter arrays were used. No model was constructed, fit or evaluated, no real data/outcomes were opened, and no numerical code or test file was edited.", "",
    "| Quantity | Expected | Before | After |", "|---|---:|---:|---:|",
    f"| s_phase | .02 | {before_phase.scale} | {after_phase.scale} |",
    f"| S | 3 | {before.sessions} | {after.sessions} |",
    f"| S_N | 2 | {before.overnight_sessions} | {after.overnight_sessions} |",
    f"| Z | .875 | {before.mass} | {after.mass} |",
    "| Maximum auxiliary-weight change | 0 | 0 | 0 |", "",
    "Expected supported origin masses are [0,1/7,2/7,4/7]. All phase labels, masks, base weights and normalized weights are unchanged; normalized weights are byte-identical. Future R changes from .005 to 1,000,000 through 1,000,059; future support is removed and auxiliary labels become NaN. Only lawful indices [0,1,2,3] enter estimators.", "",
    f"A deliberately unsliced synthetic sensitivity control changes s from {unsliced_s_before} to {unsliced_s_after} and Z from {unsliced_z_before} to {unsliced_z_after}. This confirms the perturbation matters if future rows are wrongly admitted. No model fit is involved.", "",
    "This checks admitted-role API isolation. It does not replace role-generation/maturity tests or retrospectively change the prefit fixture count.", "",
    f"Executed UTC: {started} through {completed}. JSON contains expected/actual results, exact executed source and identical before/after frozen source hashes.", "",
    "Reproduction: from a clean directory use the existing interpreter with -I, define audit_source as this source text and execute it with the repository path as argv[1]. Output creation is exclusive and will refuse to overwrite this completed receipt.", "",
    chr(96)*3+"python", audit_source.rstrip(), chr(96)*3
]
with (audit/"phase_parameter_frontier_check.md").open("x", encoding="utf-8") as stream:
    stream.write("\n".join(summary)+"\n")
print(json.dumps({"status":"PASS","s":before_phase.scale,"Z":before.mass,"weight_change":0.0,
                  "unsliced_s":[unsliced_s_before,unsliced_s_after],
                  "unsliced_Z":[unsliced_z_before,unsliced_z_after],
                  "frozen_files_unchanged":True,"timing":"post-prefit, not part of64"}))
```
