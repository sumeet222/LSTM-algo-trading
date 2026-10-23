"""P024 six frozen single-factor T2 interventions; no data access or training."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import torch
from torch import nn

from .neural_engine import SharedLSTM, optimizer, seed_all
from .neural_lifecycle import EarlyStop


@dataclass(frozen=True)
class Variant:
    arm: str
    seed: int = 42
    learning_rate: float = 0.001
    head_dropout: float = 0.10
    matrix_decay: float = 0.01
    improvement: float = 0.001
    hidden: int = 32
    layers: int = 1


REFERENCE = Variant("T2")
VARIANTS = (
    Variant("LRLOW", learning_rate=0.0003),
    Variant("DROP0", head_dropout=0.0),
    Variant("WD0", matrix_decay=0.0),
    Variant("ES025", seed=123, improvement=0.00025),
    Variant("H64", hidden=64),
    Variant("L2H32", layers=2),
)
RUNS = tuple(f"HF1M-LONG-TM0-{v.arm}-S{v.seed}-DEV1" for v in VARIANTS)


class ScreenLSTM(SharedLSTM):
    """Reuse the reference zero-state encoder and head semantics, varying dimensions only."""

    def __init__(self, variant: Variant) -> None:
        if variant.hidden == 32 and variant.layers == 1:
            super().__init__()
            self.dropout.p = variant.head_dropout
        else:
            nn.Module.__init__(self)
            self.input_dim = 16
            self.lstm = nn.LSTM(
                16, variant.hidden, num_layers=variant.layers, batch_first=True, dropout=0.0
            )
            self.dropout = nn.Dropout(variant.head_dropout)
            self.head = nn.Linear(variant.hidden, 1)


def make_model(v: Variant) -> ScreenLSTM:
    seed_all(v.seed)
    return ScreenLSTM(v)


def make_optimizer(model: ScreenLSTM, v: Variant) -> torch.optim.AdamW:
    """Keep the reference two exhaustive groups, change only the declared settings."""
    opt = optimizer(model)
    for group in opt.param_groups:
        group["lr"] = v.learning_rate
    opt.param_groups[0]["weight_decay"] = v.matrix_decay
    return opt


@dataclass
class ScreenStop(EarlyStop):
    """Historical strict comparator, no tolerance, with only its relative threshold varied."""

    improvement: float = 0.001

    def observe(self, loss: float | None) -> bool:
        if self.status != "CALIBRATING" or loss is None or not math.isfinite(loss) or loss < 0:
            raise ValueError("P024_VALID_SEQUENTIAL_MSE_REQUIRED")
        self.epoch += 1
        qualifying = self.best is None or loss < (1 - self.improvement) * self.best
        if self.raw_min is None or loss < self.raw_min:
            self.raw_min, self.raw_epoch = loss, self.epoch
        if qualifying:
            self.best, self.selected, self.patience = loss, self.epoch, 0
        else:
            self.patience += 1
        if self.epoch >= 12 and self.patience >= 10:
            self.status = "PATIENCE_STOP"
        elif self.epoch == 60:
            self.status = "MAX_EPOCHS_REACHED"
        return qualifying


def parameter_audit(v: Variant) -> dict:
    model = make_model(v)
    opt = make_optimizer(model, v)
    baseline = asdict(REFERENCE)
    baseline["seed"] = v.seed
    delta = {
        k: [baseline[k], val] for k, val in asdict(v).items() if k != "arm" and val != baseline[k]
    }
    names = {id(p): n for n, p in model.named_parameters()}
    return dict(
        variant=asdict(v),
        matched_seed=v.seed,
        delta=delta,
        parameters=sum(p.numel() for p in model.parameters()),
        shapes={n: list(p.shape) for n, p in model.named_parameters()},
        groups=[
            dict(
                names=[names[id(p)] for p in g["params"]],
                learning_rate=g["lr"],
                weight_decay=g["weight_decay"],
                betas=g["betas"],
                eps=g["eps"],
            )
            for g in opt.param_groups
        ],
        head_dropout=model.dropout.p,
        interlayer_dropout=model.lstm.dropout,
        independent_zero_state=True,
    )
