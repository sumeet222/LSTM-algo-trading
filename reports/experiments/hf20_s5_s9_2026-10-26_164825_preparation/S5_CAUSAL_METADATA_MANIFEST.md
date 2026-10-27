# S5 causal metadata manifest — proposed reduced design

**Six added clock channels; 22 total inputs. No new quality/age flag enters the LSTM.** This is the single reduced design permitted by brief §3.1 when a historical flag's knowability cannot be established. It tests explicit clock/elapsed context. It does **not** complete the separate causal missingness/indicator-age hypothesis.

## Why reduced metadata is necessary

The existing canonical hourly source contains observed-minute counts, proxies, terminal timestamps, post hoc quarantine/action masks and feature fallbacks. The native calculator can identify a numerical fallback in the current revised history. It does not supply a historical `available_at`/first-seen timestamp proving that every repair or per-indicator reason was knowable at each original cutoff. Later repair/quarantine facts must not become newly privileged forecast inputs. Missing prices and unverified publication timing remain distinct; the inherited source's two-minute timing-proxy qualification is retained. We do not assert that observed prices are unavailable merely because publication latency is unknown.

Current source/fallback/terminal-age fields are retained for explicitly retrospective diagnostic strata. They are not represented as causal live masks. Genuine zero/unchanged observations remain distinct from missing/fallback in the audit; numerical equality alone cannot identify the category. No source-era identifier, ticker embedding, newly observed opening gap, end-of-day fact or repaired 16:00 close is added.

## Existing FT16 dictionary

| Channels | Existing information and timing | What they do not certify |
| --- | --- | --- |
| M1 | Completed-hour open/close log return divided by trailing RMS60/floor; same source cutoff as the completed hourly step | Overnight close-to-open jump, explicit clock, historical publication of missingness |
| M2 | Prior matured same-origin 20-session mean / 60-session RMS, locked at each historical input session start; seven S4 contexts | Current future return, contemporaneous outcome median/MAD, an independent market state |
| M3/M4 | Prior regular-session momentum over 5/105 sessions, volatility scaled under frozen recipe | Current unfinished session or a new 16:00 daily close |
| V1/V2/V3 | Log RMS12, log RMS60 and their difference; original OC-return basis and floors | Exact future endpoint volatility or an observed overnight gap |
| B1/B2 | Completed-hour high/low range and close-location state | Complete intrahour path or publication timestamp |
| Q1 | Completed-hour volume relative to the original preceding-day/hour context | That a fallback zero is a genuine zero, or a causal repair/availability flag |
| Q2 | Prior completed regular-session 5/60 volume summaries, with inherited lower-bound/compatibility/fallback policy | Completed current-day full volume or a future action-vintage fact |
| T1/T2 | Frozen price/SMA20 distance and prior daily-sign trend | Exact source age or an explicitly supplied forecast clock |
| T3/T4/T5 | Original normalized EMA6–18/EMA24–72 differences and RSI state using historical completed inputs | A recovered minute path or new independent source |

The 15:30 last-full-hour daily-close surrogate remains a surrogate. S4 genuine 16:00 endpoint/component prices are not backfilled into these indicators. At 09:30 every one of the 48 FT16 steps is from before the current session's unfinished first hour. Previously realized gaps can influence old trends/indicators as originally defined; no newly observed 09:30 gap is appended to that previous-session sequence.

## Exact six channels and knowability

Let p=(step_end−session_open)/(scheduled_session_close−session_open), using the existing XNYS calendar. Let o be the analogous fraction at the forecast origin. For each of the original 48 completed steps append, in this order:

1. `step_sin = sin(2πp)`.
2. `step_cos = cos(2πp)`.
3. `session_boundary = 1` if this scheduled step begins a different session than the preceding scheduled step; otherwise 0.
4. `elapsed_scheduled_wall = min(log1p(Δhours)/cap, 1)`. Δhours is the difference between consecutive scheduled completed-step ends in UTC. **It is not genuine observation age.** `cap=max(training-prefix unique-input-step 99th percentile of log1p(Δhours), log(2))`, separately fitted for calibration and refit. Normal steps, overnight/weekend/holiday gaps remain distinct; the first global warmup step uses Δhours=1 and cannot be a scored first history step.
5. `origin_sin = sin(2πo)`.
6. `origin_cos = cos(2πo)`.

Origin context is broadcast across the 48 steps. The calendar and origin are known by issuance. Only the cap is fitted; it uses historical input indices of the fitting role, no validation/OOS parameters or future returns. Early-close session durations and actual UTC DST/weekend intervals are respected. There is no attention, recurrent router or special cell; only input dimension changes from 16 to 22. The fixed factory has 7,201 parameters, one hidden-32 layer, original .1 final dropout and scalar T2R head.

## Coverage and comparison

`S5_S9_ROLE_COUNTS.csv` verifies all four years × four roles against archived S4 origin identities; `S5_CAUSAL_COVERAGE_AND_DIAGNOSTIC_STRATA.csv` reports each slot, source/fallback rates and terminal-age diagnostics. All six proposed fields are finite on every original S4 eligible window. No additional origin/stock exclusion is introduced.

Primary controls are frozen S4 T2R, N1/M1 and P on identical keys/targets; S4 NR remains context only. Parameters/history differ, so this is a training-with-clock-metadata package comparison, not isolated causal attribution to time or data quality. A zero-metadata forward pass is not a trained ablation; none is proposed. Full four-role standard ranking and T2R/NUM/MAD/energy diagnostics reuse the S4 kernels.
