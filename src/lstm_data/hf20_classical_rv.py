"""Bounded, receipt-bound prior-day minute RV; no target values or fitting."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import hf20_mag_designa as b
from . import hf20_minute_inputs as minute
from .hf20_classical_math import rv_value


def build_rv(out: Path, latest_origin_date: str) -> None:
    """Stream authorized pre-2025 full sessions, preserving missing scheduled minutes."""
    if (out / "daily_rv.parquet").exists():
        raise ValueError("SINGLE_USE_RV_CONSTRUCTION")
    refs = pd.read_csv(minute.SOURCE / "S4_NUMERICAL_SOURCE_READS.csv")
    hourly = refs.loc[refs.purpose.eq("permitted adjusted hourly source")]
    minutes = refs.loc[refs.purpose.eq("permitted genuine minute endpoints; no proxy")]
    records, receipts = [], []
    fields = [
        "ticker",
        "session_date_et",
        "hour_start_utc",
        "hour_end_utc",
        "expected_minutes",
        "price_factor",
        "price_basis_id",
        "quarantine_count",
        "anomaly_event_ids",
        "genuine_count",
        "close",
        "observed_close",
    ]
    for ref in hourly.to_dict("records"):
        path = Path(str(ref["path"]))
        month = path.stem
        assert "2010-07" <= month <= "2024-12" and not path.is_absolute()
        if month > latest_origin_date[:7]:
            continue
        assert b.digest(path) == ref["sha256"]
        h = pd.read_parquet(
            path, columns=fields, filters=[("session_date_et", "<", latest_origin_date)]
        )
        # Original source includes six full bins plus the real closing half-hour.
        total = h.groupby(["session_date_et", "ticker"]).expected_minutes.sum()
        full_dates = total.unstack().index[(total.unstack() == 390).all(axis=1)].to_numpy()
        h = h.loc[h.session_date_et.isin(full_dates)].copy()
        if h.empty:
            continue
        excluded = minute.quarantine(h)
        mref = minutes.loc[minutes.path.str.endswith(month + ".parquet")].iloc[0]
        mp = Path(mref.path)
        assert mp.stem == month and mp.stat().st_size == mref.bytes
        assert b.digest(mp) == mref.sha256
        opens = h.groupby("session_date_et").hour_start_utc.min().sort_index()
        starts = pd.DatetimeIndex(opens.to_numpy()).as_unit("ns")
        times = pd.DatetimeIndex(
            pd.to_datetime(
                (
                    starts.to_numpy(dtype="datetime64[ns]").view(np.int64)[:, None]
                    + np.arange(390)[None, :] * 60_000_000_000
                ).ravel(),
                utc=True,
            )
        )
        m = pd.read_parquet(
            mp,
            columns=[
                "ticker",
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "is_rth",
                "is_genuine",
                "is_imputed",
                "source_revision",
            ],
            filters=[("timestamp", "in", times.tolist()), ("is_rth", "==", True)],
        )
        assert not m.duplicated(["ticker", "timestamp"]).any()
        assert (
            m.is_genuine.all()
            and not m.is_imputed.any()
            and m.source_revision.eq(minute.REVISION).all()
        )
        raw = m[["open", "high", "low", "close"]].to_numpy(float)
        valid = np.isfinite(raw).all(1) & (raw > 0).all(1)
        valid &= (raw[:, 1] >= np.maximum(raw[:, 0], raw[:, 3])) & (
            raw[:, 2] <= np.minimum(raw[:, 0], raw[:, 3])
        )
        if not valid.all():
            raise ValueError("INVALID_CANONICAL_OHLC", month, int((~valid).sum()))
        remove = np.asarray([(s, t) in excluded for s, t in zip(m.ticker, m.timestamp)], dtype=bool)
        m = m.loc[~remove].copy()
        mapper = pd.Series(np.arange(len(times)), index=times)
        flat = m.timestamp.map(mapper).to_numpy(int)
        day, pos = flat // 390, flat % 390
        stock = m.ticker.map({s: j for j, s in enumerate(b.SYMBOLS)}).to_numpy(int)
        groups = h.groupby(["session_date_et", "ticker"])
        assert (
            groups.price_factor.nunique().eq(1).all()
            and groups.price_basis_id.nunique().eq(1).all()
        )
        factors = (
            groups.price_factor.first()
            .unstack()
            .reindex(index=opens.index, columns=b.SYMBOLS)
            .to_numpy(float)
        )
        assert np.isfinite(factors).all() and (factors > 0).all()
        close = np.full((len(opens), 20, 390), np.nan)
        close[day, stock, pos] = m.close.to_numpy(float) * factors[day, stock]
        # Independently reproduce all saved bin counts and genuine terminal closes,
        # including the 30-minute stub; no hourly proxy is used as a minute price.
        hday = opens.index.get_indexer(pd.Index(h.session_date_et))
        hstock = h.ticker.map({s: j for j, s in enumerate(b.SYMBOLS)}).to_numpy(int)
        begin = (
            (
                h.hour_start_utc.dt.as_unit("ns").array.asi8
                - starts.to_numpy(dtype="datetime64[ns]").view(np.int64)[hday]
            )
            // 60_000_000_000
        ).astype(int)
        length = h.expected_minutes.to_numpy(int)
        observed_count = np.asarray(
            [
                np.isfinite(close[d, j, a : a + n]).sum()
                for d, j, a, n in zip(hday, hstock, begin, length)
            ]
        )
        np.testing.assert_array_equal(observed_count, h.genuine_count.to_numpy(int))
        terminal = close[hday, hstock, begin + length - 1]
        old = h.close.to_numpy(float)
        np.testing.assert_array_equal(np.isnan(terminal), np.isnan(old))
        good = np.isfinite(old)
        np.testing.assert_allclose(terminal[good], old[good], atol=1e-10, rtol=1e-10)
        rv, pairs = rv_value(close)
        for d, date in enumerate(opens.index):
            for j, ticker in enumerate(b.SYMBOLS):
                records.append(
                    dict(
                        session_date_et=str(date),
                        ticker=ticker,
                        rv=float(rv[d, j]),
                        valid_pairs=int(pairs[d, j]),
                        expected_pairs=389,
                        observed_minutes=int(np.isfinite(close[d, j]).sum()),
                    )
                )
        receipts.append(
            dict(
                path=str(mp),
                sha256=str(mref.sha256),
                rows_read=len(raw),
                quarantined=int(remove.sum()),
                full_sessions=len(opens),
                first_input=str(m.timestamp.min()),
                last_input=str(m.timestamp.max()),
                matched_hourly_bins=len(h),
                invalid_ohlc=0,
                terminal_max_error=float(np.max(abs(terminal[good] - old[good])))
                if good.any()
                else 0,
            )
        )
        b.memory()
        print("RV_SOURCE", month, len(opens), flush=True)
    f = pd.DataFrame(records)
    assert not f.duplicated(["session_date_et", "ticker"]).any()
    assert f.session_date_et.lt(latest_origin_date).all() and f.session_date_et.lt("2025").all()
    f.to_parquet(out / "daily_rv.parquet", compression="zstd", index=False)
    pd.DataFrame(receipts).to_csv(out / "rv_source_reads.csv", index=False)
    f.assign(year=f.session_date_et.str[:4], valid=f.rv.notna()).groupby(["year", "ticker"]).agg(
        sessions=("rv", "size"),
        valid_sessions=("valid", "sum"),
        observed_minutes=("observed_minutes", "sum"),
        valid_pairs=("valid_pairs", "sum"),
        expected_pairs=("expected_pairs", "sum"),
    ).reset_index().to_csv(out / "rv_coverage.csv", index=False)
