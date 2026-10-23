"""P025 preregistered natural-frequency event and proper quantile diagnostics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .branch_replication_spec import SCIENCE
from .dm_quantile_diagnostics import metrics as quantile_metrics
from .objective_screen_audit import average_precision
from .objective_screen_loss import classes
from .objective_screen_metrics import classification, equal_weights


def corrected(probability: np.ndarray, recipe: dict) -> np.ndarray:
    """Analytical inverse-weight diagnostic; no fitted parameters or calibration claim."""
    value = probability / np.asarray(recipe["class_weights"])[None, :]
    return value / value.sum(axis=1, keepdims=True)


def binary_curve(label: np.ndarray, score: np.ndarray, weight: np.ndarray) -> pd.DataFrame:
    order = np.argsort(-score, kind="stable")
    label, score, weight = label[order], score[order], weight[order]
    ends = np.r_[np.flatnonzero(np.diff(score)), len(score) - 1]
    tp, fp = np.cumsum(weight * label)[ends], np.cumsum(weight * ~label)[ends]
    positive, negative = float(weight @ label), float(weight @ ~label)
    return pd.DataFrame(
        dict(
            threshold=score[ends],
            precision=tp / (tp + fp),
            recall=tp / positive if positive else np.nan,
            FPR=fp / negative if negative else np.nan,
        )
    )


def event_metrics(
    f: pd.DataFrame, recipe: dict, *, inverse: bool = False
) -> tuple[dict, pd.DataFrame]:
    p = f[["p_NEG", "p_NORMAL", "p_POS"]].to_numpy(dtype=float)
    if inverse:
        p = corrected(p, recipe)
    days, y = f.session_date_et.to_numpy(), f.TG20.to_numpy(dtype=float)
    result = classification(y, p, days, recipe)
    w, label = equal_weights(days), classes(y, recipe["q95_abs_y"])
    curves, thresholds, budgets, slopes = [], [], [], []
    binary_reliability = []
    for k, name in [(0, "NEG"), (1, "NORMAL"), (2, "POS"), (-1, "ANY")]:
        score = p[:, 0] + p[:, 2] if k == -1 else p[:, k]
        truth = label != 1 if k == -1 else label == k
        curve = binary_curve(truth, score, w)
        curve["event"] = name
        curves.append(curve)
        positive, negative = float(w @ truth), float(w @ ~truth)
        # Trapezoidal ROC includes (0,0); undefined if either class is absent.
        result[name + "_AUROC"] = (
            float(np.trapezoid(np.r_[0.0, curve.recall], np.r_[0.0, curve.FPR]))
            if positive and negative
            else np.nan
        )
        result[name + "_AP"] = average_precision(truth, score, w)
        result[name + "_Brier"] = float(w @ ((score - truth) ** 2))
        if name == "ANY":
            ece = 0.0
            bins = np.minimum((score * 10).astype(int), 9)
            for b in range(10):
                selected = bins == b
                mass = float(w[selected].sum())
                confidence = float(w[selected] @ score[selected] / mass) if mass else np.nan
                frequency = float(w[selected] @ truth[selected] / mass) if mass else np.nan
                if mass:
                    ece += mass * abs(confidence - frequency)
                binary_reliability.append(
                    dict(
                        event="ANY",
                        bin=b,
                        rows=int(selected.sum()),
                        mass=mass,
                        confidence=confidence,
                        frequency=frequency,
                    )
                )
            result["ANY_ECE10"] = ece
        mean = float(w @ score)
        variance = float(w @ ((score - mean) ** 2))
        slope = (
            float(w @ ((score - mean) * (truth - positive)) / variance)
            if variance > 1e-15
            else np.nan
        )
        slopes.append(
            dict(
                event=name,
                slope=slope,
                intercept=positive - slope * mean,
                mean_probability=mean,
                prevalence=positive,
                calibration_in_large=mean - positive,
            )
        )
        for threshold in SCIENCE["calibration"]["probability_thresholds"]:
            called = score >= threshold
            tp, fp = float(w @ (truth & called)), float(w @ (~truth & called))
            thresholds.append(
                dict(
                    event=name,
                    threshold=threshold,
                    precision=tp / (tp + fp) if tp + fp else np.nan,
                    recall=tp / positive if positive else np.nan,
                    FPR=fp / negative if negative else np.nan,
                    called_mass=float(w @ called),
                )
            )
        scores, truths = score.reshape(-1, 20), truth.reshape(-1, 20)
        for count in SCIENCE["calibration"]["origin_top_k"]:
            order = np.argsort(-scores, axis=1, kind="stable")[:, :count]
            hits = np.take_along_axis(truths, order, axis=1).sum(axis=1)
            totals = truths.sum(axis=1)
            table = pd.DataFrame(
                dict(
                    day=days.reshape(-1, 20)[:, 0],
                    precision=hits / count,
                    recall=np.divide(
                        hits, totals, out=np.full(len(hits), np.nan), where=totals > 0
                    ),
                    false_positives=count - hits,
                )
            )
            budgets.append(
                dict(
                    event=name,
                    k=count,
                    **{
                        str(k): float(v)
                        for k, v in table.groupby("day").mean().mean().to_dict().items()
                    },
                )
            )
    result.update(
        slopes=slopes,
        threshold_diagnostics=thresholds,
        top_k=budgets,
        map="INVERSE_CLASS_WEIGHT" if inverse else "RAW_SOFTMAX",
    )
    result["reliability"].extend(binary_reliability)
    prior = np.broadcast_to(np.asarray(recipe["prevalence"]), (len(f), 3)).copy()
    normal = np.zeros_like(prior)
    normal[:, 1] = 1
    result["constant_fit_prior"] = classification(y, prior, days, recipe)
    result["always_normal"] = classification(y, normal, days, recipe)
    if inverse:
        raw = f[["p_NEG", "p_NORMAL", "p_POS"]].to_numpy(dtype=float)
        raw_any = raw[:, 0] + raw[:, 2]
        new_any = p[:, 0] + p[:, 2]
        result["ANY_raw_corrected_rank_correlation"] = (
            float(pd.Series(raw_any).rank().corr(pd.Series(new_any).rank()))
            if np.std(raw_any) > 1e-15 and np.std(new_any) > 1e-15
            else np.nan
        )
        a = np.argsort(-raw_any.reshape(-1, 20), axis=1, kind="stable")[:, :4]
        b = np.argsort(-new_any.reshape(-1, 20), axis=1, kind="stable")[:, :4]
        changed = np.array([len(set(x) ^ set(y)) / 8 for x, y in zip(a, b)])
        result["ANY_top4_membership_changed_fraction"] = float(
            pd.Series(changed, index=days.reshape(-1, 20)[:, 0]).groupby(level=0).mean().mean()
        )
    return result, pd.concat(curves, ignore_index=True)


def qr_metrics(f: pd.DataFrame, recipe: dict) -> dict:
    result = quantile_metrics(f, "QR1", recipe)
    constant = f.copy()
    for k, suffix in enumerate(("05", "50", "95")):
        constant["quantiles_z_" + suffix] = recipe["quantiles_z"][k]
    constant["z_hat"] = recipe["quantiles_z"][1]
    constant["y_hat"] = recipe["scale"] * np.sinh(constant.z_hat)
    baseline = quantile_metrics(constant, "QR1", recipe)
    result.update(unconditional=baseline, pinball_skill=1 - result["pinball"] / baseline["pinball"])
    return result


def paired_month_blocks(days: np.ndarray, statistic, *, seed: int = 22042) -> list[dict]:
    """Resample intact matched days in fixed non-overlapping 1/2-month blocks.

    statistic receives repeated integer row indices and pseudo-day IDs, allowing AP
    and other nonlinear metrics to be recomputed rather than averaging daily AP.
    """
    unique = np.unique(days)
    months = pd.to_datetime(unique).to_period("M").astype(str)
    month_names = sorted(set(months))
    result = []
    for size in (1, 2):
        groups = [
            unique[np.isin(months, month_names[i : i + size])]
            for i in range(0, len(month_names), size)
        ]
        rng = np.random.default_rng(seed)
        values = []
        for _ in range(400):
            drawn = np.concatenate([groups[i] for i in rng.integers(len(groups), size=len(groups))])
            indices = np.concatenate([np.flatnonzero(days == day) for day in drawn])
            pseudo = np.concatenate(
                [np.repeat(str(i), np.count_nonzero(days == day)) for i, day in enumerate(drawn)]
            )
            values.append(float(statistic(indices, pseudo)))
        result.append(
            dict(
                block_months=size,
                replicates=400,
                seed=seed,
                interval=np.nanquantile(values, [0.025, 0.975]).tolist(),
            )
        )
    return result
