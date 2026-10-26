# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-26T12:56:45.943349-04:00 (America/New_York).
- Contributor/session: Codex, S1/S2 saved-score visualization and S4-A opening correction/preflight.
- Submitted task: reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/submitted_instruction.txt; latest user instruction requires automatic 09:30 re-audit and inclusion when supported.
- Branch: feat/track-a-data-intake.
- Starting/ending commit: 87d8ef1b6878f6750a17d5325e44c968415fe9ce; no commits.
- Start: clean, upstream0/0. End: pyproject.toml package-data declaration plus new task source/tests/scripts/reports; no research registry changes.
- No issue/PR, index mutation, branch creation, push or merge.

## 2. Executive summary

Historical S1/S2 visualization is complete and verified:31 accepted model-fold outputs /193,980 scored stock rows, all four years, actual baseline and neural identities, failed F21 PW and deferred LP preserved. Offline interactive dashboard has24 panels and four static rank-trajectory figures.

The opening re-audit supports **seven candidate daily origins**, including09:30→13:30 on normal sessions, with genuine minute OPEN and assumed09:32 issuance. Publication latency remains unverified. All48 inputs precede the opening and exclude the unfinished current hour. Every fold retains >50 validation sessions. Exactly8 S4 lifecycles are prepared and **NOT_RUN**, pending the original task's one consolidated SHA-bound live-fit response. Ledger stays106/200.

Eight full zero-update workflow rehearsals passed:32 role exports and4,560,960 stock rows with exact checkpoint reloads, zero optimizer calls, zero new recipe fits, zero neural starts. Peak source/rehearsal RSS1,025,327,104bytes. The final32-panel S4 viewer passed category/role/multistock browser checks using a clearly untrained saved snapshot.24 deterministic tests and487-file static checking passed with0errors/0warnings.

## 3. Research/protocol impact

No empirical model fit or old scientific result changed. Proposed S4 expands seven origin slots at the same240 actual RTH-minute horizon, preservingFT16/48steps/20stocks/folds/objectives/model/optimizer/selector. Source-backed09:30 addition corrects an overly strict extra first-minute latency rule; old six-origin draft remains preserved. Opening price is a target reference only, not an added input. Expanded M2 uses the original historical-session-start lock and20/60 support rules, with seven context-specific historical signals and proposed equal1/7 phase fitting; old morning contexts and archived recipes remain unchanged. No new horizon, S4B, seed, architecture, trading mapping or confirmation access. No protected2026 file opens or hashes; no2025 tuning. P2 handoff/register hash verification was completed earlier in this session; no inherited scientific HOLD is cleared.

## 4. Files created

Reusable new files:

| path | type | purpose |
| --- | --- | --- |
| scripts/render_hf20_rankings.py | .py | Render local Plotly HTML with an already installed Chromium; never installs a browser. |
| scripts/render_hf20_s4.py | .py | Existing Chromium only: offline S4 filter QA and one PNG for each actual saved run. |
| src/lstm_data/hf20_rank_visual_html.py | .py | Small self-contained Plotly viewer for authentic saved ranking diagnostics. |
| src/lstm_data/hf20_rank_visual_report.py | .py | Compact, complete index and interpretation of archived S1/S2 visual diagnostics. |
| src/lstm_data/hf20_rank_visual_template.html | .html | Offline browser template / explicit visual QA component |
| src/lstm_data/hf20_rank_visuals.py | .py | Offline, saved-score S1/S2 ranking views; no model fitting or source-price reads. |
| src/lstm_data/hf20_s4_authority.py | .py | S4 live authority, resource checks and strict sequential append-only journal. |
| src/lstm_data/hf20_s4_clock.py | .py | S4 source-only trading-minute clock; no fitting or protected-price access. |
| src/lstm_data/hf20_s4_closeout.py | .py | Saved-score S4 per-run and collective closeout; never fits or decodes protected sources. |
| src/lstm_data/hf20_s4_data.py | .py | S4 seven-context adapter with explicit prefix authority and unchanged16 channels. |
| src/lstm_data/hf20_s4_diagnostics.py | .py | S4 role exports, independent reconciliation and complete cohort supplements. |
| src/lstm_data/hf20_s4_epoch.py | .py | S4 frozen session-batch training arithmetic; zero-update mode supports rehearsal. |
| src/lstm_data/hf20_s4_fit.py | .py | Proposed S4 prefix recipe: original formulas, seven equally weighted M2 contexts. |
| src/lstm_data/hf20_s4_opening.py | .py | Source-backed opening-reference audit; latency remains a disclosed research proxy. |
| src/lstm_data/hf20_s4_preflight.py | .py | Bounded S4 endpoint, input and M2 audit. No fitting interface or optimizer. |
| src/lstm_data/hf20_s4_prepare.py | .py | Seal a reviewable S4 proposal only after read-only gates; never grants fit permission. |
| src/lstm_data/hf20_s4_rehearsal.py | .py | Zero optimizer-call S4 checkpoint/export/gate rehearsal with archived prefix recipes. |
| src/lstm_data/hf20_s4_run.py | .py | Exactly eight prospectively authorized S4 neural lifecycles, with strict PASS gates. |
| src/lstm_data/hf20_s4_visual_qa.js | .js | Offline browser template / explicit visual QA component |
| src/lstm_data/hf20_s4_visual_supplement.js | .js | Offline browser template / explicit visual QA component |
| src/lstm_data/hf20_s4_visuals.py | .py | One offline S4 dashboard with separate, traceable views for every saved run. |
| src/lstm_data/hf20_s4_witnesses.py | .py | Independent real-candle checks for S4's unchanged channels and expanded M2. |
| tests/test_hf20_s4_readonly.py | .py | Independent clock, missing-price, display-rank and no-IO boundary oracles. |


