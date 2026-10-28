# Codex Session Report

## 1. Session metadata

- Date/session: 27–28 October 2026, HF20 S9-MAG Stage 1 / Session 2B.
- Task: complete the approved Design A calibration study using a coverage-only selector amendment; reuse F21, fit F22–F24 once.
- Branch: `feat/track-a-data-intake`.
- Starting SHA: `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42`.
- No commit/push authorized or performed.
- Initial tree: dirty registry pointer plus untracked Session 1/2 code, tests, outputs and supplied documents; all preserved. Fetch succeeded; branch matched upstream (0 ahead/0 behind).

## 2. Executive summary

**COMPLETE execution / MIXED scientific result.** F21 reused exactly; F22–F24 completed once. All 80,260 original rows / 4,013 origins / 793 sessions match. Equal-year C1a/M1 raw MSE improves 5.72%/5.68% versus C0, but MAE worsens 4.90%/5.95%. Global amplitude correction remains a benchmark, not a full conditional calibration solution. No subsequent objective was started.

## 3. Research/protocol impact

Only approved change: test July, June, May selector starts and choose the latest meeting at least 50 sessions and 25 origins per clock, using eligible coverage only. F21 July; F22 May; F23/F24 June. Initial recipes/scales move to the preceding permitted session. September refit, independent October–December calibration, original OOS keys, target, model, seed, optimizer, loss, weights and B0 definitions stay fixed. No final confirmation, 2025/2026 numerical access, trading or new objective.

## 4. Files created

- `src/lstm_data/hf20_mag_designa_continue.py`: versioned preflight, successor ledger, original fold runner calls and saved-score reporting entry point.
- `tests/test_hf20_mag_designa_continue.py`: coverage-rule, chronology and equal-year dependent-bootstrap fixtures.
- `reports/experiments/hf20_s9_mag_stage1_session2b_fourfold_2026-10-27/`: additive evidence namespace; detailed inventory below and in main report.
- This report.

## 5. Files modified

- `src/lstm_data/hf20_mag_designa.py`: optional explicitly earlier initial recipe/scale and successor journal callbacks; enforce existing dominated-exponential invalid status before OOS. No numerical trainer/scorer/baseline kernel change. Exact old source retained in successor namespace as text; critical parent artifacts and kernels bound in `parent_bindings.json`.
- `configs/CURRENT_EXPERIMENT_REGISTRY.json`: only current append-only successor pointer, after charged starts. Parent journals unchanged.

## 6. Files deleted, renamed or moved

None.

## 7. Critical interfaces

- `choose_candidate(list[dict]) -> dict`: July→June→May, counts only; fail rather than extending into April.
- `preflight(Path)`: all-four chronology/key/source/resource gate; preserves historical F21 artifacts and score population.
- `run_fold(..., initial=(recipe, scale), journal=callback)`: reuse historical fitting path with genuinely earlier initial recipes.
- `bootstrap_equal_year(dict[int, Series]) -> dict`: four-year arithmetic mean of independently month-resampled annual session means, 400 draws/seed 22042; rejects missing years.
- `postfit_report(Path)`: reads saved scores, replays factors/decoders/key weights, copies original F21 annual values unchanged and produces compact summaries.

## 8. Data/schema/provenance

Uses only the 174 already-pinned adjusted hourly partitions dated 2010-07 through 2024-12 in the saved S4 permitted-read receipt, saved S4 eligibility/endpoint labels and exact original S9 outer keys. No minute-source acquisition/reconstruction or bulk store duplication. New initial/refit recipes are separate. Stock axis remains the saved tensor order, including VZ first. `A=abs(log(P_endpoint/P_origin))`, four trading hours; timing remains price-only before approximate origin+2min issuance. Calibration forecasts come from the exact frozen September encoder used next year.

## 9. Dependencies/environment

No installation, package changes or new dependencies. Repository `.venv`, CPU PyTorch 2.10.0. PyArrow prints sandbox CPU-cache-query warnings; these do not change decoded values or prevent successful reads.

## 10. Commands and checks

```sh
git status --short --branch
git branch --show-current
git rev-parse HEAD
git remote -v
git fetch --all --prune
.venv/bin/python -m lstm_data.hf20_mag_designa_continue --preflight
.venv/bin/python -m pytest tests/test_hf20_mag_designa.py tests/test_hf20_mag_designa_continue.py -q
.venv/bin/ruff check src/lstm_data/hf20_mag_designa.py src/lstm_data/hf20_mag_designa_continue.py tests/test_hf20_mag_designa_continue.py --output-format concise
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist > /private/tmp/s9_mag_session2b_types_complete.json
.venv/bin/python -u -m lstm_data.hf20_mag_designa_continue --run > reports/experiments/hf20_s9_mag_stage1_session2b_fourfold_2026-10-27/execution.log 2>&1
```

