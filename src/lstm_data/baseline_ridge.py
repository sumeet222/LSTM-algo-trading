"""Seven-snapshot pooled ridge, frozen mean-session objective, synthetic only."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from .baseline_authority import verify
from .baseline_inputs import BaselineInput, Prediction
from .config import fingerprint
from .ft0_transforms import identity
from .hourly_proxy import ProxyLabelSample, proxy_fitting_membership
from .labels import FitWindow, fitting_window
from .p3_domain import Permission, UniverseSpec, synthetic_id

LAGS = (0, 1, 2, 5, 11, 23, 47)
PENALTIES = (0.0001, 0.001, 0.01, 0.1, 1.0)
Stage = Literal["WF1", "WF2", "PRECONFIRMATION"]


def lag_vectors(
    row: BaselineInput,
    permission: Permission,
    *,
    market: bool = False,
    allow_synthetic: bool = False,
    context: str = "ASOF",
) -> tuple[tuple[float, ...], ...]:
    row.validate(permission, allow_synthetic=allow_synthetic, context=context)
    if market:
        row.validate_market(permission, allow_synthetic=allow_synthetic)
    vectors = []
    for stock in row.stock.values:
        values = []
        for lag in LAGS:
            for value in stock[47 - lag]:
                if value is None:
                    raise ValueError("NO_MISSING_RIDGE_CELL")
                values.append(value)
        if market:
            assert row.market is not None and row.market.values is not None
            values.extend(v for lag in LAGS for v in row.market.values[47 - lag])
        if len(values) != (147 if market else 112):
            raise ValueError("FROZEN_RIDGE_WIDTH_REQUIRED")
        vectors.append(tuple(values))
    return tuple(vectors)


@dataclass(frozen=True)
class RidgeOrigin:
    inputs: BaselineInput
    label: ProxyLabelSample

    def validate(self, universe: UniverseSpec) -> None:
        label = self.label
        if (
            self.inputs.universe != universe
            or self.inputs.basis != "SYNTHETIC"
            or not self.inputs.stock.synthetic
            or self.inputs.stock.source_only
            or not label.scenario_only
            or label.plan != self.inputs.plan
            or not label.label_valid
            or label.maturity_basis != "SYNTHETIC"
            or label.maturity is None
            or label.raw_returns is None
            or len(label.raw_returns) != 5
            or label.centered_returns is None
            or len(label.centered_returns) != 5
            or not all(np.isfinite(x) for x in label.raw_returns + label.centered_returns)
        ):
            raise ValueError("SYNTHETIC_COMPLETE_FIVE_TG0_ORIGIN_REQUIRED")
        for ref in label.references:
            if ref.row is None or ref.row.source != "SYNTHETIC" or ref.row.available_at is None:
                raise ValueError("SYNTHETIC_PROXY_LABEL_PROVENANCE_REQUIRED")
            synthetic_id(ref.row.row_id)


def session_weights(keys: tuple[tuple[str, int, str], ...]) -> np.ndarray:
    """One row per stock: 1/days/origins_per_day/5, never naive pooled weights."""
    if not keys or len(set(keys)) != len(keys):
        raise ValueError("UNIQUE_COMPLETE_RIDGE_ROW_KEYS_REQUIRED")
    groups: dict[tuple[str, int], set[str]] = {}
    for day, origin, symbol in keys:
        if origin not in (1, 2):
            raise ValueError("FROZEN_ORIGIN_REQUIRED")
        groups.setdefault((day, origin), set()).add(symbol)
    symbol_sets = list(groups.values())
    if any(len(s) != 5 or s != symbol_sets[0] for s in symbol_sets):
        raise ValueError("COMPLETE_SAME_FIVE_NAME_ORIGINS_REQUIRED")
    days = {day for day, _ in groups}
    counts = {day: sum(d == day for d, _ in groups) for day in days}
    return np.asarray([1 / len(days) / counts[day] / 5 for day, _, _ in keys], dtype=float)


@dataclass(frozen=True)
class Solution:
    intercept: float
    coefficients: tuple[float, ...]
    penalty: float
    condition: float
    residual_norm: float
    objective: float
    numpy_version: str
    solver: str = "WEIGHTED_CENTERED_NORMAL_SYSTEM_NUMPY_SOLVE"


def solve_weighted(x: np.ndarray, y: np.ndarray, weights: np.ndarray, penalty: float) -> Solution:
    """Small algebra kernel supports narrow hand oracles; public ridge is112/147."""
    if (
        penalty not in PENALTIES
        or x.ndim != 2
        or x.shape[1] < 1
        or x.shape[0] != len(y)
        or y.ndim != 1
        or weights.shape != y.shape
        or not np.isfinite(x).all()
        or not np.isfinite(y).all()
        or not np.isfinite(weights).all()
        or not (weights > 0).all()
        or abs(float(weights.sum()) - 1) > 1e-12
    ):
        raise ValueError("FINITE_MEAN_WEIGHTED_FROZEN_RIDGE_SYSTEM_REQUIRED")
    center = np.sum(x * weights[:, None], axis=0)
    mean_y = float(np.sum(y * weights))
    centered, target = x - center, y - mean_y
    system = (centered.T * weights) @ centered + penalty * np.eye(x.shape[1])
    rhs = centered.T @ (weights * target)
    condition = float(np.linalg.cond(system))
    if not np.isfinite(condition) or condition > 1e12:
        raise ValueError("RIDGE_ILL_CONDITIONED_SYSTEM")
    try:
        beta = np.linalg.solve(system, rhs)
    except np.linalg.LinAlgError as exc:
        raise ValueError("RIDGE_SOLVER_FAILURE_NO_FALLBACK") from exc
    intercept = mean_y - float(center @ beta)
    residual = float(np.linalg.norm(system @ beta - rhs))
    if (
        not np.isfinite(beta).all()
        or not np.isfinite(intercept)
        or residual > 1e-9 * max(1.0, float(np.linalg.norm(rhs)))
    ):
        raise ValueError("RIDGE_NONFINITE_OR_RESIDUAL_FAILURE")
    errors = y - intercept - x @ beta
    objective = float(np.sum(weights * errors**2) + penalty * (beta @ beta))
    return Solution(
        intercept,
        tuple(float(v) for v in beta),
        penalty,
        condition,
        residual,
        objective,
        np.__version__,
    )


@dataclass(frozen=True)
class RidgeModel:
    universe: UniverseSpec
    solution: Solution
    market: bool
    fitted_at: pd.Timestamp
    window: FitWindow
    scaler_id: str
    market_scaler_id: str | None
    floor_id: str
    input_hash: str
    model_id: str
    basis: str

    def __post_init__(self) -> None:
        synthetic_id(self.model_id)
        if self.basis != "SYNTHETIC" or len(self.solution.coefficients) != (
            147 if self.market else 112
        ):
            raise ValueError("SYNTHETIC_EXACT_WIDTH_RIDGE_MODEL_REQUIRED")

    def predict(
        self, row: BaselineInput, permission: Permission, *, allow_synthetic: bool = False
    ) -> Prediction:
        verify(permission)
        if (
            not allow_synthetic
            or self.basis != "SYNTHETIC"
            or row.universe != self.universe
            or row.stock.scaler_ref != self.scaler_id
            or row.plan.cutoff is None
            or self.fitted_at > row.plan.cutoff
            or (
                self.market
                and (row.market is None or row.market.scaler_ref != self.market_scaler_id)
            )
        ):
            raise ValueError("RIDGE_MODEL_ASOF_SOURCE_UNIVERSE_BINDING_REQUIRED")
        x = np.asarray(lag_vectors(row, permission, market=self.market, allow_synthetic=True))
        scores = x @ np.asarray(self.solution.coefficients) + self.solution.intercept
        return Prediction(
            self.universe,
            row.input_id + ":RIDGE",
            row.input_id,
            row.plan,
            tuple(float(v) for v in scores),
            "RIDGE_MARKET" if self.market else "RIDGE_OWN",
            self.model_id,
            "SYNTHETIC",
        )


def choose_penalty(losses: tuple[tuple[float, float], ...]) -> float:
    if (
        len(losses) != 5
        or {p for p, _ in losses} != set(PENALTIES)
        or any(not np.isfinite(loss) for _, loss in losses)
    ):
        raise ValueError("EXACT_FIVE_FINITE_VALIDATION_LOSSES_REQUIRED")
    return min(losses, key=lambda item: (item[1], -item[0]))[0]


def fitting_origins(origins: tuple[RidgeOrigin, ...], universe: UniverseSpec, window: FitWindow):
    accepted, rejected, keys = [], [], set()
    for row in origins:
        row.validate(universe)
        if row.label.key in keys:
            raise ValueError("DUPLICATE_RIDGE_ORIGIN")
        keys.add(row.label.key)
        reason = proxy_fitting_membership(row.label, window, test_scenario=True)
        (accepted if reason == "FIT_ELIGIBLE" else rejected).append(
            row if reason == "FIT_ELIGIBLE" else (row.label.key, reason)
        )
    return tuple(accepted), tuple(rejected)


def adequacy(origins: tuple[RidgeOrigin, ...]) -> dict:
    counts = {i: sum(r.label.plan.origin == i for r in origins) for i in (1, 2)}
    days = len({r.label.plan.session for r in origins})
    if days < 50 or min(counts.values()) < 25:
        raise ValueError("D6G_VALIDATION_50_DAYS_25_EACH_ORIGIN_REQUIRED")
    return {"sessions": days, "origins": counts}


def bind_model(
    universe: UniverseSpec,
    solution: Solution,
    market: bool,
    window: FitWindow,
    scaler_id: str,
    market_scaler_id: str | None,
    floor_id: str,
    input_hash: str,
) -> RidgeModel:
    if len(solution.coefficients) != (147 if market else 112):
        raise ValueError("PUBLIC_RIDGE_EXACT112_OR147_REQUIRED")
    model_id = "SYN:RIDGE:" + fingerprint(
        [
            universe.universe_id,
            identity(solution),
            window.window_id,
            scaler_id,
            market_scaler_id,
            floor_id,
            input_hash,
        ]
    )
    return RidgeModel(
        universe,
        solution,
        market,
        window.fitted_at,
        window,
        scaler_id,
        market_scaler_id,
        floor_id,
        input_hash,
        model_id,
        "SYNTHETIC",
    )


def windows(stage: Stage, fitted_at: pd.Timestamp) -> tuple[FitWindow, FitWindow, FitWindow]:
    return (
        fitting_window(stage, "INNER_TRAIN", fitted_at=fitted_at),
        fitting_window(stage, "INNER_VALIDATION", fitted_at=fitted_at),
        fitting_window(stage, "REFIT", fitted_at=fitted_at),
    )
