"""Chronological engine boundary and independent financial-release entry.

Synthetic tapes exercise economics. The historical entry ALWAYS verifies release
before calling a source loader or creating output, regardless of source labels.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

from ...stage012.calendar_schedule import MarketClock
from ..common import D, Price
from .release import VerifiedRelease, verify_release
from .settlement import (
    FinalBar,
    NetSubmission,
    V2Book,
    carry_to,
    liquidation_requests,
    settle,
    split_order_units,
)
from .tapes import DueEvent, apply_due


@dataclass(frozen=True)
class ReleasedPrice(Price):
    release: VerifiedRelease | None = None

    def validate(self, processed: datetime) -> None:
        if self.kind != "HISTORICAL" or self.release is None:
            raise PermissionError("VERIFIED_HISTORICAL_RELEASE_REQUIRED")
        # Reuse raw/time/value arithmetic; never relabel actual data SYNTHETIC.
        end = self.completed_at or self.at
        if (
            not self.at <= end <= self.available_at <= processed
            or self.basis != "RAW_UNADJUSTED"
            or self.value <= 0
            or not self.value.is_finite()
        ):
            raise ValueError("HISTORICAL_RAW_PRICE_CONTRACT")


@dataclass(frozen=True)
class ReleasedBar(FinalBar):
    release: VerifiedRelease | None = None

    def reference(self, posted: datetime) -> Price:
        if (
            self.open is None
            or self.status != "VALID"
            or self.vintage != "ORIGINAL_OBSERVED"
            or self.complete != self.start + timedelta(minutes=1)
        ):
            raise ValueError("UNRESOLVED_BAR_OR_CORRECTION_REPLAY_REQUIRED")
        point = ReleasedPrice(
            self.start,
            self.available,
            self.open,
            self.source_id,
            self.basis,
            "HISTORICAL",
            self.complete,
            self.release,
        )
        point.validate(posted)
        return point


@dataclass(frozen=True)
class ReplayEvent:
    available: datetime
    priority: int
    event_id: str
    kind: str
    order: NetSubmission | None = None
    bar: FinalBar | None = None
    due: DueEvent | None = None
    reference: Price | None = None
    ticker: str = ""
    rate: D | None = None


class ReplayEngine:
    """One account/arm only; unobservable executions retain reservations/inventory."""

    def __init__(self, account: str, arm: str, book: V2Book, clock: MarketClock):
        self.account, self.arm, self.book, self.clock = account, arm, book, clock
        self.pending: dict[str, NetSubmission] = {}
        self.statuses: list[dict] = []
        self.last_processed: datetime | None = None
        self.rates: dict[str, D | None] = {}

    def add(self, order: NetSubmission) -> None:
        if order.account != self.account or order.arm != self.arm or order.order_id in self.pending:
            raise ValueError("ACCOUNT_ARM_OR_DUPLICATE_ORDER")
        if self.last_processed and order.submitted_at < self.last_processed:
            raise ValueError("BACKDATED_ORDER_AFTER_RECEIPT")
        if (
            any(r.role == "ENTRY" for r in order.requests)
            and self.book.capacity(order.decision_at).status != "READY"
        ):
            raise ValueError("ACCOUNT_PRETRADE_CAPACITY_HOLD")
        self.pending[order.order_id] = order

    def decision_ready(self, at: datetime) -> bool:
        return (
            not any(o.event_minute <= at for o in self.pending.values())
            and not self.book.unresolved
        )

    def process(self, events: tuple[ReplayEvent, ...]) -> None:
        ordered = sorted(events, key=lambda e: (e.available, e.priority, e.event_id))
        if len({e.event_id for e in ordered}) != len(ordered):
            raise ValueError("DUPLICATE_REPLAY_EVENT")
        for event in ordered:
            if self.last_processed and event.available < self.last_processed:
                raise ValueError("RECEIPT_REORDER_REQUIRED")
            if event.kind == "EXPIRY":
                from .orchestration import expire_unsubmitted_remainders

                expire_unsubmitted_remainders(self, event.available)
            elif event.kind == "DUE":
                if event.due is None or event.reference is None:
                    raise ValueError("DUE_TAPE_MISSING")
                self.book = carry_to(
                    self.book,
                    event.due.ticker,
                    event.due.effective,
                    self.rates.get(event.due.ticker, D(".02")),
                    event.available,
                    event.event_id + ":CARRY",
                )
                self.book = apply_due(self.book, event.due, event.reference, event.available)
                action = event.due.action
                if (
                    action
                    and action.kind == "SPLIT"
                    and action.ratio is not None
                    and action.economic_ready()
                    and action.available <= action.effective
                ):
                    for key, pending in tuple(self.pending.items()):
                        if pending.ticker == action.ticker:
                            self.pending[key] = split_order_units(
                                pending, action.ratio, action.effective, action.available
                            )
                            self.statuses.append(
                                {
                                    "order": key,
                                    "status": "SPLIT_UNIT_CHANGE",
                                    "ratio": str(action.ratio),
                                    "action": action.action_id,
                                }
                            )
            elif event.kind == "RATE":
                if event.reference is None or not event.ticker:
                    raise ValueError("RATE_TIME_REFERENCE_REQUIRED")
                self.book = carry_to(
                    self.book,
                    event.ticker,
                    event.reference.at,
                    self.rates.get(event.ticker, D(".02")),
                    event.available,
                    event.event_id + ":CARRY",
                )
                if event.rate is not None and (not event.rate.is_finite() or event.rate < 0):
                    raise ValueError("INVALID_BORROW_RATE")
                self.rates[event.ticker] = event.rate
            elif event.kind == "MARK":
                if event.reference is None or not event.ticker:
                    raise ValueError("MARK_SOURCE_MISSING")
                self.book = carry_to(
                    self.book,
                    event.ticker,
                    event.reference.at,
                    self.rates.get(event.ticker, D(".02")),
                    event.available,
                    event.event_id + ":CARRY",
                )
                marked = self.book.mark(
                    event.event_id, event.ticker, event.reference, event.available
                )
                if not isinstance(marked, V2Book):
                    raise AssertionError("V2_MARK_STATE")
                self.book = marked
            elif event.kind in ("BAR", "MISSING", "HALT"):
                if event.order is None or event.order.order_id not in self.pending:
                    raise ValueError("SUBMISSION_NOT_RECORDED")
                order = event.order
                if order != self.pending[order.order_id]:
                    raise ValueError("SUBMITTED_ORDER_MUTATION")
                if (
                    self.clock.next_observation(order.event_minute - timedelta(minutes=1))
                    != order.event_minute
                ):
                    raise ValueError("CLOSED_EXCHANGE_FILL_FORBIDDEN")
                if event.bar is None or event.kind != "BAR" or event.bar.status != "VALID":
                    result = self.book.status_event(
                        event.event_id,
                        event.available,
                        event.available,
                        "UNRESOLVED_EXECUTION_NO_PRICE",
                        order.ticker,
                        unresolved=True,
                    )
                    if not isinstance(result, V2Book):
                        raise AssertionError("V2_BOOK")
                    self.book = result
                    self.statuses.append(
                        {
                            "order": order.order_id,
                            "status": "UNRESOLVED",
                            "posted_at": event.available,
                        }
                    )
                    # Resting order state is uncertain, not an asserted broker cancellation.
                    self.last_processed = event.available
                    continue
                # Carry is segmented before changes using the previous known mark.
                self.book = carry_to(
                    self.book,
                    order.ticker,
                    event.bar.start,
                    self.rates.get(order.ticker, D(".02")),
                    event.available,
                    event.event_id + ":CARRY",
                )
                self.book = settle(self.book, order, event.bar, event.available)
                del self.pending[order.order_id]
                residual = tuple(
                    r
                    for r in order.requests
                    if any(
                        item.cohort.cohort_id == r.cohort_id and item.pending
                        for item in self.book.lots
                    )
                )
                if residual:
                    self.statuses.append(
                        {
                            "order": order.order_id,
                            "status": "PARTIAL_PENDING_REQUIRES_NEXT_SUBMISSION",
                            "posted_at": event.available,
                        }
                    )
                status = self.book.capacity(event.available).status
                if status not in ("READY", "CARRY_PENDING"):
                    self.statuses.append(
                        {
                            "status": "BLOCK_INCREASES_PROSPECTIVE_LIQUIDATION",
                            "decision_at": event.available,
                            "first_possible_minute": self.clock.next_observation(event.available),
                            "requests": [
                                asdict(r) for r in liquidation_requests(self.book, order.ticker)
                            ],
                        }
                    )
            else:
                raise ValueError("UNKNOWN_REPLAY_EVENT")
            self.last_processed = event.available

        if ordered:
            from .orchestration import expire_unsubmitted_remainders

            expire_unsubmitted_remainders(self, ordered[-1].available)

    def snapshot(self) -> dict:
        self.book.reconcile()
        return {
            "account": self.account,
            "arm": self.arm,
            "cash": self.book.cash,
            "restricted_proceeds_subset_of_cash": self.book.restricted(),
            "nav": self.book.nav(),
            "emergency_debt_in_accruals": self.book.emergency_funding_debt,
            "virtual_lots": [asdict(lot) for lot in self.book.lots],
            "physical": [asdict(p) for p in self.book.positions],
            "claims": [asdict(c) for c in self.book.claims],
            "journal": [asdict(j) for j in self.book.journal],
            "unresolved": self.book.unresolved,
            "orders_pending": list(self.pending),
            "statuses": self.statuses,
        }


def historical_financial_entry(
    gate: Path,
    binding: dict,
    public_key: Path,
    signature: Path,
    output: Path,
    loader: Callable[[VerifiedRelease], tuple[ReplayEngine, tuple[ReplayEvent, ...]]],
) -> None:
    """Gate first: no source loading, mkdir or output before signed review succeeds."""
    release = verify_release(gate, binding, public_key, signature)
    engine, events = loader(release)
    if any(
        e.bar is not None and (not isinstance(e.bar, ReleasedBar) or e.bar.release != release)
        for e in events
    ):
        raise PermissionError("REAL_SOURCE_RELEASE_BINDING_REQUIRED_NO_TYPE_FLAG_BYPASS")
    engine.process(events)
    if output.exists():
        raise ValueError("APPEND_ONLY_FINANCIAL_OUTPUT")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(engine.snapshot(), indent=2, default=str) + "\n")
