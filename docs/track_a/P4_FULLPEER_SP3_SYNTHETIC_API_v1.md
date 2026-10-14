# Full-peer / SP3 synthetic readiness API v1

This additive P4.11 interface runs in `ENGINEERING_SYNTHETIC_ONLY`. It accepts
fabricated ordered-five inputs and caller-supplied `UniverseSpec`; it grants no
historical fitting, source certification, portfolio replay or confirmation access.
The frozen scientific D9 order remains AAPL/JPM/JNJ/WMT/CAT. The proposed engineering
source profile AAPL/COST/CMCSA/SBUX/CME remains opt-in and scientifically inactive.

`fullpeer.operator_input(row, preparation, history, permission,
architecture="FULLPEER" | "SP3")` reuses `market_input` and P2 normalization,
calendar, own-step publication and floor/scaler checks. No labels or future exit
arguments enter this forecast-input path. Complete boolean stock masks, 48 full
scheduled hours, precise ordered identities and synthetic source policies are
mandatory. D7 retains its frozen valid-endpoint/46-of-48 rule, neutral historical
zeros and separate masks. All five stock histories must be complete.

`fullpeer_values(prefix)` constructs `[own16, D7_5, peer16, peer16, peer16,
peer16]` in target-excluding canonical order. The result is five ×48×85, with the
original 21-channel prefix unchanged. `FullPeerView` wraps a `MarketNeuralView`;
it retains only existing table/index references. `make_fullpeer_view` builds that
view through the existing P2 adapter. `operator_batch(market_view, positions,
architecture=...)` lets MC0/full-peer/SP3 share one actual canonical stock and
market table, origin masks and mature target population. Peer copies exist only
in current minibatch memory. No extra OHLCV or per-model window store is written.

The common factory `create_model("FULLPEER")` returns `SharedLSTM(85)` with
15,265 parameters. `create_model("SP3", universe=...)` requires an explicit
synthetic ordered-five identity. `SpatialLSTM` uses the exact `SharedLSTM(21)`
encoder, then `StockMixer` across each origin's five-stock axis. Its formula is
`H + M2 @ GELU(M1 @ LN(H))`, K=2, LN32 epsilon1e-5/non-affine, bias-free matrices.
M1 uses seeded PyTorch standard Linear-style Kaiming-uniform initialization
(a=sqrt(5), bound1/sqrt(5)); M2 is exactly zero. This is a disclosed standard
initializer within D9, with no initializer/seed search. The shared readout
applies the existing final-hidden dropout0.10 after the mixer. Count7073+20=7093.
No gate, attention, ticker embedding, mixer dropout or auxiliary loss is added.

`SharedLSTM.encode` exposes the existing zero-state encoder without changing its
stockwise forward computation. Common session loss, whole-session sampler,
AdamW groups and global clip remain the existing implementations. SP3 groups
origins independently; flattening is solely encoder computation. Raw tensor
methods cannot authenticate ticker metadata. Use `BoundOperator` with the typed
`OperatorInput`/`OperatorBatch` for source/order/architecture-checked scoring.
These methods return computational tensors and do not issue authoritative P3
forecasts. Both new families are rejected by existing `run_pair` and refit
checkpoint APIs. No synthetic or genuine pair is reserved by this package.

`operator_artifacts.save_operator/load_operator` use an isolated immutable
`ENGINEERING_UNTRAINED_OR_OPERATOR_TEST` stage, safe CPU tensor reload, SHA,
code, architecture, source/action, ordered universe, target and preprocessing
bindings. They have `prediction_authoritative=false`, no optimizer or fitted
epoch. They cannot be promoted by renaming to REFIT_FINAL. Source, floor/scaler,
axis or code replacement requires fresh views/bindings/artifacts; existing E5
checkpoint metadata is never rewritten. The narrow common-code additions also
change the existing lifecycle code identity, so old lifecycle artifacts may be
stale for current runtime even though their preserved numerical evidence is valid.

At zero M2, SP3 equals matched-core MC0 in the same tensor layout. M1 gradient
can be zero initially, while suitable loss gives M2 a gradient. After nonzero
M2, gradients reach M1 and a different stock. Fixed-parameter input-only
permutation is not invariant. The correct identity is H'=PH, M1'=M1P^T,
M2'=PM2, transformed H'=P transformed H. Different encoder batch sizes can
produce float32 rounding; same-layout identity and source isolation are tested
exactly, while separate batch layouts use the existing1e-7 absolute tolerance.

The preregistered no-update hidden law uses sender1/recipient0, M1[0,1]=0.7,
M2[0,0]=0.4 and a coordinate0 shared head: message0,0 is
`0.4 * GELU(0.7 * LN(H)[1,0])`. Independent population-variance/erf scalar
arithmetic, central finite differences and stockwise negative controls verify
routing. These are untrained operator proofs, not TG0 learnability, alpha,
Rank IC, significance, economic causality or a historical comparison.

Reproduce with the README's existing neural extra, no credentials/data:

```sh
.venv/bin/python -B -m lstm_data.fullpeer_sp3_audit --out reports/data_audit/<NEW-P4-11>
.venv/bin/python -B -m pytest -q tests/test_fullpeer_sp3.py
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist
.venv/bin/ruff check .
.venv/bin/python -B -m pytest -q
```

The audit refuses overwrite and SCIENTIFIC_REAL before outputs. Its tiny
untrained artifacts, hand oracles and one-origin trace remain separate from the
scientific ledger. P4.10/P4.12/P4.13, SP1, MC2 and LL1-neural stay unauthorized.
Full-peer and SP3 have the same five-name source information but differ in raw
sequence versus final-hidden access and capacity15265/7093. E5 summaries are
weaker peer information. Historical comparisons are NOT_MEASURED. D13-C06's
four-family versus three-family limit remains unresolved. Future empirical
work needs independent source/action/publication/formation/certificate/gate
approval, real pair budget and family-scope decisions, then a separate executor
and reviewed model lifecycle integration. No automatic next experiment follows.
