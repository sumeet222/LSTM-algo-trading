# S2-C — decomposition-assisted four-hour MAG

**Status: BLOCKED. Zero neural/non-neural fits and no forecast metrics.**

This is a separate scientific task, not an adverse score or a result of S2-B. No alternative label/population/architecture was substituted.

## Frozen specification

Protocol: `reports/experiments/hf20_s9_mag_stage2_bcd_2026-10-28/s2c_decomposition/protocol.json`. The original scientific specification preceded numerical source proof and fits. D's append-only v2 removes inherited four-hour scale/threshold reference fields from chronology metadata; no gate or scientific design changed. No gap scale or threshold was fitted or transferred.

- F21/inner_train:861 original overnight origins lack complete20 genuine components
- F21/selector:10 original overnight origins lack complete20 genuine components
- F21/restricted_refit:875 original overnight origins lack complete20 genuine components
- F21/calibration:34 original overnight origins lack complete20 genuine components
- F21/oos:112 original overnight origins lack complete20 genuine components
- F22/inner_train:934 original overnight origins lack complete20 genuine components
- F22/selector:66 original overnight origins lack complete20 genuine components
- F22/restricted_refit:1013 original overnight origins lack complete20 genuine components
- F22/calibration:11 original overnight origins lack complete20 genuine components
- F22/oos:95 original overnight origins lack complete20 genuine components
- F23/inner_train:1074 original overnight origins lack complete20 genuine components
- F23/selector:29 original overnight origins lack complete20 genuine components
- F23/restricted_refit:1109 original overnight origins lack complete20 genuine components
- F23/calibration:17 original overnight origins lack complete20 genuine components
- F23/oos:116 original overnight origins lack complete20 genuine components
- F24/inner_train:1178 original overnight origins lack complete20 genuine components
- F24/selector:43 original overnight origins lack complete20 genuine components
- F24/restricted_refit:1224 original overnight origins lack complete20 genuine components
- F24/calibration:18 original overnight origins lack complete20 genuine components
- F24/oos:137 original overnight origins lack complete20 genuine components

| year | role | N_origins | complete20_origins | missing_origins |
| --- | --- | --- | --- | --- |
| 2021 | inner_train | 6474 | 5613 | 861 |
| 2021 | selector | 195 | 185 | 10 |
| 2021 | restricted_refit | 6697 | 5822 | 875 |
| 2021 | calibration | 165 | 131 | 34 |
| 2021 | oos | 533 | 421 | 112 |
| 2022 | inner_train | 7103 | 6169 | 934 |
| 2022 | selector | 152 | 86 | 66 |
| 2022 | restricted_refit | 7286 | 6273 | 1013 |
| 2022 | calibration | 137 | 126 | 11 |
| 2022 | oos | 665 | 570 | 95 |
| 2023 | inner_train | 7793 | 6719 | 1074 |
| 2023 | selector | 177 | 148 | 29 |
| 2023 | restricted_refit | 7998 | 6889 | 1109 |
| 2023 | calibration | 139 | 122 | 17 |
| 2023 | oos | 505 | 389 | 116 |
| 2024 | inner_train | 8380 | 7202 | 1178 |
| 2024 | selector | 167 | 124 | 43 |
| 2024 | restricted_refit | 8578 | 7354 | 1224 |
| 2024 | calibration | 90 | 72 | 18 |
| 2024 | oos | 570 | 433 | 137 |

## Source and timing proof

The saved S4 artifact explicitly stores original entry/exit, genuine end-of-session price, next09:30 minute open, and signed pre/gap/post returns. The executed reader used adjusted, quarantined-source-filtered genuine minute close at actual session_close−1min and genuine next-session minute open; no15:30 surrogate, hourly proxy, synthetic target or new minute read is permitted. Original source/masks remain unchanged.

| year | role | night_origins | missing_close20 | missing_open20 |
| --- | --- | --- | --- | --- |
| 2021 | inner_train | 6474 | 4 | 857 |
| 2021 | selector | 195 | 0 | 10 |
| 2021 | restricted_refit | 6697 | 4 | 871 |
| 2021 | calibration | 165 | 5 | 29 |
| 2021 | oos | 533 | 52 | 68 |
| 2022 | inner_train | 7103 | 11 | 923 |
| 2022 | selector | 152 | 48 | 26 |
| 2022 | restricted_refit | 7286 | 63 | 958 |
| 2022 | calibration | 137 | 0 | 11 |
| 2022 | oos | 665 | 4 | 91 |
| 2023 | inner_train | 7793 | 63 | 1019 |
| 2023 | selector | 177 | 0 | 29 |
| 2023 | restricted_refit | 7998 | 67 | 1050 |
| 2023 | calibration | 139 | 0 | 17 |
| 2023 | oos | 505 | 0 | 116 |
| 2024 | inner_train | 8380 | 67 | 1119 |
| 2024 | selector | 167 | 0 | 43 |
| 2024 | restricted_refit | 8578 | 67 | 1165 |
| 2024 | calibration | 90 | 0 | 18 |
| 2024 | oos | 570 | 0 | 137 |

| year | origin_id | ticker | genuine_close_missing | next_open_missing |
| --- | --- | --- | --- | --- |
| 2021 | 2021-02-01T17:30:00+00:00 | MRK | False | True |
| 2022 | 2022-02-07T17:30:00+00:00 | MRK | False | True |
| 2023 | 2023-01-25T17:30:00+00:00 | MS | False | True |
| 2024 | 2024-02-02T17:30:00+00:00 | MS | False | True |

Signed additivity on supported cells passes atol1e−12/rtol1e−11; maximum error 4.2500725161431774e-16. This does not fill missing components. abs(total) is not a sum of component magnitudes; auxiliary labels are never inputs.

The all-original-key auxiliary source gate fails in every fold. Dropping these observations, imputing components or using a differently defined close would change this frozen experiment. No S2-C model, aux head fit, calibration or B/C performance comparison was run.

## Decision and boundaries

Reconsider only through a separate researcher decision about this exact source/coverage blocker. No new source, proxy, selector extension, minimum reduction, extra fold or future-data release is approved.2021–24 are exploratory/post-search;2025 outcomes and protected2026 values/hashes remain unused. No trading/options/strategy or deferred C0-intraday/M1-overnight route was run.
