# Codex Session Report

## 1. Session metadata

- Date/time: 26 October 2026, America/New_York; this session spans 25–26 October.
- Contributor/task: Codex, S3 non-training preflight and the subsequent live eligibility amendment.
- Branch: `feat/track-a-data-intake`.
- Starting/ending HEAD: `353402daa11704cdcdea3a7265c51aeb33afaa3e`; no commits.
- Initial tree: clean, cached upstream 0/0. Final tree: two new modules, one test module, one report namespace and this session report, all uncommitted. No pre-existing work changed.
- Git status, branch, SHA, remotes and cached ancestry inspected. Fetch skipped under the task's network restrictions; cached ancestry is not a fresh remote guarantee. No issue/PR, staging, stash, reset, integration or publication.

## 2. Executive summary

The first source audit correctly blocked mandatory common-population fitting: it removed substantial support and left F24 inner validation with 42 sessions. The user then expressly amended the design to use independent h1/h2/h4 eligibility for primary fitting/evaluation and a secondary common evaluation population.

The amended source audit passes all 12 horizon/year validation-session gates and 24 slot-origin gates. F24 now has 66/64/74 validation sessions for h1/h2/h4, with 107/93/111 origins. No minimum was lowered. Within a horizon, S3-A and S3-B masks and weights are identical. All 16 original h4 role populations and archived outcomes remain unchanged. Original h4 returns and all eight phase-scaled M2 arrays reproduce exactly.

No empirical model fit, new real h1/h2 normalizer, candidate checkpoint or ledger reservation occurred. Ledger remains 74/200. All 5,847 bound prior/source/config/checkpoint files remain unchanged; protected 2026 files were byte-hashed only, never numerically decoded. The amended design is ready for human review, not live fitting.

An operational mistake must remain disclosed: an early inherited test selection made 42 AdamW.step invocations and one LBFGS.step invocation on disposable synthetic fixtures. This exceeded the literal zero-update instruction, despite no empirical model or ledger change. It was not repeated. Final guarded verification passed 38 tests with four optimizer-using cases deselected and zero step calls.

## 3. Research/protocol impact

The live amendment supersedes only mandatory intersection fitting. Each horizon uses its own genuine endpoint/basis mask with the original FT16 input/source-quality mask, calendar, cutoffs, 48-step embargo and conservative four-hour maturity cutoff. Missing h4 prices no longer exclude legitimate h1/h2 examples. A/B keys are identical within each horizon. The original two morning forecast schedule is preserved; no early-close, afternoon or overnight origins were added.

The secondary intersection controls evaluation composition, not estimation history. It does not make the horizon-specific training populations identical. Its F24 validation subset still has 42 sessions and must never select epochs/penalties or waive the 50-session primary requirement.

No stock, target-start convention, architecture, optimizer, selector, seed, trading policy or confirmation boundary changed. The proposal keeps both shorter horizons and both T2R/NR objectives in A/B. The latest instruction requires amended eligibility design approval first. The sealed card has `fit_permission=false`; it grants no empirical fit authority. P2's 16 deferred entries were read/hash-verified and not cleared.

## 4. Files created

- `src/lstm_data/hf20_horizon_math.py`: target endpoint/source masks, amended role masks, log-return arithmetic, strictly historical M2, P020 normalizer rules and single-channel replacement. No fitting entrypoint.
- `src/lstm_data/hf20_horizon_preflight.py`: read-only journal/source/identity audits, the separate amended audit and disposable zero-update shape/gradient/reload rehearsal.
- `tests/test_hf20_horizons.py`: nine focused tests for horizon clocks, DST/weekends/stubs, raw-return/rank arithmetic, historical M2, missing runs, normalizer masks, other-channel identity, independent horizon membership and protected/unknown requests.
- `reports/experiments/hf20_s3_horizons_2026-10-26_000127_preparation/`: original instructions, preserved initial block, canonical `eligibility_amendment_v2/`, sealed proposed card, 32/72 prospective task lists, role/membership/clock/exclusion/native support tables, witnesses, tests/static/verification receipts and readable reports. `artifact_inventory.csv` enumerates every file, purpose, type, size, SHA and Git intent.
- This mandatory report, also copied as `WORK_SESSION_REPORT.md` in the namespace.

## 5. Files modified

No previously tracked file changed, including raw data, old checkpoints, source code, recipes, journals and CURRENT registry. New agent-owned preparation code/reports evolved during this session. The original intersection audit remains at root; amended primary evidence is separately versioned. Three initial pandas/tuple typing diagnostics were corrected without changing mathematical behavior or suppressing diagnostics. Exact live amendment text was retained before sealing the card.

## 6. Files deleted, renamed, or moved

None. No source, private cache, historical result or unknown work was discarded. No destructive Git operation.

## 7. Critical functions and configuration

