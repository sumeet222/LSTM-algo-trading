"""Independent original-TG20 prediction arithmetic; no optimizer or checkpoint selection."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .hf1m_action_audit import SYMBOLS


def weights(frame: pd.DataFrame) -> np.ndarray:
    """Equal day, equal surviving origin per day, equal stock within that origin."""
    origins = frame.groupby("session_date_et").origin_id.transform("nunique").to_numpy()
    stocks = frame.groupby(["session_date_et", "origin_id"]).ticker.transform("size").to_numpy()
    return 1 / (frame.session_date_et.nunique() * origins * stocks)


def summary(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return dict(rows=0, status="UNAVAILABLE: empty population")
    y = frame.actual_TG20.to_numpy(dtype=np.float64)
    p = frame.pred_original_TG20.to_numpy(dtype=np.float64)
    if not np.isfinite([y, p]).all():
        raise ValueError("P021_FINITE_DIAGNOSTIC_REQUIRED")
    w = weights(frame)
    mse = float(w @ ((p - y) ** 2))
    zero = float(w @ (y * y))
    p2 = float(w @ (p * p))
    yp = float(w @ (y * p))
    discrepancy = abs((mse - zero) - (p2 - 2 * yp))
    if discrepancy > 1e-10:
        raise ValueError("P021_ZERO_DECOMPOSITION_REQUIRED")
    return dict(
        rows=len(frame),
        origins=frame.origin_id.nunique(),
        sessions=frame.session_date_et.nunique(),
        weighting=(
            "equal session / surviving origin / surviving stocks; full population has20stocks"
        ),
        mse=mse,
        mae=float(w @ abs(p - y)),
        rmse=float(np.sqrt(mse)),
        zero_mse=zero,
        excess_mse=mse - zero,
        improvement_ratio=(zero - mse) / zero if zero > 0 else None,
        prediction_squared=p2,
        twice_target_prediction=2 * yp,
        decomposition_error=discrepancy,
        unweighted_mse=float(np.mean((p - y) ** 2)),
        unweighted_zero_mse=float(np.mean(y * y)),
        prediction_mean=float(w @ p),
        prediction_sd=float(np.sqrt(w @ ((p - w @ p) ** 2))),
        actual_mean=float(w @ y),
        actual_sd=float(np.sqrt(w @ ((y - w @ y) ** 2))),
        negative_fraction=float(w @ (y < 0)),
        positive_fraction=float(w @ (y > 0)),
        tie_fraction=float(w @ (y == 0)),
        sign_hit=float(w @ (np.sign(y) == np.sign(p))),
        sign_convention="exact sign equality; zero is separate class",
        **{
            f"prediction_p{int(q * 100):02d}": float(np.quantile(p, q))
            for q in (0.01, 0.05, 0.5, 0.95, 0.99)
        },
    )


def origin_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """20-name Spearman with average ranks; constant predictions yield undefined IC."""
    result = []
    for (day, o), f in frame.groupby(["session_date_et", "origin_id"], sort=True):
        if len(f) != 20 or set(f.ticker) != set(SYMBOLS):
            raise ValueError("P021_IC_REQUIRES_COMPLETE20")
        y = f.set_index("ticker").reindex(SYMBOLS).actual_TG20
        p = f.set_index("ticker").reindex(SYMBOLS).pred_original_TG20
        ry = y.rank(method="average").to_numpy()
        rp = p.rank(method="average").to_numpy()
        a, b = ry - ry.mean(), rp - rp.mean()
        norm = float(np.linalg.norm(a) * np.linalg.norm(b))
        ic = float(a @ b / norm) if norm > 0 else np.nan
        top_y = set(np.argsort(-y.to_numpy(), kind="stable")[:4])
        top_p = set(np.argsort(-p.to_numpy(), kind="stable")[:4])
        bottom_y = set(np.argsort(y.to_numpy(), kind="stable")[:4])
        bottom_p = set(np.argsort(p.to_numpy(), kind="stable")[:4])
        result.append(
            dict(
                session_date_et=day,
                origin_id=o,
                rank_ic=ic,
                zero_rank_ic=np.nan,
                zero_reference_plot_only=0.0,
                top4_overlap=len(top_y & top_p),
                top4_recall=len(top_y & top_p) / 4,
                bottom4_overlap=len(bottom_y & bottom_p),
                bottom4_recall=len(bottom_y & bottom_p) / 4,
                rank_tie_policy=(
                    "average for IC; canonical stock order for top/bottom boundary ties"
                ),
            )
        )
    return pd.DataFrame(result)


def daily_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    origins = origin_metrics(frame)
    return origins.groupby("session_date_et", as_index=False).agg(
        rank_ic=("rank_ic", "mean"),
        origin_count=("origin_id", "size"),
        top4_recall=("top4_recall", "mean"),
        bottom4_recall=("bottom4_recall", "mean"),
    )


def grouped(frame: pd.DataFrame, by: str) -> pd.DataFrame:
    """Diagnostic groups never change checkpoint selection or fitted thresholds."""
    records = []
    for key, f in frame.groupby(by, dropna=False, sort=True):
        records.append(dict(group=str(key), **summary(f)))
    return pd.DataFrame(records)
