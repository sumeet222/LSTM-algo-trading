# Original frozen S2-C entry-sizing diagnostics

Completed12 MATCHED accounts and9 ATTAINABLE non-EQUAL accounts; reused the three
exact original ATTAINABLE EQUAL accounts. All24 economic views reconcile. No neural
fit, recalibration, auxiliary sign, new inference or dynamic LSTM resizing occurred.

## Primary: matched common causal opportunities

| Policy | EQUAL net USD | ROLLING net USD | EWMA net USD | S2-C net USD | S2-C−EQUAL |
|---|---:|---:|---:|---:|---:|
| R01-A | -8,981.08 | -7,968.61 | -7,703.25 | -8,276.07 | +705.02 |
| R07-PERSIST | 1,895.02 | 2,984.09 | 2,318.84 | 3,111.78 | +1,216.76 |
| M04-T480 | 2,606.13 | 1,718.00 | -2,567.51 | -2,036.51 | -4,642.64 |

**R01-A:** S2-C improves net by$705.02 and net per gross-dollar-year versus EQUAL,
but remains a loss of$8,276.07, below rolling(-$7,968.61) and EWMA(-$7,703.25) in net
USD. Its drawdown worsens versus EQUAL (about-12.49% vs-11.51%); costs rise from
$5,551.24 to$5,817.03. Annual return improves versus EQUAL only in2021; it worsens
in2022–24. This does not rescue a positive directional edge on the matched base.

**M04-T480:** S2-C worsens net by$4,642.64 versus EQUAL and also loses to rolling.
It beats the negative EWMA account modestly, which does not make it successful.
Gross price falls$11,145.11→$6,114.93; costs decline only$84.45. Turnover is similar
($24.29M→$24.09M). A forecast of unsigned240-minute movement is not a guarantee
of useful sizing for a480-minute directional hold. No horizon or cost was retuned.

**R07-PERSIST:** S2-C improves net by$1,216.76 versus EQUAL, $127.68 versus rolling
and$792.93 versus EWMA. Its mean marked RTH gross/NAV is1.60%, only60 funded matched
cohorts. All four arms enter the same60 keys, but S2-C/EQUAL differ in25 exit times
and41 entry notionals because allocation changes marked risk/capital feedback.
S2-C has26 risk-closed cohorts versus EQUAL23 and rolling28. Improvement is not
simply fewer risk exits or higher leverage. Rolling and S2-C Sharpe are approximately
.598 and.602, a tiny descriptive difference. S2-C beats rolling in annual return
only in2022 and lags it in the other three years. No independent significance.

Matched R07 S2-C is concentrated in TSLA/AMD: arithmetic removal leaves+$41.08;
rolling leaves+$697.10 after its own top two. This small positive residue is not
robust-alpha certification. R01 and M04 matched S2-C remain negative even before
name omission. Keep all selected policies, including failures; no reselection occurred.

The small R07 advantage over rolling is particularly fragile: S2-C raw-price
gross is$21.80 lower, signed action value$153.98 higher and costs about$4.50 higher.
The$127.68 net gain therefore depends on action/holding allocation, not improved
raw trading P&L. S2C_INCREMENTAL_PNL_COMPONENTS.csv reconciles every contrast.
See S2C_R07_ACTION_MARGIN_QUALIFICATION.md. No action assumptions were changed.

Targets normalize by sum(g): a common scaling cancels, and a one-name basket
has the same preliminary target regardless of g. Mean g below1 is not evidence
of lower deployed risk. Actual marked exposure and normalized net are reported.
Entry g/cap distributions are in ENTRY_RISK_FACTOR_DIAGNOSTICS.csv; source counts
with explicit fold/rank support are S2C_SOURCE_COVERAGE_BY_FOLD.csv.

## Common source base versus funded paths

The primary source-ready sets are identical across four arms per policy:
R01-A537/824 calendar-admissible alpha keys; M04-T4803426/4985; R07-PERSIST61/96.
The raw R01 total832 also includes8 calendar-only terminal cutoffs. Source eligibility
never depends on the future240 endpoint or F09 labels. Classical controls require
strictly matured prior moves; original forecasts require original own-stock input
eligibility and receipt before the decision. All ranking/entry alpha is unchanged;
no tail ranks are recomputed to replace missing-risk names.

EQUAL matched is deliberately not the original full opportunity account. R01's
+$10,488 parent becomes-$8,981 matched EQUAL: availability and capital paths matter
substantially. It is invalid to call that difference an S2-C sizing effect. Among
matched R01 S2-C/EQUAL,306 keys enter in both,26 only EQUAL and37 only S2-C;110 common
exits differ. Matched M04 has1466 shared entries,133 only EQUAL,144 only S2-C and989
changed common exit times. Entry multipliers were frozen; old holdings were never
resized. The daily NAV contrasts pair account-days, not independent identical trades.

## Secondary: attainable samples (nonpaired opportunities)

See FOUR_ARM_S2C_SIZING_RESULTS.csv and S2C_MATCHED_VS_ATTAINABLE.csv. Parent EQUAL
accounts are exact archived reuses. S2-C attainable net is R01-A-$363.41,
M04-T480-$875.61, R07-PERSIST+$3,584.07. Different own-ready sets prevent attributing
these differences against full EQUAL exclusively to sizing. R01 has770 S2-C-ready
keys versus824 EQUAL; M04 has4558 versus4985; R07 has87 versus96. Classical own
sets are545,3484 and63, respectively. Do not silently substitute these for the
primary matched results or choose the more flattering population.

## Forecast and economics contract

Original four C-A/O1/FT16(48x16)/10CLOCK/C3 annual models (6572 parameters) remain
hash-identical. Exactly131111 original input-eligible forecasts were reused;
none recomputed. Original2019 fold/ticker/slot b and m_floor produce
clip(b/max(scale,m_floor),.5,1.5). Targets normalize by sum of ready g before
original caps and rounding, no redistribution. Rolling is median of last60
scheduled same-slot matured absolute moves, min40 and original strict missing
window. EWMA is RMS lambda.94 with first-square initialization on that same window.
The legacy five-day alpha mask is ignored, yielding90428 classical-ready rows.
The sign comes only from the frozen directional policy, never the magnitude model.

R01/R07 may hold ten sessions; M04 plans480 minutes. S2-C targets nominal origin
to240-scheduled-minute absolute log return. It is a short-term entry-risk proxy,
not the signed trade return, ten-session variance or a validated full-hold risk.
Actual fills use later raw openings, source receipt and original next-valid policy.
No later magnitude resizes a cohort; native dynamic or fixed exit policy remains.

All modes retain their original costs, signed dividends/splits/OGN and2% ACT365
physical-net-short borrow, funding0, collateral/caps and order-level fees. Raw
price gross is before modeled concession; physical cash already embeds fill
concession/commission. Absolute arrival movement is not charged as a second fee.
No measured NBBO or historical locate is asserted. Source/action vintages remain
retrospective/conditional. All terminal stock positions/orders/claims are zero in
these particular result rows, with no unsupported price or post2024 equity read.

Posthoc magnitude-decile diagnostics concern nominal240-minute source movement,
not actual multiday payoff. Bins use forecasts, with future-label censoring shown;
they were constructed only after funding and never used as eligibility. No risk
shuffle/null was run: no approved sign-independent module was identified. Formal
clustered/bootstrap/null inference and independent financial audit remain Stage6.

The combined conclusions are mixed and selected on reused2021–24. Neither the
R07 result nor the score ranking supplies prospective validation or deployment evidence.

