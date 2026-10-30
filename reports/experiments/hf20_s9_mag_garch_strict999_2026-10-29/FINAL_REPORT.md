# HF20 S9-MAG GARCH11-STRICT999 — final report

**COMPLETE.** All 560 uniformly constrained Gaussian GARCH fits passed, including the three former COP boundaries. Both prespecified common calibrators completed on the independent preceding Oct–Dec roles. This is a valid complete-panel benchmark on 80,260 stock-origin keys; the old unconstrained panel remains PARTIAL_BLOCKED and the older dependency block remains BLOCKED_DEPENDENCY.

The constrained GARCH **does not close the matched-calibration LSTM advantage**. Against S2-C, equal-year MSE is 3.7736% worse under G and 4.1538% worse under IO, with higher loss in all four years. IC is 0.307433340 versus S5-C 0.332045935, lower in all four years. The paired descriptive intervals retain these directions. HAR remains the strongest classical magnitude comparator and ROLL60 the strongest classical ranking comparator in this fixed grid; neither catches the corresponding strongest neural equal-year benchmark in any of the four folds. This is evidence beyond these baseline implementations, not proof that recurrence is necessary.

Raw GARCH has1.6646% lower headline MSE than raw S2-C (wins3/4 years), but its descriptive interval includes zero and the matched-calibration comparison reverses the sign. Native C3 packages remain a separate comparison. No calibrator, cap, model or deployment rule was selected from these outcomes.

## Task, preservation and interpretation

A=|log(P_exit/P_origin)| at the genuine endpoint after 240 scheduled XNYS minutes. It is endpoint magnitude, not integrated realized volatility or path variation. Evaluation is 2021–2024,19,100/23,600/17,740/19,820 rows,4,013 origins,793 sessions,20 stocks/origin. Original equal-stock/origin/session/year reducers, ties, category normalization and constant-score conventions are unchanged. EQ rows require all four years; conditional group losses normalize original weights within group. Ratios are predicted/observed equal-year means. MSE units are squared log return; MAE, mean and bias are log return.

The nominal origin precedes the historical approximate origin+2-minute publication proxy. Actual vendor arrival was not measured; this is not post-issuance executable P&L. Same-source revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56, retrospective adjustments, quarantine and survivor universe remain frozen. No raw minutes, market downloads,2025 values or protected2026 material were accessed.3,296 exact predecessor bindings were checked, including original roles, scores, contracts, both earlier GARCH failures, journal history and package records. Live neural ledger remains186/300; no neural starts, inference or refits.

The feature inputs differ: neural models use frozen48-hour own-stock FT16 plus their authorized clock/objective variants; rolling/EWMA and GARCH refresh past-return histories; HAR uses archived historical full-session RV information. Common calibration equalizes postprocessing, not information sets or architecture. The shared-stock neural training also differs from stock-slot GARCH estimation.

## Uniform constraint, fit and causal replay

Public arch 8.0.0 GARCH.constraints was subclassed only to replace the persistence inequality with .999-alpha-beta>=0. The inherited Gaussian likelihood, variance recursion, bounds, deterministic starting values, backcast and SLSQP were unchanged: x=100R,rescale=False,maxiter1000,ftol/tol1e-9. No post-fit coefficient adjustment, alternative start, cap search or retry. All 560 exact original vectors were authenticated before fitting; sample sizes range 1526–2412. The same59 overlapping history origins were excluded by start>=last retained endpoint, equality permitted; no evaluation key was excluded.

All 560 convergence flags are0, all 560 admissibility gates pass, and no solver warnings occurred. All 65 old persistence>=.99 units remain in that descriptive cohort. There are13 cap contacts and 5 tiny signed overshoots; minimum slack-1.794120407794253e-13, maximum unrounded persistence0.99900000000017941. The predeclared feasibility tolerance is 1e-10; cap-contact tolerance1e-8. These overshoots are displayed explicitly, never rounded/clipped into compliance. All saved vectors exactly equal optimizer returns. The fixed normal log-likelihood was independently recomputed, and no conditional variance touched its numerical lower/soft upper bounds.

Maximum absolute alpha/beta change among the65 old near-unit units is 0.000765188306; among the495 others it is 4.43881414e-06. No unit exceeded the predeclared .01 large-change flag. Old numerical boundary contact does not establish nonstationary stock returns. All 560 coefficient deltas, optimizer flags, supports, initial states, bounds, iterations and likelihoods are saved, including the557 old passing fits; none was transplanted.

| year | ticker | slot | alpha_old | beta_old | alpha_new | beta_new | persistence_new | cap_slack | status_new |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | COP | 15:30 | 0.114964326 | 0.885035674 | 0.11442511 | 0.88457489 | 0.999 | 1.11022302e-16 | PASS |
| 2023 | COP | 13:30 | 0.12669858 | 0.87330142 | 0.125999396 | 0.873000604 | 0.999 | 1.11022302e-16 | PASS |
| 2024 | COP | 15:30 | 0.105447722 | 0.894552278 | 0.104826163 | 0.894173837 | 0.999 | -3.77475828e-15 | PASS |


Parameters remain frozen after the September restricted prefix. Every later update uses a signed return whose genuine endpoint+2-minute maturity is strictly before issue; state replay checked all 99,240 calibration/OOS forecasts and every consumed event. Representative09:30/15:30/early-close cases are in garch_maturity_cases.csv. The package recursion and independent replay agree, and saved raw score rows match traces exactly. No unfinished current/future target enters state.

This is a one-next-observation forecast of an irregular same-stock/same-slot four-hour-return process. Calendar spacing and intraday/overnight composition vary. It is not continuous-time four-hour integrated variance. The conditional-Gaussian folded-normal mean uses mu/100 and variance/10000, without a horizon multiplier. Normality is assumed, not demonstrated.

## Table I — identical common calibration families

Every old G/IO arm below is reused exactly; only new GARCH's four G fits and four two-category IO fits were estimated. G is the nonnegative weighted MSE-optimal multiplier. IO shrinks category multipliers using n_eff=1/sum(normalized category session mass²),rho=n_eff/(n_eff+25). No old C3 output is calibrated again. Zero denominators/support would have blocked the arm; none occurred.

