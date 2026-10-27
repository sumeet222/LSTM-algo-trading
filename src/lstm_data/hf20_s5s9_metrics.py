"""Same-task controls and exact saved-output metrics for the S5/S9 campaign."""

from __future__ import annotations

import numpy as np
import pandas as pd
import torch

from .dm_quantile_loss import outputs
from .hf1m_ft16_fit import quantile
from .hf20_ranking import origin_ic, origin_weights, ranks
from .hf20_s5s9 import row_objective


def weights(days: np.ndarray) -> np.ndarray:
    return np.repeat(origin_weights(days) / 20, 20)


def probabilities(raw: np.ndarray) -> np.ndarray:
    shifted = raw - raw.max(-1, keepdims=True)
    p = np.exp(shifted)
    return p / p.sum(-1, keepdims=True)


def labels(y: np.ndarray, cutoff: float) -> np.ndarray:
    return np.where(y < -cutoff, 0, np.where(y > cutoff, 2, 1))


def decode(raw: np.ndarray, arm: str, recipe: dict) -> dict[str, np.ndarray]:
    if arm == "META-T2R":
        return dict(score=raw, inverse_TG20=recipe["t2_scale"] * np.sinh(raw.astype(float)))
    if arm == "MAG":
        return dict(
            prediction_m=raw,
            prediction_A=recipe["magnitude_scale"] * np.expm1(np.maximum(raw.astype(float), 0)),
        )
    if arm == "EVENT":
        p = probabilities(raw)
        return dict(
            p_NEG=p[..., 0], p_NORMAL=p[..., 1], p_POS=p[..., 2], p_ANY=p[..., 0] + p[..., 2]
        )
    q = outputs(torch.from_numpy(raw), "QR1", recipe["t2_scale"])
    return {
        f"{name}_{level}": value.numpy()[..., k]
        for name in ("quantiles_z", "quantiles_y")
        for k, level in enumerate(("05", "50", "95"))
        for value in (q[name],)
    }


def average_precision(actual: np.ndarray, score: np.ndarray, w: np.ndarray) -> float | None:
    """Threshold-grouped weighted AP; ties receive no artificial ordering advantage."""
    order = np.argsort(-score, kind="stable")
    s, a, ww = score[order], actual[order], w[order]
    ends = np.r_[np.flatnonzero(s[:-1] != s[1:]), len(s) - 1]
    tp = np.cumsum(a * ww)[ends]
    mass = np.cumsum(ww)[ends]
    return float(np.sum(np.diff(np.r_[0.0, tp]) * tp / mass) / tp[-1]) if tp[-1] else None


def auc(actual: np.ndarray, score: np.ndarray, w: np.ndarray) -> float | None:
    groups = (
        pd.DataFrame(dict(score=score, positive=w * actual, negative=w * (1 - actual)))
        .groupby("score")
        .sum()
    )
    p, n = groups.positive.to_numpy(), groups.negative.to_numpy()
    return (
        float((p * (np.cumsum(n) - n / 2)).sum() / (p.sum() * n.sum()))
        if p.sum() * n.sum()
        else None
    )


def weighted_rank_association(a: np.ndarray, b: np.ndarray, w: np.ndarray) -> float | None:
    x = pd.Series(a).rank().to_numpy(dtype=float, copy=True)
    y = pd.Series(b).rank().to_numpy(dtype=float, copy=True)
    x -= w @ x
    y -= w @ y
    den = float(np.sqrt((w @ (x * x)) * (w @ (y * y))))
    return float(w @ (x * y) / den) if den > 0 else None


