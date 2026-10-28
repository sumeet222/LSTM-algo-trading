# Codex Session Report

## 1. Session metadata

- Date: 27 October 2026, America/New_York; draft created 21:33:31 EDT.
- Contributor/session: Codex; HF20 S9-MAG Stage 1 Session 2 Design A.
- Requested: bounded restricted-history MAG selection/refit, independent C1a/M1 calibration, four stronger B0 controls; preflight before fitting and stop ineligible folds.
- Branch: `feat/track-a-data-intake`.
- Starting/ending commit: `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42`; no commit authorized or created.
- Start: tracked tree clean, existing untracked FT16/replication documents, Consolidation handoffs and Session 1 package/report. The user supplied the research menu under `docs/track_a` during this session; it is preserved as user-supplied work.
- Remote fetched, 0 ahead / 0 behind; no pull/merge/rebase/stash/staging/push/PR.
- Final state: F21 completed; F22–F24 blocked before fitting. Current registry pointer modified intentionally; new helper/test/compact outputs/report uncommitted. Scores/checkpoints ignored locally. Earlier user/Session1 work preserved.

## 2. Executive summary

Design A preflight admits only F21. Its selector has 57 eligible sessions / 349 origins and its independent calibration tail 56 sessions / 283 origins. F22–F24 selectors have only 35/38/47 sessions and one or more slots below 25 origins. They are blocked without fitting; no sufficiency threshold or calendar role was relaxed.

The helper and four correctness fixtures pass. Full-project prefit static check: 500 files, zero errors/warnings. F21 completed with selected epoch29, selector stop39, fresh restricted refit29. C1a raw OOS MSE fell6.89%, M1 fell7.46%, versus matched C0; MAE rose5.89%/4.78%, ordinary-period MSE worsened, and tail levels remain far too small. Scientific conclusion MIXED; operational status PARTIAL. No four-year equal-year result can be reported while three folds are unavailable.

## 3. Research/protocol impact

New, explicitly user-approved Design A chronology: fit/inner recipe through June; select epochs July–September; fresh encoder/recipe/target scale through September; independent October–December scalar calibration using that exact fixed encoder; original following-year OOS keys. Same FT16/48-step/20-stock axis, h4 endpoint labels, initialization, optimizer, MAG objective, weights and selector. No O1–O7/C1b/C1c/C2 flexible/C3/overnight-jump head or new data source.

Authorized B0: prefix raw stock mean/median, stock×clock means shrunk by fixed 50 origin-equivalent observations, and one pooled ridge with stock/clock indicators and standardized log decoded V2. Ridge penalties 0.001/0.1/10, July–September raw-MSE selection and September refit. Continuous feature normalization is phase-prefix only. Independent-tail c/k do not use OOS outcomes.

P2 handoff read and 16 register entries verified with `load_deferred_work`; no P2 status/gate closure or register amendment. Old source/publication/action/survivor/price-only execution qualifications persist. No 2025 observations/diagnostics or protected 2026 numerical/hash access. Post-search exploratory evidence only.

## 4. Files created

- `src/lstm_data/hf20_mag_designa.py`: isolated executable preflight, guarded permitted hourly-source adapter, original MAG lifecycle, two scalar maps, bounded B0 controls, saved-score metrics/reporting. No acquisition or minute-source loader.
- `tests/test_hf20_mag_designa.py`: four independent fixtures for strict maturity/embargo, input-only prefix fitting, scalar formulas/unclamped residuals, and unpenalized ridge intercept.
- `reports/experiments/hf20_s9_mag_stage1_session2_designa_2026-10-27/`: immutable design, preflight, 20-role count CSV and execution outputs, enumerated in final main report.
- This session report.

## 5. Files modified

Only tracked file modified: `configs/CURRENT_EXPERIMENT_REGISTRY.json` advances to schema24 and the new Session2 design/journal. Its old value is retained in immutable `session2_design.json`; predecessor v23 journal hash is unchanged. Last new status COMPLETED, global count131/200: one pair/two neural phase fits. No old registry definition, history, source artifact, prediction, index, recipe, dashboard or report modified. The new namespace `.gitignore` excludes only private `*.parquet`/`*.pt` outputs.

