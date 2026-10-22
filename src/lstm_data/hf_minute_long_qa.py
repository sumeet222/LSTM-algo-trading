"""Deterministic minute reconciliation and completed-hour QA; never builds model inputs."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .hf20_source import SYMBOLS
from .hf_minute_boundary import COLUMNS, longest_run, session_grid
from .hf_minute_boundary_io import REVISION

PRICE = ["open", "high", "low", "close"]
ISSUE_COLUMNS = [
    "source_revision",
    "ticker",
    "session_date_et",
    "timestamp_utc",
    "issue_type",
    "severity",
    "source_month",
    "original_record_ids_or_hashes",
    "raw_values_or_link",
    "observed_row_count",
    "resolution_action",
    "derived_is_synthetic",
    "impacted_hour_id",
    "related_issue_id",
    "issue_id",
]


@dataclass
class MonthQA:
    canonical: pd.DataFrame
    classification: pd.DataFrame
    proxies: pd.DataFrame
    minute_issues: pd.DataFrame
    hourly: pd.DataFrame
    hourly_issues: pd.DataFrame
    coverage: pd.DataFrame
    sessions: pd.DataFrame
    sensitivity: pd.DataFrame
    last_observed: dict


def valid_values(frame: pd.DataFrame) -> np.ndarray:
    """Retain rare/extreme genuine candles; reject only demonstrable scalar/OHLC defects."""
    a = frame[PRICE + ["volume"]].to_numpy(dtype=float)
    return (
        np.isfinite(a).all(axis=1)
        & (a[:, :4] > 0).all(axis=1)
        & (a[:, 4] >= 0)
        & (a[:, 1] >= a[:, :4].max(axis=1))
        & (a[:, 2] <= a[:, :4].min(axis=1))
    )


def calendar_frame(month: str) -> pd.DataFrame:
    """Minute-start grid and exact session-anchored full-hour/stub membership."""
    sessions, _ = session_grid(month)
    frames = []
    for day in sessions:
        grid = pd.date_range(day.open, day.close, freq="min", inclusive="left").as_unit("ns")
        offset = np.arange(len(grid))
        slot = offset // 60
        starts = pd.to_datetime(day.open.value + slot * 60 * 60 * 1_000_000_000, utc=True)
        ends = pd.to_datetime(
            np.minimum(
                starts.to_numpy(dtype="datetime64[ns]").astype(np.int64) + 3600 * 1_000_000_000,
                day.close.value,
            ),
            utc=True,
        )
        date = str(day.day.date())
        frames.append(
            pd.DataFrame(
                dict(
                    timestamp=grid,
                    session_date_et=date,
                    minute_of_session=offset,
                    hour_slot=slot,
                    hour_start_utc=starts,
                    hour_end_utc=ends,
                )
            )
        )
    return pd.concat(frames, ignore_index=True)


def bounded_hour_proxies(
    close: np.ndarray,
    cap: int,
    prior_close: float | None,
    prior_gap: int = 0,
    blocked: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Price proxies use only a bin's past at completed_at, never later-hour observations.

    A completed bin can reject a >cap run already known within that bin. A short trailing
    run remains a flagged endpoint proxy even if a later bin reveals a longer outage;
    later information cannot retroactively change this completed-hour representation.
    No-observation bins, session opens and action-uncertain bins receive no proxies.
    """
    result = np.full(len(close), np.nan)
    length = np.zeros(len(close), dtype=np.int16)
    genuine = np.isfinite(close)
    if blocked or not genuine.any():
        return result, length
    edges = np.diff(np.r_[False, ~genuine, False].astype(np.int8))
    for start, end in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1), strict=True):
        age = end - start + (prior_gap if start == 0 else 0)
        previous = prior_close if start == 0 else float(close[start - 1])
        if age <= cap and previous is not None and np.isfinite(previous):
            result[start:end] = previous
            length[start:end] = age
    return result, length


