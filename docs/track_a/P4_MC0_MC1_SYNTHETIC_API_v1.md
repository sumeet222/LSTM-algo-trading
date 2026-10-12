# P4 MC0/MC1 synthetic engineering API v1

Package `TA-P4-MC0-MC1-SYNTHETIC-001`. This extends the human-reviewed
[P4.1/P4.2 API](P4_NEURAL_ENGINE_API_v1.md) without activating observed experiments.
G0–G4 scientific readiness, empirical G6/G7 and P4.3/P4.4/P4.5 fitting remain HOLD.
The original ordered five-stock universe and separate SPY information series remain
unchanged; SPY is neither a sixth prediction stock nor verified USA500/Track B data.

## Models and shapes

`neural_models.create_model(architecture="TM0") -> SharedLSTM | EndpointGatedLSTM`
accepts exactly TM0/MC0/MC1. TM0 still uses the original shared 16→32→1 core (6433
parameters). MC0 reuses `SharedLSTM(21)` (7073). Both use independent zero-state
48-step sequences, one layer, final-hidden dropout .10 and a scalar shared head.

`EndpointGate.forward(endpoint: Tensor) -> Tensor` takes `(origins,5)` float32
endpoints and returns `(origins,16)` as `16*softmax(W*m+b)` with fixed tau1.
Both W(16,5) and b(16) initialize to zero; all multipliers initially equal one.
There is no temperature, extra dropout, clipping, penalty or market-only head.
Numerical nonfinite logits or softmax underflow to zero fail closed; extreme logits
are never repaired by clipping or a forced identity fallback.

`EndpointGatedLSTM.compose(joined) -> (gated_joined,alpha)` takes flattened complete
origins `(origins*5,48,21)`, checks identical market histories across each group of
five and computes one gate from its endpoint. It multiplies only the 16 stock
channels across every stock/step. Each historical direct U1–U5 row remains intact.
`forward` runs the same 21-channel core on those composed sequences; total7169.
Changing an earlier market row changes direct information, not the endpoint gate.
Only identity tests copy MC0 core weights; ordinary calibration/refit always create
fresh models and optimizers through the factory.

`SessionBatch` adds width21 to the original width16 contract, retaining complete
sessions×two origin positions×five stocks×48 steps. Shared market history is checked;
no missingness channel is appended. `batch_prediction`, `session_losses`, the
16-session sampler, AdamW and one global norm1 clip remain the common path. Gate
matrix decay .01 and bias decay0 follow the existing matrix/bias classifier.

## D7 input and publication evidence

`neural_market.MarketStamp(timestamp,period_end,available_at,evidence_ids)` describes
explicit fabricated publication evidence at the vector's own historical step.
`MarketEvidence(version,vectors,stamps)` holds one synthetic source history. `validate`
requires unique matching timestamps, synthetic source IDs/basis, exact clock/source
provenance, finite aware UTC clocks, period_end≤available_at≤own step, and age≤90min.
Explicit missing source vectors may have absent clocks and no evidence; a claimed
valid vector with unknown/late/NaT clocks is refused. These are caller assertions
about fabricated vectors, not historical vendor timing certification.

`MarketEvidence.extend(later)` allows only an identically versioned source extension;
overlapping values, masks/reasons or publication evidence cannot be replaced.
Unrelated future observations are not admitted to a historical input. Invalid
publication inside the supplied evidence is refused before evaluation.

`market_input(row: BaselineInput,prep: Preparation,history,permission,context="ASOF")`
returns `(processed_input,trace_hash)`. It has no label/exit-availability argument.
It reuses existing P3 `Preparation.apply` and FT0/D7 validation and P2 D7 scaler
math, supplementing those older windows with explicit clock evidence. Exact stock
order, 48 scheduled completed steps, scaler/floor identities and contexts are
mandatory. Endpoint must be valid and ≥46/48 complete market vectors valid. Invalid
historical vectors become standardized `(0,0,0,0,0)` with a separate mask. 45/48,
missing endpoint, wrong shape/order, forged context and stale ASOF fits fail closed.
Training-constant channels remain standardized zero, and novel later values retain
the existing P2 channel flags. No raw indicator formulas or market-floor algorithms
are duplicated in P4.

`make_market_view(data: FitData,window,prep,permission,history,allow_synthetic=False)`
wraps the existing `NeuralView`: one canonical stock table, one unique market-time
table and lightweight origin indices. Dense shared histories exist only in current
batches. Canonical tensor mutation is detected. D7 training fits count valid unique
market times once; the full input history/masks remain preserved. Old-step ASOF
certificate exclusions keep the original 63-calendar-session tail and recheck50/25
adequacy. An inadmissible market window fails the affected synthetic pair rather
than supplying an artificial complete vector.

