"""Read-only equal-stock → equal-origin → equal-day summaries using frozen rank rules."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..pretraining_policy import CANDIDATE
from .loaders import ViewUnavailable


def origin_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    from ..real_bridge_run import rank_ic

    rows = []
    for (day, origin), group in frame.groupby(["session", "origin"], sort=True):
        if len(group) != 5 or set(group.symbol) != set(CANDIDATE):
            raise ViewUnavailable("Rank IC needs the complete five-stock cross-section.")
        ordered = group.set_index("symbol").loc[list(CANDIDATE)]
        ic, status = rank_ic(tuple(ordered.score), tuple(ordered.TG0))
        rows.append(
            {
                "session": day,
                "origin": origin,
                "MSE": float(group.squared_error.mean()),
                "IC": ic,
                "status": status,
                "tied_scores": group.score.nunique() < 5,
            }
        )
    return pd.DataFrame(rows)


def summary(frame: pd.DataFrame) -> dict:
    if frame.empty:
        raise ViewUnavailable("No observations for these filters.")
    origins = origin_metrics(frame)
    daily = origins.groupby("session")[["MSE", "IC"]].mean()
    return {
        "MSE": float(daily.MSE.mean()),
        "daily_Rank_IC": float(daily.IC.mean()) if daily.IC.notna().any() else None,
        "days": len(daily),
        "origins": len(origins),
        "stock_rows": len(frame),
        "tied_origins": int(origins.tied_scores.sum()),
        "defined_origins": int((origins.status == "DEFINED").sum()),
        "score_std": float(np.std(frame.score)),
        "daily": daily.reset_index(),
        "by_origin": origins.groupby("origin")[["MSE", "IC"]].mean().reset_index(),
    }


def matched(left: pd.DataFrame, right: pd.DataFrame) -> None:
    keys = ["session", "origin", "symbol"]
    a, b = left.sort_values(keys), right.sort_values(keys)
    if list(a[keys].itertuples(index=False, name=None)) != list(
        b[keys].itertuples(index=False, name=None)
    ) or not np.array_equal(a.TG0.to_numpy(), b.TG0.to_numpy()):
        raise ViewUnavailable("Different masks/targets; matched comparison rejected.")


def loss_concentration(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    from ..four_model_diagnostics import session_concentration

    origins = origin_metrics(frame)
    result = session_concentration(origins.session.tolist(), origins.MSE.to_numpy())
    daily = origins.groupby("session").MSE.mean().sort_values(ascending=False).reset_index()
    daily["loss_rank"] = np.arange(1, len(daily) + 1)
    daily["fraction_sessions"] = daily.loss_rank / len(daily)
    total = daily.MSE.sum()
    daily["cumulative_loss_share"] = daily.MSE.cumsum() / total if total else 0.0
    return daily, result
