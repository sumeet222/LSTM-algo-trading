"""Bounded final inventory, source-coverage windows and independent hourly reconstruction."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from .config import digest, now
from .hf20_source import SYMBOLS
from .hf_minute_boundary_io import DATASET, REVISION
from .hf_minute_long_io import DERIVED, NAMESPACE, Guard, replace_json
from .hf_minute_long_qa import COLUMNS, PRICE, calendar_frame, valid_values
from .hf_minute_long_review import provider_comparison, source_profiles


def duration_pass(start: pd.Timestamp, end: pd.Timestamp, years: int, months: int = 0) -> bool:
    """Real exchange-local calendar duration, including DST, rather than month-file counts."""
    a = start.tz_convert("America/New_York")
    b = end.tz_convert("America/New_York")
    return bool(a + pd.DateOffset(years=years, months=months) <= b)


def window_runs(
    index: pd.DatetimeIndex, ends: pd.DatetimeIndex, mask: np.ndarray, standard: str
) -> list[dict]:
    """Consecutive expected tradable full-hour positions; overnight/holidays are excluded."""
    edges = np.diff(np.r_[False, mask, False].astype(np.int8))
    rows = []
    for a, b in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1), strict=True):
        a, b = int(a), int(b)
        start = pd.Timestamp(index[a])
        end = pd.Timestamp(ends[b - 1])
        rows.append(
            dict(
                standard=standard,
                first_full_hour_start=start.isoformat(),
                last_full_hour_end=end.isoformat(),
                common_full_hours=int(b - a),
                calendar_days=(end - start).total_seconds() / 86400,
                duration_at_least15y=duration_pass(start, end, 15),
                duration_at_least14y9m=duration_pass(start, end, 14, 9),
            )
        )
    return sorted(rows, key=lambda r: r["common_full_hours"], reverse=True)


def reconstruct_month(state: dict, month: str) -> list[dict]:
    """Independent raw-value reconstruction of fixed representative hours; no predictions."""
    if month < "2010-07":
        raise ValueError("STOP_IDENTITY: pre-July2010 reconstruction prohibited")
    refs = state["qa"]["files"]
    hours = pq.ParquetFile(refs["hourly_ohlcv"]["path"]).read().to_pandas()
    if hours.empty:
        return []
    chosen = []
    for mask in (
        hours.strict_candidate & ~hours.is_stub,
        hours.filled_minutes > 0,
        hours.is_stub & (hours.genuine_minutes > 0),
        hours.action_uncertainty,
    ):
        candidates = hours.loc[mask]
        if len(candidates):
            chosen.append(candidates.iloc[0])
    raw = pq.ParquetFile(state["raw"]["path"]).read(columns=COLUMNS + ["source_row"]).to_pandas()
    unique = raw.drop_duplicates(COLUMNS)
    conflict = unique.duplicated(["ticker", "timestamp"], keep=False)
    observed = unique.loc[~conflict & valid_values(unique)].copy()
    proxy = pq.ParquetFile(refs["fill_proxies_cap5"]["path"]).read().to_pandas()
    rows = []
    for hour in chosen:
        sel = observed.loc[
            (observed.ticker == hour.ticker)
            & (observed.timestamp >= hour.hour_start_utc)
            & (observed.timestamp < hour.hour_end_utc)
        ]
        fill = proxy.loc[proxy.hour_id == hour.hour_id] if len(proxy) else pd.DataFrame()
        combined = pd.concat(
            [
                sel[PRICE + ["timestamp"]],
                fill[PRICE + ["timestamp"]] if len(fill) else sel.iloc[:0][PRICE + ["timestamp"]],
            ],
            ignore_index=True,
        )
        combined = combined.sort_values("timestamp")
        volume = float(sel.volume.sum())
        expected = dict(
            open=float(combined.open.iloc[0]),
            high=float(combined.high.max()),
            low=float(combined.low.min()),
            close=float(combined.close.iloc[-1]),
        )
        valid = all(
            np.isclose(float(hour[k]), v, rtol=1e-12, atol=1e-12) for k, v in expected.items()
        )
        valid = (
            valid
            and np.isclose(volume, float(hour.observed_volume))
            and len(sel) == hour.genuine_minutes
            and len(fill) == hour.filled_minutes
        )
        if len(fill):
            for record in fill.itertuples():
                timestamp = record.timestamp
                if not isinstance(timestamp, pd.Timestamp):
                    raise ValueError("STOP_SOURCE_INTEGRITY: proxy timestamp type changed")
                prior = observed.loc[
                    (observed.ticker == hour.ticker)
                    & (observed.timestamp < record.timestamp)
                    & (
                        observed.timestamp.dt.tz_convert("America/New_York").dt.date
                        == timestamp.tz_convert("America/New_York").date()
                    )
                ].sort_values("timestamp")
                valid = bool(
                    valid
                    and len(prior) > 0
                    and record.open == record.high == record.low == record.close
                    and record.close == prior.close.iloc[-1]
                    and record.volume == 0
                    and not record.is_genuine
                    and record.is_imputed
                    and record.observed_volume_unknown
                    and hour.hour_start_utc <= timestamp < hour.hour_end_utc
                    and record.available_at_utc == hour.hour_end_utc
                    and 1 <= record.gap_length_known_at_completion <= 5
                )
        if not valid:
            raise ValueError(
                "STOP_SOURCE_INTEGRITY: independent sampled-hour reconstruction failed"
            )
        rows.append(
            dict(
                source_month=month,
                ticker=hour.ticker,
                hour_id=hour.hour_id,
                source_rows=len(sel),
                proxy_rows=len(fill),
                observed_volume=volume,
                reconstruction_pass=True,
                raw_sha256=state["raw"]["sha256"],
            )
        )
    return rows


def verify_hourly_consistency(hourly: pd.DataFrame, canonical: pd.DataFrame) -> None:
    """Check every committed bin's accounting and stock-level observed-volume conservation."""
    n = hourly.expected_minutes
    genuine = hourly.genuine_minutes
    present = genuine > 0
    partition = genuine + hourly.ambiguous_minutes + hourly.absent_minutes + hourly.invalid_minutes
    prices = hourly[["open", "high", "low", "close"]]
    price_values = prices.to_numpy(dtype=float)
    valid_prices = (
        np.isfinite(price_values).all(axis=1)
        & (price_values > 0).all(axis=1)
        & (hourly.high.to_numpy() >= price_values.max(axis=1))
        & (hourly.low.to_numpy() <= price_values.min(axis=1))
    )
    checks = [
        not hourly.hour_id.duplicated().any(),
        partition.eq(n).all(),
        (hourly.filled_minutes + hourly.unfilled_minutes + genuine).eq(n).all(),
        hourly.filled_minutes.le(n - genuine).all(),
        hourly.bin_length_minutes.eq(n).all(),
        (hourly.hour_end_utc - hourly.hour_start_utc).eq(pd.to_timedelta(n, unit="min")).all(),
        hourly.completed_at_utc.eq(hourly.hour_end_utc).all(),
        hourly.is_stub.eq(n < 60).all(),
        hourly.volume_is_complete.eq(genuine == n).all(),
        hourly.observed_volume_lower_bound.eq(genuine < n).all(),
        hourly.loc[~present, "filled_minutes"].eq(0).all(),
        prices.loc[~present].isna().all().all(),
        valid_prices[present.to_numpy()].all(),
        hourly.observed_volume.ge(0).all(),
    ]
    observed = canonical.loc[canonical.is_rth].groupby("ticker").volume.sum()
    aggregated = hourly.groupby("ticker").observed_volume.sum()
    symbols = observed.index.union(aggregated.index)
    checks.append(
        np.allclose(
            observed.reindex(symbols, fill_value=0),
            aggregated.reindex(symbols, fill_value=0),
            rtol=1e-12,
            atol=1e-8,
        )
    )
    if not all(checks):
        raise ValueError("STOP_SOURCE_INTEGRITY: full-history hourly accounting failed")


