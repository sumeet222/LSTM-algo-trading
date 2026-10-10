# P0.1 — Protocol inventory, coverage and blockers

**P0.1 inspection complete; research preflight BLOCKED.** Status vocabulary applies to actual implementation, not approval of a design. `NOT_STARTED` means outside Task 01, not failed. `PRESENT_TESTED` is scoped to the stated test/evidence. No financial confirmation metrics were read or computed.

## Authority inventory and proposed pointer

All files below were read; no required authoritative document is missing. Precedence: shared requirements → frozen menu → consistent approved Track A detail → audit contract → package sequencing. Current human-authorized source refinements remain binding.

| Actual path | Declared version | SHA-256 |
|---|---|---|
| `docs/track_a/Shared_Project_Specification.md` | 1.0, provisional shared agreement | `12863e44efa2ca3c51d5f5c5033a3735b16b4a87a00158122d372db6ed9cdf32` |
| `docs/track_a/Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md` | Frozen first-pass menu v1.0 | `7afb1d3fe6cd5bf68e1e9a1c8e6f19e200ce2c4cae6414b1b0b90e40365339ce` |
| `docs/track_a/Track_A_Consolidated_Implementation_Design_Record_v1.2_2026-10-10.md` | Consolidation draft v1.2 | `cf3f7531ecd52e47386e64035d5c86ab513acc3c1a6bbbee5e54ad325eb9a96c` |
| `docs/track_a/Track_A_Stage_Gated_Audit_and_Failure_Traceability_Plan_v1.1_2026-10-10.md` | Audit design v1.1 | `a29309ef791f74f72443b2b66ad1d9cde5f46e54dfbcd072f5bda5da68d1878d` |
| `docs/track_a/Track_A_Codex_Incremental_Implementation_and_Human_Review_Plan_v1_2026-10-10.md` | Planning v1 | `bf3459456b12c23942d99bd555cc66137cd6154c79119ae96eaa3bfdb88a202d` |

Also read: root AGENTS.md, both Task 01 session reports, current final handoff and actual code/config/data docs. Their hashes are in `p0_1_checks.json`. The newer session report supersedes initial acquisition status; this P0.1 supersedes both reports' Git state and absent-authority statements only. Historical reports remain intact. Consolidated §20/§21 and audit introduction retain older version wording: documentary WARN, not permission to rewrite them. Background menu/paper documents named inside the authorities were not supplied; no optional design or literature claim depends on inferred contents here.

Proposed, **not installed**, `configs/CURRENT_PROTOCOL.json`: `schema_version`, ordered `documents[{path,declared_version,sha256,role}]`, `precedence`, `source_amendment_refs`, `shared_signoffs[{key,status,evidence_ref}]`. Reference the actual approval JSON and provisional USA500 config; keep shared clock pending. Never replace missing approval with a pointer's mere existence.

Abbreviations below: **S** = Shared specification; **R** = frozen roadmap; **D** = consolidated design v1.2; **A** = audit v1.1; **P** = implementation plan v1. All section references refer to the inventory above.

## Actual reusable interfaces

| Actual file:function:line | Interface / verified responsibility |
|---|---|
| `src/lstm_data/config.py:load_config:31` | Path → validated intake config, fingerprint, project paths; no network/writes |
| `src/lstm_data/config.py:atomic_new:71` | Create-only complete output; no existing-file replacement |
| `src/lstm_data/validation.py:require_valid:66` | Required keys/OHLCV defects → explicit error; zero/fractional volume separately diagnosed |
| `src/lstm_data/calendar.py:session_grid:22` | Real calendar open/close → anchored hours plus flagged stub |
| `src/lstm_data/aggregation.py:aggregate_session_hours:11` | 30Min frame → complete observed OHLCV and masks in memory; interval-end availability assumption |
| `src/lstm_data/alignment.py:asof_diagnostic:10` | Backward hypothetical availability match; diagnostic age, not D2 production validator |
| `src/lstm_data/alpaca.py:HistoricalClient.bars:147` | Explicit SIP GET/pagination → typed native bars; transport mocked in current tests |
| `src/lstm_data/store.py:check_approval:147` | Config/pilot/source/adjustment authorization binding, offline check passed |
| `src/lstm_data/store.py:read_verified:71` | Chunk byte/parameter/schema verification; full table load intentionally not invoked in P0.1 |
| `src/lstm_data/cli.py:runtime:28` | Git SHA, versions, config hash; lacks dirty-tree/code-content hash and registry |

## Protocol-to-repository matrix

