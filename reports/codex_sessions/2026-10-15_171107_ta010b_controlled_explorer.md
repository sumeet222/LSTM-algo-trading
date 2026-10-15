# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-15T17:11:07.913029-04:00, America/New_York; started16:39ET.
- Contributor/session: Codex root; no subagents.
- Task: Package010B, extend existing read-only Streamlit/Plotly explorer for completed Package011 and Package012 inspection readiness.
- Branch: feat/track-a-data-intake.
- Starting/ending commit: 363fc4bf1e85b680e43dcddd1ad0f8df3a044007; no commit created.
- Starting tree: human modification only in docs/track_a/RandomNotes.md. It remains byte-identical to the starting census.
- Ending tree: dashboard/config/guide edits and new adapter/UI/tests/guide/audit/session files; exact status in reports/data_audit/ta010b_controlled_explorer_2026-10-15_164300/git_final.txt.
- Issue/PR: none. Fetch succeeded, upstream ahead/behind0/0; no integration over dirty work.

## 2. Executive summary

VISUALIZATION_ENGINEERING_PASS. Existing app extended with Controlled Experiments and an actual Feature Scaling Explorer. Original defaults and pages retained. Saved C0/H1/T1/T2/O1 comparisons separate TM0 architecture, treatment, seed and units. Exact target/population/parameter/clock/mask checks precede comparisons. All60 saved partition panels reconcile; independent equal-day MSE and rank calculations match20 development panels within1e−12. Four registered training populations match exact hashes. Historical batch gaps remain explicit PARTIAL, without synthetic histories. Ledger24/40 unchanged.

## 3. Research/protocol impact

No research definition or scientific execution changed: target/horizon, universe, features, loss policies, optimizer, clip caps, splits, seeds, scalers/floors, forecast outputs, trading/costs and confirmation protocol remain immutable. No fitting, model inference, new resampling, source requests, replay or registry transition. Read P2 handoff, verified16 entries via load_deferred_work; statuses unchanged. Read frozen roadmap/design and conditional candidate/hourly-proxy API context. Package012 remains unimplemented and unstarted. Future target values are hindsight labels only. Source rights/clock/universe/actions remain qualified researcher-attested assumptions; no new certification or gate promotion.

## 4. Files created

- src/lstm_data/visualization/controlled.py — read-only Study adapter, exact joins, immutable parameter/population checks, paired metrics, event state and48-step input inspection.
- src/lstm_data/visualization/controlled_ui.py — five controlled-study views and shared single canonical-store cache.
- tests/test_controlled_visualization.py — fabricated scientific oracles, local saved-data reconciliation and actual AppTest event navigation.
- docs/track_a/HOW_TO_VISUALLY_INSPECT_PACKAGE_011.md — beginner walkthrough with verified event/run, missingness and Package012 evidence boundary.
- reports/data_audit/ta010b_controlled_explorer_2026-10-15_164300/ — bindings, chart oracles, availability table, UI/HTTP/test/static evidence, preservation and review card; artifact_inventory.csv enumerates every file.
- reports/codex_sessions/2026-10-15_171107_ta010b_controlled_explorer.md — this mandatory handoff.

## 5. Files modified

- apps/track_a_dashboard.py — additive sidebar section and Start Here entry, feature explorer expander, complete navigation state and corrected displayed24/40 ledger. Original price/prediction/diagnostic/provenance logic preserved; old/new views share the same canonical-store cache.
- configs/track_a_visualization_v1.json — additive sealed-study reference and new reader/cache identity refs; old source/result/recipe/checkpoint refs preserved. New adapter/UI/app/metrics are hash-checked. Reader hashes and file stamps join artifact hashes in cache keys.
- docs/track_a/Visualization_User_Guide.md — six-section/24-pair coverage and linked exact walkthrough.
- Human RandomNotes.md was neither edited nor staged by this session.

## 6. Files deleted, renamed or moved

None. No raw/source/old packet was copied into a new data store or overwritten. No Git cleanup/reset/stash.

## 7. Critical interfaces

All new interfaces are read-only; they accept project-relative verified sources and return compact DataFrames/dictionaries, with no optimizer/model-output writer.

