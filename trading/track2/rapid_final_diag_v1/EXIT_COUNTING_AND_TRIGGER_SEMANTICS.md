# Exit counts and trigger semantics

A completed cohort is one immutable virtual entry key. External physical orders
and internal/external exit portions are separate units; partial exits remain
separate settled portions until the cohort finally closes. Do not add these
counts together. The complete compact cohort table restores actual allocated
cash/actions/carry and costs instead of guessing from a first entry price.

The inherited dynamic V3 adapter sets the internal legacy endpoint field to
origin when submitting a cohort. Therefore inherited early_exits, defined by
exit_at<endpoint, is zero under this dynamic contract. It does not establish
that no risk exits occurred, or that every cohort reached780 minutes/10 sessions.
The true maximum is stored separately in the dynamic group and monitored through
prospective orders. Actual scheduled holding ages use the exchange calendar.

scheduled_final_exits counts the last role EXIT, which includes signal/event/
trail/max-hold policy; it does not mean every exit was a calendar maximum.
risk_final_exits uses the final role RISK_LIQUIDATION. cohorts_with_risk_fill
counts any earlier forced portion. risk_closed_cohorts retains a risk primary
if any such portion occurred even when the final portion later had a policy role.
risk_before_240 and policy_before_240 compare actual completed age against a
common240-minute reference; they do not define a dynamic counterfactual early exit.

A marked breach creates a whole-account prospective risk reduction. If both name
and vintage caps breach, primary name takes precedence; any-vintage trigger count
can therefore exceed primary-vintage. A resulting cohort's tag is not proof that
its individual stock caused the account breach. Do not sum overlapping triggers
as mutually exclusive cohorts. The R01 reserve comparison reports both primary
and any-vintage closure counts per original832 candidate intents.

Only EVENT_RESOLVED is confirmed in M04/M05/R07. Independent weakening, decisive
reversal, trailing and maximum-hold policy retain original trigger ordering and
can preempt the wait; mandatory risk/collateral/action/borrow handling remains
outside and higher priority. Recovery counts refer to pending checks, not to
retroactively cancelling an already submitted/fill-observed broker order.

The exact seven-control parity covers these published counts and whole economic
paths. It is not independent certification of source/action vintages or actual
historical execution/locate availability.
