# Forecast parity

Original per-row C-A predictions ARE archived. All four OOS files (80260 rows) and calibration files (18980 rows) have exact unique key coverage, fixed20 stock axis and matching timestamp/category metadata; labels and weights match at required precision. Full candidate signedR and auxiliary targets additionally match the bound S4 archive exactly.

|year|quantity|n_expected|max_abs_difference|median_abs_difference|p99_abs_difference|correlation|float32_diagnostic_exceedances|
|---|---|---|---|---|---|---|---|
|2021|Mhat|19100|0.0037394165992736816|7.8111886978149414e-05|0.00080234587192535276|0.99999954507090294|17901|
|2021|S2C-RAW|19100|6.6500596894244687e-05|9.9843394545670941e-07|1.2267801061842932e-05|0.99999946919322835|9046|
|2021|S2C-C3|19100|8.4260961715144217e-05|1.2740037921921479e-06|1.5086161765181488e-05|0.99999954386578682|10603|
|2022|Mhat|23600|0.003748774528503418|0.00011718273162841797|0.00095224976539611721|0.99999946747982249|22394|
|2022|S2C-RAW|23600|5.7754003895880285e-05|1.7671971059742952e-06|1.7774701123619296e-05|0.9999993993976577|15488|
|2022|S2C-C3|23600|7.0918487084101894e-05|2.0964626097626053e-06|2.1429690924766941e-05|0.99999946843570764|16485|
|2023|Mhat|17740|0.0031121373176574707|0.00011920928955078125|0.00099428117275238061|0.99999927054268301|17025|
|2023|S2C-RAW|17740|5.756264468985417e-05|1.5388812944741766e-06|1.6467230066578568e-05|0.99999913693658571|11105|
|2023|S2C-C3|17740|6.7027745476150313e-05|1.7705552933988331e-06|1.832876130023691e-05|0.9999991986242317|11800|
|2024|Mhat|19820|0.011849343776702881|0.00020584464073181152|0.0016718763113021853|0.99999782042672269|19401|
|2024|S2C-RAW|19820|0.00013920026872539862|2.6636462822993492e-06|2.6480741936305416e-05|0.99999781341464344|15485|
|2024|S2C-C3|19820|0.0001654557681110393|3.2425242400941322e-06|3.0778701522023525e-05|0.99999800738824451|16129|

Differences are new minus original; correlation is descriptive, not parity. The diagnostic float32 tier is fixed at atol1e-6+rtol1e-5*abs(original). Many rows exceed it. No tolerance was widened. Per-stock/slot/category/p95/p99 summaries and p95/p99 error statistics are in FORECAST_PARITY.csv.

No original or independent RAW/C3 prediction is clamped to zero and no predicted ties are present. Nonetheless390 of762470 within-origin unordered pairs change order:53,109,82,146 in2021–24;368 origins are affected. The same pairs flip for Mhat/RAW/C3 because decoding is monotone per origin. Small near-order margins explain how nearly equal scalar MSE coexists with IC changes; this is not a tie/clamp bug. Pair witnesses include original margins in comparisons/pair_order_disagreements.csv.

Max C3 differences concentrate in2024; the largest stock-group maximum is SBUX, followed by BA and TSLA. Shared training can propagate stock-local feature changes to all names, so this pattern does not isolate a cause. First chronological joined-key differences are in first_difference_witnesses.csv.

Old per-row signed-head outputs are absent from the C-A forecast schema; only signed aggregate diagnostics can be compared. No original forecasts were generated.
