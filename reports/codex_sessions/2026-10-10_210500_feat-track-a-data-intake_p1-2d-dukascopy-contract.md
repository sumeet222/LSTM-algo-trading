# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-10 ET / 2026-10-11 UTC; local output/preservation snapshot 21:05:00.
- Contributor/session: Codex, P1.2D Dukascopy export-contract verification.
- Requested: bounded official documentation review, optional tiny comparison only if qualified, timing audit and unsent instructor draft.
- Branch: `feat/track-a-data-intake`; starting/ending HEAD `f9b93cc7e12d8f4762282894d9ea497f4f47846e`; no agent-created commits.
- Start: clean, nothing staged/untracked; remote fetched, 0 ahead / 0 behind. P1.3B had been committed and pushed separately (`f9b93cc`, `P1.3 except USA500`). End: one ledger append, six new package files plus this untracked report; nothing staged. No issue/PR.
- Snapshot-to-final verification: **264.6 seconds**, excludes preceding document/Git/web review. Incremental persistent report/ledger bytes: **64930**; largest new file **30317 bytes**. Actual source-price/authenticated calls and retries: 0.

## 2. Executive summary

Documented official provider context separately from the user-attested course export. Exact export side/clock/daily close/vintage remain unknown. Stopped without source sampling because no exact permitted credential-free query was established. Reused two P1.2 locators for conditional summer/winter timestamp arithmetic, shortened the instructor inquiry to three questions, and described a separately authorized blocker-preserving F01 repair boundary. No source/code/protocol changes or scientific gate approval.

## 3. Research/protocol impact

No change to TG0, dates/splits/confirmation, 48×16 FT0, U1–U5, masks, 240-minute Track A clock, universe, costs/portfolio, models/search/budget or conditional activation. All five pinned authority bindings PASS, protocol hash `119513911f3f7fb1c51cb93381e3f5ebae6b8939bac8e056bf53448726ceb843`, pointer unchanged. No collaborator D3 sign-off inferred. G0–G2 BLOCKED; G3–G9 NOT_RUN; seven original blockers and zero fits preserved. CFD membership interpretation is a joint human question, not a D1 amendment.

## 4. Files created

Under `reports/data_audit/p1_2d_2026-10-10_210500/`:

- `package_report.md`: provider/export proof boundary, skipped sampling, costs, blocker disposition and one next action.
- `dukascopy_contract_delta.md`: classified fields, official URL/section/retrieval references, two inherited OHLC/line locators and conceptual D2/F01 timing.
- `instructor_export_questions.md`: three-question ready-to-send draft, NOT SENT; separate research assumptions/amendment decisions.
- `checks.json`: 14 existing-schema partial-status checks, inherited identities/independent blockers, conditional timestamp calculations and zero-call accounting.
- `human_review_card.md`: five concrete checks and human choices.
- `preservation.json`: compact offline protection, ledger/source binding, Git and report-byte results.

This mandatory session report is the seventh new file. No `evidence.json` created because there was no source sampling/new source row. Temporary `/private/tmp/lstm_p1_2d_*.py` tooling is local inspection only, not a committed helper or hidden final-pipeline dependency.

## 5. Files modified

`reports/audit/track_a_events.jsonl`: one non-clearing G1/P1.2D BLOCKED audit, `p1.2d-dukascopy-contract-2026-10-10-210500`; `blocks=[]`, `supersedes=[]`. Eleven prior events are an exact byte prefix; twelve events total, seven identical blockers, 0/40 attempted fits. Contract delta and existing P1.2 evidence hashes bound in the event. No prior source inquiry/report edited.

## 6. Files deleted, renamed, or moved

None.

## 7. Critical functions, classes, variables, and config keys

No production interfaces changed. Reused `audit.protocol_check` (`src/lstm_data/audit.py:121`), `validate_check` (`:217`), `make_check` (`:244`); `calendar.schedule` (`src/lstm_data/calendar.py:9`) checks only the two selected dates; `ledger.append_event` (`src/lstm_data/ledger.py:281`) enforces safe append. Inspected existing `alignment.asof_diagnostic` (`src/lstm_data/alignment.py:10`, faulty age at `:51`) and `audit.f01_fixture` (`:276`); neither executed on course data or changed.

Two independent `datetime`/`ZoneInfo` calculations use inherited UTC stamps, not guessed export metadata. Conceptual future contract: explicit documented period end, independently evidenced availability and each historical cutoff; unknowns remain blocked. No fixed source delay or schema/API implementation adopted.

## 8. Data/schema/provenance changes

Raw data/schema unchanged. Reused P1.2 `course-line-123` and `course-line-15929`, original OHLC text and physical CSV locations; no raw CSV read, 29,510-row scan, raw rehash or new dataset. Inherited Task01 course source hash and manifest reused. No price matching, alternate provider, S&P membership, or 2024–25 outcome access.

Dukascopy origin remains USER_ATTESTED; official provider facts and course settings have distinct classifications in the delta. Current provider schedules and generic JForex documentation are not historical/export-specific contracts. Native :00 labels retained; daily-close/availability/prehistory/compatible U1–U5 histories not certified. Volume remains unused. Historical first publication is null, not inferred from interval end, retrieval or file mtime.

## 9. Dependency/environment changes

None. No installation/lock/config changes, .env/credential access, API key procurement, account/subscription/payment or provider contact. No production client used. Standard existing Python environment only.

