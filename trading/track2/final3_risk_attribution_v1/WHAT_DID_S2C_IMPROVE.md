# What did S2-C improve?

Status: PARTIAL_WITH_EXPLICIT_MISSING_FIELDS. All 12 saved matched books and all nine
comparisons are analyzed; unavailable exposure/mark/action fields are listed below.
No new portfolio, market-price extraction, neural inference or strategy selection ran.

| Policy | Arm | Net USD | Sharpe | Sortino | Vol/yr | Max DD loss | ES95/day loss | Mean RTH gross |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M04-T480 | EQUAL | +2,606.13 | 0.232 | 0.365 | 2.977% | 6.160% | 0.407% | 7.826% |
| M04-T480 | ROLLING_RISK | +1,718.00 | 0.161 | 0.245 | 2.908% | 7.271% | 0.429% | 7.879% |
| M04-T480 | EWMA_RISK | -2,567.51 | -0.213 | -0.320 | 2.865% | 7.234% | 0.414% | 7.736% |
| M04-T480 | S2C_RISK | -2,036.51 | -0.162 | -0.246 | 2.917% | 7.264% | 0.423% | 7.948% |
| R01-A | EQUAL | -8,981.08 | -0.654 | -0.889 | 3.514% | 11.508% | 0.557% | 11.819% |
| R01-A | ROLLING_RISK | -7,968.61 | -0.613 | -0.836 | 3.309% | 10.927% | 0.535% | 10.879% |
| R01-A | EWMA_RISK | -7,703.25 | -0.582 | -0.786 | 3.357% | 10.820% | 0.539% | 11.456% |
| R01-A | S2C_RISK | -8,276.07 | -0.605 | -0.808 | 3.480% | 12.493% | 0.576% | 11.283% |
| R07-PERSIST | EQUAL | +1,895.02 | 0.389 | 0.586 | 1.230% | 2.261% | 0.182% | 1.732% |
| R07-PERSIST | ROLLING_RISK | +2,984.09 | 0.598 | 0.947 | 1.246% | 2.100% | 0.170% | 1.608% |
| R07-PERSIST | EWMA_RISK | +2,318.84 | 0.452 | 0.696 | 1.289% | 2.168% | 0.188% | 1.630% |
| R07-PERSIST | S2C_RISK | +3,111.78 | 0.602 | 0.977 | 1.290% | 2.088% | 0.173% | 1.597% |

Each pair cell below is S2C/control. Δ+ is the improvement-oriented difference:
higher net/Sharpe/Sortino/efficiency is better; lower volatility, DD loss, ES or cost is
better. Exposure and order counts are descriptive, not a preference. Values are
rounded only here; CSV retains full float precision and exact terminal Decimal strings.

| Policy | Control | Net USD | Sharpe | Sortino | Vol %/yr | DD loss % | ES95 loss % | Net/1M gross-yr | Gross % | Cost USD | Orders |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R01-A | EQUAL | -8276.066/-8981.084; Δ+ +705.019 | -0.605/-0.654; Δ+ +0.049 | -0.808/-0.889; Δ+ +0.080 | 3.480/3.514; Δ+ +0.034 | 12.493/11.508; Δ+ -0.984 | 0.576/0.557; Δ+ -0.020 | -191039.270/-202340.349; Δ+ +11301.080 | 11.283/11.819; descriptive | 5817.033/5551.237; Δ+ -265.795 | 701.000/675.000; descriptive |
| R01-A | ROLLING_RISK | -8276.066/-7968.607; Δ+ -307.458 | -0.605/-0.613; Δ+ +0.008 | -0.808/-0.836; Δ+ +0.028 | 3.480/3.309; Δ+ -0.170 | 12.493/10.927; Δ+ -1.566 | 0.576/0.535; Δ+ -0.041 | -191039.270/-191765.684; Δ+ +726.415 | 11.283/10.879; descriptive | 5817.033/5781.669; Δ+ -35.363 | 701.000/706.000; descriptive |
| R01-A | EWMA_RISK | -8276.066/-7703.253; Δ+ -572.813 | -0.605/-0.582; Δ+ -0.023 | -0.808/-0.786; Δ+ -0.023 | 3.480/3.357; Δ+ -0.123 | 12.493/10.820; Δ+ -1.673 | 0.576/0.539; Δ+ -0.038 | -191039.270/-175778.494; Δ+ -15260.776 | 11.283/11.456; descriptive | 5817.033/5663.940; Δ+ -153.093 | 701.000/681.000; descriptive |
| M04-T480 | EQUAL | -2036.514/2606.125; Δ+ -4642.639 | -0.162/0.232; Δ+ -0.394 | -0.246/0.365; Δ+ -0.611 | 2.917/2.977; Δ+ +0.060 | 7.264/6.160; Δ+ -1.104 | 0.423/0.407; Δ+ -0.015 | -65147.366/84842.952; Δ+ -149990.318 | 7.948/7.826; descriptive | 8385.417/8469.867; Δ+ +84.450 | 3373.000/3363.000; descriptive |
| M04-T480 | ROLLING_RISK | -2036.514/1717.999; Δ+ -3754.513 | -0.162/0.161; Δ+ -0.324 | -0.246/0.245; Δ+ -0.491 | 2.917/2.908; Δ+ -0.009 | 7.264/7.271; Δ+ +0.007 | 0.423/0.429; Δ+ +0.006 | -65147.366/55135.282; Δ+ -120282.649 | 7.948/7.879; descriptive | 8385.417/8444.892; Δ+ +59.475 | 3373.000/3393.000; descriptive |
| M04-T480 | EWMA_RISK | -2036.514/-2567.513; Δ+ +530.999 | -0.162/-0.213; Δ+ +0.051 | -0.246/-0.320; Δ+ +0.074 | 2.917/2.865; Δ+ -0.052 | 7.264/7.234; Δ+ -0.030 | 0.423/0.414; Δ+ -0.009 | -65147.366/-85294.421; Δ+ +20147.055 | 7.948/7.736; descriptive | 8385.417/8349.436; Δ+ -35.980 | 3373.000/3374.000; descriptive |
| R07-PERSIST | EQUAL | 3111.776/1895.016; Δ+ +1216.761 | 0.602/0.389; Δ+ +0.213 | 0.977/0.586; Δ+ +0.392 | 1.290/1.230; Δ+ -0.060 | 2.088/2.261; Δ+ +0.172 | 0.173/0.182; Δ+ +0.009 | 481892.430/272993.417; Δ+ +208899.012 | 1.597/1.732; descriptive | 1222.069/1217.364; Δ+ -4.704 | 125.000/123.000; descriptive |
| R07-PERSIST | ROLLING_RISK | 3111.776/2984.092; Δ+ +127.685 | 0.602/0.598; Δ+ +0.004 | 0.977/0.947; Δ+ +0.031 | 1.290/1.246; Δ+ -0.044 | 2.088/2.100; Δ+ +0.012 | 0.173/0.170; Δ+ -0.003 | 481892.430/459442.700; Δ+ +22449.730 | 1.597/1.608; descriptive | 1222.069/1217.573; Δ+ -4.495 | 125.000/122.000; descriptive |
| R07-PERSIST | EWMA_RISK | 3111.776/2318.844; Δ+ +792.933 | 0.602/0.452; Δ+ +0.150 | 0.977/0.696; Δ+ +0.281 | 1.290/1.289; Δ+ -0.001 | 2.088/2.168; Δ+ +0.080 | 0.173/0.188; Δ+ +0.015 | 481892.430/353552.569; Δ+ +128339.860 | 1.597/1.630; descriptive | 1222.069/1218.726; Δ+ -3.342 | 125.000/122.000; descriptive |

