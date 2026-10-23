"""P022 fixed H2/W1/E1/R1 objectives with exact equal-session accounting."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import Tensor, nn
from torch.nn import functional as F

from .neural_engine import SharedLSTM, seed_all

ARMS = ("H2", "W1", "E1", "R1")
RUNS = tuple(f"HF1M-LONG-TM0-{arm}-S42-DEV1" for arm in ARMS)


def model_for(arm: str) -> SharedLSTM:
    if arm not in ARMS:
        raise ValueError("P022_FIXED_ARM_REQUIRED")
    seed_all(42)
    model = SharedLSTM()
    if arm == "E1":
        # Construct baseline first: identical initial backbone, separate three-logit head.
        model.head = nn.Linear(32, 3)
    expected = 6499 if arm == "E1" else 6433
    if sum(p.numel() for p in model.parameters()) != expected:
        raise ValueError("P022_PARAMETER_COUNT")
    return model


def classes(y: np.ndarray, threshold: float) -> np.ndarray:
    if threshold <= 0 or not np.isfinite(threshold) or not np.isfinite(y).all():
        raise ValueError("P022_FINITE_EVENT_TARGET")
    return np.where(y < -threshold, 0, np.where(y > threshold, 2, 1))


def fit_recipe(y: np.ndarray, weights: np.ndarray, scale: float) -> dict:
    """Caller must pass only admitted training rows for the specified fit prefix."""
    if y.shape != weights.shape or not np.isclose(weights.sum(), 1) or (weights <= 0).any():
        raise ValueError("P022_TRAINING_WEIGHT_MASS")
    threshold = float(np.quantile(abs(y), 0.95, method="linear"))
    labels = classes(y, threshold)
    prevalence = np.array([weights[labels == k].sum() for k in range(3)])
    if (prevalence <= 0).any():
        raise ValueError("P022_ABSENT_CLASS")
    coefficients = np.minimum(4.0, np.sqrt(prevalence[1] / np.maximum(prevalence, 1e-12)))
    coefficients[1] = 1.0
    return dict(
        q95_abs_y=threshold,
        q95_abs_z=float(np.quantile(abs(np.arcsinh(y / scale)), 0.95)),
        scale=scale,
        prevalence=prevalence.tolist(),
        class_weights=coefficients.tolist(),
        tiny=1e-12,
        tiny_binds=bool((prevalence < 1e-12).any()),
        counts=[int((labels == k).sum()) for k in range(3)],
        quantile_method="linear across admitted stock rows; strict tail; equality NORMAL",
    )


@dataclass(frozen=True)
class Objective:
    arm: str
    recipe: dict

    def contributions(
        self, output: Tensor, y: Tensor, mask: Tensor, rank_targets: Tensor | None = None
    ) -> dict[str, Tensor]:
        """Per-row allocations sum to each session loss. Mean sessions for the optimizer.

        R1 allocates half of each normalized pair loss to each endpoint. Padded origins
        have exactly zero mass. These allocations are accounting, not causal attribution.
        """
        if self.arm not in ARMS or y.ndim != 3 or y.shape[2] != 20 or mask.shape != y.shape[:2]:
            raise ValueError("P022_EXACT20_SESSION_OBJECTIVE")
        if not bool(mask.any(dim=1).all()) or not bool(torch.isfinite(output).all()):
            raise ValueError("P022_FINITE_NONEMPTY_SESSIONS")
        origins = mask.sum(dim=1).to(y.dtype)
        base = mask[..., None].to(y.dtype) / (origins[:, None, None] * 20)
        pair_alloc = torch.zeros_like(y)
        pair_losses = torch.empty((*y.shape[:2], 0), device=y.device, dtype=y.dtype)
        if self.arm == "E1":
            q = self.recipe["q95_abs_y"]
            label = torch.where(y < -q, 0, torch.where(y > q, 2, 1))
            raw = F.cross_entropy(
                output.reshape(-1, 3), label.reshape(-1), reduction="none"
            ).reshape_as(y)
            coefficient = torch.tensor(
                self.recipe["class_weights"], dtype=y.dtype, device=y.device
            )[label]
        else:
            z = torch.asinh(y / self.recipe["scale"])
            error = z - output
            raw = error.square()
            if self.arm == "H2":
                raw = torch.where(error.abs() <= 1, error.square(), 2 * error.abs() - 1)
            coefficient = torch.ones_like(y)
            if self.arm == "W1":
                coefficient = torch.where(
                    z.abs() > self.recipe["q95_abs_z"],
                    torch.full_like(y, 2.0),
                    torch.ones_like(y),
                )
            if self.arm == "R1":
                i, j = torch.triu_indices(20, 20, offset=1, device=y.device)
                truth = y if rank_targets is None else rank_targets
                if truth.shape != y.shape or not bool(torch.isfinite(truth).all()):
                    raise ValueError("P022_EXACT_RANK_LABEL_SHAPE")
                direction = torch.sign(truth[..., i] - truth[..., j]).to(output.dtype)
                valid = direction.ne(0) & mask[..., None]
                pair_losses = F.softplus(-direction * (output[..., i] - output[..., j])) * valid
                denom = valid.sum(dim=-1).clamp_min(1).to(y.dtype)
                allocated = 0.5 * pair_losses / denom[..., None] / origins[:, None, None]
                pair_alloc = pair_alloc.index_add(-1, i, allocated / 2)
                pair_alloc = pair_alloc.index_add(-1, j, allocated / 2)
        weight = coefficient * mask[..., None]
        weight = weight / weight.sum(dim=(1, 2))[:, None, None]
        point = raw * weight
        return dict(
            pointwise=point,
            pairwise=pair_alloc,
            total=point + pair_alloc,
            coefficient=coefficient,
            normalized_weight=weight,
            raw=raw,
            ordinary_weight=base.expand_as(y),
            pair_losses=pair_losses,
        )

    def loss(self, output: Tensor, y: Tensor, mask: Tensor) -> Tensor:
        return self.contributions(output, y, mask)["total"].sum(dim=(1, 2))
