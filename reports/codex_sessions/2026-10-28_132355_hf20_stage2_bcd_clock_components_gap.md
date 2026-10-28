# Codex Session Report

## 1. Session metadata

- Date/session: 28 October 2026, separately gated Stage2 S2-B/S2-C/S2-D.
- Task: common feasibility/budget preflight, then at most one fixed train/refit pair per task/year; three independent reports, no pooled targets or deferred route.
- Branch: `feat/track-a-data-intake`; starting/ending SHA `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42`, no commit.
- Starting tree: existing modified current registry, untracked supplied handoffs and all earlier research code/tests/reports. Preserved; no pull/integration over local work.
- Fetch succeeded; branch0 ahead/0 behind. No commit/push/merge/rebase/stash/deletion.

## 2. Executive summary

**PARTIAL overall: S2-B COMPLETE4/4; S2-C and S2-D BLOCKED before fitting.** The separate reports and combined handoff are in `reports/experiments/hf20_s9_mag_stage2_bcd_2026-10-28/`.

S2-B calibrated clock-aware raw MSE **0.000106665945886** is **0.5232% below frozen C3**, with lower annual point MSE in all four years. Descriptive paired delta−5.609962e−7,95% month interval[−1.008116e−6,−1.824438e−7]. MAE falls0.6460%; within-origin magnitude IC rises.324668→.330254. Ordinary-period accuracy improves, but realized-tail MSE worsens slightly. Retain only provisionally as an exploratory package; do not infer isolated information/capacity/calibration causality or universal intraday preference.

S2-C lacks complete genuine components on112/95/116/137 original OOS overnight origins by year. S2-D has only31/48 selector sessions in F22/F23 versus the predeclared50 minimum, also failing monthly coverage. Neither is a negative fitted-model result; no auxiliary/gap model, gap baseline, gap scale or gap threshold was fitted.

The authorized cumulative ceiling increased **200→300**, preserving the opening154 starts and all histories. Only4 feasible pairs/8 phases ran, ending **158/300**. No failures/retries, extra variants, seed, source acquisition or protected access. Final10 tests and full510-file basic static check pass.

## 3. Research/protocol impact

Three separate frozen estimands/designs were prepared before numerical endpoint/source proof and before fits:

- B: original240-trading-minute absolute endpoint magnitude, same complete20-stock S4/S9 keys; ten known schedule values concatenate to dropped final H32 hidden state before its scalar M head. New head42→1 adds10 parameters (6,433→6,443), recurrent inputs remain48×16. Main transformed-MSE selection, fresh September refit, own reserved-tail C3 IO calibration withκ25; raw diagnostic. This is one input/head/learning package, not a feature-set sweep.
- C: same original4h main target, planned three signed auxiliary heads and fixed.10 auxiliary loss; source completeness gate fails. No actual auxiliary network was instantiated/trained and no partial-label rescue was used.
- D: a new normal-session15:30 forecast of genuine16:00-close-to-next09:30-open gap magnitude, one origin/session, new next-open+2min maturity. Coverage gate fails; no4h scale/predictor was reused as a gap model.

All old FT16/source/target definitions, stock axis, labels/indices, weights, optimizer/dropout/clip/shuffle/seed42 remain intact. No trade, options, jump classifier, alternate label, new architecture family or protected confirmation. The deferred C0-intraday/M1-overnight whole-panel experiment was not created; C0-vs-C3 intraday preference remains metric-dependent and unresolved.

## 4. Files created

- `src/lstm_data/hf20_stage2_bcd.py`: one isolated campaign CLI with common gates, prospective budget amendment, clock head, one B train/refit loop, saved-score reporting and separate blocked-task reports. Reuses native readers/FT16/recipes, optimizer, selector, calibration/rank/proper-score and month-block utilities.
- `tests/test_hf20_stage2_bcd.py`: five focused fixtures for clock/early-close values, head/trunk/reload parity, signed component identity, gap timing and budget-history preservation.
- New `reports/experiments/hf20_s9_mag_stage2_bcd_2026-10-28/`:61 files/about3.81MB plus final verification; separate `s2b_clock/`, `s2c_decomposition/`, `s2d_overnight_hold/`, common source/budget/plan/gate receipts and handoff.
- This mandatory handoff.

## 5. Files modified

Only existing `configs/CURRENT_EXPERIMENT_REGISTRY.json`: schema27→28 for the prospective ceiling amendment, then29 for the new journal/plan pointer. New ceiling300; counter154→158, failures included by unchanged counting convention. Previous pointer and journal hash are retained in the amendment; old budget200/journals remain immutable. The earlier registry diff was already present at entry.

