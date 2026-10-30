# Stage3 Session1 — read-only audit handoff

## 1. Session metadata

2026-10-28; requested HF20 minute-source/causal representation audit only. Branch `feat/track-a-data-intake`; starting/ending HEAD `997b30cff98785911b0e33b7e3d2e72f61b8270b`. No commit/push/fetch/network. Cached upstream0/0, not freshly verified. Current human instruction permits new files only in this audit namespace; this handoff supplies the session report here rather than writing elsewhere.

## 2. Executive result

**PARTIAL audit: full-path SOURCE_PERMISSION_BLOCKED; metadata and proposals delivered.**174 canonical minute receipt members locally present, but purpose-limited historical endpoint access is not a current minute-feature grant. No minute OHLCV content read. Sample saved hourly counts:210 unique origin windows,1,344 grid hours,26,880 stock-hours;99.246% genuine minute positions,88.977% complete stock-hours. Zero complete20 full48 sampled origins;5/134 complete20 newest-hour OOS samples. Source coverage is conditional/nonrandom, not a forecast result or population estimate. B/C proposals require approval; no winner selection.

## 3. Research/protocol impact

None implemented. All original labels,20-stock axis,48×16 FT16,10 CLOCK fields, Design A roles/embargoes, prior controls and gap task preserved. Seven-feature B and latest-hour C contracts are explicitly unapproved. D/E and Stage5 deferred. No model, baseline, calibrator, feature normalizer, target threshold or performance metric fitted/computed. Four-hour and dedicated gap tasks remain separate; deferred C0/M1 routing and intraday preference untouched.

## 4. New files

Only this namespace. Main audit report; source access/timing receipt; minute_coverage.csv; two unapproved representation proposals; Session2 readiness matrix; metadata_audit_summary.json; role_geometry_counts.csv; compact unique-origin sample_input_geometry.csv; unique_hour_metadata_summary.csv; sample_origin_slot_summary.csv; sample_era_summary.csv; input_hour_calendar_quality.csv; this handoff. No persistent Python module/notebook, per-minute export, copied source/score store, model, plot or cache.

## 5. Existing files modified

None. Starting dirty tree remains: registry edit and untracked completed S2-D namespace/module/test/previous handoff. They belong to prior work and were preserved. No journal/registry pointer/budget metadata change.

## 6. Deleted/moved/renamed

None.

## 7. Important interfaces

No public code/config interface added. Audit equations/contracts are Markdown proposals only. `minute_coverage.csv` uses separately labeled `aggregation` rollups: do not add cross-rollup or overlapping role rows. Its `synthetic` field counts preexisting cap5 proxy placements overlapping unobserved positions; no synthetic path was created. Sample `windows` rolls up stock-window occurrences. Readiness strict-completeness counts are counterfactual descriptions, not adopted gates. S3-D/E rows are conditional notes, not executable plans.

## 8. Data/schema/provenance and exact read scope

Pinned HF dataset/revision from existing configs and S4 receipt; no acquisition manifest traversal. All174 pre2025 canonical minute members: filename/existence/size only, no content/schema/hash.16 fixed monthly adjusted-hourly partitions: count/timing/quality columns only; no price/volume payloads. Their whole-month nonstub metadata was projected before exact block-key retention in the initial audit; a focused replay pushes selected block keys into Parquet filters.14 months contribute samples;2012-05/2024-11 contribute none under frozen keys/within-month sampling, not proof of source absence.

Actual retained block times2011-04-06T18:30Z–2024-12-31T16:30Z. Whole-month timing/count projection bounds2011-04-01T13:30Z–2024-12-31T20:30Z. No retained block ends after its prospective forecast cutoff. The pre2025 grid uses a Parquet date filter; mixed grid content not hashed. Source-origin flags/clock/maturity fields and saved20 role arrays projected, no endpoint/return/target value column. Prior reports/code read for source/timing/contract context, not feature selection by forecast errors. No score Parquet or checkpoint opened; CLOCK key equivalence inherited from its role-bound protocol, not freshly score-key-joined. No2025 market or2026 protected content/path/hash, credential or network access.

