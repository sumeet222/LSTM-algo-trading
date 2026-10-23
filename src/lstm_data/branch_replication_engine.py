"""P025 seeded three-head lifecycle, delegating the frozen E1/QR1 objective kernels."""

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
from torch import nn

from .branch_replication_spec import ARMS, SEED
from .config import atomic_new, fingerprint
from .dm_quantile_loss import outputs, terms
from .hf1m_ft16_source import ref
from .hf1m_training_data import TrainingView
from .hf1m_training_run import distribution
from .neural_engine import SharedLSTM, clip, seed_all, session_batches
from .neural_lifecycle import state_hash
from .objective_screen_loss import Objective, classes
from .objective_screen_source import ordered_targets


def peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == "darwin" else value * 1024


def check_memory() -> None:
    if peak_rss_bytes() > 2_000_000_000:
        raise ValueError("P025_RAM_LIMIT")


def optimizer_hash(model: SharedLSTM, opt: torch.optim.AdamW) -> str:
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


def model_for(arm: str, seed: int = SEED) -> SharedLSTM:
    """Exactly reproduce reference construction, changing only the registered RNG seed."""
    if arm not in ARMS:
        raise ValueError("P025_ARM")
    seed_all(seed)
    model = SharedLSTM()
    model.head = nn.Linear(32, 3)
    if sum(p.numel() for p in model.parameters()) != 6499:
        raise ValueError("P025_PARAMETER_COUNT")
    return model


def contributions(
    raw: torch.Tensor, y: torch.Tensor, mask: torch.Tensor, arm: str, recipe: dict
) -> dict:
    """No replacement formulas: use the original tensor kernels verbatim."""
    if arm == "E1":
        result = Objective("E1", recipe).contributions(raw, y, mask)
        return dict(
            session_loss=result["total"].sum(dim=(1, 2)),
            components=result["raw"][..., None],
            **result,
        )
    if arm != "QR1":
        raise ValueError("P025_ARM")
    return terms(raw, y, mask, "QR1", recipe["scale"])


def save_checkpoint(
    path: Path, model: SharedLSTM, arm: str, binding: dict
) -> tuple[dict, SharedLSTM]:
    stream = io.BytesIO()
    torch.save(dict(state_dict=model.state_dict(), binding=binding), stream)
    atomic_new(path, stream.getvalue())
    saved = torch.load(path, weights_only=True, map_location="cpu")
    # Reload must not consume the training/dropout RNG stream.
    rng, numpy_rng, python_rng = torch.get_rng_state(), np.random.get_state(), random.getstate()
    loaded = model_for(arm)
    torch.set_rng_state(rng)
    np.random.set_state(numpy_rng)
    random.setstate(python_rng)
    loaded.load_state_dict(saved["state_dict"])
    if saved["binding"] != binding or state_hash(model) != state_hash(loaded):
        raise ValueError("P025_CHECKPOINT_RELOAD")
    return ref(path), loaded


def predict(
    model: SharedLSTM, view: TrainingView, arm: str, recipe: dict, binding: dict
) -> pd.DataFrame:
    """Full allowed population; retain original64 targets and genuine raw outputs."""
    model.eval()
    chunks = []
    with torch.inference_mode():
        for positions in session_batches(len(view.source.rows), SEED, 1, shuffle=False):
            x = view.origin_batch(positions)["x"]
            chunks.append(model(torch.from_numpy(x.reshape(-1, 48, 16))))
    raw = torch.cat(chunks)
    check_memory()
    f = ordered_targets(view)
    for i in range(3):
        f[f"raw_{i}"] = raw[:, i].numpy()
    if arm == "E1":
        p = raw.softmax(dim=-1).numpy()
        for k, name in enumerate(("NEG", "NORMAL", "POS")):
            f["logit_" + name] = raw[:, k].numpy()
            f["p_" + name] = p[:, k]
        f["label"] = classes(f.TG20.to_numpy(), recipe["q95_abs_y"])
        f["ANY_score"] = p[:, 0] + p[:, 2]
        f["signed_event_score"] = p[:, 2] - p[:, 0]
    else:
        for key, value in outputs(raw, "QR1", recipe["scale"]).items():
            array = value.numpy()
            if array.ndim == 2:
                for j, tau in enumerate(("05", "50", "95")):
                    f[key + "_" + tau] = array[:, j]
            else:
                f[key] = array
        f["inverse_count"] = 1
    f["arm"], f["seed"], f["partition"] = arm, SEED, view.split
    for key, value in sorted(binding.items()):
        f[key] = value
    if f.session_date_et.ge("2026-01-01").any():
        raise ValueError("P025_PROTECTED_EXPORT")
    return f


