# Source-read and provenance call graph

Status: **STOP_AWAITING_HUMAN_DECISION**. All code references below are to frozen **new Phase2** text under `replication/phase2/`; nothing was imported or executed.

## Source preparation

| Stage | Call edge and location | Established from text | What runtime evidence does not establish |
|---|---|---|---|
| Entry/registration | `contract.py:5–11`, `inspect_inputs.py:4–10`, `prepare.py:5–15` import `boundary`, call `install()`, then import readers | Registration precedes reads on these frozen paths | Actual earlier source version, exact argv and registration timestamp |
| New build selection | `prepare.py:25` selects `dataset.build()` unless `--load-fresh-geometry` | Explicit fresh/reuse branches | Exact flags for every process |
| Validation | `boundary.py:88–91` validates month/family and returns a constructed literal path |2010-07–2024-12; family table includes hourly/canonical and optional raw | Validation is not a read; optional raw is not one of348 admitted/observed sources |
| Direct recording | `boundary.py:92` increments `_events[("admitted_data_request",str(path))]` | Recorder dictionary insertion, **not `sys.audit`**; occurs before return/native reader | Whether this exact insertion executed during source preparation |
| Contract reader | `contract.py:51–55`: `data_path` → `pq.ParquetFile(path)` → metadata/hash → `pf.read()` | Same local path used for reader and hash in frozen source | Opens lack stacks/modes; hash opens cannot be separated from native I/O |
| Schema reader | `inspect_inputs.py:14–17`: `data_path` → `pq.read_table` → schema/rows/sample | Two July source readers in current source | No custom/native event attestation in inspection receipt |
| Geometry reader | `dataset.py:48–68`: two `pq.read_table(data_path(...))` calls per month | Hourly field filters; genuine/RTH canonical endpoints; no other source reader on this path | Runtime file consumption and per-read file hash were not captured |
| Geometry generation | `dataset.py:69–107` derives source gates/labels/auxiliaries, writes origins/grid/NPZ/source counts | Explicit dataflow from the source arrays to fresh artifacts | Output path opens omit operation modes; full numeric derivation not replayed |
| Feature/preflight | `prepare.py:37–68`: components → recipe/transform → tensor checks → receipt | Geometry-to-feature connection, no old input path in this entry | Source code and synthetic tests are not universal real-data lineage proof |

Conceptual flow:

```text
prepare → dataset.build → boundary.data_path
                         ├─ validate literal month/family
                         ├─ direct _events insertion [expected, absent from receipts]
                         └─ return Path → PyArrow native reader → arrays
                                                       ↓
                    saved grid/origins/source_geometry → components/recipes
```

## Recording and collection are separate layers

1. `boundary.py:24` creates a module-local dictionary. `install():75–85` uses an idempotent flag, changes working directory, modifies `sys.path`, installs the original-package blocker, registers `_audit` and an `atexit` receipt callback. `sys.dont_write_bytecode=True` prevents new bytecode writes; it does not establish that earlier bytecode or cached module instances were never loaded.
2. `_audit():43–57` intercepts only built-in `open`, `os.listdir`, `os.scandir`. It rejects non-path arguments; stringifies paths via `absolute()`; records project paths if permitted, or records a denied key and raises. It has no native-C-library syscall coverage guarantee. Path spelling checks are procedural, not an OS sandbox or a complete symlink/canonical-path security proof.
3. `data_path():92` writes directly to the same global dictionary and bypasses `_audit`. Thus the built-in event filter would ignore an arbitrary `sys.audit` event **if one were used**, but no such emission exists here. Filtering is refuted as the explanation for this frozen direct-insertion path.
4. Repeated identical `(event,path)` pairs increment an integer. Different event strings cannot collapse into `open`. `_events` is initialized once in the inspected module; no clearing/reassignment, rename or alternate emitter appears in the inspected callers. No stored event timestamp, mode or stack exists.
5. `receipt():60–72` snapshots module origins and every sorted dictionary entry into JSON, then writes the PID file. It does not filter custom keys. The write opening its own receipt occurs after the snapshot and will not appear until a later receipt call; that ordering cannot erase an earlier data-request key. Disk output is deferred to the receipt call; there is no separate custom-event flush buffer.
6. Normal `atexit` handles successful exits and ordinary exception unwinding. The interrupted contract has a valid receipt. Missing hard-kill receipts remain a general possibility, not an observed explanation for zero custom events in all existing successful and failed receipts. Current source registers before readers. Even a late built-in hook alone would not suppress direct dictionary insertion if that function version executed and the same dictionary was later serialized.
7. `postrun_check.py:121–125` explicitly calls `boundary.receipt()` before import aggregation; the later freeze path at143–148 writes one last receipt then unregisters the callback. That detach applies to the **freeze process only**. It does not establish or remove earlier preparation events.
8. `postrun_check.py:64–87` reads all existing provenance files; its admitted-path aggregation accepts every event type and deduplicates paths. Module hashes are computed at collection time, not earlier import time. It never verifies custom request count/type. Its prose claim is stronger than this check.