| Requirement | Approved source | Actual evidence | Status | Consequence | Smallest dependent package |
|---|---|---|---|---|---|
| SIP canonical source and immutable hashes | D §3/§16; A G1 | `store.py:64,95,147`; 60 footer/hash/manifest checks | PRESENT_TESTED | Reuse single store; not vendor truth | P0.2 reference existing manifests |
| Approved 30Min → hourly refinement | Current human approval; D §3; P0.1 prompt §3.4 | Dated approval, fingerprint/pilot hash verified; `aggregation.py:11`; tests | PRESENT_TESTED | Preserve amendment; old native-hour reports are history | No reacquisition/refreeze |
| Split-adjusted feature source | D §3.1 | Every manifest SIP/30Min/split; pilot split-window diagnostics | PARTIAL | Metadata proves chosen adjustment; independent inverse-volume/action proof absent | P1.3 action samples |
| Original five and fixed intake dates | D §2.1 | `configs/track_a_data.json:4`; monthly params | PRESENT_TESTED | Correct names/order/data dates, not formation qualification | P1.3 eligibility evidence |
| Formation membership/$50m/60-session liquidity/backups | D §2.2; S §4/§8.1 | Static sectors/provisional-survivor warning only; no preformation store | BLOCKED | Cannot assert investable 2020 universe or H/L identities | P1.3 references, no performance selection |
| Retrospective ≥98% overall/≥95% yearly coverage | D §2.2 | Compact gaps/all-session QA exists; yearly threshold evaluation absent | PARTIAL | Source usability differs from formation eligibility | P1.3 bounded coverage summaries |
| Dividends/raw execution/share accounting | D §3.1/§7; A G1 | No action/dividend/raw-minute reference store | BLOCKED | Cannot infer financial P&L from split-adjusted 30Min | P1.1/P1.3 source feasibility |
| Six complete hours and closing stub | D §3.1; A G1/G2 | `calendar.py:22`, `aggregation.py:42`; ordinary/gap/early-close tests | PARTIAL | Grid tested; output includes stub; feature view must exclude it explicitly | P2.1 input view |
| Historical DST/holidays/early closes | D §3.1; A G1/G2 | `calendar.py:9`; 60-test suite; synthetic early close | PRESENT_TESTED | Calendar component reusable, not full issuance/target gate | P2.1 timeline |
| Stock period_end vs published available_at | D §3.1/§4.1 | `aggregation.py:19,67` assumes interval end; no separate publication field | PARTIAL | Source latency unverified; input may not be ready at period end | P1.1/P2.1 source clock |
| USA500 identity/OHLC/daily-close compatibility | D §3.2/§9.2; S §4 | Course schema/hash/audit; upstream/calendar unknown | BLOCKED | U1–U5 and USA500-conditioned models cannot proceed | P1.2 source contract |
| Provisional USA500 close interpretation | Existing human approval; D §3.2 | Config semantics unknown plus explicit provisional assumption | PARTIAL | Assumption retained; not verified publication | P1.2 verification |
| 90-minute age from period end | D §3.2; A G2 | `alignment.py:51` subtracts assumed availability; synthetic 120/60 counterexample | CONFLICT | Delayed zero-stale summary cannot certify D2 freshness | Separately approved timing correction after P0.2 |
| Nominal cutoff/issuance/2-min allowance/5-min maximum | D §4.1 | Diagnostic decision_time only; no issuance engine | NOT_STARTED | No assurance that delayed issuance obeys original cutoff | P2.1 after source evidence |
| Genuine one-minute opens/delayed exits/TG0 prices | D §4.1; A G1/G2 | No minute store; only aggregate source | BLOCKED | 30Min cannot establish 10:33,11:33,14:33,15:33 fills | P1.1 limited minute feasibility, new authorization |
| Continuous 240min vs four complete advances | S §3.1/§8.1; R §1/§2.1; D §4.1 | D explicitly records pending sign-off; no approval artifact | CONFLICT | Common target/trade implementation held | Joint decision before P2.2 |
| C01 forecast/entry/label/fill separation | D §4.3; A G2 | No forecast/label/execution implementation | NOT_STARTED | Future missing exit must not retrospectively suppress entry | P2.2 then P3 exception tests |
| Exact FT0 48×16, scheduled gaps/warm-up | D §5.1–5.2 | No feature module/preformation source; aggregation masks only | NOT_STARTED | Strict five-name window/360 EMA/14+140 RSI/M4 warmth unmeasured | P1 feasibility before P2.3 |
| Scaler keys/train-only fits/floors/retention | D §5.3–5.4; A G3 | Intake hashes only; no transforms/retention calculation | NOT_STARTED | No 90%/85%/100-session/regime claims | P2.3 after prerequisites |
| U1–U5/48×5/46-of-48 market validity | D §9.1–9.2 | No market feature implementation; timing diagnostic only | NOT_STARTED | Neutral-fill/scaler/daily lock tests absent; source blocked | P2.4 after P1.2 |
| TG0 unscaled MAD/train-fitted floor/chronological purges | D §4.2/§4.4; A G2/G3 | No labels/split config | NOT_STARTED | No labels/purge PASS inferred from timezone tests | P2.2 after minutes/sign-off |
| D8 peer summaries/formation H↔L/lags | D §10; R E5/E5L | No feature implementation/preformation ranking | NOT_STARTED | No peer activation or causality claim | P4.7/P4.9 with source prerequisites |
| P3 physical portfolios/policies/cost/borrow/exits | D §7; A G4 | No portfolio/event code | NOT_STARTED | 24.75% legs/110% emergency/net fees require separate tests | P3.1–P3.4 |
| C07 momentum/ridge/benchmark settings | D §17; A Appendix A | Design complete; no model/baseline code | NOT_STARTED | Seven-lag ridge differs from full 48-step LSTM information | P3.5–P3.6, no design reinvention |
| P4 D6 engine/seeds/calibration/refit | D §8; A G5/G6 | No PyTorch/training module or checkpoints | NOT_STARTED | Width32/dropout placement/session weighting/40-pair guards untested | P4.1–P4.2 after G1–G4 |
| Optional MC2/SP3/SP1/TM1/TG2/TG4/AD3 | R conditional ladder; D §§9–13 | No optional jobs or activation evidence | NOT_STARTED | Inactive, no failure conclusion or automatic implementation | G7 only on activation |
| P5/P6 selection/finalist/confirmation lock | D §15; A G8/G9 | No predictions/metrics/lock/release mechanism | NOT_STARTED | Dates preserved; confirmation remains unopened for performance | P5.6/P6.1 explicit approval |
| G0–G9 evidence framework/run ledger | A §1.2/§14; P P0.2 | Separate runtime/audit JSON and session archive; no structured ledger | PARTIAL | No dependency propagation, exact budget registry or release guard | P0.2 minimal delta |
| Boundary replay T0/T1/B0–B7 and 5→20 bridge | D §22; A §13 | Source hashes/slot masks only | NOT_STARTED | Full selected prediction/trade not reconstructible; no such run exists | Add boundaries incrementally; P5.5 later |
| Storage limits/reuse | D §16; A §12.1/§14 | One source store; on-demand hours; measured disk sizes | PARTIAL | Intake conforms; future feature/checkpoint budgets untested | P0.2 registry; later stage size checks |
| Clean-machine dependency/reproducibility | AGENTS §§3/5/24; P P0.2 | pyproject ranges, README setup, installed imports/tests/pip check | PARTIAL | No lock or cross-machine rehearsal; historical dirty code hash absent | P0.2 environment metadata; final rehearsal later |