def build_reports(out: Path, guard: Guard) -> None:
    """Read compact per-month coverage once; retain only small boolean common-hour matrices."""
    guard.check(50_000_000, "reserve_final_compact_reports")
    scope = json.loads((out / "active_scope.json").read_text())
    states = json.loads((out / scope["checkpoint"]).read_text())
    if scope["start_month"] != "2010-07" or any(m < "2010-07" for m in states):
        raise ValueError("STOP_IDENTITY: report includes pre-July2010 source months")
    if len(states) != scope["active_months"] or any(
        r["status"] != "HOURLY_DONE" for r in states.values()
    ):
        raise ValueError(
            "INTERRUPTED_RESUMABLE: all authorized months must finish before final coverage report"
        )
    monthly = []
    indices = []
    end_indices = []
    matrices = []
    manifests = []
    endpoints = {}
    reconstruction = []
    issue_counts = {}
    quality_counts = {}
    network = 0
    request_count = 0
    redirects = 0
    for month, state in sorted(states.items()):
        folder = out / "months" / month
        coverage = pd.read_csv(folder / "ticker_month_coverage.csv").rename(
            columns={
                "first_genuine_utc": "first_raw_source_utc",
                "last_genuine_utc": "last_raw_source_utc",
            }
        )
        monthly.append(coverage)
        for ref in [state["raw"], *state["qa"]["files"].values()]:
            if digest(Path(ref["path"])) != ref["sha256"]:
                raise ValueError("STOP_SOURCE_INTEGRITY: final committed-file hash mismatch")
        cols = [
            "ticker",
            "hour_start_utc",
            "hour_end_utc",
            "is_stub",
            "strict_candidate",
            "moderate_candidate",
            "broad_candidate",
            "quality_tier",
            "open_is_genuine",
            "close_is_genuine",
            "volume_is_complete",
            "filled_minutes",
            "genuine_minutes",
            "hour_id",
            "expected_minutes",
            "ambiguous_minutes",
            "absent_minutes",
            "invalid_minutes",
            "unfilled_minutes",
            "bin_length_minutes",
            "completed_at_utc",
            "observed_volume_lower_bound",
            "observed_volume",
            "open",
            "high",
            "low",
            "close",
        ]
        hourly = (
            pq.ParquetFile(state["qa"]["files"]["hourly_ohlcv"]["path"])
            .read(columns=cols)
            .to_pandas()
        )
        canonical = (
            pq.ParquetFile(state["qa"]["files"]["canonical_observed"]["path"])
            .read(columns=["ticker", "timestamp", "volume", "is_rth"])
            .to_pandas()
        )
        extrema = canonical.groupby("ticker").timestamp.agg(["min", "max"])
        coverage["first_genuine_utc"] = pd.to_datetime(
            coverage.ticker.map(extrema["min"]), utc=True
        )
        coverage["last_genuine_utc"] = pd.to_datetime(coverage.ticker.map(extrema["max"]), utc=True)
        verify_hourly_consistency(hourly, canonical)
        for tier, n in hourly.quality_tier.value_counts().items():
            quality_counts[str(tier)] = quality_counts.get(str(tier), 0) + int(n)
        for kind, n in state["qa"]["issue_counts"].items():
            issue_counts[kind] = issue_counts.get(kind, 0) + n
        full = hourly.loc[~hourly.is_stub]
        base = calendar_frame(month).drop_duplicates(["session_date_et", "hour_slot"])
        base = base.loc[(base.hour_end_utc - base.hour_start_utc) == pd.Timedelta(hours=1)]
        index = pd.DatetimeIndex(base.hour_start_utc)
        ends = pd.DatetimeIndex(base.hour_end_utc)
        matrix = np.zeros((len(index), len(SYMBOLS), 4), dtype=bool)
        for s, symbol in enumerate(SYMBOLS):
            own = full.loc[full.ticker == symbol]
            positions = index.get_indexer(pd.DatetimeIndex(own.hour_start_utc))
            if (positions < 0).any():
                raise ValueError("STOP_SOURCE_INTEGRITY: unexpected full-hour membership")
            matrix[positions, s, :3] = own[
                ["strict_candidate", "moderate_candidate", "broad_candidate"]
            ].to_numpy(dtype=bool)
            matrix[positions, s, 3] = own.genuine_minutes.to_numpy() > 0
            entry = endpoints.setdefault(
                symbol,
                dict(
                    ticker=symbol,
                    first_genuine_utc=None,
                    last_genuine_utc=None,
                    first_raw_source_utc=None,
                    last_raw_source_utc=None,
                    first_strict_hour=None,
                    last_strict_hour=None,
                    first_broad_hour=None,
                    last_broad_hour=None,
                    raw_rows=0,
                    identity="EXACT_SYMBOL_ONLY_HISTORICAL_ISSUER_UNVERIFIED",
                ),
            )
            record = coverage.loc[coverage.ticker == symbol].iloc[0]
            entry["raw_rows"] += int(record.raw_rows)
            if pd.notna(record.first_raw_source_utc):
                # Initial monthly receipts label raw source extrema as first_genuine.
                # Preserve them explicitly as raw extrema; final genuine endpoints use
                # only independently classified unique valid observations.
                entry["first_raw_source_utc"] = (
                    entry["first_raw_source_utc"] or record.first_raw_source_utc
                )
                entry["last_raw_source_utc"] = record.last_raw_source_utc
            genuine_times = canonical.loc[canonical.ticker == symbol, "timestamp"]
            if len(genuine_times):
                entry["first_genuine_utc"] = (
                    entry["first_genuine_utc"] or genuine_times.min().isoformat()
                )
                entry["last_genuine_utc"] = genuine_times.max().isoformat()
            for standard in ("strict", "broad"):
                available = own.loc[own[standard + "_candidate"]]
                if len(available):
                    entry["first_" + standard + "_hour"] = (
                        entry["first_" + standard + "_hour"]
                        or available.hour_start_utc.iloc[0].isoformat()
                    )
                    entry["last_" + standard + "_hour"] = available.hour_end_utc.iloc[
                        -1
                    ].isoformat()
        matrices.append(matrix)
        indices.append(index)
        end_indices.append(ends)
        events = []
        if (folder / "http_events.jsonl").exists():
            events = [
                json.loads(r) for r in (folder / "http_events.jsonl").read_text().splitlines()
            ]
        nbytes = sum(e["bytes"] for e in events)
        network += nbytes
        request_count += len(events)
        redirects += sum(e.get("redirects", 0) for e in events)
        manifests.append(
            dict(
                month=month,
                status="HOURLY_DONE",
                source_file=state["source"]["path"],
                upstream_bytes=state["source"]["bytes"],
                upstream_lfs_sha256=state["source"]["lfs_sha256"],
                source_body_bytes=nbytes,
                http_requests=len(events),
                raw_path=state["raw"]["path"],
                raw_rows=state["raw"]["rows"],
                raw_bytes=state["raw"]["bytes"],
                raw_sha256=state["raw"]["sha256"],
                strategy=state["raw"]["strategy"],
                full_source_hash_verified=state["raw"]["full_source_hash_verified"],
                canonical_rows=state["qa"]["canonical_rows"],
                proxy_rows=state["qa"]["proxy_rows"],
                hourly_rows=state["qa"]["hourly_rows"],
                minute_issue_rows=state["qa"]["minute_issue_rows"],
                qa_receipt=(folder / "qa_v2_receipt.json").as_posix(),
                derived_files=state["qa"]["files"],
                temporary_scratch_cleanup="VERIFIED_OR_PRIOR_SINGLE_COPY_REUSE",
            )
        )
        if month.endswith(("-03", "-11")):
            reconstruction.extend(reconstruct_month(state, month))
    index = pd.DatetimeIndex(indices[0].append(indices[1:]))
    ends = pd.DatetimeIndex(end_indices[0].append(end_indices[1:]))
    matrix = np.concatenate(matrices, axis=0)
    common = matrix.all(axis=1)
    coverage = pd.concat(monthly, ignore_index=True)
    coverage["year"] = coverage.source_month.str[:4].astype(int)
    coverage["unambiguous_rth_fraction"] = coverage.valid_minutes / coverage.expected_minutes
    coverage["observed_rth_fraction"] = coverage.observed_unique_minutes / coverage.expected_minutes
    coverage["imputed_slots_cap5"] = coverage.filled_minutes
    coverage.to_csv(out / "ticker_month_coverage.csv", index=False)
    yearly = (
        coverage.groupby(["ticker", "year"], sort=False)
        .agg(
            months_examined=("source_month", "size"),
            raw_rows=("raw_rows", "sum"),
            expected_minutes=("expected_minutes", "sum"),
            observed_unique_minutes=("observed_unique_minutes", "sum"),
            valid_minutes=("valid_minutes", "sum"),
            imputed_slots_cap5=("filled_minutes", "sum"),
            strict_hours=("strict_hours", "sum"),
            moderate_hours=("moderate_hours", "sum"),
            broad_hours=("broad_hours", "sum"),
        )
        .reset_index()
    )
    yearly["fraction_basis"] = "AUTHORIZED_MONTHS_EXCHANGE_GRID_NOT_A_FULL_YEAR_OR_IPO_CLAIM"
    yearly["partial_authorized_year"] = yearly.months_examined < 12
    yearly["unambiguous_rth_fraction"] = yearly.valid_minutes / yearly.expected_minutes
    yearly.to_csv(out / "ticker_year_coverage.csv", index=False)
    stock_summary = (
        coverage.groupby("ticker", sort=False)
        .agg(
            raw_rows=("raw_rows", "sum"),
            expected_minutes=("expected_minutes", "sum"),
            valid_minutes=("valid_minutes", "sum"),
            ambiguous_minutes=("ambiguous_minutes", "sum"),
            invalid_minutes=("invalid_minutes", "sum"),
            filled_minutes=("filled_minutes", "sum"),
            hourly_rows=("hourly_rows", "sum"),
            strict_hours=("strict_hours", "sum"),
            moderate_hours=("moderate_hours", "sum"),
        )
        .reset_index()
    )
    stock_summary["unambiguous_rth_fraction"] = (
        stock_summary.valid_minutes / stock_summary.expected_minutes
    )
    stock_summary["strict_hour_fraction"] = stock_summary.strict_hours / stock_summary.hourly_rows
    stock_summary["moderate_hour_fraction"] = (
        stock_summary.moderate_hours / stock_summary.hourly_rows
    )
    stock_summary.to_csv(out / "ticker_source_quality_summary.csv", index=False)
    pd.DataFrame(endpoints.values()).to_csv(out / "ticker_actual_endpoints.csv", index=False)
    pd.DataFrame(manifests).to_csv(out / "acquisition_manifest.csv", index=False)
    pd.DataFrame(reconstruction).to_csv(out / "independent_hour_reconstruction.csv", index=False)
    runs = []
    standard_rows = []
    for j, standard in enumerate(
        (
            "STRICT_GENUINE",
            "MODERATE_GENUINE_ENDPOINTS_CAP5",
            "BROAD_PARTIAL_ACTION_UNCERTAINTY_EXCLUDED",
            "BROAD_SOURCE_PRESENT_ACTION_FLAGS_RETAINED",
        )
    ):
        r = window_runs(index, ends, common[:, j], standard)
        runs.extend(r)
        available = np.flatnonzero(common[:, j])
        standard_rows.append(
            dict(
                standard=standard,
                all20_hours=int(common[:, j].sum()),
                expected_full_hours=len(index),
                longest_contiguous_run=r[0] if r else None,
                hull_first=index[available[0]].isoformat() if len(available) else None,
                hull_last=ends[available[-1]].isoformat() if len(available) else None,
                hull_is_not_continuity_proof=True,
            )
        )
    pd.DataFrame(runs).to_csv(out / "contiguous_all20_full_hour_runs.csv", index=False)
    candidates = []
    broad = np.flatnonzero(common[:, 3])
    if len(broad):
        first = pd.Timestamp(index[broad[0]])
        last = pd.Timestamp(ends[broad[-1]])
        local_last = last.tz_convert("America/New_York")
        proposals = [
            ("LATEST_15Y", local_last - pd.DateOffset(years=15), last),
            ("LATEST_14Y9M", local_last - pd.DateOffset(years=14, months=9), last),
            (
                "EARLIEST_COMMON_PLUS15Y",
                first,
                first.tz_convert("America/New_York") + pd.DateOffset(years=15),
            ),
        ]
        for label, a, b in proposals:
            # Snap outward to genuine calendar positions so a weekend/late-session
            # boundary cannot quietly turn a proposed15y interval into14y364d.
            floor_start = int(index.searchsorted(a, side="right")) - 1
            ceil_end = int(ends.searchsorted(b, side="left"))
            a = index[max(0, floor_start)]
            b = ends[min(len(ends) - 1, ceil_end)]
            mask = (index >= a) & (ends <= b) & (index >= first) & (ends <= last)
            positions = np.flatnonzero(mask)
            if not len(positions):
                continue
            actual_a = pd.Timestamp(index[positions[0]])
            actual_b = pd.Timestamp(ends[positions[-1]])
            record = dict(
                candidate=label,
                start=actual_a.isoformat(),
                end=actual_b.isoformat(),
                expected_full_hours=int(mask.sum()),
                duration_at_least15y=duration_pass(actual_a, actual_b, 15),
                duration_at_least14y9m=duration_pass(actual_a, actual_b, 14, 9),
                selected=False,
                note="Candidate interval with explicitly counted quality losses; not "
                "uninterrupted quality PASS",
            )
            for j, s in enumerate(("strict", "moderate", "broad", "source_present_flags_retained")):
                record[s + "_all20_hours"] = int(common[mask, j].sum())
                record[s + "_all20_fraction"] = float(common[mask, j].mean())
                record[s + "_all20_missing_hours"] = int((~common[mask, j]).sum())
            candidates.append(record)
    pd.DataFrame(candidates).to_csv(out / "historical_window_candidates.csv", index=False)
    replace_json(
        out / "coverage_standards.json",
        dict(
            standards=standard_rows,
            candidates=candidates,
            no_final_window_selected=True,
            expected_calendar_full_hour_positions=len(index),
            stock_order=list(SYMBOLS),
            modeling_authorized=False,
        ),
    )
    metadata_events = [
        json.loads(r) for r in (out / "metadata_http.jsonl").read_text().splitlines()
    ]
    active_body_bytes = network
    legacy_events = []
    for path in (out / "months").glob("*/http_events.jsonl"):
        if path.parent.name < scope["start_month"]:
            legacy_events.extend(json.loads(r) for r in path.read_text().splitlines())
    source_bytes = network + sum(e["bytes"] for e in metadata_events + legacy_events)
    review = source_profiles(out, states, guard)
    provider_comparison(out, states)
    for kind, n in review["supplemental_issue_counts"].items():
        issue_counts[kind] = issue_counts.get(kind, 0) + n
    replace_json(out / "source_review_summary.json", review)
    replace_json(
        out / "complete_acquisition_manifest.json",
        dict(
            status="COMPLETE_WITH_QUALITY_FLAGS",
            dataset=DATASET,
            revision=REVISION,
            namespace=NAMESPACE,
            months=len(states),
            monthly=manifests,
            raw_rows=sum(r["raw_rows"] for r in manifests),
            raw_bytes=sum(r["raw_bytes"] for r in manifests),
            hourly_rows=sum(r["hourly_rows"] for r in manifests),
            canonical_rows=sum(r["canonical_rows"] for r in manifests),
            synthetic_proxy_rows=sum(r["proxy_rows"] for r in manifests),
            source_body_bytes=source_bytes,
            active_scope_body_bytes=active_body_bytes,
            legacy_scope_body_bytes=sum(e["bytes"] for e in legacy_events),
            active_scope_start=scope["start_date"],
            legacy_scope_preserved_not_processed=True,
            source_requests=request_count + len(metadata_events) + len(legacy_events),
            active_scope_requests=request_count,
            redirects=redirects
            + sum(e.get("redirects", 0) for e in metadata_events + legacy_events),
            automatic_network_retries=0,
            quality_issue_counts=issue_counts,
            hour_quality_counts=quality_counts,
            training_ready=False,
            final_window_selected=False,
            ledger_pairs=32,
            at=now(),
        ),
    )
    lines = [
        "# Historical coverage and 15-year candidates",
        "",
        "All authorized July2010–March2026 months were examined for every exact symbol. No "
        "modeling interval is selected.",
        "The endpoint/coverage tables record exact-symbol source presence, not "
        "historical issuer or IPO certification. "
        "No retroactive ticker alias or synthetic pre-listing price was introduced. "
        "Source adjustment, dividends, "
        "publication history, rare-event and issuer identity uncertainties remain unresolved.",
        "",
        "Strict requires all genuine unique valid minutes, complete observed volume "
        "and genuine endpoints. "
        "Moderate allows bounded causal price proxies with genuine endpoints; volume "
        "remains flagged incomplete. "
        "Broad partial coverage excludes unresolved action flags; a separate source-present "
        "standard retains those flags and rare genuine moves. Neither is a finalized model mask. "
        "Empty bins never acquire artificial prices. Stubs remain separate and are "
        "excluded from this full-hour analysis.",
        "",
        "Contiguity means consecutive expected exchange full-hour positions, spanning "
        "calendar closures correctly. "
        "A hull between earliest/latest qualifying hours is not uninterrupted "
        "coverage. Candidate intervals below "
        "explicitly count holes and are proposals for human review, never training "
        "masks or quality certification.",
        "",
        "|Standard|All-20 full hours|Longest consecutive expected-hour run|Run calendar days|",
        "|---|---:|---:|---:|",
    ]
    for r in standard_rows:
        run = r["longest_contiguous_run"] or {}
        lines.append(
            f"|{r['standard']}|{r['all20_hours']:,}|{run.get('common_full_hours', 0):,}|"
            f"{run.get('calendar_days', 0):.2f}|"
        )
    lines.extend(
        [
            "",
            "## Unselected candidate intervals",
            "",
            "See historical_window_candidates.csv for exact DateOffset duration and "
            "all-20 retained/lost hour counts.",
        ]
    )
    for r in candidates:
        lines.append("\n- " + json.dumps(r, sort_keys=True))
    lines.extend(
        [
            "",
            "### Lowest minute completeness across the authorized history",
            "",
            "This is a source-quality comparison, with all 20 names retained. Fractions use "
            "the authorized exchange grid, not an inferred issuer listing history. Hour fractions "
            "in this table include separately identified closing stubs.",
            "",
            "|Stock|Unique valid RTH minutes|Strict hours/stubs|"
            "Moderate hours/stubs|Proxy minutes|",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for r in stock_summary.sort_values("unambiguous_rth_fraction").head(5).itertuples():
        lines.append(
            f"|{r.ticker}|{r.unambiguous_rth_fraction:.4%}|{r.strict_hour_fraction:.4%}|"
            f"{r.moderate_hour_fraction:.4%}|{r.filled_minutes:,}|"
        )
    lines.extend(
        [
            "",
            "### Highest-risk stock-years by source minute completeness",
            "",
            "|Stock|Year|Months examined|Unique valid RTH fraction|",
            "|---|---:|---:|---:|",
        ]
    )
    for r in yearly.sort_values("unambiguous_rth_fraction").head(10).itertuples():
        lines.append(f"|{r.ticker}|{r.year}|{r.months_examined}|{r.unambiguous_rth_fraction:.4%}|")
    lines.extend(
        [
            "",
            "For human review, use the latest-15y candidate as the initial comparison with the "
            "latest-14y9m and earliest-common candidates; compare retained genuine endpoints, "
            "unknown volume, quality hotspots and action evidence before selecting anything. "
            "No candidate is certified as uninterrupted 15-year usable coverage or activated "
            "for modeling. Do not replace a stock or relax a mask automatically.",
        ]
    )
    lines.extend(
        [
            "",
            "## Risk review",
            "",
            "Use ticker_actual_endpoints.csv, ticker_year_coverage.csv and the "
            "persistent issue register. "
            "Long absence is not automatically an IPO, halt or vendor failure. "
            "Exact-symbol series can predate the present "
            "issuer; historical identity must be verified before later modeling. No "
            "source prices, bar definitions, "
            "split factors, scaler/epsilon or chronology can be transferred from old "
            "Twelve Data/Alpaca pipelines.",
        ]
    )
    (out / "historical_coverage_and_15y_candidates.md").write_text("\n".join(lines) + "\n")
    (out / "hourly_qa_report.md").write_text(
        "# Hourly QA — COMPLETE_WITH_QUALITY_FLAGS\n\n"
        f"{sum(r['hourly_rows'] for r in manifests):,} hourly/stub rows. "
        "Every committed bin passed count partitions, timing, OHLC invariants, missing-bin "
        "and stock-month observed-volume conservation checks. Bins follow exact session anchors. "
        f"{len(reconstruction)} independent raw reconstructions passed across March/November "
        "months, including strict, proxy, stub and action-flagged examples when available. "
        "See independent_hour_reconstruction.csv. Genuine observations preserve "
        "original OHLCV; exact duplicates "
        "count once, conflicts/invalids contribute no volume. Empty bins stay "
        "missing. Fill proxies carry only "
        "an earlier same-session genuine close, zero placeholder volume and unknown-volume flag. "
        "They become available at completed-hour time. Later-hour observations cannot "
        "revise an earlier hour. "
        "A short trailing proxy can precede a later-discovered longer outage; its "
        "endpoint remains nongenuine, "
        "and longer known gaps are not filled. Two-versus-five-minute sensitivity is "
        "stored per hour. "
        "No historical publication-time or complete corporate-action certification is implied.\n\n"
        "Physical datasets are in the derived qa_v2 tree. CANONICAL_OBSERVED plus the separate "
        "fill_proxies_cap5 delta form the DERIVED_FILLED logical view; this avoids a "
        "duplicate numerical mirror. "
        "raw_record_classification labels RTH/extended and source quality without modifying RAW. "
        "hourly_ohlcv also supplies ticker_session_hour_coverage; a manifest is "
        "supplied for this projection. "
        "Initial v1 QA trial files are retained and superseded by qa_v2 receipts.\n"
    )
    replace_json(
        out / "ticker_session_hour_coverage_manifest.json",
        dict(
            physical_root=(DERIVED / "qa_v2/hourly_ohlcv").as_posix(),
            physical_root_contains_legacy_files_do_not_glob=True,
            active_start_date=scope["start_date"],
            active_files=[r["derived_files"]["hourly_ohlcv"] for r in manifests],
            projection=[
                "ticker",
                "session_date_et",
                "hour_start_utc",
                "expected_minutes",
                "genuine_minutes",
                "ambiguous_minutes",
                "absent_minutes",
                "filled_minutes",
                "longest_gap_minutes",
                "unfilled_minutes",
                "quality_tier",
            ],
            receipt_manifest="complete_acquisition_manifest.json",
        ),
    )
    (out / "historical_data_readiness.md").write_text(
        "# Historical data readiness\n\n**COMPLETE_WITH_QUALITY_FLAGS; NOT TRAINING_READY.**\n\n"
        f"All {len(states)} pinned months examined; "
        f"{sum(r['raw_rows'] for r in manifests):,} raw rows retained. "
        "Raw conflicts, invalids, absences, synthetic proxies and incomplete observed "
        "volume remain visible. "
        "The earlier STOP_RIGHTS and 018C STOP_QUALITY records remain intact. "
        "User-reported maintainer permission "
        "covers private research operationally; it is not independent licensing or "
        "redistribution verification.\n\n"
        "No final 15-year window, cohort change, feature/target definition, fitted "
        "scaler/epsilon, split selection, "
        "prediction, training, backtest or model comparison was performed. Ledger "
        "32/200 unchanged. "
        "Old held-out outcomes remain protected for modeling; only the new raw source was audited. "
        "Human review must decide window/stock identity/quality/action policies "
        "before a new source-adapted "
        "feature/target package and separately authorized C0/T2 training.\n"
    )
    guard.check(0, "final_report_completion")
    replace_json(
        out / "run_status.json",
        dict(
            status="COMPLETE_WITH_QUALITY_FLAGS",
            months=len(states),
            ledger=32,
            training_ready=False,
            final_window_selected=False,
            source_body_bytes=source_bytes,
            at=now(),
        ),
    )
    print(
        json.dumps(
            dict(
                status="COMPLETE_WITH_QUALITY_FLAGS",
                months=len(states),
                source_body_bytes=source_bytes,
                raw_rows=sum(r["raw_rows"] for r in manifests),
            )
        ),
        flush=True,
    )
