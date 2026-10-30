"""Two fixed common magnitude calibrators and causal GARCH state arithmetic."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .hf20_classical_math import multiplier
from .hf20_mag_c3_io import GROUPS, effective_sessions


def fit_common(cal: pd.DataFrame, prediction: str) -> list[dict]:
    """Independent calibration-role rows only; positive LS with session shrinkage."""
    a, p, w = (cal[k].to_numpy(float) for k in ["A", prediction, "weight"])
    global_fit = multiplier(a, p, w)
    result = [
        dict(
            group="GLOBAL",
            family="G",
            **global_fit,
            n_eff=effective_sessions(cal),
            rho=1.0,
            k_global=global_fit["k"],
        )
    ]
    for group in GROUPS:
        mask = cal.category.eq(group).to_numpy()
        n = effective_sessions(cal.loc[mask])
        fit = multiplier(a[mask], p[mask], w[mask])
        rho = n / (n + 25.0)
        result.append(
            dict(
                group=group,
                family="IO",
                numerator=fit["numerator"],
                denominator=fit["denominator"],
                k_raw=fit["k"],
                k=rho * fit["k"] + (1 - rho) * global_fit["k"],
                n_eff=n,
                rho=rho,
                k_global=global_fit["k"],
            )
        )
    return result


def apply_common(
    frame: pd.DataFrame, prediction: str, coefficients: list[dict], family: str
) -> np.ndarray:
    """Apply saved coefficients; no labels are read."""
    chosen = [c for c in coefficients if c["family"] == family]
    if family == "G":
        factor = float(chosen[0]["k"])
    elif family == "IO":
        factor = frame.category.map({c["group"]: c["k"] for c in chosen}).to_numpy(float)
    else:
        raise ValueError("UNKNOWN_CALIBRATOR")
    result = frame[prediction].to_numpy(float) * factor
    if not np.isfinite(result).all() or (result < 0).any():
        raise ValueError("INVALID_CALIBRATED_FORECAST")
    return result


def next_variance(
    h: float, observed: float, mu: float, omega: float, alpha: float, beta: float
) -> float:
    """Given h_n and matured x_n, return h_(n+1), all in percent-return units."""
    value = omega + alpha * (observed - mu) ** 2 + beta * h
    if not np.isfinite(value) or value <= 0:
        raise ValueError("INVALID_CONDITIONAL_VARIANCE")
    return float(value)


def mature_prefix(maturities: np.ndarray, issue: int) -> int:
    """Equality is unavailable: only endpoint+2 minutes strictly before issue."""
    if (np.diff(maturities) < 0).any():
        raise ValueError("UNORDERED_MATURITY")
    return int(np.searchsorted(maturities, issue, side="left"))
