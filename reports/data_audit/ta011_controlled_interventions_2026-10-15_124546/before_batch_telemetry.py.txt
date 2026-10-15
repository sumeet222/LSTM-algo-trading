"""Optional scalar batch observability; never clips, draws RNG or changes gradients."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import torch

from .neural_engine import SessionBatch

VERSION = "TA009_BATCH_OBSERVER_v1"


class BatchTelemetry:
    """Record the already-computed loss and single clip return after optimizer.step."""

    def __init__(self, path: Path, run_id: str, architecture: str, stage: str):
        if path.exists() or stage not in {"CALIBRATION", "REFIT"}:
            raise ValueError("NEW_STAGE_TELEMETRY_PATH_REQUIRED")
        self.path, self.run_id, self.architecture, self.stage = path, run_id, architecture, stage
        self.steps = 0

    def record(
        self,
        epoch: int,
        batch_index: int,
        batch: SessionBatch,
        loss: torch.Tensor,
        preclip_norm: float,
    ) -> None:
        """Detached summaries only, with exact PyTorch epsilon convention."""
        values = loss.detach().cpu().numpy()
        targets = batch.targets.detach()[batch.origins].cpu().numpy().reshape(-1)
        if (
            not np.isfinite(values).all()
            or not np.isfinite(targets).all()
            or not math.isfinite(preclip_norm)
        ):
            raise ValueError("NONFINITE_BATCH_OBSERVATION")
        multiplier = min(1.0, 1.0 / (preclip_norm + 1e-6))
        self.steps += 1
        row = {
            "version": VERSION,
            "stage": self.stage,
            "architecture": self.architecture,
            "seed": 42,
            "epoch": epoch,
            "batch_index": batch_index,
            "run_id": self.run_id,
            "number_sessions": len(batch.ids),
            "number_origins": int(batch.origins.sum()),
            "effective_weight_sum": 1.0,
            "batch_session_weighted_MSE": float(values.mean()),
            "preclip_global_grad_norm": preclip_norm,
            "clip_applied": multiplier < 1.0,
            "exceeds_cap_for_G6": preclip_norm > 1.0,
            "clip_multiplier": multiplier,
            "finite_flag": True,
            "optimizer_step_id": self.steps,
            "session_ids": "|".join(batch.ids),
            "target_abs_max": float(np.max(np.abs(targets))),
            "target_abs_p95": float(np.quantile(np.abs(targets), 0.95)),
            "target_abs_gt10": int(np.sum(np.abs(targets) > 10)),
            "target_abs_gt20": int(np.sum(np.abs(targets) > 20)),
            "largest_session_loss_share": float(values.max() / values.sum())
            if values.sum()
            else 0.0,
        }
        exists = self.path.exists()
        with self.path.open("a", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(row))
            if not exists:
                writer.writeheader()
            writer.writerow(row)