| arm | raw_MSE | raw_MAE | predicted | observed | ratio | bias | IC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MATCH-CLOCK-G | 0.00010688204 | 0.00684636695 | 0.0108552133 | 0.0103132705 | 1.0525481 | 0.000541942778 | 0.330254043 |
| MATCH-CLOCK-IO | 0.000106525209 | 0.00682138638 | 0.0107955616 | 0.0103132705 | 1.04676413 | 0.000482291149 | 0.330254043 |
| MATCH-S2C-G | 0.000106847027 | 0.00684680351 | 0.0108734392 | 0.0103132705 | 1.05431533 | 0.000560168692 | 0.331235977 |
| MATCH-S2C-IO | 0.000106488179 | 0.00682198741 | 0.0108139775 | 0.0103132705 | 1.04854978 | 0.00050070697 | 0.331235977 |
| MATCH-S5C-G | 0.000107177324 | 0.00686344654 | 0.0108678275 | 0.0103132705 | 1.05377121 | 0.000554557032 | 0.332045935 |
| MATCH-S5C-IO | 0.000106809521 | 0.00683773833 | 0.0108078013 | 0.0103132705 | 1.04795092 | 0.000494530857 | 0.332045935 |
| MATCH-ROLL20-G | 0.000113630053 | 0.00690899177 | 0.00999959851 | 0.0103132705 | 0.969585596 | -0.000313671978 | 0.300049371 |
| MATCH-ROLL20-IO | 0.000113710746 | 0.00690962577 | 0.0099909788 | 0.0103132705 | 0.968749808 | -0.000322291687 | 0.300049371 |
| MATCH-ROLL60-G | 0.000112088653 | 0.00701626864 | 0.0108594993 | 0.0103132705 | 1.05296369 | 0.000546228826 | 0.318689978 |
| MATCH-ROLL60-IO | 0.000112121443 | 0.00701131292 | 0.0108360082 | 0.0103132705 | 1.05068593 | 0.000522737721 | 0.318689978 |
| MATCH-EXPANDING-G | 0.000113995917 | 0.00714192029 | 0.0109492444 | 0.0103132705 | 1.06166559 | 0.000635973891 | 0.308530147 |
| MATCH-EXPANDING-IO | 0.000113939771 | 0.00713306543 | 0.0109148852 | 0.0103132705 | 1.05833404 | 0.000601614704 | 0.308530147 |
| MATCH-EWMA-R2-FN-G | 0.000112376204 | 0.00691658942 | 0.0103004077 | 0.0103132705 | 0.998752794 | -1.28627694e-05 | 0.308712894 |
| MATCH-EWMA-R2-FN-IO | 0.00011241235 | 0.0069177482 | 0.0103013626 | 0.0103132705 | 0.998845382 | -1.19078923e-05 | 0.308712894 |
| MATCH-EWMA-A-G | 0.000110930418 | 0.00688985739 | 0.0103970541 | 0.0103132705 | 1.00812387 | 8.3783639e-05 | 0.314555338 |
| MATCH-EWMA-A-IO | 0.000110974097 | 0.00688749883 | 0.010378751 | 0.0103132705 | 1.00634916 | 6.54805574e-05 | 0.314555338 |
| MATCH-HAR-RV-A-G | 0.000109068194 | 0.0068339672 | 0.0104523513 | 0.0103132705 | 1.01348562 | 0.000139080838 | 0.31446518 |
| MATCH-HAR-RV-A-IO | 0.000109066473 | 0.00682951141 | 0.0104330587 | 0.0103132705 | 1.01161496 | 0.000119788186 | 0.31446518 |
| MATCH-GARCH11-STRICT999-G | 0.000110878967 | 0.00686002207 | 0.0102108016 | 0.0103132705 | 0.990064363 | -0.000102468914 | 0.30743334 |
| MATCH-GARCH11-STRICT999-IO | 0.000110911497 | 0.00686187733 | 0.0102120436 | 0.0103132705 | 0.990184788 | -0.000101226933 | 0.30743334 |


Paired GARCH-minus-reference differences within the same family; negative MSE/positive IC favors GARCH. Bounds are descriptive95% intervals,400 whole-calendar-month resamples within year,seed22042,equal-four-year aggregation. Whole overlapping sessions/stocks remain together. These repeatedly inspected years do not provide selection-adjusted confirmation.

