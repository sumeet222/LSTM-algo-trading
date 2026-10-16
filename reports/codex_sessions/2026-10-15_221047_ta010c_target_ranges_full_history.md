# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-15T22:10:47.262328-04:00 (America/New_York); start 2026-10-15T21:52:36.298397-04:00.
- Contributor/session: Codex root; no subagents. Elapsed to report: 18.2 minutes.
- Requested: Package010C complete generic TG range table, inline genuine candles and Full data history/FT0 viewer.
- Branch: feat/track-a-data-intake; starting/ending HEAD `a0663c5e9c0afa206a982e0fd7d893f102409b99`; no commit/PR.
- Start tree clean; upstream 0 ahead / 0 behind after fetch. End: four tracked UI/config files modified, new source/test/guide/audit/session files. Exact final status in `reports/data_audit/ta010c_range_history_2026-10-15_215236/git_final.txt`.

## 2. Executive summary

Implemented in the existing dashboard. Root cause was explicit `tails.head(30)` table truncation and `head(20)` decomposition after counting all filtered rows; there was no 67-row underlying population limit. Complete verified relations now feed bounds, sort, page and exact-identity selection. Blank bounds include ordinary observations. Table cells are explicitly not clickable: an accessible searchable observation selector plus always-visible Show candles button updates one inline candle/volume chart immediately. Full data adds bounded date navigation and actual saved native/scaled FT0 panels. Engineering PASS; manual browser appearance/editor refresh remain human-only review items.

## 3. Research/protocol impact

None: target/horizon, universe, source adjustments, features, floors/scalers, costs/trading, seeds, splits, masks and final-test policy unchanged. No training, inference, refitting, resampling, pair reservation, checkpoint writes, provider requests or confirmation numeric access. Ledger stays 24/40, byte-identical. P2 handoff v1 read/hash-verified with `load_deferred_work` (16 entries), no status changes or scientific closure. ASSUMPTION_CONDITIONAL rights/universe/action/period-end limitations retained; no Package012 or production D1 claim.

## 4. Files created

- `src/lstm_data/visualization/target_ranges.py`: typed target registry; original registered target population/decomposition; validated bounds, stable sort, pagination/selection, descriptive denominator comparison.
- `src/lstm_data/visualization/history.py`: strict pre-I/O confirmation/range guard, calendar navigation, scheduled horizon markers, existing source/feature adapters, preparation scope and separate-axis synchronized plots.
- `src/lstm_data/visualization/range_ui.py`: cached identity-bound slices; independent range population controls and inline inspector; Full data controls and exact origin handoff.
- `tests/test_target_range_history.py`: 13 parameterized focused tests, including actual-data AppTest interactions and independent numerical oracles.
- `docs/track_a/HOW_TO_INSPECT_TG_RANGES_AND_CANDLES.md`: exact controls and three-minute example; rendered inline from Start Here.
- This report and `reports/data_audit/ta010c_range_history_2026-10-15_215236/`: small provenance, run logs, numerical/UI evidence and human review card. `artifact_inventory.csv` enumerates each created evidence file, type/purpose/hash/size/tracking intent.

## 5. Files modified

- `apps/track_a_dashboard.py`: Full data only under Price & Features → Partition; separate route before legacy saved-experiment/date selection; Start Here guide. Other sections retain original partitions.
- `src/lstm_data/visualization/controlled_ui.py`: replaces capped target table with shared range explorer; carries selected study seed. Original target histograms and old Extreme Events deep-link retained.
- `src/lstm_data/visualization/figures.py`: source candle/volume hover precision increased to 17 significant digits and share units clarified; no numeric transformation.
- `configs/track_a_visualization_v1.json`: refreshes only maintained visualization-reader hashes and cache identities; adds three visualization readers. Scientific input/model/recipe/study references unchanged.

## 6. Files deleted, renamed, or moved

None. No raw archives, prior outputs or user notes edited, copied into a replacement store or removed.

## 7. Critical functions, classes, variables, and config keys

