# P4.6/P4.7 synthetic regime and peer API v1

TA-P4-E4R-MC2-READINESS-E5-PEER-SYNTHETIC-001. Fabricated inputs only,
ENGINEERING_SYNTHETIC_ONLY; all scientific activation remains HOLD. MC0/MC1
engineering review acceptance is REVIEW_ACCEPTANCE_PENDING until an attributable
human record supplies it. This API does not activate a universe, source or model.

## Regimes and MC2 arithmetic

`training_threshold(history: MarketEvidence, scaler: MarketScaler, permission) -> U2Threshold`
summarizes the exact unique fitted timestamp population of an existing synthetic
D7 scaler. Its median is computed after that scaler's transformation, with source,
fit time, population and scaler identity. It fits no new scaler or price indicator.
Evaluation outliers cannot change the fitted timestamp population or median.

`diagnostic_window(row, prep, history, permission, phase, context="ASOF") -> DiagnosticWindow`
reuses `neural_market.market_input` for P2 stock/D7 canonical transforms,
source/action/order, exact48 scheduled full hours, separate validity masks,
floor/scaler and own-step publication checks. Direct `DiagnosticWindow`
construction is an explicit already-standardized synthetic arithmetic oracle;
it is not a route for observed sources. Missing vector rows remain zero and masked,
with endpoint valid and at least46/48. Unknown, NaT, stale or future publication
is refused. An inadmissible origin is unavailable; callers omit it from admitted
states and retain its reason, never turn it into neutral. No confirmed sources or
protected-period data are accepted.

`classify(window, threshold) -> Regime`: U5 positive/negative/zero gives
BULL/BEAR/NEUTRAL. U2 strictly greater than its bound training median gives HIGH;
equality gives LOW. The threshold must be fitted by the relevant endpoint and
match its source and scaler. States are diagnostics, never learned categorical
inputs, trading signals or outcomes.

`occupancy(states, scheduled_sessions) -> dict` validates a complete contiguous
XNYS schedule. The earliest eligible origin anchors each day. Missing scheduled
sessions break episodes; holiday/weekend closures are calendar metadata, not extra
sessions. Occupancy uses sessions; origin slices retain per-origin labels and
within-day changes. Each state/cell needs30 distinct sessions and3 episodes;
otherwise SPARSE_EXPLORATORY_ONLY. Synthetic support always has NO_INFERENCE.

`variation(window)` excludes U1: delta is the maximum absolute endpoint difference
across U2–U5. Changed steps have delta>=1; A_t is changed/valid, qualifying at>=.25.
Invalid zero fills are excluded from both counts. `mc2_readiness(windows)` requires
unique matched TRAINING origins with no stock/batch repeats. Structural support
requires>=20% qualifying windows and>=20 distinct qualifying sessions. Its result
always remains SCIENTIFIC_NOT_ASSESSED / MC2_NOT_ACTIVATED. There is no MC2 model.

`paired_report(tuple[PairedRecord,...])` accepts only already issued fabricated
five-score records paired on exact state/window/threshold, source, target, fitting
identity and clocks. Outcomes must mature after issuance and before evaluation;
missing/duplicate/mismatched pairs fail closed. MSE is a synthetic arithmetic
oracle, averaged by origin within day then by day. Supplied MC1 gate weights reuse
`neural_models.gate_diagnostics`. Approved Rank IC and top/bottom metric code is
absent: those actual evaluations stay deferred; economic evidence is NOT_AVAILABLE.
No portfolio replay or financial/statistical inference occurs.

## Peer inputs and matched ridge

`peer_summaries(values: ndarray[5,48,16]) -> ndarray[5,48,2]` reads M1 through
`ORDER.index("M1")`. Exactly four target-excluding stocks enter each step's mean
and population dispersion, divisor4. Centered squared differences avoid
cancellation without clipping variance. Equal peers have dispersion0. Reordering
all five input rows consistently permutes outputs. Missing/nonfinite/partial
panels fail; no peer imputation or independent M1 normalization is introduced.

