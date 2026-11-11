# Exit-event schema and counting

The source is the sealed actual-exit-leg Parquet in the V3 funded manifest.
Keep distinct case, cohort key, ticker, entry origin, actual entry, actual
exit effective minute, exit decision, book-posted minute, signed pre-exit
shares, raw open, modeled fill, external flag, primary leg cause, simultaneous
triggers, entry/exit strength and saved source delay. Source clock is UTC.
Display sessions and full/half-day classification with XNYS and Eastern time.

All clock references are offline labels. The five-minute forward search
is a mark convention, never a statement that a past order would have filled.
A bar [u,u+1) has raw open at u, completion u+1 and assumed availability u+3.
The signed realized exit quantity uses contemporaneous raw-share units.

For dynamic V3, inherited early_exits compares exit_at against a lot
endpoint that was set to origin. Use separately reconstructed actual age,
risk-before-240 and policy-before-240. scheduled_final_exits counts final
EXIT-role lots, risk_final_exits final RISK_LIQUIDATION-role lots, and
cohorts_with_risk_fill any risk reduction. V3 retains a primary risk
cause even when a later ordinary partial closes the lot. Offline legs
retain their own submission cause. Risk closure is not synonymous with
early closure relative to a ten-session maximum. The exact binding
source is rapid_v3_dynamic/book.py and rapid_v2_diagnostics/book.py.

An account-wide marked breach submits reductions across holdings. A
lot's NAME/VINTAGE label does not identify which lot originated the breach.
Missing pretrade headroom and fine per-cohort fees/carry remain unavailable
unless saved. The analysis will mark unavailable fields explicitly.
