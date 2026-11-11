"""Original causal feature-state cache, no evaluation/label panel or financial books.

Original build updates each EMA/Wilder state ONCE from source genesis. All cached
columns are causal indexed prefixes; source-matured M2 uses an explicit day-open
frontier. Runtime gathers only48 completed scheduled slots. No Phase2 code.
"""

import argparse
import csv
import hashlib
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from lstm_data.hf1m_action_source import adjust_prices
from lstm_data.hf1m_ft16_fit import native
from lstm_data.hf1m_ft16_math import build, rolling
from lstm_data.hf20_s4_preflight import field_masks, input_valid
from lstm_data.hf20_s4_witnesses import scaled

from ...stage012.calendar_schedule import MarketClock
from ...stage012.historical_source_store import HOUR_COLUMNS, file_hash
from ...stage012.model_registry import SYMBOLS
from ...stage012.original_feature_pure import cached_endpoint, cached_origins

ROOT = Path("trading/track2/stage35/completion_v2")
REV = "CACHE_ORIGINAL_CAUSAL_V2"


def publish(path: Path, payload: object) -> None:
    text = json.dumps(payload, indent=2, default=str) + "\n"
    if path.exists():
        if path.read_text() != text:
            raise ValueError("IMMUTABLE_METADATA_CHANGED:" + str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text)
    temp.replace(path)


def geometry(clock: MarketClock, start="2020-09-01", stop="2024-12-31") -> pd.DataFrame:
    rows = []
    for day, session in clock.calendar.loc[start:stop].iterrows():
        date = str(pd.Timestamp(str(day)).date())
        times = cached_origins(clock, date)
        for k, t in enumerate(times):
            end = cached_endpoint(clock, t)
            rows.append(
                dict(
                    origin_id=t.isoformat(),
                    session_date_et=date,
                    slot=t.astimezone(ZoneInfo("America/New_York")).strftime("%H:%M"),
                    context=6 if k == 0 else k - 1,
                    entry_end_utc=t,
                    exit_end_utc=end,
                    session_close=session["close"],
                    regular_session=(
                        session["close"] - session["open"] == pd.Timedelta(minutes=390)
                    ),
                    category="INTRADAY" if end <= session["close"] else "OVERNIGHT",
                )
            )
    return pd.DataFrame(rows)


def prepare_plan(path: Path) -> None:
    if path.exists():
        raise ValueError("APPEND_ONLY_PLAN")
    clock = MarketClock("2010-07-01", "2025-01-10")
    geo = geometry(clock)
    keys = set()
    for t, end, slot in geo[["entry_end_utc", "exit_end_utc", "slot"]].itertuples(
        index=False, name=None
    ):
        keys.add(t if slot == "09:30" else t - timedelta(minutes=1))
        if end.astimezone(ZoneInfo("America/New_York")).year <= 2024:
            keys.add(end - timedelta(minutes=1))
    # Source-only raw/share split fixture, no trading orders.
    keys.update(
        (
            datetime(2020, 8, 28, 15, 59, tzinfo=ZoneInfo("America/New_York")),
            datetime(2020, 8, 31, 9, 30, tzinfo=ZoneInfo("America/New_York")),
        )
    )
    refs = list(
        csv.DictReader(
            Path(
                "reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv"
            ).open()
        )
    )
    by = {r["path"]: r for r in refs}
    sources = []
    for month in pd.period_range("2010-07", "2024-12", freq="M").astype(str):
        name = (
            "data/processed/hf20_hf1m_long_v1_action_qa_v1/"
            f"ta019b_action_qa_2026-10-22_201224/hourly/{month}.parquet"
        )
        sources.append({"path": name, "sha256": by[name]["sha256"], "family": "hourly"})
    for month in sorted(
        {t.astimezone(ZoneInfo("America/New_York")).strftime("%Y-%m") for t in keys}
    ):
        name = (
            "data/processed/hf20_hf1m_long_v1/"
            "776328445b7ac6e7815ef3a483e9c8ded1eb6d56/qa_v2/"
            f"canonical_observed/{month}.parquet"
        )
        sources.append({"path": name, "sha256": by[name]["sha256"], "family": "minute"})
    plan = {
        "version": REV,
        "symbols": list(SYMBOLS),
        "signal_start": "2021-01-01",
        "signal_stop": "2024-12-31",
        "sources": sources,
        "minute_keys": sorted(t.astimezone(ZoneInfo("UTC")).isoformat() for t in keys),
        "forecast_opportunities": int(geo.loc[geo.session_date_et >= "2021-01-01"].shape[0]) * 20,
        "price_stop": "2024-12-31",
        "source_read_projection": (
            "all20 hourly19fields+hourid/basis/expected_minutes;"
            "minute ticker/time/RTH/OHLC at declared anchors only"
        ),
        "resources": {
            "estimated_peak_memory_gb": 3,
            "derived_cache_disk_gb": 0.5,
            "signal_disk_gb": 0.3,
            "no_raw_copy": True,
        },
        "parity_sample": [
            (y, day, slot, ticker)
            for y, day, slot in [
                (2021, "2021-01-08", "10:30"),
                (2022, "2022-01-10", "10:30"),
                (2023, "2023-01-09", "10:30"),
                (2024, "2024-01-08", "10:30"),
                (2024, "2024-11-29", "09:30"),
                (2024, "2024-01-08", "15:30"),
            ]
            for ticker in ("AAPL", "COP")
        ],
        "numeric_tolerance": {
            "input_atol": 1e-6,
            "input_rtol": 1e-5,
            "forecast_atol": 1e-7,
            "forecast_rtol": 1e-5,
        },
        "financial_outputs": False,
        "unmatured_after_stop": "do not fetch;retain signal opportunity",
    }
    publish(path, plan)
    publish(
        path.with_suffix(".seal.json"),
        {"path": str(path), "sha256": file_hash(path), "before_market_values": True},
    )


