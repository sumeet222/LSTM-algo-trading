"""Immutable tensor-safe checkpoints and an isolated synthetic pair registry."""

from __future__ import annotations

import io
import json
import math
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import torch

from .config import atomic_new, digest, fingerprint, now, write_json
from .neural_engine import SEEDS
from .neural_models import (
    NeuralModel,
    architecture_for_information,
    architecture_of,
    create_model,
    model_version,
)

MODE = "ENGINEERING_SYNTHETIC_ONLY"


@dataclass(frozen=True)
class PairIdentity:
    """Every future fit-affecting version participates in the unique pair key."""

    experiment: str
    universe: str
    information: str
    target: str
    calendar_split_cutoff: str
    source_features_data: str
    preprocess: str
    model_optimizer_selection: str
    code: str
    seed: int = 42
    track: str = "A"
    mode: str = MODE

    def __post_init__(self) -> None:
        if (
            self.mode != MODE
            or self.track != "A"
            or self.seed not in SEEDS
            or not self.experiment.startswith("SYN:")
            or any(
                not isinstance(value, str) or not value
                for value in (
                    self.universe,
                    self.information,
                    self.target,
                    self.calendar_split_cutoff,
                    self.source_features_data,
                    self.preprocess,
                    self.model_optimizer_selection,
                    self.code,
                )
            )
        ):
            raise ValueError("P4_3_BLOCKED_SYNTHETIC_PAIR_IDENTITY_REQUIRED")

    @property
    def key(self) -> str:
        return fingerprint(vars(self))


def save_checkpoint(
    path: Path,
    model: NeuralModel,
    pair: PairIdentity,
    stage: str,
    epoch: int,
    *,
    optimizer: torch.optim.AdamW | None = None,
    trace: tuple[dict, ...] = (),
    fit_binding: str | None = None,
) -> dict:
    """Boundary checkpoints include full optimizer/RNG; final weights are immutable."""
    if architecture_of(model) in {"FULLPEER", "SP3"}:
        raise ValueError("P4_11_OPERATOR_ARTIFACT_ONLY_NO_REFIT_AUTHORITY")
    if stage not in {
        "CALIBRATION_SELECTED",
        "REFIT_FINAL",
        "CALIBRATION_BOUNDARY",
        "REFIT_BOUNDARY",
    }:
        raise ValueError("EXPLICIT_CHECKPOINT_STAGE_REQUIRED")
    if (
        type(epoch) is not int
        or not 1 <= epoch <= 60
        or architecture_of(model) != architecture_for_information(pair.information)
        or any(p.dtype != torch.float32 or p.device.type != "cpu" for p in model.parameters())
    ):
        raise ValueError("FROZEN_NEURAL_CHECKPOINT_REQUIRED")
    if stage.endswith("BOUNDARY") and optimizer is None:
        raise ValueError("FULL_EPOCH_BOUNDARY_STATE_REQUIRED")
    body = {
        "schema": 1,
        "pair": pair.key,
        "identity": vars(pair),
        "model_version": model_version(model),
        "stage": stage,
        "epoch": epoch,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict() if optimizer is not None else None,
        "torch_rng": torch.get_rng_state(),
        "trace": list(trace),
        "fit_binding": fit_binding or pair.preprocess,
    }
    buffer = io.BytesIO()
    torch.save(body, buffer)
    atomic_new(path, buffer.getvalue())
    manifest = {
        "schema": 1,
        "path": path.name,
        "sha256": digest(path),
        "pair": pair.key,
        "stage": stage,
        "epoch": epoch,
        "bytes": path.stat().st_size,
        "prediction_authoritative": stage == "REFIT_FINAL",
        "fit_binding": fit_binding or pair.preprocess,
    }
    write_json(path.with_suffix(".manifest.json"), manifest)
    return manifest