**R01-A: MIXED versus EQUAL, no general risk improvement.** S2C loses $705.02 less and
improves Sharpe/Sortino versus EQUAL, with 4.53% less mean RTH gross exposure. Its
max DD worsens from 11.51% to 12.49%; ES95 worsens, while ES99 improves marginally.
It loses more than rolling ($307.46) and EWMA ($572.81), with higher native volatility,
worse DD and ES95 than either. Exposure efficiency improves versus equal and only
slightly versus rolling, but not EWMA. Costs rise versus all controls. It improves
annual returns versus EQUAL in 2021 only. Net losses in all arms preclude an alpha claim.

**M04-T480: NO UNIVERSAL BENEFIT; MIXED only versus EWMA.** S2C turns the positive
EQUAL/rolling outcomes into a $2,036.51 loss, and worsens Sharpe/Sortino versus both.
Volatility falls slightly versus EQUAL/rolling, but DD and ES95 worsen versus EQUAL.
Versus rolling DD improves by only 0.0068 percentage points and ES95 improves, while
ES99 worsens. Versus EWMA, net improves $531.00 but volatility, DD, ES95 and ES99
worsen. S2C has more mean gross exposure than every control, so its losses are not
explained by simply investing less. Lower costs versus equal/rolling do not rescue it.

**R07-PERSIST: MIXED, encouraging mean/efficiency but weak risk dominance.** S2C has
the best native net, Sharpe, Sortino and DD, with lower mean exposure than all controls,
but native volatility is higher than all three. ES95 improves versus equal/EWMA but
worsens versus rolling; ES99 improves versus EWMA but worsens versus equal/rolling.
Versus rolling the $127.68 gain decomposes into $21.80 less price P&L, $153.98 more
signed action value and $4.50 more costs. It wins annual return versus rolling in
2022 only. After arithmetic omission of its top two profitable stocks (TSLA/AMD),
S2C net is just $41.08; rolling's own-top-two omission leaves $697.10. These are
separate descriptive omissions, not funded portfolios or matched subsets.

**Lower exposure is an incomplete explanation.** On each control's worst 5% dates,
S2C's paired mean return is better in all nine comparisons; it is worse on each
control's best 5% dates. These are retrospective control-selected dates, not an
implementable hedge. On rolling R07's worst 1%, S2C is worse. Native marginal ES
differences must not be interpreted as conditional protection. Constant mean-exposure
scaling of S2C already-net daily returns is explicitly NONEXECUTABLE: R07 at EQUAL
exposure has DD 2.264% versus EQUAL 2.261%, and ES95 0.1874% versus 0.1822%; at
rolling exposure its DD is 2.103% versus 2.101%, and ES95 0.1740% versus 0.1700%.
Thus its native drawdown advantage is largely associated with lower exposure in
those comparisons. Mean-exposure and native-volatility normalizers are reported
separately, without changing orders/fees or claiming feasible scaled performance.

Channels are independently labeled in `runs/analysis_01/CHANNEL_ASSESSMENTS.csv`; no composite
score or new winner selection is used. Full-period improvements conflicting with
annual evidence are MIXED. Four annual and 48 monthly paired descriptors replace
inferential claims; no optional bootstrap or Stage 6 audit was run.

These repeatedly inspected 2021–24 fixed-survivor results are exploratory. Original
S2-C predicts 240-scheduled-minute endpoint absolute movement, not direction,
conditional variance, or full multiday-hold risk. Unmeasured NBBO/locates, assumed
receipt and retrospective action/QA vintages remain material limitations.
