# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-11_011815 America/New_York; baseline UTC 2026-10-11T05:18:15.124581+00:00.
- Contributor/session: Codex P1.CA / P3-Prep; targeted corporate-action audit and pure accounting foundations.
- Branch: `feat/track-a-data-intake`. Starting/ending HEAD `40840aee20d2fedb481b5f1060909e21c16ca145`; no commit by this session; no issue/PR.
- Start clean, one local commit ahead / zero behind fetched upstream. Prior shared registration and proxy amendment committed/present. End: nine new code/test/report files plus one ledger append, unstaged/uncommitted. No inherited work changed.

## 2. Executive summary

Reconciled canonical116actions (110dividends,2splits,4acquirer-role mergers), isolated four native missing payable/record dates, and built one pure stdlib/Decimal module plus23focused tests. Accounting invariants PASS;180integration tests and Ruff pass. UNKNOWN payments remain signed pending claims; missing exits retain shares; missing marks produce incomplete NAV. Engineering primitives ready for conditional P3 integration; historical/source truth qualified and P3 integration pending. One non-clearing audit preserves all seven blockers. No simulator, label/model/source activation or global gate clearance.

## 3. Research/protocol impact

No universe, feature, target, split/window, confirmation, model/hyperparameter, cost/borrow, Policy A/B, execution-provider or40-pair changes. Accounting is independent of minute OPEN versus approved-direction hourly CLOSE proxy. Existing five authorities/pointer and reported shared/proxy statuses untouched. Explicit ex-session09:30ET, date-based modeled dividend settlement, share-epoch/sequence and optional fractional assumptions are labeled rather than inferred historical facts. Real raw-share cashbook obligations are enforced in small primitives; no total-return TG0 change or dividend model feature. Source/post-ex qualification distinct from future prediction/eligibility.

## 4. Files created

- `src/lstm_data/corporate_actions.py`: pure typed immutable event/evidence/position/claim/account/mark records; metadata reconcile/map, split/accrual/settlement, retained exposure, raw-basis conversion and financial snapshot.
- `tests/test_corporate_actions.py`:23focused synthetic/retained-metadata cases, independent arithmetic, fail-closed and replay guards; bounded optional116-action mapping test skips when ignored data absent.
- `reports/data_audit/p1_ca_2026-10-11_011815/package_report.md`: short package report, precise events/source unknowns/engineering status/resource boundaries and stop.
- `reports/data_audit/p1_ca_2026-10-11_011815/action_reconciliation.json`: compact116-ID field-presence/native-value/evidence/role locators, counts by symbol/year/type, exact missing IDs, source/manifest hashes and split anchor residuals; derived report, no raw copy/mutation.
- `reports/data_audit/p1_ca_2026-10-11_011815/accounting_examples.md`: six hand-calculated cases, exact function/line references and minimal future P3 caller contract/reproduction.
- `reports/data_audit/p1_ca_2026-10-11_011815/checks.json`: six existing-schema checks separating technical/accounting PASS from source WARN/payment/P3 BLOCKED, unchanged authority/blockers and0fits.
- `reports/data_audit/p1_ca_2026-10-11_011815/human_review_card.md`: five exact manual pointers/expected values/optionaldata test instructions.
- `reports/data_audit/p1_ca_2026-10-11_011815/preservation.json`: final changed-file sizes/hash identities, exact ledger prefix, source/authority/index preservation, test counts and disk growth; own digest intentionally excluded, own bytes measured.
- `reports/codex_sessions/2026-10-11_011815_feat-track-a-data-intake_p1-ca-accounting.md`: mandatory17-section handoff.

## 5. Files modified

`reports/audit/track_a_events.jsonl`: one scoped G1/BLOCKED audit `p1-ca-2026-10-11-011815`, blocks=[]/supersedes=[],20→21events. Prior 34272bytes exact prefix SHA `c7aeb49673b42ab1e1f99058f25e1946ef9def870c638d6a325955cfd857b41d`; all seven blocker IDs/dependencies retained. New event binds checks/reconciliation/code identity; source IDs inherited and new source SHA explicitly recorded. No validator or historical row rewrite.

## 6. Files deleted, renamed, or moved

