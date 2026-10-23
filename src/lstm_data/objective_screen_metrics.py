"""P022 objective-specific metrics, with no conversion from probabilities to returns."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .objective_screen_audit import average_precision, origin_ic
from .objective_screen_loss import classes


def equal_weights(days: np.ndarray) -> np.ndarray:
    """Rows are complete canonical origin×20 panels."""
    _, inverse, counts = np.unique(days, return_inverse=True, return_counts=True)
    return 1 / (len(counts) * counts[inverse])


def classification(y: np.ndarray, probability: np.ndarray, days: np.ndarray, recipe: dict) -> dict:
    if probability.shape != (len(y), 3) or not np.isfinite(probability).all():
        raise ValueError("P022_FINITE_THREE_PROBABILITIES")
    np.testing.assert_allclose(probability.sum(axis=1), 1, rtol=1e-6, atol=1e-7)
    label = classes(y, recipe["q95_abs_y"])
    w = equal_weights(days)
    predicted = probability.argmax(axis=1)
    confusion = np.zeros((3, 3))
    for a in range(3):
        for b in range(3):
            confusion[a, b] = w[(label == a) & (predicted == b)].sum()
    truth = np.eye(3)[label]
    selected = probability[np.arange(len(y)), label]
    # Fixed float64 tiny is solely for finite baseline logloss, not learned calibration.
    ce = -np.log(np.maximum(selected, np.finfo(float).tiny))
    coefficient = np.asarray(recipe["class_weights"])[label]
    table = pd.DataFrame({"day": days, "weighted": ce * coefficient, "coef": coefficient})
    g = table.groupby("day")[["weighted", "coef"]].sum()
    result = dict(
        unweighted_CE=float(w @ ce),
        normalized_class_weighted_CE=float((g.weighted / g.coef).mean()),
        confusion_weighted=confusion.tolist(),
        probability_mean=(w @ probability).tolist(),
        probability_sd=np.sqrt(w @ ((probability - w @ probability) ** 2)).tolist(),
        Brier_by_class=(w @ ((probability - truth) ** 2)).tolist(),
        observed_prevalence=(w @ truth).tolist(),
        argmax_counts=np.bincount(predicted, minlength=3).tolist(),
        decision_rule="argmax NEG/NORMAL/POS; exact ties canonical first index",
    )
    f1 = []
    rare_ap = []
    reliability = []
    for k, name in enumerate(["NEG", "NORMAL", "POS"]):
        tp = confusion[k, k]
        positive = confusion[k].sum()
        called = confusion[:, k].sum()
        recall = float(tp / positive) if positive else np.nan
        precision = float(tp / called) if called else np.nan
        f1.append(2 * tp / (positive + called) if positive + called else np.nan)
        result[name + "_recall"] = recall
        result[name + "_precision"] = precision
        result[name + "_FPR"] = float((called - tp) / (1 - positive)) if positive < 1 else np.nan
        ap = average_precision(label == k, probability[:, k], w)
        result[name + "_AP"] = ap
        if k in (0, 2) and np.isfinite(ap):
            rare_ap.append(ap)
        ece = 0.0
        bins = np.minimum((probability[:, k] * 10).astype(int), 9)
        for b in range(10):
            m = bins == b
            mass = w[m].sum()
            confidence = float(w[m] @ probability[m, k] / mass) if mass else np.nan
            frequency = float(w[m] @ (label[m] == k) / mass) if mass else np.nan
            if mass:
                ece += mass * abs(confidence - frequency)
            reliability.append(
                dict(
                    event=name,
                    bin=b,
                    rows=int(m.sum()),
                    mass=float(mass),
                    confidence=confidence,
                    frequency=frequency,
                )
            )
        result[name + "_ECE10"] = ece
    result["macro_F1"] = float(np.nanmean(f1))
    result["signed_rare_macro_AP"] = float(np.mean(rare_ap)) if rare_ap else np.nan
    result["ANY_AP"] = average_precision(label != 1, probability[:, 0] + probability[:, 2], w)
    result["reliability"] = reliability
    score = probability[:, 2] - probability[:, 0]
    daily = pd.Series(origin_ic(score, y), index=days.reshape(-1, 20)[:, 0]).groupby(level=0).mean()
    result["ordinal_daily_IC"] = float(daily.mean())
    for k, name in [(0, "NEG"), (2, "POS"), (-1, "ANY")]:
        s = probability[:, 0] + probability[:, 2] if k == -1 else probability[:, k]
        t = (label != 1 if k == -1 else label == k).reshape(-1, 20)
        rank = np.argsort(-s.reshape(-1, 20), axis=1, kind="stable")[:, :4]
        hits = np.take_along_axis(t, rank, axis=1).sum(axis=1)
        origin_day = days.reshape(-1, 20)[:, 0]
        result[name + "_precision_at4"] = float(
            pd.Series(hits / 4, index=origin_day).groupby(level=0).mean().mean()
        )
        denom = t.sum(axis=1)
        recalls = np.divide(hits, denom, out=np.full(len(hits), np.nan), where=denom > 0)
        result[name + "_recall_at4"] = float(
            pd.Series(recalls, index=origin_day).groupby(level=0).mean().mean()
        )
    return result


def regression(y: np.ndarray, pred: np.ndarray, days: np.ndarray) -> dict:
    # Aggregate arithmetic in float64 even when online labels/predictions are float32.
    # Otherwise squaring y before promotion introduces a false decomposition failure.
    y = np.asarray(y, dtype=np.float64)
    pred = np.asarray(pred, dtype=np.float64)
    w = equal_weights(days)
    error = pred - y
    ic = origin_ic(pred, y)
    daily = pd.Series(ic, index=days.reshape(-1, 20)[:, 0]).groupby(level=0).mean()
    mse = float(w @ (error**2))
    zero = float(w @ (y**2))
    energy = float(w @ (pred**2))
    cross = float(2 * w @ (y * pred))
    if not np.isclose(mse - zero, energy - cross, atol=1e-10, rtol=1e-9):
        raise ValueError("P022_ZERO_DECOMPOSITION")
    return dict(
        mse=mse,
        mae=float(w @ abs(error)),
        rmse=float(np.sqrt(mse)),
        zero_mse=zero,
        excess_mse=mse - zero,
        prediction_energy=energy,
        twice_y_pred=cross,
        daily_ic=float(daily.mean()),
        defined_ic_days=int(daily.notna().sum()),
        prediction_mean=float(w @ pred),
        prediction_sd=float(np.sqrt(w @ ((pred - w @ pred) ** 2))),
        actual_sd=float(np.sqrt(w @ ((y - w @ y) ** 2))),
        sign_hit=float(w @ (np.sign(y) == np.sign(pred))),
        prediction_quantiles=np.quantile(pred, [0, 0.01, 0.05, 0.5, 0.95, 0.99, 1]).tolist(),
    )
