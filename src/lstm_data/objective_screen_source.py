"""P022 phase-restricted reads of the immutable P020 release; no fitting."""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd

from .hf1m_action_audit import SYMBOLS
from .hf1m_ft16_loader import ModelInput
from .hf1m_ft16_source import COMMON, ORDER, checked
from .hf1m_training_data import COUNTS, TrainingView
from .visualization.hf1m_long import LongStudy


def prefix_array(path: Path, key: str, stop: int) -> np.ndarray:
    """Decode only a C-order time prefix, not later numeric values in an NPZ member."""
    if stop < 1:
        raise ValueError("P022_POSITIVE_PREFIX_REQUIRED")
    with ZipFile(path) as archive, archive.open(key + ".npy") as stream:
        version = np.lib.format.read_magic(stream)
        if version == (1, 0):
            shape, fortran, dtype = np.lib.format.read_array_header_1_0(stream)
        elif version == (2, 0):
            shape, fortran, dtype = np.lib.format.read_array_header_2_0(stream)
        else:
            raise ValueError("P022_NPY_VERSION")
        if fortran or dtype.hasobject or not shape or stop > shape[0]:
            raise ValueError("P022_C_ORDER_NUMERIC_PREFIX_REQUIRED")
        count = int(np.prod((stop, *shape[1:])))
        raw = stream.read(count * dtype.itemsize)
        if len(raw) != count * dtype.itemsize:
            raise ValueError("P022_TRUNCATED_COMPONENT")
        return np.frombuffer(raw, dtype=dtype).reshape((stop, *shape[1:]))


def scoped_view(study: LongStudy, split: str, *, stage: int) -> TrainingView:
    """Predicate-restrict Parquet rows before materializing labels; guard role first."""
    permitted = {"inner_train", "inner_validation"}
    if stage >= 2:
        permitted.add("refit")
    if stage >= 7:
        permitted.add("development")
    if split not in permitted or stage not in range(9):
        raise ValueError("P022_ROLE_NOT_AUTHORIZED_AT_STAGE")
    version = "inner" if split.startswith("inner") else "refit"
    d = study.contract
    origins = pd.read_parquet(
        checked(d["files"]["origins"]), filters=[(split + "_admitted", "=", True)]
    )
    stop = "2023-01-23" if split == "inner_train" else "2025-06-30"
    if split == "development":
        stop = "2025-12-31"
    if origins.session_date_et.gt(stop).any() or len(origins) != COUNTS[split][0]:
        raise ValueError("P022_ROLE_DATES_OR_COUNTS")
    target = pd.read_parquet(
        checked(d["files"]["targets"]),
        filters=[("fit_version", "=", version), ("origin_id", "in", origins.origin_id.tolist())],
    )
    if len(target) != len(origins) * 20 or target.session_date_et.gt(stop).any():
        raise ValueError("P022_TARGET_SCOPE")
    end = int(origins.entry_index.max()) + 1
    components = checked(d["files"]["components"])
    source = ModelInput(
        origins.reset_index(drop=True),
        prefix_array(components, version + "_scaled_common", end),
        prefix_array(components, version + "_scaled_m2", end),
        target,
        version,
        study.recipe(version),
    )
    view = TrainingView(source, split)
    if len(view.sessions) != COUNTS[split][1]:
        raise ValueError("P022_SESSION_COUNT")
    return view


def ordered_targets(view: TrainingView) -> pd.DataFrame:
    keys = pd.MultiIndex.from_product(
        [view.source.rows.origin_id, SYMBOLS], names=["origin_id", "ticker"]
    )
    return view.source.targets.set_index(["origin_id", "ticker"]).reindex(keys).reset_index()


def native_arrays(study: LongStudy, view: TrainingView) -> dict[str, np.ndarray]:
    path = checked(study.contract["files"]["components"])
    end = int(view.source.rows.entry_index.max()) + 1
    return {
        key: prefix_array(path, view.source.fit_version + "_" + key, end)
        for key in ("native_common", "native_m2", "fallback_common", "fallback_m2")
    }


def gather(
    view: TrainingView, arrays: dict[str, np.ndarray], positions: tuple[int, ...], kind: str
) -> np.ndarray:
    rows = view.source.rows.iloc[list(positions)]
    history = rows.first_step.to_numpy(dtype=np.int64)[:, None] + np.arange(48)
    slots = view.origin_slots[list(positions)]
    common = arrays[kind + "_common"][history].transpose(0, 2, 1, 3)
    m2 = arrays[kind + "_m2"][history, :, slots[:, None]].transpose(0, 2, 1)
    result = np.empty((len(rows), 20, 48, 16), dtype=common.dtype)
    for j, name in enumerate(ORDER):
        result[..., j] = m2 if name == "M2" else common[..., COMMON.index(name)]
    return result


def identity(study: LongStudy) -> dict:
    """Metadata only; safe before any numerical computation."""
    d = study.contract
    return {
        **{
            k: d[k]
            for k in (
                "source",
                "revision",
                "parent_namespace",
                "feature_id",
                "target_id",
                "model_input_id",
                "symbols",
                "feature_order",
                "tensor_shape_per_origin",
                "split_counts",
            )
        },
        "input_contract": study.plan["input_contract"],
        "source_hull": "2010-07 through 2026-03",
        "numeric_limit": "2025-12-31",
        "protected": "2026-01 through 2026-03 LOCKED",
        "baselines": ["P021 T2/42", "P021 T2/123", "ZERO", "C0 contextual"],
        "ledger": 36,
        "ceiling": 200,
    }


def assert_frozen_design(out: Path) -> dict:
    from .config import digest

    gate = json.loads((out / "stage_00_identity_design_gate.json").read_text())
    if gate["status"] != "PASS_FROZEN_DESIGN":
        raise ValueError("P022_STAGE0_REQUIRED")
    if digest(out / "frozen_design.json") != gate["design_sha256"]:
        raise ValueError("P022_FROZEN_DESIGN_CHANGED")
    return json.loads((out / "frozen_design.json").read_text())
