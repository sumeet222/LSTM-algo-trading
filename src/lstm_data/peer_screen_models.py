"""Coupled N=20 P027 models with explicit stock/origin axes and identity paths."""

from __future__ import annotations

import torch
from torch import nn

from .neural_engine import SharedLSTM, seed_all
from .peer_screen_spec import ARMS, PARAMETERS


def peer_statistics(m1: torch.Tensor) -> torch.Tensor:
    """[B,20,48] → [B,20,48,2], excluding self with population divisor19."""
    if m1.ndim != 3 or tuple(m1.shape[1:]) != (20, 48) or not torch.isfinite(m1).all():
        raise ValueError("P027_PEER_M1_COMPLETE20_REQUIRED")
    index = torch.tensor([[j for j in range(20) if j != i] for i in range(20)], device=m1.device)
    peers = m1[:, index, :]
    mean = peers.mean(2)
    # Center directly instead of E[u²]-E[u]² to avoid cancellation; no added epsilon.
    variance = (peers - mean[:, :, None, :]).square().mean(2).clamp_min(0)
    return torch.stack((mean, variance.sqrt()), -1)


class PeerModel(nn.Module):
    """Each origin is a coupled complete20 panel; different origins never interact."""

    def __init__(self, arm: str) -> None:
        super().__init__()
        if arm not in ARMS:
            raise ValueError("P027_ARM")
        self.arm = arm
        if arm == "A4":
            self.recurrent = nn.LSTM(18, 32, 1, batch_first=True, dropout=0)
            self.dropout = nn.Dropout(0.1)
            self.head = nn.Linear(32, 1)
        else:
            base = SharedLSTM()
            self.recurrent, self.dropout, self.head = base.lstm, base.dropout, base.head
            self.norm = nn.LayerNorm(32, eps=1e-5, elementwise_affine=False)
        if arm == "A5":
            generator = torch.Generator(device="cpu").manual_seed(2747)
            self.M1 = nn.Parameter(torch.randn(4, 20, generator=generator) * 0.01)
            self.M2 = nn.Parameter(torch.zeros(20, 4))
        if arm == "A6":
            generator = torch.Generator(device="cpu").manual_seed(2748)
            self.WQ = nn.Parameter(torch.randn(32, 16, generator=generator) * 0.01)
            self.WK = nn.Parameter(torch.randn(32, 16, generator=generator) * 0.01)
            self.WV = nn.Parameter(torch.randn(32, 16, generator=generator) * 0.01)
            self.WO = nn.Parameter(torch.zeros(16, 32))
        if sum(p.numel() for p in self.parameters()) != PARAMETERS[arm]:
            raise ValueError("P027_PARAMETER_COUNT")

    def validate_input(self, x: torch.Tensor) -> None:
        if (
            x.ndim != 4
            or tuple(x.shape[1:]) != (20, 48, 16)
            or not len(x)
            or x.dtype != self.head.weight.dtype
            or x.device != self.head.weight.device
            or not bool(torch.isfinite(x).all())
        ):
            raise ValueError("P027_FINITE_CANONICAL_PANEL_DTYPE_DEVICE")

    def augmented(self, x: torch.Tensor, peer_m1: torch.Tensor | None = None) -> torch.Tensor:
        self.validate_input(x)
        if self.arm != "A4":
            raise ValueError("P027_A4_ONLY")
        return torch.cat((x, peer_statistics(x[..., 0] if peer_m1 is None else peer_m1)), -1)

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        self.validate_input(x)
        augmented = self.augmented(x) if self.arm == "A4" else x
        _, (h, _) = self.recurrent(augmented.reshape(-1, 48, augmented.shape[-1]))
        return h[-1].reshape(-1, 20, 32)

    def exchange(self, h: torch.Tensor) -> dict[str, torch.Tensor]:
        if h.ndim != 3 or tuple(h.shape[1:]) != (20, 32):
            raise ValueError("P027_EXACT_HIDDEN_PANEL")
        result = dict(hidden=h, readout=h)
        if self.arm == "A5":
            bottleneck = torch.einsum("kn,bnd->bkd", self.M1, self.norm(h))
            residual = torch.einsum("nk,bkd->bnd", self.M2, torch.nn.functional.gelu(bottleneck))
            result.update(bottleneck=bottleneck, residual=residual, readout=h + residual)
        elif self.arm == "A6":
            normalized = self.norm(h)
            q, k, v = normalized @ self.WQ, normalized @ self.WK, normalized @ self.WV
            attention = ((q @ k.transpose(1, 2)) / 4.0).softmax(-1)
            residual = attention @ v @ self.WO
            result.update(attention=attention, residual=residual, readout=h + residual)
        return result

    def details(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        return self.exchange(self.encode(x))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.dropout(self.details(x)["readout"])).squeeze(-1)

    def shifted(self, own: torch.Tensor, donor: torch.Tensor) -> torch.Tensor:
        """Only other-stock histories shift; each focal stock keeps its entire own history."""
        self.validate_input(own)
        self.validate_input(donor)
        if own.shape != donor.shape or self.training:
            raise ValueError("P027_MATCHED_EVAL_ONLY_PEER_CONTROL")
        if self.arm == "A4":
            a = self.augmented(own, donor[..., 0])
            _, (h, _) = self.recurrent(a.reshape(-1, 48, 18))
            return self.head(h[-1]).reshape(-1, 20)
        h, shifted_h = self.encode(own), self.encode(donor)
        results = []
        for i in range(20):
            panel = shifted_h.clone()
            panel[:, i] = h[:, i]
            readout = self.exchange(panel)["readout"][:, i]
            results.append(self.head(readout).squeeze(-1))
        return torch.stack(results, 1)


def model_for(arm: str) -> PeerModel:
    seed_all(42)
    return PeerModel(arm)


def optimizer(model: PeerModel) -> torch.optim.AdamW:
    decay = [p for p in model.parameters() if p.ndim >= 2]
    no_decay = [p for p in model.parameters() if p.ndim < 2]
    return torch.optim.AdamW(
        [dict(params=decay, weight_decay=0.01), dict(params=no_decay, weight_decay=0.0)],
        lr=0.001,
        betas=(0.9, 0.999),
        eps=1e-8,
    )


def exact_optimizer(model: PeerModel, opt: torch.optim.AdamW) -> dict:
    names = {id(p): n for n, p in model.named_parameters()}
    seen, groups = [], []
    for group in opt.param_groups:
        if group["lr"] != 0.001 or group["betas"] != (0.9, 0.999) or group["eps"] != 1e-8:
            raise ValueError("P027_EXACT_OPTIMIZER")
        members = []
        for parameter in group["params"]:
            if group["weight_decay"] != (0.01 if parameter.ndim >= 2 else 0.0):
                raise ValueError("P027_EXACT_DECAY")
            members.append(names[id(parameter)])
        seen.extend(members)
        groups.append(
            dict(
                names=members,
                lr=group["lr"],
                betas=list(group["betas"]),
                eps=group["eps"],
                weight_decay=group["weight_decay"],
            )
        )
    if len(seen) != len(names) or len(set(seen)) != len(names):
        raise ValueError("P027_EXHAUSTIVE_UNIQUE_GROUPS")
    return dict(groups=groups, parameters=sum(p.numel() for p in model.parameters()))
