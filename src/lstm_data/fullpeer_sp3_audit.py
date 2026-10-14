"""Independent D9 hand oracles and tiny synthetic operator evidence, no fitting."""

from __future__ import annotations

import argparse
import math
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import torch

from .config import write_json
from .fullpeer import (
    FullPeerView,
    _view_binding,
    fullpeer_values,
    operator_batch,
    operator_input,
    require_mode,
)
from .neural_audit import peak_memory
from .neural_engine import SharedLSTM, clip, optimizer, seed_all, session_batches, session_losses
from .neural_market import make_market_view
from .neural_models import create_model
from .operator_artifacts import BoundOperator, load_operator, save_operator
from .p3_domain import MODE, UniverseSpec
from .spatial_operator import SpatialLSTM, StockMixer

UNIVERSE = UniverseSpec("SYN:P411_OPERATOR:v1", ("NOVA", "ORBIT", "PULSE", "QUARK", "RUNE"))


def manual_mixer(hidden: np.ndarray, m1: np.ndarray, m2: np.ndarray) -> tuple[np.ndarray, ...]:
    """Independent scalar sums, population variance and erf GELU; no production/Torch calls."""
    normalized = np.asarray(
        [
            [
                (float(v) - sum(row) / 32)
                / math.sqrt(sum((float(a) - sum(row) / 32) ** 2 for a in row) / 32 + 1e-5)
                for v in row
            ]
            for row in hidden
        ]
    )
    compressed = np.asarray(
        [
            [sum(float(m1[k, i]) * normalized[i, c] for i in range(5)) for c in range(32)]
            for k in range(2)
        ]
    )
    activated = np.asarray(
        [
            [0.5 * float(v) * (1 + math.erf(float(v) / math.sqrt(2))) for v in row]
            for row in compressed
        ]
    )
    message = np.asarray(
        [
            [sum(float(m2[i, k]) * activated[k, c] for k in range(2)) for c in range(32)]
            for i in range(5)
        ]
    )
    return normalized, compressed, activated, message, hidden + message


def planted(mixer: StockMixer) -> None:
    """Preregistered one-edge hidden law, not a trained or economic lead–lag estimate."""
    with torch.no_grad():
        mixer.m1.zero_()
        mixer.m2.zero_()
        mixer.m1[0, 1] = 0.7
        mixer.m2[0, 0] = 0.4


def inventory(model: torch.nn.Module) -> dict:
    return {
        name: {"shape": list(p.shape), "count": p.numel()} for name, p in model.named_parameters()
    }