| candidate | reference | delta_MSE | MSE_low | MSE_high | MSE_percent | delta_IC | IC_low | IC_high | MSE_win_folds | IC_win_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MATCH-GARCH11-STRICT999-G | MATCH-CLOCK-G | 3.99692743e-06 | 2.72620112e-06 | 5.61464623e-06 | 3.73956882 | -0.0228207031 | -0.027782278 | -0.0173495893 | 0 | 0 |
| MATCH-GARCH11-STRICT999-G | MATCH-S2C-G | 4.03193986e-06 | 2.81063919e-06 | 5.55439042e-06 | 3.77356297 | -0.0238026367 | -0.028985958 | -0.0184606396 | 0 | 0 |
| MATCH-GARCH11-STRICT999-G | MATCH-S5C-G | 3.70164273e-06 | 2.43939572e-06 | 5.30791218e-06 | 3.45375549 | -0.0246125946 | -0.0290519547 | -0.0196132101 | 0 | 0 |
| MATCH-GARCH11-STRICT999-G | MATCH-ROLL20-G | -2.75108592e-06 | -3.52524849e-06 | -2.00696751e-06 | -2.42109006 | 0.0073839696 | 0.00356612444 | 0.0114336251 | 4 | 3 |
| MATCH-GARCH11-STRICT999-G | MATCH-ROLL60-G | -1.20968553e-06 | -3.7493889e-06 | 8.88982352e-07 | -1.07922211 | -0.0112566379 | -0.0153414576 | -0.00693168582 | 2 | 0 |
| MATCH-GARCH11-STRICT999-G | MATCH-EXPANDING-G | -3.11694972e-06 | -4.81301165e-06 | -1.24822968e-06 | -2.73426435 | -0.00109680692 | -0.00710441983 | 0.00473176107 | 3 | 3 |
| MATCH-GARCH11-STRICT999-G | MATCH-EWMA-R2-FN-G | -1.49723692e-06 | -2.26907549e-06 | -7.48804211e-07 | -1.33234339 | -0.00127955334 | -0.0049476815 | 0.00259918068 | 4 | 3 |
| MATCH-GARCH11-STRICT999-G | MATCH-EWMA-A-G | -5.14508978e-08 | -8.55079106e-07 | 7.37393666e-07 | -0.0463812349 | -0.0071219981 | -0.0100881948 | -0.00397727073 | 2 | 0 |
| MATCH-GARCH11-STRICT999-G | MATCH-HAR-RV-A-G | 1.81077357e-06 | 1.68642383e-07 | 3.255428e-06 | 1.66022147 | -0.0070318395 | -0.0136119206 | 0.000121385486 | 1 | 0 |
| MATCH-GARCH11-STRICT999-IO | MATCH-CLOCK-IO | 4.38628806e-06 | 3.14687963e-06 | 5.99958044e-06 | 4.11760568 | -0.0228207031 | -0.027782278 | -0.0173495893 | 0 | 0 |
| MATCH-GARCH11-STRICT999-IO | MATCH-S2C-IO | 4.42331822e-06 | 3.229444e-06 | 5.98278446e-06 | 4.1538115 | -0.0238026367 | -0.028985958 | -0.0184606396 | 0 | 0 |
| MATCH-GARCH11-STRICT999-IO | MATCH-S5C-IO | 4.10197631e-06 | 2.83919334e-06 | 5.77360927e-06 | 3.84045943 | -0.0246125946 | -0.0290519547 | -0.0196132101 | 0 | 0 |
| MATCH-GARCH11-STRICT999-IO | MATCH-ROLL20-IO | -2.79924918e-06 | -3.62034703e-06 | -2.02229411e-06 | -2.46172792 | 0.0073839696 | 0.00356612444 | 0.0114336251 | 4 | 3 |
| MATCH-GARCH11-STRICT999-IO | MATCH-ROLL60-IO | -1.20994564e-06 | -3.76129063e-06 | 8.57943285e-07 | -1.07913849 | -0.0112566379 | -0.0153414576 | -0.00693168582 | 2 | 0 |
| MATCH-GARCH11-STRICT999-IO | MATCH-EXPANDING-IO | -3.02827445e-06 | -4.7199918e-06 | -1.14949284e-06 | -2.65778526 | -0.00109680692 | -0.00710441983 | 0.00473176107 | 3 | 3 |
| MATCH-GARCH11-STRICT999-IO | MATCH-EWMA-R2-FN-IO | -1.50085303e-06 | -2.28417961e-06 | -7.43762237e-07 | -1.3351318 | -0.00127955334 | -0.0049476815 | 0.00259918068 | 4 | 3 |
| MATCH-GARCH11-STRICT999-IO | MATCH-EWMA-A-IO | -6.25996711e-08 | -8.90713173e-07 | 7.33511393e-07 | -0.056409264 | -0.0071219981 | -0.0100881948 | -0.00397727073 | 2 | 0 |
| MATCH-GARCH11-STRICT999-IO | MATCH-HAR-RV-A-IO | 1.84502368e-06 | 2.2171838e-07 | 3.28521813e-06 | 1.69165063 | -0.0070318395 | -0.0136119206 | 0.000121385486 | 1 | 0 |


The strongest classical same-calibrator MSE remains HAR:2.0788% above S2-C under G and 2.4212% under IO, losing all 4 annual folds. The strongest classical IC remains ROLL60=.318689978 versus S5-C=.332045935, losing all 4 folds. GARCH neither changes these frontier descriptions nor closes either gap. These are descriptions of the complete fixed grid, not a best-from-many deployment selection.

For GARCH alone, G→IO raises MSE by 3.252982e-8 (+.029338%; interval[1.469820e-8,5.097842e-8]). Both remain reported. Calibration changes no within-origin ranks: IC, pairs, top/bottom retrieval are invariant. There are zero changed-rank origins, zero GARCH zero-scalar exceptions, and no random tie jitter.

## Raw-estimator diagnostic

| arm | raw_MSE | raw_MAE | predicted | observed | ratio | bias | IC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CLOCK-UNCAL | 0.000114270289 | 0.0064808202 | 0.00801585134 | 0.0103132705 | 0.777236605 | -0.00229741915 | 0.330254043 |
| S2C-UNCAL | 0.000113984507 | 0.00647452061 | 0.00802712439 | 0.0103132705 | 0.778329667 | -0.0022861461 | 0.331235977 |
| S5C-UNCAL | 0.000113656777 | 0.00648673239 | 0.00816402139 | 0.0103132705 | 0.791603536 | -0.0021492491 | 0.332045935 |
| ROLL20-UNCAL | 0.000113585913 | 0.0069907645 | 0.0104586062 | 0.0103132705 | 1.0140921 | 0.000145335681 | 0.300049371 |
| ROLL60-UNCAL | 0.000110596247 | 0.00691932645 | 0.0105957029 | 0.0103132705 | 1.02738534 | 0.000282432386 | 0.318689978 |
| EXPANDING-UNCAL | 0.000113609684 | 0.00686572274 | 0.00978161053 | 0.0103132705 | 0.948448946 | -0.000531659961 | 0.308530147 |
| EWMA-R2-FN-UNCAL | 0.000112932141 | 0.00708476208 | 0.0110532902 | 0.0103132705 | 1.07175413 | 0.000740019713 | 0.308712894 |
| EWMA-A-UNCAL | 0.000110669442 | 0.00689739093 | 0.0104931293 | 0.0103132705 | 1.01743955 | 0.000179858817 | 0.314555338 |
| HAR-RV-A-UNCAL | 0.0001089622 | 0.00679582537 | 0.0102729277 | 0.0103132705 | 0.996088261 | -4.03428251e-05 | 0.31446518 |
| GARCH11-STRICT999-UNCAL | 0.000112087163 | 0.00708840738 | 0.0111103064 | 0.0103132705 | 1.07728256 | 0.000797035954 | 0.30743334 |


| candidate | reference | delta_MSE | MSE_low | MSE_high | MSE_percent | delta_IC | IC_low | IC_high | MSE_win_folds | IC_win_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GARCH11-STRICT999-UNCAL | CLOCK-UNCAL | -2.18312568e-06 | -4.43396799e-06 | 1.12256377e-07 | -1.91049283 | -0.0228207031 | -0.027782278 | -0.0173495893 | 3 | 0 |
| GARCH11-STRICT999-UNCAL | S2C-UNCAL | -1.89734312e-06 | -4.1790075e-06 | 4.00255603e-07 | -1.66456229 | -0.0238026367 | -0.028985958 | -0.0184606396 | 3 | 0 |
| GARCH11-STRICT999-UNCAL | S5C-UNCAL | -1.56961359e-06 | -3.81973677e-06 | 8.00109304e-07 | -1.38101188 | -0.0246125946 | -0.0290519547 | -0.0196132101 | 3 | 0 |


