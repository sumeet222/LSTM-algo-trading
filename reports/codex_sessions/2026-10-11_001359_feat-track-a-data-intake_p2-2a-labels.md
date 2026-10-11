# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-11_001359 America/New_York; end UTC in checks/event. Contributor: Codex P2.2A.
- Requested: synthetic minute-open/TG0/causal eligibility/maturity/purge interfaces; human checkpoint.
- Branch: feat/track-a-data-intake; starting/ending HEAD `f298c6c9ee4948efe389b6d761e582851f395933`. No commit, issue or PR.
- Start clean; P2.1 and previous reports integrated by collaborator. End exact files below, unstaged/uncommitted.

## 2. Executive summary

IMPLEMENTATION COMPLETE for synthetic deterministic P2.2A. One labels module, new tests, README API guidance, compact review package and one non-clearing ledger event. 157 integration tests pass; G2 scientific status remains BLOCKED. Zero source requests/rows/confirmation outcomes, no production targets/backtests/features/models.

## 3. Research/protocol impact

Implemented frozen TG0 formula and training-only floor; target/horizon, universe/order, feature math, splits, cost/trading, seeds/search remain unchanged. Only synthetic labels generated. Reported common240min/future-market agreement remains FORMAL REGISTRATION PENDING; prior signoff card not rewritten. Five authorities/CURRENT_PROTOCOL unchanged. G0/G1/G2 blocked, market HOLD, zero40-budget neural fitting pairs. Production inner-population adequacy and source/approval checks are not certified.

## 4. Files created

- `src/lstm_data/labels.py`: typed immutable records and exact source-reference, causal eligibility, later outcome, fixed chronological membership and floor functions. No source I/O or framework.
- `tests/test_labels.py`:28 synthetic cases with independent five-return/median/MAD/floor arithmetic, reference keys, C01, split, chronology and fail-closed guards.
- `reports/data_audit/p2_2a_2026-10-11_001359/package_report.md`: compact implementation/scientific distinction, resource use and next recommendation.
- `reports/data_audit/p2_2a_2026-10-11_001359/checks.json`:6 existing-schema G2 checks, code/config/protocol/source IDs, hashes and exact tests; overall BLOCKED.
- `reports/data_audit/p2_2a_2026-10-11_001359/target_trace_examples.md`: hand-computable synthetic five-name table, maturity/purge/C01 and explicit split/share example, no source data copies.
- `reports/data_audit/p2_2a_2026-10-11_001359/human_review_card.md`:6 exact code/test/trace review locations and approve/correct/hold instruction.
- `reports/codex_sessions/2026-10-11_001359_feat-track-a-data-intake_p2-2a-labels.md`: mandatory17-section handoff, exact Git path manifest and limitations.

## 5. Files modified

- `README.md`: labels API, training-only floor, source/action assertions, cutoff/maturity semantics and boundaries; no existing CLI/API behavior changed.
- `reports/audit/track_a_events.jsonl`:one P2.2A G2/BLOCKED audit, blocks=[],supersedes=[]; old17-event prefix exact,18events now. No inherited overlapping ledger edits.

## 6. Files deleted, renamed, or moved

None. No cleanup or raw edits.

## 7. Critical functions, classes, variables, and config keys

All new interfaces in `src/lstm_data/labels.py`; no config keys changed. UNIVERSE fixed AAPL/JPM/JNJ/WMT/CAT.

