# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-10 ET; preservation snapshot 20:45:58; response 20:53:53 ET / 2026-10-11 00:53:53 UTC.
- Contributor/session: Codex, P1.3B bounded formation-first evidence.
- Requested: one small primary-stock preformation daily probe, diagnostics, explicit human handoff.
- Branch: `feat/track-a-data-intake`; starting HEAD `bf767746f6757c7e04a9abe86c45f043c906da31`; ending HEAD `6127cbcbc79fd72d7d16b848f1e0d0d378bdfcea`. This agent created no commits. Concurrent external commit `6127cbc` (`P1.2 complete`) committed the pending predecessor artifacts during this session.
- Start: tracked ledger modified; P1.1, P1.2, P1.3A packages/session reports untracked, nothing staged. End: those bytes preserved and now committed externally; new P1.3B package/session untracked and one further uncommitted ledger event, nothing staged.
- Remote fetched; initially 0 ahead / 0 behind, finally 1 ahead / 0 behind following external commit; no issue/PR.
- Snapshot-to-final-verification elapsed: **725.6 seconds**, includes escalation wait, excludes preceding Git/document inspection. Incremental persistent report/ledger bytes: **73609**. Seven new files; largest **26065 bytes**. No new large data files.

## 2. Executive summary

One successful SIP/raw daily response supplied 300 records across the fixed 60-session formation window. Daily source quality passed narrowly. All price-volume proxies exceed the reference, with stable diagnostic ranking, but estimator/vintage qualification and eligibility remain blocked. Provider aggregation rules show extended-hours volume and unequal OHLC/volume filters. No raw panel duplication, bulk acquisition, production changes, stock selection or scientific gate approval. See package artifacts for numerical tables.

## 3. Research/protocol impact

No research formulas, universe, dates/splits, features, targets, costs/trading, models/search, lookback/warmup, D8 pair or final-test policy changed. Five authority bindings and pointer verified unchanged; protocol hash `119513911f3f7fb1c51cb93381e3f5ebae6b8939bac8e056bf53448726ceb843`. The probe uses explicitly requested formation-date `asof=2020-07-01`, replacing P1.3A's suggested 2025 entity mapping only in its request. No repository configuration amendment or historic-vintage claim. All seven original blockers remain active; G0–G2 BLOCKED, G3–G9 NOT_RUN, 0/40 fits. No confirmation outcomes accessed.

## 4. Files created

Under `reports/data_audit/p1_3b_2026-10-10_204558/`:

- `probe_plan.json`: persisted predeclared endpoint, full parameters, range/session set, budgets and stop conditions. One planned request; optional six-attempt cap is not six requested probes.
- `probe_results.json`: response/count/hash/transport metadata, five illustrative raw rows with source locators, per-name quality/means/sums, unapproved rankings, arithmetic and provenance limitations. No full panel or auth headers.
- `formation_matrix.md`: compact diagnostic matrix and two hand calculations; no eligibility decision.
- `checks.json`: 14 validated existing-schema checks, independent statuses, inherited code/config/source identities, budget and preservation references.
- `package_report.md`: observed/unresolved evidence, costs, decisions and next recommendation.
- `human_review_card.md`: four direct inspection targets, three decisions and stopping boundary.

This mandatory session report is the seventh new file. Ephemeral scripts in `/private/tmp` are local inspection tools, not committed helpers or hidden project runtime dependencies. No spreadsheet/CSV artifact, app code, tests, persistent downloader, dataset or duplicated raw response was added.

## 5. Files modified

`reports/audit/track_a_events.jsonl`: one P1.3B/G1 WARN audit event `p1.3b-formation-2026-10-10-204558`, `blocks=[]`, `supersedes=[]`. Previous ten-event ledger preserved as an exact byte prefix; eleven events, seven unchanged blockers, zero fits. Existing P1.1/P1.2/P1.3A events and report files untouched.

## 6. Files deleted, renamed, or moved

None. No cleanup/stash/restore/reset operation.

## 7. Critical functions, classes, variables, and config keys

