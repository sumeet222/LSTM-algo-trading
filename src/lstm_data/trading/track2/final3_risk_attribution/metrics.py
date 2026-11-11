"""Explicit daily risk arithmetic; no strategy, execution or price generation."""

from math import ceil

import numpy as np
import pandas as pd


def simple_returns(nav: np.ndarray, initial: float = 100000.0) -> np.ndarray:
    if len(nav) == 0 or not np.isfinite(nav).all() or np.any(nav <= 0) or initial <= 0:
        raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION INVALID_WEALTH")
    return nav / np.r_[initial, nav[:-1]] - 1


def ratio(numerator: float, denominator: float, minimum: float = 1e-12) -> float | None:
    return numerator / denominator if np.isfinite(denominator) and denominator > minimum else None


def tail(values: np.ndarray, alpha: float) -> dict:
    if len(values) == 0 or not np.isfinite(values).all() or not 0 < alpha < 1:
        raise ValueError("INVALID_TAIL_SAMPLE")
    k = max(1, ceil(alpha * len(values)))
    ix = np.argsort(values, kind="stable")[:k]
    return {
        "quantile": float(np.quantile(values, alpha, method="linear")),
        "VaR_loss": float(-np.quantile(values, alpha, method="linear")),
        "ES_loss": float(-values[ix].mean()),
        "tail_count": k,
        "indices": ix,
    }


def drawdowns(
    nav: np.ndarray, dates: list[str], initial: float = 100000.0
) -> tuple[dict, list[dict]]:
    simple_returns(nav, initial)
    if len(dates) != len(nav):
        raise ValueError("DRAWDDOWN_DATE_CENSUS")
    wealth = np.r_[initial, nav]
    high = np.maximum.accumulate(wealth)
    dd = wealth / high - 1
    labels = ["INITIAL_BEFORE_" + dates[0], *dates]
    episodes = []
    peak = 0
    start = None
    trough = None
    for n in range(1, len(wealth)):
        if wealth[n] >= wealth[peak]:
            if start is not None and trough is not None:
                episodes.append(
                    {
                        "peak_index": peak,
                        "peak_date": labels[peak],
                        "peak_NAV": float(wealth[peak]),
                        "trough_index": trough,
                        "trough_date": labels[trough],
                        "trough_NAV": float(wealth[trough]),
                        "drawdown": float(wealth[trough] / wealth[peak] - 1),
                        "time_to_trough_sessions": trough - peak,
                        "underwater_sessions": n - start,
                        "peak_to_recovery_sessions": n - peak,
                        "recovery_date": labels[n],
                        "recovered": True,
                        "episode_last_date": labels[n],
                    }
                )
            peak = n
            start = None
            trough = None
        else:
            if start is None:
                start = n
                trough = n
            elif trough is not None and wealth[n] < wealth[trough]:
                trough = n
    if start is not None and trough is not None:
        episodes.append(
            {
                "peak_index": peak,
                "peak_date": labels[peak],
                "peak_NAV": float(wealth[peak]),
                "trough_index": trough,
                "trough_date": labels[trough],
                "trough_NAV": float(wealth[trough]),
                "drawdown": float(wealth[trough] / wealth[peak] - 1),
                "time_to_trough_sessions": trough - peak,
                "underwater_sessions": len(wealth) - start,
                "peak_to_recovery_sessions": None,
                "recovery_date": None,
                "recovered": False,
                "episode_last_date": labels[-1],
            }
        )
    episodes.sort(key=lambda x: (x["drawdown"], x["peak_index"]))
    worst = episodes[0] if episodes else None
    return {
        "max_drawdown": float(dd.min()),
        "drawdown_severity": float(-dd.min()),
        "max_DD_time_to_trough_sessions": worst["time_to_trough_sessions"] if worst else 0,
        "max_DD_underwater_sessions": worst["underwater_sessions"] if worst else 0,
        "longest_underwater_sessions": max((e["underwater_sessions"] for e in episodes), default=0),
        "max_DD_recovered": worst["recovered"] if worst else True,
        "current_drawdown": float(dd[-1]),
        "total_underwater_sessions": int((dd < 0).sum()),
    }, episodes