Raw neural inverse-transformed outputs underpredict average endpoint magnitude (S2-C ratio~.778); raw GARCH ratio~1.077. Their raw MSE ordering does not measure the ordering after a common calibration. Raw GARCH wins over raw S2-C in 2021–2023 and loses2024. Raw comparisons remain diagnostic and do not replace declared calibrated primaries.

## Table II — original archived forecasting packages

| arm | raw_MSE | raw_MAE | predicted | observed | ratio | bias | IC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CLOCK-C3 | 0.000106665946 | 0.00675709312 | 0.0104552101 | 0.0103132705 | 1.01376281 | 0.000141939595 | 0.330254043 |
| S2C-C3 | 0.000106548168 | 0.006756096 | 0.0104702471 | 0.0103132705 | 1.01522083 | 0.000156976572 | 0.331235977 |
| S5C-C3 | 0.000106849046 | 0.00677234848 | 0.0104821559 | 0.0103132705 | 1.01637554 | 0.000168885371 | 0.332045935 |
| ROLL20-CAL | 0.000113630053 | 0.00690899177 | 0.00999959851 | 0.0103132705 | 0.969585596 | -0.000313671978 | 0.300049371 |
| ROLL60-CAL | 0.000112088653 | 0.00701626864 | 0.0108594993 | 0.0103132705 | 1.05296369 | 0.000546228826 | 0.318689978 |
| EXPANDING-CAL | 0.000113995917 | 0.00714192029 | 0.0109492444 | 0.0103132705 | 1.06166559 | 0.000635973891 | 0.308530147 |
| EWMA-R2-FN-CAL | 0.000112376204 | 0.00691658942 | 0.0103004077 | 0.0103132705 | 0.998752794 | -1.28627694e-05 | 0.308712894 |
| EWMA-A-CAL | 0.000110930418 | 0.00688985739 | 0.0103970541 | 0.0103132705 | 1.00812387 | 8.3783639e-05 | 0.314555338 |
| HAR-RV-A-CAL | 0.000109068194 | 0.0068339672 | 0.0104523513 | 0.0103132705 | 1.01348562 | 0.000139080838 | 0.31446518 |
| MATCH-GARCH11-STRICT999-G | 0.000110878967 | 0.00686002207 | 0.0102108016 | 0.0103132705 | 0.990064363 | -0.000102468914 | 0.30743334 |
| MATCH-GARCH11-STRICT999-IO | 0.000110911497 | 0.00686187733 | 0.0102120436 | 0.0103132705 | 0.990184788 | -0.000101226933 | 0.30743334 |


| candidate | reference | delta_MSE | MSE_low | MSE_high | MSE_percent | delta_IC | IC_low | IC_high | MSE_win_folds | IC_win_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MATCH-GARCH11-STRICT999-G | CLOCK-C3 | 4.21302133e-06 | 2.94553546e-06 | 5.82830544e-06 | 3.94973419 | -0.0228207031 | -0.027782278 | -0.0173495893 | 0 | 0 |
| MATCH-GARCH11-STRICT999-G | S2C-C3 | 4.33079937e-06 | 3.12326511e-06 | 5.85481798e-06 | 4.06463993 | -0.0238026367 | -0.028985958 | -0.0184606396 | 0 | 0 |
| MATCH-GARCH11-STRICT999-G | S5C-C3 | 4.02992092e-06 | 2.66131526e-06 | 5.56954803e-06 | 3.77160214 | -0.0246125946 | -0.0290519547 | -0.0196132101 | 0 | 0 |
| MATCH-GARCH11-STRICT999-IO | CLOCK-C3 | 4.24555115e-06 | 2.982271e-06 | 5.86402969e-06 | 3.9802311 | -0.0228207031 | -0.027782278 | -0.0173495893 | 0 | 0 |
| MATCH-GARCH11-STRICT999-IO | S2C-C3 | 4.36332919e-06 | 3.14820501e-06 | 5.89054223e-06 | 4.09517055 | -0.0238026367 | -0.028985958 | -0.0184606396 | 0 | 0 |
| MATCH-GARCH11-STRICT999-IO | S5C-C3 | 4.06245074e-06 | 2.68648648e-06 | 5.59828662e-06 | 3.80204679 | -0.0246125946 | -0.0290519547 | -0.0196132101 | 0 | 0 |


CLOCK-C3/S2C-C3/S5C-C3 retain their native transformed-M residual-smearing calibration with schedule shrinkage; historical classical CAL remains its original global multiplier. New GARCH-G/IO are labelled candidates, not native C3. GARCH-G has4.0646% higher overall MSE than native S2C-C3; GARCH-IO is 4.0952% higher. A native-C3 versus multiplier comparison combines raw estimation and calibration differences and cannot isolate network quality. The original GARCH panel has no lawful full-panel score; its 557 passing units are diagnostic only. The older BLOCKED_DEPENDENCY record is not an empirical loss.

## Ranking and simple-control context

| model | IC | pair_concordance | top4 | bottom4 | tie_rate | constant_rate | capture95 | false_low95 | capture99 | false_low99 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CLOCK | 0.330254043 | 0.619443313 | 0.429465854 | 0.303027563 | 0 | 0 | 0.553063739 | 0.169008167 | 0.675659521 | 0.126698684 |
| S2C | 0.331235977 | 0.61981899 | 0.429640727 | 0.30288517 | 0 | 0 | 0.553485907 | 0.164299711 | 0.666868686 | 0.127708649 |
| S5C | 0.332045935 | 0.620176276 | 0.427680982 | 0.30354245 | 0 | 0 | 0.549833739 | 0.163505765 | 0.67225612 | 0.116572666 |
| ROLL20 | 0.300049371 | 0.60822099 | 0.410966689 | 0.293769601 | 0 | 0 | 0.528224944 | 0.196426078 | 0.625148266 | 0.159231498 |
| ROLL60 | 0.318689978 | 0.615485578 | 0.421066847 | 0.302279479 | 0 | 0 | 0.541513878 | 0.186294768 | 0.642155642 | 0.168273088 |
| EXPANDING | 0.308530147 | 0.610654414 | 0.400034272 | 0.305845017 | 0 | 0 | 0.511110676 | 0.192686951 | 0.601311203 | 0.145743324 |
| EWMA-R2-FN | 0.308712894 | 0.611284688 | 0.414343868 | 0.300346358 | 0 | 0 | 0.531023055 | 0.190624127 | 0.625185774 | 0.166056052 |
| EWMA-A | 0.314555338 | 0.613562823 | 0.4208888 | 0.301989908 | 0 | 0 | 0.54718286 | 0.185061524 | 0.646438138 | 0.160751237 |
| HAR-RV-A | 0.31446518 | 0.613466332 | 0.407792743 | 0.30231017 | 1.56641604e-06 | 0 | 0.531404513 | 0.176753733 | 0.635103934 | 0.170624888 |
| GARCH11-STRICT999 | 0.30743334 | 0.610797068 | 0.410844886 | 0.299921097 | 0 | 0 | 0.527076714 | 0.195094332 | 0.641009973 | 0.142178322 |


