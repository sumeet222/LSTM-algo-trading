"""S1/S2 ranking primitives; pure arithmetic and bounded synthetic-testable solvers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np
import pandas as pd
import torch
from torch import Tensor
from torch.nn import functional as F

YEARS = (2021, 2022, 2023, 2024)
GRID = (0.0001, 0.001, 0.01, 0.1, 1.0, 10.0)
ARMS = ("T2R", "NR", "PW")
RUNS = tuple(f"HF20-S1S2-F{y % 100}-{a}-S42" for y in YEARS for a in ARMS)


def ranks(values: np.ndarray) -> np.ndarray:
    """Ascending average ranks, retaining true ties without jitter."""
    if values.ndim != 2 or values.shape[1] < 2 or not np.isfinite(values).all():
        raise ValueError("FINITE_ORIGIN_CROSS_SECTIONS_REQUIRED")
    return pd.DataFrame(values).rank(axis=1, method="average").to_numpy(dtype=float, copy=True)


def rank_targets(values: np.ndarray) -> np.ndarray:
    return (2 * (ranks(values) - 1) / (values.shape[1] - 1) - 1).astype(np.float32)


def origin_ic(actual: np.ndarray, score: np.ndarray) -> np.ndarray:
    a, b = ranks(actual), ranks(score)
    a -= a.mean(1)[:, None]
    b -= b.mean(1)[:, None]
    den = np.sqrt((a * a).sum(1) * (b * b).sum(1))
    return np.divide((a * b).sum(1), den, out=np.full(len(a), np.nan), where=den > 0)


def origin_weights(days: np.ndarray) -> np.ndarray:
    _, inverse, counts = np.unique(days, return_inverse=True, return_counts=True)
    return 1.0 / (len(counts) * counts[inverse])


def daily_ic(actual: np.ndarray, score: np.ndarray, days: np.ndarray) -> float:
    v = origin_ic(actual, score)
    return float(pd.DataFrame(dict(day=days, ic=v)).groupby("day").ic.mean().mean())


def pair_terms(score: Tensor, returns: Tensor, tau: float = 1.0) -> tuple[Tensor, Tensor]:
    """Exact pair losses and half-to-each-endpoint allocation. Leading axes are origins."""
    if score.shape != returns.shape or score.shape[-1] < 2 or tau != 1.0:
        raise ValueError("PAIR_SHAPE_OR_FROZEN_TEMPERATURE")
    if not bool(torch.isfinite(score).all()) or not bool(torch.isfinite(returns).all()):
        raise ValueError("NONFINITE_PAIR_INPUT")
    i, j = torch.triu_indices(score.shape[-1], score.shape[-1], offset=1)
    direction = torch.sign(returns[..., i] - returns[..., j]).to(score.dtype)
    valid = direction.ne(0)
    denominator = valid.sum(-1)
    if bool(denominator.eq(0).any()):
        raise ValueError("NO_VALID_UNTIED_PAIRS")
    terms = F.softplus(-direction * (score[..., i] - score[..., j]) / tau) * valid
    allocation = torch.zeros_like(score)
    half = terms / (2 * denominator[..., None])
    allocation = allocation.index_add(-1, i, half).index_add(-1, j, half)
    np.testing.assert_allclose(
        allocation.detach().sum(-1).numpy(),
        (terms.sum(-1) / denominator).detach().numpy(),
        rtol=3e-7,
        atol=1e-8,
    )
    return terms, allocation


def row_loss(arm: str, score: Tensor, returns: Tensor, y: Tensor, scale: float) -> Tensor:
    if arm == "PW":
        return pair_terms(score, returns)[1]
    if arm == "NR":
        target = torch.from_numpy(
            rank_targets(returns.detach().numpy().reshape(-1, returns.shape[-1]))
        )
        return (score - target.reshape_as(score)).square() / score.shape[-1]
    if arm != "T2R" or scale <= 0:
        raise ValueError("DECLARED_OBJECTIVE_REQUIRED")
    return (score - torch.asinh(y.to(score.dtype) / scale)).square() / score.shape[-1]


@dataclass
class RankSelector:
    """Absolute IC qualification; first finite epoch qualifies even when IC is negative."""

    best: float = -float("inf")
    selected: int = 0
    raw_best: float = -float("inf")
    raw_epoch: int = 0
    stale: int = 0

    def observe(self, epoch: int, ic: float) -> bool:
        if not np.isfinite(ic) or not 1 <= epoch <= 60:
            raise ValueError("UNDEFINED_SELECTOR_OR_EPOCH")
        if ic > self.raw_best:
            self.raw_best, self.raw_epoch = ic, epoch
        qualifies = self.selected == 0 or ic > self.best + 0.001
        if qualifies:
            self.best, self.selected, self.stale = ic, epoch, 0
        else:
            self.stale += 1
        return qualifies

    def stop(self, epoch: int) -> bool:
        return epoch >= 60 or (epoch >= 12 and self.stale >= 10)


# Each streamed item is (origin×stock×768, original source returns, origin weight).
LinearStream = Callable[[], Iterable[tuple[np.ndarray, np.ndarray, np.ndarray]]]


def ridge(stream: LinearStream, penalty: float) -> np.ndarray:
    """min sum_origin weight mean_stock(error²) + lambda||slopes||²; free intercept."""
    return ridge_solution(*ridge_system(stream), penalty)


def ridge_system(stream: LinearStream) -> tuple[np.ndarray, np.ndarray]:
    """Accumulate shared sufficient statistics once for the fixed calibration grid."""
    gram, rhs = np.zeros((769, 769)), np.zeros(769)
    for x, returns, w in stream():
        a = np.column_stack([x.reshape(-1, 768), np.ones(x.shape[0] * x.shape[1])])
        q = rank_targets(returns).reshape(-1).astype(float)
        row_w = np.repeat(w / x.shape[1], x.shape[1])
        gram += a.T @ (row_w[:, None] * a)
        rhs += a.T @ (row_w * q)
    return gram, rhs


def ridge_solution(gram: np.ndarray, rhs: np.ndarray, penalty: float) -> np.ndarray:
    gram = gram.copy()
    gram[np.arange(768), np.arange(768)] += penalty
    result = np.linalg.solve(gram, rhs)
    if not np.isfinite(result).all():
        raise ValueError("NONFINITE_RIDGE")
    np.testing.assert_allclose(gram @ result, rhs, rtol=1e-8, atol=1e-9)
    return result


def linear_pair_value_gradient(
    coefficients: np.ndarray,
    stream: LinearStream,
    penalty: float,
) -> tuple[float, np.ndarray]:
    """Matrix-free pairs: store scores and190directions, never190×768differences."""
    total = penalty * float(coefficients @ coefficients)
    gradient = 2 * penalty * coefficients.copy()
    for x, returns, w in stream():
        n = x.shape[1]
        i, j = np.triu_indices(n, 1)
        direction = np.sign(returns[:, i] - returns[:, j])
        valid = direction != 0
        count = valid.sum(1)
        if (count == 0).any():
            raise ValueError("NO_UNTIED_LINEAR_PAIRS")
        score = x @ coefficients
        margin = -direction * (score[:, i] - score[:, j])
        total += float(np.sum(w * (np.logaddexp(0, margin) * valid).sum(1) / count))
        sigmoid = np.exp(-np.logaddexp(0, -margin))
        d = -direction * sigmoid * valid * w[:, None] / count[:, None]
        row_grad = np.zeros_like(score)
        for k in range(len(i)):
            row_grad[:, i[k]] += d[:, k]
            row_grad[:, j[k]] -= d[:, k]
        gradient += np.einsum("bnd,bn->d", x, row_grad)
    return total, gradient


def linear_pair(stream: LinearStream, penalty: float) -> tuple[np.ndarray, dict]:
    """Fixed float64 L-BFGS cap; nonconvergence stops instead of extending the search."""
    w = torch.zeros(768, dtype=torch.float64, requires_grad=True)
    opt = torch.optim.LBFGS(
        [w],
        max_iter=100,
        max_eval=125,
        tolerance_grad=1e-7,
        tolerance_change=1e-12,
        line_search_fn="strong_wolfe",
    )
    calls = 0

    def closure() -> Tensor:
        nonlocal calls
        calls += 1
        if calls > 125:
            raise ValueError("LINEAR_PAIR_EVALUATION_CAP_NO_RETRY")
        value, grad = linear_pair_value_gradient(w.detach().numpy(), stream, penalty)
        if not np.isfinite(value) or not np.isfinite(grad).all():
            raise ValueError("NONFINITE_LINEAR_PAIR")
        w.grad = torch.from_numpy(grad)
        return torch.tensor(value, dtype=torch.float64)

    opt.step(closure)
    value, grad = linear_pair_value_gradient(w.detach().numpy(), stream, penalty)
    if np.max(abs(grad)) > 1e-5:
        raise ValueError("LINEAR_PAIR_NOT_CONVERGED_NO_AUTOMATIC_RETRY")
    return w.detach().numpy().copy(), dict(
        calls=calls, objective=value, gradient_max=float(abs(grad).max())
    )