def load_checkpoint(
    path: Path,
    model: NeuralModel,
    pair: PairIdentity,
    stage: str,
    *,
    optimizer: torch.optim.AdamW | None = None,
    fit_binding: str | None = None,
) -> tuple[int, tuple[dict, ...]]:
    """Reject corruption/stale identity before safe tensor deserialization or reuse."""
    if architecture_of(model) in {"FULLPEER", "SP3"}:
        raise ValueError("P4_11_OPERATOR_ARTIFACT_ONLY_NO_REFIT_AUTHORITY")
    manifest = json.loads(path.with_suffix(".manifest.json").read_text())
    if (
        manifest.get("schema") != 1
        or manifest.get("path") != path.name
        or manifest.get("sha256") != digest(path)
        or manifest.get("pair") != pair.key
        or manifest.get("stage") != stage
        or manifest.get("prediction_authoritative") != (stage == "REFIT_FINAL")
        or manifest.get("fit_binding") != (fit_binding or pair.preprocess)
    ):
        raise ValueError("CHECKPOINT_HASH_IDENTITY_STAGE_REQUIRED")
    body = torch.load(path, map_location="cpu", weights_only=True)
    if (
        not isinstance(body, dict)
        or body.get("schema") != 1
        or body.get("pair") != pair.key
        or body.get("identity") != vars(pair)
        or body.get("model_version") != model_version(model)
        or architecture_of(model) != architecture_for_information(pair.information)
        or body.get("stage") != stage
        or body.get("epoch") != manifest.get("epoch")
        or body.get("fit_binding") != manifest.get("fit_binding")
        or type(body.get("epoch")) is not int
        or not 1 <= body["epoch"] <= 60
        or not isinstance(body.get("model"), dict)
        or not isinstance(body.get("trace"), list)
    ):
        raise ValueError("PARSED_CHECKPOINT_SCHEMA_REQUIRED")
    state = body["model"]
    expected = model.state_dict()
    if set(state) != set(expected) or any(
        not isinstance(state[name], torch.Tensor)
        or state[name].shape != tensor.shape
        or state[name].dtype != tensor.dtype
        or not bool(torch.isfinite(state[name]).all())
        for name, tensor in expected.items()
    ):
        raise ValueError("CHECKPOINT_EXACT_FINITE_TENSOR_SCHEMA_REQUIRED")
    model.load_state_dict(state, strict=True)
    if optimizer is not None:
        if not stage.endswith("BOUNDARY") or not isinstance(body.get("optimizer"), dict):
            raise ValueError("RESUME_FULL_BOUNDARY_ONLY")
        optimizer.load_state_dict(body["optimizer"])
        if len(optimizer.param_groups) != 2 or any(
            group["lr"] != 0.001
            or group["betas"] != (0.9, 0.999)
            or group["eps"] != 1e-8
            or group["amsgrad"]
            or group["weight_decay"] != (0.01 if i == 0 else 0)
            for i, group in enumerate(optimizer.param_groups)
        ):
            raise ValueError("RESUME_FROZEN_OPTIMIZER_REQUIRED")
        for state in optimizer.state.values():
            if any(
                isinstance(value, torch.Tensor) and not bool(torch.isfinite(value).all())
                for value in state.values()
            ):
                raise ValueError("RESUME_FINITE_OPTIMIZER_REQUIRED")
        rng = body.get("torch_rng")
        if not isinstance(rng, torch.Tensor) or rng.dtype != torch.uint8 or rng.ndim != 1:
            raise ValueError("RESUME_RNG_STATE_REQUIRED")
        torch.set_rng_state(rng)
    model.eval()
    return body["epoch"], tuple(body["trace"])


