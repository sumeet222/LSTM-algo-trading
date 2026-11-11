# R01 one-v20 reserve and actual capital feedback

u_i is unchanged H100 absolute provisional dollars after the existing name cap and
before integer shares. v_i is the strictly prior completed-session daily log SD
v20 from the original trailing contract; it is not an expected return. s_i=exp(v_i).
N is received marked NAV; R is original .002*N plus eligible physical-order minima.
Existing same-vintage filled plus pending absolute value x_j gives A=sum(x_j*s_j)
and L=sum(x_j*(s_j-1)). The permitted inequality is

    A + t sum(u_i s_i) <= .20 [N-R-L-t sum(u_i(s_i-1))].

Thus C=.20*(N-R-L)-A, D=sum(u_i*s_i)+.20*sum(u_i*(s_i-1)), and
t=clip(C/D,0,1) for D>0; otherwise zero. C-tD is affine decreasing. No larger
positive feasible t exists beyond the clipped root. Decimal exponential/division
uses the existing book precision. Numeric tests allow only 1e-20 rounding at the
algebraic root; financial assertions remain USD1e-7. Missing/invalid new v20 removes
the leg before budget; missing existing v20 blocks new vintage commitments. Old
positions, restrictions and liquidation are untouched. Common t precedes all
original whole-share, volume, ticket floor and short/cash checks, with no redistribution.

The 538 actual proposed leg records have t .947129–1, mean .975705, median .975054.
The same-vintage existing A/L are zero in these actual once-weekly decisions;
nonzero existing reservations are covered by synthetic witnesses, not falsely
claimed as observed market support. See funded/R01_ENTRY_RESERVES.csv for every
N/R/A/L/t, current name exposure, gross, restricted funds, old/new USD and rounded
signed shares. supplement_01/R01_STRESS_INEQUALITY_CHECKS.csv independently groups
these rows by original origin and confirms all stressed-vintage inequalities.

Unchanged H100: net -$7,629.389176; gross price $1,499.048; 618 cohorts/1,254 orders,
420 risk closures, 223 primary-vintage closures (233 with any vintage trigger).
Guarded H100: net +$991.126461; gross $10,197.5678; 538 cohorts/1,100 orders,
242 risk closures, 40 primary-vintage (50 any-trigger). Both have 832 original
weekly candidate intents. Rates: primary .268029→.048077; any .280048→.060096.
Unchanged H85: +$10,488.392222, 498 cohorts/1,016 orders, 140 risk closures and
zero vintage closures. Whole-account tags and simultaneous name/vintage causes
must not be interpreted as an individually identified causal exit.

Mean RTH gross/NAV: H10011.93%, guarded15.70%, H8516.54%. Guarding slightly smaller
commitments can leave more capital invested by avoiding disruptive cap events.
Gross exposure-year normalization also improves versus H100, but remains far
below H85. Of shared filled keys, 336 exits and 413 entry notionals differ.
114 H100-only and 34 guard-only cohorts demonstrate endogenous opportunity paths.
All marked name/vintage/aggregate/collateral rules and mandatory exits still run.

Guarded annual returns: -0.344%, +0.977%, -1.430%, +1.815%. TSLA/AVGO net $7,176
versus total $991; removing them arithmetically leaves -$6,185. This supports an
entry-reserve mechanism in this sample, not a validated momentum or sizing edge.
A next design must retain H85/H100 unchanged and explicit per-entry constraint
records. No extra buffer level, rank filter or LSTM experiment was run.
