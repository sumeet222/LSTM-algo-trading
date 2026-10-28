# S2-D — dedicated close-to-open gap magnitude

**Status: BLOCKED. Zero neural/non-neural fits and no forecast metrics.**

This is a separate scientific task, not an adverse score or a result of S2-B. No alternative label/population/architecture was substituted.

## Frozen specification

Protocol: `reports/experiments/hf20_s9_mag_stage2_bcd_2026-10-28/s2d_overnight_hold/protocol_v2.json`. The original scientific specification preceded numerical source proof and fits. D's append-only v2 removes inherited four-hour scale/threshold reference fields from chronology metadata; no gate or scientific design changed. No gap scale or threshold was fitted or transferred.

- F22/selector:sessions31<50;one role month has fewer than5 sessions
- F23/selector:sessions48<50;one role month has fewer than5 sessions

| year | role | sessions | origins | rows | months | minimum_month_sessions | first_date | last_date | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | inner_train | 1773 | 1773 | 35460 | 105 | 5 | 2011-04-01 | 2020-06-29 | PASS |  |
| 2021 | selector | 53 | 53 | 1060 | 3 | 15 | 2020-07-13 | 2020-09-28 | PASS |  |
| 2021 | restricted_refit | 1833 | 1833 | 36660 | 108 | 5 | 2011-04-01 | 2020-09-28 | PASS |  |
| 2021 | calibration | 43 | 43 | 860 | 3 | 12 | 2020-10-12 | 2020-12-29 | PASS |  |
| 2021 | oos | 145 | 145 | 2900 | 12 | 3 | 2021-01-13 | 2021-12-30 | PASS |  |
| 2022 | inner_train | 1948 | 1948 | 38960 | 115 | 5 | 2011-04-01 | 2021-04-28 | PASS |  |
| 2022 | selector | 31 | 31 | 620 | 5 | 3 | 2021-05-13 | 2021-09-29 | BLOCKED | sessions31<50;one role month has fewer than5 sessions |
| 2022 | restricted_refit | 1984 | 1984 | 39680 | 120 | 3 | 2011-04-01 | 2021-09-29 | PASS |  |
| 2022 | calibration | 44 | 44 | 880 | 3 | 8 | 2021-10-12 | 2021-12-30 | PASS |  |
| 2022 | oos | 176 | 176 | 3520 | 12 | 4 | 2022-01-12 | 2022-12-29 | PASS |  |
| 2023 | inner_train | 2124 | 2124 | 42480 | 128 | 3 | 2011-04-01 | 2022-05-27 | PASS |  |
| 2023 | selector | 48 | 48 | 960 | 4 | 4 | 2022-06-10 | 2022-09-26 | BLOCKED | sessions48<50;one role month has fewer than5 sessions |
| 2023 | restricted_refit | 2178 | 2178 | 43560 | 132 | 3 | 2011-04-01 | 2022-09-26 | PASS |  |
| 2023 | calibration | 40 | 40 | 800 | 3 | 10 | 2022-10-13 | 2022-12-29 | PASS |  |
| 2023 | oos | 147 | 147 | 2940 | 12 | 5 | 2023-01-12 | 2023-12-28 | PASS |  |
| 2024 | inner_train | 2282 | 2282 | 45640 | 140 | 3 | 2011-04-01 | 2023-05-30 | PASS |  |
| 2024 | selector | 52 | 52 | 1040 | 4 | 9 | 2023-06-12 | 2023-09-28 | PASS |  |
| 2024 | restricted_refit | 2341 | 2341 | 46820 | 144 | 3 | 2011-04-01 | 2023-09-28 | PASS |  |
| 2024 | calibration | 32 | 32 | 640 | 3 | 6 | 2023-10-11 | 2023-12-28 | PASS |  |
| 2024 | oos | 154 | 154 | 3080 | 12 | 7 | 2024-01-11 | 2024-12-30 | PASS |  |

## Source and timing proof

The eligibility calculation is new: normal full sessions only, one15:30 origin, source-input eligibility, all20 genuine current16:00 end-of-session references and next09:30 minute opens, original action-basis safeguard, next-open+2min maturity and the48-step role embargo. It does not reuse4h label eligibility/maturity. For example, F21 selector has53 eligible gap sessions rather than47 original4h15:30 origins. Early closes are excluded by the known calendar; no remapping to another origin.

Minimums were declared before counting:252 training/refit sessions,50 selector,25 calibration,100 OOS; at least5 sessions in every selector/calibration month and all12 OOS months. F22 has31 selector sessions and a month with3; F23 has48 and a month with4. These were not relaxed. Other admissible years were not fitted into a different partial design after an any-fold gate failed.

The intended primary is own-gap global-smear LSTM, with raw diagnostic, own phase s_gap and stock raw mean/median/last20 genuinely matured gap controls. None was fitted. No 4h scale, predictor or baseline was relabeled as a gap forecast; no gap metric is compared numerically with4h MSE. A15:32 forecast precedes the16:00-to-next09:30 holding interval; actual execution/auction fills are unverified.

## Decision and boundaries

Reconsider only through a separate researcher decision about this exact source/coverage blocker. No new source, proxy, selector extension, minimum reduction, extra fold or future-data release is approved.2021–24 are exploratory/post-search;2025 outcomes and protected2026 values/hashes remain unused. No trading/options/strategy or deferred C0-intraday/M1-overnight route was run.
