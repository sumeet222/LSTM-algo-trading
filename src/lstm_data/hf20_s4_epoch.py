"""S4 frozen session-batch training arithmetic; zero-update mode supports rehearsal."""

from __future__ import annotations

import math
import resource
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .hf20_ranking import origin_weights, row_loss
from .hf20_s4_data import S4Data
from .neural_engine import SharedLSTM


def epoch(
    model: SharedLSTM,
    opt: torch.optim.AdamW,
    data: S4Data,
    positions: np.ndarray,
    arm: str,
    number: int,
    phase: str,
    dest: Path,
    *,
    update: bool = True,
) -> dict:
    """Same S2 arithmetic/batch order; additional per-parameter gradient incidence."""
    if update:
        from .hf20_s4_authority import authorize

        authorize(dest.parent)
    groups = data.rows.iloc[positions].groupby("session_date_et").indices
    days = sorted(groups, key=str)
    np.random.default_rng(42 + number).shuffle(days)
    telemetry, gradients = [], []
    model.train()
    for start in range(0, len(days), 16):
        chosen = days[start : start + 16]
        pos = positions[np.concatenate([groups[d] for d in chosen])]
        x, r, y = data.arrays(pos)
        w = origin_weights(data.rows.iloc[pos].session_date_et.to_numpy())
        opt.zero_grad()
        raw = model(torch.from_numpy(x.reshape(-1, 48, 16))).reshape(-1, 20)
        loss = (
            row_loss(
                arm,
                raw,
                torch.from_numpy(r),
                torch.from_numpy(y.astype(np.float32)),
                data.recipe["t2_scale"],
            ).sum(1)
            * torch.from_numpy(w.astype(np.float32))
        ).sum()
        if not bool(torch.isfinite(loss)):
            raise ValueError("S4_NONFINITE_ONLINE_LOSS")
        loss.backward()
        for name, p in model.named_parameters():
            g = p.grad
            if g is None or not bool(torch.isfinite(g).all()):
                raise ValueError("S4_MISSING_OR_NONFINITE_PARAMETER_GRADIENT")
            gradients.append(
                dict(
                    phase=phase,
                    epoch=number,
                    batch=start // 16,
                    parameter=name,
                    cells=g.numel(),
                    nonzero=int(torch.count_nonzero(g)),
                    norm=float(torch.linalg.vector_norm(g)),
                )
            )
        before = [p.detach().clone() for p in model.parameters()]
        pre = float(
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        )
        post = math.sqrt(
            sum(float(p.grad.square().sum()) for p in model.parameters() if p.grad is not None)
        )
        if update:
            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if sys.platform != "darwin":
                rss *= 1024
            if rss > 2_000_000_000:
                raise ValueError("S4_RAM_CAP_BEFORE_OPTIMIZER_UPDATE")
            opt.step()
        delta = math.sqrt(
            sum(float((p.detach() - b).square().sum()) for p, b in zip(model.parameters(), before))
        )
        if not all(bool(torch.isfinite(p).all()) for p in model.parameters()) or post > 1.00001:
            raise ValueError("S4_NONFINITE_WEIGHTS_OR_CLIP")
        telemetry.append(
            dict(
                phase=phase,
                epoch=number,
                batch=start // 16,
                preclip=pre,
                postclip=post,
                update_norm=delta,
                sessions=len(chosen),
                online_loss=float(loss.detach()),
                parameter_norm=math.sqrt(
                    sum(float(p.detach().square().sum()) for p in model.parameters())
                ),
            )
        )
    pd.DataFrame(telemetry).to_csv(dest / f"{phase}_{number:03d}_batches.csv", index=False)
    pd.DataFrame(gradients).to_csv(dest / f"{phase}_{number:03d}_gradients.csv", index=False)
    return dict(
        phase=phase,
        epoch=number,
        steps=len(telemetry) if update else 0,
        batches=len(telemetry),
        dropout_on=True,
        online_objective=float(
            np.average(
                [r["online_loss"] for r in telemetry], weights=[r["sessions"] for r in telemetry]
            )
        ),
    )
