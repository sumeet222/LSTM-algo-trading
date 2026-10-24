"""P028 approved MC1, one-way global/local memory and two soft readout heads."""

from __future__ import annotations

from copy import deepcopy

import numpy as np
import torch
from torch import nn

from .neural_engine import seed_all
from .panel_state_audit import construct
from .state_screen_spec import ARMS, PARAMETERS


def panel_state(x: torch.Tensor) -> torch.Tensor:
    """Original float32 source pooling in float64; fixed features, no learned transform."""
    if x.ndim != 4 or tuple(x.shape[1:]) != (20, 48, 16) or x.dtype != torch.float32:
        raise ValueError("P028_EXACT_PANEL_REQUIRED")
    a = x.detach().cpu().numpy()[..., [0, 4]].transpose(0, 2, 1, 3)
    m = construct(a.reshape(-1, 20, 2)).reshape(len(x), 48, 2)
    return torch.from_numpy(np.ascontiguousarray(m)).to(x.device)


class StateModel(nn.Module):
    """Complete20 windows; explicit external state supports own-fixed causal controls."""

    def __init__(self, arm: str) -> None:
        super().__init__()
        if arm not in ARMS:
            raise ValueError("P028_ARM")
        self.arm = arm
        if arm == "A8":
            self.global_cell = nn.LSTMCell(2, 8)
            self.local_cell = nn.LSTMCell(24, 32)
            self.dropout = nn.Dropout(0.1)
            self.head = nn.Linear(32, 1)
            with torch.no_grad():
                self.local_cell.weight_ih[:, 16:24].zero_()
        else:
            self.recurrent = nn.LSTM(18, 32, 1, batch_first=True, dropout=0)
            self.dropout = nn.Dropout(0.1)
            self.head = nn.Linear(32, 1)
            if arm == "A7":
                with torch.random.fork_rng(devices=[]):
                    self.gate = nn.Linear(2, 16)
                nn.init.zeros_(self.gate.weight)
                nn.init.zeros_(self.gate.bias)
            else:
                self.expert1 = deepcopy(self.head)
                with torch.random.fork_rng(devices=[]):
                    self.router = nn.Linear(2, 2)
                generator = torch.Generator(device="cpu").manual_seed(2812)
                with torch.no_grad():
                    self.router.weight.copy_(torch.randn(2, 2, generator=generator) * 0.01)
                    self.router.bias.zero_()
        if sum(p.numel() for p in self.parameters()) != PARAMETERS[arm]:
            raise ValueError("P028_FULL_PARAMETER_COUNT")

    def validate_input(self, x: torch.Tensor) -> None:
        if (
            x.ndim != 4
            or tuple(x.shape[1:]) != (20, 48, 16)
            or not len(x)
            or x.dtype != self.head.weight.dtype
            or x.device != self.head.weight.device
            or not bool(torch.isfinite(x).all())
        ):
            raise ValueError("P028_FINITE_CANONICAL_PANEL_DTYPE_DEVICE")

    def details(
        self, x: torch.Tensor, state: torch.Tensor | None = None
    ) -> dict[str, torch.Tensor]:
        self.validate_input(x)
        m = panel_state(x) if state is None else state
        if (
            m.shape != (len(x), 48, 2)
            or m.dtype != x.dtype
            or m.device != x.device
            or not bool(torch.isfinite(m).all())
        ):
            raise ValueError("P028_FINITE_EXACT_STATE")
        result = dict(state=m)
        if self.arm == "A8":
            g, c = x.new_zeros(len(x), 8), x.new_zeros(len(x), 8)
            h, local_c = x.new_zeros(len(x) * 20, 32), x.new_zeros(len(x) * 20, 32)
            gs, cs, hs, ls = [], [], [], []
            for step in range(48):
                g, c = self.global_cell(m[:, step], (g, c))
                u = torch.cat((x[:, :, step], g[:, None].expand(-1, 20, -1)), -1)
                h, local_c = self.local_cell(u.reshape(-1, 24), (h, local_c))
                gs.append(g)
                cs.append(c)
                hs.append(h.reshape(-1, 20, 32))
                ls.append(local_c.reshape(-1, 20, 32))
            result.update(
                global_hidden=torch.stack(gs, 1),
                global_cell=torch.stack(cs, 1),
                local_hidden=torch.stack(hs, 2),
                local_cell=torch.stack(ls, 2),
                readout=hs[-1],
            )
        else:
            own = x
            if self.arm == "A7":
                alpha = 16 * self.gate(m[:, -1]).softmax(-1)
                own = x * alpha[:, None, None, :]
                result["alpha"] = alpha
            u = torch.cat((own, m[:, None].expand(-1, 20, -1, -1)), -1)
            output, (h, c) = self.recurrent(u.reshape(-1, 48, 18))
            result.update(
                hidden_history=output.reshape(-1, 20, 48, 32),
                readout=h[-1].reshape(-1, 20, 32),
                cell=c[-1].reshape(-1, 20, 32),
            )
            if self.arm == "A12":
                result["router"] = self.router(m[:, -1]).softmax(-1)
        return result

    def forward(self, x: torch.Tensor, state: torch.Tensor | None = None) -> torch.Tensor:
        d = self.details(x, state)
        h = self.dropout(d["readout"])
        a = self.head(h).squeeze(-1)
        if self.arm == "A12":
            b = self.expert1(h).squeeze(-1)
            return d["router"][:, 0, None] * a + d["router"][:, 1, None] * b
        return a

    def shifted(self, own: torch.Tensor, donor: torch.Tensor) -> torch.Tensor:
        self.validate_input(own)
        self.validate_input(donor)
        if self.training or own.shape != donor.shape:
            raise ValueError("P028_MATCHED_EVAL_ONLY_STATE_CONTROL")
        return self(own, panel_state(donor))


def model_for(arm: str) -> StateModel:
    seed_all(42)
    return StateModel(arm)


__all__ = ["StateModel", "model_for", "panel_state", "optimizer", "exact_optimizer"]


def optimizer(model: StateModel) -> torch.optim.AdamW:
    decay = [p for p in model.parameters() if p.ndim >= 2]
    no_decay = [p for p in model.parameters() if p.ndim < 2]
    return torch.optim.AdamW(
        [dict(params=decay, weight_decay=0.01), dict(params=no_decay, weight_decay=0.0)],
        lr=0.001,
        betas=(0.9, 0.999),
        eps=1e-8,
    )


def exact_optimizer(model: StateModel, opt: torch.optim.AdamW) -> dict:
    names = {id(p): n for n, p in model.named_parameters()}
    seen, groups = [], []
    for group in opt.param_groups:
        if group["lr"] != 0.001 or group["betas"] != (0.9, 0.999) or group["eps"] != 1e-8:
            raise ValueError("P028_EXACT_OPTIMIZER")
        members = []
        for parameter in group["params"]:
            if group["weight_decay"] != (0.01 if parameter.ndim >= 2 else 0.0):
                raise ValueError("P028_EXACT_DECAY")
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
        raise ValueError("P028_EXHAUSTIVE_UNIQUE_GROUPS")
    return dict(groups=groups, parameters=sum(p.numel() for p in model.parameters()))
