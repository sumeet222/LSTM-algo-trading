"""Single projected raw/share stream; no neural/evaluation-table dependency."""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..stage012.calendar_schedule import MarketClock
from ..stage012.model_registry import SYMBOLS
from ..stage35.final_backtest_v4.market import Day, Market, minute
from .paths import ROOT, V4, canonical, digest


@dataclass(frozen=True)
class RawDay(Day):
    highs: np.ndarray
    lows: np.ndarray
    basis: str = "RAW_SHARE"


def valid_ohlcv(op, hi, lo, cl, vol) -> np.ndarray:
    """Exactly the V4 raw bar QA predicate, with no return-based filter."""
    return (
        np.isfinite(op)
        & np.isfinite(cl)
        & np.isfinite(vol)
        & np.isfinite(hi)
        & np.isfinite(lo)
        & (op > 0)
        & (cl > 0)
        & (vol >= 0)
        & (lo > 0)
        & (lo <= np.minimum(op, cl))
        & (hi >= np.maximum(op, cl))
    )


class RawMarket(Market):
    def __init__(self, first: str = "2020-01-01", last: str = "2024-12-31"):
        if not "2020-01-01" <= first <= last <= "2024-12-31":
            raise ValueError("PRICE_PERIOD_SCOPE")
        self.first, self.last = first, last
        self.clock = MarketClock("2020-01-01", "2025-01-10")
        inventory = json.loads((ROOT / "audits/FROZEN_BOUNDARY_BASELINE.json").read_text())
        self.parts = {
            Path(r["path"]).stem: r
            for r in inventory["files"]
            if "/canonical_observed/" in r["path"]
            and r["path"].endswith(".parquet")
            and "2020-01" <= Path(r["path"]).stem <= "2024-12"
        }
        if len(self.parts) != 60:
            raise ValueError("RAW_WARMUP_AND_OOS_PARTITIONS")
        gap = json.loads((V4 / "ECONOMIC_GAP_SUPPLEMENT_MANIFEST_V4.json").read_text())
        if not gap["all_dates_attempted"] or any(
            r["status"] != "COMPLETE_RESPONSE" for r in gap["entries"]
        ):
            raise ValueError("GAP_MANIFEST_INCOMPLETE")
        self.gaps = {r["date"]: r for r in gap["entries"]}
        p = V4 / "sources/ogn_sip.json"
        self.ogn_source_hash = digest(p)
        self.ogn = {
            minute(r["t"]): r
            for r in json.loads(p.read_text()).get("bars", [])
            if "2021-06-03" <= str(r["t"])[:10] <= "2021-06-04"
        }
        self.reads: list[dict] = []

    def days(self, include_signals: bool = False):
        if include_signals:
            raise ValueError("DIRECTION_READER_DOES_NOT_LOAD_NEURAL_PANELS")
        columns = ["ticker", "timestamp", "is_rth", "open", "high", "low", "close", "volume"]
        for month, receipt in sorted(self.parts.items()):
            if not self.first[:7] <= month <= self.last[:7]:
                continue
            p = Path(receipt["path"])
            if digest(p) != receipt["sha256"]:
                raise ValueError("RAW_SOURCE_HASH:" + str(p))
            frame = pd.read_parquet(
                p,
                columns=columns,
                filters=[("is_rth", "==", True), ("ticker", "in", list(SYMBOLS))],
            )
            if frame.duplicated(["ticker", "timestamp"]).any():
                raise ValueError("DUPLICATE_RAW_MINUTE")
            if frame.timestamp.dt.tz is None:
                raise ValueError("NAIVE_SOURCE_TIMESTAMP")
            schedule = self.clock.calendar.loc[
                month : str(pd.Timestamp(month + "-01") + pd.offsets.MonthEnd(0))[:10]
            ]
            day_starts = [
                np.arange(minute(row["open"]), minute(row["close"]), dtype=np.int64)
                for _, row in schedule.iterrows()
            ]
            starts = np.concatenate(day_starts)
            values = np.full((len(starts), 20, 5), np.nan)
            times = (
                frame.timestamp.to_numpy(dtype="datetime64[ns]").astype(np.int64) // 60_000_000_000
            )
            ix = np.searchsorted(starts, times)
            present = ix < len(starts)
            present[present] &= starts[ix[present]] == times[present]
            js = pd.Categorical(frame.ticker, categories=SYMBOLS).codes
            present &= js >= 0
            raw = frame[["open", "close", "volume", "high", "low"]].to_numpy(float)
            values[ix[present], js[present], :] = raw[present]
            self.reads.append({"path": str(p), "sha256": receipt["sha256"], "rows": len(frame)})
            offset = 0
            for (label, _), slots in zip(schedule.iterrows(), day_starts, strict=True):
                data = values[offset : offset + len(slots)].copy()
                offset += len(slots)
                day = str(label)[:10]
                if not self.first <= day <= self.last:
                    continue
                op, cl, vol, hi, lo = (data[:, :, k] for k in range(5))
                valid = valid_ohlcv(op, hi, lo, cl, vol)
                lineage = receipt["sha256"]
                if day in self.gaps:
                    r = self.gaps[day]
                    extra_path = Path(r["path"])
                    if digest(extra_path) != r["projected_sha256"]:
                        raise ValueError("GAP_SUPPLEMENT_HASH")
                    extra = json.loads(extra_path.read_text())
                    if extra["basis"] != "RAW_SHARE":
                        raise ValueError("BAD_EXECUTION_BASIS")
                    for row in extra["bars"]:
                        ts = minute(row["t"])
                        i = int(np.searchsorted(slots, ts))
                        j = SYMBOLS.index(row["symbol"])
                        if i >= len(slots) or slots[i] != ts or valid[i, j]:
                            raise ValueError("SUPPLEMENT_OVERWRITES_OR_OUT_OF_SCOPE")
                        o, h, low, c, v = (float(row[k]) for k in ("o", "h", "l", "c", "v"))
                        if not bool(valid_ohlcv(o, h, low, c, v)):
                            raise ValueError("INVALID_SUPPLEMENT_BAR")
                        op[i, j], hi[i, j], lo[i, j], cl[i, j], vol[i, j] = o, h, low, c, v
                        valid[i, j] = True
                    lineage = canonical({"canonical": lineage, "gap_source": r["projected_sha256"]})
                yield RawDay(
                    day, slots, op, cl, vol, valid, pd.DataFrame(), lineage, self.ogn, hi, lo
                )
