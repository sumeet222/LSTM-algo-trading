# P027 cross-stock comparison

A4 sees own FT16 plus two leave-one-out peer M1 summaries at every historical step; A5/A6 encode all16 channels of all20 histories before final-state exchange. A4 is not a full-information-matched control. No fourth full-peer LSTM is authorized; A5/A6 gains cannot identify the exchange mechanism independently of information/capacity.

| arm | delta_MSE | delta_daily_IC | verdict |
|---|---|---|---|
| A4 | -9.5069e-05 | -0.0117193 | mixed/inconclusive |
| A5 | 0.00335521 | -0.0259907 | joint negative point estimates |
| A6 | 0.00607059 | -0.0273578 | joint negative point estimates |


| arm | role | parameters | original_TG20_MSE | daily_IC | origin_IC | actual_z_MSE | prediction_SD | selected | raw_best | stopped | fit_seconds | fit_peak_RSS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A4 | inner_train | 6689 | 4.14072 | 0.0697321 | 0.0685398 | 1.32749 | 0.0514219 | 7 | 7 | 17 | 287.419 | 4.89898e+08 |
| T2/42 | inner_train | 6433 | 4.1415 | 0.0686956 | undefined | 1.32776 | 0.0529382 | undefined | undefined | undefined | undefined | undefined |
| T2/123 | inner_train | 6433 | 4.15267 | 0.0304987 | undefined | 1.33386 | 0.0408401 | undefined | undefined | undefined | undefined | undefined |
| ZERO | inner_train | 0 | 4.15687 | undefined | undefined | undefined | 0 | undefined | undefined | undefined | undefined | undefined |
| A4 | inner_validation | 6689 | 3.65125 | 0.0208137 | 0.023762 | 1.31195 | 0.0484387 | 7 | 7 | 17 | 287.419 | 4.89898e+08 |
| T2/42 | inner_validation | 6433 | 3.65218 | 0.0151132 | undefined | 1.31283 | 0.0499224 | undefined | undefined | undefined | undefined | undefined |
| T2/123 | inner_validation | 6433 | 3.65567 | 0.00450251 | undefined | 1.31401 | 0.0394996 | undefined | undefined | undefined | undefined | undefined |
| ZERO | inner_validation | 0 | 3.65376 | undefined | undefined | undefined | 0 | undefined | undefined | undefined | undefined | undefined |
| A4 | refit | 6689 | 4.05514 | 0.0674683 | 0.0672768 | 1.32386 | 0.0531469 | 7 | 7 | 17 | 287.419 | 4.89898e+08 |
| T2/42 | refit | 6433 | 4.05539 | 0.068176 | undefined | 1.32402 | 0.0529598 | undefined | undefined | undefined | undefined | undefined |
| T2/123 | refit | 6433 | 4.06612 | 0.0271055 | undefined | 1.32977 | 0.0374243 | undefined | undefined | undefined | undefined | undefined |
| ZERO | refit | 0 | 4.06954 | undefined | undefined | undefined | 0 | undefined | undefined | undefined | undefined | undefined |
| A4 | development | 6689 | 3.10646 | 0.0638402 | 0.0478981 | 1.28258 | 0.0522742 | 7 | 7 | 17 | 287.419 | 4.89898e+08 |
| T2/42 | development | 6433 | 3.10656 | 0.0755594 | undefined | 1.28104 | 0.0488872 | undefined | undefined | undefined | undefined | undefined |
| T2/123 | development | 6433 | 3.11491 | 0.025493 | undefined | 1.28697 | 0.0349004 | undefined | undefined | undefined | undefined | undefined |
| ZERO | development | 0 | 3.11656 | undefined | undefined | undefined | 0 | undefined | undefined | undefined | undefined | undefined |
| A5 | inner_train | 6593 | 4.14646 | 0.0630502 | 0.0623139 | 1.32989 | 0.0436805 | 3 | 7 | 13 | 170.599 | 5.39312e+08 |
| A5 | inner_validation | 6593 | 3.65115 | 0.0240593 | 0.0267996 | 1.31126 | 0.0447146 | 3 | 7 | 13 | 170.599 | 5.39312e+08 |
| A5 | refit | 6593 | 4.05977 | 0.0638551 | 0.0643335 | 1.32576 | 0.0414524 | 3 | 7 | 13 | 170.599 | 5.39312e+08 |
| A5 | development | 6593 | 3.10992 | 0.0495687 | 0.042894 | 1.28414 | 0.0380494 | 3 | 7 | 13 | 170.599 | 5.39312e+08 |
| A6 | inner_train | 8481 | 4.15418 | 0.0350243 | 0.0340791 | 1.33369 | 0.0383022 | 1 | 3 | 12 | 158.218 | 6.2346e+08 |
| A6 | inner_validation | 8481 | 3.65669 | -0.0132269 | -0.00941722 | 1.31423 | 0.0360128 | 1 | 3 | 12 | 158.218 | 6.2346e+08 |
| A6 | refit | 8481 | 4.06739 | 0.0337845 | 0.0326807 | 1.32978 | 0.0287512 | 1 | 3 | 12 | 158.218 | 6.2346e+08 |
| A6 | development | 8481 | 3.11263 | 0.0482016 | 0.0452886 | 1.28509 | 0.0250582 | 1 | 3 | 12 | 158.218 | 6.2346e+08 |


Paired400 month/two-month sensitivities seed22042, signed effects, origin/daily IC and block occupancy remain in matched_T2_S42.json and pairwise contrast JSONs. One seed, differing capacity/information, three comparisons and repeatedly used109 development sessions preclude formal significance or causal mechanism attribution. P026 references are separately labeled historical; no P026 parent promotion, E1/QR1 fusion, automatic model promotion or new training.

Read P027_RESEARCHER_DIAGNOSIS.md and scientific_closeout_v2 for detailed interpretation and complete secondary/gradient summaries.
