"""Synthetic raw-share actions; uncertain historical action basis remains gated."""

from dataclasses import dataclass, replace
from datetime import datetime
from decimal import ROUND_DOWN, Decimal

from .accounting import Book, CashClaim
from .borrow_financing import calendar_charge
from .common import ZERO, D, Price


@dataclass(frozen=True)
class Dividend:
    action_id: str
    ticker: str
    per_share: Decimal
    known_at: datetime
    ex_at: datetime
    pay_at: datetime


def ex_dividend(book: Book, event: Dividend, point: Price, processed: datetime) -> Book:
    if event.action_id + ":EX" in book.action_keys:
        raise ValueError("DUPLICATE_ACTION")
    if (
        event.known_at > event.ex_at
        or point.at != event.ex_at
        or event.pay_at < event.ex_at
        or event.per_share < 0
    ):
        raise ValueError("DIVIDEND_TIMING_UNKNOWN")
    claims = tuple(
        CashClaim(
            event.action_id,
            lot_item.cohort.cohort_id,
            lot_item.quantity * event.per_share,
            event.pay_at,
        )
        for lot_item in book.lots
        if lot_item.cohort.ticker == event.ticker and lot_item.quantity
    )
    amounts = {c.cohort_id: c.amount for c in claims}
    marks = dict(book.marks)
    marks[event.ticker] = point
    lots = tuple(
        replace(lot_item, accrual=lot_item.accrual + amounts.get(lot_item.cohort.cohort_id, ZERO))
        for lot_item in book.lots
    )
    new = replace(
        book,
        lots=lots,
        marks=tuple(sorted(marks.items())),
        claims=book.claims + claims,
        action_keys=book.action_keys + (event.action_id + ":EX",),
    )
    return book.commit(
        new,
        event.action_id + ":EX",
        point,
        processed,
        "DIVIDEND_EX",
        event.ticker,
        amount=sum(amounts.values(), ZERO),
        details=(("dividend", str(event)), ("entitlements", str(claims))),
    )


def pay_dividend(book: Book, action_id: str, point: Price, processed: datetime) -> Book:
    if action_id + ":PAY" in book.action_keys:
        raise ValueError("DUPLICATE_ACTION")
    claims = tuple(c for c in book.claims if c.action_id == action_id)
    if not claims or any(c.due_at > point.at for c in claims):
        raise ValueError("DIVIDEND_NOT_DUE")
    amounts = {c.cohort_id: c.amount for c in claims}
    total = sum(amounts.values(), ZERO)
    if total < 0 and book.cash - book.restricted() < -total:
        raise ValueError("DIVIDEND_FUNDING_UNRESOLVED")
    lots = tuple(
        replace(
            lot_item,
            cash=lot_item.cash + amounts.get(lot_item.cohort.cohort_id, ZERO),
            nontrade_cash=lot_item.nontrade_cash + amounts.get(lot_item.cohort.cohort_id, ZERO),
            accrual=lot_item.accrual - amounts.get(lot_item.cohort.cohort_id, ZERO),
        )
        for lot_item in book.lots
    )
    new = replace(
        book,
        cash=book.cash + total,
        lots=lots,
        claims=tuple(c for c in book.claims if c.action_id != action_id),
        action_keys=book.action_keys + (action_id + ":PAY",),
    )
    return book.commit(
        new,
        action_id + ":PAY",
        point,
        processed,
        "DIVIDEND_PAY",
        "MULTI",
        amount=total,
        details=(("action_id", action_id), ("claims_paid", str(claims))),
    )


def split(
    book: Book,
    action_id: str,
    ticker: str,
    ratio: Decimal,
    point: Price,
    processed: datetime,
    known_at: datetime,
    cash_in_lieu: bool = False,
) -> Book:
    if action_id in book.action_keys:
        raise ValueError("DUPLICATE_ACTION")
    if not ratio.is_finite() or ratio <= 0 or known_at > point.at:
        raise ValueError("SPLIT_POLICY_UNKNOWN")
    lots = {lot_item.cohort.cohort_id: lot_item for lot_item in book.lots}
    positions = {p.ticker: p for p in book.positions}
    if ticker not in positions:
        raise ValueError("SPLIT_POSITION_UNKNOWN")
    for key, lot_item in list(lots.items()):
        if lot_item.cohort.ticker == ticker:
            pending = (lot_item.pending * ratio).to_integral_value(rounding=ROUND_DOWN)
            lots[key] = replace(
                lot_item,
                quantity=lot_item.quantity * ratio,
                basis=lot_item.basis / ratio,
                pending=pending,
                unit_factor=lot_item.unit_factor * ratio,
            )
    p = positions[ticker]
    p = replace(p, quantity=p.quantity * ratio, basis=p.basis / ratio)
    cash = ZERO
    if cash_in_lieu:
        remainder = p.quantity - p.quantity.to_integral_value(rounding=ROUND_DOWN)
        left = remainder
        for key, lot_item in sorted(lots.items()):
            if lot_item.cohort.ticker != ticker or lot_item.quantity * left <= 0:
                continue
            part = min(abs(left), abs(lot_item.quantity)) * (D(1) if left > 0 else D(-1))
            q = lot_item.quantity - part
            money = part * point.value
            lots[key] = replace(
                lot_item,
                quantity=q,
                basis=lot_item.basis if q else ZERO,
                cash=lot_item.cash + money,
                realized=lot_item.realized + part * (point.value - lot_item.basis),
                closed=not q and not lot_item.pending,
            )
            cash += money
            left -= part
            if not left:
                break
        if left:
            raise AssertionError("CASH_IN_LIEU_ALLOCATION")
        p = replace(
            p,
            quantity=p.quantity - remainder,
            realized=p.realized + remainder * (point.value - p.basis),
            basis=p.basis if p.quantity - remainder else ZERO,
        )
    positions[ticker] = p
    marks = dict(book.marks)
    marks[ticker] = point
    new = replace(
        book,
        cash=book.cash + cash,
        lots=tuple(lots[k] for k in sorted(lots)),
        positions=tuple(positions[k] for k in sorted(positions)),
        marks=tuple(sorted(marks.items())),
        action_keys=book.action_keys + (action_id,),
    )
    return book.commit(
        new,
        action_id,
        point,
        processed,
        "SPLIT",
        ticker,
        amount=cash,
        details=(
            ("ratio", str(ratio)),
            ("known_at", known_at.isoformat()),
            ("cash_in_lieu", str(cash_in_lieu)),
        ),
    )


def financing(
    book: Book,
    journal_id: str,
    cohort_id: str,
    notional: Decimal,
    rate: Decimal,
    start: datetime,
    point: Price,
    processed: datetime,
) -> Book:
    charge = calendar_charge(notional, rate, start, point.at)
    lots = tuple(
        replace(lot_item, accrual=lot_item.accrual - charge)
        if lot_item.cohort.cohort_id == cohort_id
        else lot_item
        for lot_item in book.lots
    )
    if not any(lot_item.cohort.cohort_id == cohort_id for lot_item in lots):
        raise ValueError("UNKNOWN_COHORT")
    return book.commit(
        replace(book, lots=lots),
        journal_id,
        point,
        processed,
        "FINANCING_ACCRUAL",
        "MULTI",
        amount=-charge,
        details=(
            ("cohort", cohort_id),
            ("rate", str(rate)),
            ("notional", str(notional)),
            ("from", start.isoformat()),
        ),
    )