No application interfaces changed. Inspected existing `alpaca.credentials` (`src/lstm_data/alpaca.py:24`), `HistoricalClient` (`:57`), `_request` (`:70`) and `bars` (`:147`); injected transport enforces the exact planned query, captures redacted provenance, and rejects further calls/pages. Existing client pagination/retry behavior and failure tests were read before execution. Local execution-only overrides: one page, one attempt, 10-second timeout, 30 requests/minute; persisted config unchanged.

Reused `calendar.schedule` (`src/lstm_data/calendar.py:9`), `validation.normalize` (`src/lstm_data/validation.py:24`) and `defects` (`:39`); source order was checked from the provider lists before client sorting could obscure it. Existing `audit.protocol_check` (`src/lstm_data/audit.py:121`), `make_check` (`:244`), `validate_check` (`:217`) and `ledger.append_event` (`src/lstm_data/ledger.py:281`) construct validated evidence and the single append. No production alignment/actions/label logic used.

## 8. Data/schema/provenance changes

No raw source schema/store changes. New reports record only source evidence and aggregates. Probe: five canonical primaries, 60 XNYS sessions April 6–June 30, 2020; raw OHLCV, UTC stamps shown in ET, SIP/USD, formation-date entity mapping. Daily period label and contemporary HTTP response time remain distinct from unavailable historical publication. Five samples retained; source hash and row locators permit review but cannot reconstruct a mutable provider vintage without repeating the bounded query. Full response used in memory only; no retained immutable response bytes were necessary for the checked invariants.

Daily extended-hours eligible volume and separate OHLC filters prohibit treating proxies as D4 RTH volume or guaranteed turnover bounds. Split product identity is algebra only; events in this window remain unknown, and dividend/share/cash bookkeeping remains absent. User says course CSV was instructor-supplied Dukascopy export; preserved as user testimony, not independent instrument/contract validation. No course read/download/inquiry performed. Membership remains undefined; no substitute S&P membership or waived condition.

## 9. Dependency/environment changes

None. Existing environment/client/dotenv only; local approved authentication loaded without printing. No install, secret/config change, account/trading/billing operation or subscription purchase. The sandbox network attempt failed; command escalation was explicitly approved and its prefix saved by the tool. Same query retried once outside the sandbox; no provider retries, feed fallback or pagination.

## 10. Commands and tests run

- Required Git status/branch/HEAD/remotes and `git fetch --all --prune`: successful; aligned upstream, prior dirty work preserved. Scoped AGENTS, authority, handoff/client/schema/test reads; no blind pull or broad data audit.
- `.venv/bin/python -B /private/tmp/lstm_p1_3b_prepare.py`: exit 0, protocol binding/calendar/predeclared query and preservation snapshot recorded.
- `.venv/bin/python -B /private/tmp/lstm_p1_3b_probe.py --execute`: exit 2, no HTTP response due to sandbox/network transport; counted as one conservative authenticated transport attempt.
- `.venv/bin/python -B /private/tmp/lstm_p1_3b_probe.py --execute --sandbox-retry`: explicitly approved escalation, exit 0, one HTTP 200, 300 rows, five samples, no continuation. Probe execution 0.229 seconds; raw response 33,288 bytes, preserved by hash only. Two attempts total, one response, ceiling six. No further source call warranted.
- Independent integer-cent recomputations of AAPL/JPM April 6 close×volume and synthetic split paired product: PASS; exact inputs/results in formation matrix and probe evidence.
- `.venv/bin/python -B /private/tmp/lstm_p1_3b_reports.py`: exit 0, 14 check records validated, one non-clearing audit append, 11 events / 7 blockers / 0 fits.
- `.venv/bin/python -B /private/tmp/lstm_p1_3b_finalize.py`: final schema, arithmetic, protected-file/raw-stat, ledger prefix/blocker/budget/source-hash and Git-scope verification PASS.
- `git diff --check`: PASS; tracked diff and final status reviewed. No pytest/Ruff rerun: no app/test changes; prior P0.2 94 tests, P1.1 22 focused and P1.2 five focused passes are inherited evidence. No known failing invariant. Live daily coverage PASS is not a scientific gate result.

Public documentation: exact official bars reference/aggregation FAQ reads only; no instrument literature search. Two guessed stock-pricing documentation paths were inaccessible; the actual FAQ supplied aggregation semantics. These public reads are outside the authenticated source-call count.

