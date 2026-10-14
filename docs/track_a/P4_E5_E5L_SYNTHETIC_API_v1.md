# P4.8 / P4.9 synthetic prerequisites v1

Package `TA-P4-E5-NEURAL-E5L-DIRECTED-RIDGE-SYNTHETIC-001` remains
**SYNTHETIC_PREREQUISITE_ONLY / HUMAN_REVIEW_PENDING**. Both engineering gates
are **PARTIAL**, for distinct reasons. No historical dataset, scientific pair,
universe activation, LL neural architecture or economic replay is authorized.

## E5 neural route

`create_model("E5")` returns the original one-layer `SharedLSTM`, now with 23
inputs, width32, final-hidden dropout.10 and one shared scalar head. Its count is
`4*32*(23+32+2)+33 = 7329`: input matrix2944, recurrent4096, biases128+128,
readout32+1. TM0/MC0/MC1 retain their computation and model versions.

`make_e5_view(data: FitData, window: FitWindow, prep: Preparation,
permission: Permission, history: MarketEvidence, allow_synthetic=False) -> E5View`
is an additive wrapper over P4.7 `PeerView`. One stock table, one market table and
window indices remain shared. Only current ephemeral batches become
sessions×2×5×48×23 `SessionBatch` values. All four peers must be valid. The first21
channels, targets, origins, underlying48 scheduled clocks and separate market
masks are conserved. `SessionBatch.validate` rejects forged peer channels.

For already scaled M1 values z, the extra channels are the target-excluding mean
`sum(z_j)/4` and population dispersion `sqrt(sum((z_j-mean)^2)/4)`. The existing
`peer_summaries` implementation is reused, without another scaler or clipping.
This tests peer access; the common-sum-minus-own algebra can preserve rankings
and does not establish directed transmission.

The existing `run_pair(..., architecture="E5", market_history=...)`, `epoch_pass`
and `forecast_scores` now accept this adapter and retain the frozen D6g sampler,
loss, optimizer, clip,63-session tail,60/12/10/.999 selector and fresh refit.
E5 batches expose peer-gradient telemetry. Checkpoints bind E5 information,
architecture, data/order/source/cutoff/preprocessing/config/seed/code. Final-only
prediction, corruption/stale identity rejection and same-CPU boundary resume
share the original checkpoint implementation.

**This session did not execute E5 calibration/refit or issue its final-refit P3
forecast.** A60-step,16-whole-session fabricated learning-health fixture had
initial MSE.22563854, final.14391030 and peer-zero ablation.21520402, with positive
peer gradients. It missed the fixture's pre-existing engineering proof criterion
`final < .35*initial and ablation > 2*final`; that criterion is not a scientific
hyperparameter or frozen empirical threshold. One identical replay added missing
error metrics; no fixture/seed/optimizer changes or subsequent fit occurred.
The failure is retained, not reclassified as a PASS. Full E5 D6g/forecast
integration remains unproved pending review of the incomplete learning proof.

`e5_input(row, prep, history, permission) -> (Tensor[5,48,23], binding)` is a
label-free forecast input constructor. `trace_e5(model, values, SYN:provenance)`
provides one origin's endpoint M1/peer values and scores without a full history
dump. An untrained trace has no forecast authority.

## Formation, antecedents and directed signals

`formation_pair(universe: UniverseSpec, rows: tuple[FormationRow,...], permission)
-> FormationPair` requires all300 unique fictional stock/session records over
the exact preceding60 XNYS sessions before2020-07-01. Each daily close×volume
must be positive, have qualified synthetic units/source and be available after
the daily close but strictly before formation. Unique high H and low L are fixed;
ties fail with `HL_TIE_UNRESOLVED`. The SHA binds the ordered complete table,
universe and qualification. `target_flags(pair)` returns five×2 [isH,isL].
This certifies only the injected fixture. Actual named-stock H/L remains
`HL_REAL_UNRESOLVED`; engineering-profile metadata does not certify formation.

`Antecedent` carries the exact previous full `ScheduledStep`, five upstream raw
M1 feature values, five own-step publications/source IDs, ordered universe,
source/action/scaler bindings, synthetic basis and verified synthetic unit
evidence. This additive one-step schema represents lag48 before a48-step window.
The existing FT0 certificate transforms these features once. Unknown/NaT/late
clocks, label/exit/outcome source IDs, missing stocks, different identities,
unverified units, noncontiguous/incorrect steps and closing stubs fail closed.
No padding, first-step copying,48→47 reduction or invented observations.