No previous run, source, config/recipe, saved prediction/checkpoint/report, ledger entry, dashboard or dependency file changed.

## 6. Files deleted, renamed or moved

None.

## 7. Critical interfaces

- `budget_amendment(Path)`: writes one prospective human-authorized200→300 receipt and successor pointer, preserves the154 opening counter and previous journal bytes, keeps global `fit_permission=False`. The larger ceiling itself never authorizes fits.
- `protocol_specs` / `preflight`: freezes independent designs before label-source proof; derives all three role populations without fitting; records all20 genuine component/gap support, new gap maturity/embargo, resource/ledger scope. Protocols are independently fingerprinted by the common receipt.
- `clock_values(rows, calendar)`: seven nominal-slot one-hots, remaining scheduled current-session minutes/240, remaining<240 crossing flag, calendar days to next scheduled session/7. Ten float32 values, no fitting; metadata repeated across20 stocks only at the output head. Exact distinct combinations are logged in `clock_dictionary.csv`.
- `ClockMAG`: inherits original zero-state48-step encoder semantics; unchanged H32 LSTM/dropout.10, scalar42-input head. Default initialization keeps recurrent parameters exactly identical to the original seeded trunk. Metadata is not dropped and is never appended to the sequence.
- `source_validation`: existing adjusted/quarantine-filtered genuine minute-reference fields only; signed additivity and missing-close/open counts, no proxy/repair. No source rebuilding or price acquisition.
- `verify_before_fits`: original role/key/stock/weight/C3 metric identity, source/legal/ledger/cap checks. Both C/D must remain blocked in this executed campaign. Own eight phase recipes/scales reproduce before the first neural start.
- `train_clock` / `predict_clock`: original session batches/weighted transformed objective/AdamW/clip/shuffle, separate head metadata; dropout off for prediction, finite guards, no extra outputs or target leakage.
- `prepare_phases`: independently recomputes each phase's weighted-left-median raw-A scale and input-only FT16 recipe; exact predecessor equality is a verification, not cross-phase transfer. Saves new phase identities referencing identical original input recipes.
- `run_clock_fold`: one initial selector and fresh same-seed/empty-optimizer September refit; new own-tail C3 coefficients freeze before OOS; exact reload forecasts/unchanged frozen parameters. No retries or raw/cal variant selection on OOS.
- `journal`: four allowed B starts, one per selector/refit pair; new records use ceiling300, old journals retain their historical ceilings. C/D consume zero starts and cannot donate budget to extra B models.
- `report`: saved predictions only, complete four-year aggregate only after four valid folds; C/D remain separate gate reports. Reuses established weighted whole-month bootstrap400/seed22042.

## 8. Data/schema/provenance

Same174 existing adjusted-hourly partitions2010-07–2024-12 from the S4 read receipt. No minute-store reads, download, bulk source/feature copy or new provider. Source components/FT16 state are materialized only in memory using the original code; no canonical source is rewritten. All20 tensor names/order remain unchanged (VZ first).

S4 `S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet` stores genuine entry/exit, actual session-end reference, next-session minute open, direct return and signed pieces. Executed `hf20_s4_preflight.load_source/price_matrix` used adjusted, quarantine-filtered observed minute closes at session_close−1min and genuine09:30 minute opens, not15:30 substitutes/hourly proxies. Supported signed additivity error is at most4.250072516e−16 under atol1e−12/rtol1e−11. Individual valid cells do not supply missing all20 component panels. Missing opens dominate; representative missing-field keys are in `source_validation.json` and the C report. No auction/executable-fill validation is claimed.

B retains all80,260 rows/4,013 origins/793 sessions, original annual19,100/23,600/17,740/19,820 rows. D admissions are separately derived from normal15:30/input eligibility, genuine close/open all20, COP basis guard, next-open+2min maturity and original48-step embargo. F21 gap selector53 sessions differs from original4h15:30 count47, demonstrating that4h label admissions were not blindly reused. New gap selectors53/31/48/52; F22/F23 fail50 and monthly minimum5 (actual minima3/4). Gap OOS populations145/176/147/154 sessions all have12 months; none was scored with a fitted gap model.

No2025 market outcome or protected2026 observation, prediction, metric, feature or content hash is accessed. Calendar-only next-session dates extend into January2025 for known schedule metadata; this is not numerical market exploration. Labels remain price-only intervals beginning before approximate origin+2min issuance, not executable returns.

## 9. Dependencies/environment