`market_data_identity` binds raw stock inputs/labels, market vectors/versions/masks,
clock evidence and market fitting populations. `market_preparation_identity` binds
actual FT0, TG0, market-scaler and market-floor objects and their fit windows.

## Shared lifecycle, artifacts and forecasts

`run_pair(data,stage,fitted_at,permission,out,seed=42,mode=MODE,architecture="TM0",
market_history=None,synthetic_validation_trace=None)` keeps the old default.
MC0/MC1 require explicit matching `MarketEvidence`; TM0 rejects it. Only
ENGINEERING_SYNTHETIC_ONLY with fabricated FitData is allowed. Real context and
observed source paths have no executor.

The D6 selector itself is unchanged: strict .999 qualifying improvement, patience10,
earliest stop12, cap60, last63 XNYS inner sessions and50 distinct/25 each-origin
adequacy. Full-prefix refit uses fresh preprocessing, model and optimizer for exactly
the selected epoch count. No early stopping or warm start is added to refit.

`synthetic_validation_trace` is an optional bounded, config-hashed **fabricated
selection oracle**, not an empirical validation metric. Actual train/validation
forward/gradient/loss passes still run and are recorded separately. The audit uses
12 script-monitored calibration epochs selecting1, then1 fresh refit epoch per
architecture. This exercises stopping/refit without repeating 60-epoch planted
examples. All such artifacts explicitly identify their scripted selection monitor;
no passing real G6, predictive alpha or empirical comparison is claimed.

`PairRun` retains its original fields and adds optional `market_history`.
`PairIdentity.information` uses FT0_D7_MC0 or FT0_D7_MC1; stock-only legacy identities
remain readable. Architecture-specific model versions and exact tensor schemas
prevent cross-family loads. Source, fit, mask, order, clock, seed, config and code
changes invalidate reuse. `weights_only=True`, SHA checks, immutable publication,
final-only prediction authority and same-CPU full-epoch boundary restart are reused.
An interrupted whole lifecycle still requires a new attempt directory.

`forecast_scores(run,row,permission,market_history=None)` retains TM0 calls. Market
models require a version-matched extension with the final fitted normalization;
only the 48 keyed historical steps enter the model. Final completed registry SHA,
fit binding, code/order and input clocks are checked. Five scores become the
original P3 `Forecast` type; its identity binds the checkpoint and complete input
trace. No policy/friction/accounting API or trading replay is changed.

## Bounded diagnostics and reproduction

`gate_diagnostics(weights)` emits channel means/SD, quantiles, min/max, entropy,
concentration/saturation, positivity/sum errors and constant-gate warnings.
`epoch_pass` adds MC1 gate/input gradient norms and per-epoch aggregate gate summaries.
`trace_model(model,joined,provenance)` is a cheap eval-mode T0/T1 hook for at most two
fabricated origins, showing input-versus-gated channel means, five scores/order and
source trace. It restores model train/eval mode. No hidden-state or tensor archive,
financial importance, Rank IC or statistical/economic claim is emitted.

Use the existing README optional neural extra (torch2.10.0), repository .venv and
CPU float32. No new dependency, credentials, raw archives or provider access is needed.

```sh
.venv/bin/python -m lstm_data.neural_market_audit --mode ENGINEERING_SYNTHETIC_ONLY --out reports/data_audit/my_new_market_audit
.venv/bin/python -B -m pytest -q tests/test_neural_market.py tests/test_neural_gate.py
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist
.venv/bin/ruff check .
.venv/bin/python -B -m pytest -q
```

The audit uses one fabricated source store and seed42; seeds123/2026 are constructor
checks only. Private synthetic registries never reserve/debit the scientific40-pair
ledger. Same-device CPU reload equality is measured; cross-device equality is not
promised. This is a synthetic reproduction route, not a final real-data portability
rehearsal or collaborator signoff.

Later approved recovered candles require a new immutable source version, upstream
causal FT0/U1–U5/targets/retention, verified action/publication evidence, new fitted
certificates and checkpoints. They plug into typed adapters after separate approval;
never patch stale fitted artifacts. G0–G4 and all16 P2/33 P3 deferrals stay unchanged.
No MC2, P4.6, model promotion, confirmation, real fit, simulation or Git integration
is authorized by this API.