def operator_oracles() -> dict:
    """Deterministic no-update proof, assertions fixed by D9 and fixture_design.json."""
    seed_all(42)
    full = create_model("FULLPEER").eval()
    assert isinstance(full, SharedLSTM)
    spatial = create_model("SP3", universe=UNIVERSE).eval()
    assert isinstance(spatial, SpatialLSTM)
    mc0 = create_model("MC0").eval()
    mc0.load_state_dict(spatial.core.state_dict(), strict=True)
    assert sum(p.numel() for p in full.parameters()) == 15265
    assert sum(p.numel() for p in spatial.parameters()) == 7093
    assert sum(p.numel() for p in spatial.mixer.parameters()) == 20
    assert not list(spatial.mixer.norm.parameters())
    x = torch.randn(2, 5, 48, 21)
    x[..., 16:] = x[:, :1, :, 16:]
    h = spatial.encode_grouped(x.reshape(10, 48, 21))
    identity_error = float((spatial.mixer(h) - h).detach().abs().max())
    score_error = float(
        (spatial(x.reshape(10, 48, 21)) - mc0(x.reshape(10, 48, 21))).detach().abs().max()
    )
    assert identity_error == score_error == 0
    # Identity is per origin; a second origin never contributes to the first mixer.
    layout_error = float((spatial(x.reshape(10, 48, 21))[:5] - spatial(x[0])).detach().abs().max())
    core_layout_error = float((mc0(x.reshape(10, 48, 21))[:5] - mc0(x[0])).detach().abs().max())
    # Different GEMM batch shapes in the original CPU core differ at float32 rounding.
    assert layout_error < 1e-7 and core_layout_error < 1e-7
    hidden = torch.tensor(
        np.arange(160).reshape(5, 32) / 37 + np.sin(np.arange(160).reshape(5, 32)),
        dtype=torch.float64,
        requires_grad=True,
    )
    mixer = StockMixer().double()
    loss = (mixer(hidden)[0, 0] - 2).square()
    loss.backward()
    assert mixer.m1.grad is not None and mixer.m2.grad is not None
    initial_m1, initial_m2 = float(mixer.m1.grad.norm()), float(mixer.m2.grad.norm())
    assert initial_m1 == 0 and initial_m2 > 0
    mixer.zero_grad(set_to_none=True)
    planted(mixer)
    parts = mixer.components(hidden)
    expected = manual_mixer(
        hidden.detach().numpy(), mixer.m1.detach().numpy(), mixer.m2.detach().numpy()
    )
    errors = [float(np.max(np.abs(a.detach().numpy() - b))) for a, b in zip(parts, expected)]
    assert max(errors) < 1e-12
    parts[-1][0, 0].backward()
    assert hidden.grad is not None and mixer.m1.grad is not None
    eventual_m1, cross = float(mixer.m1.grad.norm()), float(hidden.grad[1, 0])
    assert eventual_m1 > 0 and math.isfinite(cross) and abs(cross) > 0
    epsilon = 1e-5
    a, b = hidden.detach().numpy().copy(), hidden.detach().numpy().copy()
    a[1, 0] += epsilon
    b[1, 0] -= epsilon
    fd = float(
        (
            manual_mixer(a, mixer.m1.detach().numpy(), mixer.m2.detach().numpy())[-1][0, 0]
            - manual_mixer(b, mixer.m1.detach().numpy(), mixer.m2.detach().numpy())[-1][0, 0]
        )
        / (2 * epsilon)
    )
    assert abs(fd - cross) < 1e-8
    order = [4, 2, 0, 3, 1]
    permuted = StockMixer().double()
    with torch.no_grad():
        permuted.m1.copy_(mixer.m1[:, order])  # M1 P^T
        permuted.m2.copy_(mixer.m2[order])  # P M2
    equivariance = float((permuted(hidden[order]) - parts[-1][order]).detach().abs().max())
    input_only_error = float((mixer(hidden[order]) - parts[-1][order]).detach().abs().max())
    assert equivariance < 1e-12 and input_only_error > 0.01
    # The actual shared scalar head can observe this transmitted coordinate.
    planted(spatial.mixer)
    with torch.no_grad():
        spatial.core.head.weight.zero_()
        spatial.core.head.weight[0, 0] = 1
        spatial.core.head.bias.zero_()
    hd = hidden.detach().float().requires_grad_()
    score = spatial.core.head(spatial.mixer(hd))[0, 0]
    gradient = torch.autograd.grad(score, hd)[0]
    stockwise = spatial.core.head(hd)[0, 0]
    stockwise_gradient = torch.autograd.grad(stockwise, hd)[0]
    assert gradient[1].abs().sum() > 0 and stockwise_gradient[1].abs().sum() == 0
    changed_h = hd.detach().clone()
    changed_h[1, 0] += 0.2
    contrast = float((spatial.core.head(spatial.mixer(changed_h))[0, 0] - score).detach())
    assert abs(contrast) > 0
    # Ordinary full-peer consumes all four actual 16-channel histories.
    base = x[0].clone()
    v = fullpeer_values(base).requires_grad_()
    y = full(v)
    y[0].backward()
    assert v.grad is not None
    peer_grad = float(v.grad[0, :, 21:].norm())
    weight_grad = full.lstm.get_parameter("weight_ih_l0").grad
    assert weight_grad is not None and peer_grad > 0 and weight_grad.norm() > 0
    altered = base.clone()
    altered[1, -1, 0] += 0.2
    full_contrast = float((full(fullpeer_values(altered))[0] - y[0]).detach())
    assert abs(full_contrast) > 0
    mc0_grad_input = base.clone().requires_grad_()
    mc0_grad = torch.autograd.grad(mc0(mc0_grad_input)[0], mc0_grad_input)[0]
    assert mc0_grad[1:].abs().sum() == 0
    sp3_grad_input = base.clone().requires_grad_()
    sp3_score = spatial(sp3_grad_input)[0]
    sp3_input_grad = torch.autograd.grad(sp3_score, sp3_grad_input)[0]
    assert bool(torch.isfinite(sp3_input_grad).all()) and sp3_input_grad[1, :, :16].norm() > 0
    sp3_changed = base.clone()
    sp3_changed[1, -1, 0] += 0.2
    sp3_input_contrast = float((spatial(sp3_changed)[0] - sp3_score).detach())
    assert abs(sp3_input_contrast) > 0
    sentinel = torch.arange(5 * 48 * 16, dtype=torch.float32).reshape(5, 48, 16)
    sentinel21 = torch.cat((sentinel, torch.zeros(5, 48, 5)), dim=-1)
    sentinel85 = fullpeer_values(sentinel21)
    hand = [
        [
            *sentinel21[i, -1].tolist(),
            *[float(sentinel[j, -1, c]) for j in range(5) if j != i for c in range(16)],
        ]
        for i in range(5)
    ]
    assert sentinel85[:, -1].tolist() == hand
    losses = session_losses(
        torch.zeros(2, 2, 5),
        torch.tensor([[[math.sqrt(2)] * 5, [math.sqrt(6)] * 5], [[math.sqrt(10)] * 5, [0.0] * 5]]),
        torch.tensor([[True, True], [True, False]]),
    )
    assert torch.isclose(losses.mean(), torch.tensor(7.0))
    # Frozen optimizer covers all parameters exactly once, including mixer matrices.
    optimizer_counts = {}
    for name, model in (("FULLPEER", full), ("SP3", spatial)):
        opt = optimizer(model)
        groups = [p for g in opt.param_groups for p in g["params"]]
        assert len(groups) == len({id(p) for p in groups}) == len(list(model.parameters()))
        if name == "SP3":
            model.zero_grad(set_to_none=True)
            model(x.reshape(10, 48, 21)).square().mean().backward()
        norm = clip(model)
        assert math.isfinite(norm)
        optimizer_counts[name] = {
            "covered_tensors": len(groups),
            "preclip_norm": norm,
            "optimizer_steps": 0,
        }
    return {
        "scope": MODE,
        "seed": 42,
        "optimizer_updates": 0,
        "parameters": {"FULLPEER": inventory(full), "SP3": inventory(spatial)},
        "counts": {"FULLPEER": 15265, "MC0": 7073, "SP3": 7093, "mixer": 20},
        "fullpeer_sentinel_endpoint": hand,
        "peer_orders": [
            [s for s in UNIVERSE.symbols if s != target] for target in UNIVERSE.symbols
        ],
        "zero_M2_hidden_error": identity_error,
        "zero_M2_matched_MC0_score_error": score_error,
        "different_batch_layout_error": layout_error,
        "matched_core_different_batch_layout_error": core_layout_error,
        "manual_component_errors_float64": errors,
        "initial_m1_gradient": initial_m1,
        "initial_m2_gradient": initial_m2,
        "nonzero_m2_m1_gradient": eventual_m1,
        "cross_hidden_derivative": cross,
        "finite_difference": fd,
        "finite_difference_error": abs(fd - cross),
        "coordinate_equivariance_error": equivariance,
        "input_only_reorder_error": input_only_error,
        "SP3_cross_score_derivative": float(gradient[1, 0]),
        "MC0_cross_hidden_derivative": float(stockwise_gradient[1].norm()),
        "MC0_cross_input_derivative": float(mc0_grad[1:].norm()),
        "SP3_peer_input_gradient": float(sp3_input_grad[1, :, :16].norm()),
        "SP3_peer_input_score_change": sp3_input_contrast,
        "SP3_hidden_perturbation_score_change": contrast,
        "fullpeer_peer_gradient": peer_grad,
        "fullpeer_peer_perturbation_score_change": full_contrast,
        "session_weighted_loss": float(losses.mean()),
        "sampler_19_sizes": [len(v) for v in session_batches(19, 42, 1, shuffle=True)],
        "optimizer": optimizer_counts,
        "trace": {
            "H_coordinate0": hidden[:, 0].detach().tolist(),
            "LN_coordinate0": parts[0][:, 0].detach().tolist(),
            "M1_LN_coordinate0": parts[1][:, 0].detach().tolist(),
            "GELU_coordinate0": parts[2][:, 0].detach().tolist(),
            "message_coordinate0": parts[3][:, 0].detach().tolist(),
            "H_tilde_coordinate0": parts[4][:, 0].detach().tolist(),
            "readout": "head selects coordinate0, bias0, eval dropout off",
            "numerical_sensitivity": "Descriptive derivative; no causal financial evidence",
        },
    }