## Saved geometry consumers

`dataset.load_fresh_geometry():115–122` reads exactly `grid.parquet`, `origins.parquet` and `source_geometry.npz`. `prepare.py:25` can take this branch; `run_experiment.py:65` and `audit/report_recovery.py:41` use it. They do not call `data_path()` for inherited sources. Their saved artifact opens are positive procedural evidence; they cannot prove the upstream native reads. Recovery's three opens per geometry object include before/after protection hashing, so count3 must not be described as three reader calls.

## Earliest established break and remaining alternatives

The missing link is the expected direct request insertion/persistence during **source preparation**. Frozen text plus output footprints predicts it, but source-version-at-use and function-instance-at-use are not recorded. Single `boundary` aliases in exit snapshots weaken but do not eliminate multiple-instance/reload explanations. Preparation-time source snapshots, per-import digests, syscall traces, event timestamps, argv and stacks are unavailable in this allowed evidence. Current mtime ordering is compatible with late instrumentation; it is not proof.

No code change or retrospective event manufacture is authorized. No unsealing follows from this graph.

## Process reconstruction and limits

The JSON records every one of39 PIDs. **No receipt records argv, process start/end timestamps, hook-registration time, event timestamps, read/write mode or stack.** Mtime is reported separately and is not treated as start/end time. Most receipts lack `__main__`; source-preparation identities below are footprint-based inferences, not exact process-command proofs. Reproduction commands in Phase2 documentation are not retrospectively assigned as observed argv.

Key preparation sequence:

- PID48847: `initial_schema.json` open, matching schema-output metadata; inferred inspection. Current call site would request two source paths, but no market or custom event was saved.
- PID48886: two July source opens; contract failure log shows July RTH assertion failure. Exact command/start unknown; receipt/log mtimes are adjacent, which supports but does not authenticate attribution.
- PID48927: twelve source opens covering the early contract attempt; second log reports five completed witness months before KeyboardInterrupt during subsequent date rendering. A receipt exists despite interruption; it does not identify a native read versus hash open.
- PID48988: plausible profiling candidate from adjacent profile-log metadata, not proven. Other early diagnostic PIDs cannot be assigned to source reading solely from public-library imports; their event summaries remain explicit in JSON.
- PID49097:348 approved source opens and all four contract-output path events. Completed log has174 progress months and final totals/2,272 assertions. Contract code hashes each source once, so these348 opens need not be native-reader evidence.
- PID49485: fresh-builder/preflight001 footprint, opening the contract receipt and source-count/geometry output paths. The log reaches the later M2 assembly error after geometry creation. No source-request or market-open record covers the native reads that frozen source predicts.
- PIDs49569/49887: later preflight footprints with geometry opens, no source-count/contract-receipt event, and successful preflight logs. This supports the documented `--load-fresh-geometry` path; exact flags are not recorded. It cannot backfill source-build provenance.
- PID49976:182 training-ledger opens and one open of each geometry object. PID52103:8 recovery-ledger opens and three geometry opens each, including protection hashes. Both use `load_fresh_geometry()` according to frozen code. Their lack of `data_path` calls is expected and does not explain the preparation gap.
- PID52700:348 source hash opens in postrun integrity; these explain observed-path coverage without confirming earlier native consumption. PID52884 is the separately recorded freeze process; explicit `__main__` points to the freeze utility. Its receipt is later than the38-PID import lock.

