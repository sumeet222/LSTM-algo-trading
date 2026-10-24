"""Read-only measurements of the actual temporal modules, not explanation claims."""

from __future__ import annotations

import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import write_json
from .hf1m_action_audit import SYMBOLS
from .neural_engine import session_batches
from .temporal_screen_models import TemporalModel, causal_means


def measure(model: TemporalModel, view, destination: Path) -> dict:
    started = time.monotonic()
    model.eval()
    state = {n: p.detach().clone() for n, p in model.named_parameters()}
    records = []
    lag_sum = np.zeros((20, 48))
    samples = 0
    for positions in session_batches(len(view.source.rows), 42, 1, shuffle=False):
        x = torch.from_numpy(view.origin_batch(positions)["x"].reshape(-1, 48, 16))
        with torch.inference_mode():
            d = model.details(x)
            h = d["sequence"]
            record = dict(
                hidden_abs_mean=float(h.abs().mean()),
                hidden_sd=float(h.std(unbiased=False)),
                hidden_max=float(h.abs().max()),
            )
            if model.arm == "A1":
                a = d["attention"]
                np.testing.assert_allclose(a.sum(1).numpy(), 1, rtol=1e-6, atol=1e-7)
                entropy = -(a * torch.log(a)).sum(1)
                reference = model.head(h[:, -1]).squeeze(-1)
                changed = model.head(d["readout"]).squeeze(-1) - reference
                lag_sum += a.numpy().reshape(-1, 20, 48).sum(0)
                record.update(
                    entropy=float(entropy.mean()),
                    normalized_entropy=float(entropy.mean() / math.log(48)),
                    effective_lookback=float(entropy.exp().mean()),
                    early12_mass=float(a[:, :12].sum(1).mean()),
                    late12_mass=float(a[:, -12:].sum(1).mean()),
                    readout_z_change_rms=float(changed.square().mean().sqrt()),
                )
                originrows = view.source.rows.iloc[list(positions)]
                for k, row in enumerate(originrows.to_dict("records")):
                    mean_stock = a.numpy().reshape(-1, 20, 48)[k].mean(0)
                    for lag, value in enumerate(mean_stock):
                        records.append(
                            dict(
                                session_date_et=row["session_date_et"],
                                lag=lag - 47,
                                weight=float(value),
                            )
                        )
            samples += len(positions)
        # Bound per-sample distributions without keeping hidden tensors.
        if model.arm != "A1":
            records.append(dict(origins=len(positions), **record))
    summary = dict(
        arm=model.arm,
        origins=samples,
        scope="saved fixed checkpoint; diagnostic only; usage is not predictive skill",
        gate_statistics="NOT_DIRECTLY_OBSERVED; native GRU gates uninstrumented"
        if model.arm == "A3"
        else "not applicable",
        last_batch_hidden=record,
    )
    if model.arm == "A1":
        summary.update(
            gamma=float(model.gamma.detach()), query_norm=float(model.query.detach().norm())
        )
        pd.DataFrame(
            [
                dict(ticker=s, lag=j - 47, mean_weight=lag_sum[i, j] / samples)
                for i, s in enumerate(SYMBOLS)
                for j in range(48)
            ]
        ).to_parquet(destination / "attention_by_lag_stock.parquet", index=False)
        # Day×stock×lag means retain date variation without per-row activation dumps.
        pd.DataFrame(records).groupby(
            ["session_date_et", "lag"], as_index=False
        ).weight.mean().to_parquet(destination / "attention_by_day.parquet", index=False)
    else:
        pd.DataFrame(records).to_parquet(destination / "hidden_batches.parquet", index=False)
    positions = tuple(range(min(8, len(view.source.rows))))
    x = torch.from_numpy(view.origin_batch(positions)["x"].reshape(-1, 48, 16)).requires_grad_(True)
    output = model(x)
    differentiated = torch.autograd.grad(
        output.sum(), [x, model.mixer.weight] if model.arm == "A2" else [x]
    )
    gradient = differentiated[0]
    if model.arm == "A2":
        summary["mixer_branch_gradient_norm"] = [
            float(differentiated[1][:, j * 16 : (j + 1) * 16].norm()) for j in range(3)
        ]
    if not bool(torch.isfinite(gradient).all()):
        raise ValueError("P026_BPTT_FINITE")
    step = gradient.detach().square().sum(2).sqrt().mean(0).numpy()
    pd.DataFrame(dict(lag=np.arange(48) - 47, input_gradient_norm=step)).to_parquet(
        destination / "history_gradient.parquet", index=False
    )
    perturb = []
    with torch.inference_mode():
        for first, last in ((0, 12), (12, 36), (36, 48)):
            changed = x.detach().clone()
            changed[:, first:last] = 0
            delta = model(changed) - output.detach()
            perturb.append(
                dict(
                    first_step=first,
                    last_exclusive=last,
                    rms_z_change=float(delta.square().mean().sqrt()),
                    samples=len(x),
                )
            )
    summary["past_window_ablation"] = perturb
    summary["history_gradient_semantics"] = (
        "input derivatives at eight frozen origins; finite norms alone do"
        " not prove or disprove vanishing gradients"
    )
    if model.arm == "A2":
        with torch.no_grad():
            means = causal_means(x.detach())
            weights = model.mixer.weight.detach()
            branch = []
            for j, width in enumerate((1, 4, 12)):
                w = weights[:, j * 16 : (j + 1) * 16]
                signal = means[:, :, j * 16 : (j + 1) * 16] @ w.T
                branch.append(
                    dict(
                        window=width,
                        coefficient_norm=float(w.norm()),
                        signal_rms=float(signal.square().mean().sqrt()),
                        identity_deviation=float((w - (torch.eye(16) if j == 0 else 0)).norm()),
                    )
                )
            changed = x.detach().clone()
            changed[:, 30:] += 10
            if not torch.equal(causal_means(changed)[:, :30], means[:, :30]):
                raise ValueError("P026_MULTISCALE_SUFFIX_LEAK")
        summary["branches"] = branch
        pd.DataFrame(
            [
                dict(
                    output_channel=i,
                    input_channel=j % 16,
                    window=(1, 4, 12)[j // 16],
                    weight=float(weights[i, j]),
                )
                for i in range(16)
                for j in range(48)
            ]
        ).to_parquet(destination / "mixer_coefficients.parquet", index=False)
        summary["input_dimension"] = 16
        summary["prefix_causality"] = "PASS"
    if any(not torch.equal(p.detach(), state[n]) for n, p in model.named_parameters()):
        raise ValueError("P026_DIAGNOSTICS_MUTATED_CHECKPOINT")
    summary["inference_and_diagnostic_seconds"] = time.monotonic() - started
    summary["fixed_population_stock_rows"] = samples * 20
    write_json(destination / "mechanisms.json", summary)
    return summary