def source_oracles(out: Path) -> dict:
    """Existing fabricated P2 certificates/target population, no empirical data or neural fit."""
    from .regime_peer_audit import fabricated_case

    data, history, prep, validation, permission = fabricated_case()
    small = replace(data, origins=data.origins[-2:])
    market = make_market_view(small, validation, prep, permission, history, allow_synthetic=True)
    fullview = FullPeerView(market, data.universe, _view_binding(market))
    assert fullview.market is market and fullview.market.values is market.values
    seed_all(42)
    batches = {a: operator_batch(market, (0,), architecture=a) for a in ("FULLPEER", "SP3")}
    base = market.batch((0,))
    evidence = {}
    for a, batch in batches.items():
        assert torch.equal(batch.batch.inputs[..., :21], base.inputs)
        assert torch.equal(batch.batch.targets, base.targets)
        assert torch.equal(batch.batch.origins, base.origins)
        model = create_model(a, universe=data.universe).eval()
        bound = BoundOperator(model, batch.binding)
        scores = bound.batch_scores(batch).detach()
        path = out / (a.lower() + "_operator.pt")
        saved = save_operator(path, bound)
        loaded = load_operator(path, batch.binding, a)
        assert torch.equal(loaded.batch_scores(batch), scores)
        evidence[a] = {
            "binding": batch.binding.binding_id,
            "operator": bound.operator_id,
            "scores": scores.tolist(),
            "artifact": saved,
            "universe": data.universe.symbols,
            "origin_mask": base.origins.tolist(),
        }
    # One on-demand actual encoder→mixer→readout trace, using the same canonical prefix.
    row = data.origins[-1].inputs
    item = operator_input(row, prep, history, permission, architecture="SP3")
    model = create_model("SP3", universe=data.universe).eval()
    assert isinstance(model, SpatialLSTM)
    with torch.no_grad():
        h = model.encode_grouped(item.values)[0]
        initial = model.mixer.components(h)
        planted(model.mixer)
        parts = model.mixer.components(h)
        score = model.core.head(model.core.dropout(parts[-1])).squeeze(-1)
    hand = manual_mixer(
        h.numpy().astype(float),
        model.mixer.m1.detach().numpy().astype(float),
        model.mixer.m2.detach().numpy().astype(float),
    )
    error = float(np.max(np.abs(hand[-1] - parts[-1].numpy())))
    assert error < 1e-6
    first, last = row.stock.steps[0], row.stock.steps[-1]
    stamps = {s.timestamp: s for s in history.stamps}
    clocks = []
    for k, step in ((0, first), (47, last)):
        s = stamps[step.end]
        clocks.append(
            {
                "session": step.session,
                "slot": step.slot,
                "period_start": step.start.isoformat(),
                "period_end": step.end.isoformat(),
                "stock_key": row.stock.lineage[1][k][0],
                "stock_available_at": str(row.available_at[1][k][0]),
                "market_source_ids": s.evidence_ids,
                "market_available_at": str(s.available_at),
                "market_period_end": str(s.period_end),
            }
        )
    return {
        "scope": MODE,
        "source_table_shared_by_object_identity": True,
        "canonical_stock_rows": len(market.values),
        "canonical_market_rows": len(market.market_values),
        "persisted_dense_windows": 0,
        "MC0_PREFIX_EQUAL": True,
        "target_population_equal": True,
        "maturity_population": [(r.session, r.origin) for r in market.rows],
        "models": evidence,
        "forecast_trace_binding": item.trace,
        "clock_trace": clocks,
        "encoded_trace": {
            "H_coordinate0": h[:, 0].tolist(),
            "H_row_norm": h.norm(dim=1).tolist(),
            "initial_M2": "EXACT_ZERO",
            "initial_message_norm": float(initial[3].norm()),
            "initial_cross_stock_sensitivity": 0,
            "LN_coordinate0": parts[0][:, 0].tolist(),
            "M1_LN_coordinate0": parts[1][:, 0].tolist(),
            "GELU_coordinate0": parts[2][:, 0].tolist(),
            "message_coordinate0": parts[3][:, 0].tolist(),
            "H_tilde_coordinate0": parts[4][:, 0].tolist(),
            "readout_scores": score.tolist(),
            "manual_float64_to_float32_error": error,
            "parameter_reference": "fixture_design.json fixed planted M1[0,1]/M2[0,0]",
            "financial_interpretation": "NONE; descriptive untrained operator values",
        },
    }


def audit(out: Path, mode: str = MODE) -> dict:
    require_mode(mode)
    if out.exists():
        raise ValueError("IMMUTABLE_P4_11_OUTPUT_EXISTS")
    start = time.perf_counter()
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        proof = operator_oracles()
        source = source_oracles(out)
    finally:
        torch.set_num_threads(previous)
    write_json(out / "hand_oracles.json", proof)
    write_json(out / "source_integration.json", source)
    result = {
        "status": "P4_11_OPERATOR_ORACLES_PASS",
        "mode": mode,
        "seconds": time.perf_counter() - start,
        "peak_RSS_bytes": peak_memory(),
        "device": "CPU",
        "torch": torch.__version__,
        "real_pairs": 0,
        "D6g_pairs": 0,
        "scientific_status": "HOLD",
    }
    write_json(out / "synthetic_evidence.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", default=MODE)
    args = parser.parse_args()
    print(audit(args.out, args.mode))


if __name__ == "__main__":
    main()
