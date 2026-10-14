"""Read-only proof diagnosis: no optimizer step, fixture change or scientific fit."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from .baseline_ridge import LAGS
from .config import digest
from .e5_audit import health_fixture
from .ft0_transforms import identity
from .neural_artifacts import MODE
from .neural_engine import batch_prediction, optimizer, seed_all, session_losses
from .neural_models import create_model
from .p3_domain import Permission
from .peer_inputs import M1_INDEX, peer_summaries


def diagnose(proof_path: Path, permission: Permission) -> dict:
    """Reconstruct source-independent data and one backward pass, never train again."""
    permission.ensure()
    expected = "bdefd7800e17992fb629cfbee62df2ba9701a3e9cd4fae40a7ea9a6f9f3187df"
    if digest(proof_path) != expected:
        raise ValueError("ORIGINAL_FAILED_PROOF_SHA_REQUIRED")
    proof = json.loads(proof_path.read_text())
    if proof["scope"] != MODE:
        raise ValueError("SYNTHETIC_FAILURE_PROOF_REQUIRED")
    for name in ("log", "status"):
        path = Path(proof[name])
        if path.is_absolute() or ".." in path.parts or path.parts[:2] != ("reports", "data_audit"):
            raise ValueError("PROJECT_SYNTHETIC_FAILURE_REFERENCE_REQUIRED")
        if digest(path) != proof[name + "_sha"]:
            raise ValueError("FAILED_PROOF_SHA_CHANGED")
    old = proof["health"]
    seed_all(42)
    batch = health_fixture()
    batch.validate()
    values = batch.inputs.detach().numpy()
    # Independent four-peer sums/centered population variance, not another production preprocessor.
    z = values[..., M1_INDEX]
    oracle = np.empty(values.shape[:-1] + (2,), dtype=np.float32)
    for i in range(5):
        peers = z[:, :, np.arange(5) != i, :].astype(np.float64)
        mean = peers.mean(axis=2)
        oracle[:, :, i, :, 0] = mean
        oracle[:, :, i, :, 1] = np.sqrt(((peers - mean[:, :, None]) ** 2).mean(axis=2))
    assert np.array_equal(oracle, values[..., 21:])
    assert np.array_equal(batch.targets.numpy(), oracle[..., -1, 0])
    prefix = values[..., :21].copy()
    ablated = values.copy()
    ablated[..., 21:] = 0
    assert np.array_equal(prefix, ablated[..., :21])
    model = create_model("E5")
    model.eval()
    score = batch_prediction(model, batch)
    loss = session_losses(score, batch.targets, batch.origins).mean()
    loss.backward()
    if batch.inputs.grad is None:
        raise ValueError("E5_DIAGNOSTIC_GRADIENT_REQUIRED")
    gradient = {
        name: float(parameter.grad.norm())
        for name, parameter in model.named_parameters()
        if parameter.grad is not None
    }
    assert len(gradient) == 6 and all(np.isfinite(v) and v > 0 for v in gradient.values())
    assert abs(float(loss.detach()) - old["initial_eval_MSE"]) < 1e-7
    with torch.no_grad():
        no_peer = model(torch.tensor(ablated).reshape(-1, 48, 23)).reshape(16, 2, 5)
        loss_zero = float(session_losses(no_peer, batch.targets, batch.origins).mean())
    y = batch.targets.numpy().reshape(-1).astype(np.float64)
    own = np.stack([values[..., 47 - lag, M1_INDEX].reshape(-1) for lag in LAGS], axis=1)
    endpoint_mean = values[..., -1, 21].reshape(-1).astype(np.float64)
    # OLS projections are an identifiability hand oracle only. No new ridge fit, selection or model.
    own_design = np.column_stack((np.ones(len(y)), own))
    peer_design = np.column_stack((own_design, endpoint_mean))
    own_residual = y - own_design @ np.linalg.lstsq(own_design, y, rcond=None)[0]
    peer_residual = y - peer_design @ np.linalg.lstsq(peer_design, y, rcond=None)[0]
    opt = optimizer(model)
    norms = torch.tensor([v for v in gradient.values()], dtype=torch.float64)
    result = {
        "scope": MODE,
        "status": "E5_HEALTH_BLOCKED",
        "proof_sha": digest(proof_path),
        "original_measured_code_sha": proof["code_hash_at_measured_failure"],
        "fixture_sha": identity([values.tolist(), batch.targets.tolist(), 8049]),
        "fixture_size": [16, 2, 5, 48, 23],
        "parameter_count": sum(p.numel() for p in model.parameters()),
        "peer_oracle_exact": True,
        "target_is_endpoint_peer_mean": True,
        "current_initial_MSE_no_updates": float(loss.detach()),
        "current_initial_zero_peer_MSE_same_weights": loss_zero,
        "prior_final_MSE": old["final_eval_MSE"],
        "prior_final_zero_peer_MSE": old["peer_zero_ablation_MSE"],
        "unchanged_gate": {
            "final_bound": 0.35 * old["initial_eval_MSE"],
            "actual_final": old["final_eval_MSE"],
            "ablation_bound": 2 * old["final_eval_MSE"],
            "actual_ablation": old["peer_zero_ablation_MSE"],
            "both_failed": (
                old["final_eval_MSE"] >= 0.35 * old["initial_eval_MSE"]
                and old["peer_zero_ablation_MSE"] <= 2 * old["final_eval_MSE"]
            ),
        },
        "peer_channel_std": np.std(values[..., 21:], axis=(0, 1, 2, 3)).tolist(),
        "target_std": float(np.std(y)),
        "initial_session_MSE": session_losses(
            score.detach(), batch.targets, batch.origins
        ).tolist(),
        "target_min_max": [float(y.min()), float(y.max())],
        "own_endpoint_target_corr": float(np.corrcoef(own[:, 0], y)[0, 1]),
        "peer_mean_target_corr": float(np.corrcoef(endpoint_mean, y)[0, 1]),
        "own_rank": int(np.linalg.matrix_rank(own_design)),
        "peer_augmented_rank": int(np.linalg.matrix_rank(peer_design)),
        "own_linear_projection_MSE": float(np.mean(own_residual**2)),
        "peer_linear_projection_MSE": float(np.mean(peer_residual**2)),
        "gradient_norms": gradient,
        "peer_input_gradient_norms": [float(batch.inputs.grad[..., c].norm()) for c in (21, 22)],
        "initial_global_preclip_norm": float(norms.norm()),
        "initial_would_clip": bool(norms.norm() > 1),
        "historical_clipping_fraction": "NOT_RECORDED; no sixty-step repeat without defect",
        "optimizer_groups": [{"lr": g["lr"], "decay": g["weight_decay"]} for g in opt.param_groups],
        "new_optimizer_steps": 0,
        "new_health_runs": 0,
        "historical_steps_per_run": 60,
        "historical_runs": 2,
        "labels": (
            "Direct same-input peer mean target; no ProxyLabelSample, "
            "TG0 centering/MAD/floor or maturity clocks"
        ),
        "conclusion": (
            "No demonstrated tensor/loss/gradient/ablation defect. Data identifiable; "
            "fixed sixty-update acceptance unsupported, fixture not mature TG0 proof."
        ),
        "two_pass_fit": "NOT_RUN",
        "final_checkpoint": "NOT_CREATED",
        "real_pairs": "0/40",
    }
    assert old["passed"] is False
    assert peer_residual.max() < 1e-12
    assert np.isfinite(loss_zero)
    # Verify the original production summary math agrees too, without fitting any scaler.
    np.testing.assert_array_equal(
        peer_summaries(values[0, 0, :, :, :16]).astype(np.float32), oracle[0, 0]
    )
    return result