## 10. Commands and tests run

- Actual `AGENTS.md` read; `rg --files -g AGENTS.md -g '!data/**' -g '!.venv/**'` found root only. Relevant five authority sections, P1.2/P1.3B handoffs/source metadata and existing audit/alignment interfaces inspected.
- `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD`, `git remote -v`, `git fetch --all --prune`, `git rev-list --left-right --count 'HEAD...@{upstream}'`: successful, clean/aligned start; no integration action.
- Public documentation: seven web-tool calls; six searches and 24 open/click/find operations. Actual HTTP/cache/search backend totals are not exposed; no claim of 30 wire HTTP calls. No historical-price HTTP calls/retries/authentication. Official primary material alone used; nonofficial search results ignored. Dynamic instrument detail/API landing supplied no usable schema, so generic listing/wiki/javadocs retained as bounded evidence.
- `.venv/bin/python -B /private/tmp/lstm_p1_2d_prepare.py`: exit 0, pinned protocol binding and 52 small-file hash / 138 data-stat baseline saved.
- `.venv/bin/python -B /private/tmp/lstm_p1_2d_build.py`: exit 0, two regular-session/UTC–ET calculations PASS; summer −04:00 and winter −05:00 yield stipulated start-label ages −30/30 and close-label ages 30/90 at the two cutoffs. 14 audit-check records validated; inherited F01 fixture reused, not rerun; single non-clearing append succeeds.
- `.venv/bin/python -B /private/tmp/lstm_p1_2d_finalize.py`: report/schema/source-reference/hash, protected-file/data-stat and ledger-prefix/blocker/budget/Git/byte checks PASS.
- `git diff --check`: PASS; final tracked ledger diff and Git status reviewed. No pytest/Ruff/full source audit rerun. Prior P0.2 94-suite, P1.1 22 focused and P1.2 five focused test passes are inherited evidence only. No known failing invariant introduced; F01 remains intentionally unresolved.

## 11. Experiment/results summary

None. Provider documentation and conditional timing are source-contract evidence, not U1–U5 eligibility, model/trading performance, profitable-strategy evidence or final confirmation. Optional comparison NOT_RUN; no numerical provider match/mismatch claimed.

## 12. Reproduction instructions

Use README setup; package review needs no secrets/network/downloads. Inspect the delta's official URLs/sections and retrieval date, existing P1.2 source locators and checks' conditional examples. Convert 2020-07-08 14:00 UTC to 10:00 EDT and 2023-03-10 15:00 UTC to 10:00 EST; calculate stipulated end/cutoff ages. Those independent calculations do not choose a course interpretation. No temporary script required to inspect the result.

Read the NOT SENT instructor draft before any separately authorized communication. Later source/repair work needs a concrete reviewed contract/scope and separate authorization; do not automatically fetch or infer source delays.

## 13. Git / collaboration status

Same branch/HEAD and 0 ahead / 0 behind after fetch. P1.1/P1.2/P1.3A/P1.3B are already tracked at current HEAD; their historical reports' pending-work statements are historical and must not be replayed. No concurrent change detected. Nothing staged/committed/pushed/merged/rebased/reset/stashed/cleaned/switched/deleted by this agent.

Minimal eventual add manifest: six package files under `reports/data_audit/p1_2d_2026-10-10_210500/`, this session report and central ledger. Git approval separate; suggested focused title `docs: record P1.2D Dukascopy export contract review`. Do not stage unrelated work; re-fetch/recheck before an authorized push/PR. Central ledger remains concurrent-writer-sensitive.

## 14. Known issues, risks, and limitations

Provider-general information cannot authenticate original instrument/side/export options or historical session/availability. No exact permitted public sample request qualified. Web tool does not expose physical HTTP call/cache counts. Source terms' course-specific license/redistribution scope remains unverified, not a legal opinion. Current docs cannot certify 2020–25 publication/revision history or prehistory. Membership may need a joint protocol decision only after identity confirmation. Daily inputs/hourly compatibility still block market features; F01 and shared D3 remain independent.

Protection is small-file hashing plus unchanged raw file stats/established hashes, not new raw-byte revalidation. No new source observations were available to compare; retained course examples come solely from P1.2. No loss or known new failure.

## 15. Decisions requiring human or teammate review

Obtain original export settings through the prepared inquiry or HOLD; if publication evidence cannot be recovered, decide an explicit conservative assumption/disclosure or continued hold rather than guessing. Authorize/defer a separate isolated F01 repair with unknown metadata still blocked. Jointly settle conditional membership if a CFD is confirmed. Sending the draft, changing research protocol and Git integration are separate authorizations; shared D3 collaborator sign-off remains separate.

## 16. Next recommended steps

One next action: researcher review the shorter unsent draft and obtain export settings/handout through separately authorized communication. No automatic F01 repair, P1.3C expansion, features/joins, models or confirmation access.

**STOP — AWAIT HUMAN REVIEW.**

## 17. Artifact inventory

Five small content/check artifacts plus compact preservation and this session report: new/untracked, intended for scoped review/tracking. Ledger tracked with one pending audit event. All predecessor reports tracked/unchanged; raw source/canonical/pilot data local/ignored and untouched. No price response, parallel dataset, checkpoint, model, feature/window cache, plot, spreadsheet or persistent helper.
