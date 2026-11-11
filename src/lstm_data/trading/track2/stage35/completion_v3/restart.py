"""Versioned JSON checkpoints with a closed dataclass allowlist; never pickle/eval.

Historical restoration requires a fresh independently verified release. Checkpoint
hash comes from the append-only run receipt; it is not a replacement for release.
"""

import json
from dataclasses import fields, is_dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path

from ...stage012.calendar_schedule import MarketClock
from ...stage012.cohort_state import Cohort, Event, EventKind
from ..accounting import CashClaim, Journal, Lot, Physical
from ..common import Price
from ..completion_v2.engine import ReleasedPrice
from ..completion_v2.release import VerifiedRelease
from ..completion_v2.settlement import FeeState, NetSubmission, Request, UndatedClaim, V2Book
from ..internal_cross import Leg
from .acquire import write_once
from .engine import EconomicReplayV3
from .event_ledger import sha
from .inventory import digest

CLASSES = {
    c.__name__: c
    for c in (
        Cohort,
        Event,
        CashClaim,
        Journal,
        Lot,
        Physical,
        Price,
        ReleasedPrice,
        VerifiedRelease,
        FeeState,
        NetSubmission,
        Request,
        UndatedClaim,
        V2Book,
        Leg,
    )
}


def encode(value: object) -> object:
    if isinstance(value, Decimal):
        return {"$decimal": str(value)}
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise ValueError("CHECKPOINT_AWARE_TIMES_REQUIRED")
        return {"$datetime": value.isoformat()}
    if isinstance(value, Enum):
        if not isinstance(value, EventKind):
            raise ValueError("CHECKPOINT_ENUM_NOT_ALLOWED")
        return {"$event_kind": value.value}
    if isinstance(value, Cohort) and any(
        not isinstance(getattr(value, k), (int, float))
        for k in ("requested", "budget", "shares", "entered")
    ):
        raise ValueError("COHORT_METADATA_MUST_MATCH_FLOAT_SCHEMA")
    if is_dataclass(value) and not isinstance(value, type):
        name = type(value).__name__
        if name not in CLASSES:
            raise ValueError("CHECKPOINT_CLASS_NOT_ALLOWED")
        return {
            "$class": name,
            "fields": {f.name: encode(getattr(value, f.name)) for f in fields(value)},
        }
    if isinstance(value, tuple):
        return {"$tuple": [encode(v) for v in value]}
    if isinstance(value, list):
        return [encode(v) for v in value]
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value):
            raise ValueError("CHECKPOINT_STRING_KEYS_REQUIRED")
        return {k: encode(v) for k, v in value.items()}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise ValueError("CHECKPOINT_VALUE_NOT_ALLOWED")


def decode(value: object) -> object:
    if isinstance(value, list):
        return [decode(v) for v in value]
    if not isinstance(value, dict):
        return value
    if "$decimal" in value:
        return Decimal(value["$decimal"])
    if "$datetime" in value:
        result = datetime.fromisoformat(value["$datetime"])
        if result.tzinfo is None:
            raise ValueError("CHECKPOINT_NAIVE_TIME")
        return result
    if "$event_kind" in value:
        return EventKind(value["$event_kind"])
    if "$tuple" in value:
        return tuple(decode(v) for v in value["$tuple"])
    if "$class" in value:
        name = value["$class"]
        if name not in CLASSES:
            raise ValueError("UNTRUSTED_CHECKPOINT_CLASS")
        from .restart_schema import construct

        return construct(name, {k: decode(v) for k, v in value["fields"].items()})
    return {k: decode(v) for k, v in value.items()}


def save(engine: EconomicReplayV3, path: Path, binding: dict) -> str:
    engine.book.reconcile()
    payload = encode(
        {
            "book": engine.book,
            "pending": engine.pending,
            "last_processed": engine.last_processed,
            "rates": engine.rates,
            "statuses": engine.statuses,
            "action_receipts": engine.action_receipts,
            "release": engine.release,
        }
    )
    write_once(
        path,
        {
            "version": "V3_RESTART_1",
            "account": engine.account,
            "arm": engine.arm,
            "binding": binding,
            "payload_hash": sha(payload),
            "payload": payload,
        },
    )
    return digest(path)


def restore(
    path: Path,
    expected_file_hash: str,
    binding: dict,
    clock: MarketClock,
    release: VerifiedRelease | None = None,
) -> EconomicReplayV3:
    if digest(path) != expected_file_hash:
        raise ValueError("CHECKPOINT_FILE_HASH_CHANGED")
    record = json.loads(path.read_text())
    if (
        record["version"] != "V3_RESTART_1"
        or record["binding"] != binding
        or sha(record["payload"]) != record["payload_hash"]
    ):
        raise ValueError("CHECKPOINT_BINDING_OR_BODY_CHANGED")
    state = decode(record["payload"])
    if not isinstance(state, dict) or not isinstance(state.get("book"), V2Book):
        raise ValueError("CHECKPOINT_BOOK_TYPE")
    book = state["book"]
    if state["release"] != release:
        raise PermissionError("FRESH_EXACT_HUMAN_RELEASE_REQUIRED_TO_RESUME")
    if any(
        point.kind != "SYNTHETIC"
        and (not isinstance(point, ReleasedPrice) or point.release != release or release is None)
        for _, point in book.marks
    ):
        raise PermissionError("HISTORICAL_CHECKPOINT_CANNOT_BE_RELABELLED")
    book.reconcile()
    for before, after in zip(book.journal, book.journal[1:]):
        if before.after != after.before:
            raise ValueError("CHECKPOINT_JOURNAL_CHAIN")
    engine = EconomicReplayV3(record["account"], record["arm"], book, clock, release)
    if not isinstance(state["pending"], dict) or not all(
        isinstance(v, NetSubmission) for v in state["pending"].values()
    ):
        raise ValueError("CHECKPOINT_PENDING_ORDER_TYPES")
    engine.pending = state["pending"]
    engine.last_processed = state["last_processed"]
    engine.rates = state["rates"]
    engine.statuses = state["statuses"]
    engine.action_receipts = state["action_receipts"]
    return engine