The canonical minute stream is upstream of P019B action/quarantine adaptation. Existing adjusted hourly inputs, March2026 historical split-consistent price basis, observed share volume, COP boundary and timestamp policy are documented, not silently changed. Future action/arrival-time validity remains a decision; masks must not import retrospective label support or unavailable QA signals. Underlying vendor/feed rights and historical arrival latency remain unverified.

## 9. Environment

No dependency/env/package/install changes. Repository `.venv/bin/python -B`; no local bytecode emitted. Main audit peakRSS218,726,400bytes. Output around1MB, below inherited caps. Project last reported12.44GB; not re-scanned, to avoid broad protected-source traversal. Free volume checked by filesystem metadata only (~38GB); not a substitute for project cap. Arrow CPU-cache sysctl sandbox warnings nonfatal; optional ps inspection denied and not needed for this zero-model audit.

## 10. Commands/checks

`git status --short --branch`; `git rev-parse HEAD`; `git rev-list --left-right --count HEAD...@{upstream}`; `git diff --stat`; `git diff --check`. No fetch under explicit current restriction.

Inline `.venv/bin/python -B - <<'PY'` projections/aggregations/assertions (no persistent script) generated tables. `load_deferred_work(Path('configs/track_a_p2_engineering_handoff_v1.json'))` hash-verified16 unchanged register entries; no statuses cleared. All20 exact role lengths,>=50/25 selector coverage,48-step geometry,maturity/embargo,last-input≤origin,source revisions,stock order,counter conservation,monotone54/57/59 diagnostic counts,scoped preservation and166 ledger checks PASS. Source-minutes duplicate/finite/positivity/zero-volume/reaggregation tests BLOCKED_PERMISSION, not claimed PASS.

No broad pytest/Ruff/full-repo Pylance scan, as expressly instructed for this read-only audit. No package code changed. The previous S2-D zero-error report is historical evidence only, not a new static result. Editor refresh: retain repository `.venv/bin/python` and existing Pylance basic; actual Problems refresh is human-confirmed. No new checker/HOLD claim is inferred from not running a prohibited broad scan.

## 11. Experiments/results

No experiment run. No model scoring or target correlations. Journal remains166/300;0 neural starts/optimizer phases,0 baseline/calibration fits,0 forward passes. Conditional future B+C up to8 pairs/16 phases requires a separate authorization;134 remaining capacity is not fit permission. A third trained latest-hour summary control is outside that eight-start plan and needs explicit budget/design approval.

## 12. Reproduction

Read the receipt for exact source columns, sampled months, role archive and scoped hashes. The following source-only snippet reproduces the central unique-hour totals without model imports, targets, minute-path access, writes or new policies. It deliberately does not load every source month or any2025/2026 content.

```python
from pathlib import Path
import json
import numpy as np
import pandas as pd
base = Path('reports/experiments/hf20_s9_mag_stage3_session1_minute_readonly_audit_2026-10-28')
spec = json.loads((base/'metadata_audit_summary.json').read_text())
contract = json.loads(Path('reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122/model_input_contract.json').read_text())
g = pd.read_parquet(contract['files']['grid']['path'], columns=['hour_start_utc','session_date_et'], filters=[('session_date_et','<=','2024-12-31')])
r = pd.read_parquet('reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/opening_reaudit_v2/S4_ORIGIN_SOURCE_ELIGIBILITY.parquet', columns=['session_date_et','slot','regular_session','first_step','entry_index'])
z = np.load('reports/experiments/hf20_s9_mag_stage1_session3_o1_2026-10-28/role_indices.npz')
chosen = set()
for key in z.files:
    a = r.iloc[z[key]].copy()
    a['month'] = a.session_date_et.str[:7]
    a['first_month'] = g.session_date_et.to_numpy()[a.first_step.to_numpy(int)].astype(str)
    a = a.loc[a.month.isin(spec['sample_months']) & a.month.eq(a.first_month.str[:7])]
    for _, v in a.groupby(['month','slot','regular_session']):
        ids = v.index.to_numpy()
        chosen.update([int(ids[(len(ids)-1)//2]), int(ids[-1])])
needed = np.unique(np.concatenate([np.arange(int(x.first_step),int(x.entry_index)+1) for x in r.loc[sorted(chosen)].itertuples()]))
frames = []
for ref in spec['hourly_count_files']:
    month = ref['path'][-15:-8]
    starts = g.loc[g.index.isin(needed) & g.session_date_et.str.startswith(month),'hour_start_utc'].tolist()
    if starts:
        frames.append(pd.read_parquet(ref['path'], columns=['ticker','hour_start_utc','expected_minutes','genuine_count','missing_count','quarantine_count','conflict_count','invalid_minutes'], filters=[('hour_start_utc','in',starts)]))
h = pd.concat(frames,ignore_index=True)
assert len(chosen)==210 and len(needed)==1344 and len(h)==26880
assert not h.duplicated(['ticker','hour_start_utc']).any()
assert (h.expected_minutes==h.genuine_count+h.missing_count+h.quarantine_count+h.conflict_count+h.invalid_minutes).all()
assert h.expected_minutes.sum()==1612800 and h.genuine_count.sum()==1600640
assert h.genuine_count.eq(60).sum()==23917
print('PASS: saved-hourly sample counters only; no minute paths or target values')
```

