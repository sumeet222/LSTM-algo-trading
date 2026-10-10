# SIP feasibility pilot

Status: **passed**.

SIP access passed: True. Source/aggregation timing gate passed: True.

All selected probe requests consumed to final page.

| Probe | Symbol | Rows | Missing desired starts | Partial overlaps |
|---|---|---:|---:|---:|
| historical_2020 | AAPL | 218 | 0 | 0 |
| historical_2025 | AAPL | 192 | 0 | 0 |
| fall_dst | AAPL | 60 | 0 | 0 |
| spring_dst | AAPL | 60 | 0 | 0 |
| early_close | AAPL | 26 | 0 | 0 |
| aapl_split_window | AAPL | 92 | 0 | 0 |
| wmt_split_window | WMT | 90 | 0 | 0 |

Storage used for small pilot samples: 82237 bytes.

Split adjusts historical price and volume retrospectively. No dividend total-return adjustment. Levels are not point-in-time vintages. Corporate-action reference/event audit still needed.

If native hours fail, recommended next controlled pilot: approved 30Min source bars combined into 09:30-anchored 60-minute windows, retaining the final 30-minute stub. Roughly twice the source rows; see bulk dry-run estimate. Do not shift native hours or proceed with bulk, IEX, a subscription, or 1-minute history.

This implementation deliberately refuses native-hour bulk when closing stubs or opening overlaps cannot be established from provider aggregates. A 30Min change requires researcher approval, implementation and a fresh pilot.