None. All raw source and historical reports retained. No directory reorganization.

## 7. Critical functions, classes, variables, and config keys

All new code in corporate_actions.py; no config keys/CLI added. No I/O/persistence/network/global state. Five-symbol prototype fixed; Decimal arithmetic and timezone-aware times. Immutable tuple-backed Account, Position, Action, SourceEvidence, DividendClaim and RawMark records carry explicit IDs, raw-share epoch, chronology, provenance and pending state.

- `reconcile_source(payload,source_hash,retrieved_at)->dict` at114:116metadata-only records, native missing/null distinction, role/date/rate validation/counts; no price/features/actions applied; hashes/retrieval do not prove historical availability/issuer truth.
- `normalize_action(record,category,*,held_symbol,source,boundary,sequence,share_basis,post_split_basis=None,fractional_policy=None)->Action` at219: supported split/dividend only, explicit issuer role/declared exchange boundary/ordering/basis; acquirer/unsupported mergers rejected. Caller verifies real session and rate epoch. Action constructors restrict declared09:30ET boundary, positive ratios, finite nonnegative rates and sensible dividend pay dates.
- `apply_action(state,action)->Account` at365: raw signed physical shares split; claims accrue only from pre-boundary holdings; no external order/cost/cash on split. Action ID+content fingerprint gives idempotency and rejects changed replay/rewind/basis conflict. `apply_actions` at422 deduplicates exact replay, sorts declared boundary/sequence, rejects simultaneous ambiguity.
- `settle_dividend(state,claim_id,at)->Account` at439: known retrieved payable date + declared simulated timing, signed accrual→cash once; unknown date rejects with retained claim. Date-based transfer is not broker settlement evidence.
- `retain_missing_exit(state,symbol,at)->Account` at466: explicit outstanding exposure/claims persists across sessions; no retry/fill/liquidation algorithm.
- `raw_price_from_split_adjusted(price,raw_per_adjusted)->Decimal` at498: positive explicitly proved factor boundary; no auto-factor lookup or dividend/total-return conversion.
- `snapshot(state,marks,at)->dict` at506: cash, raw marked long/short, pending receivable/liability, cash-only/accrual-inclusive equity; missing marks→None/INCOMPLETE NAV, future/raw-epoch mismatches rejected, stale source age disclosed. Caller supplies supported as-of marks; no feed certification or continuous risk engine.

## 8. Data/schema/provenance changes

Canonical `data/raw/alpaca/track_a_close_v1/actions-d7e39f2015b86602ac9c.json` SHA `72f5432b84cd87a5941301b7ef05b81a377ca157bbb04c403fea3ebbcda63eb3`, manifest `data/raw/alpaca/track_a_close_v1/actions-d7e39f2015b86602ac9c.manifest.json`, retrieval2026-10-11T03:32:12.934774+00:00.116uniqueIDs/counts match prior closeout; paths unchanged. Source process-date-filtered archive is current retrospective vintage, not independent complete issuer/PIT/event-time truth. Native field payable_date distinct from prior QA's payment_date alias; four absent keys preserved (not fabricated null/pay dates).

AAPL23407e01-4eef-4c1e-a2dd-f585c7eabcd0 ex2020-02-07;CATc3b503fd-3d49-4da9-8934-c75beb9043b0 ex2020-01-17;JNJ44ce8288-819e-48aa-80e2-e8ec518e9857 ex2020-02-24;JPMc7ec5c17-0970-4262-9800-fbabde1e0aa2 ex2020-01-03. All pre-July2020; only qualifying warmup/carry claims depend on unknown payment, not ordinary intraday post-ex entries. Four acquired-target AMAM/ITCI/SWAV/VZIO records held JNJ/WMT as acquirer: no supported held-share transformation; no target cash booked.

Splits AAPL4:1/WMT3:1 positive retrieved components; intraday time, rounding/cash-in-lieu and full raw-basis validation qualified. Two retained AAPL anchor rows (same2020-08-28 13:30UTC) reread: raw/4−stored adjusted open−.0025,high0,low−.0025,close−.005; volume residual0. No zero-price-residual assertion or documented rounding discovered. No retained paired WMT raw sample, no download. No60-Parquet/full price audit or confirmation price outcomes accessed; WMT2024action metadata is not performance. New JSON is derived small reconciliation only; normalized accounting events require additional explicit basis assumptions. No migration/data rebuild now.