def metrics(frame: pd.DataFrame, arm: str) -> dict:
    """Frame weights already represent equal-stock/origin/session mass for its role."""
    w = frame.weight.to_numpy(float, copy=True)
    w /= w.sum()
    result: dict[str, str | int | float | None] = dict(
        arm=arm,
        rows=len(frame),
        origins=frame.origin_id.nunique(),
        sessions=frame.session_date_et.nunique(),
        optimized_loss=float(w @ frame.actual_loss),
    )
    if arm == "META-T2R":
        ic = None
        if frame.groupby("origin_id").size().eq(20).all():
            values = frame.return_4h.to_numpy().reshape(-1, 20)
            score = frame.score.to_numpy().reshape(-1, 20)
            daily = (
                pd.DataFrame(
                    dict(day=frame.session_date_et.to_numpy()[::20], ic=origin_ic(values, score))
                )
                .groupby("day")
                .ic.mean()
            )
            ic = float(daily.mean())
        result.update(
            daily_ic=ic,
            original_TG20_mse=float(w @ ((frame.TG20 - frame.inverse_TG20) ** 2)),
        )
    elif arm == "MAG":
        error = frame.prediction_A - frame.return_4h.abs()
        result.update(
            magnitude_MAE=float(w @ abs(error)),
            magnitude_RMSE=float(np.sqrt(w @ (error**2))),
            negative_m_fraction=float(w @ frame.prediction_m.lt(0)),
            magnitude_rank_association=weighted_rank_association(
                frame.prediction_A.to_numpy(), frame.return_4h.abs().to_numpy(), w
            ),
        )
    elif arm == "EVENT":
        event = frame.event_class.ne(1).to_numpy().astype(float)
        p = frame.p_ANY.to_numpy(float)
        pc = np.clip(p, 1e-12, 1 - 1e-12)
        result.update(
            prevalence=float(w @ event),
            ANY_AP=average_precision(event, p, w),
            ANY_AUC=auc(event, p, w),
            ANY_Brier=float(w @ ((p - event) ** 2)),
            ANY_log_loss=float(w @ (-event * np.log(pc) - (1 - event) * np.log1p(-pc))),
            precision_at_half=float((w * event * (p >= 0.5)).sum() / (w * (p >= 0.5)).sum())
            if (p >= 0.5).any()
            else None,
            recall_at_half=float((w * event * (p >= 0.5)).sum() / (w * event).sum())
            if event.any()
            else None,
        )
    else:
        z = frame.Z.to_numpy()
        q = frame[[f"quantiles_z_{x}" for x in ("05", "50", "95")]].to_numpy()
        tau = np.array([0.05, 0.5, 0.95])
        pin = np.maximum(tau * (z[:, None] - q), (tau - 1) * (z[:, None] - q))
        result.update(
            {f"pinball_{level}": float(w @ pin[:, k]) for k, level in enumerate(("05", "50", "95"))}
        )
        result.update(
            {
                f"coverage_{level}": float(w @ (z <= q[:, k]))
                for k, level in enumerate(("05", "50", "95"))
            }
        )
        result.update(
            coverage90=float(w @ ((z >= q[:, 0]) & (z <= q[:, 2]))),
            width_z=float(w @ (q[:, 2] - q[:, 0])),
            crossing_fraction=float(w @ ((q[:, 0] > q[:, 1]) | (q[:, 1] > q[:, 2]))),
            interval_score90_z=float(
                w
                @ (
                    (q[:, 2] - q[:, 0])
                    + 20 * np.maximum(q[:, 0] - z, 0)
                    + 20 * np.maximum(z - q[:, 2], 0)
                )
            ),
            width_magnitude_rank_association=weighted_rank_association(
                q[:, 2] - q[:, 0], abs(z - q[:, 1]), w
            ),
        )
    return result


def make_frame(
    rows: pd.DataFrame,
    symbols: tuple,
    r: np.ndarray,
    y: np.ndarray,
    raw: np.ndarray,
    arm: str,
    recipe: dict,
    role: str,
) -> pd.DataFrame:
    base = rows.loc[
        :,
        [
            "origin_id",
            "session_date_et",
            "slot",
            "category",
            "entry_end_utc",
            "exit_end_utc",
            "label_maturity_utc",
        ],
    ]
    f = base.loc[base.index.repeat(20)].reset_index(drop=True)
    f["ticker"] = np.tile(symbols, len(rows))
    f["return_4h"], f["TG20"] = r.ravel(), y.ravel()
    f["Z"] = np.arcsinh(y.ravel() / recipe["t2_scale"])
    f["numerator"] = (r - np.median(r, axis=1, keepdims=True)).ravel()
    f["mad"] = np.repeat(np.median(abs(r - np.median(r, axis=1, keepdims=True)), axis=1), 20)
    f["epsilon"], f["role"], f["arm"] = recipe["epsilon"], role, arm
    f["weight"] = weights(rows.session_date_et.to_numpy())
    if raw.ndim == 2:
        f["raw_0"] = raw.ravel()
    else:
        for k in range(raw.shape[-1]):
            f[f"raw_{k}"] = raw[..., k].ravel()
    rt, yt = torch.from_numpy(r.astype(np.float64)), torch.from_numpy(y.astype(np.float64))
    f["actual_loss"] = (
        row_objective(torch.from_numpy(raw.astype(np.float64)), rt, yt, arm, recipe).numpy().ravel()
    )
    for name, value in decode(raw.astype(np.float64), arm, recipe).items():
        f[name] = value.ravel()
    if arm == "META-T2R":
        f["actual_rank"] = (21 - ranks(r)).ravel()
        f["prediction_rank"] = (21 - ranks(raw)).ravel()
    if arm == "EVENT":
        f["event_class"] = labels(y, recipe["event_cutoff"]).ravel()
    if not np.isfinite(f.actual_loss).all():
        raise ValueError("S5S9_NONFINITE_EXPORT_LOSS")
    return f