Use existing documented environment and locally authorized artifacts; no downloads. Do not invoke old parent verifiers, source scanners, data builders, training/report runners or discovery loaders: some hash/read2025/protected scopes or fit models. None is needed to repeat this metadata audit.

## 13. Git/collaboration

Branch/SHA unchanged; cached upstream0/0. All prior work uncommitted as at entry. New audit namespace is the sole addition. Sixteen scoped preexisting hashes/mtimes match; existing registry diff unchanged. No stash/reset/clean/pull/merge/rebase/commit/push. Review this namespace before any separately authorized tracking/commit; no model files present. No additional report written outside this namespace under the current explicit write restriction.

## 14. Limitations

No current full-path permission; no numeric minute validity/arrival/reaggregation proof; stratified nonrandom sample and omitted month-boundary histories; two zero-retained requested months; no exhaustive intersections, zero-volume frequency or minute-gap locations. Historical curation/action vintage and fixed survivor universe remain. Stock missingness is not MCAR. Sample counts cannot become future eligibility thresholds. New feature/encoder proposals change information and parameters; fair-control decision remains. No newly run static/test suite or score-key join should be implied.

## 15. Human decisions

Explicit bounded minute-read grant; as-of source-QA/publication assumption; B7 features/masks/fallbacks; C7-channel/H8 fusion/dropout/normalizers; original full-key validity; simple latest-hour summary/capacity control and consequent budget. Source-restricted branches remain blocked until resolved. D/E and ranking-loss experiments need separate later decisions. No current request for permission interrupts this completed audit.

## 16. Next step

Researcher reviews main report/proposals. **STOP; no Session2/3 fitting, calibration, source acquisition, promotion, routing, trading/options or protected confirmation.**

## 17. Artifact inventory

All files below are small new uncommitted audit deliverables. CSVs contain aggregated metadata/counts only, geometry contains keys/timestamps only; JSONs contain source/preservation/permission/count receipts. No market outcomes or model outputs exported.

| File | Bytes |
| --- | --- |
| S3B_FEATURE_CONTRACT_PROPOSAL.md | 8502 |
| S3C_MINUTE_ENCODER_CONTRACT_PROPOSAL.md | 8209 |
| S3_SESSION2_READINESS_MATRIX.csv | 5032 |
| STAGE3_SESSION1_MINUTE_AUDIT_REPORT.md | 32822 |
| input_hour_calendar_quality.csv | 22804 |
| metadata_audit_summary.json | 53106 |
| minute_coverage.csv | 698862 |
| role_geometry_counts.csv | 4195 |
| sample_era_summary.csv | 551 |
| sample_input_geometry.csv | 68098 |
| sample_origin_slot_summary.csv | 348 |
| source_access_and_timing_receipt.json | 15934 |
| unique_hour_metadata_summary.csv | 2332 |

`SESSION_HANDOFF.md` is this file; its final byte size is available from the filesystem. No preexisting asset was altered.