The full report-tree path/type/byte/SHA/Git-intent inventory is reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/artifact_inventory.csv. It includes all source audits, counts, witnesses, role/slot populations, manifests, test/static receipts, HTML/PNG/CSV outputs, preserved earlier attempts, untrained preview and proposal documents. Historical old diagnostic files are exhaustively mapped in HISTORICAL_COMPLETE_DIAGNOSTIC_FILE_INDEX.csv. This session report is an additional new Markdown artifact and is copied as WORK_SESSION_REPORT.md.

## 5. Files modified

Only previously tracked change: pyproject.toml declares the packaged HTML and two JavaScript assets, so installed/cloned execution can find its offline templates. No dependency was added. New untracked files were iterated within this session. All original S1–S3 models, checkpoints, outcomes, configs and ledger entries remain untouched.

## 6. Files deleted, renamed, or moved

No existing user/scientific/raw file was deleted, moved or compressed. Normal temporary-directory cleanup removed only declared untrained rehearsal scratch. A completed untrained snapshot was explicitly retained for browser and supplemental checks; its copied-file hashes are recorded. This is not storage-cap bypass or deletion of fitted artifacts.

## 7. Critical interfaces and invariants

- hf20_rank_visuals.historical(out): exact saved-score joins, display rank21−ascending midrank, canonical20-stock identity, independent IC and cohort reconciliation; no fitting.
- hf20_s4_clock.endpoint(origin, calendar, minutes=240): actual RTH-minute counting, including closing stub and calendar closures; missing endpoints never shifted. month_guard rejects pre-July2010 and post-December2024 before file I/O.
- hf20_s4_preflight.load_source(out): verify only174hourly+174minute partitions through2024; recreate established action/volume masks without opening mixed protected-year numeric files. Existing source-read receipt must match exactly before reuse.
- expanded_m2: same context, historical input-session-start maturity lock, scheduled20/60 windows and existing support; missing latest overnight history stays missing. Original morning contexts reconcile.
- S4Data / assemble: original48shifted full-hour steps×16channels; separate input eligibility and label validity; inner/refit recipes isolated. No call to protected-source-hashing parent constructor.
- fit_expanded: original train-only recipe formulas with disclosed seven-context equal weighting; default denies fitting, and S4Data.phase requires exact live authority first.
- authority.authorize/event/validate/resources: exact8IDs, SHA-bound proposal/code/evidence, append-only charged starts and failure preservation; next start requires immutable previous numerical+visual PASS; explicit resource checks. No journalv22 exists yet.
- run.neural_one: original NR/T2R losses, strict RankIC selector, fresh same-seed selected-epoch refit; actual dropout-ON and complete-population OFF metrics, gradient/clipping/update telemetry, checkpoint bindings and reloads.
- diagnostics.verify/join_components: exact role/stock keys, complete20 panels, weights, IC/objective/cohort conservation and genuine return-component identity. Missing intermediate close remains unavailable, not zero.
- visuals.build and closeout: additive32-panel run-filtered dashboard plus each run's complete file report and collective identical-key baseline/archive comparisons. No fallback predictions for failed/absent runs. Browser rendering uses an existing local Chromium with external DNS resolution blocked.

