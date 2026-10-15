"""Candidate-only indexed stock/market/peer joins; no fitting or dense store."""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass, field

import pandas as pd
import torch

from .ft0_transforms import identity
from .labels import FitWindow
from .market_features import MarketMeasures
from .neural_engine import SessionBatch
from .peer_inputs import peer_summaries
from .pretraining_market import conditional_vector
from .pretraining_policy import verify_ref
from .pretraining_source import BARRIER
from .pretraining_tables import BaseTables
from .pretraining_transforms import CandidateView
from .real_bridge_authority import BridgeReview
from .real_bridge_data import RealInputView, build_view, load_inputs, tensor_hash


@dataclass(frozen=True)
class ConditionedView:
    """One stock view plus a unique market-time table; joins exist per batch only."""

    stock: RealInputView
    market: torch.Tensor
    market_indices: tuple[tuple[tuple[str, int], tuple[int, ...]], ...]
    market_hash: str
    recipe_id: str
    channels: int

    @property
    def rows(self):
        return self.stock.rows

    @property
    def sessions(self):
        return self.stock.sessions

    @property
    def preparation_id(self) -> str:
        return identity([self.stock.preparation_id, self.recipe_id, self.channels])

    @property
    def version(self) -> str:
        return identity(
            [
                "CONDITIONAL_REAL_JOIN_V1",
                self.stock.version,
                self.market_hash,
                self.market_indices,
                self.recipe_id,
                self.channels,
            ]
        )

    def verify(self) -> None:
        self.stock.verify()
        if (
            self.channels not in (21, 23)
            or self.market.ndim != 2
            or self.market.shape[1] != 5
            or self.market.dtype != torch.float32
            or self.market.device.type != "cpu"
            or not torch.isfinite(self.market).all()
            or tensor_hash(self.market) != self.market_hash
            or tuple(k for k, _ in self.market_indices)
            != tuple((r.session, r.origin) for r in self.rows)
        ):
            raise ValueError("BOUND_FINITE_REAL_MARKET_JOIN_REQUIRED")

    def batch(self, positions: tuple[int, ...]) -> SessionBatch:
        self.verify()
        base = self.stock.batch(positions)
        lookup = dict(self.market_indices)
        extra = torch.zeros((*base.inputs.shape[:-1], 5), dtype=torch.float32)
        for i, day in enumerate(base.ids):
            for origin in (1, 2):
                if bool(base.origins[i, origin - 1]):
                    indices = lookup[day, origin]
                    mask = torch.tensor([v >= 0 for v in indices])
                    if not bool(mask[-1]) or int(mask.sum()) < 46:
                        raise ValueError("MARKET_ENDPOINT_AND_46_OF_48_REQUIRED")
                    values = torch.zeros(48, 5, dtype=torch.float32)
                    values[mask] = self.market[torch.tensor([v for v in indices if v >= 0])]
                    extra[i, origin - 1] = values[None].expand(5, -1, -1)
        joined = torch.cat((base.inputs, extra), dim=-1)
        if self.channels == 23:
            peers = torch.zeros((*base.inputs.shape[:-1], 2), dtype=torch.float32)
            for i in range(len(base.ids)):
                for o in range(2):
                    if bool(base.origins[i, o]):
                        peers[i, o] = torch.tensor(
                            peer_summaries(base.inputs[i, o].numpy()), dtype=torch.float32
                        )
            joined = torch.cat((joined, peers), dim=-1)
        result = SessionBatch(base.ids, joined, base.targets, base.origins)
        result.validate()
        return result

    def summary(self) -> dict:
        return {
            **self.stock.summary(),
            "view_id": self.version,
            "stock_view_id": self.stock.version,
            "channels": self.channels,
            "preparation_id": self.preparation_id,
            "market_recipe_id": self.recipe_id,
            "market_table_bytes": self.market.nelement() * self.market.element_size(),
            "evidence_grade": "RESEARCHER_ATTESTED_IDEALIZED_RETROSPECTIVE",
        }


