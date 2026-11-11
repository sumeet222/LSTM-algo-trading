# Original versus independent metrics

All available C-A RAW/C3 full and conditional annual/EQ scalar/rank results, slot/calendar/tail values, event retrieval and annual signed diagnostics are compared at saved precision in the CSV.3912 matched numeric cells were compared; absent main-stock/conditional-rank/signed-EQ cells are explicitly NOT_COMPARABLE/NOT_ARCHIVED, not zero. Old NORMAL maps to REGULAR, tail_ALL/PREFIX95 to ALL:p95:event, and next_open_to_exit to post; these are explicit schema mappings. C0-deciles remain out of scope.

## Primary C3 screen

|year|metric|original|independent|delta|relative_difference|status|
|---|---|---|---|---|---|---|
|2021|mae|0.0063847103017600718|0.0063846022520348458|-1.0804972522607259e-07|-1.6923199349590936e-05|NEAR|
|2021|mse|8.2575786870776139e-05|8.2574325743986458e-05|-1.4611267896817454e-09|-1.7694373194024546e-05|NEAR|
|2021|spearman_ic|0.32746071142796407|0.32732160987468878|-0.00013910155327528928|-0.00042478852705323493|NEAR|
|2022|mae|0.0083145015809648042|0.0083145982514539977|9.6670489193456666e-08|1.1626732913825382e-05|NEAR|
|2022|mse|0.00014576497206830334|0.0001457657862122256|8.141439222547793e-10|5.5853193720181503e-06|NEAR|
|2022|spearman_ic|0.35176449709560592|0.35159485530405243|-0.00016964179155348758|-0.00048225955988782091|NEAR|
|2023|mae|0.0059815764763952043|0.0059815472180397514|-2.925835545283112e-08|-4.8914120831342541e-06|NEAR|
|2023|mse|8.6148245083777087e-05|8.6150982585531501e-05|2.7375017544136772e-09|3.1776639811426491e-05|NEAR|
|2023|spearman_ic|0.32630073404332477|0.32603295228947476|-0.00026778175385000491|-0.00082065936699501885|NEAR|
|2024|mae|0.006343595656034047|0.0063436655512255271|6.9895191480082164e-08|1.1018229292971668e-05|NEAR|
|2024|mse|0.00011170366735422022|0.00011170249861198698|-1.1687422332419496e-09|-1.0462881487460796e-05|NEAR|
|2024|spearman_ic|0.3194179649200779|0.31943557419050672|1.760927042881999e-05|5.5129242443285974e-05|NEAR|
|EQ|mae|0.0067560960037885316|0.0067561033181885305|7.3143999988756203e-09|1.0826370724711454e-06|NEAR|
|EQ|mse|0.0001065481678442692|0.00010654839828843263|2.3044416342602597e-10|2.1628167624885223e-06|NEAR|
|EQ|spearman_ic|0.33123597687174317|0.33109624791468062|-0.00013972895706254596|-0.0004218411248143192|NEAR|

All15 primary tests pass the predeclared screening bounds: relative MSE/MAE<=1e-4, absolute IC<=.0005. The broader method is not numerically equivalent because feature procedures/recipes differ and many per-row predictions exceed the diagnostic tier. Labels' annual/EQ observed means agree.

Independent arithmetic checks precede interpretation: compare.py recomputes both archives' full/category scalar and rank results; deep_checks.py separately uses Python fsum over stock→origin→session means and hand average-rank formulas; all_metric_audit.py recomputes all five Phase2 tables including conditional scopes, events, signed diagnostics and clamping. Maximum full-table difference2.22e-15, no undefined-value mismatch. Checks use round-trip CSV parsing and explicit full-key alignment; no positional score join.

Conditional scalar estimates retain original annual cell weights; conditional ranks regroup origins/sessions. Equal-year estimates average annual values; primary ratio uses mean predicted/mean observed. Tail cutoffs come from frozen refit records and are checked against exact integer-mass oracles, never estimated from OOS. No comparator fits or paired comparator inference were performed. Similar S2C outputs do not validate the original small improvement over CLOCK/classical baselines. Repeatedly inspected exploratory years and overlapping targets preclude an untouched-holdout or IID significance interpretation.