## 8. Data/schema/provenance changes

No acquisition, raw mutation, source migration or duplicate bulk minute stores. New private source-key/component tables record origin/issue/exit/maturity, context/category, source eligibility, genuine price references and optional close/open legs. Source is pinned HF1M776328445b7ac6e7815ef3a483e9c8ded1eb6d56 under P019B/P020. Timestamps retain UTC keys with explicit America/New_York display. Source document says minute START. Adjustment/dividend/action-vintage and bounded local-use qualifications remain inherited, not independently certified.

3,062/3,650 sessions have complete20 opening references;2,101 opening origins pass structural/source eligibility. Validation support F21–24 is120/92/86/87sessions; every slot has≥41origins. All role/slot retention and overlapping exclusion reasons are in S4_FOLD_ROLE_SLOT_COUNTS.csv. OOS retained candidates are roughly51–67%; seven candidate slots do not mean seven valid observations per day.

## 9. Dependency/environment changes

None. Existing .venv Python/NumPy/pandas/PyTorch/PyArrow/Plotly/calendar environment;CPU4/1,0workers. No tabulate dependency: report generation uses the repository's existing Markdown formatter after a preflight detected pandas' optional-tabulate absence. Existing installed Chrome provides PNG/browser QA; no browser/package installation. No .env or credential reads, no market downloads. Shell/static editor-extension paths are verification tooling only; execution code has no developer username paths.

## 10. Commands and tests run

- Initial git status/branch/HEAD/remotes/fetch inspected. Fetch initially hit sandbox FETCH_HEAD restriction, then authorized escalation succeeded; upstream0/0. No pull/integration over local work.
- `.venv/bin/python -m lstm_data.hf20_rank_visuals --out reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation` — genuine historical export/reconciliation; final receipt PASS.
- `.venv/bin/python scripts/render_hf20_rankings.py --out reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation` —4PNG and offline filter QA PASS. All four static figures visually inspected; F21 PW/LP absence checks explicit.
- `.venv/bin/python -u -m lstm_data.hf20_s4_preflight --out reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/opening_reaudit_v2 --rehearse` — exit0;8workflows,0optimizer calls/recipe fits/starts;48.06minutes including source/scalar checks, full role double prediction/reloads and diagnostics. This is a structural rehearsal with archived prefix recipes, not a fitted S4 campaign.
- `.venv/bin/python -m pytest tests/test_hf20_s4_readonly.py -q` —24passed,10.44s (tests_final.txt). Synthetic strict-qualification test corrected to use the exact computed IEEE floating-point boundary; selector/tolerance unchanged.
- `.venv/bin/ruff check .` —All checks passed (ruff_final_v2.txt).
- `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist` —487project-owned files,0errors,0warnings,170.005s (static_check_final_v2.txt). No suppressions/exclusions/severity changes. Editor verification remains human: select .venv/bin/python, restart Pylance, refresh Problems; editor confirmation is not asserted.
- `.venv/bin/python scripts/render_hf20_s4.py --out reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/untrained_visual_preview_v1` —PASS;6category filters,4roles,multistock,20-row heatmap and reversed rank axis; current32-panel viewer visually inspected. All actual numbers in this snapshot are explicitly untrained, excluded from research comparisons.
- Supplemental current-code matched baseline/block interval, full4role reconciliation/cohorts, per-run report and genuine component join over17,740OOSstock rows passed;9,978supported component rows conserved returns. These supplement the earlier core8-workflow rehearsal; later additions were read-only reports/joins/UI and authority hardening, not training arithmetic.
- S4run/preflight/prepare CLIs --help pass. git diff --check passes. No complete training regression suite or new optimizer update was run.

Earlier source/read-only/static failures and their logs remain preserved; final gates resolve them. Nonfatal Arrow sandbox sysctl/NEON probe warnings occurred. No empirical error was silently retried or refunded because no empirical start occurred.

## 11. Experiment/results summary

