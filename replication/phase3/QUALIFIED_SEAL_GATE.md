# Qualified seal gate — STOP

UTC: 2026-11-03T12:37:23.826421+00:00. **Original unsealing is not authorized.**

The single `.DS_Store` exception does not resolve an additional, independently confirmed provenance gap. The external manifest anchor matches. All other 232 payload files and all 348 admitted pre-2025 source identities match, with no extra or missing Phase2 files. The original failed gate and witness hashes remain unchanged. Metadata dependency evidence is in `METADATA_EXCEPTION_AUDIT.md`; the full 233-file freeze is not described as unchanged.

## Blocking evidence

The bound `audit/IMPORT_LOCK.json` claims: “Explicit admitted-data requests cover native-reader entry points.” The frozen `code/boundary.py` implements such recording in `data_path()`. Source-reading call sites in `contract.py`, `dataset.py` and `inspect_inputs.py` invoke this function.

However, all **39** frozen provenance receipts contain **zero `admitted_data_request` event entries**. Their aggregate distinct event/path entries are 30,241 `open`, 3,766 `os.listdir`, 27 `os.scandir`, and two intentionally denied probe opens. Repository-market path entries total 710 opens: PID48886 has2, PID48927 has12, PID49097 has348, PID52700 has348. These counts are entries, not sums of each entry's `count` field.

The 348 source paths in `IMPORT_LOCK` do not establish the missing reader-call coverage. `postrun_check.py` collects any allowed-path event, including the file opens performed by its own source hashing. Contract hashing also opens those files. No separate native-reader event evidence was found.

Training PID49976 and recovery PID52103 do contain positive procedural evidence for expected Phase2 geometry reads: `grid.parquet`, `origins.parquet`, and `source_geometry.npz`, alongside their distinct ledger footprints and Phase2 module origins. Their frozen call sites use `load_fresh_geometry()`, which does not invoke `data_path()`. That explains the absence of explicit source-request events during training/recovery; it does **not** explain their absence throughout source preparation. The native source-consumption claim remains uncorroborated.

This finding is an **evidence gap and unsupported runtime coverage claim**. It does not prove protected access, an original-helper import, source mutation or a scientific numerical error. The recorded module origins and observed market paths contain no such forbidden event. Nor does source text alone prove every earlier runtime used precisely that source. The known procedural, non-OS isolation limitation remains.

The accountable reviewer independently reproduced the fresh spot reviewer's zero-event finding. An initial spot-review count used an overly broad `/data/` substring and included library paths; the corrected repository-market count above was verified independently and is the operative evidence. No original result was opened during this investigation.

## Other checks completed

Fresh verification established the 18-file prefit code lock with its sole explicitly documented evaluation mask-copy transition; unchanged eight prefit evidence hashes; exact snapshot/new-source/diff bindings; eight ordered neural phases; trace/completion/refit-duration consistency; fresh optimizer-state receipts; one reporting failure after all four folds; 80 unchanged protected artifacts; five byte-identical replay tables; and eight recorded reload checks bound to the four current checkpoint hashes. No reload forward was performed in this review. All 348 inputs match the three source inventories and exactly174 months per family (2010-07–2024-12). These checks cannot cure the provenance gap.

`STAGE_A_EXCEPTION_CHECKS.json` is a structural/hash check receipt, not an unseal decision. The gate in this document and `QUALIFIED_SEAL_GATE.json` is controlling: **STOP**. D07 arithmetic recomputation, complete D08 adjudication, historical C0–C6 comparison and independent metric arithmetic were not performed after the stop condition. No replication-success or parity conclusion is available.

Only additive Phase3 files were created. No fits, recalibration, threshold fitting, new neural forwards, legacy helper execution, network, installations, Git mutations, fetch, prior-file repair or manifest regeneration occurred. Root's administrative check reports branch `feat/track-a-data-intake`, HEAD `8061483cb65d03264a7836b8b882123f67cbe4ad`, clean tracked/cached diffs and only `?? replication/`. The task-specific gate/blocker-only and Phase3-write rules supersede normal session-report placement and project-wide static checks. No new Python file was introduced; tests/static checks were not run.

Preserve all evidence. Continuing requires explicit human adjudication of this separate provenance gap; the metadata exception alone does not authorize it. `QUALIFIED_GATE_WITNESS.md` binds this decision before any original access (none occurred).