def fit_control(
    r: np.ndarray,
    y: np.ndarray,
    sigma: np.ndarray,
    days: np.ndarray,
    arm: str,
    recipe: dict,
    kind: str,
) -> dict:
    """Only training-prefix arrays may be supplied by the authority-gated caller."""
    w = origin_weights(days)
    rho = np.clip(sigma / np.median(sigma, axis=1, keepdims=True), 0.1, 10)
    if arm == "MAG":
        value = np.log1p(abs(r) / recipe["magnitude_scale"])
        c = (
            np.average(value, axis=0, weights=w)
            if kind == "STOCK"
            else float(np.average(value, weights=np.broadcast_to(w[:, None] / 20, value.shape)))
        )
        return dict(value=np.asarray(c).tolist())
    if arm == "EVENT":
        cls = labels(y, recipe["event_cutoff"])
        if kind == "VOL":
            v = np.log(sigma).ravel()
            cuts = [quantile(v, t, np.repeat(w / 20, 20)) for t in (0.25, 0.5, 0.75)]
            group = np.searchsorted(cuts, v).reshape(y.shape)
            prior = []
            for k in range(4):
                ww = np.broadcast_to(w[:, None] / 20, y.shape) * (group == k)
                if ww.sum() == 0:
                    raise ValueError("S9_EMPTY_TRAIN_VOL_GROUP")
                prior.append([float((ww * (cls == j)).sum() / ww.sum()) for j in range(3)])
            return dict(cuts=cuts, value=prior)
        prior = np.stack([np.average(cls == j, axis=0, weights=w) for j in range(3)], -1)
        return dict(value=(prior if kind == "STOCK" else prior.mean(0)).tolist())
    z = np.arcsinh(y / recipe["t2_scale"])
    if kind == "VOL":
        z = z / rho
    if kind == "STOCK":
        q = [[quantile(z[:, j], t, w) for t in (0.05, 0.5, 0.95)] for j in range(20)]
    else:
        q = [quantile(z.ravel(), t, np.repeat(w / 20, 20)) for t in (0.05, 0.5, 0.95)]
    return dict(value=q)


def control_raw(control: dict, sigma: np.ndarray, arm: str, kind: str, recipe: dict) -> np.ndarray:
    shape = sigma.shape
    if arm == "MAG":
        if kind == "VOL":
            return np.log1p(2 * np.sqrt(2 / np.pi) * sigma / recipe["magnitude_scale"])
        return np.broadcast_to(np.asarray(control["value"]), shape).copy()
    if arm == "EVENT":
        value = np.asarray(control["value"])
        p = (
            value[np.searchsorted(control["cuts"], np.log(sigma))]
            if kind == "VOL"
            else np.broadcast_to(value, (*shape, 3)).copy()
        )
        p = np.maximum(p, 1e-12)
        p /= p.sum(-1, keepdims=True)
        return np.log(p)
    q = np.broadcast_to(np.asarray(control["value"]), (*shape, 3)).copy()
    if kind == "VOL":
        q *= np.clip(sigma / np.median(sigma, axis=1, keepdims=True), 0.1, 10)[..., None]
    # Encode an already ordered baseline in the same median/softplus-gap coordinates.
    gaps = np.maximum(np.stack([q[..., 1] - q[..., 0], q[..., 2] - q[..., 1]], -1), 1e-12)
    inverse = gaps + np.log(-np.expm1(-gaps))
    return np.stack([q[..., 1], inverse[..., 0], inverse[..., 1]], -1)