def issue_frame(
    frame: pd.DataFrame,
    month: str,
    kind: str,
    severity: str,
    raw_link: str,
    action: str = "FLAG_UNRESOLVED",
    synthetic: bool = False,
) -> pd.DataFrame:
    """Stable source-linked issue records; absent rows use expected UTC minute starts."""
    n = len(frame)
    result = pd.DataFrame(index=np.arange(n))
    result["source_revision"] = REVISION
    result["ticker"] = frame["ticker"].to_numpy()
    ts = pd.DatetimeIndex(frame["timestamp"])
    result["timestamp_utc"] = ts
    result["session_date_et"] = (
        ts.tz_convert("America/New_York")
        .tz_localize(None)
        .to_numpy(dtype="datetime64[D]")
        .astype(str)
    )
    result["issue_type"] = kind
    result["severity"] = severity
    result["source_month"] = month
    result["original_record_ids_or_hashes"] = (
        frame["source_row"].astype(str).to_numpy() if "source_row" in frame else ""
    )
    result["raw_values_or_link"] = raw_link
    result["observed_row_count"] = (
        frame["raw_multiplicity"].fillna(0).astype(int).to_numpy()
        if "raw_multiplicity" in frame
        else (0 if kind == "ABSENT_MINUTE" else 1)
    )
    result["resolution_action"] = action
    result["derived_is_synthetic"] = synthetic
    result["impacted_hour_id"] = (
        frame["hour_id"].fillna("").to_numpy() if "hour_id" in frame else ""
    )
    result["related_issue_id"] = result["impacted_hour_id"]
    result["issue_id"] = (
        month
        + ":"
        + result.ticker.astype(str)
        + ":"
        + pd.Series(ts.to_numpy(dtype="datetime64[ns]").astype(np.int64) // 60_000_000_000).astype(
            str
        )
        + ":"
        + kind
    )
    return result[ISSUE_COLUMNS]


