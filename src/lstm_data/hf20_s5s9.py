"""S5 causal clock context and three separate S9 proper-scoring tasks."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.nn import functional as F

from .dm_quantile_loss import outputs as qr_outputs
from .hf1m_ft16_fit import quantile
from .hf1m_ft16_source import COMMON
from .hf20_ranking import origin_weights
from .hf20_s4_clock import sessions
from .hf20_s4_data import S4Data
from .hf20_s4_run import source_data
from .neural_engine import SharedLSTM, seed_all

S4 = Path("reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation")
ARMS = ("META-T2R", "MAG", "EVENT", "QUANTILE")
RUNS = tuple(
    f"HF20-{'S5' if arm == 'META-T2R' else 'S9'}-F{year % 100}-H4-{arm}-S42"
    for arm in ARMS
    for year in range(2021, 2025)
)
META_FIELDS = (
    "step_sin",
    "step_cos",
    "session_boundary",
    "elapsed_scheduled_wall",
    "origin_sin",
    "origin_cos",
)


def model_for(arm: str) -> SharedLSTM:
    """Same one-layer h32/dropout .1 backbone; only input/head dimensions differ."""
    if arm not in ARMS:
        raise ValueError("S5S9_FROZEN_ARM")
    seed_all(42)
    model = SharedLSTM()
    if arm == "META-T2R":
        model.input_dim = 22
        model.lstm = nn.LSTM(22, 32, num_layers=1, batch_first=True)
    elif arm in ("EVENT", "QUANTILE"):
        model.head = nn.Linear(32, 3)
    return model.float()


def target_y(returns: np.ndarray, epsilon: float) -> np.ndarray:
    median = np.median(returns, axis=1, keepdims=True)
    mad = np.median(abs(returns - median), axis=1, keepdims=True)
    return (returns - median) / (mad + epsilon)


def row_objective(
    raw: torch.Tensor, r: torch.Tensor, y: torch.Tensor, arm: str, recipe: dict
) -> torch.Tensor:
    """Unweighted stock mean is applied by caller; rows retain their actual loss units."""
    if arm == "META-T2R":
        return (raw - torch.asinh(y / recipe["t2_scale"])).square()
    if arm == "MAG":
        return (raw - torch.log1p(r.abs() / recipe["magnitude_scale"])).square()
    if arm == "EVENT":
        cutoff = recipe["event_cutoff"]
        label = torch.where(y < -cutoff, 0, torch.where(y > cutoff, 2, 1))
        return F.cross_entropy(raw.reshape(-1, 3), label.reshape(-1), reduction="none").reshape_as(
            y
        )
    if arm == "QUANTILE":
        q = qr_outputs(raw, "QR1", recipe["t2_scale"])["quantiles_z"]
        error = torch.asinh(y / recipe["t2_scale"])[..., None] - q
        tau = torch.tensor([0.05, 0.5, 0.95], dtype=raw.dtype, device=raw.device)
        return torch.maximum(tau * error, (tau - 1) * error).mean(-1)
    raise ValueError("S5S9_FROZEN_ARM")


class Data:
    """Reuse exact S4 source/masks/recipes; metadata contains no source repair flags."""

    def __init__(self) -> None:
        self.base: S4Data = source_data(S4)
        grid = self.base.grid
        calendar = sessions("2010-07-01", "2024-12-31")
        opened = dict(zip(calendar.index.astype(str).str[:10], calendar.open))
        closed = dict(zip(calendar.index.astype(str).str[:10], calendar.close))
        start = pd.DatetimeIndex(grid.session_date_et.map(opened))
        end = pd.DatetimeIndex(grid.session_date_et.map(closed))
        hours = pd.DatetimeIndex(grid.hour_end_utc)
        position = np.asarray((hours - start) / (end - start), float)
        boundary = grid.session_date_et.ne(grid.session_date_et.shift()).to_numpy(float)
        elapsed = np.r_[1.0, np.diff(hours.to_numpy(dtype="datetime64[ns]").view("int64")) / 3.6e12]
        self.log_gap = np.log1p(elapsed)
        self.step = np.column_stack(
            [np.sin(2 * np.pi * position), np.cos(2 * np.pi * position), boundary]
        )
        rows = self.base.rows
        phase = (
            (rows.entry_end_utc - rows.session_open) / (rows.session_close - rows.session_open)
        ).to_numpy(float)
        self.origin = np.column_stack([np.sin(2 * np.pi * phase), np.cos(2 * np.pi * phase)])
        self.gap_cap = 1.0
        self.task_recipe: dict = {}
        if not np.isfinite(self.step).all() or (position < 0).any() or (position > 1).any():
            raise ValueError("S5_CALENDAR_METADATA")

    def phase(self, year: int, phase: str, recipe: dict) -> None:
        """Only apply an existing S4 FT16 recipe and caller-bound task recipe."""
        old = json.loads((S4 / f"F{year % 100}_{phase}_recipe.json").read_text())
        self.base.apply_recipe(year, phase, old)
        self.task_recipe = dict(old, **recipe)
        self.gap_cap = recipe.get("gap_cap", 1.0)

    def metadata(self, positions: np.ndarray) -> np.ndarray:
        rows = self.base.rows.iloc[positions]
        ix = rows.first_step.to_numpy(int)[:, None] + np.arange(48)
        meta = np.empty((len(rows), 48, 6), np.float32)
        meta[..., :3] = self.step[ix]
        meta[..., 3] = np.minimum(self.log_gap[ix] / self.gap_cap, 1.0)
        meta[..., 4:] = self.origin[positions, None, :]
        return np.broadcast_to(meta[:, None], (len(rows), 20, 48, 6))

    def arrays(self, positions: np.ndarray, arm: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        x, r, y = self.base.arrays(positions)
        if arm == "META-T2R":
            x = np.concatenate([x, self.metadata(positions)], axis=-1)
        return x, r, y

    def volatility(self, positions: np.ndarray) -> np.ndarray:
        """Undo only the frozen V2 affine scale; no new feature or outcome is consumed."""
        sc = self.base.recipe["scalers"]["V2"]
        end = self.base.rows.iloc[positions].entry_index.to_numpy(int)
        log_sigma = self.base.common[end, :, COMMON.index("V2")] * sc["scale"] + sc["center"]
        return np.exp(log_sigma.astype(float))


def fit_task(data: Data, year: int, phase: str, arm: str, out: Path) -> dict:
    """Caller authority must precede every prefix fit; never accepts validation/OOS rows."""
    from .hf20_s5s9_run import ensure

    ensure(out)
    role = "inner_train" if phase == "inner" else "refit"
    positions = data.base.positions(year, role)
    data.phase(year, phase, {})
    rows = data.base.rows.iloc[positions]
    r = data.base.returns[positions]
    y = target_y(r, data.base.recipe["epsilon"])
    weight = np.broadcast_to(origin_weights(rows.session_date_et.to_numpy())[:, None] / 20, r.shape)
    result: dict[str, str | int | float] = dict(
        year=year,
        phase=phase,
        role=role,
        origins=len(rows),
        fit_stop=data.base.plans[year][0]["inner_stop" if phase == "inner" else "refit_stop"],
    )
    numerator = abs(r - np.median(r, axis=1, keepdims=True))
    mad = np.median(numerator, axis=1, keepdims=True)
    for name, value, tau in (
        ("tail_y95", abs(y), 0.95),
        ("tail_y99", abs(y), 0.99),
        ("num95", numerator, 0.95),
        ("mad05", np.broadcast_to(mad, y.shape), 0.05),
        ("abs_r95", abs(r), 0.95),
        ("abs_r99", abs(r), 0.99),
    ):
        result[name] = quantile(value.ravel(), tau, weight.ravel())
    if arm == "META-T2R":
        used = np.unique((rows.first_step.to_numpy(int)[:, None] + np.arange(48)).ravel())
        result["gap_cap"] = max(float(np.quantile(data.log_gap[used], 0.99)), np.log(2.0))
    elif arm == "MAG":
        result["magnitude_scale"] = max(quantile(abs(r).ravel(), 0.5, weight.ravel()), 1e-8)
    elif arm == "EVENT":
        result["event_cutoff"] = float(np.quantile(abs(y), 0.95, method="linear"))
    elif arm != "QUANTILE":
        raise ValueError("S5S9_FROZEN_ARM")
    return result
