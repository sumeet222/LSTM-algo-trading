"""Causal calendar and deterministic receipt-time scheduling."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from ..stage012.calendar_schedule import MarketClock
from ..stage012.contracts import utc


@dataclass(frozen=True)
class OrderWindow:
    decision: datetime
    submission: datetime
    first_minute: datetime
    deadline: datetime | None
    kind: str


def window(
    clock: MarketClock,
    origin: datetime,
    latest_receipt: datetime,
    kind: str = "ENTRY",
    delay: int = 2,
) -> OrderWindow:
    if delay not in (1, 2, 5) or kind not in ("ENTRY", "EXIT"):
        raise ValueError("TIMING_SCENARIO")
    anchor = origin if kind == "ENTRY" else clock.endpoint(origin)
    decision = max(utc(anchor) + timedelta(minutes=delay), utc(latest_receipt))
    deadline = utc(origin) + timedelta(minutes=5) if kind == "ENTRY" else None
    first = clock.next_observation(decision)
    if deadline is not None and first > deadline:
        raise ValueError("ENTRY_DEADLINE_UNREACHABLE")
    return OrderWindow(decision, decision, first, deadline, kind)


@dataclass(frozen=True)
class ScheduledEvent:
    event_id: str
    event_time: datetime
    available_at: datetime
    priority: int


def schedule(events: tuple[ScheduledEvent, ...]) -> tuple[ScheduledEvent, ...]:
    if len({e.event_id for e in events}) != len(events) or any(
        utc(e.available_at) < utc(e.event_time) for e in events
    ):
        raise ValueError("INVALID_EVENT_SCHEDULE")
    return tuple(
        sorted(
            events, key=lambda e: (utc(e.available_at), e.priority, utc(e.event_time), e.event_id)
        )
    )