def process_month(
    raw: pd.DataFrame, month: str, raw_sha: str, raw_link: str, previous: dict | None = None
) -> MonthQA:
    """RAW -> unique valid observed + causal proxy delta -> quality-flagged hourly.

    Quality masks are source-audit evidence, not finalized model eligibility. No source
    row is changed, and volume from ambiguous/invalid minutes is never counted.
    """
    if month < "2010-07":
        raise ValueError("STOP_IDENTITY: pre-July2010 processing prohibited by human amendment")
    previous = {} if previous is None else previous
    frame = raw.copy().reset_index(drop=True)
    frame["timestamp"] = pd.to_datetime(frame.timestamp, utc=True)
    if "source_row" not in frame:
        frame["source_row"] = np.arange(len(frame))
    key = ["ticker", "timestamp"]
    grid = calendar_frame(month)
    expected_idx = pd.DatetimeIndex(grid.timestamp)
    aligned = frame.timestamp.notna() & (frame.timestamp == frame.timestamp.dt.floor("min"))
    numeric = valid_values(frame)
    good = aligned.to_numpy() & numeric
    local_month = (
        frame.timestamp.dt.tz_convert("America/New_York")
        .dt.tz_localize(None)
        .to_numpy(dtype="datetime64[M]")
        .astype(str)
    )
    right_month = local_month == month
    good &= right_month
    dedup = frame.drop_duplicates(COLUMNS).copy()
    multiplicity = frame.groupby(key, dropna=False, sort=False).size().rename("raw_multiplicity")
    versions = dedup.groupby(key, dropna=False, sort=False).size().rename("versions")
    frame = frame.join(multiplicity, on=key).join(versions, on=key)
    conflicts = (frame.versions > 1).to_numpy()
    is_rth = frame.timestamp.isin(expected_idx).to_numpy()
    classification = pd.DataFrame(
        dict(
            source_row=frame.source_row,
            is_rth=is_rth,
            is_extended_or_noncalendar=~is_rth,
            classification=np.select(
                [~good, conflicts, frame.raw_multiplicity.to_numpy() > 1],
                ["INVALID", "AMBIGUOUS_CONFLICT", "EXACT_DUPLICATE"],
                default="UNIQUE",
            ),
        )
    )
    canonical = frame.loc[good & ~conflicts].drop_duplicates(key).sort_values(key).copy()
    canonical["is_rth"] = canonical.timestamp.isin(expected_idx)
    canonical["is_genuine"] = True
    canonical["is_imputed"] = False
    canonical["source_revision"] = REVISION
    canonical["raw_linkage_hash"] = raw_sha
    # Only classification fields + genuine original values, no duplicate numerical store.
    canonical = canonical[
        COLUMNS
        + [
            "source_row",
            "raw_multiplicity",
            "is_rth",
            "is_genuine",
            "is_imputed",
            "source_revision",
            "raw_linkage_hash",
        ]
    ]
    issue_parts = []
    proxy_issue_slices = []
    proxy_cursor = 0
    for mask, kind, severity, action in [
        (~good, "INVALID_RAW_BAR", "ERROR", "EXCLUDE_FROM_CANONICAL"),
        (conflicts, "CONFLICTING_DUPLICATE", "ERROR", "EXCLUDE_ALL_VERSIONS"),
        (
            (frame.raw_multiplicity.to_numpy() > 1) & ~conflicts,
            "EXACT_DUPLICATE",
            "INFO",
            "COLLAPSE_IDENTICAL_ONCE",
        ),
    ]:
        if mask.any():
            issue_parts.append(
                issue_frame(frame.loc[mask], month, kind, severity, raw_link, action)
            )
    hourly_rows = []
    proxy_parts = []
    coverage = []
    session_rows = []
    sensitivity = []
    last = {}
    for symbol_index, symbol in enumerate(SYMBOLS):
        stock = frame.loc[frame.ticker == symbol]
        observed = canonical.loc[(canonical.ticker == symbol) & canonical.is_rth].copy()
        if stock.empty:
            absent_symbol = pd.DataFrame(
                dict(ticker=[symbol], timestamp=pd.DatetimeIndex([pd.NaT], tz="UTC"))
            )
            issue_parts.append(
                issue_frame(
                    absent_symbol,
                    month,
                    "NO_EXACT_SYMBOL_SOURCE_ROWS",
                    "COVERAGE_UNKNOWN",
                    raw_link,
                    "NO_ALIAS_NO_PREIPO_INFERENCE",
                )
            )
            coverage.append(
                dict(
                    ticker=symbol,
                    symbol_index=symbol_index,
                    source_month=month,
                    status="EXAMINED_NO_EXACT_SYMBOL_ROWS",
                    raw_rows=0,
                    expected_minutes=len(grid),
                    observed_unique_minutes=0,
                    valid_minutes=0,
                    ambiguous_minutes=0,
                    invalid_minutes=0,
                    filled_minutes=0,
                    first_genuine_utc=None,
                    last_genuine_utc=None,
                    hourly_rows=0,
                    strict_hours=0,
                    moderate_hours=0,
                    broad_hours=0,
                    no_preIPO_inference=True,
                )
            )
            # Coverage summary explicitly records zero; never fabricate pre-IPO minute prices.
            continue
        joined = grid.merge(
            observed.drop(columns=["ticker"]), on="timestamp", how="left", validate="one_to_one"
        )
        joined["ticker"] = symbol
        joined["hour_id"] = (
            symbol + ":" + joined.session_date_et + ":" + joined.hour_slot.astype(str)
        )
        raw_keys = stock.drop_duplicates("timestamp").set_index("timestamp")
        joined["raw_multiplicity"] = (
            joined.timestamp.map(raw_keys.raw_multiplicity).fillna(0).astype(int)
        )
        joined["ambiguous"] = joined.timestamp.map(raw_keys.versions).fillna(0).to_numpy() > 1
        joined["observed_any"] = joined.timestamp.isin(pd.DatetimeIndex(stock.timestamp))
        joined["valid"] = joined.close.notna()
        joined["absent"] = ~joined.observed_any
        joined["invalid"] = joined.observed_any & ~joined.valid & ~joined.ambiguous
        # Adjacent genuine observations may span overnight/month boundaries. Flag, never adjust.
        action_times = []
        if len(observed):
            closes = observed.close.to_numpy()
            prior = previous.get(symbol)
            first_return = abs(np.log(closes[0] / prior["close"])) if prior else 0.0
            changes = np.r_[first_return, np.abs(np.log(closes[1:] / closes[:-1]))]
            jumps = observed.loc[changes > np.log(1.25)].copy()
            if len(jumps):
                action_times = jumps.timestamp.tolist()
                issue_parts.append(
                    issue_frame(
                        jumps,
                        month,
                        "ACTION_OR_SCALE_JUMP_OVER25PCT",
                        "REVIEW",
                        raw_link,
                        "PRESERVE_GENUINE_NO_ADJUSTMENT",
                    )
                )
            tail = observed.iloc[-1]
            last[symbol] = dict(timestamp=tail.timestamp.isoformat(), close=float(tail.close))
        elif symbol in previous:
            last[symbol] = previous[symbol]
        joined["action"] = joined.timestamp.isin(action_times)
        zero = observed.loc[observed.volume == 0]
        if len(zero):
            issue_parts.append(
                issue_frame(
                    zero,
                    month,
                    "GENUINE_ZERO_VOLUME",
                    "REVIEW",
                    raw_link,
                    "PRESERVE_GENUINE_NOT_NO_TRADE_CERTIFICATION",
                )
            )
        if len(observed) > 1:
            same = observed[PRICE].eq(observed[PRICE].shift()).all(axis=1).to_numpy()
            consecutive = observed.timestamp.diff().eq(pd.Timedelta(minutes=1)).to_numpy()
            stale = same & consecutive & (observed.volume.to_numpy() == 0)
            ages = np.zeros(len(stale), dtype=int)
            for j in range(len(stale)):
                ages[j] = (ages[j - 1] + 1 if j else 1) if stale[j] else 0
            markers = observed.loc[ages == 30]
            if len(markers):
                issue_parts.append(
                    issue_frame(
                        markers,
                        month,
                        "STALE_ZERO_VOLUME_RUN30",
                        "REVIEW",
                        raw_link,
                        "PRESERVE_PENDING_SOURCE_EVIDENCE",
                    )
                )
        # Presence outside first/last source day is coverage metadata, not imputed pre/post history.
        first_day = stock.timestamp.min().tz_convert("America/New_York").date()
        last_day = stock.timestamp.max().tz_convert("America/New_York").date()
        within_span = (joined.session_date_et >= str(first_day)) & (
            joined.session_date_et <= str(last_day)
        )
        missing = joined.loc[joined.absent & within_span]
        if len(missing):
            issue_parts.append(
                issue_frame(
                    missing,
                    month,
                    "ABSENT_MINUTE",
                    "WARNING",
                    raw_link,
                    "UNRESOLVED_TRADE_VS_PROVIDER_ABSENCE",
                )
            )
        for date, day in joined.groupby("session_date_et", sort=False):
            prior_close = None
            prior_gap = 0
            for _, hour in day.groupby("hour_slot", sort=False):
                close = hour.close.to_numpy(dtype=float)
                valid = np.isfinite(close)
                action = bool(hour.action.any())
                fills, gap_lengths = bounded_hour_proxies(close, 5, prior_close, prior_gap, action)
                fill2, _ = bounded_hour_proxies(close, 2, prior_close, prior_gap, action)
                fill_mask = np.isfinite(fills)
                combined = hour[PRICE].to_numpy(dtype=float).copy()
                combined[fill_mask] = fills[fill_mask, None]
                have = np.isfinite(combined[:, 3])
                count = len(hour)
                genuine = int(valid.sum())
                filled = int(fill_mask.sum())
                missing_run = longest_run(~valid)
                if not valid[0]:
                    leading = int(np.flatnonzero(valid)[0]) if valid.any() else count
                    missing_run = max(missing_run, prior_gap + leading)
                opened = bool(valid[0])
                closed = bool(valid[-1])
                strict = genuine == count and not action
                moderate = bool(
                    have.all() and opened and closed and missing_run <= 5 and not action
                )
                broad = bool(genuine > 0 and not action)
                start = pd.Timestamp(hour.hour_start_utc.iloc[0])
                end = pd.Timestamp(hour.hour_end_utc.iloc[0])
                hour_id = str(hour.hour_id.iloc[0])
                reasons = []
                if not opened:
                    reasons.append("OPEN_NOT_GENUINE")
                if not closed:
                    reasons.append("CLOSE_NOT_GENUINE")
                if hour.ambiguous.any():
                    reasons.append("AMBIGUOUS_MINUTES")
                if hour.absent.any():
                    reasons.append("ABSENT_MINUTES")
                if hour.invalid.any():
                    reasons.append("INVALID_MINUTES")
                if filled:
                    reasons.append("PRICE_PROXY_VOLUME_UNKNOWN")
                if action:
                    reasons.append("ACTION_UNCERTAINTY")
                if not genuine:
                    reasons.append("NO_GENUINE_MINUTE")
                tier = (
                    "STRICT_GENUINE"
                    if strict
                    else "MODERATE_ENDPOINTS_GENUINE"
                    if moderate
                    else ("ACTION_UNCERTAIN" if action else "PARTIAL" if genuine else "MISSING")
                )
                row = dict(
                    ticker=symbol,
                    source_month=month,
                    source_revision=REVISION,
                    session_date_et=str(date),
                    hour_id=hour_id,
                    hour_start_utc=start,
                    hour_end_utc=end,
                    completed_at_utc=end,
                    bin_length_minutes=count,
                    expected_minutes=count,
                    is_stub=count < 60,
                    genuine_minutes=genuine,
                    exact_duplicate_minutes=int(((hour.raw_multiplicity > 1) & hour.valid).sum()),
                    ambiguous_minutes=int(hour.ambiguous.sum()),
                    absent_minutes=int(hour.absent.sum()),
                    invalid_minutes=int(hour.invalid.sum()),
                    filled_minutes=filled,
                    unfilled_minutes=count - genuine - filled,
                    longest_gap_minutes=missing_run,
                    open=float(combined[have, 0][0]) if have.any() else np.nan,
                    high=float(np.nanmax(combined[:, 1])) if have.any() else np.nan,
                    low=float(np.nanmin(combined[:, 2])) if have.any() else np.nan,
                    close=float(combined[have, 3][-1]) if have.any() else np.nan,
                    observed_volume=float(hour.volume.fillna(0).sum()),
                    volume=float(hour.volume.fillna(0).sum()),
                    open_is_genuine=opened,
                    close_is_genuine=closed,
                    first_observed_open=not opened,
                    opening_minutes_missing=not opened,
                    all_ohlc_genuine_or_complete=genuine == count,
                    volume_is_complete=genuine == count,
                    observed_volume_lower_bound=genuine < count,
                    partial_hour=genuine < count,
                    zero_observed_hours=genuine == 0,
                    raw_linkage_hash=raw_sha,
                    quality_tier=tier,
                    action_uncertainty=action,
                    issue_ids=hour_id if reasons else "",
                    issue_reasons="|".join(reasons),
                    strict_candidate=strict,
                    moderate_candidate=moderate,
                    broad_candidate=broad,
                    training_eligibility_suggestion="REVIEW_ONLY_NO_MODEL_MASK",
                )
                hourly_rows.append(row)
                if filled:
                    proxy = hour.loc[
                        fill_mask,
                        ["timestamp", "ticker", "session_date_et", "hour_id", "raw_multiplicity"],
                    ].copy()
                    proxy["open"] = fills[fill_mask]
                    proxy["high"] = fills[fill_mask]
                    proxy["low"] = fills[fill_mask]
                    proxy["close"] = fills[fill_mask]
                    proxy["volume"] = 0.0
                    proxy["is_genuine"] = False
                    proxy["is_imputed"] = True
                    proxy["observed_volume_unknown"] = True
                    proxy["fill_reason"] = np.where(
                        hour.ambiguous.to_numpy()[fill_mask],
                        "AMBIGUOUS_CONFLICT",
                        np.where(hour.invalid.to_numpy()[fill_mask], "INVALID", "ABSENT"),
                    )
                    proxy["gap_length_known_at_completion"] = gap_lengths[fill_mask]
                    proxy["available_at_utc"] = end
                    proxy["source_revision"] = REVISION
                    proxy["raw_linkage_hash"] = raw_sha
                    proxy_parts.append(proxy)
                    proxy_issue_slices.append(
                        (len(issue_parts), proxy_cursor, proxy_cursor + filled)
                    )
                    proxy_cursor += filled
                    issue_parts.append(pd.DataFrame())
                sensitivity.append(
                    dict(
                        ticker=symbol,
                        source_month=month,
                        hour_id=hour_id,
                        filled_cap2=int(np.isfinite(fill2).sum()),
                        filled_cap5=filled,
                        complete_cap2=bool((valid | np.isfinite(fill2)).all()),
                        complete_cap5=bool(have.all()),
                        genuine_endpoints=opened and closed,
                    )
                )
                if valid.any():
                    last_index = int(np.flatnonzero(valid)[-1])
                    prior_close = float(close[last_index])
                    prior_gap = count - 1 - last_index
                else:
                    prior_gap += count
            values = day.valid.to_numpy()
            session_rows.append(
                dict(
                    ticker=symbol,
                    source_month=month,
                    session_date_et=str(date),
                    expected_minutes=len(day),
                    observed_minutes=int(day.observed_any.sum()),
                    valid_minutes=int(values.sum()),
                    ambiguous_minutes=int(day.ambiguous.sum()),
                    absent_minutes=int(day.absent.sum()),
                    longest_missing_run=longest_run(~values),
                    opening_minute_genuine=bool(values[0]),
                    closing_minute_genuine=bool(values[-1]),
                    filled_minutes=sum(
                        r["filled_minutes"]
                        for r in hourly_rows
                        if r["ticker"] == symbol and r["session_date_et"] == str(date)
                    ),
                    unusable_strict_hours=sum(
                        not r["strict_candidate"]
                        for r in hourly_rows
                        if r["ticker"] == symbol and r["session_date_et"] == str(date)
                    ),
                )
            )
        own_hours = [r for r in hourly_rows if r["ticker"] == symbol]
        coverage.append(
            dict(
                ticker=symbol,
                symbol_index=symbol_index,
                source_month=month,
                status="EXAMINED_WITH_SOURCE_QUALITY_FLAGS",
                raw_rows=len(stock),
                expected_minutes=len(grid),
                observed_unique_minutes=int(joined.observed_any.sum()),
                valid_minutes=int(joined.valid.sum()),
                ambiguous_minutes=int(joined.ambiguous.sum()),
                invalid_minutes=int(joined.invalid.sum()),
                filled_minutes=sum(r["filled_minutes"] for r in own_hours),
                first_genuine_utc=stock.timestamp.min().isoformat(),
                last_genuine_utc=stock.timestamp.max().isoformat(),
                hourly_rows=len(own_hours),
                strict_hours=sum(r["strict_candidate"] for r in own_hours),
                moderate_hours=sum(r["moderate_candidate"] for r in own_hours),
                broad_hours=sum(r["broad_candidate"] for r in own_hours),
                raw_conflicting_rows=int((stock.versions > 1).sum()),
                raw_exact_duplicate_rows=int(
                    ((stock.raw_multiplicity > 1) & (stock.versions == 1)).sum()
                ),
                invalid_raw_rows=int((~good[stock.index]).sum()),
                no_preIPO_inference=True,
            )
        )
    hourly = pd.DataFrame(hourly_rows)
    proxies = pd.concat(proxy_parts, ignore_index=True) if proxy_parts else pd.DataFrame()
    if len(proxies):
        proxy_issues = issue_frame(
            proxies,
            month,
            "CAUSAL_PRICE_PROXY",
            "PROXY",
            raw_link,
            "DERIVED_ONLY_ZERO_VOLUME_PLACEHOLDER",
            True,
        )
        for position, start, end in proxy_issue_slices:
            issue_parts[position] = proxy_issues.iloc[start:end]
    issues = (
        pd.concat(issue_parts, ignore_index=True)
        if issue_parts
        else pd.DataFrame(columns=ISSUE_COLUMNS)
    )
    if len(frame):
        live = frame.loc[frame.timestamp.isin(expected_idx)].drop_duplicates(
            ["ticker", "timestamp"]
        )
        counts = live.groupby("timestamp").ticker.nunique()
        present_count = frame.ticker.nunique()
        synchronous = grid.loc[
            (grid.timestamp >= frame.timestamp.min()) & (grid.timestamp <= frame.timestamp.max())
        ].copy()
        synchronous["n_present"] = synchronous.timestamp.map(counts).fillna(0).astype(int)
        synchronous = synchronous.loc[synchronous.n_present < max(1, present_count // 2)]
        if len(synchronous):
            synchronous["ticker"] = "OBSERVED_COHORT"
            cohort = issue_frame(
                synchronous,
                month,
                "MANY_STOCKS_SYNCHRONOUS_GAP",
                "REVIEW",
                raw_link,
                "FLAG_NOT_PROOF_OF_MARKET_OUTAGE",
            )
            cohort["observed_row_count"] = synchronous.n_present.to_numpy()
            issues = pd.concat([issues, cohort], ignore_index=True)
    if len(issues):
        issues["timestamp_utc"] = pd.to_datetime(issues.timestamp_utc, utc=True)
        # Raw issues gain hour linkage when they correspond to actual RTH slots.
        if len(hourly):
            mapgrid = grid[["timestamp", "session_date_et", "hour_slot"]].copy()
            mapped = issues.merge(
                mapgrid, left_on="timestamp_utc", right_on="timestamp", how="left"
            )
            mapped_ids = (
                mapped.ticker.astype(str)
                + ":"
                + mapped["session_date_et_y"].astype(str)
                + ":"
                + mapped.hour_slot.fillna(-1).astype(int).astype(str)
            )
            issues["impacted_hour_id"] = np.where(mapped.hour_slot.notna(), mapped_ids, "")
            issues["related_issue_id"] = issues.impacted_hour_id
        issues["timestamp_utc"] = pd.to_datetime(issues.timestamp_utc, utc=True)
    hour_issues = hourly.loc[hourly.issue_reasons != ""].copy() if len(hourly) else pd.DataFrame()
    return MonthQA(
        canonical.reset_index(drop=True),
        classification,
        proxies,
        issues,
        hourly,
        hour_issues,
        pd.DataFrame(coverage),
        pd.DataFrame(session_rows),
        pd.DataFrame(sensitivity),
        last,
    )
