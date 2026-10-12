"""Deterministic synthetic event graph, distinct from the protected scientific ledger."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from decimal import Decimal

import pandas as pd

from .clocks import utc
from .config import fingerprint
from .ledger import safe_payload
from .p3_domain import Permission, UniverseSpec, synthetic_id

KINDS = frozenset(
    {
        "ACCOUNT",
        "FORECAST",
        "INTENT",
        "SLEEVE",
        "TARGET",
        "ORDER",
        "FILL",
        "CASH",
        "POSITION",
        "MARK",
        "ACTION",
        "RISK",
        "RETRY",
        "EXCEPTION",
        "VALUATION",
        "BORROW",
        "FEE",
        "SETTLEMENT",
        "REJECT",
        "SLEEVE_END",
    }
)


def synthetic_payload(value: object) -> None:
    """Reject empirical provenance and activation claims before any ledger output."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"basis", "source_basis", "forecast_basis"} and item != "SYNTHETIC":
                raise ValueError("SYNTHETIC_PAYLOAD_REQUIRED")
            if key in {"provider_fill_claim", "research_ready"} and item is not False:
                raise ValueError("EMPIRICAL_ACTIVATION_NOT_AUTHORIZED")
            if key in {"source_id", "model_id"}:
                if not isinstance(item, str):
                    raise ValueError("SYNTHETIC_ID_REQUIRED")
                synthetic_id(item)
            synthetic_payload(item)
    elif isinstance(value, list):
        for item in value:
            synthetic_payload(item)


def json_value(value: object):
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("FINITE_EVENT_NUMBERS_REQUIRED")
        return value
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("FINITE_EVENT_MONEY_REQUIRED")
        return str(value)
    if isinstance(value, (datetime, pd.Timestamp, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]
    if is_dataclass(value) and not isinstance(value, type):
        return json_value(asdict(value))
    raise ValueError("SERIALIZABLE_TYPED_EVENT_REQUIRED")


@dataclass(frozen=True)
class Event:
    sequence: int
    event_id: str
    universe_id: str
    at: pd.Timestamp
    kind: str
    parent_id: str | None
    payload_json: str
    research_ready: bool = False


class EventLedger:
    def __init__(self, universe: UniverseSpec, permission: Permission):
        permission.ensure()
        self.universe, self.permission = universe, permission
        self._events: list[Event] = []
        self._ids: dict[str, Event] = {}

    @property
    def events(self) -> tuple[Event, ...]:
        return tuple(self._events)

    def record(
        self,
        event_id: str,
        at: pd.Timestamp,
        kind: str,
        payload: dict,
        parent_id: str | None = None,
    ) -> Event:
        self.permission.ensure()
        synthetic_id(event_id)
        at = utc(at)
        if kind not in KINDS:
            raise ValueError("SUPPORTED_SYNTHETIC_EVENT_KIND_REQUIRED")
        normalized = json_value(payload)
        synthetic_payload(normalized)
        safe_payload(normalized)
        encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
        previous = self._ids.get(event_id)
        if previous is not None:
            if (previous.at, previous.kind, previous.parent_id, previous.payload_json) != (
                at,
                kind,
                parent_id,
                encoded,
            ):
                raise ValueError("DIVERGENT_DUPLICATE_EVENT")
            return previous
        if (self._events and at < self._events[-1].at) or (
            parent_id is not None and parent_id not in self._ids
        ):
            raise ValueError("EVENT_REWIND_OR_ORPHAN_PARENT")
        parents = {
            "INTENT": "FORECAST",
            "SLEEVE": "INTENT",
            "ORDER": "TARGET",
            "FILL": "ORDER",
            "CASH": "FILL|BORROW|SETTLEMENT",
            "POSITION": "FILL|ACTION",
            "FEE": "FILL",
            "SLEEVE_END": "SLEEVE",
        }
        if kind in parents and (
            parent_id is None or self._ids[parent_id].kind not in parents[kind].split("|")
        ):
            raise ValueError("TYPED_EVENT_PARENT_REQUIRED")
        event = Event(
            len(self._events) + 1, event_id, self.universe.universe_id, at, kind, parent_id, encoded
        )
        self._events.append(event)
        self._ids[event_id] = event
        return event

    def export(self) -> list[dict]:
        self.permission.ensure()
        return [
            {
                "sequence": e.sequence,
                "event_id": e.event_id,
                "universe_id": e.universe_id,
                "at": e.at.isoformat(),
                "kind": e.kind,
                "parent_id": e.parent_id,
                "payload": json.loads(e.payload_json),
                "research_ready": False,
            }
            for e in self._events
        ]

    @property
    def trace_id(self) -> str:
        return fingerprint(self.export())
