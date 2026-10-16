"""HF20 source boundary: key-only census and filtered pre-confirmation numeric reads."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq

from .config import digest
from .hf_hourly_audit import CORE, calendar_grid, quality_flags, require_schema

REVISION = "ad48edaf3828ec855ab4a5bb1b8336fa0b68cdec"
SYMBOLS = (
    "VZ",
    "COP",
    "BAC",
    "BA",
    "AAPL",
    "PEP",
    "MRK",
    "SBUX",
    "CVX",
    "MS",
    "AMD",
    "KO",
    "JNJ",
    "AMZN",
    "XOM",
    "WFC",
    "AVGO",
    "TSLA",
    "MA",
    "CSCO",
)
START = pd.Timestamp("2022-06-01", tz="America/New_York")
BARRIER = pd.Timestamp("2026-01-07", tz="America/New_York")
END = pd.Timestamp("2026-10-16", tz="America/New_York")
MANIFEST = Path(
    "reports/data_audit/ta_hf_twelvedata_hourly_2026-10-16_123344_final/acquisition_manifest.json"
)


def verify_source(manifest_path: Path = MANIFEST) -> dict:
    """Hash raw bytes without interpreting protected numeric columns."""
    manifest = json.loads(manifest_path.read_text())
    if manifest["revision"] != REVISION or len(manifest["files"]) != 3:
        raise ValueError("HF20_EXACT_SOURCE_REQUIRED")
    for row in manifest["files"]:
        path = Path(row["path"])
        if path.stat().st_size != row["bytes"] or digest(path) != row["sha256"]:
            raise ValueError("HF20_SOURCE_HASH_CHANGED")
        require_schema(pq.ParquetFile(path).schema_arrow)
    return manifest


def read_source(manifest: dict, *, keys_only: bool = False) -> pd.DataFrame:
    """Predicate applied by Arrow before Python materialization; never return held-out OHLCV.

    Parquet compression pages may contain both permitted and protected dates. The
    engine can decode those pages internally; protected numeric rows are never
    materialized into a Python frame, component store, diagnostic or model input.
    Key-only reads project no numeric columns and may census the full source span.
    """
    columns = ["datetime", "symbol"] if keys_only else list(CORE)
    stop = END if keys_only else BARRIER
    timestamp_type = pa.timestamp("us", tz="America/New_York")
    predicate = (
        ds.field("symbol").isin(SYMBOLS)
        & (ds.field("datetime") >= pa.scalar(START.to_pydatetime(), type=timestamp_type))
        & (ds.field("datetime") < pa.scalar(stop.to_pydatetime(), type=timestamp_type))
    )
    parts = []
    for row in manifest["files"]:
        dataset = ds.dataset(row["path"], format="parquet")
        part = dataset.to_table(columns=columns, filter=predicate).to_pandas()
        if not keys_only and part.datetime.ge(BARRIER).any():
            raise ValueError("HF20_CONFIRMATION_NUMERIC_ACCESS_DENIED")
        part["source_file"] = row["path"]
        part["source_sha256"] = row["sha256"]
        parts.append(part)
    frame = pd.concat(parts, ignore_index=True)
    frame["UTC"] = frame.datetime.dt.tz_convert("UTC")
    frame["session"] = frame.datetime.dt.tz_localize(None).dt.strftime("%Y-%m-%d")
    return frame.sort_values(["symbol", "UTC"]).reset_index(drop=True)


def bad_hours(keys: pd.DataFrame, permitted: pd.DataFrame) -> pd.DataFrame:
    """Exact expected defects, using keys only in the protected period."""
    grid, _ = calendar_grid("2022-06-01", "2026-10-15")
    expected = grid.loc[~grid.stub]
    indexed = keys.set_index(["symbol", "UTC"])
    validity = quality_flags(permitted).valid
    good = set(zip(permitted.loc[validity, "symbol"], permitted.loc[validity, "UTC"]))
    rows = []
    for symbol in SYMBOLS:
        observed = set(keys.loc[keys.symbol.eq(symbol), "UTC"])
        for row in expected.itertuples():
            start = pd.Timestamp(str(row.start))
            heldout = start >= BARRIER
            if start in observed and (heldout or (symbol, start) in good):
                continue
            present = (symbol, row.start) in indexed.index
            rows.append(
                dict(
                    symbol=symbol,
                    session=row.session,
                    interval_start_UTC=str(row.start),
                    interval_end_UTC=str(row.end),
                    interval_start_ET=str(start.tz_convert("America/New_York")),
                    reason="INVALID_SOURCE_ROW" if present else "ABSENT_CANONICAL_SOURCE_KEY",
                    numeric_inspected=not heldout,
                    held_out=heldout,
                    source_file=(
                        "train.parquet"
                        if str(row.session) < "2024-01-01"
                        else "val.parquet"
                        if str(row.session) < "2025-01-01"
                        else "test.parquet"
                    ),
                    repair="NO_OVERRIDE_PENDING_ALIGNMENT_AND_UNITS",
                )
            )
    return pd.DataFrame(rows)