## 6. Files deleted, renamed, or moved

None. No prior work discarded.

## 7. Critical functions/classes/configuration

All implementation below is in `hf20_mag_designa.py`:

- `role_mask(rows, first, start, stop, embargo)`: frozen eligible mask, strict label maturity before ET cutoff+1day−4h, and first-of-48 input date strictly after previous cutoff. No output writes.
- `preflight(out)`: computes five roles per fold from saved S4 eligibility and P020 hourly-grid metadata; verifies original inner/OOS key equality; checks selector ≥50 sessions/≥25 origins per slot. Tail coverage is disclosed separately without inventing a new numerical calibration minimum. Writes compact own-namespace design/count receipts, no fitting.
- `source_components(grid, rows)`: reads only 174 hourly partitions listed in the already executed pre-2025 S4 read receipt; uses existing `build`, `field_masks`, `expanded_m2` and saved endpoint returns. No minute store, parent-wide future manifest/hash verification or bulk source copy. Verifies grid identity and historical V2 parity before a start.
- `feature_fit_hours(...)`: union of input-only eligible history keys clipped to phase stop, independent of future-label eligibility/values. Uses existing `fit_expanded` for new September scalers/floors. Original June recipe/scale reused only after exact inner population and scale checks.
- `View`, `epoch`, `predict`: original 48×16 assembly, per-session batches and MAG kernel; seed42+n session shuffle, original dropout/optimizer/selector; no per-weight/per-batch instrumentation. Forward states reset per window. Eval dropout off. Same September model frozen across calibration and OOS, exact checkpoint reload checked.
- `factors`, `decode`: global weighted exp(M−Mhat), using unconstrained Mhat; and nonnegative raw-MSE scalar k. No trimming. Exponential contribution concentration reported; invalid denominators/nonfinite values fail closed.
- `ridge_fit`, `baseline_fit`, `baseline_predict`: single bounded linear competitor plus raw-functional constants. Ridge objective uses normalized weighted MSE plus lambda times nonintercept squared coefficients; log-sigma normalization fitted on matching phase prefix. Stock/clock reference categories and actual selected penalty saved.
- `event`: append-only successor pair journal, old journal/plan identity binding, 130 prior starts, ceiling200, no retry. One selection/fresh-refit lifecycle is one ledger pair and two neural phase fits.
- `metrics`, `rank_metrics`, `report`: original hierarchical weights; conditional role mass for subgroup errors; true within-origin magnitude IC; fractional boundary-tie top/bottom4 retrieval and half-credit predicted ties for pair concordance; existing whole-month bootstrap seed22042/400 draws. No signed-return/trading interpretation.

## 8. Data/schema/provenance

Original source artifacts unchanged. New role-count metadata and, for completed folds, compact calibration/OOS tables reuse canonical origin/ticker keys. One columnar OOS store carries the seven arm forecasts; no separate per-arm duplicate Parquets. New September recipe/scale records are isolated. Calibration labels mature before December cutoff; October–December labels are excluded from neural/feature/target/baseline fitting and epoch selection.

Explicit source roots: S4 `opening_reaudit_v2` eligibility/endpoints/read receipt; P020 contract's grid projected to timestamp/date fields through2024; saved original S9 configuration/June recipe and prefix validation V2; original adjusted hourly paths in the S4 permitted read receipt. No unrestricted source glob, no protected contents/hashes, no acquisition or source rewrite.

## 9. Dependencies/environment

No new dependencies, packages, environment variables, network source access or secrets. Existing repository `.venv`, CPU PyTorch, NumPy/pandas/PyArrow and matching Pylance stubs. Four CPU intra-op threads, one inter-op thread, float32 neural updates and original float64 score exports. No GPU/AMP/backend change.

## 10. Commands/tests

