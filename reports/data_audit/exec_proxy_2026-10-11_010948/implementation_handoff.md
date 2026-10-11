# Execution proxy compatibility and revised P2.2A handoff

Documentation contract only; examples below are invented arithmetic, not acquired prices, certified availability, generated labels or approved fills. Code and all seven historical blockers remain unchanged. Review before separately authorizing revised P2.2A.

## Compatibility / dependency matrix

| Component | Disposition | Exact effect / prerequisite |
|---|---|---|
| D2/D3 execution reference | AMENDED WHEN IMPLEMENTED | Versioned completed scheduled hourly stock CLOSE proxy replaces mandatory minute OPEN for this first pass; retain source/as-of identity, raw/share conversion and disclosed bias. Pinned texts remain historical. |
| TG0 and train-only floor | AMENDED WHEN IMPLEMENTED | Log proxy boundary returns; same five-name median, unscaled MAD, epsilon=max(1e-4,0.1×training median MAD). Rebuild target/floor lineage; no minute-derived artifacts relabeled. |
| D4 M2 | AMENDED WHEN IMPLEMENTED | Recompute proxy-target historical origin-matched returns, 20/60 windows, maturity and pooled origin-balanced scaler; retain approved channel/coverage rules. |
| P2.1 clocks | UNCHANGED | cutoff, issue≤cutoff+5min, ceil(issue+1min) entry, entry+240min exit, same-session/calendar/DST/early-close exclusion; schedule is not a fill. |
| Existing minute-based P2.2A prompt/code | AMENDED WHEN IMPLEMENTED | Old instruction superseded for execution-reference design; retain src/lstm_data/labels.py/tests and old reports as history. Revise prompt before use; registration runs no P2.2A code. |
| D13-C01, causal admission | UNCHANGED | forecast_issuable, entry_eligible, label_valid and execution_outcome separate; missing future outcomes never delete admitted entries. |
| Policy A/B, sizing/exposure/netting | UNCHANGED | fixed intended holds, whole-pair conflict veto, ±24.75%-per-leg, net physical external orders, gross admission and physical holdings; no general accounting relaxation. |
| Base execution costs | UNCHANGED | independent 0/2/5/10bps scenarios, applied once per net physical external fill; proxy delay bias is not certified as included. |
| Split/dividend/short cashbook | BLOCKED | proven raw/split-adjusted conversion and actual action/share/borrow coverage still required; affect only dependent labels/economics. |
| D5e retries/emergency/risk observations | FUTURE APPROVAL NEEDED | explicit hourly-observation approximation, next-valid-observed retry/mark, outstanding position, detectable risk schedule, overnight exceptions; no minute-continuous claim or phantom liquidation. |
| Contextual buy-and-hold 09:30/15:59 | FUTURE APPROVAL NEEDED | independent benchmark boundary-price convention; ranking proxy endpoints cannot silently replace benchmark opportunity. |
| G0 / shared execution-rule governance | BLOCKED | Track A decision registered; Track B approval/acknowledged comparability and reviewed authority/version migration unresolved. Existing CT decisions unchanged. |
| G1 source/actions | BLOCKED | stock OHLC semantics, exact scheduled-bar coverage, historical publication/as-of and actions independently evidenced; a close proxy does not supply those facts. |
| G2 labels/maturity/purging | BLOCKED | revised versioned reference/target/M2/floor implementation, synthetic and supported real traces, source checks and review needed. |
| G4 baseline/physical simulator | BLOCKED | exception/benchmark amendment and verified price basis, cashbook/netting/admission/cost replay; prediction-only and economic claims distinct. |
| Architecture, universe, windows, confirmation, 48×16 family, training budget | UNCHANGED | frozen first-pass menu and 40-pair ceiling; no source or model activation. |
| TA-POSTPASS-OVERNIGHT-001 | FUTURE APPROVAL NEEDED | DEFERRED_CONDITIONAL_RESEARCH; separately preregister only if development diagnostics motivate it; no data/labels/training now. |
| USA500 / future conventional S&P 500 | BLOCKED | current U1–U5 / MC0–MC2 holds, source-unselected future direction and course-series amendment requirements untouched. |

## Nominal hand arithmetic and exact keys

Use an ordinary session such as 2020-07-01. ET is EDT here; UTC stored internally. No row shift, nearest bar or closing stub substitution.

| Origin | Fixed reference endpoints (ET / UTC) | Issue / simulated entry / simulated exit ET | Invented raw same-share closes | Proxy return |
|---|---|---|---|---|
| 1 | 10:30 / 14:30Z → 14:30 / 18:30Z | 10:32 / 10:33 / 14:33 | 100 → 102 | ln(102/100)=ln(1.02)≈0.019802627297 |
| 2 | 11:30 / 15:30Z → 15:30 / 19:30Z | 11:32 / 11:33 / 15:33 | 200 → 198 | ln(198/200)=ln(0.99)≈−0.010050335854 |

Each reference interval and intended event interval is 240 minutes. Nominal reference ages at both events are 180 seconds. Each stock uses its exact (symbol, session, origin, period_start, period_end) scheduled full-hour source row/version. Verify positive finite CLOSE and genuine one-hour stock field semantics; the index bar and 15:30–16:00 stub are ineligible. Apply TG0 to all five valid returns, subtract their median, divide by unscaled MAD plus the separately training-fitted frozen epsilon. No arithmetic example is a five-name source-coverage PASS.

