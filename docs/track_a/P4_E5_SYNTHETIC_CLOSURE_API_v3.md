# E5 synthetic closure API v3

Additive to P4_E5_E5L_SYNTHETIC_API_v1/v2. This task replaces the engineering
health proof prospectively, preserving the original v1 FAILED result and both
unchanged inequalities. It changes no frozen architecture, optimizer, TG0,
calendar, stock universe, source approval or scientific budget. P4.9 ridge stays
163/198 penalized slopes with a separate free intercept and once-only H/L flags.
Upstream review acceptance is still pending where recorded; no approval inferred.

`e5_fixture_v2.fixture(null=False, version=FIXTURE)` fabricates the same100 XNYS
calendar-session WF1 population,48 full-hour histories and separate matured
four-hour proxy labels using existing P2/D7/TG0 preprocessing. The synthetic
features are upstream fabricated FT0 values, not real OHLC-derived indicators.
At each completed step, five independent Gaussian M1 values and one random B2
sensitivity recipient are generated first. Separate future return is
`1e-4 * B2_i * mean(raw_M1 of the four other names)`. Four returns are0; median/MAD 0
and actual fitted epsilon 1e-4 yield target `B2_i * peer_mean_raw`. This isolates
the frozen zero-MAD/floor branch, not general financial target behavior. Market
and other stock controls are deliberately constant with existing constant flags.
No label, future source value or ticker identity is supplied as a feature.

`e5_deep_audit.original_oracle()` performs no v1 optimization. Independent
finite-difference/autograd sensitivity, all48-step gradients and exact algebra
show why the old direct peer-mean arithmetic target is not a mature TG0 proof.
Its hypothetical TG0 centered mean is minus own centered M1/4; its common
component cancels in rankings. Original60-update losses remain failed.

The immutable `fixture_v2_config.json` and `E5_HEALTH_FIXTURE_v2_DESIGN.md` were
written before fitting. Primary256-update health failed. One separately
preregistered1024-update horizon extension retained the same fixture, seed 42,
thresholds, architecture and optimizer. Both attempts remain. Each includes
actual E5, own+market MC0, independent-label null and exact primary repeat. MC0
has 7073 parameters versus E5's 7329; the independent conditional Bayes oracle
proves own-information insufficiency without a capacity-equality claim. Ordinary
D6g remains capped60 epochs. No additional horizon/fixture/seed search is active.

`e5_lifecycle_audit.run(out)` requires SHA-bound passing health and performs the
actual `neural_lifecycle.run_pair(... architecture="E5")` with
`ACTUAL_INNER_MSE`, no scripted monitor. It selected59 at cap60, with 55 eligible
validation sessions/55 each origin,180 calibration updates and413 updates in a
fresh 59-epoch refit. Calibration underfit/cap warning remains explicit. Two
immutable checkpoints are authoritative only for their own stages; selected
calibration is audit-only. Final CPU reload and repeated five-score P3 forecasts
are exact; no trading replay occurs. The original model/lifecycle/checkpoint code
is unchanged.

A changed source version rejects old preprocessing/checkpoint/forecast reuse.
Fresh replacement preparation and inputs are rebuilt in a new identity while
sharing the same immutable raw tuples. Changed numerical training content also
changes data identity. New-source neural weights would require a fresh pair;
none is copied or relabeled as refitted.

Reproduce in a NEW task directory after copying the preserved prospective config
and design files (including the extension config) from the review packet:

```sh
.venv/bin/python -B -m lstm_data.e5_deep_audit --out reports/data_audit/<NEW> --stage original
.venv/bin/python -B -m lstm_data.e5_deep_audit --out reports/data_audit/<NEW> --stage oracle
.venv/bin/python -B -m lstm_data.e5_deep_audit --out reports/data_audit/<NEW> --stage health
.venv/bin/python -B -m lstm_data.e5_deep_audit --out reports/data_audit/<NEW>/extension_1024 --stage health
.venv/bin/python -B -m lstm_data.e5_lifecycle_audit --out reports/data_audit/<NEW>
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist
.venv/bin/ruff check .
.venv/bin/python -B -m pytest -q
```

Outputs refuse overwrite. Existing root and extension config SHAs are explicitly
registered; editing thresholds/horizons invalidates execution. Current CLI uses
CPU float32/one thread, torch2.10.0; no cross-device bitwise promise. No provider
requests, credentials or dependency change. Synthetic engineering does not
activate real E5, P4.3, P4.10–P4.13, LL neural, MC2/SP3, source/action gates,
confirmation or a production universe. G0–G4,16 P2/33 P3 deferrals, seven ledger
blockers and scientific 0/40 remain unchanged. Human review is required.