The ten raw-family rows summarize rank-invariant G/IO variants. Existing neural native C3 rankings are also preserved. All tie, constant, undefined-IC, rank-spread and zero-forecast metrics for all 47 arms/scopes are in metrics.csv. Prefix95/99 events use the original lawful O1 prefix thresholds, not outer-year quantiles.

| arm | raw_MSE | raw_MAE | predicted | observed | ratio | bias | IC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C0 | 0.000114783568 | 0.00649744834 | 0.0080327552 | 0.0103132705 | 0.778875644 | -0.00228051529 | 0.324668102 |
| C3 | 0.000107226942 | 0.00680102945 | 0.0105885844 | 0.0103132705 | 1.02669511 | 0.00027531389 | 0.324668102 |
| C1a | 0.000108218653 | 0.00681593479 | 0.01050088 | 0.0103132705 | 1.01819108 | 0.000187609522 | 0.324668102 |
| M1 | 0.000108266399 | 0.00688398945 | 0.0108557659 | 0.0103132705 | 1.05260169 | 0.00054249545 | 0.324668102 |
| B0-VOL | 0.000111560421 | 0.0070127696 | 0.0106009017 | 0.0103132705 | 1.02788943 | 0.000287631193 | 0.304143161 |
| B0-CLOCK | 0.000114669543 | 0.00683908476 | 0.00950543971 | 0.0103132705 | 0.921670746 | -0.000807830783 | 0.302800204 |
| B0-RMEAN | 0.000122364417 | 0.00712961259 | 0.0095165809 | 0.0103132705 | 0.922751023 | -0.000796689594 | 0.300238273 |
| B0-RMED | 0.000138092163 | 0.00694960102 | 0.00647401598 | 0.0103132705 | 0.627736467 | -0.00383925451 | 0.296114434 |


## Annual results — complete fixed grid