- `endpoints`: scheduled full-hour h1/h2/h4 edges; rejects stubs, session jumps and post-2024 grids before price lookup.
- `target_support`: source-only genuine entry/exit and equal price basis, computed before returns or model outcomes.
- `horizon_roles`: independent horizon masks plus original input/clock/embargo and conservative four-hour maturity. H4 full-array equality is checked; A/B share the same masks.
- `historical_m2`: previous regular-day same-origin histories, fixed 20/60 windows, minimum 19/57 observations, maximum two consecutive misses, RMS denominator, original COP mask. No current-day future outcome is consumed.
- `m2_parameters` / `target_parameters`: exact P020 rule family; exercised on synthetic data only. Real new h1/h2 parameter estimation is not activated.
- `substitute_m2`: replaces channel index 1 only and asserts bitwise equality of the other 15 channels.
- `ledger`: verifies all 20 historical journal chains and 74 actual starts; only writes audit reports, never the real journal.
- `amended_audit`: 48 complete memberships, identical A/B hashes, unchanged support gates, clocks/recipe bindings, bounded feature gathers and nonempty M2 prefix pools.
- `synthetic_rehearsal`: 32 prospective configurations with finite gradients, unchanged weights, memory-only reload, empty optimizer state and fresh seed identity. Its process patches optimizer.step to raise.
- `S3_FROZEN_EXPERIMENT_CARD.json`: sealed unapproved scientific proposal; 32 future neural and 72 future baseline tasks, zero reserved/started. Maximum 106/200 only if subsequently authorized and all starts occur.

The legacy FoldData constructor flag is used solely for already-authorized local source reads under a patch that rejects new phase fitting. It is not a fabricated live-fit approval.

## 8. Data/schema/provenance

