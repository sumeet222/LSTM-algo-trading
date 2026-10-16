# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-16T15:16:41.412330-04:00 (America/New_York).
- Contributor/session: Codex, source-only feasibility implementation and audit.
- Task: TA-HF-TWELVEDATA-1H-FEASIBILITY-001; exact submitted instruction retained in `reports/data_audit/ta_hf_twelvedata_hourly_2026-10-16_123344_final/submitted_instruction.txt`.
- Branch: `feat/track-a-data-intake`.
- Starting and ending commit: `ea6ffacc2aa53ad09306edf1b3482de2d8bc6f2b` (no commits).
- Start: clean, upstream0/0 after `git fetch --all --prune`; end: only new untracked task files, upstream0/0. No issue/PR created.

## 2. Executive summary

Acquired exactly three public hourly Parquets at HF revision `ad48edaf3828ec855ab4a5bb1b8336fa0b68cdec`, verified LFS SHA256/size, and audited692,603rows /51symbols. Final decision is REVISED_CHRONOLOGY_POSSIBLE plus RIGHTS_UNRESOLVED and ADJUSTMENT_HOLD. Strict original continuity fails:3calendar-only qualifying stocks,0with required prehistory. No STRICT_20_STOCK_PASS or migration authorization is asserted.

Final review entry: `reports/data_audit/ta_hf_twelvedata_hourly_2026-10-16_123344_final/NEXT_DECISION.md`. Preliminary v1/v2 namespaces are retained; only `_final` and audit configv3 define the final proposal.

## 3. Research/protocol impact

Independent source namespace `CAND:HF_TWELVEDATA_20PLUS:SOURCE_AUDIT:v1` only. Original universe, D1, TG0, FT0, frozen dates, costs, architecture, recipes, seeds and experiments unchanged. No feature/target creation, training, WF regression evaluation, final-test outcome inspection or original confirmation numeric reads. Ledger stays28/200. New vendor train/val/test raw source quality was inspected; a proposed held-out period is model-outcome held-out, not pristine unseen raw data. Source selection is retrospective and must not be represented as PIT membership.

## 4. Files created

Reusable implementation/config/test/template files:

- `src/lstm_data/hf_hourly.py` — CLI and resource receipts.
- `src/lstm_data/hf_hourly_source.py` — public metadata, footer ranges, SHA-bound one-copy acquisition.
- `src/lstm_data/hf_hourly_audit.py` — schema/calendar and stock/month/year census.
- `src/lstm_data/hf_hourly_feasibility.py` — coverage-only shortlist and conditional origin geometry.
- `src/lstm_data/hf_hourly_diagnostics.py` — action/issuer/nominal-interval/cached overlap diagnostics.
- `src/lstm_data/hf_hourly_report.py` — decision and review document generation.
- `tests/test_hf_hourly.py` — hermetic invariant and cache/chronology oracles.
- `configs/hf_twelvedata_hourly_audit_v1.json` — versioned source-only criteria; v3 is default.
- `configs/hf_twelvedata_hourly_audit_v2.json` — versioned source-only criteria; v3 is default.
- `configs/hf_twelvedata_hourly_audit_v3.json` — versioned source-only criteria; v3 is default.
- `configs/hf_twelvedata_action_checks_v1.json` — primary issuer action references.
- `docs/track_a/templates/hf_hourly_source_suitability.md` — hourly-native compatibility and rights template.

Every generated path, type, purpose, byte count, SHA256 and Git intent is listed in `reports/data_audit/ta_hf_twelvedata_hourly_2026-10-16_123344_final/artifact_inventory.csv`. This session report is an additional new Markdown artifact. Raw cache is ignored/local; report trees contain compact summaries/source-policy text, not bulk prices. Vendor Python snapshots are `.py.txt`, never imported or executed. Existing source README/data were not modified.

## 5. Files modified

