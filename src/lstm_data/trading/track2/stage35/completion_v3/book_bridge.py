"""Non-price corporate-action transactions for the existing reconciled V2 book.

No invented midnight quote is needed to recognize/pay a cash claim. Historical
usage requires an independently verified financial release; fabricated fixtures
must carry synthetic:// source evidence, not an arbitrary source-type flag.
"""

from dataclasses import replace
from datetime import datetime
from decimal import Decimal

from ..accounting import CashClaim, Journal
from ..common import RAW, ZERO
from ..completion_v2.release import VerifiedRelease
from ..completion_v2.settlement import UndatedClaim, V2Book
from .actions import Action, Truth
from .event_ledger import sha
from .tapes import TapeEvent, midnight


def guard(action: Action, release: VerifiedRelease | None) -> None:
    if not action.sources:
        raise PermissionError("ACTION_EVIDENCE_REQUIRED")
    synthetic = all(
        s.endpoint.startswith("synthetic://") and s.source_id.startswith("SYNTHETIC:")
        for s in action.sources
    )
    if not synthetic and release is None:
        raise PermissionError("SIGNED_HISTORICAL_FINANCIAL_RELEASE_REQUIRED")
    action.validate()


def post(
    book: V2Book, new: V2Book, event: TapeEvent, posted: datetime, amount: Decimal = ZERO
) -> V2Book:
    if event.available_at > posted or event.effective_at > event.available_at:
        raise ValueError("ACTION_BOOK_CLOCK_INVERSION")
    if book.journal and (
        posted < book.journal[-1].processed_at or event.effective_at < book.journal[-1].event_time
    ):
        raise ValueError("LATE_ACTION_REPLAY_REQUIRED")
    new.reconcile()
    details = (
        ("truth", event.truth),
        ("source_hash", event.source_hash),
        ("availability_rule", event.simulation_availability_rule),
        ("action", str(event.action.record()) if event.action else ""),
    )
    receipt = Journal(
        event.event_id,
        event.effective_at,
        event.effective_at,
        event.available_at,
        posted,
        event.kind,
        event.symbol,
        "USD",
        RAW,
        (),
        amount,
        book.digest(),
        new.digest(),
        None,
        details,
    )
    return replace(new, journal=book.journal + (receipt,))