class Sources:
    def __init__(self, plan: Path, expected: str):
        if file_hash(plan) != expected:
            raise ValueError("PLAN_HASH_MISMATCH")
        self.plan = json.loads(plan.read_text())
        self.receipts = []
        self.hash = hashlib.sha256(
            json.dumps(self.plan["sources"], sort_keys=True).encode()
        ).hexdigest()

    def check(self, row: dict) -> Path:
        f = Path(row["path"])
        if f.is_absolute() or ".." in f.parts or not "2010-07" <= f.stem <= "2024-12":
            raise ValueError("PARTITION_DENIED_BEFORE_IO")
        if row not in self.plan["sources"] or file_hash(f) != row["sha256"]:
            raise ValueError("SOURCE_HASH")
        return f

    def read(self) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
        hours = []
        minutes = []
        keys = pd.DatetimeIndex(pd.to_datetime(self.plan["minute_keys"], utc=True))
        for row in self.plan["sources"]:
            f = self.check(row)
            if row["family"] == "hourly":
                frame = pd.read_parquet(
                    f,
                    columns=list(
                        dict.fromkeys(
                            [*HOUR_COLUMNS, "hour_id", "price_basis_id", "expected_minutes"]
                        )
                    ),
                )
                hours.append(frame)
            else:
                selected = keys[keys.tz_convert("America/New_York").strftime("%Y-%m") == f.stem]
                frame = pd.read_parquet(
                    f,
                    columns=["ticker", "timestamp", "is_rth", "open", "high", "low", "close"],
                    filters=[
                        ("is_rth", "==", True),
                        ("ticker", "in", list(SYMBOLS)),
                        ("timestamp", "in", selected),
                    ],
                )
                minutes.append(frame)
            self.receipts.append(
                {
                    "path": str(f),
                    "sha256": row["sha256"],
                    "rows_returned": len(frame),
                    "family": row["family"],
                    "mtime_ns": f.stat().st_mtime_ns,
                }
            )
        facts = json.loads(Path("configs/hf1m_p019_verified_event_facts_v1.json").read_text())[
            "events"
        ]
        facts = [f for f in facts if f["date"] <= "2024-12-31"]
        return pd.concat(hours, ignore_index=True), pd.concat(minutes, ignore_index=True), facts


def ns(values) -> np.ndarray:
    return (
        pd.DatetimeIndex(pd.to_datetime(values, utc=True))
        .to_numpy(dtype="datetime64[ns]")
        .view("int64")
    )


def source_movements(geo: pd.DataFrame, prices: pd.DataFrame) -> np.ndarray:
    result = np.full((len(geo), 20), np.nan)
    table = prices.set_index(["timestamp", "ticker"])
    for field in ("open", "close"):
        if table.index.duplicated().any():
            raise ValueError("AMBIGUOUS_MINUTE")
    times = pd.DatetimeIndex(geo.entry_end_utc) - pd.to_timedelta(
        np.where(geo.slot.eq("09:30"), 0, 1), unit="m"
    )
    ends = pd.DatetimeIndex(geo.exit_end_utc) - pd.Timedelta(minutes=1)
    for j, ticker in enumerate(SYMBOLS):
        part = prices.loc[prices.ticker == ticker].set_index("timestamp")
        opened = part.open.reindex(times).to_numpy(float)
        closed = part.close.reindex(times).to_numpy(float)
        anchor = np.where(geo.slot.eq("09:30"), opened, closed)
        target = part.close.reindex(ends).to_numpy(float)
        good = np.isfinite(anchor) & np.isfinite(target) & (anchor > 0) & (target > 0)
        result[good, j] = np.log(target[good] / anchor[good])
    return result


