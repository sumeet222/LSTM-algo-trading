# Source-request provenance findings

Status: **STOP_AWAITING_HUMAN_DECISION**. Classification: **B — cause unresolved, with bounded positive lineage support**. Investigation completed 2026-11-03T13:25:21.724271+00:00. This is a focused source-provenance review, not an unseal or historical-comparison authorization.

## Timeline and scope

1. Initial Phase3 Stage A stopped because `.DS_Store` differed from the frozen manifest. The failed `../SEAL_GATE.json`, `.md` and `../BLOCKER.md` remain preserved.
2. The user authorized a single metadata-file exception. Continuation verified the other232 payload files, all348 source identities,80 protected artifacts and5 replay tables, but stopped on the missing explicit request events. That decision remains in `../QUALIFIED_SEAL_GATE.json` and its witness.
3. This investigation was authorized solely to explain that provenance gap. No original result, source market file, geometry array, checkpoint, score, calibration or model was opened or executed. Existing Phase2/Phase3 evidence was not edited. No unsealing is authorized regardless of this classification.

## Main finding

The current frozen recorder **does implement** the custom event. `code/boundary.py:88–93` validates the family/month, constructs the path and directly increments `_events[("admitted_data_request", str(path))]`. It does not use `sys.audit`. The built-in hook's allowlist at lines43–57 therefore cannot filter this direct insertion. `receipt()` at lines60–72 serializes every dictionary key without an event-name filter.

Yet all39 frozen receipts lack the key. The earliest established break is **between execution expected at the frozen `data_path()` insertion and the persisted receipt population**. We cannot establish that this final function body executed during preparation; an on-disk path/hash recorded later is not a preparation-time function-body or module-instance attestation. We found no concrete filtering or serialization defect that explains the missing direct insertions. No benign root cause is asserted.

`audit/postrun_check.py:81–87` has a separate, concrete coverage-validation weakness: it accepts any allowed-path event, including hash opens, then asserts in prose that explicit native-reader requests cover entry points. It never requires the `admitted_data_request` event type. That explains why an overstated coverage claim could pass aggregation; it does **not** explain why the underlying custom events were absent.

A late instrumentation change is compatible with the evidence: current `boundary.py` mtime is2026-11-02T23:41:02.070674Z, later than contract completion metadata23:34:38 and the geometry/preflight receipts23:35–23:40. The prefit acceptance timestamp is23:41:27.714932Z. These are **metadata observations, not causality**. No saved earlier boundary source, preparation-time source hash, argv or insertion-specific timestamp establishes when line92 was added or which version executed. The investigation did not inspect or execute bytecode.

## Exact counts

Each event record is a distinct saved event/path key in one PID receipt. Count sums add the stored `count`; neither is a native-syscall count.

| Event | Records | Sum of count |
|---|---:|---:|
| open | 30,241 | 30,966 |
| os.listdir | 3,766 | 3,774 |
| os.scandir | 27 | 53 |
| DENIED:open | 2 | 2 |
| admitted_data_request | 0 | 0 |

Exact348-path membership, restricted to the approved hourly/canonical families, gives710 market-source open records and710 count sum: PID48886=2,48927=12,49097=348,52700=348. No generic `/data/` substring was used. Phase2 artifact events are275 open records/879 count sum and17 scandir records/34 count sum. The two denied probes were blocked boundary tests, not successful forbidden file reads. No protected target was probed here.

The administrative root independently recounted the39 receipts using standard-library JSON/Counter and confirmed all global record/count sums. Detailed per-PID counters, module aliases, pertinent artifact events and exact current evidence hashes are in `PROVENANCE_EVENT_COUNTS.json`.

## What positively supports lineage

This assessment does not rest on manifests or import-lock assertions alone:

- Saved input-manifest row totals independently sum to509,140 hourly rows and33,296,542 canonical rows, matching the contract receipt. Schema evidence identifies the expected fields and revision conventions.
- The saved contract contains2,272 expected/actual field comparisons across284 stock-hours. A new standard-library arithmetic check of these saved pairs reproduces all2,272 pass results under the documented1e-12 absolute/relative rule, including paired NaNs. This supports the bounded canonical-to-hourly interpretation. It is **not** a new read of canonical data or an independent authentication of the recorded values.
- `source_counts.json` contains exactly174 matching monthly keys,436,140 full-hour rows after stub exclusion, and1,298,303 endpoint-reference rows. These are structural/content observations beyond a bare PASS assertion. They are consistent with `dataset.build()`'s source filters and endpoint extraction, but do not alone prove which file supplied every value.
- PID49485 records the contract-receipt open plus source-count/geometry/role output paths. Its matching preflight failure log reaches geometry and component construction before the M2 indexing failure. This is positive builder-footprint evidence; the event schema omits read/write flags and stacks, so operation direction is inferred from code and log context.
- All20 saved geometry-role expected/actual tuples match. `audit/independent_data_review.md` documents a separate code review and ten synthetic frontier/assembly/perturbation tests, including detection of the M2 indexing defect. This independently supports the transformation mechanism; the reviewer explicitly did not audit actual inherited minute data.
- Later preflight, training and recovery receipts open the same named Phase2 geometry objects. Prior qualified StageA verification bound their bytes and protected outputs. Frozen `prepare.py`, `run_experiment.py` and `dataset.load_fresh_geometry()` supply a coherent source-to-geometry-to-feature call structure. This investigation neither reloaded those arrays nor reran feature construction.

Together these give **bounded positive lineage support**, sufficient for classificationB rather than declaring the source lineage wholly unknown. They do not provide universal native-reader attestation or exclude an unrecorded access. The absent contemporaneous request/version evidence remains material to confidence and requires human adjudication. No classA concrete omission cause has been established; no classD actual boundary violation was observed.


The full process reconstruction, all39 PIDs, timing/command gaps and source citations are in `SOURCE_READ_CALL_GRAPH.md` and `PROVENANCE_EVENT_COUNTS.json`.
