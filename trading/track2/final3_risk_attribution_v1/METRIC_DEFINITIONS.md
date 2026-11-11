# Metric definitions and availability

This read-only analysis uses 12 sealed MATCHED accounts, 2021-01-04 to 2024-12-31,
1,005 ordered XNYS sessions each. All begin at $100,000, with no annual resets.
`ANALYSIS_PROTOCOL.json` was sealed before the new descriptive outcome calculations.
Returns use each account's own capital path; overlapping trades are not independent.

## Daily performance

r[t] = NAV[t]/NAV[t-1] - 1, with NAV[0-before-first-session] = 100000. Net dollar
change = NAV[t] - NAV[t-1]. First-day returns include the initial capital observation.
Total return = last NAV / 100000 - 1. Calendar CAGR = (last NAV/initial)^(1/Y)-1,
Y = actual days from first to last saved session / 365.25 (3.98905 years here).
The first observation is end-of-session, so this explicit convention omits the
initial intraday fraction. Calendar CAGR is supplemental to the prior archive's
252/1005-session compounding convention; native Sharpe/DD match the prior archive.
Annual P&L/return start from the previous year's actual terminal NAV (initial 100000
for 2021), never from a new $100k reset. Within-year DD restarts the peak reference
at that year's opening wealth; full-period DD does not reset.

Sample SD uses ddof=1. Annual volatility = sqrt(252)*SD(r); Sharpe = sqrt(252)*mean(r)/SD(r),
rf=0. Downside deviation = sqrt(mean(min(r,0)^2)) over ALL sessions, MAR=0; annual downside
semivolatility multiplies by sqrt(252); Sortino = sqrt(252)*mean(r)/downside deviation.
Upside semivolatility uses max(r,0). Zero or tiny denominators return unavailable,
not infinity. Nonfinite/nonpositive NAV or absent daily rows trigger HOLD. Returns
are computed in float64 from saved daily marks; exact terminal/account bridges use
original Decimal strings with $1e-7 tolerance. Exact initial+net and float NAV are
both exported, with their numerical residual.

Historical VaR95/99 = minus the linear 5%/1% daily-return quantile. ES95/99 = minus
the mean of the worst ceil(alpha*N) returns, stable chronological tie-breaking;
N=1005 means 51/11 observations. Positive values denote loss (not clipped if all
returns are gains). VaR and ES use slightly different finite-sample conventions,
explicitly preserved. Quantiles 1/5/25/75/95/99%, loss-day fraction and daily dollar
loss are reported. ES99 has only eleven points; it is imprecise and not a reliable
extreme-loss model. Optional tail-asymmetry measures are descriptive ratios.

Drawdown = NAV / running maximum(including initial NAV) - 1. Latest equal-height
peak becomes the reference. Recovery requires NAV >= peak, and the recovery day
is not counted underwater. Time to trough = observed session index difference;
longest underwater = maximum count of strictly below-peak saved observations in a
spell. Unrecovered spells end at 2024-12-31 and are flagged. Three worst episodes
per book retain peak/trough/recovery dates; yearly DD and control-selected matched
calendar intervals are separate projections. No episode duration assumes wall-day
or trade independence.

## Accounting, costs and capital

Daily NAV = cash + signed physical inventory value + ordinary/special claims + special
asset marked value. Restricted short proceeds are ALREADY inside cash. Cumulative
commission/friction/borrow/funding are already embedded in cash, not subtracted again.
Terminal net = raw signed price P&L + signed actions - commission - modeled print
concession - impact - physical-net borrow - funding. This bridge is an orthogonal
attribution, not a second charge or frictionless rerun. Full original Decimal
components, cash/claims, terminal positions/orders and archived registry hash are
in ACCOUNT_BINDINGS.json. All terminal stock and pending-order counts are zero;
any signed terminal claim is retained at the executed approved valuation.

RTH gross integral = sum over received RTH intervals of absolute filled VIRTUAL lot
marked value times minutes (plus special assets), not physical netted gross. Dollar-
years = summed gross_dollar_minutes/(252*390), using actual 210-minute half days in
the numerator. Canonical mean gross/NAV = summed gross_NAV_minutes/summed RTH_minutes.
Daily RTH means weight intraday intervals; their median is an equal-session median.
Closing physical_value/NAV is SIGNED net inventory; it cannot identify gross or
separate long/short marked risk. Closing virtual_gross includes pending reservations;
it must not be substituted for the filled-lot integral. Counts of sessions with any
RTH exposure are identifiable; exact fraction of invested minutes is not saved.

