# SIP feasibility pilot

Status: **blocked_access_or_schema**.

SIP access passed: False. Native-hour timing gate passed: False.

Missing APCA_API_KEY_ID / APCA_API_SECRET_KEY (or legacy aliases). Set locally; never paste credentials in chat.

| Probe | Symbol | Rows | Missing desired starts | Partial overlaps |
|---|---|---:|---:|---:|

Storage used for small pilot samples: 0 bytes.

Split adjusts historical price and volume retrospectively. No dividend total-return adjustment. Levels are not point-in-time vintages. Corporate-action reference/event audit still needed.

If native hours fail, recommended next controlled pilot: approved 30Min source bars combined into 09:30-anchored 60-minute windows, retaining the final 30-minute stub. Roughly twice the source rows; see bulk dry-run estimate. Do not shift native hours or proceed with bulk, IEX, a subscription, or 1-minute history.

This implementation deliberately refuses native-hour bulk when closing stubs or opening overlaps cannot be established from provider aggregates. A 30Min change requires researcher approval, implementation and a fresh pilot.