Pinned source revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`, P019B/P020 lineage and contract `7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5` remain unchanged. Numerical reads are filtered through 2024-12-31. Source availability, action vintage, fixed surviving universe, bounded private-use rights and PIT limitations remain conditional.

Labels retain genuine completed-hour log ratios. Issuance is entry end plus two minutes, so the historical label begins before modeled issuance; this does not prove executable returns. The actual vendor available_at remains unknown. No label proxy/fill or volume/action repair was invented.

New evidence is compact metadata: 48 memberships, 288 role/slot/arm cells, 960 M2 prefix-pool counts and 96 native/fallback sets. No duplicated minute database or materialized overlapping 48-hour model store. There are 22 source stock-events, 20 distinct origins, 13 sessions and 13 tickers, with 66 horizon rows. Eight replacements use source availability/year/slot/chronological order only. Repeated events are not counted as independent observations.

## 9. Dependency/environment changes

None. Existing .venv NumPy/pandas/PyArrow/Torch reused. CPU four intra-op/one inter-op, zero loader workers. No network/download, install, external service, secret/.env/credential read or trading. Runtime paths are project-relative. Requested absolute paths occur in the audit manifest; the Pylance extension path is local verification tooling only.

## 10. Commands and tests run

- Git status/branch/rev-parse/remotes/cached ancestry and `git diff --check`: pass, tracked diff empty.
- `load_deferred_work(configs/track_a_p2_engineering_handoff_v1.json)`: 16 entries/hash bindings verified.
- Required brainstorming/design/original S1/S2 briefs, final reports/index/receipts, actual P020/source/M2 code, original journals and monthly/recent36 context inspected. The old named staged-prompt Markdown remains absent as previously disclosed; exact original `submitted_instruction.txt` is used by hash instead.
- With `OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 VECLIB_MAXIMUM_THREADS=4`, `.venv/bin/python -u -m lstm_data.hf20_horizon_preflight --out reports/experiments/hf20_s3_horizons_2026-10-26_000127_preparation`: source/intersection audit complete, correctly blocked on population support; 49.33 seconds, peak 841,121,792 bytes. H4 identities, 288 independent M2 scalar checks and 32 guarded synthetic configurations passed.
- Same environment/module with `--amend --out reports/experiments/hf20_s3_horizons_2026-10-26_000127_preparation/eligibility_amendment_v2`: exit 0, 99.22 seconds, peak 880,115,712 bytes. All support gates and A/B identities passed; no new real fitting or checkpoint.
- Independent source/calendar reconstruction: all 48 masks/weight sums/exclusion partitions and 16 old h4 key sets match; all 5,847 prior byte hashes unchanged. Native support audit: 4.28 seconds, peak 773,718,016 bytes; six actual calendar witnesses and 22 genuine history-clock witnesses retained.
- Nine new tests passed in 4.52 seconds. An earlier unguarded full selection reported 42 passed in 13.49 seconds, but included the synthetic optimizer steps described below. Its log remains preserved and is not zero-update evidence.
- Final safe test command wraps `pytest.main` with patches making AdamW.step and LBFGS.step raise. Targets: `tests/test_hf20_horizons.py`, `tests/test_hf20_ranking.py`, and the two protected-read nodes in the receipt. Selection: `-k 'not synthetic_lstm_rank_learning_and_fresh_state and not rank_checkpoint_and_complete_epoch_rehearsal and not linear_solvers_recover_synthetic_rank_information' -q`. Result: 38 passed, four deselected, 7.38 seconds, zero step calls. Exact arguments are in `GUARDED_TEST_RECEIPT.json`. Existing tests were not edited or weakened; exclusions enforce current authorization.
- `.venv/bin/ruff check .`: all checks passed.
- `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist`: 456 project-owned files, zero errors/warnings, 78.128 seconds. No Any/cast/ignore/severity/exclusion workaround.
- Editor confirmation remains human-owned: select repository .venv/bin/python, restart Pylance, refresh Problems, confirm zero project-owned errors. CLI parity passed; editor state is not asserted.
- Nonfatal Arrow sysctl/cache/NEON warnings. Optional ps inspection was sandbox-denied; no escalation needed. Tool sessions and receipts verified completion. No automatic approval-review rejection.

## 11. Experiment/results summary

No new S3 predictive performance result. Stage 0 source/support passes; amended design approval pending, source-vintage qualified. Stage 1 bounded mathematical/synthetic rehearsal passes. S3-A/B fitting and empirical diagnostics are NOT_RUN. Preparation closeout retains the synthetic-test scope exception.

Validation sessions h1/h2/h4: F21 104/113/115; F22 73/78/87; F23 76/75/80; F24 66/64/74. OOS origins: h1 270/346/274/299, h2 257/330/241/281, h4 293/364/284/308. A/B keys match within each horizon. All old h4 roles and results remain intact. The common F24 validation subset still has 42 sessions but is never the selector. H4 subset IC differences are sample effects, not new model gains.

## 12. Reproduction instructions

Use the documented .venv and legitimate checksum-matched P019B/P020/S1/S2 private artifacts. Read README/card/reference bindings. The CLI exposes preparation only. Reproduce into a fresh namespace: original instruction and initial source index first, then the amendment child with exact live text and parent index. Do not overwrite this immutable receipt tree. Pure horizon math and saved membership indices support independent checks without neural inference.

Use the final guarded test selection above; do not run the unguarded full ranking file under zero-update authority. Any future empirical fitting requires explicit executable-bound live approval. Design approval alone is not fitting permission. Clean-clone data handoff, lawful redistribution and editor UI refresh are not certified.

## 13. Git / collaboration status

Branch/HEAD unchanged, cached upstream 0/0; no staging, commit, push, stash, reset or integration. Only two new modules, one test, this namespace and mandatory report are untracked. Private source/witness returns and caches stay local. Review focused source/tests/compact reports/session before any separately authorized commit; do not blindly stage the namespace. Likely conflict surfaces are future horizon/report helpers. No registry conflict was created.

## 14. Known issues, risks, and limitations

The inherited test-selection mistake made 42 synthetic AdamW.step invocations and one synthetic LBFGS.step call. Internal LBFGS iterations were not retained; do not claim a total of 43 optimizer updates. No market-data model, real checkpoint or ledger changed. The source/rehearsal process receipts' zero counts remain accurate only for those guarded processes. The disclosure and original log are preserved. Final guarded verification has zero step calls; no known focused/static failure remains.

Actual new normalizers and complete fit-driver activation remain unrun. H1/h2 shape-only use of old h4 scale parameters is explicitly not a candidate recipe. Future CPU/RSS/storage are estimates and must respect existing stricter 2 GB/1 GB/10 GB caps. New M2 fallback reaches 31.19% in one h2/B role; this is disclosed coverage, not a row-deletion rule. Source/publication/action/rights/survivor/issuance qualifications persist. No new early-close forecast origin, 2025 tuning or protected 2026 numeric access.

## 15. Decisions requiring human review

Approve or revise the sealed amended eligibility design in `S3_FROZEN_EXPERIMENT_CARD.json`. The latest live instruction expressly requires this approval. It is not a request to start models. Future empirical activation still needs its exact executable/authority gates and fit response. No lower validation minimum, wider tail or extra h4 fit is necessary to pass current support.

## 16. Next recommended steps

Review amended counts, exclusions, clocks, A/B/15-channel identities and the operational exception. Stop for amended design approval. Do not fit normalizers/models, reserve the ledger, release confirmation or launch S4/S5/S7/rolling LSTMs. Both A/B remain prospective inventory, not a performance-selected subset.

## 17. Artifact inventory

README indexes every useful report, role/source table, prospective task and verification receipt. `artifact_inventory.csv` lists every new path, type, purpose, bytes, SHA and Git intent. Closure binds the inventory/card/final verification and does not self-hash. No new empirical checkpoint or raw/window store was produced. Only bounded private source-event returns and masks/timing/keys are new. All work remains uncommitted; initial blocked audit and scope-exception logs remain preserved.
