# Codex Session Report

## 1. Session metadata

- Session: HF20 S9-MAG Stage2 S2-C C-A prospective masked decomposition, 28 October2026; final handoff 2026-10-28T19:43:54.803655+00:00.
- User authorization: exactly four fixed seed42 selector/refit pairs after all-fold PASS; own fixed C3-style calibration, original four-hour target; no S2-D/extra model or source expansion.
- Branch: `feat/track-a-data-intake`; starting and ending commit `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42` (no new commit).
- Initial tree: already dirty registry plus supplied/untracked prior handoffs, research modules/tests/reports. Preserved. Current adds the new C-A module/test/output namespace and this report; registry advances only the permitted successor pointer.
- Git fetch initially denied `.git/FETCH_HEAD` by sandbox, then approved `git fetch --all --prune` succeeded; upstream0 ahead/0 behind. No pull/merge/rebase/stash/deletion/commit/push.

## 2. Executive summary

**COMPLETE4/4, marginal/mixed exploratory MSE gain.** Calibrated C-A raw MSE0.000106548167844 is0.1104% below CLOCK-C3 and0.6330% below older C3 on the same80260 rows/4013 origins/793 sessions. Annual changes versus CLOCK-C3: +0.02565%,−0.09906%,−0.02881%,−0.28826%; F21 loses. Equal-year paired delta−1.17778e−7,400-draw whole-month descriptive95% interval[−2.29973e−7,−5.11120e−9], barely below zero and not selection-adjusted confirmation. About68.5% of net gain comes from F24.

Full MAE is effectively unchanged (−0.01476%), IC improves.330254→.331236, but mean ratio slightly worsens1.01376→1.01522. Overnight MSE improves.1455%; intraday MSE/MAE worsen.0277%/.1127%. Prefix95/99 tail MSE improves.3560%/.2462% versus CLOCK-C3;95 ordinary-complement MSE worsens.4136%. Tail MSE still loses to older C3. Signed auxiliary correlations are weak/inconsistent. Keep C-A only as a provisional near-tie candidate; CLOCK-C3 remains a reference, not automatically replaced across all use cases.

Four charged starts/eight phases, ledger158→162/300, no failed attempts/retries. Selected8/13/22/17 epochs;160 actual epochs/24885 updates/304 clipped batches. Fit lifecycle sum4078.55s; peakRSS846200832 bytes, new output about3.94MB, project12.44GB (all within2GB/2.5GB/15GB caps).

## 3. Research/protocol impact

Prospective amendment only to the formerly blocked S2-C all20 auxiliary-source gate: one genuine complete-triple mask per stock-origin, identical for all three signed heads; main20-stock primary loss/keys remain complete. No C-B, missing-label recovery, imputation or source replacement. Same main log1p magnitude target and240 trading-minute endpoint,48×16 FT16, actual clock/early closes, Design A roles and phase preprocessing. Original C/D BLOCKED reports remain intact; no S2-D change or execution.

Model adds3 independent42→1 signed rows to the same final hidden+10-clock representation;6572 parameters versus S2-B6443. Rhat=s*u; aux loss is.10 times mean of three squared signed normalized risks. Training weights are original conditional overnight session/origin/20 weights times mask/global phase masked mass. Batch factor S_phase/B_batch preserves the declared global objective; no per-batch denominator or surviving-stock redistribution. Primary M loss and main-only selector remain unrestricted. Same seed42, CPUfloat32, one-layerH32, final hidden dropout.10, AdamW .001/betas(.9,.999)/eps1e-8, matrix decay.01/bias0, normclip1 and16 complete sessions. No warm start; fresh refit at selected epoch with own September s/recipe.

Own reserved Oct–Dec main residuals fit fixed C3 IO pooling kappa25 only after checkpoint freeze. Raw diagnostic is not an OOS-selected alternative. Source/target/features/survivor universe/horizon/trading mapping/seeds/search space otherwise unchanged. No portfolio, options, event-head, deferred route or protected release.

## 4. Files created

- `src/lstm_data/hf20_s2c_ca.py`: isolated authorized CLI, model, global mask weighting, all-fold source/key/preprocessing gate, one selector/refit pair/year, own calibration, saved-score reporting. Relative paths, no new dependencies/framework.
- `tests/test_hf20_s2c_ca.py`: four focused fixture groups for seeded primary parity/reload, missing/empty auxiliary gradients, global session-sampling loss identity and signed target/selector invariants. Ten existing clock/C3 fixtures reused.
- This session report.
- Every new result file is individually listed in section17. Nothing outside the new namespace is a new dataset/cache.

