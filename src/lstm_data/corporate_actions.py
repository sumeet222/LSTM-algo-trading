"""Pure retrospective action accounting, independent of fills and price frequency.

Session-boundary entitlement and fractional shares are explicit simulation
assumptions, never provider publication/effective-time assertions. No I/O here.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import dataclass, replace
from datetime import date, datetime
from decimal import Decimal
from typing import Mapping, cast
from zoneinfo import ZoneInfo

UNIVERSE = frozenset({"AAPL", "JPM", "JNJ", "WMT", "CAT"})
ET = ZoneInfo("America/New_York")


def number(value: object) -> Decimal:
    """Convert declared numeric values without silently accepting NaN/bools."""
    if isinstance(value, bool):
        raise ValueError("Boolean is not an accounting amount")
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError("Accounting amount must be finite")
    return result


def aware(value: datetime) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Explicit aware accounting timestamp required")


def identity(value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Nonempty identity/basis required")


@dataclass(frozen=True)
class SourceEvidence:
    event_id: str
    sha256: str
    retrieved_at: datetime
    publication_at: datetime | None = None

    def __post_init__(self):
        identity(self.event_id)
        if not re.fullmatch(r"[0-9a-f]{64}", self.sha256):
            raise ValueError("Source SHA-256 required")
        aware(self.retrieved_at)
        if self.publication_at is not None:
            aware(self.publication_at)


@dataclass(frozen=True)
class Action:
    source: SourceEvidence
    symbol: str
    kind: str
    boundary: datetime
    sequence: int
    amount: Decimal
    share_basis: str
    post_split_basis: str | None = None
    payable_date: date | None = None
    fractional_policy: str | None = None
    convention: str = "BEGINNING_OF_EX_SESSION_ASSUMPTION"

    def __post_init__(self):
        aware(self.boundary)
        local = self.boundary.astimezone(ET)
        if (local.hour, local.minute, local.second, local.microsecond) != (9, 30, 0, 0):
            raise ValueError("Declared beginning-of-session boundary must be 09:30 ET")
        if self.symbol not in UNIVERSE or self.kind not in {"SPLIT", "DIVIDEND"}:
            raise ValueError("Unsupported holdings/action type")
        if type(self.sequence) is not int or self.sequence < 0:
            raise ValueError("Explicit nonnegative event sequence required")
        object.__setattr__(self, "amount", number(self.amount))
        identity(self.share_basis)
        if self.convention != "BEGINNING_OF_EX_SESSION_ASSUMPTION":
            raise ValueError("Unsupported effective-time convention")
        if self.kind == "SPLIT":
            if self.amount <= 0 or not self.post_split_basis:
                raise ValueError("Positive new/old split ratio and post basis required")
            if self.post_split_basis == self.share_basis:
                raise ValueError("Split must advance raw share basis")
            if self.fractional_policy not in {"EXACT_FRACTIONAL_ASSUMPTION", "INTEGER_ONLY"}:
                raise ValueError("Unknown rounding/cash-in-lieu treatment")
            if self.payable_date is not None:
                raise ValueError("Split payable field is not a dividend settlement")
        elif self.amount < 0 or self.post_split_basis or self.fractional_policy:
            raise ValueError("Invalid dividend amount/basis options")
        if self.payable_date is not None:
            if type(self.payable_date) is not date:
                raise ValueError("Payable date must be a date")
            if self.payable_date < self.boundary.astimezone(ET).date():
                raise ValueError("Dividend payable date precedes entitlement")


def field_evidence(record: Mapping, key: str) -> dict:
    """Preserve the distinction between absent, explicit null and present values."""
    present = key in record
    value = record.get(key)
    return {
        "presence": "ABSENT" if not present else "NULL" if value is None else "PRESENT",
        "value": value,
        "evidence": "VERIFIED_IN_RETRIEVED_RECORD" if present and value is not None else "UNKNOWN",
    }


def reconcile_source(payload: Mapping, source_hash: str, retrieved_at: datetime) -> dict:
    """Audit bounded retained action metadata without constructing accounting events.

    Present fields prove only what this retrieved record says, not issuer truth,
    complete coverage or historical availability. No prices or I/O consumed.
    """
    categories = payload["corporate_actions"]
    rows, missing_dates, seen = [], [], set()
    counts, by_symbol, by_year = Counter(), Counter(), Counter()
    for category, records in categories.items():
        for index, record in enumerate(records):
            event_id = record["id"]
            SourceEvidence(event_id, source_hash, retrieved_at)
            if event_id in seen:
                raise ValueError("Duplicate source event identity")
            seen.add(event_id)
            if category == "cash_mergers":
                symbol = record.get("acquirer_symbol")
                role = "ACQUIRER" if symbol in UNIVERSE else "UNKNOWN"
                classification = "NO_SUPPORTED_ACQUIRER_HOLDINGS_TRANSFORMATION"
                if record.get("acquiree_symbol") in UNIVERSE:
                    symbol, role = record["acquiree_symbol"], "TARGET"
                    classification = "UNSUPPORTED_TARGET_CONVERSION"
                day = record.get("effective_date")
                applicable = (
                    "effective_date",
                    "process_date",
                    "rate",
                    "acquirer_symbol",
                    "acquiree_symbol",
                )
                number(record["rate"])
            elif category in {"forward_splits", "cash_dividends"}:
                symbol, role, day = record.get("symbol"), "ISSUER", record.get("ex_date")
                applicable = ("ex_date", "process_date", "record_date", "payable_date")
                if category == "forward_splits":
                    applicable += ("old_rate", "new_rate", "due_bill_redemption_date")
                    if number(record["old_rate"]) <= 0 or number(record["new_rate"]) <= 0:
                        raise ValueError("Invalid retrieved split ratio")
                    classification = "SUPPORTED_SPLIT_REQUIRES_BASIS_ROUNDING_CONVENTION"
                else:
                    applicable += ("rate",)
                    if number(record["rate"]) < 0:
                        raise ValueError("Invalid retrieved dividend rate")
                    classification = "SUPPORTED_DIVIDEND_REQUIRES_ENTITLEMENT_BASIS"
                    absent = [k for k in ("record_date", "payable_date") if record.get(k) is None]
                    if absent:
                        missing_dates.append(
                            {
                                "event_id": event_id,
                                "symbol": symbol,
                                "ex_date": day,
                                "unknown_fields": absent,
                            }
                        )
            else:
                raise ValueError("Unsupported retrieved category; quarantine before mapping")
            if symbol not in UNIVERSE or not day:
                raise ValueError("Unresolved prototype holdings role/action date")
            year = str(date.fromisoformat(day).year)
            fields = {
                k: field_evidence(record, k)
                for k in applicable
                + ("status", "first_published_at", "source_available_at", "effective_time_intraday")
            }
            for k in applicable:
                if k.endswith("date") and record.get(k) is not None:
                    date.fromisoformat(record[k])
            rows.append(
                {
                    "event_id": event_id,
                    "symbol": symbol,
                    "category": category,
                    "holdings_role": role,
                    "array_index": index,
                    "fields": fields,
                    "classification": classification,
                    "effective_boundary": "UNKNOWN",
                    "simulation_boundary": "INFERRED_FOR_SIMULATION_ONLY_IF_DECLARED",
                    "source_sha256": source_hash,
                    "retrieved_at": retrieved_at.isoformat(),
                    "historical_publication": "UNKNOWN",
                }
            )
            counts[category] += 1
            by_symbol[(symbol, category)] += 1
            by_year[(symbol, year, category)] += 1
    return {
        "rows": len(rows),
        "unique_ids": len(seen),
        "counts": dict(sorted(counts.items())),
        "by_symbol_type": [
            {"symbol": s, "category": c, "count": n} for (s, c), n in sorted(by_symbol.items())
        ],
        "by_symbol_year_type": [
            {"symbol": s, "year": y, "category": c, "count": n}
            for (s, y, c), n in sorted(by_year.items())
        ],
        "missing_dates": missing_dates,
        "events": rows,
        "source_truth": "SOURCE_PROVENANCE_QUALIFIED",
        "coverage": "Retrieved process-date-filtered archive only; not independent completeness",
    }


def normalize_action(
    record: Mapping,
    category: str,
    *,
    held_symbol: str,
    source: SourceEvidence,
    boundary: datetime,
    sequence: int,
    share_basis: str,
    post_split_basis: str | None = None,
    fractional_policy: str | None = None,
) -> Action:
    """Map supported issuer-side records with caller-declared boundary/share basis.

    Merger records are quarantined rather than converted. The caller must supply
    an exchange-session beginning on the reported ex-date; no calendar inferred.
    Dividend rate basis and split rounding are external evidence/assumptions.
    """
    aware(boundary)
    if record.get("id") != source.event_id or held_symbol not in UNIVERSE:
        raise ValueError("Event identity/held symbol mismatch")
    if category == "cash_mergers":
        if record.get("acquirer_symbol") == held_symbol:
            raise ValueError("ACQUIRER_ROLE_NO_SUPPORTED_HOLDINGS_TRANSFORMATION")
        raise ValueError("UNSUPPORTED_OR_AMBIGUOUS_MERGER_CONVERSION")
    if record.get("symbol") != held_symbol:
        raise ValueError("Explicit issuer holdings role required")
    ex_date = date.fromisoformat(record["ex_date"])
    if boundary.astimezone(ET).date() != ex_date:
        raise ValueError("Boundary must be on reported ex-date")
    if category == "forward_splits":
        old, new = number(record["old_rate"]), number(record["new_rate"])
        if old <= 0 or new <= 0:
            raise ValueError("Split components must be positive")
        return Action(
            source,
            held_symbol,
            "SPLIT",
            boundary,
            sequence,
            new / old,
            share_basis,
            post_split_basis,
            fractional_policy=fractional_policy,
        )
    if category == "cash_dividends":
        payable = record.get("payable_date")
        return Action(
            source,
            held_symbol,
            "DIVIDEND",
            boundary,
            sequence,
            number(record["rate"]),
            share_basis,
            payable_date=date.fromisoformat(payable) if payable is not None else None,
        )
    raise ValueError("Unsupported action category")


@dataclass(frozen=True)
class Position:
    symbol: str
    position_id: str
    quantity: Decimal
    held_since: datetime
    share_basis: str

    def __post_init__(self):
        if self.symbol not in UNIVERSE:
            raise ValueError("Unsupported symbol")
        identity(self.position_id)
        identity(self.share_basis)
        aware(self.held_since)
        object.__setattr__(self, "quantity", number(self.quantity))


@dataclass(frozen=True)
class DividendClaim:
    claim_id: str
    source: SourceEvidence
    position_id: str
    symbol: str
    entitled_at: datetime
    eligible_shares: Decimal
    rate: Decimal
    share_basis: str
    payable_date: date | None
    settled: bool = False

    def __post_init__(self):
        for value in (self.claim_id, self.position_id, self.share_basis):
            identity(value)
        aware(self.entitled_at)
        object.__setattr__(self, "eligible_shares", number(self.eligible_shares))
        object.__setattr__(self, "rate", number(self.rate))
        if self.rate < 0 or self.symbol not in UNIVERSE or type(self.settled) is not bool:
            raise ValueError("Invalid dividend claim")
        if self.payable_date is not None and (
            type(self.payable_date) is not date
            or self.payable_date < self.entitled_at.astimezone(ET).date()
        ):
            raise ValueError("Invalid claim payable date")

    @property
    def signed_amount(self) -> Decimal:
        return self.eligible_shares * self.rate


@dataclass(frozen=True)
class Account:
    cash: Decimal
    positions: tuple[Position, ...]
    as_of: datetime
    claims: tuple[DividendClaim, ...] = ()
    applied: tuple[tuple[str, str], ...] = ()
    last_action_key: tuple[datetime, int, str] | None = None
    unresolved_exits: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()

    def __post_init__(self):
        aware(self.as_of)
        object.__setattr__(self, "cash", number(self.cash))
        if not all(
            isinstance(v, tuple)
            for v in (
                self.positions,
                self.claims,
                self.applied,
                self.unresolved_exits,
                self.assumptions,
            )
        ):
            raise ValueError("Immutable tuples required")
        if len({p.symbol for p in self.positions}) != len(self.positions):
            raise ValueError("One net physical position per symbol required")
        if len({p.position_id for p in self.positions}) != len(self.positions):
            raise ValueError("Duplicate position identity")
        if any(p.held_since > self.as_of for p in self.positions):
            raise ValueError("Position opened after state timestamp")
        if len({c.claim_id for c in self.claims}) != len(self.claims):
            raise ValueError("Duplicate entitlement")
        if len(dict(self.applied)) != len(self.applied):
            raise ValueError("Duplicate applied action")


def apply_action(state: Account, action: Action) -> Account:
    """Apply once to current net physical shares; never creates an order or fee."""
    fingerprint = hashlib.sha256(repr(action).encode()).hexdigest()
    previous = dict(state.applied).get(action.source.event_id)
    if previous is not None:
        if previous != fingerprint:
            raise ValueError("Replayed action changed content/evidence")
        return state
    key = (action.boundary, action.sequence, action.source.event_id)
    if action.boundary < state.as_of or (state.last_action_key and key <= state.last_action_key):
        raise ValueError("Action ordering would rewind state")
    positions, claims = [], list(state.claims)
    for p in state.positions:
        if p.symbol != action.symbol or p.quantity == 0:
            positions.append(p)
            continue
        if p.held_since >= action.boundary:
            if action.kind == "SPLIT":
                raise ValueError("Position at/after split boundary has ambiguous basis")
            positions.append(p)
            continue
        if p.share_basis != action.share_basis:
            raise ValueError("Unproved action rate/share basis or split ordering")
        if action.kind == "SPLIT":
            quantity = p.quantity * action.amount
            if action.fractional_policy == "INTEGER_ONLY" and quantity != quantity.to_integral():
                raise ValueError("Fractional result requires explicit cash-in-lieu policy")
            positions.append(replace(p, quantity=quantity, share_basis=action.post_split_basis))
        else:
            positions.append(p)
            claims.append(
                DividendClaim(
                    action.source.event_id + ":" + p.position_id,
                    action.source,
                    p.position_id,
                    p.symbol,
                    action.boundary,
                    p.quantity,
                    action.amount,
                    p.share_basis,
                    action.payable_date,
                )
            )
    assumptions = set(state.assumptions) | {action.convention}
    if action.kind == "SPLIT" and action.fractional_policy == "EXACT_FRACTIONAL_ASSUMPTION":
        assumptions.add(action.fractional_policy)
    return replace(
        state,
        positions=tuple(positions),
        claims=tuple(claims),
        applied=state.applied + ((action.source.event_id, fingerprint),),
        as_of=action.boundary,
        last_action_key=key,
        assumptions=tuple(sorted(assumptions)),
    )


def apply_actions(state: Account, actions: tuple[Action, ...]) -> Account:
    """Deterministic declared ordering; simultaneous ties fail rather than infer."""
    unique = {}
    for action in actions:
        previous = unique.get(action.source.event_id)
        if previous is not None and previous != action:
            raise ValueError("Duplicate source identity with conflicting contents")
        unique[action.source.event_id] = action
    actions = tuple(unique.values())
    keys = [(a.boundary, a.sequence) for a in actions]
    if len(keys) != len(set(keys)):
        raise ValueError("Ambiguous simultaneous action ordering")
    for action in sorted(actions, key=lambda a: (a.boundary, a.sequence, a.source.event_id)):
        state = apply_action(state, action)
    return state


def settle_dividend(state: Account, claim_id: str, at: datetime) -> Account:
    """Transfer signed accrual to cash once, on/after retrieved payable date.

    Date-based simulated settlement is not verified broker payment timing.
    Unknown payment dates fail closed and leave the original claim outstanding.
    """
    aware(at)
    claim = next((c for c in state.claims if c.claim_id == claim_id), None)
    if claim is None:
        raise ValueError("Unknown entitlement identity")
    if claim.settled:
        return state
    if claim.payable_date is None:
        raise ValueError("UNKNOWN_PAYMENT_DATE: retain unsettled claim")
    if at < state.as_of or at.astimezone(ET).date() < claim.payable_date:
        raise ValueError("Settlement before state/payable date")
    return replace(
        state,
        cash=state.cash + claim.signed_amount,
        as_of=at,
        claims=tuple(
            replace(c, settled=True) if c.claim_id == claim_id else c for c in state.claims
        ),
        assumptions=tuple(sorted(set(state.assumptions) | {"PAYABLE_DATE_SETTLEMENT_ASSUMPTION"})),
    )


def retain_missing_exit(state: Account, symbol: str, at: datetime) -> Account:
    """Carry shares/claims unchanged when an exit is unavailable; no retry policy."""
    aware(at)
    if at < state.as_of or not any(p.symbol == symbol and p.quantity for p in state.positions):
        raise ValueError("Missing exit must refer to current outstanding exposure")
    return replace(
        state, as_of=at, unresolved_exits=tuple(sorted(set(state.unresolved_exits) | {symbol}))
    )


@dataclass(frozen=True)
class RawMark:
    symbol: str
    price: Decimal
    observation_at: datetime
    available_at: datetime
    share_basis: str
    source_id: str
    price_basis: str = "RAW"

    def __post_init__(self):
        aware(self.observation_at)
        aware(self.available_at)
        identity(self.source_id)
        identity(self.share_basis)
        object.__setattr__(self, "price", number(self.price))
        if self.price <= 0 or self.price_basis != "RAW" or self.symbol not in UNIVERSE:
            raise ValueError("Positive raw-share-basis mark required")
        if self.available_at < self.observation_at:
            raise ValueError("Mark available before observation")


def raw_price_from_split_adjusted(price: object, raw_per_adjusted: object) -> Decimal:
    """Explicit conversion boundary; caller must prove the source factor/version."""
    price, factor = number(price), number(raw_per_adjusted)
    if price <= 0 or factor <= 0:
        raise ValueError("Positive price and proven conversion factor required")
    return price * factor


def snapshot(state: Account, marks: tuple[RawMark, ...], at: datetime) -> dict:
    """Cash-only and accrual-inclusive statements; absent marks yield incomplete NAV.

    A permitted stale mark is disclosed by timestamp/age, not a current fill.
    Raw share basis prevents a pre-split mark valuing post-split shares.
    """
    aware(at)
    if at < state.as_of:
        raise ValueError("Snapshot cannot rewind current accounting state")
    if len({m.symbol for m in marks}) != len(marks):
        raise ValueError("Duplicate valuation mark")
    lookup = {m.symbol: m for m in marks}
    long_assets = short_liability = Decimal(0)
    missing, used = [], []
    for p in state.positions:
        if not p.quantity:
            continue
        mark = lookup.get(p.symbol)
        if mark is None:
            missing.append(p.symbol)
            continue
        if mark.available_at > at or mark.observation_at > at:
            raise ValueError("Future valuation mark")
        if mark.share_basis != p.share_basis:
            raise ValueError("Raw price/share basis mismatch")
        value = p.quantity * mark.price
        long_assets += max(value, Decimal(0))
        short_liability += max(-value, Decimal(0))
        used.append(
            {
                "symbol": p.symbol,
                "source_id": mark.source_id,
                "observation_at": mark.observation_at.isoformat(),
                "available_at": mark.available_at.isoformat(),
                "age_seconds": (at - mark.observation_at).total_seconds(),
            }
        )
    pending = [c for c in state.claims if not c.settled]
    receivables = sum((max(c.signed_amount, Decimal(0)) for c in pending), Decimal(0))
    liabilities = sum((max(-c.signed_amount, Decimal(0)) for c in pending), Decimal(0))
    cash_nav = None if missing else state.cash + long_assets - short_liability
    unknown = [c.claim_id for c in pending if c.payable_date is None]
    return {
        "cash": state.cash,
        "long_assets": None if missing else long_assets,
        "short_liability": None if missing else short_liability,
        "receivables": receivables,
        "dividend_liabilities": liabilities,
        "cash_only_equity": cash_nav,
        # cash_nav is a Decimal on this same not-missing branch.
        "accrual_equity": None if missing else cast(Decimal, cash_nav) + receivables - liabilities,
        "status": "INCOMPLETE" if missing else "ASSUMPTION_DEPENDENT",
        "paid_cash_scope": "INCOMPLETE" if unknown else "MODELED_PAYABLE_DATES",
        "unknown_payment_claims": unknown,
        "missing_marks": missing,
        "unresolved_exits": list(state.unresolved_exits),
        "marks": used,
        "assumptions": list(state.assumptions),
        "research_ready": False,
    }
