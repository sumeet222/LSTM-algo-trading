"""Three stock-independent causal P026 modules and exact optimizer groups."""

from __future__ import annotations

import math

import torch
from torch import nn

from .neural_engine import SharedLSTM, seed_all
from .temporal_screen_spec import ARMS, PARAMETERS


def causal_means(x: torch.Tensor) -> torch.Tensor:
    """Inclusive 1/4/12-step prefix means of the existing finite scaled inputs."""
    if x.ndim != 3 or tuple(x.shape[1:]) != (48, 16) or not bool(torch.isfinite(x).all()):
        raise ValueError("P026_EXACT_FINITE_INPUT")
    # Short fixed windows avoid subtracting large cumulative sums and preserve causality.
    return torch.cat(
        [
            torch.stack([x[:, max(0, s - w + 1) : s + 1].mean(1) for s in range(48)], 1)
            for w in (1, 4, 12)
        ],
        -1,
    )


class TemporalModel(nn.Module):
    """One stock sequence per batch row; no cross-stock computation or persistent state."""

    def __init__(self, arm: str) -> None:
        super().__init__()
        if arm not in ARMS:
            raise ValueError("P026_ARM")
        self.arm = arm
        if arm == "A3":
            self.recurrent = nn.GRU(16, 32, 1, batch_first=True, dropout=0)
            self.dropout = nn.Dropout(0.1)
            self.head = nn.Linear(32, 1)
        else:
            base = SharedLSTM()
            self.recurrent = base.lstm
            self.dropout = base.dropout
            self.head = base.head
        if arm == "A1":
            generator = torch.Generator(device="cpu").manual_seed(2643)
            self.query = nn.Parameter(torch.randn(32, generator=generator) * 0.01)
            self.gamma = nn.Parameter(torch.zeros(()))
            self.norm = nn.LayerNorm(32, eps=1e-5, elementwise_affine=False)
        if arm == "A2":
            with torch.random.fork_rng(devices=[]):
                self.mixer = nn.Linear(48, 16)
            with torch.no_grad():
                self.mixer.weight.zero_()
                self.mixer.weight[:, :16].copy_(torch.eye(16))
                self.mixer.bias.zero_()
        if sum(p.numel() for p in self.parameters()) != PARAMETERS[arm]:
            raise ValueError("P026_PARAMETER_COUNT")

    def details(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        if (
            x.ndim != 3
            or tuple(x.shape[1:]) != (48, 16)
            or not len(x)
            or x.dtype != self.head.weight.dtype
            or x.device != self.head.weight.device
            or not bool(torch.isfinite(x).all())
        ):
            raise ValueError("P026_FINITE_EXACT_DTYPE_DEVICE")
        mixed = self.mixer(causal_means(x)) if self.arm == "A2" else x
        sequence, state = self.recurrent(mixed)
        hidden = state if isinstance(state, torch.Tensor) else state[0]
        last = hidden[-1]
        result = dict(sequence=sequence, readout=last, mixed=mixed)
        if self.arm == "A1":
            attention = (self.norm(sequence) @ self.query / math.sqrt(32)).softmax(1)
            context = (attention[:, :, None] * sequence).sum(1)
            result.update(attention=attention, readout=last + self.gamma * (context - last))
        return result

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.dropout(self.details(x)["readout"])).squeeze(-1)


def model_for(arm: str) -> TemporalModel:
    seed_all(42)
    return TemporalModel(arm)


def optimizer(model: TemporalModel) -> torch.optim.AdamW:
    decay = []
    no_decay = []
    for name, p in model.named_parameters():
        (decay if p.ndim >= 2 or name == "query" else no_decay).append(p)
    return torch.optim.AdamW(
        [dict(params=decay, weight_decay=0.01), dict(params=no_decay, weight_decay=0.0)],
        lr=0.001,
        betas=(0.9, 0.999),
        eps=1e-8,
    )


def exact_optimizer(model: TemporalModel, opt: torch.optim.AdamW) -> dict:
    names = {id(p): n for n, p in model.named_parameters()}
    seen = []
    groups = []
    for g in opt.param_groups:
        if g["lr"] != 0.001 or g["betas"] != (0.9, 0.999) or g["eps"] != 1e-8:
            raise ValueError("P026_EXACT_HYPERPARAMETERS")
        members = []
        for p in g["params"]:
            n = names[id(p)]
            if g["weight_decay"] != (0.01 if p.ndim >= 2 or n == "query" else 0.0):
                raise ValueError("P026_EXACT_DECAY")
            members.append(n)
        seen += members
        groups.append(
            dict(
                names=members,
                lr=g["lr"],
                betas=list(g["betas"]),
                eps=g["eps"],
                weight_decay=g["weight_decay"],
            )
        )
    if sorted(seen) != sorted(names.values()) or len(seen) != len(set(seen)):
        raise ValueError("P026_PARAMETER_COVERAGE")
    return dict(parameters=sum(p.numel() for p in model.parameters()), groups=groups)