## G0 subchecks and stage boundaries

| G0 check (A §2) | Status | Saved evidence / limitation |
|---|---|---|
| Authority/version | WARN | All five read/hashed; stale internal wording; shared-clock conflict unresolved |
| Conditional status/permission | PASS for P0.1 scope | Inspection only, no conditional model launched; future automated enforcement NOT_RUN |
| Source identity/entitlement | BLOCKED | Historical SIP pilot access evidence available; USA500 identity/usage/publication and minutes not verified |
| Common clock/sign-offs | BLOCKED | D §4.1 explicitly pending; no joint evidence found |
| Window/confirmation | PASS for inventory | D windows unchanged; no performance objects exist/used; software release guard NOT_RUN |
| Resource/scope | WARN | Zero fitting pairs now; no structured pair/budget ledger or forecast |
| Secret handling | PASS, bounded | .env/raw/venv untracked/ignored; .env never opened; placeholders and redacted client inspected; no comprehensive history scan |
| Repository/data safety | PASS | Clean start; no existing file edits; all 60 chunks/course hashes match; no copies/integration |

Overall **G0 BLOCKED**, not all-PASS. **G1 PARTIAL/BLOCKED**: raw integrity, existing numerical QA and calendar/aggregation evidence present; minutes, actions, formation and publication remain blocked. **G2 PARTIAL/BLOCKED**: reusable calendar/backward matching; F01 conflict, clocks/labels/issuance absent. **G3–G9 NOT_RUN**: no features, simulator, engine, fits, activated mechanisms, development or confirmation. Model-level replay is NOT_RUN. P0.1 acceptance and research preflight are different judgments.

## Named blockers / decisions