## 11. Experiment/results summary

No forecasting/trading experiment or performance metric. Only formation-window source and proxy diagnostics; report-eligible source facts versus unapproved retrospective research assumptions are separated. No return labels, training, test-period outcomes or backups queried. All numerical comparisons are in the package matrix, not repeated here.

## 12. Reproduction instructions

Use README's authoritative environment route. Read the six package files with no credentials/network required. Calendar window is the last 60 XNYS sessions through June 30, 2020. Each exact mean is its persisted sum divided by 60; reproduce the two examples via integer-cent arithmetic. Daily aggregation semantics are linked to primary provider documentation in the package.

Any later source re-query needs separate human authorization; exact query/stop parameters are in `probe_plan.json`, not an instruction to automatically execute. Supplying documented local Alpaca environment secrets and the existing client suffices technically, but today's history can change and does not restore 2020 publication. Temporary scripts are not needed to consume/review evidence, and have no portability role in the project's final pipeline.

## 13. Git / collaboration status

Same branch; HEAD advanced externally from `bf76774` to `6127cbc` (`P1.2 complete`) while reports were being finalized. That commit contains only the 23 predecessor report/ledger paths; no code/protocol/config change. Its committed ledger is exactly the ten-event starting byte prefix. All protected predecessor bytes remain unchanged. Initially aligned upstream, now 1 ahead / 0 behind. This agent did not stage/commit/push/switch/merge/rebase/reset/stash/delete. No staged files at end. Tracked working diff from current HEAD contains just this session's one audit row; P1.3B package/session remain untracked.

Separate Git decision needed for P1.3B and any push. Predecessor integration occurred externally, so no automatic reintegration is needed; it does not constitute scientific sign-off. Exact P1.3B manifest: six files under its package directory, this session report and the central ledger append. Suggested future focused title: `docs: record bounded P1.3B formation evidence`. Re-fetch/recheck divergence before separately approved push/PR. Central ledger is the concurrent-writer conflict point; do not discard history or amend the external commit.

## 14. Known issues, risks, and limitations

Unapproved proxy/vintage qualification prevents formation PASS despite complete diagnostic inputs. Eligible extended-hours/volume filters differ from RTH and OHLC extrema. Historical availability, mapping/vintage truth, all action dates/share/cash treatment, minute coverage/retries, warmup and full-study retention remain unverified. No action-free-window assertion. Unknown USA500 exact contract/membership/timing, unchanged F01 defect and shared D3 sign-off remain independent. Feed request provenance is explicit, but response has no feed echo; headers do not identify account SKU or assure future limits. No billing evidence encountered, no billing verification undertaken.

Preservation uses 44 small protected-file hashes and 138 raw/data file-stat identities with established prior source hashes, not a fresh 60-file raw rehash. Five examples/hash/aggregates are deliberately insufficient to reconstruct all 300 response rows offline; upstream corrections need a new authorized source-evidence version. No known application test failure introduced.

## 15. Decisions requiring human or teammate review

Three explicit choices: provisional raw close×vendor daily-volume proxy versus qualified RTH/turnover evidence; justified present-history formation assumption versus required vintage evidence/HOLD; approve a separate Dukascopy source-contract verification through existing owner/export questions versus HOLD. These choices have no implied universe/D8, bulk, label/model, Git or gate approval. Shared D3 collaborator sign-off and eventual actions accounting require their own decisions.

## 16. Next recommended steps

One recommendation: separately scope Dukascopy source-contract verification, now that the bounded daily window is complete, using the existing unsent inquiry/export settings. Do not launch a redundant P1.3C probe until its missing source field is specified. No additional package/acquisition begins automatically.

**STOP — AWAIT HUMAN REVIEW.**

## 17. Artifact inventory

Six compact P1.3B package files plus mandatory session report: untracked, intended for review/tracking. Central ledger tracked with one pending P1.3B audit event; predecessor outputs/events committed externally and byte-preserved. Original course/canonical/pilot raw data intentionally local/ignored and untouched. No large artifacts, raw response file, parquet store, checkpoint, model, plot, label cache, per-seed/window copies or persistent helper.
