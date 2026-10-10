# SIP feasibility pilot

Status: **blocked_timing_or_coverage**.

SIP access passed: True. Native-hour timing gate passed: False.

All selected probe requests consumed to final page.

| Probe | Symbol | Rows | Missing desired starts | Partial overlaps |
|---|---|---:|---:|---:|
| historical_2020 | AAPL | 110 | 49 | 7 |
| historical_2025 | AAPL | 96 | 42 | 6 |
| fall_dst | AAPL | 30 | 14 | 2 |
| spring_dst | AAPL | 30 | 14 | 2 |
| early_close | AAPL | 13 | 4 | 1 |
| aapl_split_window | AAPL | 46 | 21 | 3 |
| wmt_split_window | WMT | 45 | 21 | 3 |

Storage used for small pilot samples: 69080 bytes.

Split adjusts historical price and volume retrospectively. No dividend total-return adjustment. Levels are not point-in-time vintages. Corporate-action reference/event audit still needed.

If native hours fail, recommended next controlled pilot: approved 30Min source bars combined into 09:30-anchored 60-minute windows, retaining the final 30-minute stub. Roughly twice the source rows; see bulk dry-run estimate. Do not shift native hours or proceed with bulk, IEX, a subscription, or 1-minute history.

This implementation deliberately refuses native-hour bulk when closing stubs or opening overlaps cannot be established from provider aggregates. A 30Min change requires researcher approval, implementation and a fresh pilot.