No previously tracked files modified. New implementation and reports were iterated within this session. Configv2 append-only clarifies issuer-history exclusions after the initial census; v3 append-only reserves126complete regular warmup sessions instead of126exchange sessions. Both bind predecessor hashes and disclose the clarification. No return/model criterion was used.

## 6. Files deleted, renamed, or moved

None. Slow intermediate processes were interrupted; preliminary outputs remain preserved. No unknown local work was discarded.

## 7. Critical functions, classes, variables, and config keys

- `PublicHTTP.get(url, maximum, byte_range=None) -> bytes`: public-only native HTTPS, identity transfer, bounded body, range206validation, no environment credentials or automatic retries. Logs initial public URL only, never signed redirects.
- `validate_listing`, `verify_cached`, `download`: require immutable40-character revision, exact3hourly paths, sizes/LFS hashes; reuse exact cache, resume `.part`, hash before atomic publication. Bad cache fails closed.
- `Census`: projected source frame, XNYS grid, observed/usable bool matrices and compact per-stock/month summaries. UTC keys remain unchanged; naive wall-clock formatting is used only for calendar fields.
- `qualifying` / `best_overlap`: >=99.5% valid canonical full hours, max2consecutive missing expected hours, no wholly missing aligned sessions or invalid/duplicate rows, explicit issuer exclusions; month-boundary interval search. No interpolation.
- `geometry`: presence/quality of48complete historical hourly steps and four same-session future hourly rows; no future price arithmetic, labels, tensors or fitting.
- `evaluate`: static publisher-sector round robin with missingness/alphabetical ties; reserve126complete regular days with all20full-hour and terminal-row presence, then chronological60/20/20session partitions. Conditional geometry is not FT0/TG0 eligibility.
- `cached_overlap`: six fixed dates before2024-07-01;12matched nominal hourly examples from cached two-half-hour Alpaca rows. No provider requests. Use `--no-cached-comparison` on a machine without the original source cache/readers.
- `main`: mutually exclusive `--metadata-only`, `--audit-cached`, `--download-bars-1h`; default configv3. Config keys include byte limits, exact file list, frozen strict scope, issuer exclusions, warmup count and training_authorized=false.

## 8. Data/schema/provenance changes

New isolated raw cache: `data/raw/hf_twelvedata_hourly/ad48edaf3828ec855ab4a5bb1b8336fa0b68cdec/bars_1h/`. Exactly101,602,217 /20,679,513 /37,664,211bytes, total159,945,941. All3remote/local SHA256 identities are in acquisition_manifest.json.

Actual datetime is timestamp[us,tz=America/New_York], unlike card's ns description; OHLC/close_adj double, volume int64. Only9source columns projected; all supplied indicators/macro features ignored. Train443,552rows, val89,574, test159,477. Unique keys/null/nonfinite/bad-OHLC/negative-volume counts are zero;11rows have nonpositive price components. close_adj equals close in all692,603rows. Clock drift includes9:00/top-of-hour history; off-grid rows are never relabeled.Outside-start rows must be interpreted using the exact nominal-interval JSON:18,980outside-RTH starts,11,193leading partial overlaps,80,729nominal terminal overruns,0noncalendar dates. Nominal overruns do not prove actual trades after close.

Four official split-boundary examples are descriptive only. Publisher source snapshot revision `f352327a10fcc4a3faf9b53e0eead1e0f76a766b` copies absent close_adj from close and clamps OHLC extrema; it is not attested as the HF build source. Dividends, volume parity, action vintage, publication timing and data rights remain unverified. Original cached-Alpaca comparisons report ratios without declaring either vendor truth.

## 9. Dependency/environment changes

None. Existing requests, pyarrow, pandas, numpy and exchange_calendars suffice. Python3.14.6/arm64; no huggingface_hub/duckdb install, secrets/login/.env reads, API subscriptions or paid services. Public access required no token.

## 10. Commands and tests run

