# Three policies at native portfolio risk

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

All accounts are separate $100k books, continuous across 2021–24. Their USD results
must not be summed into a fund. R01 uses weekly six-minus-one-month cross-sectional
momentum and dynamic exits; M04 uses confirmed gap continuation with a fixed nominal
480 scheduled-minute exit; R07 uses weekly compression breakout with two daily failure
checks and dynamic exits. Parent entry/exit/cost policies are unchanged by this task.

Risk sizing changes exposure, integer rounding, filled opportunities, constraints and
later exits, so matched input eligibility is not identical holdings. Funded opportunity
joins show R01 S2C/EQUAL shared 306, equal-only 26 and S2C-only 37; M04 shared 1,466,
equal-only 133 and S2C-only 144. R07 has the same 60 funded opportunity keys in every
arm, yet 25 of its S2C/EQUAL shared final exit times differ. Exact dollar allocation of
rounding versus risk reservations is not identifiable without the original reservation
snapshots, and is not reconstructed here.

The small R07 account has about 1.6–1.7% mean RTH gross exposure and 60 closed cohorts
per arm. Exposure-normalized dollar ratios can therefore look large; they are not
leveraged portfolio returns. R01 is negative in all four arms; M04's mode-specific
hypothetical micro costs differ from conservative retail and are not a fair cost switch.

See WHAT_DID_S2C_IMPROVE.md for nine dimension-by-dimension comparisons, plus paired
tail dates, annual/monthly differences, drawdown intervals and normalization CSVs.
