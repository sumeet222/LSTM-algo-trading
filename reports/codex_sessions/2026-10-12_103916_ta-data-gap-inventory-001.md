# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-12, completed 2026-10-12T10:43:02.591056-04:00 (America/New_York). Native inventory/conservation phase: 10:39:16–10:40:58 ET; static/focused checks took approximately 12 seconds.
- Contributor/session: Codex / TA-DATA-GAP-INVENTORY-001.
- Requested task: read-only exact original missing-candle inventory, not a continuation of universe acquisition.
- Branch: `feat/track-a-data-intake`.
- Starting and ending commit: `34a23ccba7241df704034b41b2f0085ca74d86fd`; no commit created.
- Start: clean working tree. End: only new audit directory and this session report untracked.
- Remote fetch: completed; upstream ahead/behind 0/0. No issue/PR.

## 2. Executive summary

MISSING_CANDLE_INVENTORY_COMPLETE — HUMAN_REVIEW_REQUIRED. Verified original July 2020–June 2025 native source against actual XNYS sessions: 168 absent half-hours, exactly matching both prior ledgers, in 15 affected stock-sessions and 15 maximal contiguous runs. AAPL0, JPM36, JNJ37, WMT48, CAT47. CAT and JNJ on 2022-03-08 each lack all 13 RTH candles. All 15 runs include the terminal close. No adapter dropped a present terminal row. All 168 rows are shown without truncation in Markdown and both machine-readable inventories.

## 3. Research/protocol impact

No research question, target/horizon, features, universe, source activation, splits, thresholds, cost/trading rules, model/search parameters or scientific status changed. Confirmation-period source keys were read only for explicitly authorized integrity checks; no features, labels, returns, predictive or economic outcomes were computed. No provider requests or credential loading. Scientific HOLDs remain independent.

## 4. Files created

|Path|Type|Purpose|
|---|---|---|
|`reports/data_audit/ta_exact_missing_candles_2026-10-12_103916/MISSING_CANDLES_REPORT.md`|.md|Ordered human summary, all 15 runs, all 168 candles and daily-close/T2 diagnosis|
|`reports/data_audit/ta_exact_missing_candles_2026-10-12_103916/missing_candles.csv`|.csv|Exact prescribed one-row-per-absent-candle schema, 168 rows|
|`reports/data_audit/ta_exact_missing_candles_2026-10-12_103916/missing_candles.json`|.json|Same full rows plus scope, 60 manifest hashes, summaries and terminal checks|
|`reports/data_audit/ta_exact_missing_candles_2026-10-12_103916/missing_clusters.csv`|.csv|All 15 maximal contiguous runs, duration and terminal impact|
|`reports/data_audit/ta_exact_missing_candles_2026-10-12_103916/terminal_close_t2_audit.md`|.md|All 15 affected closing slots, earlier-row evidence, exact existing adapter rules and cached T2 counts|
|`reports/data_audit/ta_exact_missing_candles_2026-10-12_103916/reconciliation.json`|.json|81305 expected = 81137 present + 168 absent; all key matches, manifest SHA, conservation and output hashes|
|`reports/data_audit/ta_exact_missing_candles_2026-10-12_103916/human_review_card.md`|.md|Three focused human checks without authorizing repairs or source activation|
|`reports/data_audit/ta_exact_missing_candles_2026-10-12_103916/checks.json`|.json|Recorded static/test/data validation and unchanged scientific HOLD status|
|`reports/codex_sessions/2026-10-12_103916_ta-data-gap-inventory-001.md`|.md|Mandatory 17-section session handoff and reproduction procedure|

All source locators are repository-relative. Missing rows identify the source scope checked, not invented source row IDs.

## 5. Files modified

No pre-existing repository files modified. Draft new artifacts were corrected before delivery to use portable relative locators and accurately state that all 15 terminal closes are absent. Final hashes are recorded in reconciliation.json.

## 6. Files deleted, renamed, or moved

None.

## 7. Critical functions, classes, variables, and config keys

No new production interfaces. Reused `load_config`, `monthly_requests`, `chunk_paths`, `read_verified`, `calendar.schedule`, and `aggregate_session_hours` for the 15 affected sessions only. Existing `StockHistory` daily terminal selection and `FeatureCalculator` T2 coverage rule were inspected, not changed or rerun across FT0. `verify_screen_authority` verified the hash-bound 16 P2 and 33 P3 deferred entries.

## 8. Data/schema/provenance changes

Original immutable namespace `data/raw/alpaca/track_a`; 60 verified monthly chunks, 159008 native rows, SIP, 30Min, split-adjusted, entity asof2025-06-30, interval-start labels. Scope 2020-07-01–2025-06-30 inclusive ET; 1255 actual XNYS sessions including 9 early closes. Expected81305 RTH keys = present81137 + absent168; 77871 genuine non-RTH source rows excluded from the expected-key set. No off-grid within-RTH source timestamps, duplicates or wrong metadata were admitted. All missing rows are normal-session half-hours with ISO timezone offsets. Source absence does not establish zero volume/no trades/vendor defect. No raw schema or source content changed.

## 9. Dependency/environment changes