- Git start: `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD`, `git remote -v`, `git fetch --all --prune`; clean0/0. Later `git diff --check` and `git diff --stat`: pass/empty tracked diff; final status contains only task-new files.
- Final audit: `.venv/bin/python -u -m lstm_data.hf_hourly --audit-cached --revision ad48edaf3828ec855ab4a5bb1b8336fa0b68cdec --out reports/data_audit/ta_hf_twelvedata_hourly_2026-10-16_123344_final` — exit0,0network, final runtime202.192s, scan0.440s, census182.663s, feasibility15.306s, peak RSS374,423,552bytes.
- `.venv/bin/python -m lstm_data.hf_hourly --metadata-only --revision ad48edaf3828ec855ab4a5bb1b8336fa0b68cdec --out reports/data_audit/ta_hf_twelvedata_hourly_2026-10-16_123344_final/metadata_only_smoke` — exit0;9small requests,637,935body bytes, no Parquet download. SOURCE_NOT_ACQUIRED in this smoke means this invocation was metadata-only, not that the separate verified cache is absent.
- `.venv/bin/python -m lstm_data.hf_hourly --help` — pass.
- `.venv/bin/python -m pytest tests/test_hf_hourly.py -q` —13passed,2.46s. Includes early-close/DST, duplicate/schema/OHLC, split-boundary cases, byte-cap-before-network, immutable cache/resume/corruption, label-free geometry and complete-session/stub warmup oracle.
- `.venv/bin/ruff check .` — All checks passed.
- `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist` —227project-owned files,0errors,0warnings,19.975s; exact JSON retained. No suppressions/severity reductions/exclusions added.
- Editor verification remains human-confirmed: select repository `.venv/bin/python`, restart Pylance, refresh Problems, confirm zero project-owned error diagnostics. CLI parity passed; editor confirmation is not asserted.
- Native acquisition:12requests/21including redirects,160,583,876body bytes,7.412s; three full Parquet transfer responses4.742s combined. Including source snapshots and metadata smoke:32instrumented requests/47including redirects,161,277,907body bytes;5additional manual preflight requests;1sandbox DNS failure then authorized escalation;0automatic retries. Web research HTTP bytes are unmetered and explicitly separate.
- Arrow emitted sandbox sysctl cache/NEON probe warnings; scans/tests completed. Early timezone-aware wall-format benchmarking was slow and interrupted; vectorized naive-wall formatting preserves original UTC keys and resolves that performance issue. No large model regression suite run for source-only work.

## 11. Experiment/results summary

No empirical model experiment. Conditional primary20: VZ,COP,BAC,BA,AAPL,PEP,MRK,SBUX,CVX,MS,AMD,KO,JNJ,AMZN,XOM,WFC,AVGO,TSLA,MA,CSCO. Backups:NKE,V. Longest practical month-boundary common interval2022-06-01–2026-10-15;22qualifying names after disclosed issuer exclusions. Primary cohort has131,214usable/131,220expected stock-hours (99.9954275%),6missing stock-hours across5common positions;6,556positions have all20usable rows.

Reserve warmup2022-06-01–2022-11-30:127exchange sessions,126complete regular sessions. Proposed train2022-12-01–2025-03-28:582sessions,1,073common48h+4h origins; development2025-03-31–2026-01-06:194sessions,382origins; held_out2026-01-07–2026-10-15:195sessions,390origins. All proposals require independent methodology/rights/action resolution. These are source geometry counts, not calculated targets or certified execution opportunities. Original AAPL/SBUX included; COST present but fails common coverage; CMCSA/CME absent. No predictive/trading metric was calculated.

## 12. Reproduction instructions

Use the repository's documented .venv setup/dependencies, no new credentials. From repository root, choose a NEW output directory for each invocation:

