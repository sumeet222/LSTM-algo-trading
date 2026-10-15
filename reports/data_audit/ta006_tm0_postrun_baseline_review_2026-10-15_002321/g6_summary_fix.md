# Future G6 summary correction

Before: real_bridge_run examined sustained clipping in refit_trace only. Actual Package005calibration 5, 7–14warnings were omitted from its raw PASS. Effective historical WARN already existed and remains intact.

After: reusable neural_health.g6_summary requires sequential nonempty telemetry for both passes, propagates calibration/refit clipping, keeps constant-score/max-epoch warnings and returns FAIL for recorded nonfinite gradients/dispersion. The runner now calls that aggregator for future results. No training math, sampler, optimizer, thresholds, seeds, stopping or checkpoint bytes changed. This does not expand the runner's TM0-only permission/registry scope.

Four narrow unit tests cover calibration-only warning, clean both-pass PASS, refit warning, and nonfinite/missing-pass failure. Actual saved pilot traces produce WARN with the exact9calibration warning epochs and0refit warnings. The old4bridge source files are archived byte-for-byte under historical_source/*.py.txt solely as historical evidence. source_changes.diff contains the only pre-existing source edit. No historical artifact/code-hash field was regenerated; new future code has a different identity and rejects the consumed old neural permit.
