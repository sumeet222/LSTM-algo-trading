"""Preregistered descriptive analysis; historical admission is checked first.

No parameter selection or independence/significance claim. Cost addback is an
accounting decomposition on the actual holdings, not a frictionless rerun.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from .paths import publish
from .release import Admission, check_admission


def metrics(values: np.ndarray, dates: pd.DatetimeIndex, initial: float = 100000.0) -> dict:
    if (
        len(values) != len(dates)
        or not len(values)
        or not np.isfinite(values).all()
        or (values <= 0).any()
    ):
        return {"status": "UNDEFINED_NONPOSITIVE_OR_INCOMPLETE_NAV"}
    returns = values / np.r_[initial, values[:-1]] - 1
    sigma = float(returns.std(ddof=1)) if len(returns) > 1 else 0.0
    downside = float(np.sqrt(np.mean(np.minimum(returns, 0) ** 2)))
    high = np.maximum.accumulate(np.r_[initial, values])[1:]
    mdd = float(np.min(values / high - 1))
    years = (dates[-1] - pd.Timestamp("2021-01-01")).days / 365.25
    cagr = float((values[-1] / initial) ** (1 / years) - 1) if years > 0 else None
    return {
        "status": "OBSERVED_EXPLORATORY",
        "cumulative_return": float(values[-1] / initial - 1),
        "CAGR": cagr,
        "volatility_252": sigma * np.sqrt(252),
        "Sharpe_252": float(returns.mean() / sigma * np.sqrt(252)) if sigma else None,
        "Sortino_252": float(returns.mean() / downside * np.sqrt(252)) if downside else None,
        "maximum_daily_drawdown": mdd,
        "Calmar": cagr / abs(mdd) if cagr is not None and mdd else None,
        "days": len(values),
        "final_NAV": float(values[-1]),
    }


def analyze(folder: Path, admission: Admission) -> dict:
    check_admission(admission, "2021-01-01", "2024-12-31", False)
    output = {}
    paired = []
    for path in sorted(folder.glob("*/daily.jsonl.gz")):
        scenario = path.parent.name
        daily = pd.read_json(path, lines=True, compression="gzip")
        for account_key, part in daily.groupby(["arm", "population"], sort=True):
            if not isinstance(account_key, tuple) or len(account_key) != 2:
                raise ValueError("ACCOUNT_GROUP_SCHEMA")
            arm, population = account_key
            part = part.sort_values("date")
            dates = pd.DatetimeIndex(pd.to_datetime(part["date"]))
            key = f"{scenario}/{population}/{arm}"
            if (part.status != "OBSERVED").any() or part.nav.isna().any():
                output[key] = {
                    "status": "NAV_INCOMPLETE",
                    "unavailable_days": int(part.nav.isna().sum()),
                }
                continue
            nav = part.nav.to_numpy(float)
            result = metrics(nav, dates)
            result["costs"] = {
                name: float(part.iloc[-1][name])
                for name in (
                    "commission_cumulative",
                    "friction_cumulative",
                    "borrow_cumulative",
                    "funding_cumulative",
                )
            }
            result["mean_virtual_gross_to_NAV"] = float((part.gross / part.nav).mean())
            result["mean_own_cash_to_NAV"] = float((part.own_cash / part.nav).mean())
            result["rejections_attempt_counters_not_unique_opportunities"] = part.iloc[-1][
                "rejections_cumulative"
            ]
            overlay = part.proxy_standalone_cumulative.to_numpy(float)
            if np.any(overlay):
                result["standalone_yield_adjustment_final"] = float(overlay[-1])
                result["standalone_yield_adjusted_metrics"] = metrics(nav + overlay, dates)
                result["overlay_is_trading_cash_or_buying_power"] = False
            output[key] = result
            years = np.asarray([pd.Timestamp(value).year for value in dates], dtype=int)
            for year, chunk in part.groupby(years):
                mask = years == year
                first = int(np.flatnonzero(mask)[0])
                base = 100000.0 if first == 0 else nav[first - 1]
                annual = metrics(chunk.nav.to_numpy(float), pd.DatetimeIndex(dates[mask]), base)
                annual["CAGR"] = None
                annual["Calmar"] = None
                output[key + "/" + str(year)] = annual
            paired.append(part.assign(scenario=scenario))
        for kind in ("cohorts", "terminal_lots"):
            file = path.parent / (kind + ".jsonl.gz")
            if not file.exists():
                continue
            data = pd.read_json(file, lines=True, compression="gzip")
            if kind == "terminal_lots" and "snapshot_session" in data:
                data = data.loc[data.snapshot_session == data.snapshot_session.max()]
            if "arm" not in data:
                # Closed rows in the journal carry account identity in their key;
                # a missing explicit account field is never guessed for reporting.
                output[f"{scenario}/{kind}_attribution"] = {"status": "MISSING_EXPLICIT_ACCOUNT_ID"}
                continue
            if kind == "cohorts":
                executed = data.loc[data.entry_at.notna()].copy()
                for names, group in executed.groupby(
                    ["arm", "population", "ticker", "direction"], sort=True
                ):
                    output[f"{scenario}/closed_attribution/{names}"] = {
                        "cohorts": len(group),
                        "cash_pnl": float(group.cash_pnl.sum()),
                        "win_rate": float((group.cash_pnl > 0).mean()),
                        "fees": float(group.fees.sum()),
                        "borrow": float(group.borrow.sum()),
                    }
    if paired:
        all_daily = pd.concat(paired, ignore_index=True)
        for names, group in all_daily.groupby(["scenario", "population"]):
            pivot = group.pivot(index="date", columns="arm", values="nav")
            if "S2C_RISK" in pivot:
                for arm in ("EQUAL", "ROLLING_RISK", "EWMA_RISK"):
                    if arm in pivot:
                        delta = pivot["S2C_RISK"] - pivot[arm]
                        output[f"paired/{names}/S2C_MINUS_{arm}"] = {
                            "terminal_NAV_difference": float(delta.iloc[-1]),
                            "mean_daily_NAV_difference": float(delta.mean()),
                            "inference": "DESCRIPTIVE_ONLY",
                        }
    result = {
        "metrics": output,
        "independent_Stage6_complete": False,
        "selection_or_tuning": False,
        "gross_definition": (
            "netNAV plus accounting cost addback on same holdings;not counterfactual"
        ),
    }
    publish(folder / "DESCRIPTIVE_ANALYSIS.json", result)
    return result