```bash
.venv/bin/python -m lstm_data.hf_hourly --metadata-only --revision ad48edaf3828ec855ab4a5bb1b8336fa0b68cdec --out reports/data_audit/hf_hourly_metadata_reproduction
.venv/bin/python -m lstm_data.hf_hourly --download-bars-1h --revision ad48edaf3828ec855ab4a5bb1b8336fa0b68cdec --out reports/data_audit/hf_hourly_reproduction --no-cached-comparison
.venv/bin/python -m lstm_data.hf_hourly --audit-cached --revision ad48edaf3828ec855ab4a5bb1b8336fa0b68cdec --out reports/data_audit/hf_hourly_offline_reproduction --no-cached-comparison
.venv/bin/python -m pytest tests/test_hf_hourly.py -q
.venv/bin/ruff check .
```

The download flag acquires only the three pinned files and reuses verified cache on rerun. --audit-cached does no network. Keep default250MBcompressed/500MBworking limits; respect local exploratory restrictions. Reproduce cached-Alpaca comparison only with documented existing original cache/reader bindings, otherwise skip it. No path in committed implementation depends on a username; the local editor extension path is intentionally machine-specific verification tooling only.

## 13. Git / collaboration status

Branch/HEAD unchanged and upstream0/0. Remote fetched at start. No Git index mutations, staging, commits, branch creation, integration or push. All task implementation/config/docs/report trees and this report remain uncommitted. No existing tracked diff. Preserve the cleanly separated local raw cache; never add licensed Parquets. Candidate future commit guidance, if separately authorized: review listed new source/config/test/template files and compact reports including this session report; exclude ignored raw files, then commit on a named branch and use a PR. Do not merge/push automatically. Likely conflict surfaces: future CLI/config/docs work; no existing registry edits.

## 14. Known issues, risks, and limitations

Rights/adjustment/issuer/PIT publication holds prevent input migration and model authorization. Source quality selection is retrospective survivorship conditioning; static publisher sector ETFs and large-cap claim are not independently verified historical sector/liquidity evidence. Coarse month-boundary search is a declared practical interval search, not a claim that every possible daily interval was optimized. Raw held-out quality was inspected, so freeze model-outcome boundaries before modeling. Native30-minute constituents and original FT0 source lineage cannot be reconstructed. Stub row presence does not certify actual terminal duration or original daily/EMA warmups. Training target feasibility is conditional on a separate hourly-native methodology. Memory374.4MB and task storage~164.5MB were observable below budgets; source requests and web research have separate accounting. No failing focused tests/type diagnostics; editor refresh remains human-confirmed. Publisher source/data-build relationship unverified. No provider/fallback acquisition occurred.

## 15. Decisions requiring human or teammate review

Choose whether to pursue a separately scoped hourly-native methodology plus rights/action resolution for this conditional cohort, or hold this source and separately authorize a sampled-month1minute fallback pilot. No live approval is needed to end this authorized audit. No future training, migration, rights certification or protocol change is implied.

## 16. Next recommended steps

Read NEXT_DECISION.md and source_suitability_and_rights.md. Resolve underlying use/modeling/redistribution rights and adjustment/volume/dividend/publication evidence. If proceeding, approve a separate feature/target/stub/action methodology and freeze cohort/splits before any model selection. Otherwise authorize only a narrow fallback pilot in a new task. Preserve all original candidates and28/200ledger.

## 17. Artifact inventory

`reports/data_audit/ta_hf_twelvedata_hourly_2026-10-16_123344_final/artifact_inventory.csv` lists every implementation/config, summary, source-policy snapshot, preliminary namespace and ignored raw cache file at inventory time with SHA256. Final decision, census/month/year/calendar tables, coverage/schema JSON, chronology and origin geometry, source suitability, actions,12overlap ratios, nominal interval diagnostics, HTTP/manifests, preservation/zero-fit evidence, resources and test/type receipts are compact reviewable uncommitted artifacts. No plots/checkpoints/features/labels/model outputs were created. Local single-copy raw Parquets remain ignored and must not be redistributed. This session report and final inventory/test receipts supplement the recorded inventory; the inventory does not self-hash.