- Study.discover(Catalog) → Study: verifies sealed proposal/source and fold/preparation contracts; depends on existing Catalog/verified/read_preparation.
- Study.panel(fold,seed,arm,partition) → DataFrame: loads saved scores verbatim, checks result/parameter IDs and exact five-stock control masks/clocks/targets. Development targets additionally match the original input-binding float32 targets and sealed predictions_long table. T2 predictions are already canonical; no inverse is applied here.
- Study.parameter(fold,arm,prefix) → dict: validates immutable parameter hash, prep ID and cutoff. Inner/refit are separate. Study.training_targets(base,fold,prefix) → compact labels: reuses canonical_population/tg0, requires exact registered float64 population hash/count, calculates no fitted statistic.
- exact_match(left,right) → None: rejects duplicates, nonfinite values, incomplete cross-sections, differing keys/targets/timestamps. No inner join/intersection policy.
- label_views(targets,t1,t2) → DataFrame: display-only raw/registered clipped/asinh labels; existing cap/s only. paired_table(control,treatment) → summary/daily tables: existing equal-stock/origin/day metrics and ZERO convention.
- Study.trace(fold,seed,arm): adds recorded p90/p99; missing historical applied fractions remain NaN rather than borrowing exceedance fractions.
- event_state(row,fold,seed,arm,partition) → all original page filters; navigation callback carries exact symbol/date/origin/model/fold/partition and enables horizon markers.
- input_context(...) →48×16 stock-feature rows: lawful saved mask, exact48 full-hour steps, existing components and existing recipe, float32 scaled inputs; no inference or fit. feature_parameters(...) exposes actual scaler/floor parameters and bounded-channel identity.
- controlled_page and feature_explorer render Streamlit/Plotly; source/prediction/preparation identities and population/units appear near charts. Cached views include actual artifact and reader SHA/stamp identities. No renderer or metric decimation.

## 8. Data/schema/provenance changes

No scientific schema or dataset changed. Package011 sealed artifact_bindings.json is discovered through the existing visualization controlled_package. New visualization-only config key controlled_explorer binds that seal, proposal and cache_readers. Old sealed artifacts/scientific readers remain unchanged; the old --verify-only still reports READ_ONLY_RECOMPUTATION_MATCH/20panels/23,200forecasts. AvailableIDs table lists60 legal panels across20fold/seed/arm combinations ×3partitions. Registered training populations: WF1inner6880/refit7510, WF2inner8130/refit8750 stock observations. Their float64 hashes agree before display transforms; saved predictions/targets retain canonical float32 history.

TG0 is centered future four-hour log return divided by cross-sectional MAD+epsilon. Historical volatility is not an intermediate target denominator. Future return, median/MAD and TG0 are EX-POST; no same-origin feature leakage. Source candles retain retrospective split-price/inverse-volume representation, UTC keys and ET display. Native/full-hour distinctions, stubs, early-close and protected-date predicates remain unchanged. New guide data is small, not an archive redistribution permission.

## 9. Dependencies/environment

No dependency/version/environment-variable/setup changes. Uses declared visualization extra and repository .venv; existing scientific dependencies unchanged. No global packages, secrets, account IDs or network data access. Localhost sockets required approved outside-sandbox verification after a sandbox denial.

## 10. Commands and tests

See commands.md and actual logs in reports/data_audit/ta010b_controlled_explorer_2026-10-15_164300. Focused final suite: `.venv/bin/python -m pytest tests/test_controlled_visualization.py tests/test_visualization_readonly.py tests/test_controlled_review.py -q` —23passed, no model fits. Earlier fixture omitted derived timestamp columns; corrected fixture and reran. Initial sandbox socket test failed; approved outside-sandbox focused run passed. Baseline old dashboard suite7passed before implementation. No90-minute legacy learning suite; shared scientific modules unchanged.

`.venv/bin/ruff check .` PASS. Exact full static command: `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist` —203project-owned files,0errors/0warnings; final installed_pylance.json records exact run. Initial new-code pandas scalar diagnostics were corrected with existing validated numeric conversion, without suppression, casts, exclusions or weaker severity.

`./scripts/run_track_a_dashboard.sh --check` PASS890dependencies. `--smoke` actual health200/HTML200, clean SIGINT exit0. First sandbox smoke denied sockets; approved localhost retry passed. Recorded startup-to-health1.019s, shutdown0.315s. AppTest19multi-page cases passed; startup 2.321s, original AAPL price submission 5.805s; full walkthrough server work 44.388s. Browser drawing is not measured/claimed. Later focused AppTest verifies the actual SBUX guide event and48-step context. Bare-mode and sandbox Arrow CPU-probe warnings are preserved as environment warnings, not fabricated results. A temporary baseline harness failed only while serializing nonexistent filtered_state after the app had rendered; final harness uses public widget state. A concurrent development-time source edit correctly triggered the source hash guard in an earlier harness; restarted verification after refreshing the approved visualization binding passed.

`git diff --check` PASS, including preserved Notes. Reviewed Git diff/status and new files. No secrets, hardcoded developer paths in executable app code or large new dataset/checkpoint. Pylance editor verification: select repository .venv/bin/python, installed extension/basic severity, restart language server and refresh Problems. Human editor confirmation remains pending; CLI zero diagnostics verified.

