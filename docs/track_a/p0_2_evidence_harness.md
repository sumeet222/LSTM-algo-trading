# P0.2 offline evidence contract

This utility records the current known and blocked state. It does not amend the
five governing documents or authorize the next package. `configs/CURRENT_PROTOCOL.json`
pins those exact files, version labels and SHA-256 values, plus P0.1 checks, the
existing bulk approval and pilot by reference. Source counts/hashes are inherited
from P0.1; the runner never opens raw data. Hashes prove identity, not provider truth.

From the repository root, after the existing README setup:

```bash
lstm-data evidence
lstm-data evidence --mode diagnose
lstm-data evidence --mode diagnose --output reports/my_unique_review.json
```

Default inspection writes nothing and returns 0 when metadata infrastructure is
valid, even though research remains BLOCKED. Diagnosis uses one fake 2001 record
per source and returns 2: F01-D2 is INVALID, with observed availability-age 60 and
required period-end age 120 minutes against the approved D2 maximum of 90. The
fixture's 60-minute delay is hypothetical, not a source-publication assumption.
`--output` creates a new small JSON file and refuses an existing path. `--dry-run`
forbids all writes. `--root` selects another clone; recorded paths remain relative.
The existing CLI `--config` applies to data commands; evidence uses the pinned
`configs/track_a_data.json`. No `.env` loading or credential availability probing is needed.

## Stable identities and check schema

Canonical JSON uses sorted keys and compact separators. Configuration fingerprints
exclude underscore internals, explicit metadata timestamp/Git/environment fields,
machine/executable attribution and credential fields; substantive date ranges,
cutoffs and research parameters remain included. Absolute configured inputs are
rejected, not silently normalized. Environment attribution is stored separately.
Existing ingestion fingerprints keep their original serializer; P0.2's compact
canonical `config_id` is a separate identifier and may differ for the same config.
Protocol identity includes the exact document list, evidence references and source
IDs. Run identity combines code contents, configuration, protocol and invocation
mode. Git SHA plus dirty/diff flags are attribution; uncommitted source changes are
also captured by the code-content hash. Local installed versions and version ranges
are not a portable lock or a completed clean-machine rehearsal.

Every check has `schema_version=1`, `gate_id` (G0–G9), `check_id`, `audit_run_id`,
`time_utc`, `protocol_version`, `protocol_hash`, nullable `code_id`, `config_id`,
`source_ids`, `status`, `evidence`, nullable `approved_threshold`, `example_ids`,
`affected_branches`, `owner_action`, `rerun_scope`, `explanation`.
Thresholds appear only when a governing rule exists. Machine statuses are exactly
PASS, WARN, BLOCKED, INVALID, INCONCLUSIVE, INACTIVE_CONDITIONAL, NOT_RUN. WARN maps
to the contract's investigate severity; INVALID to hard fail; no ambiguous aliases.

## Ledger schema and explicit append

One central ledger: `reports/audit/track_a_events.jsonl`. Each UTF-8 line is one
immutable event. Required fields are illustrated below; this is an example only,
not a recorded fitting result or human approval. Use the actual pointer hash when
preparing a separately authorized event.

```json
{
  "schema_version": 1,
  "event_id": "review-example-unique-id",
  "time_utc": "2001-01-02T15:00:00Z",
  "track": "A",
  "protocol_hash": "119513911f3f7fb1c51cb93381e3f5ebae6b8939bac8e056bf53448726ceb843",
  "gate_id": "G0",
  "package": "P0.2",
  "kind": "audit",
  "status": "NOT_RUN",
  "code_id": null,
  "config_id": null,
  "source_ids": null,
  "affected_branches": [],
  "artifact_refs": [],
  "evidence": {"example_id": "documentation-only"},
  "rationale": "Illustrative schema; not scientific evidence",
  "owner_action": "Human review before recording a real event",
  "blocks": [],
  "supersedes": []
}
```

After explicitly authorizing/preparing a small event file under `reports/`, append
with `lstm-data evidence --mode append --event reports/my_event.json`, then inspect.
Duplicate IDs, invalid fields/statuses, non-UTC timestamps, mixed protocol identities,
unknown correction targets, malformed/truncated rows and duplicate JSON fields fail
closed. A correction is a new event with `supersedes` IDs and an explanatory rationale;
old bytes remain an exact prefix. P0.2 refuses clearance or narrowing of blockers,
including a PASS correction. That requires a separately reviewed repair/migration.

`kind` is audit, decision, approval, blocker or experiment. Optional `decision_ref`
must bind a real relative decision file's `path`, `sha256`, `decision_id`. Its JSON
needs matching `decision_id`, `actor_type=human`, `owner`, and a nonempty `scope` list.
This is local human attribution, not cryptographic authentication; review the actual
record. Boolean approval flags are rejected. A decision record cannot activate a
research executor. Optional `run_id`, `seed`, `fitting_cutoff` are for future relevant
experiment plans. Genuine `attempt_id` or completed fitting events are prohibited
in this package. No genuine pair has been registered.

Writes use an exclusive `.lock` sidecar, validated old history, a bounded temporary
file, fsync and atomic replacement containing the exact old prefix plus one row.
This gives logical append-only behavior for cooperating local writers; it does not
make filesystem history tamper-proof or promise power-loss durability on every
filesystem. The ledger is bounded at 2 MB. Interrupted pre-publication writes leave
the prior ledger intact. A crash may leave a lock/temp file: preserve and inspect
it; there is no automatic stale-lock clearing, truncation repair or history deletion.

## Dependencies and managed enforcement

The derived blocker view never clears a blocker because an unrelated test passed.
Seven initial events cite preserved P0.1 checks: F01, USA500 identity/publication,
stock publication, minute execution, actions/dividends, formation/prehistory, shared
D3 clock. P0.1 raw-integrity PASS subchecks remain narrower evidence by reference.
G0/G1/G2 research readiness remains BLOCKED; G3–G9 are NOT_RUN.

`guard_operation` allows only stock-only administration in this package. Market
timing/F01 adds market-specific causes; portfolio-accounting failures add economic
causes without contaminating independent predictive checks. All actual features,
training and evaluations are unavailable until a separately reviewed runner and
human authorization exist. Confirmation is always rejected here, including with
an empty ledger: future G9 needs an immutable manifest lock and human decision.
No predictive/economic confirmation metrics are read or generated.

The pure future `pair_budget` guard counts unique attempted pair IDs across all
history, including failed attempts and superseded outcomes. At 39, a new 40th ID
is allowed by the budget alone; at 40 a new 41st is BLOCKED. A reused candidate ID
is rejected rather than disguising a new attempt; repeated outcome records for
the same pair count once. Synthetic tests exercise boundaries without fits. A
budget PASS is not authorization. These guards constrain this managed API only;
they do not block arbitrary shell scripts or enforce OS-wide research permissions.

Offline tests cover hashes, schema, append failure preservation, narrow blockers,
F01, missing approvals, confirmation refusal and synthetic budget limits. They do
not verify publication timing, source identity, formation, corporate actions,
execution data, real target construction or scientific performance.
