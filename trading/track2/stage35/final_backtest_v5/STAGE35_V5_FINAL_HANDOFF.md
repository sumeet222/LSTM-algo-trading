# Track 2 V5 final handoff

**STAGE35_V5_FINANCIAL_BACKTEST_COMPLETE_EXPLORATORY**

Actual completed/reconciled scenarios: **24/24 total (baseline plus 23 sealed variants)**, four arms × matched/attainable = eight independent accounts per case. Original cached forecasts, source data and prior artifacts were reused. Stage 6 independent financial/statistical audit remains **PENDING**. No live/paper order, model training/refit/calibration, return-based parameter search or 2025+ market-price access occurred.

Final report UTC: 2026-11-10T18:16:39.753773+00:00. Branch `feat/track-a-data-intake`; HEAD `8061483cb65d03264a7836b8b882123f67cbe4ad`. Current execution fingerprint `9e093b3f6a62`. No commits/pushes or destructive Git operations. All new work is uncommitted; existing untracked work is preserved.

## Actual scope and data

Fixed 20-stock survivor panel; original F21–F24 C-A/O1/48×16 FT16/10 CLOCK/original C3 and target scales, 6,572 frozen parameters. This study reused the 131,111 cached original-model magnitude forecasts and 9,169 explicit input-unavailable rows; it did not repeat neural inference or the prior replication campaign. 1,005 sessions, 7,014 legal nominal origins, 140,280 calendar stock opportunities per scenario; 128,192 EQUAL/S2C candidates and 87,557 matched four-arm input-ready candidates. Candidates are not funded cohorts or external fills. No future endpoint/F09 scoreability or realized profitability selected opportunities.

Direction is the first-decision session-frozen sign of log(P[D−1]/P[D−6]). Original nominal 240 scheduled XNYS-minute endpoints are unchanged. Fixed cohorts may overlap and oppose; later forecasts do not resize held cohorts. The main calibrated absolute-log magnitude sizes exposure only; it is neither directional alpha nor conditional sigma.

## Reconciled baseline — all net costs included

| Arm | Matched final USD | Matched compound return | Attainable final USD | Attainable compound return |
|---|---:|---:|---:|---:|
| EQUAL | 2,222.13 | -97.7779% | 2,911.95 | -97.0881% |
| ROLLING_RISK | 1,840.62 | -98.1594% | 1,840.62 | -98.1594% |
| EWMA_RISK | 2,008.24 | -97.9918% | 2,008.24 | -97.9918% |
| S2C_RISK | 1,926.90 | -98.0731% | 2,638.94 | -97.3611% |

All baseline arms lose roughly 97–98%. On matched opportunities S2C finishes $295.23 below EQUAL, $81.33 below EWMA and $86.28 above ROLLING. This is no consistent economically useful baseline improvement. Repeated commissions and modeled friction dominate; whole shares and wealth depletion materially affect later investability. Adding costs back to the same holdings is an accounting decomposition, not a frictionless rerun. Attainable comparisons to the classical arms include eligibility differences; matched comparisons are the primary sizing comparison. No significance claim is made.

All frozen scenario results, including adverse results and failures if any, are in `presentation/FINAL_TABLES_V5/SCENARIO_RESULTS.md` and its CSVs. Annual metrics, Sharpe/Sortino/Calmar, drawdown/duration, turnover, costs, idle cash/exposure, cohort long/short/ticker/origin/year attribution, actual holding/overnight durations, delay counts and terminal cash/claims are linked there and in `presentation/ADDITIONAL_DESCRIPTIVE_TABLES_V5/`. Daily conventional annualization uses 252 sessions, rf=0/MAR=0; CAGR uses calendar years. Cohorts overlap and are not independent samples. Sector/beta metadata are not established and are explicitly unavailable.

## Execution and accounting evidence