Full receipt coverage (UTC mtimes are observations only):

| PID | Receipt mtime observed | Approved source open records | Role assessment |
|---|---|---:|---|
| 48847 | 2026-11-02T23:24:05.102564+00:00 | 0 | Schema inspection footprint; inferred, no argv in receipt |
| 48886 | 2026-11-02T23:26:31.393174+00:00 | 2 | Contract first failed attempt; inferred from July opens and matching log metadata |
| 48927 | 2026-11-02T23:30:47.603432+00:00 | 12 | Contract interrupted second attempt; inferred from12 source opens and log metadata |
| 48962 | 2026-11-02T23:28:41.168797+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 48970 | 2026-11-02T23:28:46.991911+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 48988 | 2026-11-02T23:29:08.392016+00:00 | 0 | Profiling candidate; inferred only from log metadata proximity, not proven |
| 49009 | 2026-11-02T23:29:26.557090+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49018 | 2026-11-02T23:30:02.160923+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49084 | 2026-11-02T23:30:22.090334+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49097 | 2026-11-02T23:34:38.953891+00:00 | 348 | Completed contract footprint:348 source opens and contract-output events |
| 49159 | 2026-11-02T23:30:59.270732+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49168 | 2026-11-02T23:31:18.551115+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49189 | 2026-11-02T23:31:56.120401+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49242 | 2026-11-02T23:32:49.988619+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49467 | 2026-11-02T23:35:03.331097+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49477 | 2026-11-02T23:34:57.254986+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49485 | 2026-11-02T23:35:37.870004+00:00 | 0 | Fresh geometry builder/preflight001 footprint:contract receipt, source_counts and geometry outputs |
| 49547 | 2026-11-02T23:36:09.820457+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49569 | 2026-11-02T23:37:03.155555+00:00 | 0 | Preflight002 saved-geometry load footprint; source_counts/contract read absent |
| 49669 | 2026-11-02T23:37:11.217649+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49737 | 2026-11-02T23:37:31.506948+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49748 | 2026-11-02T23:38:14.784516+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49789 | 2026-11-02T23:38:25.542177+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49811 | 2026-11-02T23:39:07.170236+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49835 | 2026-11-02T23:39:33.701375+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49863 | 2026-11-02T23:40:15.698292+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49887 | 2026-11-02T23:40:52.554504+00:00 | 0 | Preflight003 saved-geometry load footprint; source_counts/contract read absent |
| 49967 | 2026-11-02T23:41:27.718209+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 49976 | 2026-11-03T00:40:02.882812+00:00 | 0 | Training footprint:182 ledger opens and one geometry open each |
| 50382 | 2026-11-02T23:49:38.176659+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 51977 | 2026-11-03T00:42:59.232373+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 52019 | 2026-11-03T00:43:48.687451+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 52038 | 2026-11-03T00:44:06.002709+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 52039 | 2026-11-03T00:44:13.723055+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 52086 | 2026-11-03T00:45:09.798593+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 52103 | 2026-11-03T00:53:49.102816+00:00 | 0 | Report recovery footprint:8 recovery ledger opens;geometry opens include protection hashing |
| 52632 | 2026-11-03T00:52:56.895848+00:00 | 0 | Not a positively identified source-preparation run; role unknown from bounded evidence |
| 52700 | 2026-11-03T00:54:02.110324+00:00 | 348 | Postrun integrity hashing footprint |
| 52884 | 2026-11-03T00:59:03.001832+00:00 | 0 | Freeze process, explicit __main__ postrun_check.py |

No alternate native event name exists in the39 receipts. All observed boundary module paths use the single name `boundary`; this does not exclude transient aliases, module reloads or earlier versions before exit. Exact preparation commands/start/end/registration and a complete native-read chain remain unavailable. These limitations are retained rather than replaced by invented timing or stack evidence.
