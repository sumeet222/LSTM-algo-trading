# Source and control bindings

All 13 accounts use the original 20 ordered survivors, 2021–2024 cached causal
features, V3 dynamic engine, V1 micro/retail costs and approved V5 raw/action rules.
The seven controls reproduce the archived V3 H85 accounts for M04/R01/M01/M05/M03/R07
and R01 H100. Regime is encoded CONTROL/H100 in this namespace only.
The signed directions, original entry schedules, 6/day or 5/week physical-entry
budgets, 10% name/20% vintage/100% gross/net caps, receipt +2, nominal+10 entry
expiry, prior-volume 1%, next valid raw open, fixed entry identities, original
borrow/cash/claims and maximum holds remain unchanged.

The original M01 already implements two successive micro weakening checks,
missing-score reset and two-check decisive reversal. The requested WEAK2 arm is
therefore an explicit identity experiment; no third check or new reversal
threshold is invented. M04/M05/R07 filter only EVENT_RESOLVED. Independent
SIGNAL_WEAKENING can preempt and may make the new confirmation ineffective.
M05 breakout direction means its immutable original signed trade; independent
original reversal continues to override. R07 checks are full-session slot1,
once per session; holidays and half days provide no synthetic check.

M03: v20 and gap/gap_z are log-return distances. Original trail=2*v20;
treatment=min(original,abs(gap/gap_z)), frozen before entry fill. Missing scale
abstains that leg. All other exits are unchanged.

R01: provisional H100 budget/name caps are unchanged before whole-share rounding.
For new u_i and prior completed daily log SD v_i, s_i=exp(v_i),
D=sum(u_i*s_i)+.20*sum(u_i*(s_i-1)),
C=.20*(N-R-L)-A, t=clip(C/D,0,1), with t=0 for no positive D.
A=sum(existing absolute committed value*s), L=sum(value*(s-1)), same vintage only,
including pending. Existing holdings remain unchanged. Missing existing scale
blocks new vintage risk; missing new scale excludes the leg before budgeting.
One common t precedes original whole-share/participation/minimum-notional gates;
there is no redistribution. For D>0 the constraint is C-tD>=0, decreasing in t;
the clipped root is maximal feasible. Existing risk liquidation is never waived.

The pilot is fixed at 2024-11-18 through 2024-12-02 (10 XNYS sessions), including
Thanksgiving half day, overnight and weekend. Synthetic witnesses force each
modified branch, even if no real trigger occurs. Before full result publication,
all controls must match all archived 1,005 daily rows and economic/count totals
at USD 1e-7; large dollar-minute integrals allow 1e-5 and relative rendering 1e-12.
The source-backed pilot also tests exact restart and AVGO 16:33 missing /16:34
conditional fill parity with V5. No historical broker fill is asserted.

The registry is sealed before funded pilot outcomes. Full run is one shared 48-month
source pass, 13 independent books, compact completed cohorts, physical fills,
daily rows, exit portions and four year-end compressed checkpoints; target <100MB.
Each mechanism is judged on BOTH total net and net per marked gross RTH dollar-year;
R01 additionally needs fewer vintage-trigger closures per original weekly candidate.
Tail reporting uses worst cohort/worst five, negative sum and name concentration;
no new threshold is fitted. Low real trigger support is reported explicitly.

All outcomes are post-selection exploratory on repeatedly reused 2021–2024 data.
The prior recommendation for untouched data governs future confirmation; this
owner-authorized historical diagnostic does not claim to supply it.