V5 keeps an already submitted simulated order pending until the actual next valid observed RTH minute. Entry effective start must be <= nominal+10 wall minutes; expiry is explicitly simulated nonfill, not broker cancellation. Exits retain inventory/carry/actions until an actual later qualified bar; no entry expiry is imposed on them. Actual bar-open value is known after completion+receipt and never decides its own order. Baseline receipt is assumed 2 minutes (1/5 stress), modeled compute duration zero, prior received minute-volume participation 1%, 5 bp half-spread +5 bp impact per physical external side, $0.005/share and cumulative $1/order minimum. Internal transfers use the same ex-post raw-open reference and no external fee.

Budgets are <=20% marked NAV per vintage, <=10% aggregate name, <=100% virtual gross including pending and <=100% absolute physical net. Whole shares round toward zero without redistribution. Short proceeds are restricted within cash once. NAV = cash + marked long value − short liability + ordinary claims + special-action assets/liabilities; fees/borrow/funding already debited in cash are not deducted twice. Physical shares equal summed virtual shares. Observed gaps/breaches are retained with prospective risk reduction; no retrospective cancellation or favorable deletion.

Completed-case maximum book residual: **6.71747E-21 USD** against unchanged 1e−8 threshold. All completed cases have zero terminal pending orders, unpriced specials and incomplete account-days. Daily balance and mechanical cross-scenario checks are in the descriptive supplement. Priced unpaid claims, if any, are retained separately from flat physical stock and unavailable capital.

Baseline source impact: 10,374 residual missing/invalid source cells are distinct from 212 missing execution attempts on 168 account orders /90 ticker-minute keys. There are 166 qualified later reference settlements and two explicitly modeled entry expiries. Qualified reference/FILL event counts include internal-only or zero-external cases; they are not all external market trades.

AVGO June 9: 16:33 UTC absent remains absent. Standing EQUAL −2 and S2C −3 use actual 16:34 raw open 464.965, adverse sell 464.50, $1 fee each, completed 16:35 and posted/available 16:37. Physical shares −8→−10 and −10→−13. Actual pre-June9 checkpoint replay matches uncompressed events/daily/cohorts byte-for-byte. Old V4 remains strict UNRESOLVED/NOT_COMPARABLE, with the 18 odd-lot/derived-print evidence untouched; 465.04 was never adopted as an approved fill.

Five current-code source pilots pass: Jan4–8 2021, Jun2–11 2021, Aug24–26 2022, May9–17 2024, Nov27–Dec2 2024; 26 sessions/3,580 opportunities/eight accounts. See `V5_PILOT_RECONCILIATION_FINAL.md` and `audits/PILOT_CERTIFICATION_V5_9e093b3f6a62.json`. All-case gap outcomes are in `V5_SOURCE_GAP_AND_ORDER_IMPACT_REPORT_FINAL.md`.

## Integrity, actions, tests and qualifications

Final SHA256 and mtime verification: **10,410 protected objects and 227 original source partitions unchanged**. Original/Phase2/Phase3/Stage012/V1–V4 frozen bytes were not edited. Exact archived historical prediction parity remains NOT_COMPARABLE; Phase3 MATERIAL_NUMERICAL_OR_METHODOLOGICAL_MISMATCH is unchanged. V5 market HTTP requests: zero; replay uses the 48 original OOS monthly raw partitions plus the sealed V4 SIP supplement and action/OGN tapes; all 227 original source partitions remain integrity-checked.

Ordinary action confidence is retained: 16 supported and 251 single-provider observed cash events, three splits, eight verified-zero and eight unknown security-years. Unknown years are not promoted to verified nonpayers. Standalone 1.5%/3% yield sensitivity is kept outside funded buying power and never double-pays observed dividends. MRK/OGN primary signed 1:10 terms and actual quote tape are retained; CIL price/payment and clearing assumptions remain conditional, with 95.23/4.77 long tax-basis bookkeeping preserving total basis rather than creating NAV. Strict factual locates remain UNKNOWN; conditional academic shorting uses 2% ACT/365 marked physical-net-short carry, with 1/5% stresses. No live/PIT, NBBO, broker-fill or real locate certification.

