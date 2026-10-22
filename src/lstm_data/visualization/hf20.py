"""Read-only, independently locked HF20 saved-result and bounded-source reader."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

from ..config import digest
from ..hf20_replication_authority import IDS as REPLICATION_IDS
from ..hf20_source import SYMBOLS
from ..hf20_training_authority import IDS
from ..hf_hourly_audit import calendar_grid
from .loaders import ViewUnavailable

CONFIG = Path("configs/track_a_hf20_visualization_v1.json")
REPLICATION_CONFIG = Path("configs/track_a_hf20_replication_visualization_v1.json")
TARGET = "TG20_HF20_CROSS_SECTIONAL_V1"


def guard(
    start: str, end: str, symbol: str | None = None, run_id: str | None = None, *, seed: int = 42
) -> None:
    """Deny protected and wrong-family requests before any numerical I/O/cache lookup."""
    if not "2025-03-31" <= start <= end <= "2026-01-06":
        raise ViewUnavailable(
            "HF20 held-out locked: only 2025-03-31 through 2026-01-06 development."
        )
    if symbol is not None and symbol not in SYMBOLS:
        raise ViewUnavailable("HF20 fixed ordered20 names only.")
    if seed not in (42, 123):
        raise ViewUnavailable("Only the registered HF20 seeds42/123.")
    if run_id is not None and run_id not in (IDS if seed == 42 else REPLICATION_IDS):
        raise ViewUnavailable("Wrong study/model: only the two sealed HF20 runs.")


def verified(root: Path, ref: dict) -> Path:
    path = (root / ref["path"]).resolve()
    if (
        not path.is_relative_to(root.resolve())
        or not path.is_file()
        or digest(path) != ref["sha256"]
    ):
        raise ViewUnavailable("Missing or changed HF20 artifact: " + ref["path"])
    return path


def handoff(root: Path, seed: int = 42) -> dict:
    guard("2025-03-31", "2026-01-06", seed=seed)
    config_path = CONFIG if seed == 42 else REPLICATION_CONFIG
    ids = IDS if seed == 42 else REPLICATION_IDS
    if not (root / config_path).is_file():
        raise ViewUnavailable("HF20 result handoff absent; no fits are launched by this dashboard.")
    config = json.loads((root / config_path).read_text())
    h = json.loads(verified(root, config["handoff"]).read_text())
    if (
        h.get("target_id") != TARGET
        or h.get("symbols") != list(SYMBOLS)
        or h.get("runs") != list(ids)
        or h.get("seed", 42) != seed
        or h.get("score_units") != "CANONICAL_TG20"
        or h.get("T2_saved_inverse_count") != 1
        or h.get("heldout_numeric_rows") != 0
    ):
        raise ViewUnavailable("HF20 source/order/target/inverse identity denied.")
    c = json.loads(verified(root, h["input_contract"]).read_text())
    if any(
        h[k] != c[k] for k in ("source_revision", "feature_id", "target_id", "clock_id", "symbols")
    ):
        raise ViewUnavailable("HF20 input contract family differs from saved study.")
    for arm, run_id in zip(("C0", "T2"), ids):
        result = json.loads(verified(root, h["run_artifacts"][arm]["run_result"]).read_text())
        plan = json.loads(verified(root, result["plan"]).read_text())
        for name, sha in plan["code"].items():
            verified(root, dict(path="src/lstm_data/" + name, sha256=sha))
        if (
            result.get("run_id") != run_id
            or result.get("status") != "COMPLETED"
            or result.get("input_contract") != h["input_contract"]
            or result.get("scales") != h["scales"]
            or plan["scope"]["seed"] != seed
        ):
            raise ViewUnavailable("HF20 wrong seed/run/input/plan; no checkpoint fallback.")
        for key, stage, recipe in (
            ("calibration_checkpoint", "CALIBRATION_SELECTED", "inner"),
            ("refit_checkpoint", "REFIT_FINAL", "refit"),
        ):
            manifest = result[key]
            binding = manifest["binding"]
            if (
                binding["run_id"] != run_id
                or binding["seed"] != seed
                or binding["stage"] != stage
                or binding["symbols"] != list(SYMBOLS)
                or binding["recipe_id"] != c["recipe_ids"][recipe]
                or binding["preparation_id"] != c["preparation_id"]
                or binding["scale"]
                != (
                    plan["scales"]["inner_train" if recipe == "inner" else "refit"]
                    if arm == "T2"
                    else None
                )
                or binding["input_contract"] != h["input_contract"]
                or binding["target_id"] != TARGET
                or binding["arm"] != arm
                or binding["code_sha256"] != result["code_sha256"]
                or binding["plan"] != result["plan"]
                or binding["selected_epoch"] != result["selection"]["selected"]
                or binding["inverse"] != ("IDENTITY" if arm == "C0" else "SCALE_TIMES_SINH_ONCE")
            ):
                raise ViewUnavailable("HF20 checkpoint stage/seed/recipe/inverse identity denied.")
            verified(root, manifest["checkpoint"])  # Hash bytes; never load model weights in UI.
    return h


def table(root: Path, h: dict, key: str) -> pd.DataFrame:
    return pd.read_csv(verified(root, h["artifacts"][key]), float_precision="round_trip")


def predictions(
    root: Path, start: str, end: str, symbol: str, run_id: str, *, seed: int = 42
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    guard(start, end, symbol, run_id, seed=seed)
    h = handoff(root, seed)
    f = table(root, h, "matched_predictions_development.csv")
    if len(f) != 7320 or f.session.ge("2026-01-07").any() or not f.target_id.eq(TARGET).all():
        raise ViewUnavailable("HF20 exact development population/target denied.")
    for _, g in f.groupby(["session", "origin"], sort=False):
        if tuple(g.symbol) != SYMBOLS or not np.array_equal(g.symbol_index, np.arange(20)):
            raise ViewUnavailable("HF20 saved row order changed.")
    if (
        f[["session", "origin", "symbol"]].duplicated().any()
        or not np.isfinite(f[["target", "C0", "T2", "ZERO"]]).all().all()
    ):
        raise ViewUnavailable("HF20 duplicate/nonfinite predictions denied.")
    subset = f.loc[f.symbol.eq(symbol) & f.session.between(start, end)].copy()
    return h, f, subset


def feature_history(
    root: Path, h: dict, symbol: str, day: str, origin: int
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    guard(day, day, symbol)
    if origin not in (1, 2):
        raise ViewUnavailable("Only HF20 origins1/2.")
    c = json.loads(verified(root, h["input_contract"]).read_text())
    from ..hf20_features import COMMON
    from ..hf20_loader import load_hf20_train_data

    view = load_hf20_train_data(root / h["input_contract"]["path"], root=root)
    selected = view.rows.loc[view.rows.session.eq(day) & view.rows.origin.eq(origin)]
    if len(selected) != 1:
        raise ViewUnavailable("No admitted genuine origin for this date/time.")
    row = selected.iloc[0]
    position = int(selected.index[0])
    last = int(row.last_step)
    j = SYMBOLS.index(symbol)
    x = view.batch((position,)).x[0, j]
    with np.load(verified(root, c["store"]), allow_pickle=False) as s:
        indices = np.arange(last - 47, last + 1)
        ends = pd.to_datetime(s["ends_UTC"][indices], utc=True)
        native = s["native_refit"][indices, j, :]
        m2 = s["native_m2_refit"][s["day_index"][indices], j, origin - 1]
        records = []
        for k, name in enumerate(c["feature_order"]):
            values = m2 if name == "M2" else native[:, COMMON.index(name)]
            records.extend(
                dict(
                    step=i - 47,
                    end_UTC=str(ends[i]),
                    feature=name,
                    native=float(values[i]),
                    scaled=float(x[i, k]),
                )
                for i in range(48)
            )
        starts = pd.to_datetime(s["starts_UTC"][indices], utc=True)
    # Arrow predicate precedes materialization; no protected numerical application row is returned.
    frames = []
    timestamp_type = pa.timestamp("us", tz="America/New_York")
    first = starts[0].tz_convert("America/New_York")
    stop = pd.Timestamp(row.exit_proxy_reference_UTC).tz_convert("America/New_York")
    if stop >= pd.Timestamp("2026-01-07", tz="America/New_York"):
        raise ViewUnavailable("HF20 protected source read denied before I/O.")
    for ref in c["source"]:
        dataset = ds.dataset(verified(root, ref), format="parquet")
        predicate = (
            (ds.field("symbol") == symbol)
            & (ds.field("datetime") >= pa.scalar(first.to_pydatetime(), type=timestamp_type))
            & (ds.field("datetime") < pa.scalar(stop.to_pydatetime(), type=timestamp_type))
        )
        f = dataset.to_table(
            columns=["datetime", "symbol", "open", "high", "low", "close", "volume"],
            filter=predicate,
        ).to_pandas()
        frames.append(f)
    candles = pd.concat(frames).sort_values("datetime")
    if candles.datetime.ge(pd.Timestamp("2026-01-07", tz="America/New_York")).any():
        raise ViewUnavailable("HF20 protected numeric row denied.")
    # Only canonical full-hour starts, no off-grid/stub relabeling.
    grid, _ = calendar_grid(str(first.date()), str(stop.date()))
    canonical = pd.to_datetime(grid.loc[~grid.stub, "start"], utc=True)
    candles = candles.loc[candles.datetime.dt.tz_convert("UTC").isin(canonical)].copy()
    return (
        pd.DataFrame(records),
        candles,
        {
            k: str(row[k])
            for k in (
                "feature_cutoff_UTC",
                "forecast_issuance_UTC",
                "entry_proxy_reference_UTC",
                "exit_proxy_reference_UTC",
                "label_maturity_UTC",
            )
        },
    )