- MinuteReference(symbol,row_id,minute_start,raw_open,source_version,source,...): validates aware exactminute, positive finite open,raw adjustment,1min interval,SIP/synthetic source and clock basis; IDs/version retained. Source availability is optional and independent from timestamp/retrieval; ASSUMED retained but inactive. No publication latency inferred.
- minute_reference(rows,symbol,minute)->MinuteReference|None: exactkey lookup,duplicate failure, no substitutions.
- ForecastEvidence and causal_eligibility(plan,forecast,entries,*,test_scenario=False)->CausalEligibility: upstream fullfive input/source/clock assertion plus entry reference checks at entry. Future exits/action/floor never input; entry scope excludes portfolio admission. Rechecks plan against P2.1, including original cutoff/issuance/entry/exit.
- ActionScope/SplitFact: explicit covering five-name interval/no-action or time-specific share facts. Unknown/non-supported scope blocks; factors apply on(entry,exit] converting exit raw value to entry-share units. No dividend cashbook.
- label_sample(plan,forecast,entries,exits,*,observed_at,actions=None,test_scenario=False)->LabelSample: independent late five-name raw logs/centered values/median/unscaled MAD, source IDs/version, action/split IDs, maturity/basis and label reason. Missing returns stayNone. Maturity max(exit,all required supported reference availabilities); observed_at must reach it, causal inputs must be eligible. Unknown maturity blocks supervised/floor use even if math retained. execution_outcome NOT_EVALUATED/market HOLD/research_readyFalse.
- fitting_window(stage,phase,*,fitted_at)->FitWindow: WF1 throughJun2023,WF2 throughDec2023,PRECONFIRMATION throughJun2024; last63 actual exchange sessions for inner tail, not eligible-date selection. Exclusive next-period ETmidnight storedUTC, independent actualfit bound. No lookback embargo; adequacy50sessions/25each-origin deferred to production.
- fitting_membership(sample,window,*,test_scenario=False)->str: origin/maturity/outcome-boundary membership reason; synthetic use opt-in; per-origin reasons later aggregateable.
- fit_tg0_floor(samples,window,*,test_scenario=False)->FittedFloor: onlytraining phases and matured eligible origins, unique origin keys; fitted epsilon=max(1e-4,0.1*median(MAD)), hashbound scope/keys/MAD/maturity/source/action identity, exclusions. Empty/duplicate population fails. Floor fitting is deterministic preprocessing, not neural training.
- apply_tg0_floor(sample,floor,*,test_scenario=False)->TG0Target: frozen floor only, five scores, no clipping/refit; invalid or unverified label raises. No scientific executor.

## 8. Data/schema/provenance changes

No acquired raw rows inspected; optional schema probe unnecessary. Fake raw opens constructed in tests, taggedSYNTHETIC/fake-v1; fake input/action/publication assertions explicit. UTC keys, ET calendar boundaries. Actual calendar metadata includes fixed fitting dates, no confirmation price outcomes. P1 summary metadata reused:3minute sample days,168half-hour gaps,4cash-date records and fullminute preflight HOLD. No full-source hashes/scans/migrations/copies or empirically certified label store.

## 9. Dependency/environment changes

None. Existing pandas/exchange_calendars/pytest/Ruff; Python3.14.6. No .env or network required for tests. README setup remains authoritative.

## 10. Commands and tests run

- Git status/branch/HEAD/remotes inspected before editing; startclean. `git fetch --all --prune` first denied .git/FETCH_HEAD by sandbox; exact required escalated retry succeeded. Upstream0ahead/0behind. No pull/merge/branch mutation.
- `.venv/bin/ruff format src/lstm_data/labels.py tests/test_labels.py`: formatted new paths only. `.venv/bin/ruff check src/lstm_data/labels.py tests/test_labels.py`:PASS.
- `.venv/bin/python -B -m pytest tests/test_labels.py -q`:26passed4.11s; no failures. Then added two plan/key guards.
- `.venv/bin/python -B -m pytest -q`:single final fullsuite157passed30.51s, includes final28new cases. No repeated full suite.
- `.venv/bin/ruff check src tests`:PASS; `git diff --check`:PASS.
- Existing inspect(diagnose=True),check/safe-payload schemas and protocol identity verified; prior clock/frozen hashes preserved. Exact oldledgerprefix,17→18events,seven blockers and zero fits verified before/end append. One existing F01 fixture assertion in new tests; unchanged diagnostic.
- No raw/source clock inquiry,provider request,data hash rescan,price-performance evaluation,training or portfolio work.