Cash minus restricted proceeds, before other reservations, is the archived cash
proxy. It is neither full spendable buying power nor a precise idle-cash fraction.
Closing timestamps use metadata-only XNYS schedule, not reconstructed quote/mark
receipt times. No price panels or post-2024 market observations are read. Overnight
risk and ACT/365 borrowing use a different clock from RTH exposure and are not
silently included in RTH dollar-years.

Executed side notional = sum(abs(external shares)*executed price), including entries,
exits and special-asset external transactions once each. Both-side total is NOT
multiplied by two. Half that total is a labeled arithmetic roundtrip-equivalent,
not an independently observed matched ticket measure. Turnover = side notional /
mean end-session NAV. Cost/notional bps = cost/side notional*10000; net/gross-exposure-
year = net*1M/gross-dollar-years. Expense/edge = total cost/(raw price+action edge),
with negative denominators retained and interpreted as no positive edge to finance
costs. Per-trade cost summaries are by distinct physical order ID, grouping partials;
virtual cohorts and external orders differ. Retail $1 incidence uses cumulative
commission per physical order; MICRO_PRO has no floor and the floor field is N/A.
No regulatory pass-through or true NBBO/locate inference is made.

Gross/net cohort winner and loser units are the saved closed virtual cohort with
its engine-allocated execution cost, action, borrow and funding. `cost` already
includes `fees`; adding them would double charge commissions. Cohort lifetime net
and gross aggregates reconcile to full accounts. Holding span is first fill to final
exit, not a share-weighted duration for partials. Overnight means the cohort spans
ET sessions; it does not allocate an exact overnight-versus-RTH dollar P&L. Cohort
entry/exit-year sums are NOT calendar-year NAV P&L. Stock, side, slot and cause views
are alternative projections and cannot be added. A physical order serving multiple
cohorts cannot be counted independently in each virtual projection. Unsupported
per-stratum physical order counts or marked exposure remain unavailable.

## Paired descriptors and missing fields

S2C versus each control is paired on all 1005 session dates. Improved P&L/Sharpe/Sortino
is S2C minus control; volatility/DD-loss/ES/cost improvement is control minus S2C.
Exposure/order differences are descriptive, without a preference. Dollar differences
use actual NAV changes; a sum of simple return differences is never called dollars.
Eligibility is matched input readiness, not matched funded holdings. Entry keys are
(original UTC origin, ticker, direction) within the sealed case; state feedback can
change entry quantity, acceptance and exits. Cause attribution to rounding versus
particular reservations is not reconstructed when the snapshots are absent.

Paired tails use a fixed 51/11 worst or 51 best CONTROL-return dates and compare S2C
on those same dates, including its contemporaneous RTH exposure. These are hindsight
strata only and cannot select trades. Fixed exposure bins are ZERO, (0,5%], (5,10%],
(10,20%], (20,40%], (40,100%], >100%, preserving all sessions; conditioning is endogenous.
No return-dependent data exclusion, new alpha ranking or subsequent funded run occurs.

NONEXECUTABLE normalization: k = control realized mean gross / S2C realized mean
gross, or control realized annual volatility / S2C annual volatility; proxy daily
return = k*r_S2C (already net). Both are constant, retrospective whole-sample ratios.
They do not rebudget holdings, cash, borrowing, costs, market impact or constraints.
Refuse tiny denominator (<1e-6 gross or <1e-12 vol), k<=0, k>10 or any 1+k*r<=0.
These are accounting descriptors, never funded strategy results or forecasts.

Each channel is separately SUPPORTED_EXPLORATORY if full-period improvement and all
four defined annual improvements are nonnegative; conflicting evidence is MIXED;
nonpositive without an improving year is NO_EVIDENCE; absent is NOT_IDENTIFIABLE.
No composite score, new winner selection or inferential significance is calculated.
Four annual and 48 monthly paired summaries are supplied; optional moving-block
bootstrap was NOT_RUN. Dependence, repeated selection and eleven-point ES99 limit
claims, independently of any hypothetical confidence interval.

NOT_IDENTIFIABLE_FROM_SAVED_OUTPUTS applies to per-stock marked exposure, physical
gross/long-short exposure, cap utilization, minute-exact invested time, complete
action ex/pay/day-P&L postings, exact mark receipt timestamps, per-order cohort links
and buying power after all pending reservations. Minimal saved fields needed are
listed in CONCENTRATION_AND_ECONOMIC_LIMITATIONS.md. No missing value is fabricated
as zero; aggregate accounts still reconcile. Historical/ATTAINABLE figures are not
primary matched comparisons. Stage 6 and untouched/prospective confirmation remain
separate; this diagnostic changes no research strategy, forecast or trading path.
