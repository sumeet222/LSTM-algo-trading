"""Indexed genuine conditional TM0 inputs, reusing the immutable Package004 store."""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass

import numpy as np
import pandas as pd
import torch
from torch import Tensor

from .baseline_ridge import windows
from .config import fingerprint
from .ft0_transforms import identity
from .labels import FitWindow
from .neural_data import IndexedOrigin
from .neural_engine import SessionBatch
from .pretraining_policy import CANDIDATE
from .pretraining_source import BARRIER
from .pretraining_store import load_tables, read_preparation
from .pretraining_tables import BaseTables
from .pretraining_transforms import CandidateView
from .real_bridge_authority import BridgeReview


def tensor_hash(values: Tensor) -> str:
    return hashlib.sha256(values.detach().cpu().numpy().tobytes()).hexdigest()


def supervised_status(
    base: BaseTables,
    day: str,
    origin: int,
    window: FitWindow,
    preparation_stop: pd.Timestamp,
    *,
    asof: bool,
) -> str:
    """Future outcome validity gates supervised samples, never forecast eligibility."""
    panel = base.panels[day, origin]
    if not window.start <= panel.cutoff < window.stop:
        return "OUTSIDE_WINDOW"
    if panel.cutoff >= BARRIER or window.stop > BARRIER:
        raise ValueError("CONFIRMATION_NUMERIC_ACCESS_FORBIDDEN")
    if (
        not panel.label_valid
        or panel.maturity is None
        or pd.isna(panel.maturity)
        or panel.maturity >= window.stop
        or panel.maturity > window.fitted_at
    ):
        return "LABEL_INVALID_UNMATURED_OR_BOUNDARY_PURGED"
    positions = base.origin_steps[day, origin]
    if (
        len(positions) != 48
        or tuple(positions) != tuple(range(positions[-1] - 47, positions[-1] + 1))
        or base.history.calendar.steps[positions[-1]].end != panel.cutoff
    ):
        raise ValueError("EXACT_48_SCHEDULED_FULL_HOURS_REQUIRED")
    steps = tuple(base.history.calendar.steps[p] for p in positions)
    if any(s.slot not in range(1, 7) or s.end > panel.cutoff for s in steps):
        raise ValueError("NO_STUB_OR_FUTURE_STEP")
    if (
        panel.issuance - panel.cutoff != pd.Timedelta(minutes=2)
        or panel.entry_event - panel.cutoff != pd.Timedelta(minutes=3)
        or panel.exit_event - panel.entry_event != pd.Timedelta(minutes=240)
        or panel.maturity < panel.exit_event
    ):
        raise ValueError("HOURLY_PROXY_EVENT_AND_MATURITY_CLOCK_REQUIRED")
    if asof and any(s.end < preparation_stop for s in steps):
        return "SCALER_NOT_AVAILABLE_AT_EVERY_HISTORICAL_STEP"
    return "ELIGIBLE"


@dataclass(frozen=True)
class RealInputView:
    """Transient unique step table plus immutable indices; not a synthetic NeuralView."""

    review_binding: str
    preparation_id: str
    window: FitWindow
    values: Tensor
    rows: tuple[IndexedOrigin, ...]
    sessions: tuple[str, ...]
    content_hash: str
    metadata_hash: str
    excluded: tuple[tuple[tuple[str, int], str], ...]

    def verify(self) -> None:
        if (
            self.values.ndim != 2
            or self.values.shape[1] != 16
            or self.values.dtype != torch.float32
            or self.values.device.type != "cpu"
            or not bool(torch.isfinite(self.values).all())
            or tensor_hash(self.values) != self.content_hash
            or identity(
                [
                    self.review_binding,
                    self.preparation_id,
                    self.window,
                    self.rows,
                    self.sessions,
                    self.excluded,
                ]
            )
            != self.metadata_hash
            or self.sessions != tuple(sorted({r.session for r in self.rows}))
            or len({(r.session, r.origin) for r in self.rows}) != len(self.rows)
        ):
            raise ValueError("REAL_INPUT_CONTENT_OR_IDENTITY_CHANGED")

    @property
    def version(self) -> str:
        return "CONDITIONAL_REAL_TM0:" + fingerprint([self.content_hash, self.metadata_hash])

    def batch(self, positions: tuple[int, ...]) -> SessionBatch:
        self.verify()
        if (
            not positions
            or len(set(positions)) != len(positions)
            or any(type(p) is not int or not 0 <= p < len(self.sessions) for p in positions)
        ):
            raise ValueError("UNIQUE_VALID_SESSION_POSITIONS_REQUIRED")
        ids = tuple(self.sessions[p] for p in positions)
        x = torch.zeros(len(ids), 2, 5, 48, 16, dtype=torch.float32)
        y = torch.zeros(len(ids), 2, 5, dtype=torch.float32)
        mask = torch.zeros(len(ids), 2, dtype=torch.bool)
        for j, day in enumerate(ids):
            for row in self.rows:
                if row.session == day:
                    x[j, row.origin - 1] = self.values[torch.tensor(row.indices)]
                    y[j, row.origin - 1] = torch.tensor(row.targets, dtype=torch.float32)
                    mask[j, row.origin - 1] = True
        batch = SessionBatch(ids, x, y, mask)
        batch.validate()
        return batch

    def summary(self) -> dict:
        return {
            "view_id": self.version,
            "origins": len(self.rows),
            "sessions": len(self.sessions),
            "per_origin": dict(Counter(str(r.origin) for r in self.rows)),
            "preparation_id": self.preparation_id,
            "unique_feature_rows": len(self.values),
            "excluded": dict(Counter(reason for _, reason in self.excluded)),
            "tensor_bytes": self.values.nelement() * self.values.element_size(),
            "dtype": "float32",
            "designation": "ASSUMPTION_CONDITIONAL_REAL_NOT_PRODUCTION",
        }


