# Gate D — independent calibration and evaluation

PASS: 13 synthetic tests passed in 4.901 seconds. The clean basic Pyright check reports **0 errors, 0 warnings, 0 informations**. This gate covers mathematics and newly generated synthetic score persistence; no empirical model was fitted, market data read, historical results opened, network accessed, or Git operation performed.

The only behavioral authority was the complete `replication/EXPERIMENT_SPEC.md`. New code is in `code/evaluation.py`, synthetic tests in `tests/test_evaluation.py`, and the isolated static configuration in `audit/pyright_evaluation.json`. File digests and environment versions are recorded in `evaluation_gate.json`. Installed third-party libraries were used with the existing `.venv` interpreter.

The implementation includes own C3 calibration, unclamped residuals, category moments using inherited weights, effective-session shrinkage with kappa 25, strict calibration maturity, recipe/checkpoint identity, RAW and C3 decoding, frozen restricted-refit tail cut points, canonical twenty-stock score validation, full-key joins, annual and equal-year scalar/rank/event/signed diagnostics, early-close cohorts, and clamping-induced tie counts. Scalar conditional weights retain original mass; rank category reducers rebuild session means. EQ primary ratio divides mean predicted by mean observed. Undefined scalar ratios retain NaN/inf, while undefined signed correlation is null/NaN.

Score bundles are newly created directories containing Parquet plus a manifest with SHA-256, calibration identity, coefficients, and restricted-refit thresholds. Existing bundles cannot be overwritten. `report_only_replay` verifies the bundle and regenerates the reports with zero fitting calls. Decoder outputs are checked again when writing and reading. A shuffled full-key join fixture verifies stable alignment and rejects label/key/population mismatches. No comparator decile or uncertainty table is synthesized; the reports identify those outputs as pending separately authorized independent comparators.

The first synthetic run identified a pandas 3 read-only NumPy view in signed-weight normalization. An explicit copy fixed it, and all tests were repeated. Static diagnostics concerned pandas union return annotations; explicit runtime shape/type checks and typed NumPy reductions resolved them without suppressions, casts, severity changes, or weakened tests.

Reproduction uses `REPO_ROOT` for the checkout and a clean temporary working directory. The executed command forms below had `REPO_ROOT` expanded to the active checkout. Neither command reads the original project configuration:

```sh
"$REPO_ROOT/.venv/bin/python" -I -c 'import sys, runpy; sys.path.insert(0,"<REPO_ROOT>/replication/phase2/code"); runpy.run_path("<REPO_ROOT>/replication/phase2/tests/test_evaluation.py", run_name="__main__")'
"$REPO_ROOT/.venv/bin/python" -I -m pyright --project "$REPO_ROOT/replication/phase2/audit/pyright_evaluation.json" --pythonpath "$REPO_ROOT/.venv/bin/python"
```

For the first command, substitute the same checkout value inside the two Python string literals. The test installs the new phase-2 import boundary before importing third-party packages. The second command checks only the new evaluation module and test. Pylance editor verification remains human-confirmed: select the repository `.venv/bin/python`, retain basic severity, reload the language server, and refresh Problems for these files. This is not a claim of an original-project-wide editor check.

Known runtime note: PyArrow emitted denied `sysctlbyname` cache/NEON probes inside the filesystem sandbox. Parquet round-trip, digest verification and replay still passed. No escalation, changed package, or environmental workaround was required.

The lead must supply canonical metadata, actual new model/recipe digests, lawful calibration and restricted-refit role populations, and the real OOS scores. Historical nominal-origin/two-minute issuance mismatch, retrospective action policy, fixed survivor universe, and label-completeness scoreability are preserved by the surrounding authorized reconstruction; this module does not reinterpret them. This receipt is part of the clean phase-2 handoff, and the lead owns the overall session/Git report.