| arm | MSE_2021 | IC_2021 | MSE_2022 | IC_2022 | MSE_2023 | IC_2023 | MSE_2024 | IC_2024 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MATCH-CLOCK-G | 8.25689972e-05 | 0.326276066 | 0.000146773489 | 0.354450911 | 8.60889716e-05 | 0.323804151 | 0.000112096701 | 0.316485046 |
| MATCH-CLOCK-IO | 8.20637003e-05 | 0.326276066 | 0.000146170891 | 0.354450911 | 8.59813354e-05 | 0.323804151 | 0.000111884909 | 0.316485046 |
| MATCH-S2C-G | 8.25953507e-05 | 0.327460711 | 0.000146922329 | 0.351764497 | 8.60556756e-05 | 0.326300734 | 0.000111814754 | 0.319417965 |
| MATCH-S2C-IO | 8.2104527e-05 | 0.327460711 | 0.00014627358 | 0.351764497 | 8.59067844e-05 | 0.326300734 | 0.000111667823 | 0.319417965 |
| MATCH-S5C-G | 8.32605592e-05 | 0.329436454 | 0.000146734277 | 0.354295639 | 8.60602898e-05 | 0.328670863 | 0.000112654172 | 0.315780783 |
| MATCH-S5C-IO | 8.27152361e-05 | 0.329436454 | 0.000146139521 | 0.354295639 | 8.59602828e-05 | 0.328670863 | 0.000112423043 | 0.315780783 |
| MATCH-ROLL20-G | 8.92065088e-05 | 0.305088668 | 0.000157691031 | 0.315386703 | 8.89880382e-05 | 0.294477085 | 0.000118634635 | 0.285245027 |
| MATCH-ROLL20-IO | 8.92400841e-05 | 0.305088668 | 0.000157691628 | 0.315386703 | 8.90032243e-05 | 0.294477085 | 0.000118908049 | 0.285245027 |
| MATCH-ROLL60-G | 8.69245315e-05 | 0.319192524 | 0.000159852984 | 0.329617223 | 8.67859161e-05 | 0.315863317 | 0.00011479118 | 0.310086848 |
| MATCH-ROLL60-IO | 8.6923263e-05 | 0.319192524 | 0.000159889828 | 0.329617223 | 8.67898154e-05 | 0.315863317 | 0.000114882864 | 0.310086848 |
| MATCH-EXPANDING-G | 9.11380406e-05 | 0.300266636 | 0.000157582462 | 0.324375251 | 9.27031328e-05 | 0.306324979 | 0.000114560032 | 0.303153722 |
| MATCH-EXPANDING-IO | 9.09989402e-05 | 0.300266636 | 0.000157478321 | 0.324375251 | 9.27469168e-05 | 0.306324979 | 0.000114534908 | 0.303153722 |
| MATCH-EWMA-R2-FN-G | 8.6737218e-05 | 0.313324714 | 0.000154948142 | 0.32541651 | 8.76355358e-05 | 0.306345565 | 0.000120183921 | 0.289764785 |
| MATCH-EWMA-R2-FN-IO | 8.67677835e-05 | 0.313324714 | 0.000154973872 | 0.32541651 | 8.76529765e-05 | 0.306345565 | 0.000120254769 | 0.289764785 |
| MATCH-EWMA-A-G | 8.62887697e-05 | 0.31665584 | 0.000154167127 | 0.330778127 | 8.72900778e-05 | 0.312554234 | 0.000115975698 | 0.298233152 |
| MATCH-EWMA-A-IO | 8.62845793e-05 | 0.31665584 | 0.000154172892 | 0.330778127 | 8.72961276e-05 | 0.312554234 | 0.000116142788 | 0.298233152 |
| MATCH-HAR-RV-A-G | 8.47160148e-05 | 0.317108469 | 0.000150889127 | 0.32819327 | 8.74399793e-05 | 0.31112561 | 0.000113227654 | 0.30143337 |
| MATCH-HAR-RV-A-IO | 8.4687613e-05 | 0.317108469 | 0.000150927269 | 0.32819327 | 8.74377392e-05 | 0.31112561 | 0.000113213272 | 0.30143337 |
| MATCH-GARCH11-STRICT999-G | 8.60225959e-05 | 0.301521814 | 0.000153793196 | 0.327163045 | 8.72989254e-05 | 0.307597863 | 0.000116401152 | 0.293450639 |
| MATCH-GARCH11-STRICT999-IO | 8.60366201e-05 | 0.301521814 | 0.00015377963 | 0.327163045 | 8.74207901e-05 | 0.307597863 | 0.000116408948 | 0.293450639 |
| CLOCK-UNCAL | 9.05610757e-05 | 0.326276066 | 0.000159190305 | 0.354450911 | 9.1029308e-05 | 0.323804151 | 0.000116300468 | 0.316485046 |
| S2C-UNCAL | 9.08226018e-05 | 0.327460711 | 0.000158114349 | 0.351764497 | 9.06166228e-05 | 0.326300734 | 0.000116384452 | 0.319417965 |
| S5C-UNCAL | 9.00113142e-05 | 0.329436454 | 0.00015837742 | 0.354295639 | 8.90871596e-05 | 0.328670863 | 0.000117151214 | 0.315780783 |
| ROLL20-UNCAL | 8.90895829e-05 | 0.305088668 | 0.000158295027 | 0.315386703 | 8.9327642e-05 | 0.294477085 | 0.000117631399 | 0.285245027 |
| ROLL60-UNCAL | 8.70849864e-05 | 0.319192524 | 0.000154115837 | 0.329617223 | 8.74108738e-05 | 0.315863317 | 0.000113773292 | 0.310086848 |
| EXPANDING-UNCAL | 8.77499475e-05 | 0.300266636 | 0.000165195867 | 0.324375251 | 8.66883772e-05 | 0.306324979 | 0.000114804543 | 0.303153722 |
| EWMA-R2-FN-UNCAL | 8.65275525e-05 | 0.313324714 | 0.000155769968 | 0.32541651 | 8.87985652e-05 | 0.306345565 | 0.000120632479 | 0.289764785 |
| EWMA-A-UNCAL | 8.62345077e-05 | 0.31665584 | 0.00015383949 | 0.330778127 | 8.75739274e-05 | 0.312554234 | 0.000115029841 | 0.298233152 |
| HAR-RV-A-UNCAL | 8.44671485e-05 | 0.317108469 | 0.000150740253 | 0.32819327 | 8.74585943e-05 | 0.31112561 | 0.000113182803 | 0.30143337 |
| GARCH11-STRICT999-UNCAL | 8.73376666e-05 | 0.301521814 | 0.000153557524 | 0.327163045 | 8.86021837e-05 | 0.307597863 | 0.000118851279 | 0.293450639 |
| ROLL20-CAL | 8.92065088e-05 | 0.305088668 | 0.000157691031 | 0.315386703 | 8.89880382e-05 | 0.294477085 | 0.000118634635 | 0.285245027 |
| ROLL60-CAL | 8.69245315e-05 | 0.319192524 | 0.000159852984 | 0.329617223 | 8.67859161e-05 | 0.315863317 | 0.00011479118 | 0.310086848 |
| EXPANDING-CAL | 9.11380406e-05 | 0.300266636 | 0.000157582462 | 0.324375251 | 9.27031328e-05 | 0.306324979 | 0.000114560032 | 0.303153722 |
| EWMA-R2-FN-CAL | 8.6737218e-05 | 0.313324714 | 0.000154948142 | 0.32541651 | 8.76355358e-05 | 0.306345565 | 0.000120183921 | 0.289764785 |
| EWMA-A-CAL | 8.62887697e-05 | 0.31665584 | 0.000154167127 | 0.330778127 | 8.72900778e-05 | 0.312554234 | 0.000115975698 | 0.298233152 |
| HAR-RV-A-CAL | 8.47160148e-05 | 0.317108469 | 0.000150889127 | 0.32819327 | 8.74399793e-05 | 0.31112561 | 0.000113227654 | 0.30143337 |
| CLOCK-C3 | 8.25546131e-05 | 0.326276066 | 0.000145909506 | 0.354450911 | 8.61730734e-05 | 0.323804151 | 0.000112026591 | 0.316485046 |
| S2C-C3 | 8.25757869e-05 | 0.327460711 | 0.000145764972 | 0.351764497 | 8.61482451e-05 | 0.326300734 | 0.000111703667 | 0.319417965 |
| S5C-C3 | 8.30919153e-05 | 0.329436454 | 0.000145744566 | 0.354295639 | 8.59918322e-05 | 0.328670863 | 0.000112567872 | 0.315780783 |
| C0 | 9.05411142e-05 | 0.317858411 | 0.000158509783 | 0.350296859 | 9.11617854e-05 | 0.320244732 | 0.000118921589 | 0.310272403 |
| C3 | 8.33206581e-05 | 0.317858411 | 0.000146675673 | 0.350296859 | 8.62582077e-05 | 0.320244732 | 0.00011265323 | 0.310272403 |
| C1a | 8.43031656e-05 | 0.317858411 | 0.000148225017 | 0.350296859 | 8.68356246e-05 | 0.320244732 | 0.000113510805 | 0.310272403 |
| M1 | 8.37906705e-05 | 0.317858411 | 0.000149379874 | 0.350296859 | 8.66027315e-05 | 0.320244732 | 0.000113292321 | 0.310272403 |
| B0-VOL | 8.6535921e-05 | 0.311836316 | 0.000153696422 | 0.323147173 | 9.02286885e-05 | 0.290951703 | 0.000115780653 | 0.290637452 |
| B0-CLOCK | 8.87338372e-05 | 0.290385328 | 0.00016861834 | 0.317860598 | 8.65792473e-05 | 0.303643541 | 0.000114746747 | 0.299311349 |
| B0-RMEAN | 9.63421623e-05 | 0.289524999 | 0.00017887366 | 0.31318948 | 9.29967288e-05 | 0.303483201 | 0.000121245116 | 0.294755411 |
| B0-RMED | 0.000108972654 | 0.280935149 | 0.000212799446 | 0.312479373 | 0.00010117992 | 0.299685135 | 0.00012941663 | 0.291358079 |


