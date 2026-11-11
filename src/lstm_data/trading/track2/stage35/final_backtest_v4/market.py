"""Chronological projected RAW source; calendar axis never depends on future labels."""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ...stage012.calendar_schedule import MarketClock
from ...stage012.model_registry import SYMBOLS
from .paths import ROOT, V2, canonical, digest


@dataclass(frozen=True)
class Day:
    date: str
    starts: np.ndarray
    opens: np.ndarray
    closes: np.ndarray
    volumes: np.ndarray
    valid: np.ndarray
    signals: pd.DataFrame
    source_hash: str
    ogn: dict[int, dict]


def minute(value: object) -> int:
    return int(pd.Timestamp(str(value)).value // 60_000_000_000)


def stamp(value: int) -> str:
    return pd.Timestamp(value * 60_000_000_000, tz="UTC").isoformat()


class Market:
    def __init__(
        self, first: str = "2021-01-01", last: str = "2024-12-31", use_gap_supplement: bool = True
    ):
        if first < "2021-01-01" or last > "2024-12-31":
            raise ValueError("PRICE_PERIOD_SCOPE")
        self.first, self.last = first, last
        self.clock = MarketClock("2020-12-01", "2025-01-10")
        receipts = json.loads((V2 / "audits/cache/source_receipts.json").read_text())
        self.parts = {
            Path(r["path"]).stem: r
            for r in receipts
            if r["family"] == "minute" and "2021-01" <= Path(r["path"]).stem <= "2024-12"
        }
        if len(self.parts) != 48:
            raise ValueError("RAW_SOURCE_COVERAGE")
        self.ogn_source_hash = digest(ROOT / "sources/ogn_sip.json")
        ogn = json.loads((ROOT / "sources/ogn_sip.json").read_text())
        self.ogn = {
            minute(row["t"]): row
            for row in ogn.get("bars", [])
            if "2021-06-03" <= str(row["t"])[:10] <= "2021-06-04"
        }
        self.reads: list[dict] = []
        self.gap_entries: dict[str, dict] = {}
        gap_manifest = ROOT / "ECONOMIC_GAP_SUPPLEMENT_MANIFEST_V4.json"
        if use_gap_supplement and gap_manifest.exists():
            source = json.loads(gap_manifest.read_text())
            if not source["all_dates_attempted"] or any(
                row["status"] != "COMPLETE_RESPONSE" for row in source["entries"]
            ):
                raise ValueError("RAW_GAP_RETRIEVAL_INCOMPLETE")
            self.gap_entries = {row["date"]: row for row in source["entries"]}

    def days(self, include_signals: bool = True):
        start_month = self.first[:7]
        end_month = self.last[:7]
        columns = ["ticker", "timestamp", "is_rth", "open", "high", "low", "close", "volume"]
        for month, item in sorted(self.parts.items()):
            if not start_month <= month <= end_month:
                continue
            path = Path(item["path"])
            if digest(path) != item["sha256"]:
                raise ValueError("RAW_SOURCE_HASH")
            frame = pd.read_parquet(
                path,
                columns=columns,
                filters=[("is_rth", "==", True), ("ticker", "in", list(SYMBOLS))],
            )
            if frame.duplicated(["ticker", "timestamp"]).any():
                raise ValueError("DUPLICATE_RAW_MINUTE")
            frame["date"] = frame.timestamp.dt.tz_convert("America/New_York").dt.strftime(
                "%Y-%m-%d"
            )
            self.reads.append(
                {"path": str(path), "sha256": item["sha256"], "projected_rows": len(frame)}
            )
            for date in self.clock.calendar.loc[
                month : str(pd.Timestamp(month + "-01") + pd.offsets.MonthEnd(0))[:10]
            ].index:
                day = str(date)[:10]
                if not self.first <= day <= self.last:
                    continue
                scheduled = self.clock.calendar.loc[date]
                opened = pd.Timestamp(scheduled["open"])
                closed = pd.Timestamp(scheduled["close"])
                idx = pd.date_range(opened, closed, freq="min", inclusive="left")
                sample = frame.loc[frame.date == day]
                arrays = []
                for key in ("open", "close", "volume", "high", "low"):
                    arrays.append(
                        sample.pivot(index="timestamp", columns="ticker", values=key)
                        .reindex(index=idx, columns=SYMBOLS)
                        .to_numpy(float)
                        .copy()
                    )
                op, cl, vol, hi, lo = arrays
                valid = (
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
                source_hash = item["sha256"]
                if day in self.gap_entries:
                    receipt = self.gap_entries[day]
                    extra_path = Path(receipt["path"])
                    if digest(extra_path) != receipt["projected_sha256"]:
                        raise ValueError("RAW_GAP_SUPPLEMENT_HASH")
                    extra = json.loads(extra_path.read_text())
                    if extra["basis"] != "RAW_SHARE":
                        raise ValueError("RAW_GAP_BASIS")
                    starts = idx.to_numpy(dtype="datetime64[ns]").astype(np.int64) // 60_000_000_000
                    for row in extra["bars"]:
                        t = minute(row["t"])
                        i = int(np.searchsorted(starts, t))
                        j = SYMBOLS.index(row["symbol"])
                        if i >= len(starts) or int(starts[i]) != t or valid[i, j]:
                            raise ValueError("SUPPLEMENT_OUT_OF_SCOPE_OR_OVERWRITES_VALID_SOURCE")
                        values = np.asarray([row[k] for k in ("o", "h", "l", "c", "v")], float)
                        o, h, low, c, v = values
                        if not (
                            np.isfinite(values).all()
                            and min(o, h, low, c) > 0
                            and v >= 0
                            and low <= min(o, c)
                            and h >= max(o, c)
                        ):
                            raise ValueError("INVALID_GAP_QUOTE")
                        op[i, j], cl[i, j], vol[i, j], hi[i, j], lo[i, j] = o, c, v, h, low
                        valid[i, j] = True
                    source_hash = canonical(
                        {"canonical": source_hash, "gap_source": receipt["projected_sha256"]}
                    )
                signal = V2 / f"audits/signals_release/F{int(day[:4]) - 2000:02d}/{day}.parquet"
                if not signal.is_file():
                    raise ValueError("SOURCE_OPPORTUNITY_PARTITION_MISSING")
                signals = pd.read_parquet(signal) if include_signals else pd.DataFrame()
                if include_signals and len(signals) != 20 * len(self.clock.origins(day)):
                    raise ValueError("CALENDAR_OPPORTUNITY_AXIS")
                yield Day(
                    day,
                    idx.to_numpy(dtype="datetime64[ns]").astype(np.int64) // 60_000_000_000,
                    op,
                    cl,
                    vol,
                    valid,
                    signals,
                    source_hash,
                    self.ogn,
                )
