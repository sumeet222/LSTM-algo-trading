"""Package011 prospective single-factor objectives; canonical TG0 is never mutated."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import torch

from .ft0_transforms import identity
from .neural_engine import session_losses
from .real_bridge_data import RealInputView

ARMS = ("C0", "H1", "T1", "T2", "O1")
VERSION = "TA011_CONTROLLED_LOSS_v1"


@dataclass(frozen=True)
class LossPolicy:
    arm: str
    cap: float = 1.0
    scale: float = 1.0

    def __post_init__(self) -> None:
        if (
            self.arm not in ARMS
            or not np.isfinite((self.cap, self.scale)).all()
            or min(self.cap, self.scale) <= 0
        ):
            raise ValueError("REGISTERED_FINITE_POSITIVE_LOSS_POLICY_REQUIRED")

    @property
    def clip(self) -> float:
        return 5.0 if self.arm == "O1" else 1.0

    def canonical(self, logits: torch.Tensor) -> torch.Tensor:
        value = self.scale * torch.sinh(logits) if self.arm == "T2" else logits
        if not bool(torch.isfinite(value).all()):
            raise ValueError("T2_INVERSE_OR_PREDICTION_NONFINITE_NO_OUTPUT_CAP")
        return value

    def objective(
        self,
        logits: torch.Tensor,
        target: torch.Tensor,
        origins: torch.Tensor,
        *,
        stock_count: int = 5,
    ) -> torch.Tensor:
        if self.arm == "H1":
            element = torch.nn.functional.huber_loss(logits, target, reduction="none", delta=2.0)
            return (element.mean(dim=2) * origins).sum(dim=1) / origins.sum(dim=1)
        truth = (
            target.clamp(-self.cap, self.cap)
            if self.arm == "T1"
            else torch.asinh(target / self.scale)
            if self.arm == "T2"
            else target
        )
        return session_losses(logits, truth, origins, stock_count=stock_count)


def fit_policy(view: RealInputView, arm: str) -> dict:
    """Unweighted unique session/origin/stock training labels; no window duplicates."""
    if view.window.phase not in {"INNER_TRAIN", "REFIT"}:
        # Existing fitting windows use only fitting phases, never inner/outer validation.
        raise ValueError("TRAINING_PREFIX_ONLY_POLICY_FIT")
    values = np.abs(np.asarray([v for r in view.rows for v in r.targets], dtype=np.float64))
    if not len(values) or not np.isfinite(values).all():
        raise ValueError("FINITE_TRAINING_LABEL_POPULATION_REQUIRED")
    policy = LossPolicy(
        arm,
        float(np.quantile(values, 0.99, method="linear")) if arm == "T1" else 1.0,
        max(float(np.median(values)), 1e-6) if arm == "T2" else 1.0,
    )
    value = dict(
        version=VERSION,
        policy=asdict(policy),
        population="UNWEIGHTED_POOLED_UNIQUE_SESSION_ORIGIN_STOCK",
        observations=len(values),
        quantile_method="numpy.linear",
        scale_floor=1e-6,
        preparation_id=view.preparation_id,
        view_id=view.version,
        cutoff=str(view.window.stop),
        target_population_hash=identity([(r.session, r.origin, r.targets) for r in view.rows]),
    )
    return {**value, "parameter_id": identity(value)}