None. Existing .venv interpreter/dependencies used. No .env read or credentials loaded; no editor/settings/severity changes. Nonfatal sandbox PyArrow CPU-cache sysctl warnings appeared during Parquet reads; all read/validation operations succeeded.

## 10. Commands and tests run

- `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD`, `git remote -v`, `git fetch --all --prune`, `git rev-list --left-right --count HEAD...@{upstream}`: clean start, branch/SHA above, fetch successful, 0/0 upstream.
- `.venv/bin/python /private/tmp/lstm_exact_inventory.py`: ephemeral local evidence-only orchestration; verified all canonical chunks and exact missing-key set, snapshot/rehash700 tracked and276 raw files; no credential/network APIs called. Helper intentionally not added to repository.
- `.venv/bin/python /private/tmp/lstm_exact_finalize.py`: all168 CSV/JSON/Markdown rows and timezone/cluster/source-hash checks PASS; portable locator check PASS.
- `.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist`: actual local Pylance2026.4.1 dist, Pyright1.1.414 basic profile, all98 owned files, **0 errors / 0 warnings**, 7.067s. Existing exact local extension path was resolved from `/private/tmp/p35_pylance`; no machine path introduced into committed code/config.
- `.venv/bin/ruff check .`: PASS.
- `.venv/bin/python -m pytest -q tests/test_aggregation.py tests/test_calendar_alignment.py tests/test_stock_source.py`: **41 passed**, 4.69s.
- `git diff --check`: PASS. No tracked diff.
- Full suite not run: no production or repository Python files changed, as required by this narrow task.
- Optional editor verification: repository .venv selected, refresh Problems; no language-server restart needed. CLI parity is measured here; no fresh manual editor count is claimed.

## 11. Experiment/results summary

Source-integrity diagnostic only. No model/seed, predictive metrics, trading metrics, fitting or confirmation performance. Prior masks were read as metadata only: original-source T2 failed origins AAPL58/JPM220/JNJ220/WMT278/CAT274. Separately labeled inactive warmup counts AAPL0/JPM162/JNJ162/WMT220/CAT216, unique union220; per-stock losses overlap. Original mechanical919/1502 and inactive warmup1183/1502 were verified from existing masks, not recomputed. Prior source-gap ledger75 direct +244 additional propagated =319 remains reconciled; not all319 are T2 effects.

## 12. Reproduction instructions

Use README environment and original canonical source; no credentials/network required. From repository root, load `configs/track_a_data.json`. Iterate `monthly_requests`; derive `chunk_paths` and run `read_verified` for each. Generate XNYS schedule via `calendar.schedule(start_date,end_date)`; for each ordered symbol/session generate `[open,close)` starts every30min. Native rows are keyed by exact(symbol,UTCstart); reject duplicates/wrong metadata/off-grid RTH labels. Subtract source keys from scheduled keys. Compare exact keys with both `gap_cluster_reconciliation.json` and `ft0_source_qa.json`; expect168 matches, no differences. Group sorted missing starts into maximal30min runs within each stock/session; never span nights. Check affected sessions using existing `aggregate_session_hours` and terminal part rule in `stock_source.py`. Read existing masks only for reported T2 counts. Every input/manifest hash and exact row needed to repeat/check this arithmetic is in reconciliation.json and missing_candles.json. Ephemeral helpers are conveniences, not required source/config dependencies.

## 13. Git / collaboration status

Branch/SHA unchanged; remote fetched, upstream0/0. No staging, commit, push, PR, pull, merge, stash, reset or cleanup. Only nine new audit/session artifacts untracked; existing source/code/human files preserved. No integration action requested. For later authorized integration, review and stage only these listed paths; never broad-stage unknown work.

## 14. Known issues, risks, and limitations

No failed inventory assertions, tests or static checks. Source publication timing, formation/action vintage, execution and other scientific gates remain HOLD. Source absence is not proof of no trading. Earlier native closes are genuine observations but cannot substitute for the scheduled terminal half-hour under approved daily rules. There is no alternate daily-close input in this original config/namespace. This task does not test supplemental providers, activate inactive warmup or evaluate universe replacements. Cached per-stock T2 counts are overlapping window-level failures, not raw candle counts or per-gap independent causal effects.

## 15. Decisions requiring human or teammate review

Review the three checks in human_review_card.md: full inventory/conservation, ranked clumps/calendar, and terminal/T2 distinctions. No repair, source substitution or scientific activation is authorized by this report.

## 16. Next recommended steps

Human review of this exact inventory. Stop here; pursue recovery/amendment only under a separate explicit task.

## 17. Artifact inventory

All nine small audit/session files are untracked review artifacts; exact individual SHA/bytes inventory in reconciliation.json (self-hash excluded). No plots, checkpoints, new caches, source archives or large artifacts. Prior ledger: `reports/data_audit/ta_data_remed_ft0_001_2026-10-11_195135/gap_cluster_reconciliation.json`; authoritative full-scope QA: `reports/data_audit/ta_p2_close_ft0_2026-10-11/ft0_source_qa.json`; prior origin masks and latest universe-screen handoff preserved. Final source/manifest SHA checks PASS.