## 11. Experiment/results summary

No empirical experiment/run/seed/metric. Synthetic logs(-0.02,-0.01,0,0.01,0.03),median0,MAD0.01,epsilon0.001,scores=r/0.011; zeroMAD epsilon0.0001. Tiny synthetic floor population is math-test evidence, not50-session production adequacy. C01 causalflags unchanged aftermissing/delayed futureexit. Source/maturity/protocol readiness not certified by passing arithmetic.

## 12. Reproduction instructions

Use existing clean-venv README setup (`python -m pip install -e '.[dev]'`); run `python -m pytest tests/test_labels.py -q`, optionally fullsuite and `ruff check src tests`. No data or secrets required. `tests/test_labels.py:27` constructs complete tagged examples; use label_sample/test_scenario, fitting_window/fit_tg0_floor/apply_tg0_floor as tested. Do not repurpose test fixtures as real market observations. Exact public API documented in README; genuine source integration is not provided yet.

## 13. Git / collaboration status

Branch/HEAD unchanged, clean start, fetch succeeded0/0. No staging/commit/push/PR/merge/rebase/switch/stash/reset/cleanup. Exact proposed review manifest, not executed:

```bash
git add src/lstm_data/labels.py tests/test_labels.py README.md reports/audit/track_a_events.jsonl reports/data_audit/p2_2a_2026-10-11_001359/package_report.md reports/data_audit/p2_2a_2026-10-11_001359/checks.json reports/data_audit/p2_2a_2026-10-11_001359/target_trace_examples.md reports/data_audit/p2_2a_2026-10-11_001359/human_review_card.md reports/codex_sessions/2026-10-11_001359_feat-track-a-data-intake_p2-2a-labels.md
```

No folder bulk staging/ignored data. README/central ledger likely overlap points; exact starting bytes checked immediately before append. Prior P2.1/RandomNotes protected from edits. Fetch/reinspect before separately authorized focused commit/normal PR workflow.

## 14. Known issues, risks, and limitations

No failing tests. Real historical source availability/full minute references,action/mapping/formation/168gap obligations,formal shared registration and market HOLD remain. Caller DOCUMENTED metadata is an assertion requiring supported evidence, not provider certification. P2.2A does not choose an assumed publication clock; no actual source samplecertification. Entry-minute opens inside a later retrieved bar do not prove contemporaneous availability or fillability. Source row locator/version integrity and action completeness need production evidence. Upstream FT0/five-name eligibility asserted only; P3 admission/risk/exceptions/cashbook unimplemented. Inner-tail adequacy and empirical datasets deferred. Date split midnight is pure membership; actual model/source readiness remains separate.

## 15. Decisions requiring human or teammate review

APPROVE / CORRECT / HOLD synthetic implementation. Supply/review actual source availability and comprehensive genuine minute references plus action/share/mapping coverage,formal clock/source registration before real labels. Future conventional S&P500 selection/amendment remains separate; no source chosen. Resolve next source bridge versus production P2.2B scope with explicitauthorization.

## 16. Next recommended steps

Separately approve a source-coverage/availability bridge first while measured blockers persist; P2.2B integration requires concrete source/maturity/purge and full eligibility/registration evidence. Keep supervised population distinct from causal entry population; future exits never delete prior entries. No automatic P2.2B/P2.3/features/backtests/models/market work.

## 17. Artifact inventory

7new files:module,test,4package files,thissession; 2modified files:README,ledger. Small tracked-ready artifacts only; no raw copies/checkpoints/charts/production labels. elapsed snapshot 539.0s from pre-edit baseline; persistent code/test/docs/report/ledger delta 73797bytes; raw/source bytes and queries0; 7new and2modified files; no data scans or neural fits.. Checks bind exact module/test/clock/README/trace hashes and currentcode identity; predecessor protocol/clock/ledger preserved. One-time private report tooling not required by the reproducible library/test workflow.