Pre-fit: eight tests passed; Ruff passed; full project basic parity check 502 files, zero errors/warnings. Initial static attempt found six new-module typing errors, all corrected before fitting without weakened severity/ignores. Final snapshot: 502 files, zero errors and warnings (65.609 seconds); eight focused tests pass (2.85 seconds); Ruff and git diff --check pass. Editor: select `.venv/bin/python`, use Pylance basic and refresh Problems; actual editor refresh/zero Problems remains human-confirmed, not agent-verified.

## 11. Experiment/results

All four valid folds complete. C1a annual raw-MSE changes versus C0: −6.89%, −6.49%, −4.75%, −4.55%; M1: −7.46%, −5.76%, −5.00%, −4.73%. Equal-year raw MSE: C0 0.000114783568; C1a 0.000108218653; M1 0.0001082663992. C1a−M1 descriptive paired interval includes zero. Both beat B0-VOL equal-year MSE by about 3%; B0-CLOCK slightly beats both in F23.

Mean ratios C0/C1a/M1: 0.779/1.018/1.053. Equal-year MAE: 0.00649745/0.00681593/0.00688398. Overnight MSE improves in all years, but prefix-95 ordinary-complement MSE worsens in every year (+13.37%/+23.87% equal-year). Prefix-95 event ratios remain only 0.351/0.376. Within-origin IC remains 0.324668 for all three; exact rank vectors are unchanged, with no negative-Mhat OOS rows or corrected zeros.

Selected epochs 29/27/22/15 (F21 reused). All ridge choices 0.001. Three new pairs / six neural phases / 158 epochs; actual new pair lifecycles total 2,538.35 seconds (preparation/report time excluded). New process peak RSS 1,165,688,832 bytes, below 2GB; old F21 peak is 1,244,594,176. Ledger 131→134/200, no failed/aborted attempt, empty continuation queue. No four-year average was emitted until all four were valid.

See main report and compact CSVs for full precision, all controls, clocks/tails, reliability, 400-draw month-block uncertainty and coefficients. All results exploratory/post-search; no selection-adjusted significance or trading interpretation.

## 12. Reproduction

On the documented environment with pinned local source and historical S4/S9 artifacts, replay saved evidence only:

```sh
.venv/bin/python -m lstm_data.hf20_mag_designa_continue --report
```

`--run` is single-use and refuses an already charged successor lifecycle; no instruction here authorizes rerunning fits. Immutable `amendment.json` binds the inherited numerical specification, coverage rule and uncertainty procedure; `preflight.json` binds all-four gate, source counts, resources and F21 disposition.

## 13. Git/collaboration

No integration over the dirty tree. Registry schema24 at session start advances to schema25; the HEAD diff also includes the preceding session’s schema23→24 change, which is not new work here. No commit, push, merge, stash, reset or discarded work. Final status/diff reviewed; preserve both pre-existing and current untracked source/reports before future integration. Intentionally local `.pt` and `.parquet` outputs ignored in the successor namespace. Small code/config/report artifacts need researcher review before a focused commit.

## 14. Issues/limitations

Calibration coverage 56/50/48/40 sessions; no binding selector 50/25 test applies to pooled scalar calibration. F24 has only 19 observations at its sparsest slot. All three pairs completed with no retry or changed parameter. Eight focused tests and source/key/decoder/reload checks pass; no known failing check remains after final static verification. Historical research years were already examined repeatedly. Fixed survivors, source vintage and non-executable price-proxy timing remain limitations.

## 15. Human decisions

Review completed four-year comparison before selecting another intervention. No authorization here for O1, C2/C3, new overnight heads, options or protected confirmation. Editor Problems refresh requires human confirmation.

## 16. Next steps

Stop: Session 2B is complete. Researcher reviews the report and chooses the next question; M1 is the parsimonious scalar benchmark and a separately approved O1 is a reasonable next discussion. No automatic continuation, C3 or protected confirmation.

## 17. Artifact inventory

Successor root: `reports/experiments/hf20_s9_mag_stage1_session2b_fourfold_2026-10-27/`.

