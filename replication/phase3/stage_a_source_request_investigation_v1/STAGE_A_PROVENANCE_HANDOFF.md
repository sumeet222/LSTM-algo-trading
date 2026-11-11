# Stage A source-request investigation handoff

Completed UTC: 2026-11-03T13:27:07.471672+00:00.

**Classification B — cause unresolved with bounded positive lineage support. Status STOP_AWAITING_HUMAN_DECISION.** No unseal is authorized. The existing qualified STOP and metadata-only exception are preserved; this investigation does not supersede either.

## Result and decision boundary

The frozen code directly inserts `admitted_data_request` into `_events`; neither the built-in audit filter nor JSON serialization explains its absence. All39 provenance receipts have zero such events. The postrun collector accepts generic allowed-path events and thus permits its coverage claim without checking the missing event type. Actual preparation-time code/version/instance and native-read provenance remain unverified. Mtime ordering supports investigating late instrumentation, but does not prove it.

Bounded positive support includes stored canonical/hourly field comparisons, monthly source/extraction counts, role-geometry consistency, a builder footprint, an independent synthetic/code review, and later same-geometry consumer footprints. The saved evidence's arithmetic was checked; no real-data derivation was rerun. This is not a universal source-consumption, isolation or scientific-correctness proof.

A human must decide whether to accept this **separate unresolved source-request provenance limitation** or authorize another bounded evidence collection. Any subsequent exception and historical unseal need separate explicit authorization. Nothing here authorizes repair, retrospective receipt regeneration, code changes, preparation reruns, model work or unsealing.

## Exact five-file inventory

| File | Bytes | SHA256 |
|---|---:|---|
| `PROVENANCE_GAP_FINDINGS.md` | 6931 | `8421ea2794f2a99c28904bf2ccc204591f183f470da629cfb4870068adfdce6f` |
| `SOURCE_READ_CALL_GRAPH.md` | 15795 | `11d39a7f762b50c9757c883d5704b8e9e6b9233a3c7d5d90e13bb5d009667897` |
| `PROVENANCE_EVENT_COUNTS.json` | 78945 | `a3bf040dfe83a08cf823b03ad3aab82e41cc873d59c9288f7db916d6d3c0f875` |
| `HYPOTHESIS_AND_RISK_MATRIX.md` | 6736 | `5be44d7af20adccee8f1a5c7da31544539d5fd3d3da7565f21900452c12eeefc` |
| `STAGE_A_PROVENANCE_HANDOFF.md` | self-excluded | Hash returned externally after final write |

This handoff binds the other four files and excludes itself to avoid recursive hashing. No sixth manifest, saved script, log or auxiliary file was created. The initial `stage_a_source_request_investigation_v1` path did not exist; creation used `mkdir(exist_ok=False)`.

## Evidence identities and preservation

`PROVENANCE_EVENT_COUNTS.json` contains current SHA256/bytes/observed mtime for69 inspected Phase2 objects:39 frozen provenance receipts and30 specifically relevant source/audit/document files. Every one matched its frozen-manifest entry on initial inspection and was rehashed immediately before this handoff. The manifest itself matches retained external anchor `acee4b37613fc905ae2d1b3dd1624a8a19762bd3cdc42086fe6c474911f02410`.

All10 pre-existing Phase3 gate, witness and supporting evidence files were also rehashed against the investigation's captured identities immediately before handoff. They are unchanged. Their full identities are recorded in the JSON. The original three remain:

- `SEAL_GATE.json`: `b014bdd1f15ecf908375668dc04e7bb92d9e19315a6a3b9276b661ff8dffa7ff`.
- `SEAL_GATE.md`: `c8ab3a1a858533645d5371ab210e63b04b0d57f5f05190566581f4bfe91b3920`.
- `BLOCKER.md`: `b1206f45946355f27115d030a1c82b0872c49d13780d8764c09a618fbf7276bf`.

The previous qualified investigation's232/348/80/5 integrity results are **prior verified evidence**, not rerun claims. The348 market sources, geometry arrays, fitted artifacts and metric tables were not opened or rehashed here. The `.DS_Store` exception remains separate; its changing observed identities are retained in the earlier metadata audit, and this task did not read or alter it.