## 5. Files modified

Only existing `configs/CURRENT_EXPERIMENT_REGISTRY.json`: schema29→30 and current definition/plan/journal/predecessor pointer for the authorized C-A successor. Ceiling300 and all other unchanged metadata preserved. Opening pointer is frozen in S2C_CA_PROTOCOL.json. Previous registry edits were already present at entry; no older ledger/config/report/checkpoint/recipe/score/source/dashboard edited.

New own reporting tables/interpretation were finalized after fits; frozen protocol/preflight, learned coefficients, traces, models and model code remain unchanged. `--report` produces byte-identical numerical tables.

## 6. Deleted, renamed or moved

None.

## 7. Critical interfaces

- `ComponentMAG` / `model_for_components()`: original seeded S2-B trunk/main initialization, signed linear auxiliary rows, shared dropped final representation; no labels/masks as model inputs. `forward` is inherited primary-only; `all_heads` supplies training and post-fit signed diagnostics.
- `phase_aux_weights(rows,pos,mask) -> (weights,receipt)`: legal phase-only overnight base weights, global masked normalization; outside phase/N/mask zero. Requires nonempty finite mass. Saves S_phase versus S_N/session/origin denominators.
- `masked_aux_loss(u,labels,mask,w,s,S/B)`: indexes only genuine supported cells before residual arithmetic, averages3 head risks, returns exact zero-gradient term for an empty batch. Never replaces NaN labels with zero.
- `preflight`: new immutable declared contract before numeric source proof, all20 role arrays and genuine label/source/clock/key/axis/maturity checks, exact archived mask counts. No fit/forecast scoring.
- `prepare_phases`: independently refits8 legal prefix scalers/floors/s; verifies exact S2-B parity before first STARTED. Uses original input-only fitting rows, not auxiliary-supported subset.
- `train_epoch` / `run_fold`: complete-session shuffle42+epoch, main+fixed auxiliary loss, main-only qualified-best epoch selection, fresh seed/optimizer September refit; freezes model before own-tail scalar estimation and OOS. No retries.
- `journal`: one charged pair/year159–162, statuses STARTED/SELECTED/REFITTING/COMPLETED, append-only predecessor link/current pointer update, no reset.
- `write_report`: saved same-key comparisons, native dependent-time bootstrap and conditional group/rank summaries. No model forward or fitting on replay.

## 8. Data/schema/provenance

Existing174 permitted adjusted-hourly partitions2010-07..2024-12 and the existing saved S4 genuine endpoint/component Parquet; no new minute/source read, provider, bulk tensor copy or acquisition. Numeric fields inspected only as authorized for source checks, labels, training and final diagnostics. Positive/finite supported genuine prices, one-closure geometry and COP basis pass; supported signed additivity max4.250072516e−16 under atol1e−12/rtol1e−11. A supplemental direct per-leg ratio check during execution (before performance inspection) matches every supported saved component exactly, with zero error; principal pre-fit source positivity/identity/provenance checks had already passed. No component is inferred or repaired.

Original main keys and weights exactly match S2-B/C3 and saved S4 role arrays. True240-minute endpoints and early-close morning exceptions are preserved. All original main20 stocks remain even where auxiliary labels are missing. Full stock/month/slot source concentration is referenced from the unchanged audit; MS/MRK and historical MA missingness is not assumed MCAR. No primary-label eligibility relaxed. Calendar-only next-session lookup may enter Jan2025; no2025 market or2026 protected numeric/path/hash read. Target starts before approximate origin+2min issuance; price-only, not executable returns.

New OOS/calibration Parquets contain only own main Mhat/raw/calibrated values plus canonical metadata/A/weights; no copied old score columns. Signed aux diagnostics use original OOS weights renormalized on supported cells/ticker; these are descriptive auxiliary-task errors, not primary magnitude errors or a new gap model.

## 9. Dependencies/environment

No new/changed package, lockfile, setup or environment variable. Existing repository .venv;4 intra-op/1 inter-op Torch threads, deterministic CPUfloat32 seed42. Physical RAM8GB;35GiB free disk at gate. Sandbox denied first Git fetch/sysctl; approved reruns succeeded. PyArrow CPU-cache sysctl EPERM warnings are nonfatal metadata probes; source reads and checks succeeded. No source network/downloads. No portability rehearsal/new environment install in this scoped task.

## 10. Commands and tests