No new empirical experiment. Historical equal-year daily RankIC: N1/M1≈0.0117255,T2R≈0.0076733,NR≈0.0023695,LR≈0.0060425,P≈0.0006351; N0undefined. These saved exploratory results remain weak and do not establish tradeable edge. F21PWfailed andLPdeferred are not filled in; PW has no full4year aggregate. S3h2T2R aligned-M2 delta+0.015958 has descriptive interval[−0.000770,0.029417], including zero, and is only separately labeled context.

S4 all8statusesNOT_RUN. No trainedS4 predictive, trading, tail or aggregate conclusion exists. Required future per-run and collective outputs are implemented and indexed; the NOT_RUN report explicitly identifies what is absent.

## 12. Reproduction instructions

Use documented repository .venv, permitted pinned source cache and existing saved S1/S2 exports; no new credentials. Use new output directories for reproduction. Run historical CLI, existing-Chromium renderer, then hf20_rank_visual_report.report(out). Copy the reviewed S4_SOURCE_POLICY.json into a new audit directory and run hf20_s4_preflight --out that_directory --rehearse. Run the24focused tests and full static/Ruff checks above. Rehearsal never fits new scalers or updates weights.

The live executor is `.venv/bin/python -u -m lstm_data.hf20_s4_run --out reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation` **only after an actual exact live response is recorded and verified**. Do not rerun a populated/charged campaign. Later all-eight browser review uses render_hf20_s4.py and saved outputs only. Do not substitute copied untrained recipes/scores for fitted outputs.

## 13. Git / collaboration status

Branch/HEAD unchanged, upstream0/0; initial remote fetch succeeded. No staging/commit/push. The new source/configuration assets, tests, scripts, compact audits and this report are uncommitted. Bulk keyed scores/checkpoints/HTML and private price witnesses are ignored/local. Future authorized commit guidance: review pyproject and listed small implementation/tests/reports, exclude private scientific stores/raw data/large HTML, include session report, then a named-branch PR; no automatic publication. Preserve local task files before any integration. Likely conflict surfaces: package-data declaration and future S4 modules/registry work.

## 14. Known issues, risks, and limitations

The only current fit blocker is the original task's required consolidated live authority. New S4 resource caps are proposed2.5GBtask/15GBproject/2GBRAM; S3-only resource permission was not silently inherited. Preparation remains below1GBtask/10GBproject and measured2GBprocessRAM. Actual retained source population varies by slot/year and conditions results. Publication latency/auction identity/action vintage/rights/survivor conditioning remain qualified. Browser QA uses one untrained representative S4 component view; each actual model's saved numerical/visual payload gate and final all-eight browser review remain required after fitting. Final editor Problems refresh is human-confirmed. No failing final automated tests/static diagnostics remain.

## 15. Decisions requiring human or teammate review

One consolidated exact8start live-fit response, including8Pfits/8prefixrecipes and explicitS4resource caps, per original Authorization boundary and active registry. No separate09:30source approval is needed. ProposalSHA256 971765111037fb649a7c5319e4a260223301a9bc8a80ce8621fe29e7061349f0; executionSHA256 a737c9219513ddbbfffb882a2e76af7708e2f3ee55a297e1b145790bc47f2a95. Review S4_LIVE_FIT_APPROVAL_REQUEST.md. No other research decisions/experiments are authorized.

## 16. Next recommended steps

Review the historical dashboard/full diagnostic index and opening audit. On an exact live response, preserve its text and hashes, verify all evidence, then execute8fold-majorNR→T2Rlifecycles with stage gates and resource checks. Preserve any failed start; no implicit retry. Complete all8individual reports, saved-score dashboard/PNGs, matched baseline/archive/category comparisons and final verification; keep2026closed. Without approval, leave the ledger106/200 and all8NOT_RUN.

## 17. Artifact inventory

artifact_inventory.csv and DIAGNOSTIC_FILE_INDEX.csv cover every current-task artifact and implementation file with path, type, purpose, bytes, SHA256 and local/commit intent. HISTORICAL_COMPLETE_DIAGNOSTIC_FILE_INDEX.csv separately maps all original S1/S2diagnostic/analysis artifacts. Major entrypoints: README.md; historical HTML/report/PNGs; opening_reaudit_v2/09:30audit and allrolecounts; S4clockaudit; eight-startNOT_RUNindex; sealedcard/readiness; untrainedbrowserrehearsal; exacttests/staticlogs; this session report. Inventories do not self-hash. No new fitted checkpoint or model store exists.
