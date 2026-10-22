# Historical coverage and 15-year candidates

All authorized July2010–March2026 months were examined for every exact symbol. No modeling interval is selected.
The endpoint/coverage tables record exact-symbol source presence, not historical issuer or IPO certification. No retroactive ticker alias or synthetic pre-listing price was introduced. Source adjustment, dividends, publication history, rare-event and issuer identity uncertainties remain unresolved.

Strict requires all genuine unique valid minutes, complete observed volume and genuine endpoints. Moderate allows bounded causal price proxies with genuine endpoints; volume remains flagged incomplete. Broad partial coverage excludes unresolved action flags; a separate source-present standard retains those flags and rare genuine moves. Neither is a finalized model mask. Empty bins never acquire artificial prices. Stubs remain separate and are excluded from this full-hour analysis.

Contiguity means consecutive expected exchange full-hour positions, spanning calendar closures correctly. A hull between earliest/latest qualifying hours is not uninterrupted coverage. Candidate intervals below explicitly count holes and are proposals for human review, never training masks or quality certification.

|Standard|All-20 full hours|Longest consecutive expected-hour run|Run calendar days|
|---|---:|---:|---:|
|STRICT_GENUINE|2,647|37|9.92|
|MODERATE_GENUINE_ENDPOINTS_CAP5|17,860|206|55.08|
|BROAD_PARTIAL_ACTION_UNCERTAINTY_EXCLUDED|23,601|4,450|1079.17|
|BROAD_SOURCE_PRESENT_ACTION_FLAGS_RETAINED|23,613|7,455|1811.00|

## Unselected candidate intervals

See historical_window_candidates.csv for exact DateOffset duration and all-20 retained/lost hour counts.

- {"broad_all20_fraction": 0.9972034801136364, "broad_all20_hours": 22465, "broad_all20_missing_hours": 63, "candidate": "LATEST_15Y", "duration_at_least14y9m": true, "duration_at_least15y": true, "end": "2026-03-31T19:30:00+00:00", "expected_full_hours": 22528, "moderate_all20_fraction": 0.7671786221590909, "moderate_all20_hours": 17283, "moderate_all20_missing_hours": 5245, "note": "Candidate interval with explicitly counted quality losses; not uninterrupted quality PASS", "selected": false, "source_present_flags_retained_all20_fraction": 0.9977361505681818, "source_present_flags_retained_all20_hours": 22477, "source_present_flags_retained_all20_missing_hours": 51, "start": "2011-03-31T18:30:00+00:00", "strict_all20_fraction": 0.11700994318181818, "strict_all20_hours": 2636, "strict_all20_missing_hours": 19892}

- {"broad_all20_fraction": 0.9971557562076749, "broad_all20_hours": 22087, "broad_all20_missing_hours": 63, "candidate": "LATEST_14Y9M", "duration_at_least14y9m": true, "duration_at_least15y": false, "end": "2026-03-31T19:30:00+00:00", "expected_full_hours": 22150, "moderate_all20_fraction": 0.7689841986455982, "moderate_all20_hours": 17033, "moderate_all20_missing_hours": 5117, "note": "Candidate interval with explicitly counted quality losses; not uninterrupted quality PASS", "selected": false, "source_present_flags_retained_all20_fraction": 0.9976975169300226, "source_present_flags_retained_all20_hours": 22099, "source_present_flags_retained_all20_missing_hours": 51, "start": "2011-06-30T18:30:00+00:00", "strict_all20_fraction": 0.11846501128668172, "strict_all20_hours": 2624, "strict_all20_missing_hours": 19526}

- {"broad_all20_fraction": 0.9972493345164153, "broad_all20_hours": 22478, "broad_all20_missing_hours": 62, "candidate": "EARLIEST_COMMON_PLUS15Y", "duration_at_least14y9m": true, "duration_at_least15y": true, "end": "2025-07-01T14:30:00+00:00", "expected_full_hours": 22540, "moderate_all20_fraction": 0.7516415261756877, "moderate_all20_hours": 16942, "moderate_all20_missing_hours": 5598, "note": "Candidate interval with explicitly counted quality losses; not uninterrupted quality PASS", "selected": false, "source_present_flags_retained_all20_fraction": 0.9977373558118899, "source_present_flags_retained_all20_hours": 22489, "source_present_flags_retained_all20_missing_hours": 51, "start": "2010-07-01T13:30:00+00:00", "strict_all20_fraction": 0.11011535048802129, "strict_all20_hours": 2482, "strict_all20_missing_hours": 20058}

### Lowest minute completeness across the authorized history

This is a source-quality comparison, with all 20 names retained. Fractions use the authorized exchange grid, not an inferred issuer listing history. Hour fractions in this table include separately identified closing stubs.

|Stock|Unique valid RTH minutes|Strict hours/stubs|Moderate hours/stubs|Proxy minutes|
|---|---:|---:|---:|---:|
|MA|95.7079%|59.6995%|92.4199%|62,605|
|AVGO|95.8010%|50.4253%|93.6688%|62,056|
|TSLA|97.0100%|76.7891%|95.4317%|41,454|
|AMD|98.6243%|84.1520%|98.2154%|17,797|
|AMZN|98.6560%|75.9710%|97.9946%|17,435|

### Highest-risk stock-years by source minute completeness

|Stock|Year|Months examined|Unique valid RTH fraction|
|---|---:|---:|---:|
|TSLA|2010|6|77.5633%|
|MA|2013|12|81.1172%|
|TSLA|2012|12|85.4847%|
|AVGO|2010|6|86.3691%|
|MA|2012|12|88.5169%|
|AVGO|2023|12|89.8610%|
|AMD|2015|12|90.4299%|
|MA|2025|12|90.4425%|
|TSLA|2011|12|90.5056%|
|MA|2024|12|91.5664%|

For human review, use the latest-15y candidate as the initial comparison with the latest-14y9m and earliest-common candidates; compare retained genuine endpoints, unknown volume, quality hotspots and action evidence before selecting anything. No candidate is certified as uninterrupted 15-year usable coverage or activated for modeling. Do not replace a stock or relax a mask automatically.

## Risk review

Use ticker_actual_endpoints.csv, ticker_year_coverage.csv and the persistent issue register. Long absence is not automatically an IPO, halt or vendor failure. Exact-symbol series can predate the present issuer; historical identity must be verified before later modeling. No source prices, bar definitions, split factors, scaler/epsilon or chronology can be transferred from old Twelve Data/Alpaca pipelines.