def apply_action(
    book: V2Book, event: TapeEvent, posted: datetime, release: VerifiedRelease | None = None
) -> V2Book:
    action = event.action
    if action is None:
        raise ValueError("ACTION_RECORD_REQUIRED")
    guard(action, release)
    prior = next((j for j in book.journal if j.journal_id == event.event_id), None)
    if prior is not None:
        if dict(prior.details).get("source_hash") != event.source_hash:
            raise ValueError("CORRECTED_ACTION_REPLAY_REQUIRED")
        return book
    amount = ZERO
    held = tuple(lot for lot in book.lots if lot.cohort.ticker == action.symbol)
    if action.status in (Truth.SPECIAL_ACTION_HOLD, Truth.CONFLICTED_HOLD, Truth.UNKNOWN):
        # Keep all existing positions and obligations. No invented OGN value or CIL.
        new = replace(book, unresolved=book.unresolved + (action.event_id + ":ACTION_HOLD",))
    elif event.kind == "CASH_SETTLEMENT":
        claims = tuple(c for c in book.claims if c.action_id == action.event_id)
        if not claims:
            # No entitlement is not the same as unavailable action evidence.
            if action.event_id + ":EX" not in book.action_keys:
                raise ValueError("PAY_WITHOUT_REPLAYED_EX_ENTITLEMENT")
            new = book
        else:
            if any(c.due_at > event.effective_at for c in claims):
                raise ValueError("PAY_BEFORE_DUE")
            by_lot = {c.cohort_id: c.amount for c in claims}
            amount = sum(by_lot.values(), ZERO)
            if amount < 0 and book.cash - book.restricted() < -amount:
                new = replace(
                    book, unresolved=book.unresolved + (action.event_id + ":PAY_FUNDING_HOLD",)
                )
                amount = ZERO
            else:
                lots = tuple(
                    replace(
                        lot,
                        cash=lot.cash + by_lot.get(lot.cohort.cohort_id, ZERO),
                        nontrade_cash=lot.nontrade_cash + by_lot.get(lot.cohort.cohort_id, ZERO),
                        accrual=lot.accrual - by_lot.get(lot.cohort.cohort_id, ZERO),
                    )
                    for lot in book.lots
                )
                new = replace(
                    book,
                    cash=book.cash + amount,
                    lots=lots,
                    claims=tuple(c for c in book.claims if c not in claims),
                    action_keys=book.action_keys + (action.event_id + ":PAY",),
                )
    elif event.kind == "CASH_DIVIDEND":
        if action.amount is None or action.special:
            raise ValueError("ORDINARY_CASH_AMOUNT_REQUIRED")
        by_lot = {
            lot.cohort.cohort_id: lot.quantity * action.amount for lot in held if lot.quantity
        }
        amount = sum(by_lot.values(), ZERO)
        lots = tuple(
            replace(lot, accrual=lot.accrual + by_lot.get(lot.cohort.cohort_id, ZERO))
            for lot in book.lots
        )
        if action.payable_date:
            due = midnight(action.payable_date)
            claims = tuple(
                CashClaim(action.event_id, key, value, due) for key, value in sorted(by_lot.items())
            )
            new = replace(
                book,
                lots=lots,
                claims=book.claims + claims,
                action_keys=book.action_keys + (action.event_id + ":EX",),
            )
        else:
            undated = tuple(
                UndatedClaim(action.event_id, key, value) for key, value in sorted(by_lot.items())
            )
            new = replace(
                book,
                lots=lots,
                undated_claims=book.undated_claims + undated,
                action_keys=book.action_keys + (action.event_id + ":EX",),
                unresolved=book.unresolved + (action.event_id + ":PAY_UNKNOWN",),
            )
    elif event.kind == "SPLIT":
        ratio = action.split_ratio_new_old
        if ratio is None or not ratio.is_finite() or ratio <= 0:
            raise ValueError("SPLIT_RATIO_REQUIRED")
        lots = tuple(
            replace(
                lot,
                quantity=lot.quantity * ratio,
                basis=lot.basis / ratio,
                pending=(lot.pending * ratio).to_integral_value(rounding="ROUND_DOWN"),
                unit_factor=lot.unit_factor * ratio,
            )
            if lot.cohort.ticker == action.symbol
            else lot
            for lot in book.lots
        )
        positions = tuple(
            replace(p, quantity=p.quantity * ratio, basis=p.basis / ratio)
            if p.ticker == action.symbol
            else p
            for p in book.positions
        )
        # Unit conversion of an OLD known mark is explicit; its old timestamp stays
        # stale. This is not a newly observed quote or model-adjusted economic price.
        marks = tuple(
            (
                ticker,
                replace(
                    point,
                    value=point.value / ratio,
                    available_at=max(point.available_at, event.available_at),
                    source_id=point.source_id + "|SPLIT:" + action.event_id,
                ),
            )
            if ticker == action.symbol
            else (ticker, point)
            for ticker, point in book.marks
        )
        fractional = any(
            p.ticker == action.symbol and p.quantity != p.quantity.to_integral_value()
            for p in positions
        )
        new = replace(
            book,
            lots=lots,
            positions=positions,
            marks=marks,
            action_keys=book.action_keys + (action.event_id,),
            unresolved=book.unresolved
            + ((action.event_id + ":CIL_UNPRICED",) if fractional else ()),
        )
    elif action.effect_on_books.startswith("NO_"):
        new = book
    else:
        new = replace(book, unresolved=book.unresolved + (action.event_id + ":UNSUPPORTED_ACTION",))
    return post(book, new, event, posted, amount)


def bound_action_hash(action: Action) -> str:
    return sha(action.record())
