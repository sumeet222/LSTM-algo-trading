# P2.2A-R1 synthetic trace examples

| Trace (ET, ordinary2020-07-01) | Expected behavior |
|---|---|
| Origin1 CLOSE100 at10:30→CLOSE102 at14:30 | proxy log return ln(1.02)=0.019802627297; scheduled10:33→14:33;lag180s;label not mature at14:30, no earlier than14:33. |
| Origin2 CLOSE200 at11:30→CLOSE198 at15:30 | ln(.99)=−0.010050335854;scheduled11:33→15:33; source period ends11:30/15:30, no16:00 stub. |
| Five synthetic ratios .98,.99,1,1.01,1.03 | median logs0;unscaled MAD=−ln(.99)=.010050335854;training epsilon=.0010050335854;scores=log(ratio)/(.0110553694394). This is synthetic single-origin arithmetic, not production fit adequacy. |
| Actual issue10:35 | cutoff10:30 unchanged, entry10:36,exit14:36,source ends10:30/14:30;lag360s;label maturity≥14:36. |
| Exit published14:40 | at14:33 LABEL_NOT_MATURED;later label maturity14:40 if all facts supported. Reference valid_at_event=False at14:33;execution_outcome remains NOT_EVALUATED even if later label valid. |
| Missing final-name exit / next-hour candidate | label invalid; original causal entry flags identical to complete-exit history. No nearest/shifted row, trade removal or liquidation fabricated. |
| Boundary14:31 vs hourly end14:30 | label with14:33 scheduled maturity purged. Boundary14:35 vs late publication14:40 also purged. Original frozen splits preserved; synthetic boundary only tests rule. |
| Synthetic2:1 split10:31, raw entry100 at10:30 / raw exit51 at14:30 | reference-basis exit102;log1.02. Scope beginning10:33 cannot certify the price interval and is rejected. No dividends or cashbook change. |
| Minute sample/floor passed to proxy wrapper | ValueError version/lineage required. Distinct source rows/versions, proxy keys and hash-bound floor; no relabeled old M2/scalers. |

All observations, publication facts, action facts and forecast evidence here are explicitly SYNTHETIC. Source availability at completion is a fixture assumption, not a provider fact. No acquired/confirmation prices read to build these examples. Tests in tests/test_hourly_proxy.py and unchanged tests/test_labels.py provide independent numeric expectations and the counterfactual. Full FT0/policy/risk/maturity coverage on real sources remains unverified.
