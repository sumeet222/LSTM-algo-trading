"""P020 strict indexed batch loader; no model, older studies, or protected data access."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_audit import REVISION, SYMBOLS, digest
from .hf1m_ft16_source import COMMON, CONFIG, ORDER, checked, configuration, verify_parent


@dataclass
class ModelInput:
    rows: pd.DataFrame
    common: np.ndarray
    m2: np.ndarray
    targets: pd.DataFrame
    fit_version: str
    fit: dict

    def batch(self, positions: tuple[int, ...], target_mode: str = "C0") -> dict[str, np.ndarray]:
        """Exactly20×48×16 per origin; C0/T2 share immutable inputs and population."""
        if target_mode not in {"C0", "T2"}:
            raise ValueError("P020_TARGET_MODE")
        x = []
        y = []
        for position in positions:
            if position < 0 or position >= len(self.rows):
                raise IndexError("P020_BATCH_POSITION")
            row = self.rows.iloc[position]
            end = int(row.entry_index)
            start = int(row.first_step)
            if end - start != 47 or str(row.session_date_et) >= "2026-01-01":
                raise ValueError("P020_PROTECTED_OR_CONTEXT_ACCESS")
            o = pd.Timestamp(row.entry_end_utc).tz_convert("America/New_York").hour - 10
            if o not in (0, 1):
                raise ValueError("P020_ORIGIN_CLOCK")
            common = self.common[start : end + 1].transpose(1, 0, 2)
            m2 = self.m2[start : end + 1, :, o].T
            tensor = np.empty((20, 48, 16), dtype=np.float32)
            for k, name in enumerate(ORDER):
                tensor[:, :, k] = m2 if name == "M2" else common[:, :, COMMON.index(name)]
            label = (
                self.targets.loc[self.targets.origin_id.eq(row.origin_id)]
                .set_index("ticker")
                .reindex(SYMBOLS)
            )
            values = label.TG20.to_numpy(dtype=np.float32)
            if values.shape != (20,) or not label.label_eligible.all():
                raise ValueError("P020_COMPLETE20_LABEL_REQUIRED")
            x.append(tensor)
            y.append(values)
        inputs = np.stack(x)
        targets = np.stack(y)
        if not np.isfinite(inputs).all() or not np.isfinite(targets).all():
            raise ValueError("P020_FINITE_BATCH_REQUIRED")
        if target_mode == "T2":
            targets = np.arcsinh(targets / self.fit["t2_scale"]).astype(np.float32)
        return {"x": inputs, "y": targets}


def load_model_input(contract_path: Path, *, split: str, fit_version: str) -> ModelInput:
    """Only four frozen permitted splits; protected credentials cannot bypass the API."""
    if split not in {"inner_train", "inner_validation", "refit", "development"}:
        raise ValueError("P020_PROTECTED_OR_UNKNOWN_SPLIT_DENIED")
    required = "inner" if split.startswith("inner") else "refit"
    if fit_version != required:
        raise ValueError("P020_SPLIT_FIT_MISMATCH")
    d = json.loads(contract_path.read_text())
    c = configuration()
    if (
        d.get("revision") != REVISION
        or tuple(d.get("symbols", [])) != SYMBOLS
        or tuple(d.get("feature_order", [])) != ORDER
        or d.get("feature_id") != c["feature_id"]
        or d.get("target_id") != c["target_id"]
        or d.get("model_input_id") != c["model_input_id"]
        or d.get("parent_namespace") != c["parent_namespace"]
        or d.get("lookback") != 48
        or d.get("maximum_numeric_date") != "2025-12-31"
        or d.get("protected_numeric_access") is not False
        or d.get("upstream_gate_sha256") != c["upstream_gate_sha256"]
    ):
        raise ValueError("STOP_IDENTITY: P020 contract required; no legacy fallback")
    if Path(d["config"]["path"]) != CONFIG:
        raise ValueError("STOP_IDENTITY: wrong config reference")
    if (
        Path(d["fit_recipes"]["path"]) != contract_path.parent / "train_only_fit_recipes.json"
        or d["root_register_sha256"] != c["root_register_sha256"]
    ):
        raise ValueError("STOP_IDENTITY: recipe or root reference")
    checked(d["config"])
    verify_parent(c)
    up = Path(c["upstream_packet"])
    if d["action_ledger_sha256"] != digest(up / "unresolved_event_ledger_v3.json"):
        raise ValueError("STOP_IDENTITY: stale ledger")
    root = Path("data/processed/hf20_hf1m_long_v1_ft16_v1") / contract_path.parent.name
    for reference in d["files"].values():
        if Path(reference["path"]).parent != root:
            raise ValueError("STOP_IDENTITY: numeric store mixing")
        checked(reference)
    recipes = json.loads(checked(d["fit_recipes"]).read_text())
    rows = pd.read_parquet(checked(d["files"]["origins"]))
    if rows.session_date_et.ge("2026-01-01").any():
        raise ValueError("P020_PROTECTED_ROWS_DENIED")
    rows = rows.loc[rows[split + "_admitted"]].reset_index(drop=True)
    if len(rows) != d["split_counts"][split]:
        raise ValueError("P020_POPULATION_CHANGED")
    recipe = recipes[fit_version]
    expected = "2023-01-23" if fit_version == "inner" else "2025-06-30"
    if recipe["fit_stop_inclusive"] != expected:
        raise ValueError("P020_FIT_CUTOFF")
    with np.load(checked(d["files"]["components"]), allow_pickle=False) as arrays:
        if tuple(arrays["symbols"]) != SYMBOLS or tuple(arrays["feature_order"]) != ORDER:
            raise ValueError("P020_COMPONENT_ORDER")
        if str(arrays["feature_id"]) != c["feature_id"]:
            raise ValueError("P020_FEATURE_VERSION")
        common = arrays[fit_version + "_scaled_common"]
        m2 = arrays[fit_version + "_scaled_m2"]
    targets = pd.read_parquet(checked(d["files"]["targets"]))
    if targets.session_date_et.ge("2026-01-01").any():
        raise ValueError("P020_PROTECTED_LABEL_ACCESS")
    targets = targets.loc[targets.fit_version.eq(fit_version)]
    return ModelInput(rows, common, m2, targets, fit_version, recipe)


def inverse_t2(prediction: np.ndarray, scale: float) -> np.ndarray:
    """Once-only mathematical inverse; callers keep explicit prediction-space metadata."""
    if scale <= 0 or not np.isfinite(scale):
        raise ValueError("POSITIVE_T2_SCALE_REQUIRED")
    return scale * np.sinh(prediction)