No installation, package/lock/setup or environment change. Existing `.venv`, torch2.10.0 CPU float32, four intra-op/one inter-op threads, deterministic seed42. Known PyArrow sandbox CPU-cache sysctl EPERM warnings do not invalidate reads. No external network source; Git fetch only for required collaboration inspection.

## 10. Commands and checks

```sh
git status --short --branch
git branch --show-current
git rev-parse HEAD
git remote -v
git fetch --all --prune
git rev-list --left-right --count HEAD...@{upstream}
.venv/bin/python -m lstm_data.hf20_stage2_bcd --preflight
.venv/bin/ruff format src/lstm_data/hf20_stage2_bcd.py tests/test_hf20_stage2_bcd.py
.venv/bin/ruff check src/lstm_data/hf20_stage2_bcd.py tests/test_hf20_stage2_bcd.py --output-format concise
.venv/bin/python -m pytest tests/test_hf20_stage2_bcd.py tests/test_hf20_mag_c3_io.py -q
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist > /private/tmp/hf20_bcd_types_pre.json
.venv/bin/python -u -m lstm_data.hf20_stage2_bcd --run > reports/experiments/hf20_s9_mag_stage2_bcd_2026-10-28/execution.log 2>&1
.venv/bin/python -m lstm_data.hf20_stage2_bcd --report
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist > /private/tmp/hf20_bcd_types_final.json
git diff --check
```

Final10 focused tests pass (4.64s), Ruff passes, final full basic static **510 files/zero errors/zero warnings** (83.335s). Pre-fit final static also zero errors (110.62s). Initial7 type diagnostics from heterogeneous JSON assembly and Python sum's integer start were fixed using one complete receipt construction and explicit array addition; no Any/cast/ignore/exclusion/severity workaround or numerical design change. Formatting diagnostics were fixed before any fit. No empirical neural failure/retry occurred.

Fixtures prove actual early-close/regular clock values/weekend gap;6,443 parameters and seeded recurrent-trunk parity; stable shape/metadata guards/reloaded synthetic outputs; signed additivity versus nonadditivity of magnitudes; gap next-open maturity distinct from4h; prospective ceiling preservation on a temporary fake154 journal. Existing C3 fixtures cover residual/scale/decoder and session pooling. No optimizer step is run by the new synthetic tests. Empirical reload max error0 in every fold; no clamp rows; raw/cal ranks identical. Complete matched C3 metrics reproduce before fits. Single-closure geometry and one15:30 gap candidate per normal session pass.

Final numerical replay is byte-identical for14 frozen protocol/metric/journal files. Code/tests remain at pre-fit readiness hashes; all critical source/journal/protocol bindings pass. Full historical tests/mega-audit were not run.

Editor verification: select repository `.venv/bin/python`, keep Pylance basic, refresh Problems. The final actual editor refresh remains human-confirmed, not agent-verified.

## 11. Experiment/results summary

- B IDs: `HF20-S2B-F21-CLOCK-S42` through `F24`, own final checkpoints/score stores. Selected epochs8/13/11/16; selector stops18/23/21/26. Raw minimum20/23 differs from qualified11/16 in F23/F24; it was not silently substituted.
-136 epochs/21,020 optimizer updates/302 clipped batches; fit-lifecycle sum2,183.83s. Peak training process RSS978,681,856 bytes; output about3.81MB; project stays below15GB and task below2.5GB.
- Primary equal-year CLOCK-C3 MSE.000106665945886 vs C3 .000107226942123 (−.5232%), paired descriptive interval[−1.008116e−6,−1.824438e−7]. Annual changes−.9194%,−.5224%,−.0987%,−.5563%. F22/F23 annual intervals include zero.
- CLOCK-C3 improves full MAE.6460%, mean ratio1.02670→1.01376, IC.324668→.330254. Raw CLOCK-RAW MSE is−.4472% vs C0 overall, driven mainly by F24; earlier raw evidence is mixed. M1/B0-VOL full MSE changes−1.4783%/−4.3873%.
- Conditional intraday/overnight MSE changes−.5778%/−.5150% vs C3. Intraday annual directions are mixed; C0 still has lower intraday MAE than calibrated models, so no universal preference/route is chosen.
- Prefix95/99 full tail MSE worsens1.0232%/.7384%; ordinary complements improve3.2626%/1.2337%.15:30 MSE improves1.5749% but MAE worsens.9077%. No claim of new gap/jump discrimination.
- Eight own-tail factors are finite; sameκ25 fixed, no trimming/search. F24 n_eff30.69/32.96, overnight maxq10.2420, top10 moment5.6599%, top1%8.2789%; factor estimation remains uncertain.
- C/D: BLOCKED, zero fits/metrics/scales/baselines. No cross-task winner or invented aggregate.

