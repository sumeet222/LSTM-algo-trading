# Monthly ranking stability, 2021–2024

All31 accepted saved OOS model-fold cells reproduce their published annual ICs; four-year means also reconcile. This study uses saved annual fold forecasts only: no checkpoint forward, fitting or missing-PW replay. Each of the7 complete models has48 observed months; PW has36 actual months and12 explicit UNAVAILABLE_FAILED_START_65 cells. N0 has48 UNDEFINED cells, never zeros. January input embargo and quality eligibility reduce the original exchange-session population; reported counts are eligible sessions, not all scheduled market days.

Spearman uses within-origin20-stock ascending average ranks, undefined for constants. Origins are averaged equally within each session; sessions equally within month. Per-month mean, origin mean/SD/p05/p50/p95, sessions/origins/stock rows, positive-day fraction, pair concordance, ties and constant rates are in [MONTHLY_IC_BY_MODEL.csv](MONTHLY_IC_BY_MODEL.csv). [SAVED_DAILY_METRICS.csv](SAVED_DAILY_METRICS.csv) and [SAVED_ORIGIN_METRICS.csv](SAVED_ORIGIN_METRICS.csv) retain the denominators. Annual means weight months by defined-session counts; the final primary mean weights four annual means equally. Equal-weight months would answer a different question.

## Observed temporal variation

| year | model | defined_months | positive_months | minimum | maximum | minimum_sessions |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | LR | 12 | 8 | -0.08536726 | 0.09819549 | 6 |
| 2021 | N1 | 12 | 6 | -0.0963332 | 0.1460079 | 6 |
| 2021 | NR | 12 | 8 | -0.1408785 | 0.1335004 | 6 |
| 2021 | P | 12 | 4 | -0.191061 | 0.09254956 | 6 |
| 2021 | PW | 0 | 0 | nan | nan | 0 |
| 2021 | T2R | 12 | 7 | -0.09138756 | 0.12636 | 6 |
| 2022 | LR | 12 | 7 | -0.0854279 | 0.1104637 | 6 |
| 2022 | N1 | 12 | 6 | -0.07464869 | 0.08903509 | 6 |
| 2022 | NR | 12 | 5 | -0.1131579 | 0.1157895 | 6 |
| 2022 | P | 12 | 6 | -0.1282523 | 0.06140351 | 6 |
| 2022 | PW | 12 | 7 | -0.1460677 | 0.1409774 | 6 |
| 2022 | T2R | 12 | 6 | -0.05674629 | 0.1095596 | 6 |
| 2023 | LR | 12 | 5 | -0.1012889 | 0.1013963 | 7 |
| 2023 | N1 | 12 | 9 | -0.08055816 | 0.1417189 | 7 |
| 2023 | NR | 12 | 6 | -0.1200501 | 0.1573935 | 7 |
| 2023 | P | 12 | 9 | -0.2094612 | 0.1227712 | 7 |
| 2023 | PW | 12 | 7 | -0.1300752 | 0.1361738 | 7 |
| 2023 | T2R | 12 | 7 | -0.1174812 | 0.119883 | 7 |
| 2024 | LR | 12 | 6 | -0.1421053 | 0.06775272 | 7 |
| 2024 | N1 | 12 | 6 | -0.07002325 | 0.1229947 | 7 |
| 2024 | NR | 12 | 4 | -0.1176692 | 0.104386 | 7 |
| 2024 | P | 12 | 9 | -0.1249624 | 0.09488722 | 7 |
| 2024 | PW | 12 | 5 | -0.07013127 | 0.07603383 | 7 |
| 2024 | T2R | 12 | 3 | -0.08239348 | 0.07660819 | 7 |


M1 changes sign repeatedly: positive in6/12 months in2021,6/12 in2022,9/12 in2023 and6/12 in2024. Its annual IC stays positive in all4 years, declining from0.016731 in2023 to0.008443 in2024. T2R drops from7 positive months in2023 to3 in2024; NR6→4; PW7→5; LR5→6 despite its annual IC falling. Positive-month counts do not encode session weighting or effect magnitude and are not independent significance tests. Individual monthly ICs are noisy with as few as7 eligible sessions in the common2024 panel.

The common2024 deterioration is not universal: M1 remains positive annually and fitted static P is positive in9 months with annual IC0.020117. T2R/NR/PW annual ICs turn negative; LR is negative too. This is weaker evidence than a wholesale disappearance of all temporal ranking information. M1 itself changes, so a model's negative relative difference does not alone prove its own score degraded: both absolute and paired curves are provided.

[MONTHLY_PAIRED_IC.csv](MONTHLY_PAIRED_IC.csv) gives T2R−M1, NR−M1, LR−M1, T2R−LR, NR−T2R and actual PW comparisons; no PW2021 pair is manufactured. [MONTHLY_RANKING_STABILITY.html](MONTHLY_RANKING_STABILITY.html) shows monthly IC and paired differences offline; profile/reversal/constant context remains in CSV to avoid clutter. [MONTH_BLOCK_SENSITIVITY.csv](MONTH_BLOCK_SENSITIVITY.csv) preserves whole calendar-month blocks of paired daily sums/counts,400 fixed-seed replicates. Every annual key comparison interval includes zero. These are descriptive sensitivity intervals, not formal p-values or correction for the large prior model-selection history.

## Explanations and limits

Genuine feature-to-rank coefficient drift is plausible. Competing explanations include sampling noise, changes in eligible sessions/quality/fallback composition, label volatility and a static identity effect. Quality/slot attributions are available for the new matched linear comparison; no new state thresholds or bull/bear bins were chosen from2024 outcomes. A separately frozen time-forward repetition or a formal selection-aware null on an authorized new period would discriminate persistence from noise; neither is run here.

Gross index appreciation is not an adequate explanation by itself: a common additive log-return shift within an origin leaves realized ranks and IC unchanged. Heterogeneous beta/sector effects could still change ordering, but no comparable independent market-index series is approved/read here, so that causal explanation remains untested. Annual index trend is not substituted for within-origin rank evidence. Source publication/action-vintage, fixed-survivor, historical-label-before-issuance and repeatedly inspected2025 development qualifications remain. Protected2026 remains closed.
