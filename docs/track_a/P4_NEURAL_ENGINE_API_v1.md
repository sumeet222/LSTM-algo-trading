# P4.1–P4.2 synthetic neural engine API v1

TA-P4-NEURAL-ENGINE-LIFECYCLE-001. This software permission does not activate
historical fitting, scientific G5/G6, confirmation or P4.3. Original source,
frozen protocols, 16 P2/33 P3 scientific deferrals and real pair usage remain intact.

## Setup and hermetic entry point

Use the README environment and `pip install -e '.[dev,neural]'`. The explicitly
approved optional `neural` extra pins PyTorch 2.10.0; no torchvision/torchaudio is
required. A full test checkout needs this extra. Torch must provide a compatible
wheel for the chosen Python/platform. CPU is the synthetic audit default; MPS
availability is reported but no MPS or cross-device equivalence is claimed.

```sh
.venv/bin/python -m lstm_data.neural_audit --mode ENGINEERING_SYNTHETIC_ONLY --out reports/data_audit/my_new_g5
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist
.venv/bin/ruff check .
.venv/bin/python -B -m pytest -q
```

The CLI has no source path, provider, empirical-label or model-search argument.
`SCIENTIFIC_REAL` is rejected before creating output or fixtures. Existing
destinations are refused. The fixture uses fabricated FT0 and existing synthetic
TG0/preprocessing, not observed stock data. One actual seed-42 two-pass example
is executed; the authoritative scientific ledger is read, never written.

## Computation

`neural_engine.SharedLSTM(input_dim=16)` accepts finite float32 sequences
`(sequences,48,d)` on the model's device. Standard one-layer `nn.LSTM(d,32)`
creates fresh zero h/c for every sequence/call. Final-hidden dropout 0.10 precedes
the shared `Linear(32,1)` head. There is no ticker head, persistent recurrent
state, recurrent/input dropout or price/order output. Actual parameter count is
6433 for d=16; d=21 is a structural utility only (7073), not a market experiment.

`SessionBatch(ids,inputs,targets,origins)` holds `(sessions,2,5,48,16)` inputs,
`(sessions,2,5)` targets and boolean `(sessions,2)` origin masks. Padding describes
an absent whole origin, never an imputed stock/feature. Every session must have
one or two complete ordered five-stock origins. Only valid sequences are flattened
for computation; predictions are restored before loss.

`session_losses(prediction,target,origins)` returns the five-stock mean squared
error averaged over each session's eligible origins. The batch loss is its session
mean. The independent 2/6 and 10 oracle gives session losses 4/10 and overall 7;
pooled-origin 6 is wrong. `epoch_pass` sums session losses and divides by the actual
session count across all batches, preserving a 16+remainder epoch.

`session_batches(count,seed,epoch,shuffle=...)` groups complete sessions, every
eligible session once, 16-session target, drop_last=False. Training permutations
depend only on the registered seed and epoch, with logged session-order hashes.
Validation is chronological; historical steps are never shuffled.

`optimizer(model)` creates two exhaustive disjoint AdamW groups: matrices decay
0.01, biases decay 0; lr0.001, betas(.9,.999), eps1e-8, amsgrad=False, no scheduler.
`clip(model)` applies one global L2 cap1 after backward and before step, rejecting
nonfinite norms. Scalar health reports preclip quantiles/multipliers, clipped
fraction, optimizer steps, score dispersion, target tails and session-loss
concentration; sustained clipping warns without changing any research setting.

## Certificates, canonical storage and chronology

`neural_data.make_view(data: FitData,window,preparation,permission,allow_synthetic=...)`
is a thin adapter over P3 `FitData`/`BaselineInput` and P2 fitting membership,
48 scheduled slots, all 16 channels, per-cell publication, floors/scaler application
and TG0. No feature or target mathematics is duplicated. It rejects observed basis,
unknown/future publication, missing cells, duplicate origins and conflicting
same-key feature values. A `NeuralView` stores one canonical step table and small
origin/window index lists. Full 48-step tensors exist only for the current batch;
no per-seed windows or copied Parquets are persisted. Tensor mutation changes the
content hash and blocks subsequent use.