```sh
git status --short --branch
git branch --show-current
git rev-parse HEAD
git remote -v
git fetch --all --prune
git rev-list --left-right --count HEAD...@{upstream}
.venv/bin/python -m lstm_data.hf20_s2c_ca --preflight
.venv/bin/ruff format src/lstm_data/hf20_s2c_ca.py tests/test_hf20_s2c_ca.py
.venv/bin/ruff check src/lstm_data/hf20_s2c_ca.py tests/test_hf20_s2c_ca.py --output-format concise
.venv/bin/python -m pytest tests/test_hf20_s2c_ca.py tests/test_hf20_stage2_bcd.py tests/test_hf20_mag_c3_io.py -q
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist > /private/tmp/s2c_ca_types_ready.json
.venv/bin/python -u -m lstm_data.hf20_s2c_ca --run > reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/execution.log 2>&1
.venv/bin/python -m lstm_data.hf20_s2c_ca --report
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist > /private/tmp/s2c_ca_types_final.json
git diff --check
```

Final14 tests pass in3.94s; Ruff PASS; full512-file basic static check zero errors/warnings109.308s (pre-fit final151.985s, zero errors/warnings). Initial2 diagnostics (Pandas Hashable group key, Python sum's int start in fixture) fixed before fitting via string-key conversion/explicit Tensor addition; no ignore/cast/severity exclusion or model/protocol change. Initial formatting errors fixed before fits. No hidden neural failure or changed scientific rescue.

Synthetic checks prove primary initialization/trunk parity and actual reload, three signed shapes, NaN masked cells ignored, missing-stock and empty-aux gradients zero, uneven-origin/three-session minibatch global-gradient identity, complete primary target hierarchy, signed-sum versus absolute-sum distinction and qualified selector rule. Existing clock/C3 fixtures cover actual early-close exceptions and matched decoder/session shrinkage. Empirical all4 reload errors0, raw/cal ranks identical with zero clamps; all150 old B control metric rows reproduce;8 own prefix phase recipes/scales exactly match. Final9-file numeric protocol/metric/journal replay is byte-identical, new code still equals pre-fit readiness hashes; previous bound assets unchanged.

Editor instructions: select `.venv/bin/python`, retain installed Pylance basic severity, refresh Problems; actual editor refresh remains human-confirmed, not agent-verified. No residual checker/parity failure/HOLD.

## 11. Experiment/results summary

IDs `HF20-S2C-CA-F21-S42`..`F24`. Initial/refit phases remain frozen Design A cutoffs; own s in phases.json, exact final checkpoint identities in result.json. Selected epochs8/13/22/17; selector stops18/23/32/27; raw minima8/13/22/23 (F24 raw minimum23 does not override qualifying17). No same-year/Oct–Dec supervision in model fitting or epoch selection. Fit summary and calibration table record all selected quantities, not a grid.

Primary equal-year MSE.000106548167844 vs CLOCK-C3 .000106665945886;−.1104%. Versus C3−.6330%,M1−1.5870%,B0-VOL−4.4929%. Raw model versus CLOCK-RAW MSE−.2501%. None establishes separate causal decomposition effect; architecture-head capacity/dropout RNG trajectory, joint gradients, epochs and own calibration are connected choices. Signed correlations remain near zero/inconsistent. Gap-sign auxiliary performance is not a dedicated15:30 gap-magnitude forecast or event classifier.

95/99 tail MSE−.3560%/−.2462% versus CLOCK-C3, but95 ordinary complement+.4136%; intraday MSE+.0277%. Mean ratio worsens slightly.95-event top4 recall55.3486% vs55.3064%;99 recall66.6869% vs67.5660%;false-low99 worsens12.6699→12.7709%. Event cohorts use already saved legal prefix thresholds; no OOS threshold fitting. Full MAE/rank changes are tiny. Only F24 annual CLOCK contrast interval excludes0; equal-year interval barely does, and all evidence is post-search/conditional, not confirmation.

## 12. Reproduction

Use documented existing .venv/setup and already-authorized saved source/role/calibration/comparator artifacts. From repo root, `--report` reproduces central tables without fitting/model inference. `--run` is single-use and must refuse this completed namespace; do not bypass journal guard or rerun to change outcomes. Reproducing the original training requires a separately authorized fresh namespace, original inputs/contracts and identical design/seed; the current task is STOPPED.

The extra post-fit event_retrieval.csv is derived with the exact standalone saved-score snippet below (no fitting, inference, new event threshold or environment state). It reuses native helper paths/weights and verifies fractional top4 mass4/origin and false-low equality against groups.csv. Copy to a temporary file and execute with `.venv/bin/python -B`; all paths are repository-relative. Core --report leaves this derived table intact.

```python
from pathlib import Path
import pandas as pd,numpy as np,json
from lstm_data import hf20_s2c_ca as s
p=s.OUT
records=[]
for y in s.b.YEARS:
 f=pd.read_parquet(s.c3.root(y)/'oos_scores.parquet')
 new=pd.read_parquet(p/f'F{y%100}/oos_scores.parquet');clock=pd.read_parquet(s.clock.OUT/f's2b_clock/F{y%100}/oos_scores.parquet')
 np.testing.assert_array_equal(f[['origin_id','ticker']],new[['origin_id','ticker']]);np.testing.assert_array_equal(f[['origin_id','ticker']],clock[['origin_id','ticker']])
 f[s.CAL]=new[s.CAL];f['CLOCK-C3']=clock['CLOCK-C3'];f['C3']=s.prior.frozen_c3(f,y)
 threshold=json.loads((p/f'F{y%100}/phases.json').read_text())['thresholds']
 for arm in [s.CAL,'CLOCK-C3','C3','B0-VOL']:
  grouped=f.groupby('origin_id')[arm];first=grouped.rank(method='min',ascending=False);last=grouped.rank(method='max',ascending=False)
  top=np.clip((5-first)/(last-first+1),0,1);low=grouped.rank(method='average').le(10.5)
  assert np.allclose(pd.DataFrame(dict(id=f.origin_id,top=top)).groupby('id').top.sum(),4)
  for scope,base in [('ALL',pd.Series(True,index=f.index)),('INTRADAY',f.category.eq('INTRADAY')),('OVERNIGHT',f.category.eq('OVERNIGHT'))]:
   for level in [95,99]:
    event=f.A.gt(threshold[str(level)])&base;mass=float(f.loc[event,'weight'].sum());base_mass=float(f.loc[base,'weight'].sum())
    if not mass:continue
    hits=float((f.loc[event,'weight']*top.loc[event]).sum());topmass=float((f.loc[base,'weight']*top.loc[base]).sum())
    records.append(dict(year=str(y),arm=arm,scope=scope,prefix_percentile=level,event_rows=int(event.sum()),event_sessions=f.loc[event,'session_date_et'].nunique(),event_prevalence=mass/base_mass,event_top4_recall=hits/mass,top4_event_precision=hits/topmass,false_low_rank=float(np.average(low.loc[event],weights=f.loc[event,'weight']))))
t=pd.DataFrame(records);eq=[]
for (arm,scope,level),h in t.groupby(['arm','scope','prefix_percentile'],sort=False):
 if len(h)==4:eq.append(dict(year='EQ',arm=arm,scope=scope,prefix_percentile=level,event_rows=int(h.event_rows.sum()),event_sessions=int(h.event_sessions.sum()),**{k:float(h[k].mean()) for k in ['event_prevalence','event_top4_recall','top4_event_precision','false_low_rank']}))
t=pd.concat([t,pd.DataFrame(eq)],ignore_index=True)
g=pd.read_csv(p/'groups.csv',dtype={'year':str})
for row in t.to_dict('records'):
 h=g.loc[g.year.eq(row['year'])&g.arm.eq(row['arm'])&g.field.eq('tail_'+row['scope'])&g.group.eq('PREFIX'+str(row['prefix_percentile']))].iloc[0]
 np.testing.assert_allclose(row['false_low_rank'],h.false_low_rank,atol=1e-14,rtol=1e-13)
t.to_csv(p/'event_retrieval.csv',index=False)
print(t.loc[t.year.eq('EQ')&t.scope.eq('ALL')].to_string(index=False))

```

## 13. Git/collaboration status

Current branch/SHA unchanged; remote fetched successfully,0 ahead/0 behind at start. No commit or push. Unknown/preexisting untracked research assets and dirty registry changes protected; do not pull/integrate over them. New code/test/reports and all small receipts remain uncommitted; PT/Parquet intentionally local/ignored. Review only the new C-A files and permitted registry successor, plus separately account for prior untracked module/artifact dependencies before any future teammate PR; do not blindly add/discard all old work.

## 14. Known issues/limitations

No failing test or model/source/key invariant. Result is a tiny, F24-heavy MSE gain with ordinary/intraday and mean-calibration costs. Repeatedly used annual folds and fixed fitted/scalar bootstrap conditionals understate development/fitting uncertainty. One seed;4 years are not seeds/independent confirmation. Missing labels select certain stocks/periods. C3 F24 tail effective sessions30.69/32.96; maxq10.381, overnight top10/top1% moment5.643%/8.258%, finite/untrimmed but precision limited. No verified execution/auction/option profitability claim.

Coverage table nan in training denominator columns for selector/cal/OOS is N/A, not a nonfinite label/prediction; no auxiliary training normalization is fitted on those roles. Main raw/cal ranks match, so calibration did not invent cross-sectional information. Unresolved old intraday preference/deferred route remain untouched.

## 15. Human review decisions

Whether the.1104% point-MSE gain and small costs justify retaining C-A beside CLOCK-C3; no general replacement declared. No authorization follows for alpha/kappa/head/seed changes, C-B, S2-D, event-assisted models, Stage2 alternate targets, trading or protected confirmation. Original C all20 BLOCKED and D BLOCKED records preserved; only this prospective C-A amendment ran.

## 16. Next steps

Review main report/tables and stop. Keep C-A a provisional near-tie candidate only; keep CLOCK-C3 reference. Researcher decides any next separate protocol. No continuation queue or pending fit exists.

## 17. Artifact inventory

All newly created result files below; small metadata/CSV/MD intended for review/tracking later, checkpoints/Parquets local ignored. No source copies or dashboard changes. New output about3.94MB (capacity2.5GB), process peak846.2MB (capacity2GB), project12.44GB (capacity15GB). Runtime4078.55s describes this machine/run, not a future promise.

| New path | Type | Bytes | Purpose / invariant |
| --- | --- | --- | --- |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/.gitignore` | metadata | 15 | Run log or local large-artifact ignore policy |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F21/aux_refit_normalization.json` | .json | 210 | Phase-global masked overnight mass/session denominator; no batch normalization |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F21/auxiliary_diagnostics.csv` | .csv | 9212 | Signed component post-fit diagnostics on genuine supported cells only |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F21/calibration_coefficients.csv` | .csv | 779 | Independent Oct–Dec own residual factors, effective sessions and concentration |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F21/calibration_scores.parquet` | .parquet | 96484 | Own frozen main predictions/targets/keys/weights for paired replay; local, ignored |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F21/oos_scores.parquet` | .parquet | 676726 | Own frozen main predictions/targets/keys/weights for paired replay; local, ignored |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F21/phases.json` | .json | 538 | Own phase scale/cutoff and identical existing recipe references |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F21/restricted_final.pt` | .pt | 29963 | Own September selected model; local, ignored; no old checkpoint copied |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F21/result.json` | .json | 548 | Completed frozen-model/checkpoint/reload/optimizer/run identity receipt |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F21/selection.json` | .json | 558 | Qualified epoch/raw minimum receipt; no outer selection |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F21/training.csv` | .csv | 2963 | Per-epoch main/aux diagnostics, clipping and timing |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F22/aux_refit_normalization.json` | .json | 210 | Phase-global masked overnight mass/session denominator; no batch normalization |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F22/auxiliary_diagnostics.csv` | .csv | 9227 | Signed component post-fit diagnostics on genuine supported cells only |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F22/calibration_coefficients.csv` | .csv | 776 | Independent Oct–Dec own residual factors, effective sessions and concentration |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F22/calibration_scores.parquet` | .parquet | 84326 | Own frozen main predictions/targets/keys/weights for paired replay; local, ignored |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F22/oos_scores.parquet` | .parquet | 834346 | Own frozen main predictions/targets/keys/weights for paired replay; local, ignored |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F22/phases.json` | .json | 536 | Own phase scale/cutoff and identical existing recipe references |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F22/restricted_final.pt` | .pt | 29963 | Own September selected model; local, ignored; no old checkpoint copied |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F22/result.json` | .json | 550 | Completed frozen-model/checkpoint/reload/optimizer/run identity receipt |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F22/selection.json` | .json | 545 | Qualified epoch/raw minimum receipt; no outer selection |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F22/training.csv` | .csv | 4048 | Per-epoch main/aux diagnostics, clipping and timing |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F23/aux_refit_normalization.json` | .json | 195 | Phase-global masked overnight mass/session denominator; no batch normalization |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F23/auxiliary_diagnostics.csv` | .csv | 9220 | Signed component post-fit diagnostics on genuine supported cells only |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F23/calibration_coefficients.csv` | .csv | 780 | Independent Oct–Dec own residual factors, effective sessions and concentration |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F23/calibration_scores.parquet` | .parquet | 88590 | Own frozen main predictions/targets/keys/weights for paired replay; local, ignored |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F23/oos_scores.parquet` | .parquet | 629667 | Own frozen main predictions/targets/keys/weights for paired replay; local, ignored |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F23/phases.json` | .json | 536 | Own phase scale/cutoff and identical existing recipe references |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F23/restricted_final.pt` | .pt | 29963 | Own September selected model; local, ignored; no old checkpoint copied |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F23/result.json` | .json | 550 | Completed frozen-model/checkpoint/reload/optimizer/run identity receipt |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F23/selection.json` | .json | 560 | Qualified epoch/raw minimum receipt; no outer selection |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F23/training.csv` | .csv | 5932 | Per-epoch main/aux diagnostics, clipping and timing |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F24/aux_refit_normalization.json` | .json | 195 | Phase-global masked overnight mass/session denominator; no batch normalization |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F24/auxiliary_diagnostics.csv` | .csv | 9201 | Signed component post-fit diagnostics on genuine supported cells only |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F24/calibration_coefficients.csv` | .csv | 777 | Independent Oct–Dec own residual factors, effective sessions and concentration |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F24/calibration_scores.parquet` | .parquet | 58367 | Own frozen main predictions/targets/keys/weights for paired replay; local, ignored |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F24/oos_scores.parquet` | .parquet | 702834 | Own frozen main predictions/targets/keys/weights for paired replay; local, ignored |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F24/phases.json` | .json | 534 | Own phase scale/cutoff and identical existing recipe references |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F24/restricted_final.pt` | .pt | 29963 | Own September selected model; local, ignored; no old checkpoint copied |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F24/result.json` | .json | 548 | Completed frozen-model/checkpoint/reload/optimizer/run identity receipt |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F24/selection.json` | .json | 557 | Qualified epoch/raw minimum receipt; no outer selection |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F24/training.csv` | .csv | 4873 | Per-epoch main/aux diagnostics, clipping and timing |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/S2C_CA_PREFLIGHT.json` | .json | 8258 | Frozen scientific/source/chronology/count contract |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/S2C_CA_PROTOCOL.json` | .json | 4306 | Frozen scientific/source/chronology/count contract |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/S2C_CA_REPORT.md` | .md | 40662 | Human scientific report/interpretation; no new performance population |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/auxiliary_coverage.csv` | .csv | 1387 | Frozen scientific/source/chronology/count contract |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/auxiliary_diagnostics.csv` | .csv | 33880 | Signed component post-fit diagnostics on genuine supported cells only |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/calibration_coefficients.csv` | .csv | 2614 | Independent Oct–Dec own residual factors, effective sessions and concentration |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/event_retrieval.csv` | .csv | 12867 | Proper-score/ranking, conditional or paired dependent-time aggregate table |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/execution.log` | .log | 7721 | Run log or local large-artifact ignore policy |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/final_checks.json` | .json | 1248 | Fit, source, preflight/static, replay or resource verification; no extra model |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/fit_summary.csv` | .csv | 1214 | Fit, source, preflight/static, replay or resource verification; no extra model |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/groups.csv` | .csv | 387787 | Proper-score/ranking, conditional or paired dependent-time aggregate table |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/integrity_checks.json` | .json | 1444 | Fit, source, preflight/static, replay or resource verification; no extra model |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/interpretation.json` | .json | 4754 | Human scientific report/interpretation; no new performance population |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/metrics.csv` | .csv | 48024 | Proper-score/ranking, conditional or paired dependent-time aggregate table |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/neural_starts.jsonl` | .jsonl | 5632 | Neural pair append-only lifecycle journal; includes all attempted starts |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/paired_mse.csv` | .csv | 8532 | Proper-score/ranking, conditional or paired dependent-time aggregate table |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/phase_parity.json` | .json | 2538 | Fit, source, preflight/static, replay or resource verification; no extra model |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/readiness.json` | .json | 819 | Fit, source, preflight/static, replay or resource verification; no extra model |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/source_formula_checks.json` | .json | 274 | Fit, source, preflight/static, replay or resource verification; no extra model |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/source_validity.json` | .json | 489 | Fit, source, preflight/static, replay or resource verification; no extra model |
| `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/verification.json` | .json | 483 | Fit, source, preflight/static, replay or resource verification; no extra model |