Repository inspection: `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD`, `git remote -v`, `git fetch --all --prune`, `git rev-list --left-right --count HEAD...@{upstream}`. Successful fetch; 0/0.

P2: `.venv/bin/python -B` invocation of `load_deferred_work(Path('configs/track_a_p2_engineering_handoff_v1.json'))`: 16 verified entries; no scientific status changed.

```bash
.venv/bin/python -m lstm_data.hf20_mag_designa --preflight
.venv/bin/python -m lstm_data.hf20_mag_designa --help
.venv/bin/python -m pytest tests/test_hf20_mag_designa.py -q
.venv/bin/ruff check src/lstm_data/hf20_mag_designa.py tests/test_hf20_mag_designa.py --output-format concise
```

Preflight/key checks and CLI passed. Four tests passed (final prefit run 3.34s). Ruff passed. Initial development typing issues were fixed by explicit numerical result types and a vectorized daily weighted reduction; no diagnostic suppression or weakened tests.

Exact static check:

```bash
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist > /private/tmp/s9_mag_session2_types_ready.json
```

500 project-owned files, 0 errors / 0 warnings, 93.853s, exit0, basic profile with repository interpreter and matching installed Pylance stubs. This absolute path is local verification tooling, not a runtime path dependency. Final editor refresh remains human-confirmed: select repository `.venv/bin/python`, restart Pylance, refresh Problems, confirm zero project-owned errors.

Authorized fitting command:

```bash
.venv/bin/python -u -m lstm_data.hf20_mag_designa --run > reports/experiments/hf20_s9_mag_stage1_session2_designa_2026-10-27/execution.log 2>&1
```

Fitting command exit0; one admitted pair completed with no failed start/retry.39 selector epochs +29 refit epochs; initial132 and refit136 optimizer steps per epoch,9,092 actual updates total. Actual lifecycle1072.426s, peak RSS1,244,594,176bytes. Original F21 benchmark was2521.918s for its different37+27 lifecycle; rough preflight phase-count projection for120 maximum epochs was~4729s, not a promise. A20MB artifact reserve fit within existing2.5GB task/15GB project/2GB RAM caps; initial project12,413,581,596bytes. Actual namespace1,587,576bytes at final report replay.

Saved-only `--report` replay exited0 and left ten critical metric/design/protocol/score/model/recipe/coefficient identities unchanged. The immutable final protocol was not rewritten. Independent saved-calibration arithmetic reproduced c/k and all three OOS decoders at atol1e−14/rtol1e−13; exact20-stock keys, equal-session weight sums, finite/positive forecasts passed. Previous journal hash matched its successor binding; final global starts131. Report formatting/interpretation was refined after fitting; numerical fitting/scoring/metric definitions were unchanged.

Final focused pytest:4 passed in4.87s; Ruff passed. Final completion static check: **500 files, 0 errors / 0 warnings**,59.969s, exit0:

```bash
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist > /private/tmp/s9_mag_session2_types_completion.json
```

A report-presentation edit initially produced14 diagnostics from seven pandas Scalar→float conversions; these were fixed by explicit real-valued array extraction plus a finite/single-element assertion. No numerical definition, fit, checkpoint or forecast changed. The successful final saved-output replay left all ten preserved identities unchanged and main-report bytes29,758. No exclusions, ignores, casts or severity reductions. Human editor verification instructions above remain applicable.

Nonfatal PyArrow sandbox CPU-cache/neon sysctl warnings are retained in the log; all permitted Parquet reads and calculations completed. No sandbox escalation/install was needed. Runtime versions: torch2.10.0, NumPy2.5.3, pandas3.0.6.

## 11. Experiment/results

Only F21 admitted; F22/F23/F24 blocked before neural/baseline fitting or new OOS metrics. F21 has11,449 inner origins/2,100 sessions; selector349/57; restricted refit11,846/2,164; independent calibration283/56 (5,660rows); original OOS955/188 (19,100rows).

