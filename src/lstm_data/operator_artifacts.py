"""Untrained P4.11 operator artifacts, deliberately outside pair/forecast authority."""

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import Tensor

from .config import atomic_new, digest, write_json
from .ft0_transforms import identity
from .fullpeer import (
    FULLPEER,
    SP3,
    OperatorBatch,
    OperatorBinding,
    OperatorInput,
    operator_code_identity,
    require_mode,
)
from .neural_engine import batch_prediction
from .neural_models import NeuralModel, architecture_of, create_model, model_version
from .p3_domain import MODE
from .spatial_operator import SpatialLSTM

STAGE = "ENGINEERING_UNTRAINED_OR_OPERATOR_TEST"


@dataclass(frozen=True)
class BoundOperator:
    """Only a computational score tensor; never a P3 authoritative forecast or fitted pair."""

    model: NeuralModel
    binding: OperatorBinding

    def validate(self) -> None:
        require_mode(self.binding.mode)
        if (
            architecture_of(self.model) not in (FULLPEER, SP3)
            or self.binding.code != operator_code_identity()
            or (
                isinstance(self.model, SpatialLSTM) and self.model.universe != self.binding.universe
            )
            or any(
                p.dtype != torch.float32
                or p.device.type != "cpu"
                or not bool(torch.isfinite(p).all())
                for p in self.model.parameters()
            )
        ):
            raise ValueError("EXACT_BOUND_OPERATOR_REQUIRED")

    @property
    def operator_id(self) -> str:
        self.validate()
        return identity(
            [
                STAGE,
                self.binding.binding_id,
                model_version(self.model),
                [(n, list(p.shape)) for n, p in self.model.named_parameters()],
            ]
        )

    def scores(self, inputs: OperatorInput, *, mode: str = MODE) -> Tensor:
        require_mode(mode)
        self.validate()
        inputs.validate()
        if inputs.binding != self.binding or inputs.architecture != architecture_of(self.model):
            raise ValueError("OPERATOR_SOURCE_ORDER_FIT_ARCHITECTURE_MISMATCH")
        return self.model(inputs.values)

    def batch_scores(self, batch: OperatorBatch, *, mode: str = MODE) -> Tensor:
        require_mode(mode)
        self.validate()
        batch.validate()
        if batch.binding != self.binding or batch.architecture != architecture_of(self.model):
            raise ValueError("OPERATOR_SOURCE_ORDER_FIT_ARCHITECTURE_MISMATCH")
        return batch_prediction(self.model, batch.batch)


def save_operator(path: Path, bound: BoundOperator, *, mode: str = MODE) -> dict:
    """Atomic publication without optimizer, epoch, fit reservation or forecast authority."""
    require_mode(mode)
    bound.validate()
    body = {
        "schema": 1,
        "stage": STAGE,
        "mode": MODE,
        "operator": bound.operator_id,
        "architecture": architecture_of(bound.model),
        "binding": bound.binding.binding_id,
        "code": operator_code_identity(),
        "model": bound.model.state_dict(),
    }
    buffer = io.BytesIO()
    torch.save(body, buffer)
    atomic_new(path, buffer.getvalue())
    manifest = {k: v for k, v in body.items() if k != "model"}
    manifest.update(
        path=path.name,
        sha256=digest(path),
        prediction_authoritative=False,
        bytes=path.stat().st_size,
    )
    write_json(path.with_suffix(".manifest.json"), manifest)
    return manifest


def load_operator(
    path: Path, binding: OperatorBinding, architecture: str, *, mode: str = MODE
) -> BoundOperator:
    """Reject mismatched source/order/code before any tensor deserialization."""
    require_mode(mode)
    if architecture not in (FULLPEER, SP3):
        raise ValueError("P4_11_OPERATOR_ARCHITECTURE_REQUIRED")
    bound = BoundOperator(create_model(architecture, universe=binding.universe), binding)
    bound.validate()
    manifest = json.loads(path.with_suffix(".manifest.json").read_text())
    expected = {
        "schema": 1,
        "stage": STAGE,
        "mode": MODE,
        "operator": bound.operator_id,
        "architecture": architecture,
        "binding": binding.binding_id,
        "code": operator_code_identity(),
        "prediction_authoritative": False,
        "path": path.name,
        "sha256": digest(path),
        "bytes": path.stat().st_size,
    }
    if manifest != expected:
        raise ValueError("OPERATOR_ARTIFACT_IDENTITY_HASH_STAGE_REQUIRED")
    body = torch.load(path, map_location="cpu", weights_only=True)
    if not isinstance(body, dict) or any(
        body.get(k) != v
        for k, v in expected.items()
        if k not in {"path", "sha256", "bytes", "prediction_authoritative"}
    ):
        raise ValueError("OPERATOR_ARTIFACT_SCHEMA_REQUIRED")
    state = body.get("model")
    template = bound.model.state_dict()
    if (
        not isinstance(state, dict)
        or set(state) != set(template)
        or any(
            not isinstance(state[n], Tensor)
            or state[n].shape != t.shape
            or state[n].dtype != t.dtype
            or not bool(torch.isfinite(state[n]).all())
            for n, t in template.items()
        )
    ):
        raise ValueError("EXACT_FINITE_OPERATOR_TENSOR_SCHEMA_REQUIRED")
    bound.model.load_state_dict(state, strict=True)
    bound.model.eval()
    return bound
