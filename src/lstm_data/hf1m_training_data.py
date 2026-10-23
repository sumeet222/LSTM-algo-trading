"""P021 source-specific whole-session adapter for immutable P020 inputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch

from .config import fingerprint
from .hf1m_action_audit import SYMBOLS
from .hf1m_ft16_loader import ModelInput, load_model_input
from .hf1m_ft16_source import COMMON, ORDER
from .neural_engine import SessionBatch

CONTRACT = Path(
    "reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122/model_input_contract.json"
)
COUNTS = {
    "inner_train": (4428, 2513),
    "inner_validation": (766, 459),
    "refit": (5210, 2980),
    "development": (183, 109),
}


@dataclass
class TrainingView:
    """Gather scheduled windows without materializing a duplicated dense dataset."""

    source: ModelInput
    split: str
    sessions: tuple[str, ...] = field(init=False)
    positions_by_session: tuple[tuple[int, ...], ...] = field(init=False)
    labels: np.ndarray = field(init=False)
    origin_slots: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        rows = self.source.rows
        if rows.session_date_et.ge("2026-01-01").any():
            raise ValueError("P021_PROTECTED_NUMERICS_DENIED")
        self.sessions = tuple(sorted(set(rows.session_date_et)))
        groups = rows.groupby("session_date_et", sort=True).indices
        self.positions_by_session = tuple(tuple(int(i) for i in groups[d]) for d in self.sessions)
        import pandas as pd

        self.origin_slots = np.array(
            [pd.Timestamp(v).tz_convert("America/New_York").hour - 10 for v in rows.entry_end_utc]
        )
        target = self.source.targets.set_index(["origin_id", "ticker"])
        keys = pd.MultiIndex.from_product([rows.origin_id, SYMBOLS])
        selected = target.reindex(keys)
        self.labels = selected.TG20.to_numpy(dtype=np.float32).reshape(-1, 20)
        if (
            not selected.label_eligible.all()
            or not np.isfinite(self.labels).all()
            or not np.isin(self.origin_slots, (0, 1)).all()
            or rows.origin_id.duplicated().any()
            or (rows.entry_index - rows.first_step).ne(47).any()
        ):
            raise ValueError("P021_COMPLETE20_UNIQUE_48_STEP_REQUIRED")

    def origin_batch(self, positions: tuple[int, ...]) -> dict[str, np.ndarray]:
        rows = self.source.rows.iloc[list(positions)]
        history = rows.first_step.to_numpy(dtype=np.int64)[:, None] + np.arange(48)
        common = self.source.common[history].transpose(0, 2, 1, 3)
        slots = self.origin_slots[list(positions)]
        m2 = self.source.m2[history, :, slots[:, None]].transpose(0, 2, 1)
        x = np.empty((len(positions), 20, 48, 16), dtype=np.float32)
        for i, name in enumerate(ORDER):
            x[..., i] = m2 if name == "M2" else common[..., COMMON.index(name)]
        if not np.isfinite(x).all():
            raise ValueError("P021_FINITE_INPUT_REQUIRED")
        return {"x": x, "y": self.labels[list(positions)]}

    def batch(self, positions: tuple[int, ...]) -> SessionBatch:
        days = tuple(self.sessions[i] for i in positions)
        indices = tuple(k for i in positions for k in self.positions_by_session[i])
        raw = self.origin_batch(indices)
        x = np.zeros((len(days), 2, 20, 48, 16), dtype=np.float32)
        y = np.zeros((len(days), 2, 20), dtype=np.float32)
        mask = np.zeros((len(days), 2), dtype=bool)
        day_positions = {d: i for i, d in enumerate(days)}
        for i, k in enumerate(indices):
            j = day_positions[self.source.rows.iloc[k].session_date_et]
            o = int(self.origin_slots[k])
            if mask[j, o]:
                raise ValueError("P021_DUPLICATE_SESSION_ORIGIN")
            x[j, o], y[j, o], mask[j, o] = raw["x"][i], raw["y"][i], True
        result = SessionBatch(
            days, torch.from_numpy(x), torch.from_numpy(y), torch.from_numpy(mask), 20
        )
        result.validate()
        return result

    def summary(self) -> dict:
        return dict(
            origins=len(self.source.rows),
            stock_rows=self.labels.size,
            sessions=len(self.sessions),
            population_sha256=fingerprint(self.source.rows.origin_id.tolist()),
            target_float32_sha256=fingerprint(self.labels.tolist()),
            fit_version=self.source.fit_version,
            scale=self.source.fit["t2_scale"],
            first_session=self.sessions[0],
            last_session=self.sessions[-1],
            weighting="equal session, equal admitted origins within session, equal20 stocks",
        )


def load_views(contract: Path = CONTRACT) -> dict[str, TrainingView]:
    """Use the released loader for every split; never access any older numeric study."""
    result = {}
    for split, expected in COUNTS.items():
        version = "inner" if split.startswith("inner") else "refit"
        source = load_model_input(contract, split=split, fit_version=version)
        sibling = result.get("inner_train" if version == "inner" else "refit")
        if sibling is not None:
            source.common, source.m2, source.targets = (
                sibling.source.common,
                sibling.source.m2,
                sibling.source.targets,
            )
        view = TrainingView(source, split)
        if (len(source.rows), len(view.sessions)) != expected:
            raise ValueError("P021_FROZEN_POPULATION_MISMATCH:" + split)
        result[split] = view
    return result