## 9. Dependency/environment changes

None. stdlib Decimal/dataclasses/datetime/zoneinfo plus existing project test/data tools. No secrets/environment reads, new package/version/CLI/setup requirements. README authoritative setup unchanged.

## 10. Commands and tests run

- Actual AGENTS and authority hierarchy reused/read in preceding turns (unchanged hashes), latest relevant proxy/shared/P2.1/P2.2A/closeout/P1.3D evidence inspected; canonical116-action JSON/manifest located, exact source hash verified. Existing src inspected: no accounting module to extend.
- Git status/branch/HEAD/remotes, `git fetch --all --prune` (approved escalation), upstream rev-list/index inspection: clean start,1ahead/0behind, no integration/branch/index/history mutation.
- `.venv/bin/ruff format src/lstm_data/corporate_actions.py tests/test_corporate_actions.py`; focused Ruff import fix and final checks:PASS.
- `.venv/bin/python -B -m pytest tests/test_corporate_actions.py -q`:initial21passed0.33s; then23passed0.42s after adding reusable reconcile_source and its tests/empty-payable guard. No credentials/provider access.
- Initial `.venv/bin/python -B -m pytest -q`:178passed15.40s and `ruff check src tests` PASS. Final after substantive metadata-function/test changes:180passed16.95s, `ruff check src tests` PASS. Rerun justified by new research-critical code; no suite rerun for report formatting.
- Source anchor: PyArrow reads one retained raw row and exact symbol/timestamp-filtered adjusted row; residuals match prior QA. Harmless sandbox CPU-cache sysctl permission warnings; reads successful, no escalation needed. No broad scan/API.
- `.venv/bin/python -B /private/tmp/lstm_ca_report.py`: source classification/report orchestration and one existing locked append; PASS. Temporary helper not required for package/library verification.
- Existing check/event/safe-payload schemas, metadata/portable path/link/line references, exact manifest, raw/authority/index/HEAD/old-prefix/7blockers/0fits verified; `git diff --check` PASS. Details and exact disk bytes in preservation.json. No known failing tests.

- Initial report-link verification ran before preservation.json existed and correctly rejected the dangling link; final verification was rerun after the manifest was created. No code/test failure or historical record mutation.

## 11. Experiment/results summary

No empirical experiment/run/model/seed/predictive/trading metrics. Synthetic split invariance, ±$77 long/short claims, one-time settlement,308post-split claim example, idempotency and incomplete NAV verified. Accounting code PASS not G1/G2/G4/source truth PASS. Zero neural training pairs; confirmation outcomes unopened.

## 12. Reproduction instructions

README virtualenv (`python -m pip install -e '.[dev]'`), `python -m pytest tests/test_corporate_actions.py -q`;23pass with retained archive or22pass+1skip absent it. No credentials/downloads; synthetic tests run on clean clone. Fullsuite `python -m pytest -q` and `ruff check src tests` appropriate when independently integrating code, not necessary to repeat report review. Source reconstruction optional: supply exact ignored JSON+manifest, verify source SHA, read corporate_actions payload, call reconcile_source as documented in accounting_examples.md; no prices/labels required. Retained canonical source path/version declared in report; missing raw file does not prevent pure accounting use. Existing donor API reproduction in closeout remains provenance-qualified, not issuer-completeness proof. Do not reappend event.

## 13. Git / collaboration status

Branch `feat/track-a-data-intake`, HEAD `40840aee20d2fedb481b5f1060909e21c16ca145`; fetch succeeded1ahead/0behind. No commit/staging/push/merge/cherry-pick/stash/reset/cleanup. Protected old tracked files/source/index byte identities remain. Exact new review manifest:

