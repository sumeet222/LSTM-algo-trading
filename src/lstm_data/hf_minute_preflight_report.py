"""Stage-appropriate Package018 stop reports; never imply sampled or complete history."""

from pathlib import Path


def write_reports(out: Path, manifest: dict, boundary: str) -> None:
    resources = manifest["resources"]
    rights = manifest["rights"]
    decision = rights["decision"]
    url = manifest["dataset_url"]
    revision = manifest["revision"]
    readme_url = f"{url}/blob/{revision}/README.md"
    terms = rights["provider_terms_url"]
    text = f"""# Package018 coverage preflight

**{decision}. No minute bars downloaded, sampled, filled or aggregated.** The first failing
gate is substantiation of legitimate local research use for this new Finnhub-derived source.
The existing Twelve Data rights attestation is source-specific and does not cover this dataset.
Public availability is not attributable permission for third-party data or its redistribution.
This is the requested operational gate decision, not a finding that any party acted unlawfully.

## Pinned evidence

Dataset [{manifest["dataset"]}]({url}), immutable revision {revision}.
The [pinned publisher card]({readme_url}) attributes data to Finnhub. API card license:
{rights["card_license"]}; license file paths:{rights["license_files"]}. No attributable grant
covering the uploader's distribution and this local research scope was established.
[Finnhub's public terms]({terms}) restrict sharing data and derived results without written
approval; access itself does not establish a license. Native terms receipt records the HTTP
body SHA256/time plus a short excerpt. Provider lineage and historical terms remain unverified.
No private agreements/accounts were inspected. This is not an independent legal determination.

## Filename listing is not per-stock coverage

There are{resources["monthly_files"]}monthly Parquets, listed from
{manifest["first_listed_month"]}through **{manifest["latest_listed_month"]}**.
Missing filename months:{manifest["missing_filename_months"]}. Exact sizes/LFS SHA256,
Git blob and Xet identities where supplied are in monthly_file_manifest.csv/source_manifest.json.
Listing completeness was checked against the API sibling set; no whole-repository clone/load.

**Latest genuinely complete month:UNVERIFIED.** No assumption of coverage through October2026,
or even a complete last listed month, is made. Card schema is timestamp minute-start UTC,
ticker and OHLCV; no actual Parquet schema or timestamp convention was independently checked.

Exact canonical20order:{",".join(manifest["symbols"])}.
For every stock, first/last genuine minute, regular-session coverage, duplicate/invalid rates,
ticker variants, month boundaries, DST/half-days and cross-year continuity remain UNVERIFIED.
coverage_preflight.csv has20explicit rows; stock_by_sampled_month.csv is a **planned** matrix
marked NOT_SAMPLED_STOP_RIGHTS, with empty observed values, not zero observed coverage.
No stock was dropped, replaced or selected by model outcomes.

## Duration gate

Actual common start/end and >=14calendar-years+9calendar-months verdict are **UNVERIFIED**.
If the last listed month were genuinely complete, a conservative theoretical start boundary
would be around **{boundary}**. This calendar calculation is a sampling/resource bound,
not evidence of real rows or an approved window. Compare actual start plus
DateOffset(years=14,months=9) to actual end; a month-file count does not prove elapsed duration.
Exact genuine session boundaries still need inspection. No short-window failure is asserted.

## Resources before any large transfer

All monthly upstream files total{resources["all_monthly_upstream_bytes"]:,}bytes
({resources["all_monthly_upstream_bytes"] / 1e9:.3f}GB decimal); disk free at check
{resources["disk_free_bytes"]:,}bytes ({resources["disk_free_bytes"] / 1e9:.3f}GB).
The theoretical boundary-through-latest subset is{resources["theoretical_candidate_files"]}files /
{resources["theoretical_candidate_upstream_bytes"]:,}bytes; largest month
{resources["largest_month_bytes"]:,}bytes. Ticker filtering is not proven to reduce transfer.
No remote-footer/range or predicate-pushdown claim was tested or made.

Pure bandwidth scenarios:approximately{resources["candidate_transfer_hours_at_10_Mbps"]:.2f}hours
at10Mbps or{resources["candidate_transfer_hours_at_50_Mbps"]:.2f}hours at50Mbps sustained,
excluding overhead. These are assumptions, not measured throughput or transfer permission.
Persistent20stock size, Arrow expansion and bounded row-group working set remain unmeasured.
No source-mirror or numerical working-set fit is asserted. Later acquisition needs resumable,
checksum-verified month checkpoints, row-group extraction and sufficient temporary space.

## Stop and preservation

Per Package018 §1.1, do not advance past this unresolved rights gate. Sentinel rows, raw minute
QA, imputation, hourly aggregation, overlap/action comparison, feature/target creation and
source activation were not reached. No placeholder PASS, synthetic years or hourly release.
Existing original/HF20held-out, protocol, scalers, models, dashboard and ledgers are unchanged;
journal remains32/200. No model inference/training, portfolio replay, substitution, data-bearing
Parquet/TAR request or bulk cache was created. Source metadata is not a certified data panel.

Possible human decision:hold this source, or supply attributable evidence covering its
distribution and local research use. Then resume preflight at the rights boundary and inspect
actual rows before any duration/quality PASS. No alternate provider, cohort reduction,
threshold relaxation or additional experiment begins automatically.
"""
    (out / "coverage_preflight.md").write_text(text)
    (out / "expansion_readiness.md").write_text(f"""# Expansion readiness — {decision}

No >=14y9m usable common history has been established. No stock-level endpoints or genuine
minute coverage were sampled because rights substantiation failed before data transfer.
Newest listed month:{manifest["latest_listed_month"]}; actual completeness is unverified.
This is not STOP_WINDOW_SHORT and proves neither scientific data success nor failure.

First need attributable permissions for this Finnhub-derived dataset and local research scope.
Then require actual all20stock sentinel rows, continuous annual/monthly coverage, timestamp/
calendar/identity/action/adjustment evidence, defensible98%overall/95%year genuine coverage,
endpoint/large-gap checks and a measured bounded transfer/storage plan. Only a passing preflight
permits incremental raw acquisition under the original request. Filling/hourly release remain
conditional on whole-interval raw QA. Repairs cannot inflate genuine coverage.

No reliable LSTM data-growth estimate or new split strategy follows from a filename list.
Any expansion must be a separate minute-derived source version, retain canonical20order and
compare compatible targets/masks/common development dates under a separately approved method.
No pooling with Twelve Data or refitting FT1/TG20 here. Existing HF20held-out2026-01-07–2026-10-15
and original five-stock confirmation stay locked. Early2026file listings grant no protected
outcome access or new development membership. The10+3program and model-pair spending stay inactive.

No minute_qa_report/filling_audit/hourly_qa_report, plots, source-QA dashboard or data release
was generated because those stages were not reached. The existing explorer was not changed.
""")
