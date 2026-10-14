"""MC0 composition and the frozen MC1 endpoint feature gate; no source loader."""

from __future__ import annotations

import torch
from torch import Tensor, nn

from .neural_engine import MODEL_VERSION, SharedLSTM

ARCHITECTURES = ("TM0", "MC0", "MC1", "E5")


class EndpointGate(nn.Module):
    """One origin endpoint → 16 positive channel multipliers, tau exactly one."""

    def __init__(self) -> None:
        super().__init__()
        self.linear = nn.Linear(5, 16)
        nn.init.zeros_(self.linear.weight)
        nn.init.zeros_(self.linear.bias)

    def forward(self, endpoint: Tensor) -> Tensor:
        if (
            endpoint.ndim != 2
            or endpoint.shape[1] != 5
            or not len(endpoint)
            or endpoint.dtype != self.linear.weight.dtype
            or endpoint.device != self.linear.weight.device
            or not bool(torch.isfinite(endpoint).all())
        ):
            raise ValueError("FINITE_FIVE_CHANNEL_ENDPOINT_REQUIRED")
        logits = self.linear(endpoint)
        weights = 16 * torch.softmax(logits, dim=-1)
        # No clipping/fallback: floating underflow or overflow is an input failure.
        if (
            not bool(torch.isfinite(weights).all())
            or not bool((weights > 0).all())
            or not torch.allclose(
                weights.sum(-1), torch.full_like(weights[:, 0], 16), atol=2e-6, rtol=1e-6
            )
        ):
            raise ValueError("FINITE_STRICTLY_POSITIVE_SUM16_GATE_REQUIRED")
        return weights


class EndpointGatedLSTM(nn.Module):
    """MC1: one endpoint gate shared by five stocks and all historical steps."""

    input_dim = 21

    def __init__(self) -> None:
        super().__init__()
        self.core = SharedLSTM(21)
        self.gate = EndpointGate()

    def compose(self, x: Tensor) -> tuple[Tensor, Tensor]:
        # Flat stockwise computation must still contain complete five-name origins.
        if (
            x.ndim != 3
            or tuple(x.shape[1:]) != (48, 21)
            or not len(x)
            or len(x) % 5
            or x.dtype != self.core.head.weight.dtype
            or x.device != self.core.head.weight.device
            or not bool(torch.isfinite(x).all())
        ):
            raise ValueError("MC1_COMPLETE_FINITE_FIVE_STOCK_ORIGINS_REQUIRED")
        origins = x.reshape(-1, 5, 48, 21)
        market = origins[:, 0, :, 16:]
        if not torch.equal(origins[:, :, :, 16:], market[:, None].expand(-1, 5, -1, -1)):
            raise ValueError("ONE_SHARED_MARKET_HISTORY_PER_ORIGIN_REQUIRED")
        alpha = self.gate(market[:, -1])
        stock = origins[..., :16] * alpha[:, None, None, :]
        return torch.cat((stock, origins[..., 16:]), dim=-1).reshape(-1, 48, 21), alpha

    def forward(self, x: Tensor) -> Tensor:
        values, _ = self.compose(x)
        return self.core(values)


NeuralModel = SharedLSTM | EndpointGatedLSTM


def create_model(architecture: str = "TM0") -> NeuralModel:
    """Fresh models only; copying MC0 tensors is never part of ordinary refit."""
    if architecture not in ARCHITECTURES:
        raise ValueError("DECLARED_TM0_MC0_MC1_E5_REQUIRED")
    return (
        EndpointGatedLSTM()
        if architecture == "MC1"
        else SharedLSTM({"TM0": 16, "MC0": 21, "E5": 23}[architecture])
    )


def architecture_of(model: NeuralModel) -> str:
    return (
        "MC1"
        if isinstance(model, EndpointGatedLSTM)
        else {16: "TM0", 21: "MC0", 23: "E5"}[model.input_dim]
    )


def architecture_for_information(information: str) -> str:
    # Legacy stock-only pair information strings remain loadable without migration.
    if information.startswith("FT0_D7_") and information not in {
        "FT0_D7_MC0",
        "FT0_D7_MC1",
        "FT0_D7_E5",
    }:
        raise ValueError("UNAPPROVED_MARKET_ARCHITECTURE")
    return {"FT0_D7_MC0": "MC0", "FT0_D7_MC1": "MC1", "FT0_D7_E5": "E5"}.get(information, "TM0")


def model_version(model: NeuralModel) -> str:
    architecture = architecture_of(model)
    return MODEL_VERSION if architecture == "TM0" else "SYN:" + architecture + ":1"


def gate_diagnostics(weights: Tensor) -> dict:
    """Bounded descriptive computational summaries, never financial importance."""
    a = weights.detach()
    if (
        a.ndim != 2
        or a.shape[1] != 16
        or not len(a)
        or not bool(torch.isfinite(a).all())
        or not bool((a > 0).all())
        or not torch.allclose(a.sum(-1), torch.full_like(a[:, 0], 16), atol=2e-6, rtol=1e-6)
    ):
        raise ValueError("VALID_GATE_DIAGNOSTICS_REQUIRED")
    p = a / 16
    entropy = -(p * p.log()).sum(-1)
    return {
        "channel_mean": a.mean(0).tolist(),
        "channel_sd": a.std(0, unbiased=False).tolist(),
        "min": float(a.min()),
        "max": float(a.max()),
        "quantiles": torch.quantile(a.flatten(), torch.tensor([0.05, 0.5, 0.95])).tolist(),
        "entropy_mean": float(entropy.mean()),
        "entropy_min": float(entropy.min()),
        "concentration_max": float(p.max()),
        "saturated_fraction": float((p > 0.9).float().mean()),
        "constant_gate_warning": bool((a.std(0, unbiased=False) == 0).all()),
        "positive": True,
        "sum16_max_error": float((a.sum(-1) - 16).abs().max()),
    }


def trace_model(model: NeuralModel, joined: Tensor, provenance: str) -> dict:
    """Cheap T0/T1 hook for at most two fabricated origins; no hidden-state dump or labels."""
    from .p3_domain import synthetic_id

    synthetic_id(provenance)
    if len(joined) not in (5, 10) or tuple(joined.shape[1:]) != (48, 21):
        raise ValueError("BOUNDED_FIVE_STOCK_MARKET_TRACE_REQUIRED")
    training = model.training
    model.eval()
    try:
        with torch.no_grad():
            gated, weights = (
                model.compose(joined) if isinstance(model, EndpointGatedLSTM) else (joined, None)
            )
            predictions = model(joined).reshape(-1, 5)
            output = {
                "architecture": architecture_of(model),
                "provenance": provenance,
                "input_channel_mean": joined[..., :16].mean((0, 1)).tolist(),
                "gated_channel_mean": gated[..., :16].mean((0, 1)).tolist(),
                "scores": predictions.tolist(),
                "descending_order": torch.argsort(
                    predictions, dim=-1, descending=True, stable=True
                ).tolist(),
                "gate": gate_diagnostics(weights) if weights is not None else None,
            }
            return output
    finally:
        model.train(training)
