# S3-B — saved-result comparison

Status: QUALIFIED scientific result; technical stage gates are separate.

Primary estimates use each horizon's legitimate population. Secondary common evaluation retains horizon-specific fitting sets; it is not a fully identical-training-population effect. Four-hour scores/recipes are unchanged archival references. N0 IC is undefined.

| population | horizon | model | equal_year_ic | years | mean_concordance | mean_top4 | mean_bottom4 | complete_four_years |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRIMARY_HORIZON_SPECIFIC | 1 | NR | 0.01292187 | 4 | 0.5048579 | 0.229291 | 0.2069757 | True |
| PRIMARY_HORIZON_SPECIFIC | 1 | T2R | 0.006177281 | 4 | 0.5026829 | 0.2360447 | 0.2020342 | True |
| PRIMARY_HORIZON_SPECIFIC | 2 | NR | -0.0009608485 | 4 | 0.4993319 | 0.2115485 | 0.2069326 | True |
| PRIMARY_HORIZON_SPECIFIC | 2 | T2R | 0.00428328 | 4 | 0.5011746 | 0.2166574 | 0.2186079 | True |
| SECONDARY_COMMON | 1 | NR | 0.009991232 | 4 | 0.5029672 | 0.229961 | 0.2013693 | True |
| SECONDARY_COMMON | 1 | T2R | 0.01021884 | 4 | 0.5040476 | 0.2351041 | 0.1971306 | True |
| SECONDARY_COMMON | 2 | NR | 0.0041597 | 4 | 0.5008374 | 0.2149767 | 0.2135334 | True |
| SECONDARY_COMMON | 2 | T2R | 0.01043314 | 4 | 0.5032591 | 0.2255679 | 0.2215985 | True |


Full yearly/slot/month/stock/quality, true objective and tail tables are indexed in DIAGNOSTIC_FILE_INDEX.csv at collective close. Scores are price-only forecasts with a two-minute issuance assumption; no trading inference.

## Paired B minus A

| year | horizon | model | status | delta_ic | month_block_low | month_block_high | delta_concordance | delta_top4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 1 | T2R | PAIRED | 0.0006599112 | -0.01582911 | 0.01403698 | 0.001179676 | -0.002403846 |
| 2021 | 1 | NR | PAIRED | 0.02813511 | -0.02281665 | 0.06603027 | 0.009801837 | -0.005608974 |
| 2021 | 2 | T2R | PAIRED | 0.01036847 | -0.02295954 | 0.03718618 | 0.003997884 | 0.003810976 |
| 2021 | 2 | NR | PAIRED | -0.003663647 | -0.01417953 | 0.008023779 | -0.001543701 | -0.01219512 |
| 2022 | 1 | T2R | PAIRED | -0.01247155 | -0.03888969 | 0.01321464 | -0.005777819 | 0.009920635 |
| 2022 | 1 | NR | PAIRED | -0.002987671 | -0.01503568 | 0.01250541 | -0.0008913377 | -0.002645503 |
| 2022 | 2 | T2R | PAIRED | 0.01906425 | -0.01156232 | 0.04568286 | 0.004935736 | 0.003865979 |
| 2022 | 2 | NR | PAIRED | -0.003248071 | -0.01654306 | 0.01058084 | -0.0003129961 | 0.003865979 |
| 2023 | 1 | T2R | PAIRED | 0.0151305 | -0.02840356 | 0.04701393 | 0.005828075 | 0.03380503 |
| 2023 | 1 | NR | PAIRED | 0.01036302 | -0.007910696 | 0.02370659 | 0.003590738 | 0.0408805 |
| 2023 | 2 | T2R | PAIRED | 0.008784127 | -0.01901531 | 0.04541331 | 0.002936115 | -0.00400641 |
| 2023 | 2 | NR | PAIRED | 0.00924911 | -0.01168877 | 0.03085455 | 0.003221819 | 0 |
| 2024 | 1 | T2R | PAIRED | 0.002821678 | -0.01098195 | 0.01429733 | 0.001550255 | -0.008928571 |
| 2024 | 1 | NR | PAIRED | 0.001278011 | -0.0184949 | 0.02149932 | 0.0008317752 | -0.02232143 |
| 2024 | 2 | T2R | PAIRED | 0.02561522 | -0.02205837 | 0.05543532 | 0.00748518 | 0.005179558 |
| 2024 | 2 | NR | PAIRED | 0.007834752 | -0.02767496 | 0.04070994 | 0.001993474 | -0.01933702 |

Whole-month 400-replicate intervals are descriptive sensitivity summaries, not post-search significance tests.
