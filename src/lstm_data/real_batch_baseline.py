"""Optional, separately approved147-column ridge; never consumes a neural pair."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from .baseline_ridge import LAGS, PENALTIES, choose_penalty, session_weights, solve_weighted
from .config import digest, write_json
from .neural_engine import session_batches
from .pilot_postrun import summarize
from .pretraining_policy import CANDIDATE
from .real_batch_authority import load_plan
from .real_batch_data import ConditionedView, load_batch_inputs


def market_lags(x: np.ndarray) -> np.ndarray:
    """Canonical112stock columns followed by35market columns, not interleaved."""
    if x.shape[-3:] != (5, 48, 21) or not np.isfinite(x).all():
        raise ValueError("EXACT_FINITE_MATCHED_21_CHANNEL_BASELINE_REQUIRED")
    selected = x[..., [47 - lag for lag in LAGS], :]
    return np.concatenate(
        (selected[..., :16].reshape(-1, 112), selected[..., 16:21].reshape(-1, 35)), axis=1
    ).astype(np.float64)


def design(view: ConditionedView) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    features, labels, keys = [], [], []
    for positions in session_batches(len(view.sessions), 42, 1, shuffle=False):
        batch = view.batch(positions)
        features.append(market_lags(batch.inputs[batch.origins].numpy()))
        labels.append(batch.targets[batch.origins].numpy().reshape(-1))
        keys.extend(
            (day, o + 1, s)
            for i, day in enumerate(batch.ids)
            for o in (0, 1)
            if bool(batch.origins[i, o])
            for s in CANDIDATE
        )
    return (
        np.concatenate(features),
        np.concatenate(labels).astype(float),
        session_weights(tuple(keys)),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    plan_ref = {"path": str(args.plan), "sha256": digest(args.plan)}
    plan, review = load_plan(Path.cwd(), plan_ref)
    decision = json.loads(args.approval.read_text())
    if (
        decision.get("actor_type") != "human"
        or decision.get("status") != "APPROVED"
        or decision.get("owner") != "Track A researcher"
        or decision.get("scope") != "RIDGE_MARKET_147_WF1_ONLY"
        or decision.get("plan_sha256") != plan_ref["sha256"]
        or not decision.get("response_text")
        or not decision.get("response_provenance")
    ):
        raise ValueError("SEPARATE_ACTUAL_MARKET_RIDGE_APPROVAL_REQUIRED")
    if args.output.exists():
        raise ValueError("MARKET_RIDGE_ATTEMPT_ALREADY_EXISTS_NO_REFIT_REPLAY")
    torch.set_num_threads(1)
    binding = json.loads((review.root / plan["dataset"]["path"]).read_text())
    inputs = load_batch_inputs(review, binding)
    views = {k: inputs.view(k, 21) for k in ("inner", "validation", "refit", "WF1")}
    if any(v.version != plan["runs"][0]["views"][k]["view_id"] for k, v in views.items()):
        raise ValueError("EXACT_REVIEWED_MARKET_RIDGE_MASK_REQUIRED")
    t = time.monotonic()
    x, y, w = design(views["inner"])
    vx, vy, vw = design(views["validation"])
    fx, fy, fw = design(views["refit"])
    ex, _, _ = design(views["WF1"])
    application = time.monotonic() - t
    args.output.mkdir(parents=True)
    write_json(args.output / "STARTED.json", {"approval": decision, "neural_pairs_added": 0})
    losses = []
    t = time.monotonic()
    for penalty in PENALTIES:
        fit = solve_weighted(x, y, w, penalty)
        errors = vy - fit.intercept - vx @ np.asarray(fit.coefficients)
        losses.append(
            {
                "penalty": penalty,
                "MSE": float(vw @ errors**2),
                "condition": fit.condition,
                "residual": fit.residual_norm,
            }
        )
    selection_seconds = time.monotonic() - t
    chosen = choose_penalty(tuple((r["penalty"], r["MSE"]) for r in losses))
    t = time.monotonic()
    final = solve_weighted(fx, fy, fw, chosen)
    refit_seconds = time.monotonic() - t
    scores = (final.intercept + ex @ np.asarray(final.coefficients)).reshape(-1, 5)
    write_json(
        args.output / "result.json",
        {
            "status": "COMPLETED_SEPARATELY_APPROVED_NONNEURAL",
            "decision": decision,
            "candidates": losses,
            "chosen_penalty": chosen,
            "coefficients": final.coefficients,
            "intercept": final.intercept,
            "condition": final.condition,
            "residual": final.residual_norm,
            "metrics": summarize(views["WF1"].stock, scores),
            "scores": scores.tolist(),
            "origin_keys": [(r.session, r.origin) for r in views["WF1"].rows],
            "timing_seconds": {
                "design_application": application,
                "five_inner_fits": selection_seconds,
                "fresh_refit": refit_seconds,
                "total": time.monotonic() - started,
            },
            "fit_counts": {"inner": 5, "fresh_refit": 1, "neural": 0},
            "evidence_grade": "RESEARCHER_ATTESTED_IDEALIZED_RETROSPECTIVE_CANDIDATE_ONLY",
        },
    )
    print(
        json.dumps(
            {
                "status": "COMPLETED",
                "lambda": chosen,
                "seconds": time.monotonic() - started,
                "new_neural_pairs": 0,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
