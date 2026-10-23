"""P024 real-source zero-update proof, forward/backward, checkpoint and export checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch

from .config import fingerprint, write_json
from .controlled_loss import LossPolicy
from .hf1m_ft16_source import checked, ref
from .hf1m_training_run import predictions
from .neural_engine import batch_prediction, clip, session_losses
from .neural_lifecycle import state_hash
from .objective_screen_source import scoped_view
from .optimization_screen import VARIANTS, make_model, make_optimizer, parameter_audit
from .optimization_screen_run import Telemetry, persist, save_reload
from .visualization.hf1m_long import LongStudy


def preflight(out: Path, tag: str = "final") -> None:
    if tag not in {"final", "initial"}:
        raise ValueError("P024_PREFLIGHT_TAG")
    stage0 = json.loads((out / "stage_0_receipt.json").read_text())
    if stage0["status"] != "PASS_STAGE0":
        raise ValueError("P024_STAGE0_REQUIRED")
    study = LongStudy.discover(Path.cwd())
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    views = {role: scoped_view(study, role, stage=7) for role in stage0["views"]}
    private = Path("artifacts/hf20_hf1m_long_v1") / out.name / ("zero_update_preflight_" + tag)
    private.mkdir(parents=True, exist_ok=False)
    checks = []
    with patch.object(
        torch.optim.AdamW, "step", side_effect=AssertionError("P024_NO_OPTIMIZER_STEP_IN_PREFLIGHT")
    ):
        for v in VARIANTS:
            model = make_model(v)
            initial = state_hash(model)
            opt = make_optimizer(model, v)
            batch = views["inner_train"].batch(tuple(range(16)))
            policy = LossPolicy("T2", scale=views["inner_train"].source.fit["t2_scale"])
            observer = Telemetry(model, opt, private / (v.arm + "_hook.jsonl"), "inner_train", 1)
            raw = batch_prediction(model, batch)
            loss = policy.objective(raw, batch.targets, batch.origins, stock_count=20)
            loss.mean().backward()
            pre = clip(model)
            observer.pre(opt, (), {})
            observer.post(opt, (), {})  # Observe unchanged parameters; never calls step.
            observer.close()
            np.testing.assert_allclose(observer.records[0]["preclip_norm"], pre, rtol=2e-6)
            if observer.records[0]["update_norm"] != 0 or opt.state:
                raise ValueError("P024_PREFLIGHT_UPDATE_DETECTED")
            if not all(
                p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters()
            ):
                raise ValueError("P024_PREFLIGHT_GRADIENTS")
            z = torch.asinh(batch.targets / views["inner_train"].source.fit["t2_scale"])
            expected = session_losses(raw, z, batch.origins, stock_count=20)
            torch.testing.assert_close(loss, expected, rtol=0, atol=0)
            checkpoint, loaded = save_reload(
                private / (v.arm + ".pt"), model, v, dict(preflight=True, initial_hash=initial)
            )
            if initial != state_hash(model):
                raise ValueError("P024_PREFLIGHT_WEIGHTS_CHANGED")
            fresh = make_model(v)
            if state_hash(fresh) != initial or make_optimizer(fresh, v).state:
                raise ValueError("P024_PREFLIGHT_REFIT_NOT_FRESH")
            populations = []
            for role, view in views.items():
                p = LossPolicy("T2", scale=view.source.fit["t2_scale"])
                a = predictions(
                    model,
                    view,
                    p,
                    dict(checkpoint_sha256=checkpoint["sha256"], arm=v.arm, seed=v.seed),
                )
                b = predictions(
                    loaded,
                    view,
                    p,
                    dict(checkpoint_sha256=checkpoint["sha256"], arm=v.arm, seed=v.seed),
                )
                if not a.equals(b):
                    raise ValueError("P024_PREFLIGHT_EXPORT_RELOAD")
                # Keep compact excerpts and full-population hashes, avoiding array duplication.
                path = private / (v.arm + "_" + role + "_sample.parquet")
                a.head(40).to_parquet(path, index=False)
                populations.append(
                    dict(
                        role=role,
                        rows=len(a),
                        population_sha256=fingerprint(a[["origin_id", "ticker"]].values.tolist()),
                        prediction_sha256=fingerprint(a.raw_net_output.tolist()),
                        sample=ref(path),
                        full_reload_max_error=0.0,
                    )
                )
            sample = batch.inputs[batch.origins].reshape(-1, 48, 16)
            model.eval()
            with torch.no_grad():
                output, (h, c) = model.lstm(sample)
                zero = torch.zeros((v.layers, len(sample), v.hidden))
                explicit, (h0, c0) = model.lstm(sample, (zero, zero))
                torch.testing.assert_close(output, explicit, rtol=0, atol=0)
                torch.testing.assert_close(h, h0, rtol=0, atol=0)
                torch.testing.assert_close(c, c0, rtol=0, atol=0)
            checks.append(
                dict(
                    arm=v.arm,
                    audit=parameter_audit(v),
                    initial_hash=initial,
                    checkpoint=checkpoint,
                    gradients_finite=True,
                    forward_backward_batches=1,
                    optimizer_step_calls=0,
                    hidden_shape=list(h.shape),
                    cell_shape=list(c.shape),
                    hidden_abs_max=float(h.abs().max()),
                    cell_abs_max=float(c.abs().max()),
                    populations=populations,
                )
            )
    progress_dir = private / "progress_regression"
    progress_dir.mkdir()
    epochs = []
    for phase, count in [("calibration", 12), ("refit", 2)]:
        for epoch in range(1, count + 1):
            record = dict(phase=phase, training=dict(epoch=epoch), optimizer_updates=0)
            epochs.append(record)
            persist(progress_dir, record, epochs)
    try:
        persist(progress_dir, epochs[-1], epochs)
    except FileExistsError:
        pass
    else:
        raise ValueError("P024_IMMUTABLE_RECEIPT_NOT_ENFORCED")
    if (
        json.loads((progress_dir / "epochs_progress.json").read_text()) != dict(epochs=epochs)
        or len(list((progress_dir / "epoch_receipts").glob("*.json"))) != 14
    ):
        raise ValueError("P024_PROGRESS_REGRESSION")
    for r in stage0["protected_refs"]:
        checked(r)
    write_json(
        out / ("stage_1_preflight_" + tag + ".json"),
        dict(
            status="PASS_ZERO_UPDATE_PREFLIGHT",
            checks=checks,
            optimizer_step_calls=0,
            model_starts=0,
            immutable_receipts=14,
            duplicate_receipt_rejected=True,
            protected_numeric_access=False,
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tag", choices=["initial", "final"], default="final")
    args = parser.parse_args()
    preflight(args.out, args.tag)