- `src/lstm_data/corporate_actions.py`
- `tests/test_corporate_actions.py`
- `reports/data_audit/p1_ca_2026-10-11_011815/package_report.md`
- `reports/data_audit/p1_ca_2026-10-11_011815/action_reconciliation.json`
- `reports/data_audit/p1_ca_2026-10-11_011815/accounting_examples.md`
- `reports/data_audit/p1_ca_2026-10-11_011815/checks.json`
- `reports/data_audit/p1_ca_2026-10-11_011815/human_review_card.md`
- `reports/data_audit/p1_ca_2026-10-11_011815/preservation.json`
- `reports/codex_sessions/2026-10-11_011815_feat-track-a-data-intake_p1-ca-accounting.md`
- `reports/audit/track_a_events.jsonl`

Only old modified path is central ledger; primary collision point. Exact prior bytes checked immediately before existing exclusive-lock/atomic append; no concurrent change detected. No frozen/proxy/shared/P2.1 edits. After APPROVE and separate commit authorization, fetch/reinspect and stage exact manifest, not directories. Proposed command, not executed:

```bash
git add src/lstm_data/corporate_actions.py tests/test_corporate_actions.py reports/data_audit/p1_ca_2026-10-11_011815/package_report.md reports/data_audit/p1_ca_2026-10-11_011815/action_reconciliation.json reports/data_audit/p1_ca_2026-10-11_011815/accounting_examples.md reports/data_audit/p1_ca_2026-10-11_011815/checks.json reports/data_audit/p1_ca_2026-10-11_011815/human_review_card.md reports/data_audit/p1_ca_2026-10-11_011815/preservation.json reports/codex_sessions/2026-10-11_011815_feat-track-a-data-intake_p1-ca-accounting.md reports/audit/track_a_events.jsonl
```

Then focused normal branch/PR workflow; no force/history rewrite. Preserve the preexisting local ahead commit.

## 14. Known issues, risks, and limitations

No failing tests. Source provenance/issuer completeness/effective-time/publication/entity mapping/rate epoch/rounding remain qualified, four payment/record dates UNKNOWN. Caller assertions are not source certification. Explicit fractional model preserves synthetic wealth but is not actual issuer cash-in-lieu evidence. Settlement uses declared date convention, omitting taxes/withholding/recalls/broker plumbing/interest. No share/cash trade, borrow/cost engine or policy/mark/retry/risk/valuation freshness calibration; P3 must supply causal state and price evidence. Action ordering must be explicitly supported; if ambiguous or basis wrong, affected output rejected. Outstanding holdings retained; missing valuation blocks NAV rather than fabricate exit.

All seven prior blockers active: p0.1-F01, p0.1-USA500-source-clock, p0.1-stock-publication, p0.1-minute-execution, p0.1-actions-dividends, p0.1-formation-prehistory, p0.1-shared-D3-clock. Market/source and proxy/shared execution approval unchanged; no automatic narrower scope closure. Ex-dividend economic accounting separate from price-only supervised labels, which this module does not create. Economic claim readiness depends on pending hourly exception/benchmark policy and G4 integration.

## 15. Decisions requiring human or teammate review

**APPROVE / REVISE / HOLD** primitives and scoped source reconciliation. Review boundary/rate basis/sequence/fractional assumptions and unknown-pay cash scope, rather than silently assert historical truth. Separately resolve source evidence and hourly-proxy exception/mark/retry/benchmark/shared-rule obligations before P3 economic integration. No provider contact, source lookup or signed approval obtained.

## 16. Next recommended steps

After review, separately scope P3.1/P3.4 integration of these primitives and outstanding-claim/position financial statements with explicit policy/source dependencies. Separately authorize revised P2.2A execution-provider/label version if desired; no price-frequency coupling here. Keep source UNKNOWNs, market HOLD and actual gate/confirmation controls. STOP; no automatic simulator/labels/models/overnight experiment.

## 17. Artifact inventory

One module,one test,six small report JSON/Markdown files,this session and one ledger append;9new+1modified tracked-ready, all unstaged. No source duplicates/parquet/checkpoints/window/model/cache artifacts. preservation.json records exact growth/file sizes and SHA paths, source/protocol/code IDs, all old preservation checks and23/180test counts. Private helpers/baseline files are local scaffolding only. Own preservation digest excluded to avoid self-reference; its actual bytes and total disk delta are verified.
