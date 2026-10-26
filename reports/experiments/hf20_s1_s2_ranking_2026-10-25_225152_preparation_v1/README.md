# HF20 S1 + S2 — preparation only

**Ledger62/200; no real fits or new neural starts.** Stage0 QUALIFIED, Stage1 PASS, Stages2–5 NOT_RUN. No predictive results exist because no models were fitted.

Start with [live approval card](LIVE_FIT_FREEZE_AND_APPROVAL_CARD_PROPOSED.md), [preflight/design reconciliation](PREFLIGHT_AND_DESIGN_RECONCILIATION.md), [rehearsal/readiness](REHEARSAL_AND_READINESS.md) and [session report](WORK_SESSION_REPORT.md).

All current analysis/evidence files:

| Files | Purpose |
|---|---|
| [proposal](proposal.json), [source references](preflight_source_refs.json), [preservation](preservation_manifest.json) | Exact proposed science/code/source bindings; original checkpoint/source bytes |
| [folds](folds.json), F21..F24_{inner_train,inner_validation,refit,oos}_indices.csv | All16 exact populations, embargo/maturity/exclusion counts |
| [rank identity](preflight_numerics.json), [source reconstruction](independent_source_preflight.json) | Historical endpoint/rank oracles and XNYS checks; no fitting |
| [sampler equivalence](bounded_archive_adapter_equivalence.json) | Four bounded real inputs bit-exact to P020 |
| [source quality](source_quality_by_fold_role.csv), [IC feasibility](defined_ic_source_feasibility.csv) | Availability/proxy audit only; no model IC |
| [22 source cases](shared_source_case_keys.csv), [genuine-case checks](source_case_preflight.json) | Shared original-source witnesses and endpoint reconstructions |
| [tests](tests.txt), [static](static_check.json), [Ruff](ruff.txt), [CLI](cli_help.txt), [denial](missing_approval_rejection.txt) | Rehearsal/guard receipts |
| [verification](verification_receipt.json), [submitted brief](submitted_instruction.txt) | Final preparation checks and exact task |

After approval, model/fold directories will contain four-role keyed `*_scores.parquet`, `*_metrics.json`, `*_cohorts.csv`, `*_thresholds.json`, `*_stock_quality.csv`, `*_origins.csv`, month/slot tables and neural `source_cases.csv`. Cohorts contain detailed original-target extremes/complements, true-objective losses and numerator/MAD partitions. Pair arms also have `*_pair_types.csv`. Neural folders retain complete calibration/refit batch/epoch/checkpoint/selection receipts and PASS hashes. These files are NOT_RUN now.

Collective closeout will write `four_fold_models.csv`, `equal_year_summary.csv`, `paired_calendar_sensitivity.json`, `independent_output_reconciliation.csv`, `annual_rank_ic.html`, `FINAL_RESEARCH_DECISION.md`, and `completed_reports_v1/{README,S1_FOUR_FOLD_RANKING_BASELINES,S2_FOUR_FOLD_LSTM_RANKING_COMPARISON,RANKING_EXTREMES_AND_OBJECTIVE_DIAGNOSTICS,TRAINING_AND_SELECTION_TRACE,WORK_SESSION_REPORT}.md`. After results, the agent completes the substantive researcher diagnosis and full file index. No empty placeholder is represented as a completed scientific report.

Use the documented repository .venv and existing local source caches. Run exact focused checks in readiness. Do not regenerate --prepare into this populated namespace. After actual live approval, record the exact response, proposal/execution hashes, baseline_fits64 and listed neural runs (empty for S1-only) in a new authority JSON. The NOT_AUTHORITY template explicitly has approved=false and is rejected. An approved invocation from repository root is:

```bash
OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 VECLIB_MAXIMUM_THREADS=4 .venv/bin/python -m lstm_data.hf20_ranking_run --run --out reports/experiments/hf20_s1_s2_ranking_2026-10-25_225152_preparation_v1 --approval PATH_TO_ACTUAL_LIVE_APPROVAL.json
```

No source, old result or journal changed during preparation. No commit/push performed. All current new files remain uncommitted.
