"""P027 session objective, telemetry and immutable model export; no implicit fit authority."""

from __future__ import annotations

import hashlib
import io
import json
import math
import random
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import atomic_new, fingerprint
from .controlled_loss import LossPolicy
from .hf1m_ft16_source import ref
from .hf1m_training_run import distribution
from .neural_engine import session_batches
from .objective_screen_source import ordered_targets
from .peer_screen_models import PeerModel, model_for


def state_hash(model: PeerModel) -> str:
    return fingerprint({n: v.detach().cpu().tolist() for n, v in model.state_dict().items()})


def peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == "darwin" else value * 1024


def check_memory() -> None:
    if peak_rss_bytes() > 2_000_000_000:
        raise ValueError("P027_RAM_LIMIT")


def optimizer_hash(model: PeerModel, opt: torch.optim.AdamW) -> str:
    """Hash all named optimizer moments/steps without serialization float coercion."""
    hasher = hashlib.sha256()
    for name, p in model.named_parameters():
        for key, value in sorted(opt.state.get(p, {}).items()):
            hasher.update((name + str(key)).encode())
            if isinstance(value, torch.Tensor):
                a = value.detach().cpu().numpy()
                hasher.update(str((a.dtype, a.shape)).encode())
                hasher.update(a.tobytes())
            else:
                hasher.update(json.dumps(value, sort_keys=True, allow_nan=False).encode())
    return hasher.hexdigest()


def rng_hash() -> str:
    numpy_state = np.random.get_state()
    return fingerprint(
        dict(
            torch=torch.get_rng_state().tolist(),
            python=repr(random.getstate()),
            numpy=[
                numpy_state[0],
                numpy_state[1].tolist(),
                int(numpy_state[2]),
                int(numpy_state[3]),
                float(numpy_state[4]),
            ],
        )
    )


def save_checkpoint(
    path: Path, model: PeerModel, arm: str, binding: dict
) -> tuple[dict, PeerModel]:
    stream = io.BytesIO()
    torch.save(
        dict(
            state_dict=model.state_dict(),
            binding=binding,
            rng_sha256=rng_hash(),
            model_state_sha256=state_hash(model),
        ),
        stream,
    )
    atomic_new(path, stream.getvalue())
    saved = torch.load(path, weights_only=True, map_location="cpu")
    # Reload must not consume the training/dropout RNG stream.
    rng, numpy_rng, python_rng = torch.get_rng_state(), np.random.get_state(), random.getstate()
    loaded = model_for(arm)
    torch.set_rng_state(rng)
    np.random.set_state(numpy_rng)
    random.setstate(python_rng)
    loaded.load_state_dict(saved["state_dict"])
    if (
        saved["binding"] != binding
        or state_hash(model) != state_hash(loaded)
        or saved["rng_sha256"] != rng_hash()
        or saved["model_state_sha256"] != state_hash(model)
    ):
        raise ValueError("P027_CHECKPOINT_RELOAD")
    return ref(path), loaded


def predict(model: PeerModel, view, arm: str, recipe: dict, binding: dict) -> pd.DataFrame:
    """Canonical full panels with one original-scale inverse and no protected role."""
    if view.split not in ("inner_train", "inner_validation", "refit", "development"):
        raise ValueError("P027_PROTECTED_BEFORE_EXPORT_IO")
    model.eval()
    pieces = []
    policy = LossPolicy("T2", scale=recipe["scale"])
    with torch.inference_mode():
        for positions in session_batches(len(view.source.rows), 42, 1, shuffle=False):
            x = view.origin_batch(positions)["x"]
            raw = model(torch.from_numpy(x))
            pieces.append(torch.stack((raw, policy.canonical(raw)), -1).reshape(-1, 2).numpy())
    values = np.concatenate(pieces)
    f = ordered_targets(view)
    f["raw_net_output"] = values[:, 0]
    f["pred_original_TG20"] = values[:, 1].astype(float)
    f["actual_TG20"] = f.TG20
    f["inverse_count"] = 1
    f["t2_scale"] = recipe["scale"]
    f["arm"], f["seed"], f["partition"] = arm, 42, view.split
    for k, v in sorted(binding.items()):
        f[k] = v
    if (
        len(f) != len(view.source.rows) * 20
        or f.session_date_et.ge("2026-01-01").any()
        or not np.isfinite(values).all()
    ):
        raise ValueError("P027_EXACT_FINITE_POPULATION")
    check_memory()
    return f


