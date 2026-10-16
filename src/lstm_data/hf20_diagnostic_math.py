"""Pure weighted HF20 postrun algebra and independent checkpoint-selection oracles."""

from __future__ import annotations

import numpy as np
import pandas as pd


def day_weights(frame: pd.DataFrame) -> np.ndarray:
    """Equal day, eligible origin within day, and stock within origin; no pooling shortcut."""
    if frame.empty or frame[["session", "origin", "symbol"]].duplicated().any():
        raise ValueError("UNIQUE_NONEMPTY_ORIGIN_STOCK_KEYS_REQUIRED")
    days = frame.session.nunique()
    origins = frame.groupby("session").origin.transform("nunique").to_numpy(dtype=float)
    stocks = frame.groupby(["session", "origin"]).symbol.transform("size").to_numpy(dtype=float)
    weights = 1 / (days * origins * stocks)
    if not np.isclose(weights.sum(), 1, rtol=0, atol=1e-12):
        raise ValueError("HIERARCHICAL_WEIGHT_MASS")
    return weights


def weighted_decomposition(y: np.ndarray, prediction: np.ndarray, weights: np.ndarray) -> dict:
    """Exact MSE difference, variance/mean terms, covariance and descriptive slope only."""
    y, p, w = (np.asarray(a, dtype=np.float64).reshape(-1) for a in (y, prediction, weights))
    if (
        not len(y)
        or len(y) != len(p)
        or len(y) != len(w)
        or not np.isfinite([y, p, w]).all()
        or (w < 0).any()
        or w.sum() <= 0
    ):
        raise ValueError("FINITE_MATCHED_POSITIVE_WEIGHT_POPULATION_REQUIRED")
    w = w / w.sum()
    ey, ep = float(w @ y), float(w @ p)
    ey2, ep2, eyp = float(w @ (y * y)), float(w @ (p * p)), float(w @ (y * p))
    vy, vp = float(w @ ((y - ey) ** 2)), float(w @ ((p - ep) ** 2))
    cov = float(w @ ((y - ey) * (p - ep)))
    mse = float(w @ ((y - p) ** 2))
    delta = mse - ey2
    algebra = ep2 - 2 * eyp
    if not np.isclose(delta, algebra, atol=2e-12, rtol=2e-12):
        raise ValueError("ZERO_MSE_ALGEBRA_INCONSISTENT")
    return dict(
        rows=len(y),
        E_y2=ey2,
        E_prediction2=ep2,
        E_y_prediction=eyp,
        MSE=mse,
        MAE=float(w @ np.abs(y - p)),
        delta_MSE_vs_ZERO=delta,
        amplitude_cost=ep2,
        alignment_benefit=2 * eyp,
        algebra_residual=delta - algebra,
        improvement_fraction_vs_ZERO=-delta / ey2 if ey2 else None,
        target_mean=ey,
        prediction_mean=ep,
        target_variance=vy,
        prediction_variance=vp,
        target_sd=float(np.sqrt(vy)),
        prediction_sd=float(np.sqrt(vp)),
        covariance=cov,
        weighted_Pearson=cov / np.sqrt(vy * vp) if vy > 0 and vp > 0 else None,
        diagnostic_slope_y_on_score=cov / vp if vp > 0 else None,
        mean_component=ep * ep - 2 * ey * ep,
        variance_covariance_component=vp - 2 * cov,
        relative_sign_accuracy=float(w @ (np.sign(y) == np.sign(p))),
        target_positive_fraction=float(w @ (y > 0)),
        target_negative_fraction=float(w @ (y < 0)),
        target_zero_fraction=float(w @ (y == 0)),
        prediction_negative_fraction=float(w @ (p < 0)),
        prediction_zero_fraction=float(w @ (p == 0)),
        prediction_positive_fraction=float(w @ (p > 0)),
    )


def quantiles(values: np.ndarray, absolute: bool = False) -> dict:
    """Pooled unique-observation descriptive quantiles; no fitted/deployable transform."""
    a = np.asarray(values, dtype=float).reshape(-1)
    if absolute:
        a = np.abs(a)
    if not len(a) or not np.isfinite(a).all():
        raise ValueError("FINITE_QUANTILE_POPULATION")
    return {
        **{f"q{q:g}": float(np.quantile(a, q / 100)) for q in (1, 5, 25, 50, 75, 95, 99, 99.9)},
        "minimum": float(a.min()),
        "maximum": float(a.max()),
        "rows": len(a),
    }


def selection_trace(values: list[float]) -> pd.DataFrame:
    """Independent strict0.999 qualifying-best calculation, not a new early-stop policy."""
    best = None
    selected = 0
    raw = None
    raw_epoch = 0
    patience = 0
    previous = None
    rows = []
    for epoch, value in enumerate(values, 1):
        if not np.isfinite(value) or value < 0:
            raise ValueError("FINITE_NONNEGATIVE_VALIDATION")
        before = best
        threshold = 0.999 * before if before is not None else None
        qualifies = best is None or value < 0.999 * best
        if raw is None or value < raw:
            raw, raw_epoch = value, epoch
        if qualifies:
            best, selected, patience = value, epoch, 0
        else:
            patience += 1
        rows.append(
            dict(
                epoch=epoch,
                validation_MSE=value,
                qualified_best_before=before,
                required_new_MSE_strictly_below=threshold,
                qualifying=qualifies,
                improvement_vs_previous=None if previous is None else previous - value,
                percent_improvement_vs_previous=None
                if previous is None
                else 100 * (previous - value) / previous,
                improvement_vs_qualifying_best=None if before is None else before - value,
                percent_improvement_vs_qualifying_best=None
                if before is None
                else 100 * (before - value) / before,
                required_relative_percent=0.1,
                patience=patience,
                selected_epoch=selected,
                raw_min=raw,
                raw_epoch=raw_epoch,
                stop_reason="PATIENCE_STOP"
                if epoch >= 12 and patience >= 10
                else "MAX_EPOCHS_REACHED"
                if epoch == 60
                else "CALIBRATING",
            )
        )
        previous = value
    return pd.DataFrame(rows)