@dataclass
class BatchInputs:
    review: BridgeReview
    base: BaseTables
    candidates: dict[str, CandidateView]
    market_store: dict
    stock_cache: dict[str, RealInputView] = field(default_factory=dict)
    market_cache: dict[str, tuple[torch.Tensor, dict[pd.Timestamp, int]]] = field(
        default_factory=dict
    )

    def stock_view(self, key: str) -> RealInputView:
        if key not in {"inner", "validation", "refit", "WF1"}:
            raise ValueError("EXACT_WF1_BATCH_WINDOW_REQUIRED")
        if key not in self.stock_cache:
            from .baseline_ridge import windows

            inner, tail, full = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))
            wf = FitWindow(
                "BRIDGE_REVIEW:WF1",
                pd.Timestamp("2023-07-01T04:00Z"),
                pd.Timestamp("2024-01-01T05:00Z"),
                pd.Timestamp("2024-01-01T05:00Z"),
                "INNER_VALIDATION",
            )
            recipe = "WF1_INNER_TRAIN" if key in {"inner", "validation"} else "WF1_REFIT"
            self.stock_cache[key] = build_view(
                self.review,
                self.candidates[recipe],
                {"inner": inner, "validation": tail, "refit": full, "WF1": wf}[key],
                asof=key in {"validation", "WF1"},
            )
        return self.stock_cache[key]

    def view(self, key: str, channels: int) -> ConditionedView:
        stock = self.stock_view(key)
        prefix = "WF1_INNER_TRAIN" if key in {"inner", "validation"} else "WF1_REFIT"
        recipe = self.market_store["preparations"][prefix]
        if (
            pd.Timestamp(recipe["window"]["stop"])
            != self.candidates[prefix].preparation.window.stop
        ):
            raise ValueError("MATCHED_STOCK_MARKET_PREFIX_REQUIRED")
        if prefix not in self.market_cache:
            values, times = [], {}
            for original in self.market_store["measures"]:
                row = dict(original)
                row["timestamp"] = pd.Timestamp(row["timestamp"])
                row["evidence_ids"] = tuple(row["evidence_ids"])
                if row["timestamp"] >= BARRIER:
                    raise ValueError("CONFIRMATION_MARKET_ACCESS_FORBIDDEN")
                raw = conditional_vector(
                    MarketMeasures(**row), recipe["hourly_floor"], recipe["daily_floor"]
                )
                if raw is not None:
                    if row["timestamp"] in times:
                        raise ValueError("DUPLICATE_MARKET_TIMESTAMP")
                    times[row["timestamp"]] = len(values)
                    values.append(
                        tuple(
                            0.0 if method == "CONSTANT" else (v - c) / s
                            for v, c, s, method in zip(
                                raw, recipe["centers"], recipe["scales"], recipe["methods"]
                            )
                        )
                    )
            self.market_cache[prefix] = torch.tensor(values, dtype=torch.float32), times
        table, times = self.market_cache[prefix]
        indices = []
        for row in stock.rows:
            steps = [
                self.base.history.calendar.steps[p]
                for p in self.base.origin_steps[row.session, row.origin]
            ]
            if key in {"validation", "WF1"} and any(
                s.end < pd.Timestamp(recipe["window"]["stop"]) for s in steps
            ):
                raise ValueError("MARKET_SCALER_NOT_AVAILABLE_AT_OWN_STEP")
            ids = tuple(times.get(s.end, -1) for s in steps)
            if ids[-1] < 0 or sum(i >= 0 for i in ids) < 46:
                raise ValueError("UNMATCHED_REAL_MARKET_POPULATION")
            indices.append(((row.session, row.origin), ids))
        view = ConditionedView(
            stock, table, tuple(indices), tensor_hash(table), identity(recipe), channels
        )
        view.verify()
        return view


def load_batch_inputs(review: BridgeReview, binding: dict) -> BatchInputs:
    """Load original stores once per worker; no new floor/scaler or features fitted."""
    base, candidates = load_inputs(review, ("WF1_INNER_TRAIN", "WF1_REFIT"))
    path = verify_ref(review.root, binding["SPY_store_reference_only_not_TM0_input"])
    market = json.loads(gzip.decompress(path.read_bytes()))
    return BatchInputs(review, base, candidates, market)