@contextmanager
def _lock(path: Path) -> Iterator[None]:
    """Exclusive same-machine reservation; a stale lock fails closed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_suffix(".lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("PAIR_REGISTRY_LOCKED") from None
    try:
        os.close(descriptor)
        yield
    finally:
        lock.unlink()


class PairRegistry:
    """Synthetic namespace only; mock 40-pair/24-hour guards never write real ledger."""

    transitions = {
        "RESERVED": {"CALIBRATING", "FAILED"},
        "CALIBRATING": {"CALIBRATED", "FAILED"},
        "CALIBRATED": {"REFITTING", "FAILED"},
        "REFITTING": {"COMPLETE", "FAILED"},
        "COMPLETE": set(),
        "FAILED": set(),
    }

    def __init__(self, path: Path, namespace: str = MODE) -> None:
        if namespace != MODE or "audit" in path.parts or path.name == "track_a_events.jsonl":
            raise ValueError("AUTHORITATIVE_SCIENTIFIC_REGISTRY_WRITE_FORBIDDEN")
        self.path = path

    def _read(self) -> dict:
        if not self.path.exists():
            return {"schema": 1, "namespace": MODE, "entries": {}}
        data = json.loads(self.path.read_text())
        if data.get("schema") != 1 or data.get("namespace") != MODE:
            raise ValueError("PAIR_REGISTRY_SCHEMA_REQUIRED")
        for row in data["entries"].values():
            if (
                row["state"] not in self.transitions
                or not math.isfinite(row["seconds"])
                or row["seconds"] < 0
            ):
                raise ValueError("PAIR_REGISTRY_STATE_REQUIRED")
        return data

    def _publish(self, data: dict) -> None:
        # Replace only this owned mutable synthetic registry, under its exclusive lock.
        temporary = self.path.with_suffix(".pending")
        atomic_new(temporary, (json.dumps(data, sort_keys=True, indent=2) + "\n").encode())
        os.replace(temporary, self.path)

    def reserve(self, pair: PairIdentity, seconds: float = 60.0) -> bool:
        if not math.isfinite(seconds) or seconds <= 0:
            raise ValueError("BOUNDED_FITTING_TIME_REQUIRED")
        with _lock(self.path):
            data = self._read()
            if pair.key in data["entries"]:
                row = data["entries"][pair.key]
                if row["state"] == "COMPLETE":
                    if digest(Path(row["checkpoint"])) != row["checkpoint_sha"]:
                        raise ValueError("COMPLETE_CHECKPOINT_CORRUPTED")
                    path = Path(row["checkpoint"])
                    manifest = json.loads(path.with_suffix(".manifest.json").read_text())
                    load_checkpoint(
                        path,
                        create_model(architecture_for_information(pair.information)),
                        pair,
                        "REFIT_FINAL",
                        fit_binding=manifest["fit_binding"],
                    )
                    return False
                raise ValueError("PAIR_ALREADY_RESERVED_OR_FAILED")
            if len(data["entries"]) >= 40:
                raise ValueError("FORTY_PAIR_CEILING")
            if sum(row["seconds"] for row in data["entries"].values()) + seconds > 24 * 3600:
                raise ValueError("PRELIMINARY_TRAINING_TIME_ENVELOPE")
            data["entries"][pair.key] = {
                "identity": vars(pair),
                "state": "RESERVED",
                "seconds": seconds,
                "history": [{"state": "RESERVED", "time": now()}],
            }
            self._publish(data)
        return True

    def transition(
        self,
        pair: PairIdentity,
        state: str,
        *,
        checkpoint: Path | None = None,
        seconds: float | None = None,
    ) -> None:
        with _lock(self.path):
            data = self._read()
            if pair.key not in data["entries"]:
                raise ValueError("RESERVED_PAIR_REQUIRED")
            row = data["entries"][pair.key]
            if state not in self.transitions[row["state"]]:
                raise ValueError("INVALID_PAIR_LIFECYCLE_TRANSITION")
            if seconds is not None:
                if not math.isfinite(seconds) or seconds < 0:
                    raise ValueError("FINITE_ACTUAL_FITTING_TIME_REQUIRED")
                row["seconds"] = seconds
            if state == "COMPLETE":
                if checkpoint is None:
                    raise ValueError("FINAL_REFIT_CHECKPOINT_REQUIRED")
                manifest = json.loads(checkpoint.with_suffix(".manifest.json").read_text())
                load_checkpoint(
                    checkpoint,
                    create_model(architecture_for_information(pair.information)),
                    pair,
                    "REFIT_FINAL",
                    fit_binding=manifest["fit_binding"],
                )
                row.update(checkpoint=str(checkpoint), checkpoint_sha=digest(checkpoint))
            row["state"] = state
            row["history"].append({"state": state, "time": now(), "seconds": row["seconds"]})
            self._publish(data)