def performance(
    nav: np.ndarray, dates: list[str], initial: float = 100000.0
) -> tuple[dict, list[dict]]:
    r = simple_returns(nav, initial)
    n = len(r)
    mean = float(r.mean())
    std = float(r.std(ddof=1)) if n > 1 else 0.0
    downside = float(np.sqrt(np.mean(np.minimum(r, 0) ** 2)))
    upside = float(np.sqrt(np.mean(np.maximum(r, 0) ** 2)))
    years = max((pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days / 365.25, 1 / 365.25)
    delta = np.diff(np.r_[initial, nav])
    dd, episodes = drawdowns(nav, dates, initial)
    five, one = tail(r, 0.05), tail(r, 0.01)
    out = {
        "sessions": n,
        "initial_NAV": initial,
        "final_NAV": float(nav[-1]),
        "net_PnL_USD": float(nav[-1] - initial),
        "total_return": float(nav[-1] / initial - 1),
        "CAGR": float((nav[-1] / initial) ** (1 / years) - 1),
        "calendar_years_for_CAGR": years,
        "mean_session_return": mean,
        "median_session_return": float(np.median(r)),
        "arithmetic_annual_return": mean * 252,
        "annual_volatility": std * np.sqrt(252),
        "Sharpe": ratio(mean * np.sqrt(252), std),
        "downside_deviation_daily": downside,
        "downside_semivol_annual": downside * np.sqrt(252),
        "upside_semivol_annual": upside * np.sqrt(252),
        "Sortino": ratio(mean * np.sqrt(252), downside),
        "loss_day_fraction": float(np.mean(r < 0)),
        "worst_daily_return": float(r.min()),
        "worst_daily_loss_USD": float(-delta.min()),
        "best_daily_return": float(r.max()),
        "daily_q01": one["quantile"],
        "daily_q05": five["quantile"],
        "daily_q25": float(np.quantile(r, 0.25)),
        "daily_q75": float(np.quantile(r, 0.75)),
        "daily_q95": float(np.quantile(r, 0.95)),
        "daily_q99": float(np.quantile(r, 0.99)),
        "VaR95_loss": five["VaR_loss"],
        "VaR99_loss": one["VaR_loss"],
        "ES95_loss": five["ES_loss"],
        "ES99_loss": one["ES_loss"],
        "ES95_tail_count": five["tail_count"],
        "ES99_tail_count": one["tail_count"],
        "upside_downside_semivol_ratio": ratio(upside, downside),
        **dd,
    }
    out["Calmar"] = ratio(out["CAGR"], out["drawdown_severity"])
    out["upside95_to_downside05_ratio"] = ratio(out["daily_q95"], -out["daily_q05"])
    return out, episodes


def nonexecutable_proxy(
    returns: np.ndarray, dates: list[str], control_level: float, s2c_level: float, kind: str
) -> dict:
    minimum = 1e-6 if kind == "MEAN_RTH_GROSS" else 1e-12
    scale = ratio(control_level, s2c_level, minimum)
    if scale is None or scale <= 0 or scale > 10 or np.any(1 + scale * returns <= 0):
        return {"status": "REFUSED_UNSTABLE_OR_NONPOSITIVE", "scale": scale}
    nav = 100000.0 * np.cumprod(1 + scale * returns)
    m, _ = performance(nav, dates)
    return {
        "status": "NONEXECUTABLE_ARITHMETIC_ONLY",
        "scale": scale,
        "scaled_proxy_total_return": m["total_return"],
        "scaled_proxy_net_USD": m["net_PnL_USD"],
        "scaled_proxy_annual_volatility": m["annual_volatility"],
        "scaled_proxy_downside_semivol_annual": m["downside_semivol_annual"],
        "scaled_proxy_ES95_loss": m["ES95_loss"],
        "scaled_proxy_ES99_loss": m["ES99_loss"],
        "scaled_proxy_drawdown_severity": m["drawdown_severity"],
        "scaled_proxy_Sharpe": m["Sharpe"],
        "scaled_proxy_Sortino": m["Sortino"],
    }
