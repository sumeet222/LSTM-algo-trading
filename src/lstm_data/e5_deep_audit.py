"""Immutable staged E5 v2 diagnostic execution, synthetic only, CPU seed42."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .baseline_ridge import windows
from .config import digest, write_json
from .e5_audit import health_fixture
from .e5_fixture_v2 import B2, FIXTURE, fixture, planted_returns, step_values, training_preparation
from .e5_health_diagnosis import diagnose
from .neural_artifacts import MODE
from .neural_audit import peak_memory
from .neural_engine import (
    SharedLSTM,
    batch_prediction,
    clip,
    norm_summary,
    optimizer,
    seed_all,
    session_batches,
    session_losses,
)
from .neural_lifecycle import state_hash
from .neural_models import NeuralModel, create_model
from .p3_domain import Permission
from .peer_neural import E5View, make_e5_view

PROOF = Path("reports/data_audit/ta_p4_e5_e5l_2026-10-13_225047/failed_health_proof.json")


def original_oracle() -> dict:
    """Original unchanged arithmetic plus finite difference/graph diagnostic; zero updates."""
    result = diagnose(PROOF, Permission(MODE))
    seed_all(42)
    batch = health_fixture()
    model = create_model("E5")
    model.eval()
    x = batch.inputs.detach().clone().reshape(-1, 48, 23).requires_grad_()
    prediction = model(x)
    prediction[0].backward()
    assert x.grad is not None
    gradient = x.grad[0, :, 21:]
    # Double precision isolates local numerical sensitivity from float32 roundoff.
    model.double()
    xd = x.detach().double().requires_grad_()
    v = model(xd)[0]
    g = torch.autograd.grad(v, xd)[0][0, -1, 21]
    eps = 1e-5
    plus, minus = xd.detach().clone(), xd.detach().clone()
    plus[0, -1, 21] += eps
    minus[0, -1, 21] -= eps
    with torch.no_grad():
        fd = float((model(plus)[0] - model(minus)[0]) / (2 * eps))
        repeated = torch.equal(model(xd), model(xd))
    z = batch.inputs.detach().numpy()[..., 0].astype(float)
    mean = (z.sum(axis=2, keepdims=True) - z) / 4
    centered = mean - np.median(mean, axis=2, keepdims=True)
    identity = -(z - np.median(z, axis=2, keepdims=True)) / 4
    result.update(
        {
            "hypothetical_TG0_center_identity_error": float(np.max(np.abs(centered - identity))),
            "TG0_actually_applied_in_v1": False,
            "ranking_identity": "rank(peer_mean) = reverse rank(own_M1); common sum cancels",
            "local_sensitivity": {
                "autograd": float(g),
                "finite_difference": fd,
                "epsilon": eps,
                "absolute_tolerance": 1e-7,
                "absolute_error": abs(float(g) - fd),
            },
            "input_peer_gradients_all_steps": gradient.detach().tolist(),
            "nonzero_peer_gradient_steps": int((gradient.norm(dim=1) > 0).sum()),
            "eval_repeat_exact": repeated,
            "zero_peer_ablation": "off-manifold; descriptive, not independent peer importance",
            "optimizer_updates": 0,
        }
    )
    if abs(float(g) - fd) > 1e-7 or not repeated:
        raise ValueError("ORIGINAL_GRAPH_SENSITIVITY_DEFECT")
    return result


def views(*, null: bool = False) -> tuple[E5View, E5View, dict]:
    data, history, guard = fixture(null=null)
    prep = training_preparation(data, guard)
    inner, valid, _ = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))
    inner = replace(inner, fitted_at=inner.stop)
    train = make_e5_view(data, inner, prep, guard, history, allow_synthetic=True)
    evaluation = make_e5_view(data, valid, prep, guard, history, allow_synthetic=True)
    trace = {
        "train_sessions": len(train.sessions),
        "valid_sessions": len(evaluation.sessions),
        "train_origins": len(train.rows),
        "valid_origins": len(evaluation.rows),
        "valid_excluded": evaluation.excluded,
        "train_version": train.version,
        "valid_version": evaluation.version,
        "preparation": train.peer.market.preparation_id,
        "epsilon": prep.tg0_floor.epsilon,
        "floor": prep.tg0_floor.floor_id,
    }
    if len(evaluation.sessions) < 50 or any(
        sum(r.origin == i for r in evaluation.rows) < 25 for i in (1, 2)
    ):
        raise ValueError("FIXED_CALENDAR_VALIDATION_INADEQUATE")
    return train, evaluation, trace


def evaluate(
    model: NeuralModel, view: E5View, *, own_only: bool = False
) -> tuple[float, list[float]]:
    model.eval()
    losses, scores = [], []
    with torch.no_grad():
        for positions in session_batches(len(view.sessions), 42, 1, shuffle=False):
            batch = view.batch(positions)
            if own_only:
                batch = replace(batch, inputs=batch.inputs[..., :21])
            y = batch_prediction(model, batch)
            losses.extend(session_losses(y, batch.targets, batch.origins).tolist())
            scores.extend(y[batch.origins].reshape(-1).tolist())
    return float(np.mean(losses)), scores


def zero_reference(view: E5View) -> float:
    losses = []
    for positions in session_batches(len(view.sessions), 42, 1, shuffle=False):
        batch = view.batch(positions)
        losses.extend(
            session_losses(torch.zeros_like(batch.targets), batch.targets, batch.origins).tolist()
        )
    return float(np.mean(losses))


def fit_health(
    train: E5View, valid: E5View, *, own_only: bool = False, update_cap: int = 256
) -> dict:
    """Prospective fixed diagnostic horizon; no validation checkpoint selection."""
    if type(update_cap) is not int or update_cap not in (256, 1024):
        raise ValueError("REGISTERED_DIAGNOSTIC_HORIZON_REQUIRED")
    seed_all(42)
    model = create_model("MC0" if own_only else "E5")
    assert isinstance(model, SharedLSTM)
    opt = optimizer(model)
    initial, _ = evaluate(model, train, own_only=own_only)
    losses, norms, peer_grads, peer_weight_grads = [], [], [], []
    started = time.monotonic()
    updates, epoch = 0, 1
    while updates < update_cap:
        for positions in session_batches(len(train.sessions), 42, epoch, shuffle=True):
            if updates == update_cap:
                break
            batch = train.batch(positions)
            if own_only:
                batch = replace(batch, inputs=batch.inputs[..., :21])
            else:
                batch.inputs.requires_grad_()
            model.train()
            opt.zero_grad(set_to_none=True)
            loss = session_losses(
                batch_prediction(model, batch), batch.targets, batch.origins
            ).mean()
            loss.backward()
            if not own_only:
                weight_gradient = dict(model.named_parameters())["lstm.weight_ih_l0"].grad
                assert batch.inputs.grad is not None and weight_gradient is not None
                peer_grads.append(float(batch.inputs.grad[..., 21:].norm()))
                peer_weight_grads.append(float(weight_gradient[:, 21:].norm()))
            norms.append(clip(model))
            opt.step()
            losses.append(float(loss.detach()))
            updates += 1
        epoch += 1
    final_train, _ = evaluate(model, train, own_only=own_only)
    final_valid, scores = evaluate(model, valid, own_only=own_only)
    return {
        "seed": 42,
        "updates": updates,
        "initial_train_mse": initial,
        "final_train_mse": final_train,
        "heldout_mse": final_valid,
        "zero_reference_mse": zero_reference(valid),
        "update_losses": losses,
        "gradient_summary": norm_summary(tuple(norms)),
        "min_peer_input_gradient": min(peer_grads) if peer_grads else None,
        "min_peer_input_weight_gradient": min(peer_weight_grads) if peer_weight_grads else None,
        "scores": scores,
        "parameter_count": sum(p.numel() for p in model.parameters()),
        "state_sha": state_hash(model),
        "seconds": time.monotonic() - started,
        "peak_memory": peak_memory(),
    }


def finite_oracle() -> dict:
    """Hand-checkable conditional counterexample and finite TG0/population checks."""
    at = pd.Timestamp("2023-03-01T15:30Z")
    a = np.zeros((5, 16))
    a[0, B2] = 1
    a[1:, 0] = (1, 2, 3, 4)
    b = a.copy()
    b[1:, 0] = (-1, -2, -3, -4)
    ya, yb = planted_returns(a, at) / 1e-4, planted_returns(b, at) / 1e-4
    assert np.array_equal(a[0], b[0]) and ya[0] == 2.5 and yb[0] == -2.5
    perm = np.array([4, 2, 0, 3, 1])
    np.testing.assert_array_equal(planted_returns(a[perm], at), planted_returns(a, at)[perm])
    data, _, _ = fixture()
    errors, positives, maturity = [], 0, []
    for row in data.origins:
        assert row.inputs.plan.cutoff is not None and row.label.maturity is not None
        expected = (
            planted_returns(step_values(row.inputs.plan.cutoff), row.inputs.plan.cutoff) / 1e-4
        )
        assert row.label.centered_returns is not None
        actual = np.asarray(row.label.centered_returns) / 1e-4
        errors.append(float(np.max(np.abs(actual - expected))))
        positives += int(np.any(actual > 0))
        maturity.append(float((row.label.maturity - row.inputs.plan.cutoff).total_seconds()))
        assert row.label.unscaled_mad == 0
    return {
        "status": "ORACLE_PASS",
        "same_own_input_two_targets": [ya[0], yb[0]],
        "rank_reversal": True,
        "alternate_order_equivariant": True,
        "population_own_Bayes_MSE": 0.05,
        "peer_formula_population_MSE": 0.0,
        "TG0_log_exp_max_error": max(errors),
        "origins": len(data.origins),
        "positive_signal_origins": positives,
        "negative_signal_origins": len(errors) - positives,
        "maturity_seconds_min_max": [min(maturity), max(maturity)],
        "source_contract": "fabricated FT0/D7 values; actual P2 normalization and TG0 references",
    }


def health(out: Path) -> dict:
    config_path = out / "fixture_v2_config.json"
    config = json.loads(config_path.read_text())
    registered = {
        "24b27ce0f5727d2fde73b13506b10b2e41f5f3fb72c92ecdf5eb674be3a4f066": 256,
        "856dc579bd6ba4772014b54af91b32d646681cdd00011301dac3a5564b3abed6": 1024,
    }
    if config["fixture"] != FIXTURE or config["updates_per_arm"] not in (256, 1024):
        raise ValueError("PROSPECTIVE_V2_CONFIG_REQUIRED")
    cap = config["updates_per_arm"]
    if digest(config_path) not in registered or registered[digest(config_path)] != cap:
        raise ValueError("IMMUTABLE_PROSPECTIVE_CONFIG_SHA_REQUIRED")
    write_json(
        out / "health_attempt_reservation.json",
        {
            "config_sha": digest(config_path),
            "code": digest(Path(__file__)),
            "fixture_code": digest(Path(__file__).with_name("e5_fixture_v2.py")),
            "arms": config["arms"],
            "diagnostic_updates_cap": 4 * cap,
            "real_pairs": 0,
            "forecast": config["compute_forecast"],
        },
    )
    train, valid, population = views()
    results = {}
    for name, own in (
        ("E5_PLANTED", False),
        ("MC0_PLANTED", True),
        ("E5_PLANTED_EXACT_REPEAT", False),
    ):
        result = fit_health(train, valid, own_only=own, update_cap=cap)
        write_json(out / (name + ".json"), result)
        results[name] = result
        print(
            {"arm": name, "heldout_mse": result["heldout_mse"], "seconds": result["seconds"]},
            flush=True,
        )
    null_train, null_valid, null_population = views(null=True)
    result = fit_health(null_train, null_valid, update_cap=cap)
    write_json(out / "E5_NULL.json", result)
    results["E5_NULL"] = result
    primary, own, repeat = (
        results[n] for n in ("E5_PLANTED", "MC0_PLANTED", "E5_PLANTED_EXACT_REPEAT")
    )
    thresholds = config["primary_thresholds"]
    checks = {
        "train_reduction": primary["final_train_mse"]
        < thresholds["train_final_lt_initial_fraction"] * primary["initial_train_mse"],
        "heldout_signal": primary["heldout_mse"]
        < thresholds["valid_final_lt_zero_reference_fraction"] * primary["zero_reference_mse"],
        "MC0_information_control": own["heldout_mse"]
        > thresholds["MC0_valid_gt_E5_multiple"] * primary["heldout_mse"],
        "null_not_spurious_learning": result["heldout_mse"]
        > thresholds["null_valid_gt_own_Bayes_reference_fraction"] * result["zero_reference_mse"],
        "positive_peer_gradients": primary["min_peer_input_gradient"] > 0
        and primary["min_peer_input_weight_gradient"] > 0,
        "repeat_exact": primary["scores"] == repeat["scores"]
        and primary["state_sha"] == repeat["state_sha"],
    }
    evidence = {
        "status": "PASS" if all(checks.values()) else "FAILED",
        "checks": checks,
        "population": population,
        "null_population": null_population,
        "config_sha": digest(config_path),
        "diagnostic_updates": 4 * cap,
        "arms": {
            n: {k: v for k, v in r.items() if k not in ("scores", "update_losses")}
            for n, r in results.items()
        },
    }
    write_json(out / "health_v2_result.json", evidence)
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--stage", choices=("original", "oracle", "health"), required=True)
    args = parser.parse_args()
    torch.set_num_threads(1)
    if args.stage == "original":
        write_json(args.out / "original_failure_oracle.json", original_oracle())
    elif args.stage == "oracle":
        result = finite_oracle()
        write_json(args.out / "fixture_v2_oracle.json", result)
        print(result)
    else:
        print(health(args.out)["status"])


if __name__ == "__main__":
    main()
