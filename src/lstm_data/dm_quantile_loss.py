"""Frozen P023 DM1/QR1/SS1 math and duplicate-safe whole-session sampling."""

from __future__ import annotations

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.nn import functional as F

from .hf1m_training_data import TrainingView
from .neural_engine import SessionBatch, SharedLSTM, seed_all

ARMS = ("DM1", "QR1", "SS1")
RUNS = tuple(f"HF1M-LONG-TM0-{arm}-S42-DEV1" for arm in ARMS)


def model_for(arm: str) -> SharedLSTM:
    if arm not in ARMS:
        raise ValueError("P023_ARM")
    seed_all(42)
    model = SharedLSTM()
    if arm != "SS1":
        model.head = nn.Linear(32, 3)
    return model


def outputs(raw: torch.Tensor, arm: str, scale: float) -> dict[str, torch.Tensor]:
    if arm == "DM1":
        p = raw[..., 0].sigmoid()
        pos, neg = F.softplus(raw[..., 1]), F.softplus(raw[..., 2])
        z = p * pos - (1 - p) * neg
        return dict(p=p, mu_positive=pos, mu_negative=neg, z_hat=z, y_hat=scale * torch.sinh(z))
    if arm == "QR1":
        median = raw[..., 0]
        q = torch.stack(
            [median - F.softplus(raw[..., 1]), median, median + F.softplus(raw[..., 2])], dim=-1
        )
        return dict(
            quantiles_z=q,
            quantiles_y=scale * torch.sinh(q),
            z_hat=median,
            y_hat=scale * torch.sinh(median),
        )
    if arm != "SS1":
        raise ValueError("P023_ARM")
    return dict(z_hat=raw, y_hat=scale * torch.sinh(raw))


def terms(
    raw: torch.Tensor, y: torch.Tensor, mask: torch.Tensor, arm: str, scale: float
) -> dict[str, torch.Tensor]:
    z = torch.asinh(y / scale)
    prediction = outputs(raw, arm, scale)
    if arm == "DM1":
        positive = z >= 0
        ce = F.binary_cross_entropy_with_logits(raw[..., 0], positive.to(y.dtype), reduction="none")
        observed = torch.where(positive, prediction["mu_positive"], prediction["mu_negative"])
        magnitude = (observed - z.abs()).square()
        components = torch.stack([ce, magnitude], dim=-1)
        loss = components.sum(dim=-1)
    elif arm == "QR1":
        error = z[..., None] - prediction["quantiles_z"]
        tau = torch.tensor([0.05, 0.5, 0.95], dtype=y.dtype)
        components = torch.maximum(tau * error, (tau - 1) * error)
        loss = components.mean(dim=-1)
    else:
        loss = (z - raw).square()
        components = loss[..., None]
    weight = mask[..., None].to(y.dtype) / (mask.sum(dim=1)[:, None, None] * 20)
    return dict(
        loss=loss,
        components=components,
        row_allocation=loss * weight,
        session_loss=(loss * weight).sum(dim=(1, 2)),
    )


def fitting_recipe(target: pd.DataFrame, scale: float, sessions: tuple[str, ...]) -> dict:
    """Only call on the named training prefix. Weighted quantiles use inverse empirical CDF."""
    y = target.TG20.to_numpy(dtype=float)
    w = 1 / (
        target.session_date_et.nunique()
        * target.groupby("session_date_et").origin_id.transform("nunique").to_numpy()
        * 20
    )
    z = np.arcsinh(y / scale)
    positive = z >= 0
    prior = float(w[positive].sum())
    if not 0 < prior < 1:
        raise ValueError("P023_BOTH_SIGNS_REQUIRED")
    order = np.argsort(z, kind="stable")
    cumulative = np.cumsum(w[order])
    cumulative[-1] = 1
    quantiles = [
        float(z[order[min(np.searchsorted(cumulative, t, side="left"), len(z) - 1)]])
        for t in [0.05, 0.5, 0.95]
    ]
    n = len(target) // 100
    # Caller supplies canonical origin×stock order, stable source origin tie order.
    stock = np.tile(np.arange(20), len(target) // 20)
    ranked = np.lexsort((stock, target.origin_id.to_numpy(), -abs(y)))
    tail_dates = set(target.iloc[ranked[:n]].session_date_et)
    tail = [i for i, d in enumerate(sessions) if d in tail_dates]
    ordinary = [i for i, d in enumerate(sessions) if d not in tail_dates]
    if not tail or not ordinary:
        raise ValueError("P023_NONEMPTY_SAMPLER_GROUPS_REQUIRED")
    return dict(
        scale=scale,
        sign_prior=prior,
        exact_zero_rows=int((y == 0).sum()),
        magnitude_positive=float(w[positive] @ abs(z[positive]) / prior),
        magnitude_negative=float(w[~positive] @ abs(z[~positive]) / (1 - prior)),
        quantiles_z=quantiles,
        quantile_method="equal-session/origin/stock weighted inverse empirical CDF, left",
        tail_positions=tail,
        ordinary_positions=ordinary,
        session_count=len(sessions),
        tail_natural_share=len(tail) / len(sessions),
        tail_rank_rows=n,
        tail_cutoff_abs_y=float(abs(y[ranked[n - 1]])),
        tail_sessions=sorted(tail_dates),
    )


def draws(recipe: dict, epoch: int) -> list[tuple[tuple[int, ...], np.ndarray]]:
    """Balanced pairs; odd final draw chooses group Bernoulli(.5), so q_g remains .5."""
    rng = np.random.default_rng(np.random.SeedSequence([42, epoch, 2301]))
    n = recipe["session_count"]
    p = recipe["tail_natural_share"]
    result = []
    for start in range(0, n, 16):
        size = min(16, n - start)
        groups = np.array([0, 1] * (size // 2) + ([int(rng.integers(2))] if size % 2 else []))
        rng.shuffle(groups)
        positions = tuple(
            int(rng.choice(recipe["tail_positions"] if g else recipe["ordinary_positions"]))
            for g in groups
        )
        weight = np.where(groups == 1, 2 * p, 2 * (1 - p)).astype(np.float32)
        result.append((positions, weight))
    return result


def draw_batch(view: TrainingView, positions: tuple[int, ...]) -> SessionBatch:
    """Keep repeated sessions as independent draws with unique validated draw IDs."""
    batches = [view.batch((position,)) for position in positions]
    batch = SessionBatch(
        tuple(f"{b.ids[0]}#draw{i}" for i, b in enumerate(batches)),
        torch.cat([b.inputs for b in batches]),
        torch.cat([b.targets for b in batches]),
        torch.cat([b.origins for b in batches]),
        20,
    )
    batch.validate()
    return batch
