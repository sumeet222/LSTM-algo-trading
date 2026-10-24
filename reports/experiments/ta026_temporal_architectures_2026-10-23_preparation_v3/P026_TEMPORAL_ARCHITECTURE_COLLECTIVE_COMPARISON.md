# P026 temporal architecture comparison

| arm | delta_MSE | delta_IC | verdict | uncertainty |
|---|---|---|---|---|
| A1 | -0.000257931 | 0.00024151 | suggestive joint positive point estimates | 400 month-block sensitivities; exploratory |
| A2 | 0.00209625 | -0.0159633 | negative joint point estimates | 400 month-block sensitivities; exploratory |
| A3 | 0.00818003 | -0.0634414 | negative joint point estimates | 400 month-block sensitivities; exploratory |


| arm | architecture | parameters | role | MSE | IC | prediction_SD | z_MSE | seconds | RSS | selected_epoch | raw_epoch | stopping_epoch |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T2/42 | saved TM0/T2 | 6433 | inner_train | 4.1415 | 0.0686956 | 0.0529382 | 1.32776 | undefined | undefined | undefined | undefined | undefined |
| T2/123 | saved TM0/T2 | 6433 | inner_train | 4.15267 | 0.0304987 | 0.0408401 | 1.33386 | undefined | undefined | undefined | undefined | undefined |
| ZERO | constant | 0 | inner_train | 4.15687 | undefined | 0 | undefined | undefined | undefined | undefined | undefined | undefined |
| A1 | TM1_ATTENTION | 6466 | inner_train | 4.14159 | 0.0679147 | 0.0532862 | 1.32784 | 244.176 | 4.83869e+08 | 7 | 7 | 17 |
| T2/42 | saved TM0/T2 | 6433 | inner_validation | 3.65218 | 0.0151132 | 0.0499224 | 1.31283 | undefined | undefined | undefined | undefined | undefined |
| T2/123 | saved TM0/T2 | 6433 | inner_validation | 3.65567 | 0.00450251 | 0.0394996 | 1.31401 | undefined | undefined | undefined | undefined | undefined |
| ZERO | constant | 0 | inner_validation | 3.65376 | undefined | 0 | undefined | undefined | undefined | undefined | undefined | undefined |
| A1 | TM1_ATTENTION | 6466 | inner_validation | 3.65215 | 0.0140402 | 0.050275 | 1.31286 | 244.176 | 4.83869e+08 | 7 | 7 | 17 |
| T2/42 | saved TM0/T2 | 6433 | refit | 4.05539 | 0.068176 | 0.0529598 | 1.32402 | undefined | undefined | undefined | undefined | undefined |
| T2/123 | saved TM0/T2 | 6433 | refit | 4.06612 | 0.0271055 | 0.0374243 | 1.32977 | undefined | undefined | undefined | undefined | undefined |
| ZERO | constant | 0 | refit | 4.06954 | undefined | 0 | undefined | undefined | undefined | undefined | undefined | undefined |
| A1 | TM1_ATTENTION | 6466 | refit | 4.05507 | 0.0681036 | 0.0535979 | 1.32394 | 244.176 | 4.83869e+08 | 7 | 7 | 17 |
| T2/42 | saved TM0/T2 | 6433 | development | 3.10656 | 0.0755594 | 0.0488872 | 1.28104 | undefined | undefined | undefined | undefined | undefined |
| T2/123 | saved TM0/T2 | 6433 | development | 3.11491 | 0.025493 | 0.0349004 | 1.28697 | undefined | undefined | undefined | undefined | undefined |
| ZERO | constant | 0 | development | 3.11656 | undefined | 0 | undefined | undefined | undefined | undefined | undefined | undefined |
| A1 | TM1_ATTENTION | 6466 | development | 3.1063 | 0.075801 | 0.0497437 | 1.28096 | 244.176 | 4.83869e+08 | 7 | 7 | 17 |
| A2 | TM3_MULTISCALE | 7217 | inner_train | 4.1411 | 0.0714076 | 0.0571736 | 1.32743 | 271.223 | 9.8997e+08 | 7 | 7 | 17 |
| A2 | TM3_MULTISCALE | 7217 | inner_validation | 3.6509 | 0.0164947 | 0.0541376 | 1.3128 | 271.223 | 9.8997e+08 | 7 | 7 | 17 |
| A2 | TM3_MULTISCALE | 7217 | refit | 4.05602 | 0.0693395 | 0.052768 | 1.3241 | 271.223 | 9.8997e+08 | 7 | 7 | 17 |
| A2 | TM3_MULTISCALE | 7217 | development | 3.10866 | 0.0595961 | 0.0480931 | 1.28276 | 271.223 | 9.8997e+08 | 7 | 7 | 17 |
| A3 | GRU32 | 4833 | inner_train | 4.14821 | 0.0452136 | 0.0404204 | 1.33144 | 147.975 | 9.8997e+08 | 3 | 6 | 13 |
| A3 | GRU32 | 4833 | inner_validation | 3.65495 | 0.0044738 | 0.0459661 | 1.31376 | 147.975 | 9.8997e+08 | 3 | 6 | 13 |
| A3 | GRU32 | 4833 | refit | 4.06286 | 0.0514207 | 0.0363007 | 1.32751 | 147.975 | 9.8997e+08 | 3 | 6 | 13 |
| A3 | GRU32 | 4833 | development | 3.11474 | 0.012118 | 0.0348634 | 1.28743 | 147.975 | 9.8997e+08 | 3 | 6 | 13 |


Primary comparison is saved seed42 T2 on identical panels; T2/123 contextual and ZERO are in each metrics file. Joint MSE/IC improvement is suggestive only; mixed outcomes remain mixed. Three dependent, development-informed architecture comparisons cannot establish formal significance or isolate parameter-count effects. E1/QR1 remain independent branches. No automatic promotion or further fitting. Inspect matched month-block intervals, all slices and mechanism tables before interpreting point estimates.