| ID | Observed evidence | Approved rule | Why / dependent work | Lowest-cost verification | Human/collaborator approval? |
|---|---|---|---|---|---|
| B01 source amendment | Matching existing SIP/30Min/split approval and passing pilot; old native-hour text retained | Human Task 01 refinement + D2 hourly inputs | No revert; downstream audits still needed | Keep approval/hash references in pointer | Already authorized; no reapproval for same source |
| B02 168 gaps | 15 exceptions in compact QA; 98 incomplete windows in coverage manifests | D4 strict scheduled 48×16×5, no stock imputation | Warm-up, RMS/EMA/RSI and daily context can extend losses beyond gap day; P2.3/G3 | Later permitted validity/warm-up summary, no future-label filter | Approval required for any relaxation/backfill/source change |
| B03 USA500 semantics | No provider contract; close provisional | D2/D7 actual complete OHLC/daily close/available_as_of | Blocks P1.2→P2.4→E3/E4 and market/peer-conditioned branches | Obtain course/provider documentation, historical timing examples | Human supplies evidence; changes need decision |
| B04 trailing course timestamp | July1 local row beyond June30; hash intact | D1 fit/development/confirmation bounds, S leakage rules | Raw retained; later fit/label selection must enforce bounds | Small boundary fixture in future feature builder | No deletion; no new window authorized |
| B05 raw minute/action prices | Only split-adjusted 30Min; no raw minutes/dividend store | D2/D3/D5 genuine raw minute opens, wealth accounting | TG0, M2 history, fills, delayed exits, P&L blocked | Authorized small minute/action source pilot and footprint estimate | New acquisition scope approval needed |
| B06 formation/warm-up | Store starts Jul2020; no earlier 60-session liquidity/membership/M4 context | D1 formation separate from retrospective completeness; D4 warmth | Universe qualification, H/L, early FT0 retained origins unknown | Source metadata plus preformation history feasibility | No automatic backup/selection; amendments reviewed |
| B07 authority/version | All requested docs now present; old reports say absent; stale v1.1 references | S hierarchy; P §7 current pointer | Inventory blocker resolved; pointer still absent | Hash manifest using actual current paths | Human acknowledges pointer/current versions in P0.2 |
| B08 timing measurement (F01) | Delay60 reports availability-age 60 for period-end-age120; start-only guard | D2 period-end age≤90; D3 original cutoff and publication constraints | Diagnostic not reusable as final causal join/G2 | Included tiny synthetic counterexample; later explicit dual-clock test | Repair must be separately authorized; no new delay invented |
| B09 shared clock | 240 continuous minutes vs four complete advances, second exit in stub | S §3.1/§8.1; D13-C02 | Labels/trades/common comparisons held; infrastructure unaffected | Joint recorded choice and minute timeline | **Joint sign-off required**, not assumed |
| B10 conditional controls/details | SP3 needs full-peer fourth family; FC6/TG4/AD3 gaps stated | D9/D12 three-family cap; optional detail protections | Only matters if branch activates or SP3 shortlisted | Keep inactive status; review before activation/confirmation | Conditional scope/resource amendment or narrow claim |
| B11 ledger/lineage | Runtime records base SHA for then-uncommitted implementation; no structured run ledger | A §1.2/§14; D6h; P P0.2 | New work lacks enforced audit dependencies/resource/release trace | Reuse hashes/runtime; add small append-only index | P0.2 approval before implementation |

Known missing half-hours by session (counts only, no source prices):

| Session | JPM | JNJ | WMT | CAT | Total |
|---|---:|---:|---:|---:|---:|
| 2021-04-19 | 12 | 12 | 12 | 12 | 48 |
| 2021-10-25 | 12 | 12 | 12 | 12 | 48 |
| 2022-01-24 | 0 | 0 | 10 | 10 | 20 |
| 2022-01-26 | 0 | 0 | 2 | 0 | 2 |
| 2022-03-08 | 12 | 13 | 12 | 13 | 50 |
| **Total** | **36** | **37** | **48** | **47** | **168** |

AAPL has no recorded gaps. Full missing timestamps remain in the existing compact QA JSON; no duplicate exception dataset was created. JNJ/CAT's March8 entire-session gaps account for their no-RTH-overlap counts. The independent historical JPM April19 probe corroborates the returned-history issue for that day only; missing vendor data is not proof of no exchange trading.

Safe next boundary, subject to human approval: offline P0.2 infrastructure can reuse this evidence while marking B03/B05/B06/B09 unresolved. Stock-only source feasibility need not await USA500 identity; stock-only FT0 still needs M2 minute history and warm-up. Market formulas need B03/B08; target/trading clocks need B05/B09; economics additionally need actions and G4. A-E9 remains held by G9, irrespective of test success. Formal full-selection null funding and its tension with the project-wide null deliverable require later collaborator review before claims; no null or optional pilot ran.

**AWAITING HUMAN REVIEW — NO AUTOMATIC NEXT PACKAGE.**