## Shifted issuance and availability

For origin 1, actual issue 10:35:00 ET (allowed +5min), entry 10:36, exit 14:36. Original input cutoff and fixed reference boundaries stay 10:30 and 14:30; event/reference ages become 360 seconds, not 180. This is the existing P2.1 event formula, not a favorable-price search. Revised coding must retain actual timestamps and exact original origin keys. Any shifted-event mapping not supported by these fixed scheduled endpoints must fail closed for human review. Do not choose a later entry feature, substitute another bar or invent publication delay.

Historical completed input references must be available by each input's cutoff; entry reference must already be known at entry. Exit reference availability and scheduled execution outcome are separate. Unknown publication basis cannot become DOCUMENTED because a file was later retrieved. If a reference is not usable at the scheduled event, record its reason and unresolved execution; do not retrospectively assert a fill once it appears.

## Missing hour / exit and D13-C01 counterfactual

Missing the exact 10:30 input/entry reference invalidates that dependent forecast/entry; no 09:30 or 11:30 substitution. Missing 14:30 exit reference can invalidate a later supervised label while leaving an earlier eligible 10:33 entry unchanged. Hold the admitted physical exposure outstanding and suspend dependent new entries per existing intent; actual hourly retry/mark/exit treatment awaits the separate portfolio amendment.

Counterfactual for future tests: two histories identical through 10:33, with identical issued scores, historical source facts and portfolio state. One later contains valid 14:30 exit references; the other lacks an exit (or receives it too late). Both must have identical forecast_issuable and entry_eligible decisions. label_valid / execution_outcome may differ later. No hindsight deletion of the second entry, no invented exit, no successful portfolio path from a complete-label-only dataset.

## Maturity / purge and historical M2

For a otherwise valid label, permissible maturity is no earlier than max(scheduled 240-minute exit event, required supported exit-reference availability across all five stocks). Nominal first-origin maturity cannot precede 14:33 even when closes complete at 14:30. If last supported exit observation only becomes available at 14:40, maturity is no earlier than 14:40; label validity still requires all source/action/reference predicates, and availability after scheduled exit does not certify that a fill occurred at 14:33. Unknown availability blocks verified maturity. Shifted first-origin maturity cannot precede 14:36 in the example above.

Purge fitting/evaluation boundary-crossing labels using scheduled outcome and permitted actual maturity, not dataframe rows or bar-end alone. Keep frozen split dates and D6g last-63-calendar-session validation tail/adequacy unchanged; transforms fit inner training for stopping and all permitted training for refit. Revised tests must include a hypothetical boundary between observation completion and event maturity, and between scheduled exit and delayed source availability. No confirmation prices are needed to test this.

Historical M2 may consume only strictly earlier origin-matched proxy outcomes matured at that historical feature step's own cutoff. Preserve 10:30 vs 11:30 origin identity, approved 19/20 and 57/60 coverage/max-gap and 50/50 pooled-origin scaling. Regenerate M2, TG0 floor and affected scalers under new lineage; old minute-derived values cannot be renamed.

## Split / price basis example

Invented two-for-one action on (entry,exit]: raw entry 100, raw exit 51. Entry-share-equivalent exit value is 2×51=102, giving ln(102/100), rather than the fictitious ln(51/100) crash. Adjusted 50→51 prices can express the same return only with proved adjustment basis. A raw-share cashbook retains raw 100/51 prices and doubles actual shares at the action; feeding adjusted 50 into cash accounting while also doubling raw shares is wrong. Preserve action IDs/effective instants/share conversion and dividend/short obligations. Unknown basis/action scope blocks affected output, not a fabricated zero-action assumption.

## Versioned provider contract for later coding

Conceptual interface (not implemented): resolve_reference(event, symbol, expected_slot, source_version, execution_version) → immutable reference(price or None, symbol/side, scheduled_event_at, observation_id, period_start/end, available_at or unknown, availability_basis, price_basis, source/version, proxy_kind, lag_seconds, validity_reason, action/share_basis_ids).

Explicit kinds MINUTE_OPEN and COMPLETED_HOURLY_CLOSE_PROXY retain distinct execution/target versions. No fallback between them. Provider emits data and reason; model and ledger consume the common contract, with model access limited to causal inputs. Keep original information cutoff, issue, event, observation end and availability separate; lag=event−observation_end, not source age relabeled as maturity. IDs bind hourly aggregation/calendar/action/availability versions, source rows, labels, M2, fitting membership, epsilon/scalers and later result comparisons. No new runtime/config API exists from this document.

Audit trace: source observation → scheduled slot/as-of → origin/issue → four independent eligibility/outcome flags → target/execution/M2 version → actual maturity/purge → training-only fit IDs → later prediction/order/physical equity events. Before implementation, revise the old minute-open P2.2A prompt and explicitly preserve source holds, shared-rule review and portfolio exception dependency. Re-evaluate matched dependent artifacts if any empirical runs exist; current ledger reports zero neural fits. No delay-sensitivity values selected; a development-only adverse-movement diagnostic remains separately approved work, independent of base costs.