`data_identity` hashes explicit raw inputs, clocks, source/action/version bindings,
scaler/floor identities, fitting observations and label provenance. It avoids
repeated giant certificate reprs. `preparation_identity` binds actual stock-only
scaler/floor/TG0 fit objects and window; unused market payloads do not enter TM0.

`run_pair(data,stage,fitted_at,permission,out,seed=42,mode=...) -> PairRun` uses
the existing `windows` constructor: validation is the last 63 actual XNYS sessions,
not surviving rows. It reuses maturity/purging and requires at least 50 eligible
validation sessions and 25 observations at each origin. The first validation
windows can fail the inherited P2 ASOF scaler-at-each-step rule: exclusions are
explicit, the calendar tail is not shifted, and adequacy is rechecked after
preprocessing. Training/refit use the existing HISTORICAL_TRAINING context; no
synthetic clock is promoted to historical publication certification.

Inner preprocessing uses only the training prefix. Validation cannot alter its
objects. Refit constructs fresh full-prefix preprocessing; changed raw-feature
floor basis fails with the existing upstream-rebuild requirement. Neither outer
development nor confirmation is passed to the stopping engine.

## Selection and refit

`EarlyStop.observe(loss)` consumes each completed epoch's mean-session validation
MSE in eval mode. First valid epoch is the baseline; qualifying improvement is
strictly `loss < .999 * qualifying_best`. Patience10 and earliest stop12 are
independent; cap60 has no epoch61. Exact ties keep the earliest checkpoint. Raw
minimum/epoch is recorded separately. Zero/near-zero losses require no division.
Missing/nonfinite/negative loss fails; invalid calibration cannot unlock refit.

Refit resets the seed stream, creates a new model and optimizer with no inherited
state, fits fresh preprocessing and trains exactly the selected epoch count.
Only its last-epoch checkpoint is prediction-authoritative. Calibration weights,
epoch traces, sampler hashes and actual stage updates/times are retained for audit.

## Artifacts, restart and future source replacement

`PairIdentity` binds track/family, ordered universe, information/TG0, fit windows,
source/features/data, preprocessing, frozen model/optimizer/selection, code/library
versions and seed/context. `PairRegistry` is synthetic-only and excludes the real
audit namespace. Exclusive same-machine locks protect reservation races; failed
and partial entries remain charged in isolated 40-pair/24-hour mock guards.
Identical completed fits require checksum verification for reuse. This is not an
authorized scientific reservation service; a later real executor must be reviewed.

`save_checkpoint` writes a new tensor-safe `.pt` and manifest atomically, refusing
overwrite. `load_checkpoint` uses `weights_only=True`, validates SHA, identity,
stage, epoch, preprocessing and exact finite tensor names/shapes/dtypes. Final
prediction verifies the complete registry's original SHA as well. Changed source,
normalization, order, target, cutoff, code/config or seed blocks stale reuse.

Explicit epoch-boundary snapshots may include model, optimizer, used Torch RNG
and completed trace. Frozen sampler order is re-derived from seed/epoch; NumPy and
Python RNGs are not used inside optimizer epochs. The same-CPU boundary recovery
test reproduces the uninterrupted next update. No mid-epoch resume is claimed.
`run_pair` refuses an existing attempt directory; an interrupted/failed complete
lifecycle must restart with a distinct attempt directory, never masquerade as
finished or warm-start a refit. Complete manifests remain immutable.

`forecast_scores(run: PairRun,row: BaselineInput,permission) -> p3_domain.Forecast`
loads only a completed final refit with exact refit preprocessing, code/order and
checkpoint binding. It validates ASOF input cells and emits five scores through a
thin P3 adapter. The forecast ID binds neural checkpoint/input identities without
changing P3 APIs. No current target or future exit-availability argument is present;
no portfolio simulation is run. This is also the small eval-mode T0/T1 replay hook,
not the full D13 economic replay.

Future genuine replacement data requires a new source namespace/version, upstream
features/TG0/eligibility, fresh floor/scaler certificates, baseline/neural refits and
new bound artifacts. Never graft repaired rows onto existing caches/checkpoints.
Historical source/action/execution/retention, joint approvals and empirical fitting
remain HOLD even after synthetic engineering tests pass. P4.3 is not started.
