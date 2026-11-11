# Why conservative diverged

Match pre-funding candidates by weekly origin, ticker, side and identical
received feature lineage. The 832 opportunities yielded 438 fills in all
three regimes, 132 in none, and 262 in a subset. Only 22 filled exclusively
in conservative across the three arms. The source keys and first and final
fill markers are in the opportunity table. The aggregate rejection counts
close exactly: active same-side 325/206/214, signal cooldown 1/0/0 and
calendar maximum-age cutoff 8/8/8. The archive retains aggregate reasons,
with bounded samples of individual rejects.

| H85 compared with | Shared | H85 only | Comparator only | Shared gross advantage | Total gross advantage |
|---|---:|---:|---:|---:|---:|
| Standard | 463 | 35 | 155 | USD 16,263 | USD 17,600 |
| High-risk | 451 | 47 | 159 | USD 10,405 | USD 20,394 |

Every shared entry first-filled at the same time in its two regimes. Last
exit times changed for 309 of 463 and 297 of 451 shared lots. A symmetric
arithmetic bridge splits the shared gross delta into the change in signed
entry quantity times average per-share move, plus average signed quantity
times the change in the exit and entry prices. Partial exits are combined
in original share units.

| H85 comparison | Quantity contribution | Entry-price contribution | Exit-price contribution | Unshared contribution |
|---|---:|---:|---:|---:|
| vs standard | +USD 1,943 | 0 | +USD 14,320 | +USD 1,337 |
| vs high-risk | −USD 241 | 0 | +USD 10,646 | +USD 9,988 |

These are decompositions of observed paths. The matched sets are themselves
affected by funding. There is no controlled order-by-order causal effect.

## Ranked explanation

1. **Exit path and feedback have the strongest numerical support.** H85
   recorded 140 risk closures (28.1%) versus 420 (68.0%) and 374 (61.3%).
   Median actual hold was 1,986 scheduled minutes versus 1,170 in each
   comparator. Mean marked RTH gross was 16.54% versus 11.93% and 12.66%.
   H85 stayed invested longer despite lower intended initial allocation.
   It had zero gross exposure on 10.7% of sessions versus 28.3% and 25.0%.
   It also suppressed 119 more active same-side candidates than standard.
2. **A simple “risk exits destroyed winners” story fails on matched trades.**
   On 116 shared H85/standard lots with risk causes in both arms, H85 led
   by USD 17,479 gross and held a median 1,960 vs 1,054 minutes. On 208
   shared lots where H85 closed by policy and standard by risk, H85
   trailed by USD 4,538 gross, despite median 3,120 vs 729 minutes.
   Against high-risk those same category contrasts were +USD 13,730 and
   −USD 7,850. Exit categories are endogenous. Conservative's trailing
   group lost USD 46,873 net, offset by name-cap, maximum and weakening
   groups. Name-cap exits also include its largest observed winners.
3. **Opportunity selection and concentration matter.** Unshared lots explain
   about half the gross gap to high-risk. The narrow profitable tail,
   two-name dependence and 2023 loss weaken a general directional claim.
   Fixed entries and a different book path produced different opportunity
   sets, with no evidence of a better ranking rule in H85.
4. **Lower costs were secondary.** The cost savings were USD 751 vs
   standard and USD 821 vs high-risk. H85 paid more borrow. H85 gross
   per USD 1M executed turnover was USD 3,096 versus USD 219 and −USD 187.
   Net per USD 1M marked gross RTH dollar-years was USD 153,476 versus
   −USD 170,773 and −USD 225,542. Gross dollar-years use 252×390 RTH
   minutes. Category-level normalization uses a labeled entry-notional
   proxy because exact intraday capital by cohort is unavailable.

## What the cap evidence supports

Name-cap check counts were 38/49/20 and vintage-cap check counts 0/57/77.
Check classes can co-occur. Realized primary causes were 140/197/69 name
and 0/223/305 vintage. Raising the name cap alone left the vintage cap
binding. Near a fully utilized vintage constraint, the baseline sizing
formula's 0.2% reserve leaves roughly 0.04 percentage points of vintage room
before fees, rounding and other constraints. The 85% multiplier leaves
roughly 3 percentage points under the same idealized assumptions. This
is an ex-ante sensitivity calculation. Actual per-decision headroom,
price-shock size, which lot tripped the check, restricted cash and pending
reservations are absent from the compact archive. Measure those in the
next controlled test. A price increase in a long can cause a breach by
raising marked exposure even as it raises NAV.

## Fixed-horizon reference

V1 fixed 240 and V2 H100 parity each lost USD 9,834. V2 fixed 240 H85
lost USD 8,732. V2 H100 planned 1/3/5 sessions lost USD 9,912, USD 12,374
and USD 7,177 respectively. V2 changed one prespecified input at a time
within its replay protocol, with induced funding and holding differences.
V3 adds daily exits, actual-entry age, cooldown and calendar differences.
The V2-to-V3 comparison is historical context for a later controlled
test of the dynamic exit package.

[Regime bridge](extraction_02/R01_REGIME_DIVERGENCE.csv) · [Opportunity keys](extraction_02/R01_OPPORTUNITY_MATCH.csv) · [Fixed references](extraction_02/R01_FIXED_REFERENCES.csv)