## 11. Results/experiment summary

No new experiment. Existing Package011 descriptive results remain mixed/inconclusive, no finalist promotion. Stored T2-minus-C0 MSE WF1/seed42−0.011421188656, WF2/seed42−0.011104274498 are reconstructed in canonical units; existing exploratory five-session intervals retain their limits. No trading results or alpha claim.

Concrete guide event: TA011-T2-S42-WF1, SBUX2023-11-17 origin2/11:30ET/16:30UTC, saved canonical TG0−24.3998966217, forecast−0.0053515672. Final focused AppTest navigates to this exact date/stock/origin and actual48-step context. Separate19-case walkthrough navigated TA011-T2-S123-WF2 to CME2024-02-14 origin1/10:30ET. Default AAPL2024-01-16–19 contains52half-hour candles/4closing stubs or24full-hour candles/0stubs. Actual context48timestamps/768feature cells.

## 12. Reproduction

Follow README authoritative environment route and existing optional visualization setup. Provision legitimately accessible exact relative-path artifacts from existing manifests; missing optional weights do not trigger inference. Run `./scripts/run_track_a_dashboard.sh`, then Start Here → Package011entry. Follow docs/track_a/HOW_TO_VISUALLY_INSPECT_PACKAGE_011.md. Stop Ctrl+C. Use --check/--smoke for local diagnostics. Run the focused test/static commands above. Restore matching artifacts if hashes fail; never loosen identity checks or rerun a fit to fill a plot. No temporary script is required to use the app or run its committed tests. Independent chart oracles and small availability/binding tables are included in the packet. Clean-clone final-submission rehearsal was not part of this local visualization task.

## 13. Git/collaboration

Starting/ending branch feat/track-a-data-intake; HEAD363fc4bf1e85b680e43dcddd1ad0f8df3a044007. Fetch completed;0ahead/0behind at start. No add/commit/push/pull/merge/rebase/reset/stash. Preserve human Notes separately. Review the three modified owned files, four new source/test/guide files, new010Bpacket and this report before staging. If later authorized, use explicit paths from artifact_inventory.csv and a focused commit such as `feat: add read-only controlled experiment explorer`; fetch/check status before any push and use the team PR workflow. Do not include licensed raw data/weights or unrelated Notes. Likely conflict areas: app and visualization config/guide. Exact final status saved in git_final.txt; report itself appears untracked.

## 14. Issues/risks/limitations

No final failing tests or reproducible static errors. Historical WF1C0 batch traces and actual applied clipping fractions are Not recorded; p90/p99/>5 appear only if recorded. Full optimizer/dropout/per-example gradient histories are unavailable; associations cannot identify causation. No historical-volatility-normalized intermediate target exists in TG0. Original labels preserve extreme values. Feature T1/T2 channels differ from the treatments with those names. Readiness inspection adds no alternative normalization scheme.

No native browser screenshot or manual appearance review claimed. AppTest/HTTP provide programmatic evidence. Current caveats remain ASSUMPTION_CONDITIONAL, with no observed publication/action vintage/PIT/independent license or course equivalence certification. Confirmation stays locked. No Package012 execution or research selection. Large canonical components are decoded once and shared in process, not copied into new stores; only compact bound views are cached. Compatibility reader map and cache_readers must both be refreshed together for a future intentional visualization code revision; scientific reader changes remain a separate matter.

## 15. Human/teammate review

One consolidated human_review_card.md covers visual clarity, fixed units/populations, missing telemetry, event context, and editor Problems refresh. No new scientific approval is requested. Existing training authorizations are neither re-requested nor extended. Git integration remains unperformed. Review appearance and editor refresh manually; these are not claimed as completed.

## 16. Next steps

Use the five-minute guide and record interpretation. Review/commit visualization changes only if authorized. Any future Package012 study requires its own design/evidence/run scope. No follow-on experiment initiated; stop after this package.

## 17. Artifact inventory

reports/data_audit/ta010b_controlled_explorer_2026-10-15_164300/artifact_inventory.csv lists created/modified owned sources, tests, guides, this report and all audit files with SHA/bytes/type/tracking intent. Key evidence: source_binding_evidence.json, available_study_ids.csv, numerical_chart_oracles.json, target_label_oracles.json, preserved_demo_oracles.json, AppTest.json/terminal log, verified_event_navigation.json, http_smoke.json, focused pytest/static logs, preservation_before/extended_before/after, old_package_readonly_verification.json, package_report.md and human_review_card.md. Small evidence is intended for review/tracking; raw archives, components, weights and all original packets remain at their existing locations. No new dense windows, models, checkpoints, raw export or analytics. Smoke server stopped cleanly.
