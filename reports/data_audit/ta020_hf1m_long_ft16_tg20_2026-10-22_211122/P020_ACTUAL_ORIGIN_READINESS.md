# P020 actual origin readiness

**FEATURE_READY_FOR_TRAINING. Dataset preparation only; neural training is not authorized.**

Frozen chronology: warmup2010-07-01–2011-03-31; research train2011-04-01–2025-06-30; inner train ends2023-01-23; nominal inner validation2023-01-24–2025-06-30; development2025-07-01–2025-12-31; protected confirmation2026-01-01–2026-03-31 (keys/calendar/source quality only). First48complete-hour contexts after fit cutoffs are embargoed. All horizons mature within the same session; no crossing labels survive. The nominal15calendar-year research/confirmation span contains14years3months of fitted training history plus9months earlier startup. Missing dates and hourly positions never compress.

| Split | Admitted origins | Stock rows | First/last admitted date |
| --- | --- | --- | --- |
| inner_train | 4428 | 88560 | 2011-04-01 / 2023-01-23 |
| inner_validation | 766 | 15320 | 2023-02-03 / 2025-06-30 |
| refit | 5210 | 104200 | 2011-04-01 / 2025-06-30 |
| development | 183 | 3660 | 2025-07-15 / 2025-12-31 |

| Split | Scheduled | Past input | Finite FT16 | Future20 | Joint before embargo | Final | Stock rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | 5894 | 5248 | 5248 | 4864 | 4428 | 4428 | 88560 |
| inner_validation | 1210 | 1010 | 1010 | 909 | 782 | 766 | 15320 |
| refit | 7104 | 6258 | 6258 | 5773 | 5210 | 5210 | 104200 |
| development | 250 | 250 | 250 | 194 | 194 | 183 | 3660 |

P019B upper bounds were5,210training /194development joint closing-price origins, not FT counts. Actual finite16channels preserve5,210/5,210=100%of the train bound. Development retains183/194=94.3299%; 11source-qualified origins fall in the predeclared48hour transform-availability embargo. Relative to scheduled opportunities: train5,210/7,104=73.3390%; development183/250=73.2%. Masks do not resurrect COP or long unavailable price contexts. Volume fallback provides usable fixed-width features without pretending the original incomplete volume tape became complete.

| Feature | Refit fallback % | Development fallback % |
| --- | --- | --- |
| M1 | 2.9971% | 2.9969% |
| M2 | 6.4799% | 5.9284% |
| M3 | 5.5225% | 4.8714% |
| M4 | 5.6445% | 4.8366% |
| V1 | 5.0585% | 3.7005% |
| V2 | 2.6872% | 2.8227% |
| V3 | 6.0922% | 4.5560% |
| B1 | 0.0041% | 0.0000% |
| B2 | 0.0041% | 0.0000% |
| Q1 | 6.7006% | 4.4553% |
| Q2 | 21.6755% | 10.0529% |
| T1 | 0.9061% | 0.8493% |
| T2 | 3.2655% | 4.0875% |
| T3 | 2.9657% | 0.0000% |
| T4 | 2.9657% | 0.0000% |
| T5 | 0.7346% | 0.0000% |

All15training calendar years have>=100eligible origins; exact counts: {"2011": 283, "2012": 126, "2013": 243, "2014": 429, "2015": 379, "2016": 452, "2017": 450, "2018": 456, "2019": 466, "2020": 436, "2021": 307, "2022": 376, "2023": 298, "2024": 320, "2025": 189}.

The maximum admitted channel fallback over all four splits is 34.2549%, below the declared80%screen. The13scaled channels are finite; native Q1/Q2 vary substantially rather than becoming constants. These are engineering screens, not statistical power or predictive-alpha claims. Sources retain missingness, retrospective cohort selection and incomplete volume limitations.

| Hypothetical exclusion | Retained names | Feature+endpoint potential |
| --- | --- | --- |
| NONE | 20 | 5210 |
| MA | 19 | 5540 |
| AVGO | 19 | 5533 |
| MA,AVGO | 18 | 5885 |

These quality-only counterfactuals do not construct smaller targets or change the20-stock cohort. No universe change is implemented or needed to meet the predeclared readiness screens.