## Commands and verification

All shell commands ran from the project root using existing `.venv/bin/python -B` for standard-library analysis. No saved investigation Python file or pipeline import was used.

The following exact read-only recount command was executed successfully:

```sh
.venv/bin/python -B - <<'PY'
from pathlib import Path
from collections import Counter
import json
p=Path('replication/phase2');m=json.loads((p/'PHASE2_FROZEN_MANIFEST.json').read_text());a=json.loads((p/'audit/input_manifest.json').read_text());allowed={str(Path.cwd()/x['path']) for x in a};rows=Counter();calls=Counter();market=Counter();market_calls=Counter();n=0
for x in m['files']:
 if not x['path'].startswith('audit/provenance_'):continue
 n+=1
 for e in json.loads((p/x['path']).read_text())['file_events']:
  rows[e['event']]+=1;calls[e['event']]+=e['count']
  if e['path'] in allowed:market[e['event']]+=1;market_calls[e['event']]+=e['count']
print(json.dumps({'receipts':n,'event_records':dict(rows),'count_sums':dict(calls),'source_records':dict(market),'source_count_sums':dict(market_calls)},indent=2))
PY
```

It returned39 receipts; records/count sums: open30241/30966, listdir3766/3774, scandir27/53, DENIEDopen2/2; approved-source opens710/710; zero custom request events. The administrative root independently corroborated the global counts using a separate standard-library recount.

Representative exact source-read commands executed were:

```sh
nl -ba replication/phase2/code/boundary.py && nl -ba replication/phase2/code/inspect_inputs.py && nl -ba replication/phase2/code/prepare.py
nl -ba replication/phase2/code/dataset.py | head -125 && nl -ba replication/phase2/code/contract.py | head -65 && nl -ba replication/phase2/audit/postrun_check.py | head -95
cat replication/phase2/audit/contract_execution.log replication/phase2/audit/contract_execution_002.log
```

Additional inline standard-library commands read the exact evidence identities listed in JSON; collected per-PID counters, modules, artifact footprints and metadata; checked2,272 saved witness pairs with `abs(expected-actual) <= 1e-12 + 1e-12*abs(actual)` and paired-NaN equality; summed manifest/extraction rows; checked20 saved expected/actual role tuples; and rehashed the69 inspected files and10 prior Phase3 files. All these final checks passed. These are forensic arithmetic/identity checks, not fresh data-pipeline or scientific tests.

A diagnostic summary initially assumed every JSON root was a dictionary and stopped on the list-valued source-count file with `AttributeError`. A type-aware follow-up completed the read. This caused no file mutation, pipeline execution or lost evidence. Existing Arrow hardware-query warnings were observed only in historical Phase2 logs; no Arrow reader ran in this task.

No tests, static checker, model code or editor refresh were run. Exactly five documentation/JSON files were created, with no new Python source; the task-specific five-file/write-boundary restriction supersedes normal session-report location. No claim of new zero-error project-wide static verification is made.

## Scope compliance and Git

No source market data, geometry arrays, features, checkpoint, calibrator, scores, original code/results or sealed historical results were opened; no2025/protected2026 market path was enumerated, read or hashed. Dates2026 in audit filenames refer to reports, not market partitions. No network, installs, background processes, retries of pipeline work, Git mutation, fetch, fitting, refitting, calibration, threshold fitting or neural forward occurred. No additional agent was spawned for this investigation.

No Git command ran in this focused investigation. Last administrative state supplied by root remains branch `feat/track-a-data-intake`, HEAD `8061483cb65d03264a7836b8b882123f67cbe4ad`, tracked/cached diffs quiet and only untracked `replication/`; that is prior reported state, not a new check. No commit or push is authorized or recommended before human adjudication.

## Limitations and safe next step

No receipt supplies argv, start/end time, exact hook-registration time, event timestamp, read/write mode, call stack or preparation-time function hash. Current mtimes are not causality. Recorded good-path evidence cannot show that all unrecorded bad access was impossible. Synthetic method review does not independently authenticate every real source value. The B classification is intentionally narrower than numerical replication acceptance or live/causal certification.

Preserve all existing evidence. Review the specific provenance limitation with a human; stop here pending that decision. **Original results remain sealed.**
