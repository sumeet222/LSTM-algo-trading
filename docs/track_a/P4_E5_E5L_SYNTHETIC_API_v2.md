# Corrective P4.8/P4.9 synthetic API v2

This additive document supersedes v1's ridge-layout refusal only. E5 remains
`P4.8_PARTIAL / E5_HEALTH_BLOCKED`; full E5 D6g calibration/refit, final
checkpoint and P3 forecast are NOT_RUN. Preserve the old failed proof and v1
report. The unchanged 60-update proof failed both inequalities; independent
diagnosis performs zero optimizer steps, rather than modifying its fixture or
acceptance rule. All scientific gates remain HOLD, real pairs 0/40, and upstream
MC0/MC1/P4.6/P4.7 acceptance remains REVIEW_PENDING.

`e5_health_diagnosis.diagnose(proof_path, permission) -> dict` verifies the old
log/status SHAs, reconstructs exact RNG8049 inputs, checks independent peer
arithmetic and bitwise first21 conservation, and runs one initial forward/backward
without optimization. The old target is the current input's endpoint peer mean;
it has no mature proxy/TG0 references. An independently specified chronology/TG0
health fixture needs separate human approval before replacing this failed gate.

`directed_peers.directed_ridge_fit(data, stage, history, archive, pair, permission,
decision_path, allow_synthetic=False) -> MatchedFits` requires all bindings and
explicit synthetic opt-in. It delegates to `directed_ridge.fit_directed`, which
uses unchanged `baseline_fit.selection_fit`, frozen five lambdas,63-calendar-session
tail, maturity/purge checks, train-only preparation,50-session/25-per-origin
guards and one fresh full-prefix refit per arm. No observed-data route or generic
production model was enabled. Old public112/147 RidgeModel and147/161 peer fits
retain their original contracts. Code hash changes invalidate old fitted code
bindings; unchanged numerics do not authorize replay of stale checkpoints.

New D8 bulk provenance uses `SYN:D8_TYPED_JSON:1`, the existing typed JSON
serializer with ISO timestamps. Every dataclass field remains bound. This avoids
locale-heavy timestamp repr formatting found by a one-second profile; it changes
new D8 hashes without changing numerical data or protected legacy encodings.

`DirectedArchive` holds one immutable fabricated raw-M1 table with exact source,
action, unit, five-name/order and own-step publication identities. `MatchedDesign`
requires raw input M1 and lineage to agree with that table. The calendar's exact
49th full-hour predecessor feeds `directed_window`; missing sources/stubs and
unqualified clocks fail the whole origin. Its shared cache rejects input-content
conflicts and gives all three arms the same mask before lambda fitting.

`extension(window, sham, prep, context, arm, decision_sha) -> DirectedExtension`
appends peer14 + once-only flags2 to the original147 prefix. LL1/sham append
directed35; the canonical widths are163/198/198. `column_names()` gives all198
names and offsets. Every slope is penalized once; the single intercept is free.
See [the additive decision](decisions/D8_RIDGE_FLAGS_ONCE_v1_2026-10-13.md).

The sham changes only the35 directed columns to the same stock/slot exactly ten
preceding eligible XNYS sessions. Older raw publications stay at their original
timestamps. The existing fit transforms them at the corresponding **current**
input step under the explicit ASOF or HISTORICAL_TRAINING context. Trace binding
records original source time, transform application time and fit time; it does
not assert a transformed value existed before its fit. Missing shifted slots
exclude that origin from every arm. This is a weak engineering diagnostic, not
a permutation p-value or evidence of causal transmission.

`directed_ridge_fixture.fixture(FORWARD|REVERSE|NULL, optional_fictional_universe)`
generates independent bounded raw M1 first, then separate complete five-name
matured proxy references through existing TG0 math. Forward/reverse plant prior
H→L/L→H respectively; null has zero returns. No source Parquet, credentials,
confirmation results or real fitting is used. `run_case()` records actual five
candidate fits, one fresh refit per arm, held-out weighted TG0 MSE and full-prefix
coefficients. Its five-score examples are explicitly historical synthetic
illustrations, not final ASOF forecasts or P3 replay authority.

Reproduce compact evidence in a new path, once for each predeclared case:

```sh
.venv/bin/python -B -m lstm_data.directed_ridge_audit --case FORWARD --decision docs/track_a/decisions/D8_RIDGE_FLAGS_ONCE_v1_2026-10-13.json --output reports/data_audit/<NEW-directory>/ridge_forward.json
.venv/bin/python -B -m pytest -q tests/test_directed_ridge.py tests/test_directed_peers.py tests/test_e5_neural.py
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist
.venv/bin/ruff check .
.venv/bin/python -B -m pytest -q
```

No new dependencies. Do not start P4.10–P4.13, LL neural variants, scientific
fits, source migration or trading from this API. Human review remains required.