- `TargetSpec`: frozen typed metadata, signed/absolute units, provenance, eligibility, maturity, registered horizon and callable decomposition. Only TG0 registered; `target_spec(key)` rejects unknown TGn as NOT_IMPLEMENTED.
- `tg0_decomposition(study, base, fold, population, seed) -> DataFrame`: verifies registered float64 training hash/count or exact saved development mask before decomposition; returns cutoff/ET/UTC, full components, IDs and existing floor flag. Development float32 binding checked at absolute 2e-6; canonical training float64 verified at 1e-12. All outcome fields EX-POST.
- `TargetRange.parse/select`: finite optional bounds, ordered validation, signed/absolute and explicit independent endpoint inclusion. `ordered/page_rows/retained_selection`: stable identity tie-break, bounded complete pages, reset on population/filter removal; no top-k cap.
- `history_guard/history_bars/indicator_slice`: reject confirmation and >32-day ranges before source/recipe/store numeric readers, including first cache miss. No unlock path. Source adapter is unchanged genuine source_bars with predicate-before-conversion and request/schema/hash checks.
- `context_window/nearby_sessions/target_markers`: existing exchange schedule, max five sessions each side, archive clipping, actual full-hour steps; invalid early-close/unknown horizons unavailable, never wall-clock substitution.
- `preparation_scope/history_features`: explicit saved inner/refit preparation and source binding. Refit scope = original training through its own development end; inner scope = inner training through original calibration tail. Out-of-scope requests have no fallback/refit. Training-prefix application explicitly retrospective.
- `observation_figure/history_figure/center_history_origin`: existing candlestick/volume component; separate feature panels and common time axes. Full data carries known origin metadata without reading outcomes.
- `range_explorer/full_data_page/open_full_data`: read-only rendering/caches keyed by artifact+reader token, population and symbol/date/recipe; no scientific writer. Selection persists through sort and clears when no longer eligible.

## 8. Data/schema/provenance changes

No canonical data/schema changes. Complete display relation adds stable identity and exact decomposition columns. Source intervals remain genuine SIP 30Min START labels, USD vendor retrospective split prices and inverse-split adjusted-share volume. Features retain completed-hour END timestamps and actual FT0 definitions/floors; B2/T2/T5 bounded identity. Both clocks and full precision retained. Full data timeline 2020-07-01–2025-06-30; numerical reads stop at 2024-06-30. Existing compressed preconfirmation components reused once in process; no new dense stores, raw exports or full-history feature computations.

## 9. Dependency/environment changes

None. Existing repository .venv, Streamlit1.64.0/Plotly6.3.1 and current Pylance/basic stubs retained. No packages, environment variables, settings or secrets changed. Local socket verification required approved outside-sandbox execution after sandbox denial.

## 10. Commands and tests run

Exact commands in packet commands.md. Final `.venv/bin/python -m pytest tests/test_target_range_history.py tests/test_controlled_visualization.py tests/test_visualization_readonly.py tests/test_controlled_review.py -q`: **36 passed, 0 failed, 75.61s**. New-only suite previously 13 passed. Isolated corrected volume oracle 1 passed/14.90s. Earlier test-only Plotly encoded-array mismatch corrected; no production volume issue hidden. See verification_notes.md for iterative checks.

`.venv/bin/ruff check .`: PASS. Exact static command: `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist`: **207 owned files, 0 errors, 0 warnings, 28.799s**. No suppression, severity/stub/exclusion change. Editor: select repository `.venv/bin/python`, keep installed Pylance basic, restart language server and refresh Problems; human confirmation pending.

`./scripts/run_track_a_dashboard.sh --check`: PASS893 bound dependencies. `--smoke`: health200/HTML200, clean SIGINT exit0, startup2.118s/shutdown0.492s. Actual new AppTest checks range/page/ordinary+extreme selection/inline chart/population reset/native-normalized-Both/confirmation reader spies. Eight additional legacy AppTest route/control cases PASS, including saved T2 and diagnostics. `git diff --check`: PASS. No expensive unchanged synthetic training suite. Bare Streamlit and sandbox Arrow CPU-probe warnings are environment messages; no final failing test/static diagnostic.

## 11. Experiment/results summary

