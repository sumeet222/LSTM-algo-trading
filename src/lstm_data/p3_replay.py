"""Immutable synthetic opportunity scripts, fresh accounts for each scenario."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import pandas as pd

from .clocks import utc
from .config import fingerprint
from .p3_accounting import ActionInstruction
from .p3_domain import Forecast, Frictions, Permission, PriceReference, UniverseSpec, synthetic_id
from .p3_engine import PortfolioEngine
from .p3_events import json_value
from .p3_execution import ExecutionOffer
from .p3_policy import Policy


@dataclass(frozen=True)
class ReplayFrame:
    universe: UniverseSpec
    frame_id: str
    at: pd.Timestamp
    marks: tuple[PriceReference, ...] = ()
    offers: tuple[ExecutionOffer, ...] = ()
    forecast: Forecast | None = None
    borrow_close: bool = False
    actions: tuple[ActionInstruction, ...] = ()
    settlements: tuple[str, ...] = ()
    action_coverage: str = "SYNTHETIC_COMPLETE"

    def __post_init__(self) -> None:
        synthetic_id(self.frame_id)
        object.__setattr__(self, "at", utc(self.at))
        if (
            not isinstance(self.marks, tuple)
            or not isinstance(self.offers, tuple)
            or not isinstance(self.actions, tuple)
            or not isinstance(self.settlements, tuple)
            or self.action_coverage not in {"SYNTHETIC_COMPLETE", "UNKNOWN"}
            or any(a.universe != self.universe or a.boundary != self.at for a in self.actions)
            or any(r.universe != self.universe for r in self.marks)
            or any(o.universe != self.universe for o in self.offers)
            or (self.forecast is not None and self.forecast.universe != self.universe)
        ):
            raise ValueError("IMMUTABLE_FRAME_UNIVERSE_MISMATCH")
        for claim in self.settlements:
            synthetic_id(claim)


def replay(
    permission: Permission,
    universe: UniverseSpec,
    script: tuple[ReplayFrame, ...],
    policy: str,
    frictions: Frictions,
    cash: Decimal,
    at: pd.Timestamp,
) -> PortfolioEngine:
    permission.ensure()
    if (
        not isinstance(script, tuple)
        or any(f.universe != universe for f in script)
        or any(a.at > b.at for a, b in zip(script, script[1:]))
    ):
        raise ValueError("MONOTONIC_IMMUTABLE_SYNTHETIC_SCRIPT_REQUIRED")
    seen: dict[str, ReplayFrame] = {}
    times: set[pd.Timestamp] = set()
    unique = []
    for frame in script:
        old = seen.get(frame.frame_id)
        if old is not None:
            if old != frame:
                raise ValueError("DIVERGENT_DUPLICATE_REPLAY_FRAME")
            continue
        seen[frame.frame_id] = frame
        if frame.at in times:
            raise ValueError("COMBINE_SIMULTANEOUS_EVENTS_IN_ONE_EXPLICIT_FRAME")
        if frame.actions and (frame.offers or frame.forecast is not None):
            raise ValueError("UNAPPROVED_SAME_TIME_ACTION_FILL_ORDERING")
        times.add(frame.at)
        unique.append(frame)
    engine = PortfolioEngine(universe, permission, Policy(universe, policy), frictions, cash, at)
    for frame in unique:
        permission.ensure()
        if frame.forecast is not None and (
            engine.pending_target is not None
            or any(s.expires_at <= frame.at for s in engine.sleeves)
        ):
            raise ValueError("UNAPPROVED_SIMULTANEOUS_EXCEPTION_EXIT_AND_NEW_ENTRY")
        if frame.action_coverage == "UNKNOWN":
            engine.action_coverage = False
        engine.apply_actions(frame.actions, frame.at)
        for claim in frame.settlements:
            engine.book.settle(claim, frame.at)
        engine.monitor(frame.at, frame.marks, frame.frame_id)
        # A trigger at this instant may only liquidate at a later supported minute.
        if engine.pending_target is not None:
            if engine.pending_since is not None and frame.at > engine.pending_since:
                engine.retry(frame.at, frame.offers, frame.frame_id)
        else:
            engine.expire(frame.at, frame.offers, frame.frame_id + ":EXPIRY")
        if frame.forecast is not None:
            engine.enter(frame.forecast, frame.at, frame.offers, frame.marks)
        if frame.borrow_close:
            engine.borrow.close(engine.book, frame.at)
        engine.valuation(frame.at, frame.marks, frame.frame_id)
    return engine


def scenario_matrix(
    permission: Permission,
    universe: UniverseSpec,
    script: tuple[ReplayFrame, ...],
    cash: Decimal,
    at: pd.Timestamp,
) -> list[dict]:
    permission.ensure()
    input_id = fingerprint(json_value(script))
    rows = []
    for policy in ("A", "B"):
        for bps in (0, 2, 5, 10):
            for borrow in (Decimal(0), Decimal(".005"), Decimal(".03")):
                frictions = Frictions(universe, Decimal(bps), borrow)
                engine = replay(permission, universe, script, policy, frictions, cash, at)
                rows.append(
                    {
                        "scope": "SYNTHETIC_ACCOUNTING_ONLY",
                        "universe_id": universe.universe_id,
                        "script_id": input_id,
                        "policy": policy,
                        "bps": bps,
                        "annual_borrow": str(borrow),
                        "friction_id": frictions.friction_id,
                        "execution_fee": str(engine.book.execution_fees),
                        "borrow_fee": None
                        if engine.borrow.total is None
                        else str(engine.borrow.total),
                        "rejections": engine.rejections,
                        "exceptions": engine.exceptions,
                        "trace_id": engine.ledger.trace_id,
                        "research_ready": False,
                    }
                )
    return rows
