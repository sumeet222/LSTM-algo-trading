# Package012A: read-only FT0 normalization audit

The active packet is
`reports/data_audit/ta012a_ft0_normalization_2026-10-15_230238_v2/`.
The dashboard binds `display_manifest_final.json`, including the resolved example
consumer metadata and symbol-qualified verified tail identities. Earlier files
and the preliminary packet are preserved; they are not the active display binding.

Start with `normalization_hypotheses_ranked.md`, then
`interpretation_addendum.md`, `feature_registry_and_equations.md` and
`human_review_card.md` in that directory. Exact recipes, population hashes,
native/scaled distributions, stock/temporal differences, floor activation,
clipping collisions and independent oracles are accompanying compact tables.
The synthetic nonzero-constant fallback edge is disclosed separately; no active
recipe uses that branch, and historical feature math was not repaired here.

Run from the repository root in the documented environment:

```bash
./scripts/run_track_a_dashboard.sh
./scripts/run_track_a_dashboard.sh --check
./scripts/run_track_a_dashboard.sh --smoke
```

Use **Start Here → Package012A normalization audit**. Select audit fold, channel,
population and stock/pooled. Native/scaled histogram units remain distinct; the
stock table and monthly/quarterly drift use all canonical unique observations.
Choose **WF2 / B1 / Development / CMCSA**, then **Open normalization example**.
It opens genuine candles/volume for January25,2024 with the exact WF2/refit
recipe. Enable the actual48-step context checkbox to see its registered consuming
forecast inputs. The older live Feature Scaling Explorer remains available for
bounded time traces. See the packet's `visualization_walkthrough.md` for five minutes
of examples. Full data remains chart-only and confirmation remains locked.

Reproduce the complete numerical audit into a **new**, never-existing directory:

```bash
.venv/bin/python -m lstm_data.normalization_audit --out reports/data_audit/ta012a_ft0_normalization_local_recheck_01
```

Choose another new suffix for each run. This CLI does not repoint the dashboard,
fit an estimator/scaler, request a provider, write a checkpoint or reserve a pair.
It reuses the exact locally provisioned, legitimate preconfirmation sources and
saved recipes; follow `data/README.md` for their existing provisioning route.
No new dependency or credential is required. The current numerical pass took
267.34 seconds,258.996 CPU seconds and719,044,608 peak RSS bytes on the local
arm64 machine; machine/runtime details are in `resource_usage.json`.

Focused checks:

```bash
.venv/bin/python -m pytest tests/test_normalization_audit.py tests/test_target_range_history.py tests/test_controlled_visualization.py tests/test_visualization_readonly.py tests/test_controlled_review.py -q
.venv/bin/ruff check .
```

Use `scripts/check_python_types.py` with the locally installed Pylance `dist` path
and repository interpreter, retaining basic severity/stub parity. Source, model,
recipe, protocol and ledger preservation are recorded. The ledger stays24/40;
012B variants, any native-floor change, the fallback repair and confirmation
inspection require their own future scope. No alpha or production readiness claim.