def epoch_pass(
    model: SharedLSTM,
    view: TrainingView,
    arm: str,
    recipe: dict,
    epoch: int,
    opt: torch.optim.AdamW | None,
    telemetry: Path,
    *,
    update: bool,
    authority: tuple[Path, Path, str] | None = None,
) -> dict:
    """Whole-session training/evaluation; rehearsal backpropagates but never calls step."""
    if update:
        if authority is None or opt is None:
            raise ValueError("P025_LIVE_AUTHORITY_REQUIRED_BEFORE_UPDATES")
        from .branch_replication_authority import ensure

        ensure(*authority)
    training = opt is not None
    model.train(training)
    initial = state_hash(model)
    start = time.monotonic()
    losses, auxiliary, component_rows, pre, post, ids_seen = [], [], [], [], [], []
    module_norms: dict[str, list[float]] = {"lstm_l0": [], "head": []}
    for step, positions in enumerate(
        session_batches(len(view.sessions), SEED, epoch, shuffle=training), 1
    ):
        batch = view.batch(positions)
        with torch.set_grad_enabled(training):
            raw_valid = model(batch.inputs[batch.origins].reshape(-1, 48, 16))
            raw = torch.zeros((*batch.targets.shape, 3), dtype=raw_valid.dtype)
            raw[batch.origins] = raw_valid.reshape(-1, 20, 3)
            terms_ = contributions(raw, batch.targets, batch.origins, arm, recipe)
            by_session = terms_["session_loss"]
            if not bool(torch.isfinite(by_session).all()):
                raise ValueError("P025_NONFINITE_OBJECTIVE")
            if arm == "E1":
                ordinary = terms_["ordinary_weight"]
                auxiliary.extend((terms_["raw"] * ordinary).sum(dim=(1, 2)).detach().tolist())
            else:
                ordinary = batch.origins[..., None, None] / (
                    batch.origins.sum(dim=1)[:, None, None, None] * 20
                )
                component_rows.extend(
                    (terms_["components"] * ordinary).sum(dim=(1, 2)).detach().tolist()
                )
            before = {}
            module = {}
            if opt is not None:
                opt.zero_grad(set_to_none=True)
                by_session.mean().backward()
                for name in module_norms:
                    prefix = "lstm." if name == "lstm_l0" else "head."
                    module[name] = math.sqrt(
                        sum(
                            float(p.grad.square().sum())
                            for n, p in model.named_parameters()
                            if n.startswith(prefix) and p.grad is not None
                        )
                    )
                    module_norms[name].append(module[name])
                pre.append(clip(model))
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
                    raise ValueError("P025_NONFINITE_WEIGHTS")
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
            weight = math.sqrt(sum(float(p.detach().square().sum()) for p in model.parameters()))
        losses.extend(by_session.detach().tolist())
        ids_seen.extend(batch.ids)
        record = dict(
            epoch=epoch,
            role=view.split,
            batch=step,
            sessions=len(batch.ids),
            objective=float(by_session.detach().mean()),
            optimizer_step=update,
            backward=training,
            preclip_norm=pre[-1] if training else None,
            postclip_norm=post[-1] if training else None,
            module_preclip=module,
            update_norm=change,
            weight_norm=weight,
            lr=[g["lr"] for g in opt.param_groups] if opt else [],
            weight_decay=[g["weight_decay"] for g in opt.param_groups] if opt else [],
            model_state_sha256=state_hash(model),
            optimizer_state_sha256=optimizer_hash(model, opt) if opt else None,
        )
        with telemetry.open("a") as stream:
            stream.write(json.dumps(record, allow_nan=False) + "\n")
            stream.flush()
    if len(ids_seen) != len(view.sessions) or len(set(ids_seen)) != len(ids_seen):
        raise ValueError("P025_EXACT_SESSION_EPOCH")
    if not update and state_hash(model) != initial:
        raise ValueError("P025_ZERO_STEP_WEIGHTS_CHANGED")
    check_memory()
    result: dict = dict(
        epoch=epoch,
        role=view.split,
        optimized_objective=float(np.mean(losses)),
        ordinary_CE=float(np.mean(auxiliary)) if auxiliary else None,
        component_means=np.mean(component_rows, axis=0).tolist() if component_rows else None,
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
            module_preclip={k: distribution(v, "norm") for k, v in module_norms.items()},
            clipped_count=sum(x > 1 for x in pre),
            clipping_denominator=len(pre),
            clipping_fraction=float(np.mean(np.array(pre) > 1)),
        )
    return result