`peer_input(row, prep, history, permission, context="ASOF")` first reuses the strict
P2/P4 canonical clock/source/fit validation, then returns processed input,
peer summaries and source/code-bound trace. `peer_lag_vectors(...)` preserves the
original147-column ridge prefix byte-for-byte numerically, appending14 columns
in lag-major order: `(mean, dispersion)` for each lag0,1,2,5,11,23,47, corresponding
to exact48-step indices47,46,45,42,36,24,0. The original112 stock prefix and35 market
columns retain their old coefficient mapping.

`make_peer_view(data, window, prep, permission, history, allow_synthetic=False) -> PeerView`
wraps the existing indexed `MarketNeuralView`. It references one canonical16-channel
stock table and one5-channel market table; no per-model dense history storage.
`PeerView.batch(positions) -> PeerBatch` computes ephemeral23-channel float32 CPU
inputs, retaining the exact MC0 prefix, targets, origin population and masks.
`PeerBatch` is a data-only type intentionally unsupported by the current neural
factory/SessionBatch. No E5 model or neural fit is supplied by this package.

`matched_peer_ridge(data, stage, history, permission, allow_synthetic=False)` calls
the shared P3 `baseline_fit.selection_fit` kernel for147/161 controls. That kernel
is extracted from the original `select_and_refit`; the latter retains its112/147
public model/forecast contract. The optional typed `DesignAdapter` contributes
strictly validated synthetic inputs and either0 or14 trailing columns. Original
P3 fitting, purging,63-session calendar tail,50-day/25-each-origin guards,
training-only preparation, fixed five penalties, free intercept, weighted-mean
session MSE, larger-penalty exact tie and fresh full-prefix refit remain common.
The diagnostic returns fitted solutions and evidence, without model or forecast
authority. Both arms must have identical accepted and rejected origin keys,
TG0/scaler/floor identities and weights. A shared temporary transform cache binds
unique input IDs and actual preparation/context; no fitted dataset is persisted.

A shared common additive peer term need not change cross-sectional order.
Dispersion can differ by target even then. Computational correctness establishes
neither directed transmission nor incremental alpha.

## Reproduction and version replacement

Use the existing repository setup with the approved optional torch2.10.0 dependency,
.venv interpreter and basic Pylance severity. No credentials, source archives,
network, additional dependencies or Git integration are required:

```sh
.venv/bin/python -m lstm_data.regime_peer_audit --mode ENGINEERING_SYNTHETIC_ONLY --out reports/data_audit/<NEW-directory>
.venv/bin/python -B -m pytest -q tests/test_regime_diagnostics.py tests/test_peer_inputs.py
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist
.venv/bin/ruff check .
.venv/bin/python -B -m pytest -q
```

The audit supplies one fabricated100-session source and small pinned arithmetic
oracles; no neural training pair or scientific ledger reservation. It writes only
compact synthetic evidence to a new immutable directory. Resource measurements
are observed execution values; same-device float arithmetic does not promise
cross-device bit equality.

New prices, actions, clock evidence, order or fits require new immutable source,
feature/target/certificate versions and new diagnostic identities. Peer view IDs
include source, preprocessing, order, indexed masks, code and table hashes;
mutation/rebinding rejects stale reuse. Existing MC0/MC1/TM0 cores and checkpoints
are conserved. The narrow P3 kernel extraction changes its code SHA, so old fitted
forecast artifacts retain their old code binding and cannot be silently reused
under the new code; no checkpoint migration or refit is performed here.

Actual RS1/MC2 source certification, genuine MC0/MC1 comparisons, real peer ridge,
empirical floors/scalers, retention, actions/execution/formal signoff, confirmation,
P4.8 E5 neural, P4.9 lead–lag and SP3 remain NOT_RUN/NOT_ASSESSED. Preserve all16 P2,
33 P3, candidate follow-ups and seven original blockers. A future human acceptance
of engineering is separate from any scientific activation authorization.
