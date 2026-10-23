"""Unique-key P020 train-only native fallbacks, robust scales, TG20 and T2 contracts."""

from __future__ import annotations

import numpy as np

from .hf1m_action_audit import SYMBOLS
from .hf1m_ft16_math import Components
from .hf1m_ft16_source import BOUNDED, COMMON


def quantile(v: np.ndarray, q: float, w: np.ndarray | None = None) -> float:
    if w is None:
        return float(np.quantile(v, q))
    order = np.argsort(v, kind="stable")
    a = v[order]
    weights = w[order]
    return float(
        a[min(np.searchsorted(np.cumsum(weights) / weights.sum(), q, side="left"), len(a) - 1)]
    )


def robust(v: np.ndarray, w: np.ndarray | None = None) -> dict:
    if not len(v) or not np.isfinite(v).all():
        raise ValueError("FINITE_TRAIN_ONLY_FALLBACK_REQUIRED")
    center = quantile(v, 0.5, w)
    mad = quantile(np.abs(v - center), 0.5, w)
    iqr = (quantile(v, 0.75, w) - quantile(v, 0.25, w)) / 1.349
    sd = float(np.sqrt(np.average((v - np.average(v, weights=w)) ** 2, weights=w)))
    scale, method = (
        (mad, "MAD")
        if mad > 0
        else (iqr, "IQR_1.349")
        if iqr > 0
        else (sd, "POPULATION_SD")
        if sd > 0
        else (1.0, "EXACT_CONSTANT_SCALE1")
    )
    return {"center": center, "scale": scale, "method": method, "n": len(v)}


def positive_floor(v: np.ndarray) -> float:
    values = v[np.isfinite(v) & (v > 0)]
    if not len(values):
        raise ValueError("POSITIVE_TRAIN_ONLY_FLOOR_REQUIRED")
    return float(np.percentile(values, 5))