## 12. Reproduction

Use the established environment and exact saved original source/role/score artifacts bound by receipts. `--report` is saved-score replay only, no model calls or raw hourly numerical reads. `--preflight` replays the frozen planning receipt after it exists. Started namespaces refuse `--run` via `NO_RETRY_STARTED_NAMESPACE`; do not delete guards, lower gates or reset ledger state. A fresh empirical reproduction needs separate live authorization/capacity and the same174 allowed source partitions/S4 contracts plus prior model scores; the increased ceiling alone is not fit authority. Foreground execution was monitored to completion; no job was detached.

## 13. Git/collaboration status

Same branch/SHA, fetched0/0 upstream. No commit/push/merge. New source/test/report namespace and this handoff remain untracked/reviewable; model/Parquet artifacts are intentionally ignored by the new namespace `.gitignore`. Old untracked work is preserved. Review the budget successor and new small artifacts together; do not blindly commit older local work. Only the current registry file is modified by this session; all prior journals/configs/reports remain unchanged.

## 14. Issues, risks and limitations

No known failing check or remaining B correctness blocker. Primary B evidence is small and post-search; intervals condition on selected fitted weights/scalars and repeated prior model/hypothesis choice, not independent confirmation. Four annual folds are not seeds. Input/head size/initialization/epoch selection and learning jointly change; no authorized ablation isolates each clock feature or capacity. Realized-tail errors and some clocks worsen; magnitude ordering is not signed alpha or option profitability. F24 calibration precision is limited. Existing vendor adjustment/execution timing limitations are preserved, not repaired.

D metadata clarification: initial common chronology references included archival4h scales/thresholds. Before fitting, append-only `s2d_overnight_hold/protocol_v2.json` removes those irrelevant fields and leaves gap scales/thresholds explicitly NOT_FITTED; `planning_receipt_v2.json` binds it. Previous versions remain intact, operative scientific definitions/minimums/source masks and BLOCKED result unchanged. No4h scale or label was used for a gap forecast. Old role NPZ binds calendar chronology/input provenance; actual gap counts use separately derived next-open maturity masks.

## 15. Decisions for researcher review

Whether to retain B as a provisional calibrated4h candidate despite small gains/tail costs. C needs a separate decision about missing genuine component coverage; no proxy or source expansion is authorized here. D needs a separate decision about its selector coverage/minimums; current gates cannot be retroactively lowered. Intraday C0-vs-C3 preference and deferred C0-intraday/M1-overnight route remain untouched. Editor Problems refresh is human-confirmed.

## 16. Next steps

Review the three independent reports and combined handoff, then stop. No automatic downstream experiment, routed mixture, source repair, confirmation release, seed/feature/architecture/calibration sweep or trade/options study.

## 17. Artifact inventory

All below live under the new combined namespace unless stated:

- `STAGE2_COMBINED_RESEARCH_HANDOFF.md`: short independent verdicts/no pooled winner, about5.8KB.
- `s2b_clock/S2B_CLOCK_REPORT.md`: full B scientific result, about24.6KB; `s2c_decomposition/S2C_DECOMPOSITION_REPORT.md`: source blocker about5.8KB; `s2d_overnight_hold/S2D_OVERNIGHT_HOLD_REPORT.md`: coverage blocker about4.6KB.
- `budget_amendment_300.json`, `source_policy.json`, `planning_receipt.json`/`planning_receipt_v2.json`, task protocols including D v2: immutable small prospective/versioned metadata. Old versions preserved.
- `component_coverage.csv`, `gap_coverage.csv`, `source_validation.json`, `clock_dictionary.csv`: compact source/clock/role evidence, no bulk source copy.
- B `metrics.csv`150 annual/EQ arm/scope rows, `groups.csv`1,155 aggregate rows, `paired_mse.csv`30 contrasts, `fit_summary.csv`4 rows, `calibration_coefficients.csv`8 rows.
- B per F21–F24: own `phases.json`, `selection.json`, `training.csv`, `result.json`, selected `restricted_final.pt`, new-only `calibration_scores.parquet`/`oos_scores.parquet`. No old predictor columns/checkpoint copies or unselected forecasts. PT/Parquet intentionally ignored/local.
- `execution_plan.json`, `readiness.json`, B `phase_parity.json`, `neural_starts.jsonl`, `continuation.json` (empty B queue/C&D blocked), `execution.log`, `interpretation.json`, `verification.json`: minimal resource/lifecycle/replay evidence.
- New module/test and this session handoff are untracked, no commit. No figure/dashboard/source cache is added.
