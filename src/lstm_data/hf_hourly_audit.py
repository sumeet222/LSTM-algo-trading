"""Hourly source census against actual XNYS sessions; no labels, features or fitting."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .calendar import schedule, session_grid
from .config import write_json
from .hf_hourly_source import verify_cached

CORE = ("datetime", "symbol", "timeframe", "open", "high", "low", "close", "close_adj", "volume")
ET = "America/New_York"


def require_schema(schema: pa.Schema) -> None:
    if not set(CORE) <= set(schema.names):
        raise ValueError("REQUIRED_SOURCE_COLUMNS_MISSING")
    timestamp = schema.field("datetime").type
    if not pa.types.is_timestamp(timestamp) or getattr(timestamp, "tz", None) != ET:
        raise ValueError("EXPLICIT_AMERICA_NEW_YORK_START_CLOCK_REQUIRED")
    for name in CORE[3:]:
        field = schema.field(name).type
        if not (pa.types.is_floating(field) or pa.types.is_integer(field)):
            raise ValueError("NUMERIC_OHLCV_REQUIRED:" + name)


def quality_flags(frame: pd.DataFrame) -> pd.DataFrame:
    """No coercion/repair. Adjusted close is audited separately from native candle bounds."""
    prices = frame[["open", "high", "low", "close"]]
    numeric = frame[list(CORE[3:])].to_numpy(dtype=float)
    flags = pd.DataFrame(index=frame.index)
    flags["null_key"] = frame[["datetime", "symbol", "timeframe"]].isna().any(axis=1)
    flags["null_OHLCV"] = frame[["open", "high", "low", "close", "volume"]].isna().any(axis=1)
    flags["nonfinite"] = ~np.isfinite(numeric).all(axis=1)
    flags["nonpositive_price"] = (prices <= 0).any(axis=1)
    flags["negative_volume"] = frame.volume < 0
    flags["bad_OHLC"] = (frame.high < prices.max(axis=1)) | (frame.low > prices.min(axis=1))
    flags["duplicate_key"] = frame.duplicated(["symbol", "datetime"], keep=False)
    flags["wrong_timeframe"] = ~frame.timeframe.eq("1h")
    flags["bad_close_adj"] = (
        frame.close_adj.isna() | ~np.isfinite(frame.close_adj) | frame.close_adj.le(0)
    )
    flags["valid"] = ~flags.any(axis=1)
    return flags


def vendor_boundary_ok(frame: pd.DataFrame, split: str) -> bool:
    dates = frame.datetime.dt.tz_localize(None).dt.strftime("%Y-%m-%d")
    if split == "train":
        return bool(dates.le("2023-12-31").all())
    if split == "val":
        return bool(dates.between("2024-01-01", "2024-12-31").all())
    if split == "test":
        return bool(dates.ge("2025-01-01").all())
    raise ValueError("ONLY_VENDOR_TRAIN_VAL_TEST")


def load_core(manifest: dict) -> tuple[pd.DataFrame, dict]:
    """Project nine original columns only; no precomputed indicator/macro/target use."""
    frames, schemas = [], {}
    remote = {Path(r["path"]).stem: r for r in manifest["remote_files"]}
    started = time.monotonic()
    for row in manifest["files"]:
        path = Path(row["path"])
        split = path.stem
        verify_cached(path, remote[split])
        parquet = pq.ParquetFile(path)
        require_schema(parquet.schema_arrow)
        frame = parquet.read(columns=list(CORE)).to_pandas()
        if not vendor_boundary_ok(frame, split):
            raise ValueError("VENDOR_SPLIT_BOUNDARY_VIOLATION")
        frame["vendor_split"] = split
        schemas[split] = dict(
            schema=str(parquet.schema_arrow),
            rows=len(frame),
            projected_columns=list(CORE),
            full_columns=parquet.schema_arrow.names,
            boundary_passed=True,
        )
        frames.append(frame)
    return pd.concat(frames, ignore_index=True), dict(
        files=schemas, scan_seconds=time.monotonic() - started
    )


def calendar_grid(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    sessions = schedule(start, end)
    for day, row in sessions.iterrows():
        for slot, step in enumerate(session_grid(row.open, row.close), 1):
            rows.append(
                dict(
                    session=pd.Timestamp(str(day)).date().isoformat(),
                    slot=slot,
                    start=step["start"],
                    end=step["end"],
                    stub=step["stub"],
                    session_open=row.open,
                    session_close=row.close,
                    early_close=row.close - row.open < pd.Timedelta(hours=6, minutes=30),
                )
            )
    grid = pd.DataFrame(rows)
    return grid, sessions


def max_gap(present: np.ndarray) -> int:
    gaps = np.flatnonzero(np.diff(np.r_[True, present, True].astype(int)))
    return int(np.max(gaps[1::2] - gaps[::2], initial=0))


def longest_runs(present: np.ndarray, days: list[str], limit: int = 3) -> list[dict]:
    edges = np.flatnonzero(np.diff(np.r_[False, present, False].astype(int)))
    ranges = sorted(zip(edges[::2], edges[1::2]), key=lambda r: r[1] - r[0], reverse=True)[:limit]
    return [dict(start=days[a], end=days[b - 1], sessions=int(b - a)) for a, b in ranges]


@dataclass
class Census:
    frame: pd.DataFrame
    full: pd.DataFrame
    grid: pd.DataFrame
    days: list[str]
    symbols: list[str]
    usable: np.ndarray
    observed: np.ndarray
    monthly: pd.DataFrame
    census: pd.DataFrame
    coverage: dict
    quality: dict


def census(frame: pd.DataFrame, schema: dict, out: Path) -> Census:
    started = time.monotonic()
    flags = quality_flags(frame)
    frame = frame.copy()
    frame["valid"] = flags.valid
    # Wall fields are formatted after vectorized tz removal; UTC timestamps stay original.
    wall = frame.datetime.dt.tz_localize(None)
    frame["session"] = wall.dt.strftime("%Y-%m-%d")
    frame["clock"] = wall.dt.strftime("%H:%M")
    frame["month"] = frame.session.str[:7]
    frame["year"] = frame.session.str[:4]
    frame["UTC"] = frame.datetime.dt.tz_convert("UTC")
    seconds = (wall - frame.UTC.dt.tz_localize(None)).dt.total_seconds()
    if not seconds.isin([-14400, -18000]).all():
        raise ValueError("EXPECTED_EASTERN_DST_OFFSETS_REQUIRED")
    frame["offset"] = seconds.map({-14400: "-0400", -18000: "-0500"})
    first = pd.Timestamp(frame.datetime.min()).strftime("%Y-01-01")
    last = str(frame.session.max())
    grid, sessions = calendar_grid(first, last)
    full = grid.loc[~grid.stub].reset_index(drop=True)
    days = [pd.Timestamp(d).date().isoformat() for d in sessions.index]
    symbols = sorted(str(s) for s in frame.symbol.unique())
    expected_index = pd.DatetimeIndex(full.start)
    stub_index = pd.DatetimeIndex(grid.loc[grid.stub, "start"])
    opens = {
        pd.Timestamp(str(day)).date().isoformat(): row.open for day, row in sessions.iterrows()
    }
    closes = {
        pd.Timestamp(str(day)).date().isoformat(): row.close for day, row in sessions.iterrows()
    }
    frame["aligned_full"] = frame.UTC.isin(expected_index)
    frame["aligned_stub"] = frame.UTC.isin(stub_index)
    frame["calendar_session"] = frame.session.isin(days)
    open_series = pd.to_datetime(frame.session.map(opens), utc=True)
    close_series = pd.to_datetime(frame.session.map(closes), utc=True)
    frame["within_RTH_start"] = frame.UTC.ge(open_series) & frame.UTC.lt(close_series)
    frame["off_grid_RTH"] = frame.within_RTH_start & ~frame.aligned_full & ~frame.aligned_stub
    frame["outside_RTH"] = ~frame.within_RTH_start
    usable = np.zeros((len(full), len(symbols)), dtype=bool)
    observed = np.zeros_like(usable)
    counts, monthly, coverage = [], [], {}
    full_days = full.session.to_numpy()
    months = sorted(set(full.session.str[:7]))
    for j, symbol in enumerate(symbols):
        g = frame.loc[frame.symbol.eq(symbol)].sort_values("UTC")
        f = flags.loc[g.index]
        observed[:, j] = expected_index.isin(g.UTC)
        usable[:, j] = expected_index.isin(g.loc[g.valid, "UTC"])

        def scope(a: str, b: str) -> dict:
            select = (full_days >= a) & (full_days <= b)
            v = usable[select, j]
            d = pd.DataFrame(dict(day=full_days[select], present=v)).groupby("day").present.sum()
            observed_dates = set(g.loc[g.session.between(a, b), "session"])
            return dict(
                expected_full_hours=len(v),
                observed_full_hours=int(observed[select, j].sum()),
                usable_full_hours=int(v.sum()),
                missing_or_invalid_hours=int((~v).sum()),
                coverage=float(v.mean()) if len(v) else None,
                max_consecutive_missing=max_gap(v),
                calendar_sessions=len(d),
                missing_entire_observed_sessions=int(sum(x not in observed_dates for x in d.index)),
                no_usable_aligned_sessions=int(d.eq(0).sum()),
            )

        row = dict(
            symbol=symbol,
            rows=len(g),
            train_rows=int(g.vendor_split.eq("train").sum()),
            val_rows=int(g.vendor_split.eq("val").sum()),
            test_rows=int(g.vendor_split.eq("test").sum()),
            earliest_ET=str(g.datetime.min()),
            latest_ET=str(g.datetime.max()),
            earliest_UTC=str(g.UTC.min()),
            latest_UTC=str(g.UTC.max()),
            unique_dates=g.session.nunique(),
            exchange_sessions=g.loc[g.calendar_session, "session"].nunique(),
            duplicate_keys=int(g.duplicated(["symbol", "datetime"]).sum()),
            aligned_full_rows=int(g.aligned_full.sum()),
            aligned_terminal_stub_rows=int(g.aligned_stub.sum()),
            off_grid_RTH_rows=int(g.off_grid_RTH.sum()),
            outside_RTH_rows=int(g.outside_RTH.sum()),
            noncalendar_rows=int((~g.calendar_session).sum()),
            close_adj_unequal_close=int((g.close_adj != g.close).sum()),
            close_adj_outside_OHLC=int(((g.close_adj < g.low) | (g.close_adj > g.high)).sum()),
            **{name: int(f[name].sum()) for name in flags.columns if name != "valid"},
        )
        original = scope("2020-07-01", "2024-06-30")
        row.update({"strict_" + k: v for k, v in original.items()})
        for a, b, label in (
            ("2020-07-01", "2023-06-30", "training"),
            ("2023-07-01", "2024-06-30", "development"),
            ("2019-12-18", "2020-06-30", "prehistory"),
        ):
            row.update({label + "_" + k: v for k, v in scope(a, b).items()})
        daily = (
            pd.DataFrame(dict(day=full_days, present=usable[:, j]))
            .groupby("day")
            .present.agg(["sum", "count"])
        )
        clean = daily["sum"].eq(daily["count"]).to_numpy()
        coverage[symbol] = dict(
            active_range=dict(start=str(g.session.min()), end=str(g.session.max())),
            strict=original,
            full_available=scope(str(g.session.min()), str(g.session.max())),
            clock_start_ET_counts={
                str(k): int(v) for k, v in g.clock.value_counts().sort_index().items()
            },
            UTC_offset_counts={str(k): int(v) for k, v in g.offset.value_counts().items()},
            longest_calendar_perfect_runs=longest_runs(clean, list(daily.index)),
        )
        for month in months:
            select = full.session.str.startswith(month).to_numpy()
            h = g.loc[g.month.eq(month)]
            v = usable[select, j]
            ds = pd.DataFrame(dict(day=full_days[select], present=v)).groupby("day").present.sum()
            last_positions = full.loc[select].groupby("session").tail(1).index.to_numpy()
            stubs = grid.loc[grid.stub & grid.session.str.startswith(month)]
            monthly.append(
                dict(
                    symbol=symbol,
                    month=month,
                    expected_calendar_sessions=len(ds),
                    observed_rows=len(h),
                    expected_full_hours=len(v),
                    observed_aligned_hours=int(observed[select, j].sum()),
                    usable_full_hours=int(v.sum()),
                    missing_full_hours=int((~v).sum()),
                    full_hour_coverage=float(v.mean()),
                    max_consecutive_missing=max_gap(v),
                    missing_entire_sessions=int(sum(x not in set(h.session) for x in ds.index)),
                    no_usable_aligned_sessions=int(ds.eq(0).sum()),
                    missing_last_complete_hour=int((~usable[last_positions, j]).sum()),
                    expected_terminal_stubs=len(stubs),
                    missing_terminal_stubs=int((~stubs.start.isin(h.UTC)).sum()),
                    off_grid_RTH_rows=int(h.off_grid_RTH.sum()),
                    outside_RTH_rows=int(h.outside_RTH.sum()),
                    invalid_rows=int((~h.valid).sum()),
                )
            )
        counts.append(row)
    monthly_frame = pd.DataFrame(monthly)
    census_frame = pd.DataFrame(counts)
    census_frame.to_csv(out / "hourly_symbol_census.csv", index=False)
    monthly_frame.to_csv(out / "hourly_missingness_by_month.csv", index=False)
    yearly = (
        frame.groupby(["symbol", "year"])
        .agg(
            rows=("symbol", "size"),
            aligned_full_rows=("aligned_full", "sum"),
            off_grid_RTH_rows=("off_grid_RTH", "sum"),
            outside_RTH_rows=("outside_RTH", "sum"),
        )
        .reset_index()
    )
    yearly.to_csv(out / "hourly_coverage_by_year.csv", index=False)
    alignment = []
    day_rows = frame.groupby("session", sort=False).indices
    expected_days = full.groupby("session", sort=False).indices
    stub_days = grid.loc[grid.stub].set_index("session").start.astype(str).to_dict()
    for day in days:
        expected = full.iloc[expected_days[day]]
        h = frame.iloc[day_rows.get(day, np.array([], dtype=int))]
        positions = expected.index.to_numpy()
        alignment.append(
            dict(
                session=day,
                expected_full_slots_per_symbol=len(expected),
                expected_full_starts_UTC="|".join(expected.start.astype(str)),
                expected_terminal_stub_start_UTC=stub_days.get(day, ""),
                early_close=bool(expected.early_close.any()),
                expected_stock_hours=len(expected) * len(symbols),
                usable_stock_hours=int(usable[positions].sum()),
                missing_stock_hours=int((~usable[positions]).sum()),
                symbols_with_all_full_hours=int(usable[positions].all(axis=0).sum()),
                observed_symbols=h.symbol.nunique(),
                off_grid_RTH_rows=int(h.off_grid_RTH.sum()),
                outside_RTH_rows=int(h.outside_RTH.sum()),
                observed_clock_signature="|".join(sorted(h.clock.unique())),
            )
        )
    pd.DataFrame(alignment).to_csv(out / "hourly_calendar_alignment.csv", index=False)
    write_json(out / "per_symbol_coverage.json", coverage)
    quality = dict(
        **schema,
        rows=len(frame),
        symbols=len(symbols),
        quality_counts={name: int(flags[name].sum()) for name in flags.columns},
        observed_clock_counts={
            str(k): int(v) for k, v in frame.clock.value_counts().sort_index().items()
        },
        declared_interval=(
            "1h interval START per publisher; actual interval end/publication not supplied"
        ),
        calendar="XNYS including actual DST/early closes; no closed-hour forward filling",
        census_seconds=time.monotonic() - started,
        confirmation_labels_created=0,
        original_confirmation_source_access=False,
        precomputed_indicators_used=False,
        close_adj_unequal_close=int((frame.close_adj != frame.close).sum()),
    )
    write_json(out / "hourly_schema_quality.json", quality)
    return Census(
        frame,
        full,
        grid,
        days,
        symbols,
        usable,
        observed,
        monthly_frame,
        census_frame,
        coverage,
        quality,
    )
