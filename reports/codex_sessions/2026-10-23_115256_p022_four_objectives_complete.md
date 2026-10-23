# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-23T11:52:56.821500-04:00.
- Contributor: Codex. Task: complete the explicitly approved P022 repair, exactly four starts H2/42→W1/42→E1/42→R1/42, sequential verification, collective diagnostics and existing-dashboard integration.
- Branch: `feat/track-a-data-intake`. Starting/ending HEAD: `3c41ec78c5aed8c69d4cc8fc6c3af9acf0072e38`. No commits or PR.
- Start: prior repair work dirty/untracked, preserved exactly. Existing modifications were the v10 current registry pointer and repaired executor; prior recovery module/test/script, v10 definition/journal/report were untracked. Upstream 0/0. End: those plus this continuation's new diagnostics/UI/config/journal/report changes. No index mutations.
- Exact live approval recorded in `reports/experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation/live_repair_approval.json`; proposal `188d34d737f4dae30dd7e4fb283e72c9be17442531d4dc5c81605e0473436068`, execution `3b30417eef1f6a475824dbd9830a39c147fb8fd9fa007150984136a6042bf255`.

## 2. Executive summary

**PASS_P022_COMPLETE. Ledger 41/200.** Four authorized starts 38–41 completed sequentially; failed start 37 remains charged and unchanged. Calibration/refit epochs: H2 12/1, W1 17/7, E1 16/6, R1 17/7. All phase/checkpoint/selector/input/telemetry checks passed before advancing. No additional fit, seed, combination, P&L or protected 2026 numeric access.

Read [ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation/P022_FINAL_HUMAN_REVIEW_v2.md](../experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation/P022_FINAL_HUMAN_REVIEW_v2.md), then collective diagnostics and objective-space attribution. R1 is essentially tied with saved T2/42; H2/W1 regressions do not improve. E1 improves rare-event ranking but ordinary probability calibration/log loss/Brier are worse. No automatic promotion.

The existing Streamlit app has a new P022 section with complete comparisons, objective/gradient/tail views, exact cases and genuine history/features. 76 relevant tests passed across sandbox/native validation, static checking has zero errors, and launcher smoke passed.

## 3. Research/protocol impact

Frozen HF1M source revision, 20 names/order, FT16/TG20, 48-step histories, dates/masks, train-only recipes, D6g selector and hyperparameters are unchanged. Exact approved fitting code stayed hash-identical for all four runs. The approved objective differences alone distinguish H2/W1/E1/R1. E1 uses class-weighted CE selection; other arms use original-TG20 validation MSE. Development is exploratory, never used to select epochs. Protected Jan–Mar 2026 remains locked. No original protocol gate or 10+3 backlog item was silently changed.

## 4. Files created

Reusable implementation:

- `src/lstm_data/objective_screen_verify.py`: read-only per-run checkpoint, selector, row-count, inverse/probability, telemetry and ledger verification CLI.
- `src/lstm_data/objective_screen_attribution.py`: actual float32 pointwise objectives, exact float64 R1 pair directions, independent NumPy pair allocation, ranked/range/magnitude cohorts, conservation and one-event feature excerpts.
- `src/lstm_data/objective_screen_diagnostics.py`: four-stage gate before development inference; exact matched four-role comparisons, fixed-prior E1 baselines, daily differences/block intervals, quality strata, checkpoint attribution and genuine source cases.
- `src/lstm_data/objective_screen_report.py`: separate regression/classification reports, each-arm training summaries, objective-space attribution and exact-candle annexes.
- `src/lstm_data/visualization/objective_screen.py`: checksum-bound reader, model/role/date guards before access, complete-population filtering and bounded-prefix feature decoding.
- `src/lstm_data/visualization/objective_screen_ui.py`: additive existing-app seven-view P022 interface.
- `tests/test_objective_screen_diagnostics.py`: five accounting/cohort/matched-population oracles.
- `tests/test_objective_screen_visualization.py`: protected-before-read tests, all real model/role populations, actual AppTest component routes and legacy navigation.

New metadata:

- `configs/track_a_candidate_experiment_registry_v11_p022_repair.json`, `reports/audit/track_a_real_pairs_v11_p022_repair.jsonl`: linked starts38–41, all completed; immutable predecessor v10 retains failed37.
- `configs/track_a_p022_visualization_v1.json`: private completed-study manifest binding.
- Within `reports/experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation`: live approval/granted gate; four run directories/logs/verification receipts; real stage03–08 receipts; legacy-config snapshot/update receipt; diagnostic v1 partial and v2 completed trees; v1/v2 viewer manifests; current human review/LATEST_REVIEW; scientific, test/type/smoke receipts; final inventory/closeout.
- Within `artifacts/hf20_hf1m_long_v1/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation`: four selected calibration/final refit checkpoints, three-role prediction exports and durable optimizer logs. No dense historical rolling-window duplication.
- This mandatory session report. Exact file-level inventory is `artifact_inventory_final.csv`; detailed numeric reports/model stores are intentionally ignored/private.

## 5. Files modified

- `apps/track_a_dashboard.py`: one new sidebar entry and guarded route; existing branches preserved.
- `configs/track_a_visualization_v1.json`: only the two existing app-reader SHA bindings updated; all numerical/result/scaler references independently compared unchanged.
- `configs/CURRENT_EXPERIMENT_REGISTRY.json`: authorized append-only successor pointer v10→v11, with false generic fit permission and exact live-plan/journal references. No free-standing future-fit authority.
- Prior uncommitted executor/recovery changes were preserved; no fitting-module byte changed during this continuation. New diagnostic/UI modules were iterated within scope.

## 6. Files deleted, renamed, or moved

None. Historical STOP/preapproval reports, original failed start, partial diagnostic output and initial failed UI receipts remain preserved. Temporary smoke server was started/stopped by the smoke tool; existing port8501 server was not touched.

## 7. Critical functions, classes, variables and config keys

- `verify(plan_path,run_id)`: reload exact checkpoint tensors, replay selector, reconcile unique epoch receipts/steps/prediction rows; records PASS before next start. Never calls optimizer.step.
- `allocations(frame,arm,recipe)`: exact session-normalized H2/W1/E1/R1 allocation; returns per-row population and R1 all190pair table. Pair signs use canonical float64 labels; point objectives match executor float32 arithmetic. Ordinary and objective weights are separately retained.
- `cohort_masks`/`cohort_table`: stable ranked tails, unique-origin MAD expansion, disjoint mechanisms, signs/complements, train-max anchored ranges. Fitting cutoffs remain frozen for validation/development.
- `exact_cases`: 48 input +4 outcome candles, all20 endpoint returns and 48×16 native/scaled features; independently reconstructs canonical TG20. Labels/outcome candles never enter inputs.
- `daily_scores`, `daily_classification`, `canonical`: complete20-name groups, equal daily aggregation, undefined ZERO rank/recall, exact baseline matching and CE/Brier differences.
- `Screen.discover/file/population/filtered`: config→manifest→artifact SHA chain; strict model/role/date denial before numeric access. `safe_features`: requested permitted prefix only.
- `panel`: actual P022 selectors and seven views, class/regression unit separation, protected query guard, original source history viewer reuse.
- Stage7 viewer manifest v2 maps logical optimization.csv to supplemented optimization_v2.csv; current stage7/stage8 gates end `_v2.json`. Historical v1 receipts remain traceable.

## 8. Data/schema/provenance changes