No experiment. Independent immutable-panel oracle: 7,510 rows; strict |TG0|>1 =2,860, |TG0|>10 =67, |TG0|<2 =6,035, signed [-2,-1] =691. At50/page, >1 has58pages/10last rows; union of pages exactly equals matching IDs with no duplicates. AAPL2020-12-09 origin2 cutoff11:30EST/16:30UTC: TG0−29.11614698023523, return−0.032215045932356495, median−0.011395641081844732, MAD0.00046406869742296464, epsilon0.00025097800379902393, denominator0.0007150467012219886, numerator−0.020819404850511765; original floor flag false. Exact proxy target14:30EST/maturity14:33EST.

AAPL date has13 genuine half-hour candles. Direct exact-key Parquet OHLCV agrees with viewer, original source chart and inline slice; model M1 equals native formula and saved float32 center/scale arithmetic. Native/scaled have separate axes. Exact48-step context ends at forecast cutoff, without future candles. No predictive/economic conclusions generated.

## 12. Reproduction instructions

Follow README setup and legitimately provision existing artifacts using data/README.md; no new data dependency. Launch `./scripts/run_track_a_dashboard.sh`, follow Start Here's guide or new Markdown guide. For direct history choose Price & Features → Partition: Full data → AAPL → Jump to date2020-12-09; M1 with explicit WF1/refit recipe supports Standard/Normalized/Both. Run --check/--smoke and focused pytest/static commands above. Missing genuine data or unsupported recipe dates remain unavailable, never trigger downloads/fits.

## 13. Git / collaboration status

Branch/HEAD unchanged; fetched origin, 0ahead/0behind. No add/commit/push/restore/reset/clean/pull/merge/rebase/stash. Four tracked edits plus the new files listed above remain uncommitted. Preservation:887 original bound files hash-match; source/recipe/model/ledger evidence unchanged; no unrelated tracked edits. Conflict-prone files: app, controlled_ui, visualization config and figures. Small audit inventory is intended for review/tracking; licensed data/weights remain existing local references.

If separately authorized later: review inventory, then stage only the four modified files, three new source modules, new test/guide, this report and this new audit packet; `git commit -m "feat: add complete target ranges and protected full-history viewer"`; fetch/recheck upstream, then `git push origin feat/track-a-data-intake` and use the existing team PR workflow. Preserve any later local work; never force/integrate over divergence. None executed here.

## 14. Known issues, risks, and limitations

No residual failing tests/static diagnostics. No unavailable dataset in this local fixture; other machines must provision exact legitimate artifacts. Native FT0 depends on registered saved floors; out-of-preparation dates do not get surrogate native/scaled values. Confirmation intentionally locked; no numeric unlock consent supplied. No native browser screenshot/manual visual review or editor Problems refresh claimed. API/price/action/PIT/source-rights qualifications remain; proxy closes are not execution fills. Unknown target/horizon unavailable. Caches are in-memory bounded slices, not persistent duplicated data. Final clean-machine rehearsal is outside this UI package.

## 15. Decisions requiring human or teammate review

Human review card marks functionality engineering PASS, with browser appearance and editor refresh HOLD pending human confirmation. Any later confirmation viewing needs separate explicit researcher authorization/audit and holdout review. No request to widen research/Git scope is made now.

## 16. Next recommended steps

Use the three-minute guide and review appearance. Refresh editor Problems. Review the explicit diff/artifact inventory before any separately authorized Git integration. Keep future Package012 design/execution and any new holdout decision separate.

## 17. Artifact inventory

`reports/data_audit/ta010c_range_history_2026-10-15_215236/artifact_inventory.csv`: all owned source/test/guide/report/evidence paths, types, bytes and SHA256 (inventory excludes itself). Key evidence: numerical_oracles.json, preservation_before/after.json, AppTest_evidence.json, legacy_ui_smoke.json, focused_pytest.log, installed_pylance.json, ruff.log, setup_check.log, http_smoke.log, diagnostics_before_after.json, commands.md, verification_notes.md and human_review_card.md. No new plots/checkpoints/dense raw data. Server stopped cleanly.