def epoch_pass(
    model: PeerModel,
    view,
    arm: str,
    recipe: dict,
    epoch: int,
    opt: torch.optim.AdamW | None,
    telemetry: Path,
    *,
    update: bool,
    authority: tuple[Path, Path, str] | None = None,
) -> dict:
    """Same T2 kernel and whole sessions; a dry backward can never call optimizer.step."""
    if update:
        if authority is None or opt is None:
            raise ValueError("P027_LIVE_AUTHORITY_REQUIRED")
        from .peer_screen_authority import ensure

        ensure(*authority)
    training = opt is not None
    model.train(training)
    initial = state_hash(model)
    policy = LossPolicy("T2", scale=recipe["scale"])
    losses, mse_values, pre, post, ids_seen = [], [], [], [], []
    start = time.monotonic()
    modules = {n: [] for n, _ in model.named_parameters()}
    for step, positions in enumerate(
        session_batches(len(view.sessions), 42, epoch, shuffle=training), 1
    ):
        batch = view.batch(positions)
        with torch.set_grad_enabled(training):
            raw_valid = model(batch.inputs[batch.origins])
            raw = torch.zeros_like(batch.targets)
            raw[batch.origins] = raw_valid.reshape(-1, 20)
            by_session = policy.objective(raw, batch.targets, batch.origins, stock_count=20)
            original = policy.canonical(raw)
            mse = ((original - batch.targets).square().mean(2) * batch.origins).sum(
                1
            ) / batch.origins.sum(1)
            if not bool(torch.isfinite(by_session).all()) or not bool(torch.isfinite(mse).all()):
                raise ValueError("P027_NONFINITE_LOSS")
            gradients = {}
            before = {}
            if opt is not None:
                opt.zero_grad(set_to_none=True)
                by_session.mean().backward()
                for name, p in model.named_parameters():
                    if p.grad is None or not bool(torch.isfinite(p.grad).all()):
                        raise ValueError("P027_FINITE_CONNECTED_GRADIENTS")
                    gradients[name] = float(p.grad.norm())
                    modules[name].append(gradients[name])
                pre.append(
                    float(
                        torch.nn.utils.clip_grad_norm_(
                            model.parameters(), 1.0, error_if_nonfinite=True
                        )
                    )
                )
                post.append(
                    math.sqrt(
                        sum(
                            float(p.grad.square().sum())
                            for p in model.parameters()
                            if p.grad is not None
                        )
                    )
                )
                if update:
                    before = {n: p.detach().clone() for n, p in model.named_parameters()}
                    opt.step()
                if any(not bool(torch.isfinite(p).all()) for p in model.parameters()):
                    raise ValueError("P027_NONFINITE_WEIGHT")
        change = (
            math.sqrt(
                sum(
                    float((p.detach() - before[n]).square().sum())
                    for n, p in model.named_parameters()
                )
            )
            if before
            else 0.0
        )
        losses += by_session.detach().tolist()
        mse_values += mse.detach().tolist()
        ids_seen += list(batch.ids)
        record = dict(
            epoch=epoch,
            role=view.split,
            batch=step,
            sessions=len(batch.ids),
            optimizer_step=update,
            backward=training,
            objective=float(by_session.detach().mean()),
            original_mse=float(mse.detach().mean()),
            preclip_norm=pre[-1] if training else None,
            postclip_norm=post[-1] if training else None,
            parameter_preclip=gradients,
            update_norm=change,
            weight_norm=math.sqrt(
                sum(float(p.detach().square().sum()) for p in model.parameters())
            ),
            lr=[g["lr"] for g in opt.param_groups] if opt else [],
            weight_decay=[g["weight_decay"] for g in opt.param_groups] if opt else [],
            model_state_sha256=state_hash(model),
            optimizer_state_sha256=optimizer_hash(model, opt) if opt else None,
            parameter_weight_norms={
                n: float(p.detach().norm()) for n, p in model.named_parameters()
            },
            raw_sd=float(raw_valid.detach().std(unbiased=False)),
            target_original_SD=float(batch.targets[batch.origins].detach().std(unbiased=False)),
            target_z_SD=float(
                torch.asinh(batch.targets[batch.origins] / recipe["scale"])
                .detach()
                .std(unbiased=False)
            ),
            prediction_positive_fraction=float(
                (policy.canonical(raw_valid.detach()) > 0).float().mean()
            ),
            target_positive_fraction=float((batch.targets[batch.origins] > 0).float().mean()),
        )
        with telemetry.open("a") as stream:
            stream.write(json.dumps(record, allow_nan=False) + "\n")
            stream.flush()
    if len(ids_seen) != len(view.sessions) or len(set(ids_seen)) != len(ids_seen):
        raise ValueError("P027_SESSION_CONSERVATION")
    if not update and state_hash(model) != initial:
        raise ValueError("P027_ZERO_STEP_CHANGED_WEIGHTS")
    check_memory()
    result: dict = dict(
        epoch=epoch,
        role=view.split,
        optimized_objective=float(np.mean(losses)),
        original_mse=float(np.mean(mse_values)),
        optimizer_steps=len(pre) if update else 0,
        backward_batches=len(pre),
        sessions=len(ids_seen),
        order_sha256=fingerprint(ids_seen),
        seconds=time.monotonic() - start,
        forward_state="online_pre_update_train_mode"
        if training
        else "fixed_checkpoint_dropout_OFF",
        nonfinite_count=0,
    )
    if pre:
        result.update(
            preclip=distribution(pre, "norm"),
            postclip=distribution(post, "norm"),
            parameter_preclip={k: distribution(v, "norm") for k, v in modules.items()},
            clipping_fraction=float(np.mean(np.array(pre) > 1)),
            clipped_count=sum(v > 1 for v in pre),
            clipping_denominator=len(pre),
        )
    return result