No source/model-input mutation. Raw HF revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`; P019B action QA and P020 FT16/TG20 remain canonical. Input contract hash `7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5` unchanged. All1701raw/derived files,1,446,901,820bytes verified by hash/size; protected files byte-hashed only.

Four role populations: 88560inner-train,15320inner-validation,104200refit,3660development rows. All16arm-role populations reconcile targets, cross-sectional medians/MADs and saved baselines. E1 has logits/probabilities/signed score; no fabricated return forecast. New private population schema includes coefficient/raw loss/ordinary weight/objective weight/point/pair/total/equivalent-row loss, source revision/QA and checkpoint identity. Existing schemas unchanged.

94exact cases =4888candles,72192feature cells,1880endpoint-return records. Final-refit cases include five each of AAPL/AMZN/TSLA/SBUX per arm plus E1/R1 exceptions. All52scheduled rows retained; unknown extrema/volume remain marked. No interpolation or new repairs.

## 9. Dependency/environment changes

None. Existing repository .venv, Torch/Pandas/NumPy/Plotly/Streamlit/Pytest. No .env/credential read, install or market-data download. Git fetch required authorized native execution because sandbox blocked .git/FETCH_HEAD. Local-port smoke/test similarly rerun natively after sandbox bind denial. No broad host access or publication.

## 10. Commands and tests run

- Startup Git status/branch/HEAD/remotes; `git fetch --all --prune` rerun natively after sandbox rejection; `git rev-list --left-right --count HEAD...@{upstream}`:0/0. AGENTS/latest relevant report read; P2 deferred-work hashes verified (16entries), statuses preserved.
- Exactly four sequential commands: `.venv/bin/python -u -m lstm_data.objective_screen_run --plan reports/experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation/experiment_design.json --approval reports/experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation/live_repair_approval.json --run-id HF1M-LONG-TM0-ARM-S42-DEV1`, replacing ARM with H2,W1,E1,R1 in that order. All exit0; stdout/stderr in each ARM_execution.log.
- After each: `.venv/bin/python -m lstm_data.objective_screen_verify --plan reports/experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation/experiment_design.json --run-id HF1M-LONG-TM0-ARM-S42-DEV1`: PASS, respective ledger38,39,40,41.
- `.venv/bin/python -u -m lstm_data.objective_screen_diagnostics --plan reports/experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation/experiment_design.json --out reports/experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation/collective_diagnostics_v2`: exit0,53.534s,809517056bytes peak RSS. Earlier collective_diagnostics_v1 stopped on a duplicate epsilon metadata argument during case export; partial output preserved, fixed by validating/reusing existing epsilon; no model rerun.
- `.venv/bin/python -m lstm_data.objective_screen_report --plan reports/experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation/experiment_design.json --out reports/experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation/collective_diagnostics_v2`: exit0. Researcher diagnosis appended, current report hashes bound by report_generation_receipt_v2.json.
- `.venv/bin/python -m pytest tests/test_objective_screen.py tests/test_objective_screen_recovery.py tests/test_objective_screen_diagnostics.py tests/test_objective_screen_visualization.py tests/test_hf1m_training.py tests/test_hf1m_long_visualization.py tests/test_controlled_visualization.py tests/test_visualization_readonly.py -q`:75passed, one local-port test sandbox-blocked,45.03s. Exact native rerun `.venv/bin/python -m pytest tests/test_visualization_readonly.py::test_bound_hash_change_and_local_port_selection -q`:1passed,1.07s. Thus all76relevant tests passed in permitted environments, no unresolved failure.
- Actual component suite `.venv/bin/python -m pytest tests/test_objective_screen_visualization.py -q`:3passed,7.07s separately. Initial E1 AP chart test failed due omitted scalar export columns; supplemented145rows from saved epochs into optimization_v2.csv, fixed generator, reran successfully. No new inference/fitting. Tests include all4model views, all7model×4role readers, full-population filtering, protected-before-read denial, real history/features and legacy navigation.
- `.venv/bin/ruff check .`:all passed. `git diff --check`:pass; diff/status reviewed.
- `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist`:331files,0errors,0warnings,42.486s final. Earlier pandas typing/optional-selection issues were corrected without suppressions, exclusions, broad Any or severity changes. Final receipt `final_types.json`.
- `./scripts/run_track_a_dashboard.sh --check`:PASS901bound dependencies. `./scripts/run_track_a_dashboard.sh --smoke`:sandbox local-port denial, then native PASS127.0.0.1:8502; health200/HTML200,1.539s startup, cleanSIGINT/serverexit0. Existing8501preserved. Parsed native receipt launcher_smoke_receipt.json; original prefaced stdout retained separately.
- Final independent source hash, exact16role target/median/MAD, selected checkpoint metric, baseline population, frozen code, ledger and legacy binding checks:PASS (`final_scientific_verification.json`).
- Arrow sandbox sysctl probe warnings and AppTest bare-script context warnings were benign. No full100minute repo suite run.
- Editor verification: select `.venv/bin/python`, restart Pylance, refresh Problems and confirm zero project-owned errors. CLI parity passed; final editor UI state is human-confirmed, not asserted.

## 11. Experiment/results summary

Four completed seed42 arms;13,723optimizer steps,718.073s combined fitting, max622,641,152bytes fitRSS;58,566,464bytes per-run artifacts. No additional optimizer steps in diagnostics. Ledger41/200 includes prior failed37 (316steps preserved separately).

Development original MSE/dailyIC: H2 3.111709/.054480; W1 3.108253/.050782; R1 3.106240/.074718; savedT2/42 3.106560/.075559; savedT2/123 3.114912/.025493; ZERO3.116560/undefined. R1's tiny MSE advantage and slight IC deterioration have paired intervals including0; no clear regression gain. H2/W1 are worse. E1 ANYAP.131678 vs prior.041514; weightedCE.423936 vs.538091, but ordinaryCE difference+.033419 and summedBrier+.021074; signedIC−.003713. Mean rare probabilities overstate observed frequencies. Event ranking is promising but calibration/direction are weak.

Final-refit top-|y|1/5% loss shares: H2 4.687958/18.440103%; W1 11.063187/38.014677%; E1 11.891304/73.538661%; R1 5.885965/20.354964%. Objective units differ; not a predictive-performance ranking. Both .99/.95 train-max magnitude ranges contain one row. R1 point/pair/total allocation conserves; training and final-checkpoint loss contexts are separate. Fixed400replicate seed22042 calendar-month CIs with2month sensitivity remain exploratory.

## 12. Reproduction instructions

Use documented .venv and lawfully provisioned exact pinned local P020/P021/P022 artifacts; no new credentials. For inspection launch `./scripts/run_track_a_dashboard.sh` and choose the P022 section. The click guide enumerates actual selectors. Config/manifests use project-relative paths; missing or changed evidence fails closed with no fallback.

For read-only regeneration after the four successful runs, invoke objective_screen_diagnostics and objective_screen_report commands above with a NEW output directory. Current code emits the complete scalar optimization table directly; the existing release preserves the append-only v2 supplement. Verify file hashes before rebinding a new view manifest. Do not rerun the fitting CLI: its terminal-state guard rejects extra starts. Replication/retraining requires new authorization. Exact approved model outputs are private artifacts, not assumed available in a clean public clone; no clean-machine final-submission rehearsal or data-sharing right is asserted.

## 13. Git / collaboration status

Same branch/HEAD, upstream0/0 after fetch; no staging/commit/push/merge/rebase. Current tracked diffs: prior executor repair, current registry pointer, additive dashboard route and two legacy-reader hashes. New files include prior repair work plus this turn's6source/UI modules,2tests,v11metadata,new viewer config and session report. Numeric stores/reports remain ignored.

Future separately authorized commit guidance: review exact new code/tests/configs and both session reports; keep registry definition/journal/pointer consistent. Do not force-add raw prices, checkpoints or derived stores. A portable metadata/data handoff requires existing rights review and all referenced artifacts; do not commit dangling private paths as a public release. Likely conflict surfaces: app route, viewer config and current registry pointer.

## 14. Known issues, risks and limitations

No unresolved test/type/runtime defect. Initial read-only diagnostic and plotting-export defects were corrected with preserved evidence; no fit repeated. One seed per new model,109development sessions, correlated stocks/overlapping labels and few month blocks; no confirmatory alpha inference. Conditional rights/publication/action-vintage, volume/proxy/fallback and retrospective survivorship remain. E1 weighted CE improvement does not imply ordinary calibration. Constant prior top4 ties follow canonical order; chance AP uses observed prevalence. All numerical outputs remain private/local.

Original13-direction improvement backlog list/path was not found, despite references; its existing content was not changed and no replacement list was invented. Final editor refresh and clean-machine submission rehearsal remain human/future work. Total storage about2.98GB, current continuation roughly333MB additional, under10GBtotal/1GBadditional limits; final inventory has exact file bytes. No live trading/confirmation access.

## 15. Decisions requiring human or teammate review

No approval required to conclude this authorized package. If further work is desired, E1 is the most informative separately authorized seed123 replication for event ranking/calibration; R1 is secondary for a near-zero regression difference. No automatic promotion. No additional seeds/combinations/null fitting/walk-forward retuning/confirmation unlock/trading/Git publication is authorized. Provide the authoritative10+3list when available for a faithful future summary.

## 16. Next recommended steps

Read the final human review and collective/tail reports; inspect all four arms in the dashboard. Assess E1 ranking versus poor calibration and R1 versus baseline uncertainty before choosing any new package. Preserve every failed/approved/completed ledger entry and prior baseline. Refresh Pylance Problems manually.

## 17. Artifact inventory

`reports/experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation/artifact_inventory_final.csv` lists task-owned code/config/journal/report files, all four run artifacts, both diagnostic namespaces, exact cases and receipts with size/SHA and local/review intent. Includes prior repair artifacts for a complete package handoff; does not self-hash. `closeout_receipt_final.json` separately binds this report, inventory, final review, stage7/8gates and exact ledger/state. Numeric data, logits/checkpoints/candles/features, partial diagnostics and detailed reports are ignored/private. No new standalone app, dense historical window archive, public data export or trading output exists.
