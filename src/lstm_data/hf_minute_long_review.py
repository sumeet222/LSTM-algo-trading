"""Bounded source-regime diagnostics and six protected-period-safe provider comparisons."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq

from .config import digest
from .hf_minute_boundary_io import REVISION
from .hf_minute_long_io import DERIVED, Guard, replace_json
from .hf_minute_long_qa import issue_frame


def source_profiles(out: Path, states: dict, guard: Guard) -> dict:
    """One projected monthly scan for volume regimes, calendar anomalies and jump context."""
    profile = []
    receipts = []
    total_counts = {}
    context = []
    issue_summaries = []
    previous: dict[str, tuple[float, str]] = {}
    for month, state in sorted(states.items()):
        events = []
        sampled_events = 0
        # The human start-date boundary applies to all source audit passes too.
        if month < "2010-07":
            raise ValueError("STOP_IDENTITY: review outside active human scope")
        ref = state["qa"]["files"]["canonical_observed"]
        frame = pq.ParquetFile(ref["path"]).read().to_pandas()
        issues = (
            pq.ParquetFile(state["qa"]["files"]["minute_quality_issues"]["path"])
            .read(columns=["ticker", "timestamp_utc", "issue_type", "severity"])
            .to_pandas()
        )
        jumps = issues.loc[issues.issue_type == "ACTION_OR_SCALE_JUMP_OVER25PCT"]
        grouped = (
            issues.groupby(["ticker", "issue_type", "severity"], dropna=False)
            .agg(
                issue_records=("issue_type", "size"),
                distinct_timestamps=("timestamp_utc", "nunique"),
            )
            .reset_index()
        )
        grouped["source_month"] = month
        issue_summaries.append(grouped)
        for symbol, own in frame.loc[frame.is_rth].groupby("ticker", sort=False):
            own = own.sort_values("timestamp")
            median_volume = float(own.volume.median())
            median_close = float(own.close.median())
            prior = previous.get(symbol)
            ratio = median_volume / prior[0] if prior and prior[0] > 0 else np.nan
            profile.append(
                dict(
                    ticker=symbol,
                    source_month=month,
                    median_reported_minute_volume=median_volume,
                    median_reported_close=median_close,
                    volume_median_ratio_to_prior_observed_month=ratio,
                    scope="SOURCE_QA_NOT_TRAINABLE",
                    units="AS_REPORTED_NOT_INDEPENDENTLY_CERTIFIED",
                )
            )
            if prior is not None and np.isfinite(ratio) and (ratio >= 20 or ratio <= 0.05):
                event = issue_frame(
                    own.iloc[[0]],
                    month,
                    "VOLUME_REGIME_CHANGE_CANDIDATE",
                    "REVIEW",
                    state["raw"]["path"],
                    "NO_UNIT_CONVERSION_WITHOUT_EVIDENCE",
                )
                event["median_volume_ratio"] = ratio
                event["prior_observed_month"] = prior[1]
                events.append(event)
            previous[str(symbol)] = (median_volume, month)
            positions = pd.DatetimeIndex(own.timestamp).get_indexer(
                pd.DatetimeIndex(jumps.loc[jumps.ticker == symbol, "timestamp_utc"])
            )
            for position in positions:
                if sampled_events >= 5:
                    break
                position = int(position)
                if position < 0:
                    continue
                sampled_events += 1
                for k in range(max(0, position - 2), min(len(own), position + 3)):
                    record = own.iloc[k]
                    context.append(
                        dict(
                            source_month=month,
                            ticker=symbol,
                            source_row=int(record.source_row),
                            event_timestamp=str(own.timestamp.iloc[position]),
                            timestamp=str(record.timestamp),
                            open=float(record.open),
                            high=float(record.high),
                            low=float(record.low),
                            close=float(record.close),
                            volume=float(record.volume),
                            raw_link=state["raw"]["path"],
                            source_revision=REVISION,
                            disposition="PRESERVE_NO_CORPORATE_ACTION_ADJUSTMENT",
                        )
                    )
        # Keep noncalendar source prints as evidence, outside all model-oriented RTH hours.
        local = (
            frame.timestamp.dt.tz_convert("America/New_York")
            .dt.tz_localize(None)
            .to_numpy(dtype="datetime64[D]")
            .astype(str)
        )
        hourly = (
            pq.ParquetFile(state["qa"]["files"]["hourly_ohlcv"]["path"])
            .read(columns=["ticker", "session_date_et", "hour_start_utc", "issue_reasons"])
            .to_pandas()
        )
        affected = hourly.loc[hourly.issue_reasons != ""].copy()
        if len(affected):
            affected["issue_type"] = affected.issue_reasons.str.split("|")
            affected = affected.explode("issue_type")
            grouped = (
                affected.groupby(["ticker", "issue_type"])
                .agg(
                    issue_records=("issue_type", "size"),
                    distinct_timestamps=("hour_start_utc", "nunique"),
                )
                .reset_index()
            )
            grouped["issue_type"] = "HOURLY_" + grouped.issue_type
            grouped["severity"] = "REVIEW"
            grouped["source_month"] = month
            issue_summaries.append(grouped)
        valid_dates = set(hourly.session_date_et)
        noncalendar = frame.loc[~pd.Series(local).isin(valid_dates).to_numpy()]
        if len(noncalendar):
            events.append(
                issue_frame(
                    noncalendar,
                    month,
                    "NONCALENDAR_SOURCE_PRINT",
                    "REVIEW",
                    state["raw"]["path"],
                    "RETAIN_RAW_EXCLUDE_FROM_RTH_AGGREGATION",
                )
            )
        supplemental = pd.concat(events, ignore_index=True) if events else pd.DataFrame()
        counts = supplemental.issue_type.value_counts().to_dict() if len(supplemental) else {}
        for kind, n in counts.items():
            total_counts[kind] = total_counts.get(kind, 0) + n
        if len(supplemental):
            grouped = (
                supplemental.groupby(["ticker", "issue_type", "severity"], dropna=False)
                .agg(
                    issue_records=("issue_type", "size"),
                    distinct_timestamps=("timestamp_utc", "nunique"),
                )
                .reset_index()
            )
            grouped["source_month"] = month
            issue_summaries.append(grouped)
        receipts.append(
            guard.parquet(
                DERIVED / "qa_v2/source_regime_issues" / f"{month}.parquet",
                pa.Table.from_pandas(supplemental, preserve_index=False),
            )
        )
    pd.DataFrame(profile).to_csv(out / "source_month_regime_profiles.csv", index=False)
    issue_summary = pd.concat(issue_summaries, ignore_index=True)
    issue_summary["category"] = np.select(
        [
            issue_summary.issue_type.str.startswith("HOURLY_"),
            issue_summary.issue_type.eq("CAUSAL_PRICE_PROXY"),
            issue_summary.issue_type.isin(
                ["CONFLICTING_DUPLICATE", "EXACT_DUPLICATE", "INVALID_RAW_BAR"]
            ),
        ],
        ["AGGREGATION", "FILL", "RECONCILIATION"],
        default="SOURCE",
    )
    issue_summary["year"] = issue_summary.source_month.str[:4].astype(int)
    issue_summary["count_unit"] = np.where(
        issue_summary.category.eq("AGGREGATION"),
        "AFFECTED_HOUR_REASON",
        "MINUTE_ISSUE_OR_COVERAGE_MARKER",
    )
    issue_summary.to_csv(out / "issue_counts_by_ticker_month.csv", index=False)
    issue_summary.groupby(["ticker", "year", "category", "issue_type", "severity"], dropna=False)[
        ["issue_records", "distinct_timestamps"]
    ].sum().reset_index().to_csv(out / "issue_counts_by_ticker_year.csv", index=False)
    totals = (
        issue_summary.groupby(["category", "issue_type", "severity", "count_unit"], dropna=False)[
            ["issue_records", "distinct_timestamps"]
        ]
        .sum()
        .reset_index()
    )
    totals.to_csv(out / "issue_counts_by_type.csv", index=False)
    pd.DataFrame(context).to_parquet(
        out / "action_jump_neighbor_candles.parquet", index=False, compression="zstd"
    )
    replace_json(
        out / "supplemental_source_quality_manifest.json",
        dict(
            files=receipts,
            issue_counts=total_counts,
            scope_start="2010-07-01",
            max_jump_examples_per_month=5,
        ),
    )
    with (out / "data_quality_issue_register.md").open("a") as f:
        f.write(
            "\n## Final source-regime and event-context audit\n\n"
            f"Supplemental source issue counts: `{json.dumps(total_counts)}`. "
            "20x or1/20x month-to-month median reported volume is only a source-regime candidate, "
            "not proof of a unit change. No volume or price rescaling applied. "
            "Jump neighbor candles retain actual OHLCV, including rare genuine moves. "
            "Noncalendar prints remain raw/canonical evidence and never enter RTH hourly bins. "
            "All passes obey July2010 start. Earlier issuer warnings remain legacy evidence only.\n"
        )
        f.write(
            "\n|Category|Issue|Records|Distinct ticker/timestamp occurrences|\n"
            "|---|---|---:|---:|\n"
        )
        for row in totals.itertuples():
            f.write(
                f"|{row.category}|{row.issue_type}|{row.issue_records:,}|{row.distinct_timestamps:,}|\n"
            )
        f.write(
            "\nMinute/source records and affected-hour reasons have separate count units. "
            "Counts of records include all conflicting versions; distinct occurrences count "
            "ticker/timestamps within each issue type. Categories overlap and must not be summed "
            "as independent defects. NaT coverage markers have no timestamp. See the ticker-month "
            "and ticker-year issue tables for exact location/severity summaries.\n"
        )
    return dict(
        supplemental_issue_counts=total_counts,
        neighbor_candles=len(context),
        source_profile_rows=len(profile),
    )


def provider_comparison(out: Path, states: dict) -> None:
    """Six fixed pre-confirmation examples, separate sources; no scoring or data substitution."""
    path = Path(
        "reports/data_audit/ta_hf_twelvedata_hourly_2026-10-16_123344_final/acquisition_manifest.json"
    )
    if not path.exists():
        replace_json(
            out / "provider_comparison_status.json", dict(status="OLD_CACHE_UNAVAILABLE_NO_REQUEST")
        )
        return
    manifest = json.loads(path.read_text())
    ref = next(r for r in manifest["files"] if r["path"].endswith("/train.parquet"))
    old_path = Path(ref["path"])
    old_sha = ref["sha256"]
    if not old_path.exists() or digest(old_path) != ref["sha256"]:
        replace_json(
            out / "provider_comparison_status.json", dict(status="OLD_CACHE_UNAVAILABLE_NO_REQUEST")
        )
        return
    parquet = pq.ParquetFile(old_path)
    # Prove the entire selected source file predates both protected outcome barriers.
    datetime_col = parquet.schema_arrow.names.index("datetime")
    for i in range(parquet.num_row_groups):
        stats = parquet.metadata.row_group(i).column(datetime_col).statistics
        if (
            not stats
            or not stats.has_min_max
            or pd.Timestamp(str(stats.max)) >= pd.Timestamp("2024-07-01", tz="UTC")
        ):
            raise ValueError("STOP_IDENTITY: comparison file could decode protected old rows")
    times = [
        pd.Timestamp(date + " 09:30", tz="America/New_York")
        for date in ("2023-03-13", "2023-06-14", "2023-11-22")
    ]
    old = (
        ds.dataset(old_path)
        .to_table(
            columns=["datetime", "symbol", "open", "high", "low", "close", "volume"],
            filter=ds.field("datetime").isin(times) & ds.field("symbol").isin(["AAPL", "VZ"]),
        )
        .to_pandas()
    )
    rows = []
    for time in times:
        month = time.strftime("%Y-%m")
        ref = states[month]["qa"]["files"]["hourly_ohlcv"]
        new = pq.ParquetFile(ref["path"]).read().to_pandas()
        for symbol in ("AAPL", "VZ"):
            a = old.loc[(old.symbol == symbol) & (old.datetime == time)]
            b = new.loc[(new.ticker == symbol) & (new.hour_start_utc == time)]
            row: dict = dict(
                ticker=symbol,
                nominal_start_utc=time.tz_convert("UTC").isoformat(),
                status="MATCHED" if len(a) == len(b) == 1 else "NOT_MATCHED",
                interpretation="DESCRIPTIVE_DIFFERENT_PROVIDERS_NO_TRUTH_OR_EQUIVALENCE_CLAIM",
            )
            if len(a) == len(b) == 1:
                left = a.iloc[0]
                right = b.iloc[0]
                row.update(
                    old_vendor_close=float(left.close),
                    minute_derived_close=float(right.close),
                    close_ratio=float(right.close / left.close),
                    old_vendor_volume=float(left.volume),
                    new_observed_volume=float(right.observed_volume),
                    new_volume_complete=bool(right.volume_is_complete),
                    new_quality_tier=right.quality_tier,
                )
            rows.append(row)
    pd.DataFrame(rows).to_csv(out / "descriptive_provider_comparison.csv", index=False)
    replace_json(
        out / "provider_comparison_status.json",
        dict(
            status="DONE_PRIVATE_CACHE_ONLY",
            requested_examples=6,
            matched=sum(r["status"] == "MATCHED" for r in rows),
            network_bytes=0,
            protected_old_rows_decoded=0,
            old_manifest_sha256=digest(path),
            old_source_file_sha256=old_sha,
        ),
    )
