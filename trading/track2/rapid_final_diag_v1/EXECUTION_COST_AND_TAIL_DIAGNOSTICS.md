# Physical costs, tails and actual-price distinctions

The inherited cash change is -signed external shares*executed price-commission.
Executed price is the later valid raw open plus an adverse assumed concession.
Raw-price gross excludes that modeled concession; gross+actions-commission-spread-
impact-borrow-funding equals terminal NAV minus initial. Subtracting costs again
from executed-price gross would double charge. All 13 bridges and complete cohort
sum checks pass. Signed decision-mark→raw-open arrival is reported separately;
absolute arrival is not a fee, and a favorable movement is not a measured spread.

MICRO_PRO retains h=.0003*clip(v20/v60,.5,2), clipped1–6bp, plus prior-ADV/physical
net-size impact .0001*ratio*sqrt((abs(q)/ADV20)/.0001), clipped.25–5bp; commission
$.002/external share with no minimum. RETAIL retains assumed5bp+5bp per external
side, adverse cent rounding, $.005/share and cumulative $1 minimum once per physical
order across partials. Internal transfers pay zero external costs. Net physical
short carry remains2% ACT/365 across calendar days; base funding0. Short proceeds
are restricted. No measured midpoint, quote spread, locate or broker fill exists.

The canonical physical-cost table is supplement_01/PHYSICAL_COST_DIAGNOSTICS_COMPLETE.csv,
with ORDER_NOTIONAL_BANDS.csv and PHYSICAL_ORDERS_RECONCILIATION.csv. The regular
funded fill export omitted three OGN disposal records already charged by the
account. Exact signed quantities12/12/6, actual raw34.28, commission$1 each and
concessions survive in the content-bound 2021 checkpoint. They are added only to
the analysis supplement, preserving the original funded manifest. All physical
commission, concession, impact, notional and distinct-order counts then reconcile.
This is an export repair, not altered financial accounting or a rerun.

Median order notionals: M04 about$5,600; M01$2,947; M05about$3,200; M03about$2,900–3,000;
R01$4,691 H100/$4,993 guard/$5,619 H85; R07about$8,400. About95–98% of retail orders
bind the $1 minimum. The fee floor is physical-order level, not cohort-level.
The 0.5×/1.5× concession columns are same-holdings arithmetic, not rebudgeted or
independently funded counterfactuals. Guarded R01 becomes -$2,524 at1.5×, R07 -$347;
M05 remains deeply negative even at0.5×. No favorable quote assumption was inserted.

Full net/gross winner and loser sums, worst cohort, worst/best five and profit
factors are in analysis_01/COHORT_TAILS.csv. M03's worst-five reduction does not
improve net economics. M04's worst-five loss worsens. M05's worst-five improves
slightly but its negative gross price is a serious contrary finding. R01/R07
positive totals disappear after arithmetic removal of their two leading names.
Those removals are descriptive sensitivities, not executable portfolios.

Raw source gaps, receipt+2, standing orders, prior-minute1% participation, partial
fees and next-valid execution remain inherited. All control daily cash/exposure
and reason counts match. No material unresolved terminal exposure remains; signed
payable claims remain valued by the original conditional protocol, including
post-2024 pay metadata without post-2024 prices. Source/unknown action caveats
and conditional borrow remain. Source samples and action tests do not certify
point-in-time completeness or actual historical broker availability.