def check_bridge_window(window: FitWindow) -> None:
    """Only frozen first-pair windows and two nonconfirmation review folds."""
    known = {
        w.window_id: w
        for w in (
            *windows("WF1", pd.Timestamp("2023-07-01T04:00Z")),
            *windows("WF2", pd.Timestamp("2024-01-01T05:00Z")),
        )
    }
    for stage, start, stop in (
        ("WF1", "2023-07-01T04:00Z", "2024-01-01T05:00Z"),
        ("WF2", "2024-01-01T05:00Z", "2024-07-01T04:00Z"),
    ):
        key = "BRIDGE_REVIEW:" + stage
        known[key] = FitWindow(
            key, pd.Timestamp(start), pd.Timestamp(stop), pd.Timestamp(stop), "INNER_VALIDATION"
        )
    if known.get(window.window_id) != window:
        raise ValueError("EXACT_FROZEN_BRIDGE_WINDOW_REQUIRED")


def build_view(
    review: BridgeReview, candidate: CandidateView, window: FitWindow, *, asof: bool = False
) -> RealInputView:
    review.ensure()
    candidate.preparation.ensure(candidate.base)
    prep = candidate.preparation
    check_bridge_window(window)
    if (
        prep.window.stop > window.stop
        or window.stop > BARRIER
        or (asof and prep.window.stop > window.start)
        or (window.phase == "INNER_VALIDATION" and not asof)
    ):
        raise ValueError("MATCHED_TRAIN_PREFIX_STAGE_AND_CUTOFF_REQUIRED")
    positions: dict[tuple[str, int, int], int] = {}
    values: list[tuple[float, ...]] = []
    rows, rejected = [], []
    for (day, origin), panel in sorted(candidate.base.panels.items()):
        reason = supervised_status(candidate.base, day, origin, window, prep.window.stop, asof=asof)
        if reason == "OUTSIDE_WINDOW":
            continue
        if reason == "ELIGIBLE" and not candidate.input_status(day, origin)[0]:
            reason = "FT0_OR_SOURCE_INVALID"
        if reason != "ELIGIBLE":
            rejected.append(((day, origin), reason))
            continue
        indices = []
        for symbol in CANDIDATE:
            seq = []
            for pos in candidate.base.origin_steps[day, origin]:
                key = symbol, pos, origin  # M2 is origin-specific, unlike the other 15 channels.
                value = candidate.row(symbol, pos, origin)
                if value is None:
                    raise ValueError("COMPLETE_FIVE_STOCK_FT0_REQUIRED")
                if key not in positions:
                    positions[key] = len(values)
                    values.append(value)
                seq.append(positions[key])
            indices.append(tuple(seq))
        _, y = candidate.window(day, origin)
        rows.append(IndexedOrigin(day, origin, tuple(indices), tuple(float(v) for v in y)))
    tensor = torch.tensor(np.asarray(values, dtype=np.float32)).reshape(-1, 16)
    sessions = tuple(sorted({r.session for r in rows}))
    metadata = identity(
        [review.binding, prep.preparation_id, window, tuple(rows), sessions, tuple(rejected)]
    )
    view = RealInputView(
        review.binding,
        prep.preparation_id,
        window,
        tensor,
        tuple(rows),
        sessions,
        tensor_hash(tensor),
        metadata,
        tuple(rejected),
    )
    view.verify()
    return view


def load_inputs(
    review: BridgeReview,
    keys: tuple[str, ...] = ("WF1_INNER_TRAIN", "WF1_REFIT", "WF2_REFIT"),
) -> tuple[BaseTables, dict[str, CandidateView]]:
    review.ensure()
    if (
        not keys
        or len(set(keys)) != len(keys)
        or not set(keys) <= {"WF1_INNER_TRAIN", "WF1_REFIT", "WF2_REFIT"}
    ):
        raise ValueError("EXACT_NONCONFIRMATION_PREFIX_KEYS_REQUIRED")
    base = load_tables(review.preparation_authority, review.manifest["canonical_store"])
    return base, {
        key: CandidateView(base, read_preparation(review.root, ref))
        for key, ref in review.manifest["preparations"].items()
        if key in keys
    }


def first_pair_views(
    review: BridgeReview, candidates: dict[str, CandidateView]
) -> dict[str, RealInputView]:
    """Use exact repository windows; never fit or modify existing preprocessing."""
    inner, tail, full = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))
    return {
        "inner": build_view(review, candidates["WF1_INNER_TRAIN"], inner),
        "validation": build_view(review, candidates["WF1_INNER_TRAIN"], tail, asof=True),
        "refit": build_view(review, candidates["WF1_REFIT"], full),
    }
