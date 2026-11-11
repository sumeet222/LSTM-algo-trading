"""Explicit validated JSON-to-domain constructors for restart files; no type erasure."""

from datetime import datetime
from decimal import Decimal
from typing import TypeVar

from ...stage012.cohort_state import Cohort, Event, EventKind
from ..accounting import CashClaim, Journal, Lot, Physical
from ..common import Price
from ..completion_v2.engine import ReleasedPrice
from ..completion_v2.release import VerifiedRelease
from ..completion_v2.settlement import FeeState, NetSubmission, Request, UndatedClaim, V2Book
from ..internal_cross import Leg

T = TypeVar("T")


def required(row: dict, key: str, kind: type[T]) -> T:
    value = row[key]
    if not isinstance(value, kind):
        raise ValueError("CHECKPOINT_FIELD_TYPE:" + key)
    return value


def optional(row: dict, key: str, kind: type[T]) -> T | None:
    return None if row[key] is None else required(row, key, kind)


def sequence(row: dict, key: str, kind: type[T]) -> tuple[T, ...]:
    value = required(row, key, tuple)
    result: list[T] = []
    for item in value:
        if not isinstance(item, kind):
            raise ValueError("CHECKPOINT_SEQUENCE_TYPE:" + key)
        result.append(item)
    return tuple(result)


def pairs(row: dict, key: str, kind: type[T]) -> tuple[tuple[str, T], ...]:
    result = []
    for item in required(row, key, tuple):
        if (
            not isinstance(item, tuple)
            or len(item) != 2
            or not isinstance(item[0], str)
            or not isinstance(item[1], kind)
        ):
            raise ValueError("CHECKPOINT_PAIR_TYPE:" + key)
        result.append((item[0], item[1]))
    return tuple(result)


def number(row: dict, key: str) -> int | float:
    value = row[key]
    if not isinstance(value, (int, float)):
        raise ValueError("CHECKPOINT_NUMBER:" + key)
    return value


def construct(name: str, f: dict) -> object:
    if name == "Cohort":
        return Cohort(
            required(f, "cohort_id", str),
            required(f, "ticker", str),
            number(f, "requested"),
            number(f, "budget"),
            required(f, "origin", datetime),
            required(f, "endpoint", datetime),
            required(f, "entry_deadline", datetime),
            required(f, "basis", str),
            sequence(f, "provenance", str),
            required(f, "status", str),
            number(f, "shares"),
            number(f, "entered"),
            optional(f, "entry_at", datetime),
            None if f["entry_price"] is None else number(f, "entry_price"),
            optional(f, "exit_at", datetime),
            None if f["exit_price"] is None else number(f, "exit_price"),
            optional(f, "planned_exit_order_at", datetime),
            sequence(f, "events", Event),
        )
    if name == "Event":
        return Event(
            required(f, "event_id", str),
            required(f, "kind", EventKind),
            required(f, "at", datetime),
            number(f, "quantity"),
            number(f, "price"),
            number(f, "amount"),
            required(f, "basis", str),
        )
    if name == "CashClaim":
        return CashClaim(
            required(f, "action_id", str),
            required(f, "cohort_id", str),
            required(f, "amount", Decimal),
            required(f, "due_at", datetime),
        )
    if name == "UndatedClaim":
        return UndatedClaim(
            required(f, "action_id", str),
            required(f, "cohort_id", str),
            required(f, "amount", Decimal),
        )
    if name == "Physical":
        return Physical(
            required(f, "ticker", str),
            required(f, "quantity", Decimal),
            required(f, "basis", Decimal),
            required(f, "realized", Decimal),
            optional(f, "borrow_asof", datetime),
        )
    if name == "Lot":
        return Lot(
            required(f, "cohort", Cohort),
            required(f, "quantity", Decimal),
            required(f, "basis", Decimal),
            required(f, "cash", Decimal),
            required(f, "realized", Decimal),
            required(f, "nontrade_cash", Decimal),
            required(f, "accrual", Decimal),
            required(f, "pending", Decimal),
            required(f, "unit_factor", Decimal),
            required(f, "closed", bool),
        )
    if name == "Price":
        return Price(
            required(f, "at", datetime),
            required(f, "available_at", datetime),
            required(f, "value", Decimal),
            required(f, "source_id", str),
            required(f, "basis", str),
            required(f, "kind", str),
            optional(f, "completed_at", datetime),
        )
    if name == "ReleasedPrice":
        return ReleasedPrice(
            required(f, "at", datetime),
            required(f, "available_at", datetime),
            required(f, "value", Decimal),
            required(f, "source_id", str),
            required(f, "basis", str),
            required(f, "kind", str),
            optional(f, "completed_at", datetime),
            optional(f, "release", VerifiedRelease),
        )
    if name == "VerifiedRelease":
        return VerifiedRelease(
            required(f, "binding_sha256", str),
            required(f, "approval_id", str),
            required(f, "approver_key_sha256", str),
        )
    if name == "FeeState":
        return FeeState(
            required(f, "order_id", str),
            required(f, "shares", Decimal),
            required(f, "paid", Decimal),
        )
    if name == "Request":
        return Request(
            required(f, "cohort_id", str), required(f, "delta", Decimal), required(f, "role", str)
        )
    if name == "NetSubmission":
        return NetSubmission(
            required(f, "order_id", str),
            required(f, "account", str),
            required(f, "arm", str),
            required(f, "ticker", str),
            required(f, "decision_at", datetime),
            required(f, "submitted_at", datetime),
            required(f, "event_minute", datetime),
            optional(f, "expiry", datetime),
            sequence(f, "requests", Request),
            required(f, "net", Decimal),
            required(f, "external_capacity", Decimal),
            required(f, "prior_volume_available", datetime),
            required(f, "reference_price", Decimal),
            required(f, "borrow_mode", str),
            required(f, "conditional_assumption_id", str),
        )
    if name == "Leg":
        return Leg(
            required(f, "cohort_id", str),
            required(f, "quantity", Decimal),
            required(f, "price", Decimal),
            required(f, "fee", Decimal),
            required(f, "internal", bool),
        )
    if name == "Journal":
        return Journal(
            required(f, "journal_id", str),
            required(f, "event_time", datetime),
            required(f, "observation_time", datetime),
            required(f, "available_at", datetime),
            required(f, "processed_at", datetime),
            required(f, "cause", str),
            required(f, "ticker", str),
            required(f, "currency", str),
            required(f, "basis", str),
            sequence(f, "legs", Leg),
            required(f, "amount", Decimal),
            required(f, "before", str),
            required(f, "after", str),
            optional(f, "reference", Price),
            pairs(f, "details", str),
        )
    if name == "V2Book":
        return V2Book(
            required(f, "initial_cash", Decimal),
            required(f, "cash", Decimal),
            sequence(f, "lots", Lot),
            sequence(f, "positions", Physical),
            pairs(f, "marks", Price),
            sequence(f, "journal", Journal),
            sequence(f, "unresolved", str),
            sequence(f, "claims", CashClaim),
            sequence(f, "action_keys", str),
            sequence(f, "order_fees", FeeState),
            required(f, "emergency_funding_debt", Decimal),
            sequence(f, "undated_claims", UndatedClaim),
            pairs(f, "funding_claims", Decimal),
        )
    raise ValueError("UNTRUSTED_CHECKPOINT_CLASS")