| Arm | Raw MSE | Raw MAE | Mean predicted/realized ratio |
| --- | --- | --- | --- |
| C0 | 0.00009054111419 | 0.006104297201 | 0.7691488233 |
| C1a | 0.00008430316562 | 0.006463772715 | 1.049986423 |
| M1 raw multiplier | 0.00008379067054 | 0.006396317672 | 1.041321211 |
| B0-RMEAN | 0.00009634216226 | 0.006787098054 | 0.9497308568 |
| B0-RMED | 0.0001089726542 | 0.006576385997 | 0.6426438748 |
| B0-CLOCK | 0.00008873383723 | 0.006441366538 | 0.9495225582 |
| B0-VOL | 0.00008653592101 | 0.006608992445 | 1.046544813 |

C1a−C0 raw MSE −6.237948566e−6, descriptive95% month-block interval[−1.056991457e−5,−3.177538653e−6]. M1−C0 −6.750443655e−6 [−1.121125100e−5,−3.538970388e−6]. C1a−B0VOL interval includes zero; C1a−M1 is slightly positive. No special smearing/Jensen advantage established.

Restricted target scale0.005848759193156053 (September30); prefix95/99 cutoffs0.029152683601565685/0.055591859892280306. Fitted c1.20559953878307, k1.3538618008487935; ridge penalty0.001 chosen on July–September. Largest weighted exponential row0.203%, ten rows1.503%, top1%5.653%; finite and not dominated by a handful. Across-fold factor stability unavailable.

Original Mhat transformed MSE0.22555554398316285 is unchanged across C0/C1a/M1. All magnitude rankings unchanged (IC0.3178584114), no MAG negative-output/clamp/tie/constant mass. B0-VOL clamps144 rows to zero and has small pair ties. C1a overnight MSE improves9.66%, but intraday worsens3.04%, ordinary≤prefix95 worsens10.98%, and prefix95/99 mean ratios remain0.373/0.235.15:30 ratio remains0.869. No tail-jump or signed alpha claim.

One pair/two neural fits; nine bounded non-neural coefficient fits: three grouped controls, three ridge candidates plus refit, two scalar maps. New September feature/target/threshold statistics are recorded separately. June feature/target parameters reused only after exact membership/scale/V2 parity checks.

No four-fold equal-year average is available. CI interpretation remains exploratory, temporal block descriptive, not multiple-testing-adjusted confirmation. No P&L, signal or options claim.

## 12. Reproduction

Use existing README setup and legitimately available private S4/S9 hourly/source archives. No new download/credentials. The preflight command is safe only before a new lifecycle; completed starts are single-use and cannot be retried through `--run`. Saved-only reporting:

```bash
.venv/bin/python -m lstm_data.hf20_mag_designa --report
```

This reads the new saved forecasts/coefficient records and regenerates compact tables/report without fitting. Do not rerun the old campaign or invent a new output directory to evade no-retry accounting. Any continuation for blocked folds needs an explicit chronology amendment, not revised hyperparameters chosen on OOS.

## 13. Git/collaboration

Preserve initial untracked documents and Session1 work; no pull/merge/rebase over this work. New source/test/results and this report remain uncommitted. Current-pointer successor, if started, is intentional accounting and must travel with its new journal/design. No old history changes or automatic publication.

After review, exact optional commit guidance (not executed):

```bash
git switch -c exp/hf20-mag-designa
git add -- src/lstm_data/hf20_mag_designa.py tests/test_hf20_mag_designa.py configs/CURRENT_EXPERIMENT_REGISTRY.json reports/experiments/hf20_s9_mag_stage1_session2_designa_2026-10-27 reports/codex_sessions/2026-10-27_213331_hf20_s9_mag_session2_designa.md
git commit -m "Add bounded S9 MAG Design A calibration evidence"
git fetch --all --prune
git push -u origin exp/hf20-mag-designa
```

Review explicit compact public metadata/code separately from private scores/checkpoints; do not accidentally add bulk private artifacts. No source-data publication is implied.

## 14. Issues/limitations