## Conditions, tails and persistent score component

| arm | scope | raw_MSE | raw_MAE | ratio | IC |
| --- | --- | --- | --- | --- | --- |
| MATCH-S2C-G | FULL | 0.000106847027 | 0.00684680351 | 1.05431533 | 0.331235977 |
| MATCH-S2C-G | INTRADAY | 5.24070647e-05 | 0.0051388321 | 1.1342809 | 0.318110216 |
| MATCH-S2C-G | OVERNIGHT | 0.000148582679 | 0.00816413367 | 1.01628036 | 0.342408042 |
| MATCH-S2C-IO | FULL | 0.000106488179 | 0.00682198741 | 1.04854978 | 0.331235977 |
| MATCH-S2C-IO | INTRADAY | 5.14097549e-05 | 0.00499321855 | 1.06644863 | 0.318110216 |
| MATCH-S2C-IO | OVERNIGHT | 0.000148724386 | 0.00823323823 | 1.0399912 | 0.342408042 |
| MATCH-HAR-RV-A-G | FULL | 0.000109068194 | 0.0068339672 | 1.01348562 | 0.31446518 |
| MATCH-HAR-RV-A-G | INTRADAY | 5.19634028e-05 | 0.0049784997 | 1.03319951 | 0.303432544 |
| MATCH-HAR-RV-A-G | OVERNIGHT | 0.000152894828 | 0.00826664466 | 1.0042695 | 0.326066534 |
| MATCH-HAR-RV-A-IO | FULL | 0.000109066473 | 0.00682951141 | 1.01161496 | 0.31446518 |
| MATCH-HAR-RV-A-IO | INTRADAY | 5.18654682e-05 | 0.00494836367 | 1.01614791 | 0.303432544 |
| MATCH-HAR-RV-A-IO | OVERNIGHT | 0.000152968935 | 0.00828225654 | 1.00964071 | 0.326066534 |
| MATCH-GARCH11-STRICT999-G | FULL | 0.000110878967 | 0.00686002207 | 0.990064363 | 0.30743334 |
| MATCH-GARCH11-STRICT999-G | INTRADAY | 5.29613817e-05 | 0.00495609724 | 0.988975525 | 0.299205161 |
| MATCH-GARCH11-STRICT999-G | OVERNIGHT | 0.000155297211 | 0.00832714844 | 0.989968598 | 0.314087667 |
| MATCH-GARCH11-STRICT999-IO | FULL | 0.000110911497 | 0.00686187733 | 0.990184788 | 0.30743334 |
| MATCH-GARCH11-STRICT999-IO | INTRADAY | 5.29266944e-05 | 0.00494534518 | 0.982630103 | 0.299205161 |
| MATCH-GARCH11-STRICT999-IO | OVERNIGHT | 0.000155381437 | 0.0083386467 | 0.993100042 | 0.314087667 |


GARCH has higher MSE and lower IC than matched S2-C in both intraday and overnight conditions, while its intraday MAE is lower. A near-unity overall mean ratio does not imply good conditional calibration or tail accuracy. Calibration-dependent extreme-event conclusions remain: raw GARCH's tail MSE advantage over raw S2-C reverses under common G/IO, but GARCH can still beat native S2C-C3 on realized-tail loss while losing overall. The distinct calibration procedures explain why those statements can coexist.

| comparison | level | GARCH_MSE | reference_MSE | percent | GARCH_ratio | reference_ratio | GARCH_loss_share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RAW | 95 | 0.00104127555 | 0.00134310341 | -22.4724213 | 0.400331242 | 0.280563329 | 0.523927108 |
| RAW | 99 | 0.00369563597 | 0.00438392742 | -15.7003387 | 0.261209278 | 0.182477644 | 0.301641508 |
| G | 95 | 0.00111518054 | 0.00109228115 | 2.09647384 | 0.367905974 | 0.379360217 | 0.56761564 |
| G | 99 | 0.00386903631 | 0.00382941538 | 1.03464718 | 0.240145173 | 0.246978511 | 0.317903026 |
| IO | 95 | 0.00111341122 | 0.00108251814 | 2.85381664 | 0.368586745 | 0.383313909 | 0.566665651 |
| IO | 99 | 0.00386329495 | 0.0038002969 | 1.65771405 | 0.240840768 | 0.250531455 | 0.317273485 |
| G vs native C3 | 95 | 0.00111518054 | 0.00113572815 | -1.80920163 | 0.367905974 | 0.35979035 | 0.56761564 |
| G vs native C3 | 99 | 0.00386903631 | 0.00393470875 | -1.66905451 | 0.240145173 | 0.233589157 | 0.317903026 |
| IO vs native C3 | 95 | 0.00111341122 | 0.00113572815 | -1.96498859 | 0.368586745 | 0.35979035 | 0.566665651 |
| IO vs native C3 | 99 | 0.00386329495 | 0.00393470875 | -1.81497022 | 0.240840768 | 0.233589157 | 0.317273485 |


Realized-tail categories are outcome diagnostics only. PREFIX95 and PREFIX99 complements, predicted/observed ratios and weighted squared-error contributions are saved for every arm/year/category. No future extreme is used to select a model or route forecasts. The previously suggested classical/LSTM extreme-event hybrid remains a deferred, unvalidated idea; none was constructed.

