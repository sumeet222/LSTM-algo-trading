# Reproduce and recover

Use repository-root paths and existing .venv. No dependencies, secrets or data
subscriptions were added. Local permitted raw48-month partitions, original V1
feature cache, action/OGN sources and archived controls must be supplied according
to their existing manifests/source rights. Proprietary raw payloads are not copied.
All original files remain read-only. Registry/cache paths and code hashes are
in FINAL_DIAGNOSTIC_REGISTRY.json; INPUTS_BEFORE.json freezes immediate references.

Executed commands, in order:

    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag.cli freeze
    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag.cli validate
    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag.cli pilot
    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag.cli run --run-id final-diag-20261110-r1
    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag_analysis
    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag_supplement
    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag_handoff

Only the first run is executed. Commands refuse overwrite. Already complete
funded results must be hash-verified, not rerun after a transport failure. The
analysis/recovery modules are separate from the sealed online code. Later edits
to those files were lint/type-boundary refinements, without altered numeric outputs.
A future code-matching independent reproduction needs a distinct run ID; it is not
permission to optimize the policy. Freeze is only for a new owned namespace, never
an overwrite of this registry. Tables are CSV/Parquet, docs Markdown.

Recovery: inspect active process/lock and RUN_RECEIPT.json first. The current
frontier is COMPLETE2024-12-31,1005 sessions,13 accounts. Do not resume this completed
run. An actually interrupted compatible run may use --resume <same-run>/states/
<last-committed-session>.json.gz; the binding includes registry, cache, period,
ordered account keys. Content hashes, full-state restore and no duplicate events
are checked. A source-backed stop-after-two-session pilot proves exact restart.
If any identity differs, preserve the old outputs and HOLD rather than mix state.
Four immutable year-end checkpoints are retained, not per-session journals.

Analysis_01 contains cohort attribution/tails, all potential versus filled-key
joins, source-only449-portion/1347-reference future diagnostic and explicit
unfilled-key limitations. Supplement_01 recovers exactly three OGN physical rows
and checks order-cost/notional counts and all grouped R01 stress inequalities.
Small root CSVs mirror canonical summaries; no model or raw-price copy exists.

Read VALIDATION_AND_INTEGRITY.md for78 tests, scoped0-error checks and the full
repository32-error legacy qualification. Full command stdout/stderr and codes
are retained in final_validation. No commits or pushes. The inherited untracked
research tree must be protected before any future Git integration.