- Original July–September sufficiency gates block three years. No four-year success/negative conclusion can be claimed from a single admitted year.
- F23/F24 calibration tails have only48/40 sessions; these are explicit coverage flags, not a newly invented hard50 requirement. F24 also has sparse slots. Any revised design must settle this coverage question prospectively.
- The menu became available at the user-supplied `docs/track_a` path and was read; its former absence is resolved without altering Session1 reports.
- Global c/k cannot create missing jump information or signed alpha. A corrected mean may retain major tail/overnight shortfalls.
- Existing price-only, publication/action vintage, survivor/source-access qualifications persist. Protected2026 remains closed.
- No remaining numerical/runtime failure. Final static receipt and editor refresh are documented separately; final Git diff/status reviewed. No four-fold completion or confirmation certification.

## 15. Human decisions

For blocked folds, the latest monthly-start extension satisfying selector coverage is May–September for F22 (58 sessions/min36 per slot), June–September for F23 (59/min38), June–September for F24 (69/min31), with initial training ending the preceding month. These are **metadata-only unapproved alternatives**, not executed designs. A common uniform revision may be preferable; never silently apply fold-specific shifts. Independent October–December coverage still needs interpretation.

Researcher must review completed F21 evidence and choose whether to authorize a revised chronology or stop. No O1/Stage2/C3 or other follow-on is automatically launched.

## 16. Next steps

F21 completed and preserved. Stop after this handoff. Researcher and ChatGPT must decide any blocked-fold chronology amendment or Session3 objective work; no further fitting or release follows.

## 17. Artifact inventory

Main report: `reports/experiments/hf20_s9_mag_stage1_session2_designa_2026-10-27/S9_MAG_STAGE1_SESSION2_B0_C1_DESIGNA_REPORT.md`.

Namespace inventory (20 files,1,587,576bytes; all new):

| File | Bytes | Git intent |
| --- | --- | --- |
| `.gitignore` | 15 | Compact metadata |
| `session2_design.json` | 3529 | Immutable prefit design |
| `preflight.json` | 2634 | Compact gate/availability receipt |
| `session2_role_counts.csv` | 2888 | Twenty role populations |
| `session2_protocol.json` | 7473 | Immutable final protocol/result identities |
| `session2_metrics.csv` | 2353 | Seven annual arm rows |
| `session2_groups.csv` | 28483 | 161 stratum/decile/cohort rows |
| `neural_starts.jsonl` | 2778 | Successor ledger, preserve with pointer |
| `execution.log` | 3327 | Intentionally local/ignored |
| `S9_MAG_STAGE1_SESSION2_B0_C1_DESIGNA_REPORT.md` | 29758 | Main researcher review |
| `F21/training.csv` | 3310 | 68 compact epoch rows |
| `F21/selection.json` | 206 | Selected epoch and June scale |
| `F21/restricted_recipe.json` | 151549 | New September FT16 recipe |
| `F21/restricted_target.json` | 147 | New scale/prefix95/99 |
| `F21/coefficients.json` | 7109 | Scalars and bounded B0 coefficients |
| `F21/result.json` | 662 | Completion, frozen network, reload/RAM/time |
| `F21/selected_initial.pt` | 28865 | Intentionally local/ignored |
| `F21/restricted_final.pt` | 28865 | Intentionally local/ignored |
| `F21/calibration_scores.parquet` | 252538 | Private fitting-pair lineage, ignored |
| `F21/oos_scores.parquet` | 1031087 | One private seven-arm keyed store, ignored |

No blocked-fold checkpoint/score or duplicate source data generated. Main report records the numerical group paths and exact source roots. Outside the namespace: source helper63,028bytes, new test2,809bytes, plus this mandatory handoff. Final git diff/status verified; this report appears untracked. No staging/commit/push or follow-on fit.

Source/helper/test/report metadata are new uncommitted review artifacts. Raw datasets, old predictions/models/recipes/ledgers and dashboards remain unchanged. Temporary `/private/tmp/s9_mag_session2_types_*.json` receipts are intentionally local and not runtime dependencies.