def cache_build(plan_path: Path, expected: str, folder: Path) -> None:
    if (folder / "CACHE_READY.json").exists():
        return
    folder.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    source = Sources(plan_path, expected)
    hours, raw, facts = source.read()
    clock = MarketClock("2010-07-01", "2025-01-10")
    geo = geometry(clock)
    print("Source loaded", len(hours), len(raw), flush=True)
    adjusted = adjust_prices(raw, facts)
    moves = source_movements(geo, adjusted)
    np.save(folder / "matured_source_moves.npy", moves)
    geo.to_parquet(folder / "movement_geometry.parquet", index=False)
    raw.to_parquet(folder / "bounded_raw_anchor_tape.parquet", index=False)
    # One original source-state pass;IndicatorState updates each stock/hour once.
    components = build(hours, field_masks(hours, facts))
    grid = components.grid.copy()
    grid.to_parquet(folder / "grid.parquet", index=False)
    np.save(folder / "input_valid.npy", input_valid(components))
    np.save(folder / "genuine_close.npy", components.source["close"])
    np.save(folder / "m2_mean_original_two.npy", components.m2_mean)
    components.m2_mean = np.full((len(grid), 20, 7), np.nan)
    components.m2_rms = np.full_like(components.m2_mean, np.nan)
    mature_ns = ns(geo.exit_end_utc) + 120 * 10**9
    input_days = grid.loc[grid.session_date_et >= "2020-12-01", "session_date_et"].unique()
    for context in range(7):
        eligible = geo.loc[geo.context.eq(context) & geo.regular_session]
        for day in input_days:
            selected = eligible.index[eligible.session_date_et < day].to_numpy(int)[-60:]
            if len(selected) < 60:
                continue
            sample = moves[selected].copy()
            day_open = clock.calendar.loc[str(day) : str(day)].iloc[0]["open"]
            sample[mature_ns[selected] >= pd.Timestamp(day_open).value] = np.nan
            mean = rolling(sample[-20:], 20, 19)[-1]
            rms = rolling(sample, 60, 57, True)[-1]
            positions = grid.index[grid.session_date_et == day]
            components.m2_mean[positions, :, context] = mean
            components.m2_rms[positions, :, context] = rms
        print("M2 context", context, "cached", flush=True)
    blocked = (
        components.hours.pivot(index="hour_start_utc", columns="ticker", values="cop_dependency")
        .reindex(index=grid.hour_start_utc, columns=SYMBOLS)
        .to_numpy(bool)
    )
    components.m2_mean[blocked] = np.nan
    components.m2_rms[blocked] = np.nan
    registry = json.loads(Path("trading/track2/stage012/original_bundles.json").read_text())[
        "bundles"
    ]
    for year, row in registry.items():
        recipe = json.loads(Path(row["recipe"]).read_text())
        common, m2 = scaled(components, recipe)
        raw_common, raw_m2 = native(components, recipe["floors"])
        np.save(folder / f"{year}_common.npy", common)
        np.save(folder / f"{year}_m2.npy", m2)
        np.save(folder / f"{year}_missing_common.npy", ~np.isfinite(raw_common))
        np.save(folder / f"{year}_missing_m2.npy", ~np.isfinite(raw_m2))
        print("Original recipe", year, "cached", flush=True)
    # Opening-reference existence,not future endpoint completeness.
    opens = adjusted.loc[
        adjusted.timestamp.isin(pd.DatetimeIndex(geo.loc[geo.slot == "09:30", "entry_end_utc"]))
    ]
    opens[["ticker", "timestamp", "open"]].to_parquet(folder / "opening_refs.parquet", index=False)
    publish(folder / "source_receipts.json", source.receipts)
    identities = [
        {"path": f.name, "sha256": file_hash(f), "bytes": f.stat().st_size}
        for f in sorted(folder.iterdir())
        if f.is_file() and f.suffix in (".npy", ".parquet", ".json")
    ]
    publish(
        folder / "CACHE_READY.json",
        {
            "version": REV,
            "plan_sha256": expected,
            "source_hash": source.hash,
            "elapsed_seconds": time.monotonic() - start,
            "grid_hours": len(grid),
            "movement_origins": len(geo),
            "identities": identities,
            "original_helper_genesis_passes": 1,
            "financial_computations": 0,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["plan", "build"])
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--hash")
    parser.add_argument("--cache", type=Path)
    args = parser.parse_args()
    if args.action == "plan":
        prepare_plan(args.plan)
    elif args.hash and args.cache:
        cache_build(args.plan, args.hash, args.cache)
    else:
        parser.error("build requires hash/cache")


if __name__ == "__main__":
    main()