`directed_window(row, prep, history, permission, calendar, pair, antecedent,
context="ASOF") -> DirectedWindow` first calls existing `peer_input` for strict
P2/FT0/D7 checks. It preserves processed controls and constructs five×48×5:

1. `H_TO_L_0 = 1{i=L} z_H(s)`;
2. `H_TO_L_1 = 1{i=L} z_H(s-1)`;
3. `L_TO_H_0 = 1{i=H} z_L(s)`;
4. `L_TO_H_1 = 1{i=H} z_L(s-1)`;
5. `PEER_MEAN_1 = mean_{j!=i} z_j(s-1)`.

Forty-nine immutable synthetic M1 samples retain every source/publication/step
identity. Signals, flags, pair, source/scaler/order/code and content are bound;
mutation invalidates them. `trace(calendar,index=47)` gives a single exact
current/previous timestamp pair, flags, signals, publications and wall-clock age.
Ordinary overnight lag1 is1140min; the March2021 DST weekend is3960min; after the
November2020 early close it is4200min. Lag1 means one full scheduled observation,
never a uniform60 elapsed minutes, and the terminal stub is omitted.

## Ridge decision gate and sham

Frozen D8§10.3 and D13§17 specify two identical H/L identity controls but do not
specify their ridge flattening placement. Both interpretations remain visible:

| Convention | LL0-R | LL1-R |
|---|---:|---:|
| Flags once after unchanged147+14=161 prefix |163|198|
| Flags repeated at each of seven lags |175|210|

Repeating identical columns changes the effective coefficient penalty to λ/7.
The layouts are not interchangeable under the frozen penalty grid.
`ridge_layout_status()` returns `HUMAN_LAYOUT_DECISION_REQUIRED`;
`directed_ridge_fit()` always refuses. **No production design/fit API, LL ridge
selection/refit, planted forward/reverse/null coefficient comparison or sham
predictive score is claimed.** The original147/161 matched ridge and shared P3
selection/solver/kernel remain untouched. After a layout decision the additive
adapter must reuse them; no new solver, lag dictionary or hyperparameter grid.
LL0/LL1 neural25/30 channels and7585/8225 counts are informational frozen
contracts only; their factories reject, as do MC2/SP3/SP1/LL2/LL3.

`timing_destroy(window, history: tuple[CompletedM1,...], eligible_sessions,
calendar) -> ShamResult` shifts the same source stock to the same scheduled slot
exactly10 preceding caller-declared eligible exchange sessions. Calendar closure,
early-close slots and missing source keys are not fabricated. Source/scaler/unit
binding and unique keys must match. Any missing antecedent excludes the whole
origin identically from LL0,LL1 and shifted arms, with reason counts. Controls
remain in `window.processed`; only peer-signal values are shifted. Current→prior
pairs are recorded explicitly. This is a weak timing-destruction sham, **not** a
formal temporal permutation, p-value or selection-adjusted inference; availability
and marginal distributions may change. Matched fit evidence awaits the ridge gate.

## Reproduction and activation boundary

Existing README setup and approved torch2.10.0 suffice; no dependency, credential
or source archive is needed. Reuse the failure to regenerate independent math
without retraining, choosing a NEW output directory:

```sh
.venv/bin/python -B -m lstm_data.e5_audit --mode ENGINEERING_SYNTHETIC_ONLY --out reports/data_audit/<NEW-directory> --failed-health-proof reports/data_audit/ta_p4_e5_e5l_2026-10-13_225047/failed_health_proof.json
.venv/bin/python -B -m pytest -q tests/test_e5_neural.py tests/test_directed_peers.py tests/test_neural_engine.py tests/test_neural_artifacts.py tests/test_neural_lifecycle.py
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist
.venv/bin/ruff check .
.venv/bin/python -B -m pytest -q
```

The failure-proof SHA and exact logged historical code SHA are retained; this is
not a fitted current-code checkpoint. Omitting the proof explicitly reruns the
same learning fixture in a new report, rather than silently replacing its failure.
Neither route automatically launches calibration/refit or LL fits.

Resolve the ridge flag decision and incomplete E5 learning proof before claiming
engineering completion. Upstream P4.4/P4.5/P4.6/P4.7 human acceptance is still
pending. G0–G4 remainHOLD; realG5/G6/G7 remainNOT_RUN; real pairs0/40. Separate
scientific prerequisites include D1/formation, native units/actions/vintage,
publication/minute execution, genuine FT0/TG0/floors/scalers/retention, joint/course
clocks/source sign-off and P4.3/MC0 precedents. Changed certified datasets/order/
fits/policies require new bindings and full rebuilds; no stale checkpoint reuse.
P4.10–P4.13 and optional architectures remain unactivated.