- Small reviewable files: amendment/preflight/parent bindings, old implementation text, role and candidate counts, fourfold metrics/groups, paired uncertainty, fit summaries, continuation manifest, execution log and new append-only ledger.
- New F22/F23/F24 only: initial/refit recipes and target scales/tails, selection/training trace, coefficients/results, selected/final checkpoints, compact keyed calibration/OOS scores. Checkpoints/Parquets intentionally local/ignored; no duplicated F21 outputs.
- Main scientific report: `S9_MAG_STAGE1_DESIGNA_FOURFOLD_COMPLETION_REPORT.md`.
- Final namespace is approximately 5.55MB (54 files including final receipt): six compressed Parquets about 3.89MB, six checkpoints 173KB, small phase/config/receipt JSONs, nine CSVs including three epoch traces, and one main report. F21 remains referenced from its parent. All new code/reports and the pre-existing untracked materials remain uncommitted; checkpoints/Parquets are intentionally ignored. No file was deleted or overwritten in the historical namespaces.

## Final verification receipts

- `integrity_checks.json`: PASS for all four folds: exact keys/weights/axis, phase recipe prefix-hour sets, saved-calibration/OOS decoder replay, exact rank vectors, parameter reload/hash, unchanged 16 parent artifacts and ten numerical kernels. No inference backfill or fit in verification.
- Full static completion receipt: `execution_receipt.json`, 502 files / zero errors and warnings. Saved-only report replay leaves all four aggregate CSVs byte-identical and rechecks bound parent files. Final report contains no pending placeholders.
- Post-fit report edits added diagnostic fields and interpretation only; no fitting code, numerical kernel, seed, split, hyperparameter or forecast was changed.
- Main report: `reports/experiments/hf20_s9_mag_stage1_session2b_fourfold_2026-10-27/S9_MAG_STAGE1_DESIGNA_FOURFOLD_COMPLETION_REPORT.md`.

### Generated file map

All paths below are inside the successor namespace, except the source/tests/session report and current registry named above. Generated files are small metadata unless marked intentionally local.

| Paths | Purpose |
| --- | --- |
| `.gitignore` | Ignore checkpoint/forecast stores, without excluding reviewable metadata |
| `amendment.json`, `preflight.json` | Immutable amended rule/inherited numerical specification and all-four admissibility/source/resource receipt |
| `parent_bindings.json`, `parent_implementation.py.txt` | Sixteen critical historical file bindings, ten unchanged kernels and exact historical helper source |
| `role_counts.csv`, `selector_candidates.csv` | Exact five-role dates/embargo/maturity/coverage and deterministic candidate counts |
| `fourfold_metrics.csv`, `fourfold_groups.csv` | Per-year/equal-year proper errors, rank scores, clocks/tails/reliability and same-key deltas |
| `paired_MSE.csv`, `fit_summary.csv` | Annual/equal-year dependent uncertainty and coefficients/epochs/scales/concentration/reload/resource facts |
| `review_interpretation.json` | Saved scientific narrative used by report-only replay; no parameter selection |
| `integrity_checks.json`, `execution_receipt.json` | Final correctness, static/test, code-binding, replay and execution/resource receipts |
| `execution.log`, `neural_starts.jsonl`, `continuation.json` | Minimal epoch log, append-only starts/phase states, completed/pending queue (empty) |
| `S9_MAG_STAGE1_DESIGNA_FOURFOLD_COMPLETION_REPORT.md` | Self-contained scientific handoff |
| `F{22,23,24}/initial_recipe.json`, `initial_target.json` | New earlier-prefix FT16 fitting keys/scalers and phase-specific target scale/cutoff |
| `F{22,23,24}/selection.json`, `training.csv` | Frozen selected epochs and compact selection/refit trace |
| `F{22,23,24}/restricted_recipe.json`, `restricted_target.json` | September-only FT16 recipe, scale and prefix 95/99 thresholds |
| `F{22,23,24}/coefficients.json`, `result.json` | Independent scalar/B0 parameters, lifecycle identity/runtime and reload evidence |
| `F{22,23,24}/selected_initial.pt`, `restricted_final.pt` | Six small checkpoints, intentionally local/ignored |
| `F{22,23,24}/calibration_scores.parquet`, `oos_scores.parquet` | Six compressed keyed forecast/label lineage stores; one OOS store per year for every arm, intentionally local/ignored |

### Commit/push guidance (not executed)

Review and deliberately stage only the listed code, tests and small metadata/reports, coordinating the pre-existing untracked Session 1/2 provenance first. Do not add the whole dirty tree or ignored forecast/checkpoint stores. After the researcher has reviewed and staged the intended files, the exact commands are:

```sh
git diff --cached --check
git diff --cached --stat
git commit -m "Complete HF20 Design A four-fold calibration study"
git fetch --all --prune
git status --short --branch
git push origin HEAD:feat/track-a-data-intake
```

Inspect divergence after fetching; do not force push, reset or integrate over unknown work. No command above was executed automatically. Ending HEAD remains the starting SHA; branch remains 0 ahead/0 behind the fetched upstream.