def native(c: Components, floors: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    v = c.values
    shape = c.source["close"].shape
    h = np.asarray([p["hourly_floor"] for p in floors])
    d = np.asarray([p["daily_floor"] for p in floors])
    qh = np.full(shape, np.nan)
    qd = np.full(shape, np.nan)
    for j, p in enumerate(floors):
        for regime, value in p["volume_pseudocounts"].items():
            qh[c.hourly_volume_basis[:, j] == regime, j] = value["hour"]
            qd[c.hourly_volume_basis[:, j] == regime, j] = value["day"]
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = {
            "M1": v["OC"] / np.maximum(v["RMS60"], h),
            "M3": v["MOM5"] / (np.sqrt(5) * np.maximum(v["RMS63"], d)),
            "M4": v["MOM105"] / (np.sqrt(105) * np.maximum(v["RMS63"], d)),
            "V1": np.log(np.maximum(v["RMS12"], h)),
            "V2": np.log(np.maximum(v["RMS60"], h)),
            "Q1": np.log((v["VOLUME_H"] + qh) / (v["Q1_MEAN"] + qh)),
            "Q2": np.log((v["Q2_5"] + qd) / (v["Q2_60"] + qd)),
        }
    raw["V3"] = raw["V1"] - raw["V2"]
    for name in ["B1", "B2", "T1", "T2", "T3", "T4", "T5"]:
        raw[name] = v[name]
    common = np.stack([raw[name] for name in COMMON], axis=-1)
    floor = np.asarray([p["m2_floor"] for p in floors])[None, :, None]
    m2 = c.m2_mean / np.maximum(c.m2_rms, floor)
    return common, m2


def fit(c: Components, fit_hours: np.ndarray, stop: str) -> tuple[dict, dict[str, np.ndarray]]:
    """Prefix membership uses input availability only, never future return values."""
    if not fit_hours.any() or (c.grid.loc[fit_hours, "session_date_et"] > stop).any():
        raise ValueError("TRAIN_FIT_PREFIX_REQUIRED")
    daily_fit = (c.regular_days >= "2011-04-01") & (c.regular_days <= stop)
    unique_day = c.grid.loc[fit_hours].drop_duplicates("session_date_et").index.to_numpy(dtype=int)
    floors = []
    for j, symbol in enumerate(SYMBOLS):
        regimes = {}
        for regime in sorted(set(c.hourly_volume_basis[fit_hours, j])):
            hv = c.source["volume_for_feature"][
                fit_hours & (c.hourly_volume_basis[:, j] == regime), j
            ]
            dv = c.daily_volume[daily_fit & (c.daily_basis[:, j] == regime), j]
            hv = hv[np.isfinite(hv) & (hv > 0)]
            dv = dv[np.isfinite(dv) & (dv > 0)]
            # Missing entire training regime population stays missing, not a borrowed share unit.
            if len(hv) and len(dv):
                regimes[regime] = {
                    "hour": 0.01 * float(np.median(hv)),
                    "day": 0.01 * float(np.median(dv)),
                    "hour_n": len(hv),
                    "day_n": len(dv),
                }
        positive = c.m2_rms[unique_day, j, :]
        vals = []
        weights = []
        for o in (0, 1):
            x = positive[:, o]
            x = x[np.isfinite(x) & (x > 0)]
            if not len(x):
                raise ValueError("BOTH_M2_ORIGINS_REQUIRED")
            vals.append(x)
            weights.append(np.full(len(x), 0.5 / len(x)))
        floors.append(
            {
                "symbol": symbol,
                "hourly_floor": positive_floor(
                    np.concatenate(
                        [c.values["RMS12"][fit_hours, j], c.values["RMS60"][fit_hours, j]]
                    )
                ),
                "daily_floor": positive_floor(c.values["RMS63"][unique_day, j]),
                "m2_floor": quantile(np.concatenate(vals), 0.05, np.concatenate(weights)),
                "volume_pseudocounts": regimes,
            }
        )
    raw, m2 = native(c, floors)
    scaled = raw.copy()
    imputed = ~np.isfinite(raw)
    m2imputed = ~np.isfinite(m2)
    scalers = {}
    fallbacks = {}
    for k, name in enumerate(COMMON):
        x = raw[fit_hours, :, k]
        x = x[np.isfinite(x)]
        if not len(x):
            raise ValueError("STOP_FEATURE_UNSAFE: no native training population " + name)
        p = robust(x)
        fallbacks[name] = 0.0 if name in BOUNDED else p["center"]
        filled = np.where(np.isfinite(raw[:, :, k]), raw[:, :, k], fallbacks[name])
        if name in BOUNDED:
            scalers[name] = {"center": 0.0, "scale": 1.0, "method": "BOUNDED_IDENTITY", "n": len(x)}
            scaled[:, :, k] = filled
        else:
            scalers[name] = p
            scaled[:, :, k] = (filled - p["center"]) / p["scale"]
    vals = []
    weights = []
    for o in (0, 1):
        x = m2[unique_day, :, o]
        x = x[np.isfinite(x)]
        if not len(x):
            raise ValueError("M2_TRAIN_POPULATION_REQUIRED")
        vals.append(x)
        weights.append(np.full(len(x), 0.5 / len(x)))
    p = robust(np.concatenate(vals), np.concatenate(weights))
    scalers["M2"] = p
    fallbacks["M2"] = p["center"]
    filled = np.where(np.isfinite(m2), m2, p["center"])
    scaled_m2 = (filled - p["center"]) / p["scale"]
    arrays = {
        "native_common": raw,
        "native_m2": m2,
        "scaled_common": scaled.astype(np.float32),
        "scaled_m2": scaled_m2.astype(np.float32),
        "fallback_common": imputed,
        "fallback_m2": m2imputed,
    }
    if not np.isfinite(arrays["scaled_common"]).all() or not np.isfinite(arrays["scaled_m2"]).all():
        raise ValueError("STOP_FEATURE_UNSAFE: nonfinite float32")
    recipe = {
        "fit_start": "2011-04-01",
        "fit_stop_inclusive": stop,
        "floors": floors,
        "scalers": scalers,
        "fallbacks": fallbacks,
        "unique_hour_timestamps": int(fit_hours.sum()),
        "unique_hour_stock_rows": int(fit_hours.sum()) * 20,
        "unique_m2_day_timestamps": len(unique_day),
        "fit_hour_indices": np.flatnonzero(fit_hours).tolist(),
        "fit_population": (
            "union of scheduled history keys in input-only eligible training origins, "
            "prefix-clipped; no window multiplicity; no development; M2 stock/day/origin50:50"
        ),
        "model_trained": False,
        "clipping": False,
    }
    return recipe, arrays


def target_values(returns: np.ndarray, epsilon: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Canonical complete20 price-only TG; missing one stock invalidates all20."""
    if returns.ndim != 2 or returns.shape[1] != 20:
        raise ValueError("EXACT20_TARGET_REQUIRED")
    median = np.median(returns, axis=1)
    mad = np.median(np.abs(returns - median[:, None]), axis=1)
    y = (returns - median[:, None]) / (mad[:, None] + epsilon)
    y[~np.isfinite(returns).all(axis=1)] = np.nan
    return y, median, mad