The first funded attempt (`baseline_v5_r1`, 104 sessions) failed repeating-Decimal OGN share conservation. It and old code are preserved. The V5-only attoshare residual fix does not change source terms, strategy or precision tolerance. Fresh baseline/scenarios use code 9e093b3f6a62; 522,866 event /832 daily /89,663 cohort recoverable pre-spinoff rows match the failed run exactly. Unbounded price-time integer accumulation also prevents int64 overflow without changing carry formula.

Fresh recovery validation: **255 tests pass**, Ruff E/F/I passes, owned basic types **13 files /0 errors /0 warnings**. Full installed Pylance: **694 files /30 unchanged errors** —27 frozen replication plus three pre-existing unmodified Plotly viewer-test diagnostics, zero added diagnostics. This is not globally type-clean. Exact commands/stdout/stderr and comparisons are in the recovery namespace. Editor select `.venv`, basic severity, restart Pylance/refresh Problems; human UI refresh is not claimed.

## Transport recovery and run provenance

At recovery the original parent PID61526 and guard62477 were alive; output writers and checkpoint advance were verified before any action. G0 independently verified 8 complete /8 active (four resource-paused) /8 queued. No duplicate backtest, account reset, pilot or source acquisition was launched. Three existing workers later received bounded SIGCONT continuations only when real slots were free; the original guard released the remaining worker. Computing concurrency stayed <=4 and simulated clocks/code/inputs remained unchanged. All status and signal decisions are append-only in `recovery/20261110T124734Z/`.

## Scenario census

| Scenario | Actual terminal status |
|---|---|
| baseline | COMPLETE_RECONCILED |
| lag_1 | COMPLETE_RECONCILED |
| lag_5 | COMPLETE_RECONCILED |
| spread_1 | COMPLETE_RECONCILED |
| spread_15 | COMPLETE_RECONCILED |
| impact_1 | COMPLETE_RECONCILED |
| impact_15 | COMPLETE_RECONCILED |
| fee_0 | COMPLETE_RECONCILED |
| fee_0.01 | COMPLETE_RECONCILED |
| minimum_0 | COMPLETE_RECONCILED |
| minimum_2 | COMPLETE_RECONCILED |
| borrow_0.01 | COMPLETE_RECONCILED |
| borrow_0.05 | COMPLETE_RECONCILED |
| funding_0.05 | COMPLETE_RECONCILED |
| funding_0.10 | COMPLETE_RECONCILED |
| unknown_yield_0.015 | COMPLETE_RECONCILED |
| unknown_yield_0.03 | COMPLETE_RECONCILED |
| cil_postclose_33.30 | COMPLETE_RECONCILED |
| cil_postclose_40.70 | COMPLETE_RECONCILED |
| cil_sessions_1 | COMPLETE_RECONCILED |
| cil_sessions_10 | COMPLETE_RECONCILED |
| known_mrk_cross_prohibition | COMPLETE_RECONCILED |
| fixed_borrow_reject_recall | COMPLETE_RECONCILED |
| joint_adverse | COMPLETE_RECONCILED |

## Reproduction and next scope

All run commands, environment, failure history, Git state, code/config/source hashes and source rights/vintage limits are in the session reports, release bindings and child manifest. The CLI runs from repository root using `.venv`; unique output versions are mandatory and no force/RSA switch exists. Do not rerun completed work just to recreate a report. Large vendor payloads, journals and state checkpoints remain local/ignored; no commits/pushes were made.

Read `STAGE35_EXPLORATORY_BACKTEST_REPORT.md`, both presentation table directories, `FINAL_TEST_MATRIX_V5.md`, `OPEN_ISSUES_STAGE35_V5.md`, and `STAGE35_V5_HANDOFF_TO_STAGE6.md`. Stage6 must independently recompute source/ledger/fees/actions/carry, inspect reused-period/survivor/PIT/selection limitations, and design dependence-aware null/walk-forward/prospective checks under separate authorization. No independent statistical audit or deployment readiness is claimed.

The new child SHA256 manifest binds all V5 code/config/tests/docs/evidence/results with explicit self-exclusion. The final recovery handoff and companion manifest preserve initial and final frontiers rather than rewriting the initial inventory.
