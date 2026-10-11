# Shared decisions registration package

Registration COMPLETE; scientific/execution status BLOCKED. CT-D3-001 is RESEARCHER_REPORTED_JOINT_AGREEMENT (240 continuous RTH minutes), with formal independent attestation pending. CT-MKT-002 is APPROVED_DIRECTION / IMPLEMENTATION_DEFERRED / SOURCE_UNRESOLVED. This records the researcher's reported joint agreement and instructor permission; it does not authenticate absent correspondence.

Record: `docs/track_a/decisions/Shared_Cross_Track_Decisions_2026-10-11_v1.0.md`

SHA-256: `11bfcf177dd8b0b5a98d01f2c394ae5f25d87e16f59bcec38e9f2d62e408725b`. Submitted handoff SHA-256: `51c73d1ff320c8be6e8dcbc6417f644f9173f56148214cd8f3c85b493b45f179`. Full substantive §§1–2 preserved; registration/discrepancy index added in the same single file. No existing canonical cross-track register found; frozen D1–D13 and task-local USA500 registers are not overwritten.

## Preserved authority

| File | Unchanged SHA-256 |
|---|---|
| `docs/track_a/Shared_Project_Specification.md` | `12863e44efa2ca3c51d5f5c5033a3735b16b4a87a00158122d372db6ed9cdf32` |
| `docs/track_a/Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md` | `7afb1d3fe6cd5bf68e1e9a1c8e6f19e200ce2c4cae6414b1b0b90e40365339ce` |
| `docs/track_a/Track_A_Consolidated_Implementation_Design_Record_v1.2_2026-10-10.md` | `cf3f7531ecd52e47386e64035d5c86ab513acc3c1a6bbbee5e54ad325eb9a96c` |
| `docs/track_a/Track_A_Stage_Gated_Audit_and_Failure_Traceability_Plan_v1.1_2026-10-10.md` | `a29309ef791f74f72443b2b66ad1d9cde5f46e54dfbcd072f5bda5da68d1878d` |
| `docs/track_a/Track_A_Codex_Incremental_Implementation_and_Human_Review_Plan_v1_2026-10-10.md` | `bf3459456b12c23942d99bd555cc66137cd6154c79119ae96eaa3bfdb88a202d` |

Pointer: `configs/CURRENT_PROTOCOL.json`; unchanged SHA-256 `1b83b2ef8f727618ef319c0c04b36056c5c8cb19857ebe40927851e3295ca600`. Protocol identity `119513911f3f7fb1c51cb93381e3f5ebae6b8939bac8e056bf53448726ceb843`. Exact 41 protected document/config/code/test/setup/report hashes and Git index identity verified unchanged. Pointer not migrated; raw/source rows and confirmation outcomes not read.

## Ledger and remaining blockers

`reports/audit/track_a_events.jsonl`: 18 → 19 events. Exactly one `kind=decision`, `status=WARN`, G0 registration event `shared-decisions-2026-10-11-010144`; `blocks=[]`, `supersedes=[]`. Prior 28233 bytes remain an exact prefix, SHA-256 `5b8a76665af1e9c8714005837bfa765d0cdc13c73eb4003eb8f86ebf59c3caca`. No approval event inferred. Existing validators reused unchanged; writer uses an exclusive lock and atomic replacement.

- `p0.1-F01`
- `p0.1-USA500-source-clock`
- `p0.1-stock-publication`
- `p0.1-minute-execution`
- `p0.1-actions-dividends`
- `p0.1-formation-prehistory`
- `p0.1-shared-D3-clock`

All seven blocker identities/dependencies remain. Shared-clock substantive disagreement is resolved by the reported decision; its administrative evidence blocker remains historical and active until separately authorized evidence-qualified closure. Source/availability/action/formation/label obligations and USA500 U1–U5/MC0–MC2 holds remain. F01 repair is not source certification. Zero of 40 training pairs used. No G0/G1/G2 global PASS.

## Changed files

- `docs/track_a/decisions/Shared_Cross_Track_Decisions_2026-10-11_v1.0.md`
- `reports/data_audit/shared_decisions_2026-10-11_010144/package_report.md`
- `reports/data_audit/shared_decisions_2026-10-11_010144/checks.json`
- `reports/codex_sessions/2026-10-11_010144_feat-track-a-data-intake_shared-decisions.md`
- `reports/audit/track_a_events.jsonl`

Five small files: four new Markdown/JSON records and one append-only ledger modification. No code, tests, source config, roadmap or P2.1 edits; no data requests, labels, training or full suite. Git index unchanged; nothing staged, committed or pushed by this task.

Locator clarification for the addendum discrepancy table: Consolidated **P05 is in §18** and **C02 is in §19** (the table's §19 P05 / §20 C02 section numbers are typographical errors; the stable item IDs are correct). The hash-bound addendum and ledger row are preserved; use these corrected locators during review.

## Human review checkpoint

1. Review CT-D3-001: 240 continuous same-session RTH minutes are substantively chosen by researcher-reported joint agreement; cutoff/issuance/entry/C01 boundaries retained; independent attestation remains pending.
2. Review CT-MKT-002: approve/correct the reported direction and its deferred scope. No source chosen; course-series disposition, compliance evidence and joint scientific amendment still required.
3. Verify hash bindings and the single WARN/decision ledger row: no supersedes, no blocker narrowing, no global G0/G1/G2 PASS or execution authorization.

STOP after this micro-package. Researchers can add independently attributable acknowledgment in a durable channel under existing governance. Source selection/amendment/pointer migration and any next implementation need separate authorization; the scientific debate is not reopened by missing administrative evidence. No human contact was sent.

## Tiny verification and reproduction

Existing event/check validators; record/authority/pointer hashes; preserved code/config/test/index/HEAD; exact ledger prefix, blocker identities and zero fits; `git diff --check`. Metadata checks only: no repeated full suite or raw scan. Follow README's existing virtualenv setup (`python -m pip install -e '.[dev]'`); no secrets/data needed for the checks below. Prefix SHA is historical evidence, not a reconstructed raw dataset. Later authorized appended events may exist beyond this package's recorded ledger endpoint.

```bash
python -B - <<'PY'
from pathlib import Path
import hashlib, json
from lstm_data.audit import validate_check
from lstm_data.ledger import decode_ledger, current_blockers, safe_payload
payload = json.loads(Path("reports/data_audit/shared_decisions_2026-10-11_010144/checks.json").read_text())
safe_payload(payload)
for c in payload['checks']:
    validate_check(c)
    for key in ('document', 'pointer'):
        e = c['evidence']
        if key + '_path' in e:
            assert hashlib.sha256(Path(e[key + '_path']).read_bytes()).hexdigest() == e[key + '_sha256']
    for d in c['evidence'].get('documents', []):
        assert hashlib.sha256(Path(d['path']).read_bytes()).hexdigest() == d['sha256']
e = next(c['evidence'] for c in payload['checks'] if c['check_id'] == 'CT-LEDGER-PRESERVED')
raw = Path(e['path']).read_bytes()
assert hashlib.sha256(raw[:e['old_prefix_bytes']]).hexdigest() == e['old_prefix_sha256']
events = decode_ledger(raw)
recorded = events[:e['events_after']]
assert len(recorded) == e['events_after']
assert recorded[-1]['event_id'] == e['event_id']
assert recorded[-1]['kind'] == 'decision'
assert recorded[-1]['blocks'] == recorded[-1]['supersedes'] == []
assert [b['event_id'] for b in current_blockers(recorded)] == e['remaining_blocker_ids']
print('Schemas, record/authority hashes, historical ledger prefix and blockers verified')
PY
```