| family | field | group | rows | sessions | GARCH_MSE | S2C_MSE | percent | GARCH_ratio | S2C_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G | slot | 09:30 | 9900 | 495 | 8.8646821e-05 | 8.65444023e-05 | 2.42929488 | 0.963942822 | 1.06780325 |
| G | slot | 10:30 | 12200 | 610 | 4.48754605e-05 | 4.40842172e-05 | 1.79484486 | 0.979632728 | 1.14981567 |
| G | slot | 11:30 | 12920 | 646 | 3.66741745e-05 | 3.68573828e-05 | -0.497073435 | 1.01266867 | 1.1938384 |
| G | slot | 12:30 | 12000 | 600 | 0.000138044032 | 0.000133812798 | 3.16205504 | 1.00398061 | 1.03418035 |
| G | slot | 13:30 | 10800 | 540 | 0.000164754853 | 0.000157532513 | 4.58466581 | 0.987937948 | 1.02411519 |
| G | slot | 14:30 | 10940 | 547 | 0.000151464905 | 0.000144149349 | 5.07498388 | 0.996736219 | 1.02771741 |
| G | slot | 15:30 | 11500 | 575 | 0.000169844673 | 0.000161982427 | 4.85376446 | 0.984179549 | 0.983326278 |
| G | calendar | EARLY | 280 | 5 | 0.000113403509 | 9.49402937e-05 | 19.4471858 | 0.752712313 | 1.06632559 |
| G | calendar | NORMAL | 79980 | 788 | 0.000110866429 | 0.000106929489 | 3.68180901 | 0.991919041 | 1.05424396 |
| IO | slot | 09:30 | 9900 | 495 | 8.85694946e-05 | 8.60453551e-05 | 2.93349884 | 0.957979375 | 1.00578229 |
| IO | slot | 10:30 | 12200 | 610 | 4.48535401e-05 | 4.30270658e-05 | 4.24494272 | 0.973120781 | 1.08260046 |
| IO | slot | 11:30 | 12920 | 646 | 3.66701595e-05 | 3.5617374e-05 | 2.95582009 | 1.00595986 | 1.12349826 |
| IO | slot | 12:30 | 12000 | 600 | 0.000138087261 | 0.000134130059 | 2.95027252 | 1.00715691 | 1.0583393 |
| IO | slot | 13:30 | 10800 | 540 | 0.000164826286 | 0.000157760991 | 4.47848044 | 0.991109393 | 1.04799874 |
| IO | slot | 14:30 | 10940 | 547 | 0.000151597036 | 0.000144371621 | 5.00473347 | 0.999879405 | 1.05169047 |
| IO | slot | 15:30 | 11500 | 575 | 0.000169938194 | 0.000161793628 | 5.03392219 | 0.987274631 | 1.00624039 |
| IO | calendar | EARLY | 280 | 5 | 0.000113733571 | 9.55776446e-05 | 18.995997 | 0.75502565 | 1.09120732 |
| IO | calendar | NORMAL | 79980 | 788 | 0.000110897407 | 0.000106564955 | 4.06554972 | 0.992026845 | 1.04828114 |


Only 5 early-close sessions/14 origins/280 OOS rows are represented; these results have very limited support. All 20 stock comparisons and months are retained in heterogeneity_comparisons.csv/groups.csv; rank_groups.csv uses complete20-stock origin panels for clock/month/calendar ranking. Coverage and cap-contact cohorts are descriptive conditional summaries, not filters on the evaluation panel. Stock-score deciles use the archived C0 descriptive cut convention; they do not fit calibration.

| year | arm | static_variance | temporal_variance | static_fraction |
| --- | --- | --- | --- | --- |
| EQ | MATCH-S2C-G | 1.21376783e-05 | 3.24852088e-06 | 0.780676124 |
| EQ | MATCH-S5C-G | 1.17011544e-05 | 3.17075715e-06 | 0.780849236 |
| EQ | MATCH-ROLL60-G | 1.69080514e-05 | 3.09204333e-06 | 0.839349014 |
| EQ | MATCH-HAR-RV-A-G | 1.37890928e-05 | 4.56771669e-06 | 0.747344285 |
| EQ | MATCH-GARCH11-STRICT999-G | 1.40452177e-05 | 4.52396959e-06 | 0.76016911 |
| EQ | MATCH-GARCH11-STRICT999-IO | 1.4041709e-05 | 4.56679267e-06 | 0.75873007 |
| EQ | B0-RMEAN | 1.14828592e-05 | 6.16743425e-34 | 1 |


The within-origin-centered score decomposition gives GARCH~76.0% static cross-stock variance under G, versus~78.1% for S2-C/S5-C,~83.9% for ROLL60 and~74.7% for HAR. Thus GARCH has a somewhat larger temporal component than these neural outputs, but still a dominant persistent stock component and lower ranking skill. These variance fractions are not a decomposition of predictive accuracy and do not establish a causal role for recurrence.

## Verification and resource record

All 660 archived metric rows across 44 frozen arms, four annual folds plus equal-year rows and three scopes replay within the existing tolerance. Every saved predecessor score column is exactly identical in all eight calibration/OOS panels. New coefficients were independently recomputed from Oct–Dec only, and all new raw/G/IO keys, labels and weights agree. Fit and calibration outputs are separately hash-frozen.

37 focused tests pass; Ruff passes. Full installed Pylance/basic analysis covers 546 Python files with 0 errors/0 warnings, without exclusions or reduced severity. The researcher confirmed a human VSCode Problems refresh at zero errors. Initial synthetic-fixture/type-check failures and their corrections are retained; no real unit was retried. Arrow sandbox hardware notices are nonfatal. A /usr/bin/time wrapper failed its sandboxed kern.clockrate query after a zero-diagnostic static check; the wrapper failure is retained and is not represented as a type-check failure or a measured memory peak. A subsequent successful resource-aware full check recorded peak child RSS 1.718731GB, below the 2GB process ceiling, with zero errors/warnings.

Real fitting took 210.228s, peak process RSS527.581MB; independent replay peak519.094MB. Calibration took 5.381s. Final storage/resources and report-only byte-parity replay are recorded in final_integrity.json and report_replay_verification.json. Task output exceeded its initial150MB estimate because complete frozen comparison score panels were preserved, but remained well below 2.5GB; project remains below 15GB. No dependencies changed, Git fetch/commit/push, neural work, source rebuild, trading or protected holdout action occurred.

## Decision and hard stop

| Decision | Result |
|---|---|
| Technical admissibility | COMPLETE:560/560;13 cap contacts explicitly audited; three COP units now pass. |
| Full-panel fairness |80,260 identical OOS rows; no diagnostic/cohort exclusions; original weights and roles. |
| G against G / IO against IO |GARCH loses magnitude MSE and ranking to all three neural comparators in all four years; strongest classical frontiers remain HAR and ROLL60. |
| Remaining uncertainty |Conditional-Gaussian/irregular-event approximation, unequal feature sets, publication proxy, source/survivor vintage and repeated-year/post-search evidence. |
| Historical primaries |All old scores/calibrations/failures and journals preserved; old GARCH remains blocked. |
| Benchmark closure |This bounded classical implementation comparison is technically closed. No claim that all classical methods are exhausted or recurrence is indispensable. |
| Next action |Researcher review only. STOP: no tuning, router/hybrid, trading, new model or autonomous sequel. |
