"""Whole-session HF20 adapter; no model fitting or source reconstruction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from .config import fingerprint
from .hf20_loader import HF20View, load_hf20_train_data
from .neural_engine import SessionBatch

CONTRACT = Path(
    "reports/data_audit/ta_hf20_pretraining_2026-10-16_160248/training_ready_input_contract.json"
)


@dataclass(frozen=True)
class TrainingView:
    """Preserve all admitted origins, padding only absent origins within a session."""

    source: HF20View

    @property
    def sessions(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.source.rows.session)))

    def batch(self, positions: tuple[int, ...]) -> SessionBatch:
        days = tuple(self.sessions[i] for i in positions)
        indices = tuple(int(i) for i in self.source.rows.index[self.source.rows.session.isin(days)])
        raw = self.source.batch(indices)
        x = np.zeros((len(days), 2, 20, 48, 16), dtype=np.float32)
        y = np.zeros((len(days), 2, 20), dtype=np.float32)
        mask = np.zeros((len(days), 2), dtype=bool)
        for i, (day, origin) in enumerate(zip(raw.sessions, raw.origins)):
            if not raw.label_valid[i]:
                raise ValueError("HF20_SUPERVISED_LABEL_REQUIRED")
            j, o = days.index(day), origin - 1
            if mask[j, o]:
                raise ValueError("HF20_DUPLICATE_ORIGIN")
            x[j, o], y[j, o], mask[j, o] = raw.x[i], raw.y[i], True
        result = SessionBatch(
            days, torch.from_numpy(x), torch.from_numpy(y), torch.from_numpy(mask), 20
        )
        result.validate()
        return result

    def summary(self) -> dict:
        return dict(
            origins=len(self.source.rows),
            sessions=len(self.sessions),
            population_sha256=fingerprint(self.source.rows[["session", "origin"]].values.tolist()),
            preparation_id=self.source.preparation_id,
            recipe_id=self.source.recipe_id,
        )


def load_views(contract: Path = CONTRACT) -> dict[str, TrainingView]:
    result = {
        split: TrainingView(
            load_hf20_train_data(
                contract, split=split, recipe="inner" if split.startswith("inner") else "refit"
            )
        )
        for split in ("inner_train", "inner_validation", "refit", "development")
    }
    expected = {
        "inner_train": (872, 436),
        "inner_validation": (110, 55),
        "refit": (998, 499),
        "development": (366, 183),
    }
    for name, view in result.items():
        if (len(view.source.rows), len(view.sessions)) != expected[name]:
            raise ValueError("HF20_BOUND_MASK_MISMATCH:" + name)
    return result


def target_values(view: TrainingView) -> np.ndarray:
    """One value per eligible origin-stock; no repeated lookback observations."""
    rows = view.source.rows
    values = np.stack(
        [
            view.source.targets[day, :, origin - 1]
            for day, origin in rows[["day_index", "origin"]].to_numpy(dtype=np.int64)
        ]
    )
    if values.shape != (len(rows), 20) or not np.isfinite(values).all():
        raise ValueError("HF20_EXACT_FINITE20_TARGET_REQUIRED")
    return values


def fit_scale(view: TrainingView, split: str) -> dict:
    if split not in ("inner_train", "refit"):
        raise ValueError("HF20_TRAIN_ONLY_SCALE")
    y = target_values(view).astype(np.float64)
    value = dict(
        split=split,
        scale=max(float(np.median(np.abs(y))), 1e-6),
        observations=y.size,
        target_sha256=fingerprint(y.tolist()),
        population="UNWEIGHTED_POOLED_UNIQUE_SESSION_ORIGIN_STOCK",
        floor=1e-6,
        **view.summary(),
    )
    return {**value, "scale_id": "HF20_T2:" + fingerprint(value)}
