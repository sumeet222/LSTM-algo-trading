"""Raw-share/action contracts and due events. Unknown economics remain unresolved."""

from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal

from ...stage012.contracts import utc
from .. import corporate_actions as actions
from ..common import RAW, D, Price
from .settlement import UndatedClaim, V2Book, carry_to


@dataclass(frozen=True)
class RawObservation:
    ticker: str
    at: datetime
    complete: datetime
    available: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    basis: str
    source_hash: str
    vintage: str
    status: str = "VALID"

    def validate(self) -> None:
        for stamp in (self.at, self.complete, self.available):
            utc(stamp)
        if not self.at < self.complete <= self.available or self.basis != RAW:
            raise ValueError("RAW_SHARE_BASIS_OR_TIME")
        if (
            not all(
                v.is_finite() for v in (self.open, self.high, self.low, self.close, self.volume)
            )
            or min(self.open, self.high, self.low, self.close) <= 0
            or self.volume < 0
            or not self.low <= min(self.open, self.close) <= max(self.open, self.close) <= self.high
            or self.status != "VALID"
            or self.vintage != "ORIGINAL_OBSERVED"
            or not self.source_hash
        ):
            raise ValueError("RAW_OHLCV_INVALID_OR_UNRESOLVED_CORRECTION")


@dataclass(frozen=True)
class ActionEvent:
    action_id: str
    ticker: str
    kind: str
    effective: datetime
    available: datetime
    source_hash: str
    amount: Decimal | None = None
    pay_at: datetime | None = None
    ratio: Decimal | None = None
    point_in_time_certified: bool = False
    status: str = "VERIFIED_RETROSPECTIVE"

    def economic_ready(self) -> bool:
        return bool(
            self.source_hash
            and self.status in ("VERIFIED_RETROSPECTIVE", "SYNTHETIC_KNOWN")
            and (
                self.kind == "SPLIT"
                and self.ratio is not None
                and self.ratio > 0
                or self.kind == "DIVIDEND"
                and self.amount is not None
                and self.amount >= 0
                and self.pay_at is not None
                and self.pay_at >= self.effective
            )
        )


@dataclass(frozen=True)
class DueEvent:
    effective: datetime
    priority: int
    event_id: str
    kind: str
    ticker: str
    action: ActionEvent | None = None


def due_events(
    actions_tape: tuple[ActionEvent, ...],
    start: datetime,
    end: datetime,
    short_tickers: tuple[str, ...],
) -> tuple[DueEvent, ...]:
    result = []
    for action in actions_tape:
        if start < action.effective <= end:
            result.append(
                DueEvent(
                    action.effective,
                    1,
                    action.action_id + ":EFFECTIVE",
                    action.kind,
                    action.ticker,
                    action,
                )
            )
        if action.pay_at is not None and start < action.pay_at <= end:
            result.append(
                DueEvent(
                    action.pay_at,
                    2,
                    action.action_id + ":PAY",
                    "DIVIDEND_PAY",
                    action.ticker,
                    action,
                )
            )
    result.extend(
        DueEvent(end, 0, "BORROW:" + t + ":" + end.isoformat(), "BORROW", t) for t in short_tickers
    )
    return tuple(sorted(result, key=lambda e: (e.effective, e.priority, e.event_id)))


def apply_due(
    book: V2Book, event: DueEvent, point: Price, posted: datetime, rate: Decimal | None = D(".02")
) -> V2Book:
    if point.at != event.effective:
        raise ValueError("DUE_EVENT_PRICE_TIME_MISMATCH")
    if event.kind == "BORROW":
        return carry_to(book, event.ticker, event.effective, rate, posted, event.event_id)
    action = event.action
    if (
        action is not None
        and event.kind == "DIVIDEND"
        and action.pay_at is None
        and action.amount is not None
        and action.amount.is_finite()
        and action.amount >= 0
        and action.available <= action.effective <= posted
        and action.status in ("VERIFIED_RETROSPECTIVE", "SYNTHETIC_KNOWN")
        and action.source_hash
    ):
        if action.action_id + ":EX" in book.action_keys:
            raise ValueError("DUPLICATE_ACTION")
        claims = tuple(
            UndatedClaim(action.action_id, lot.cohort.cohort_id, lot.quantity * action.amount)
            for lot in book.lots
            if lot.cohort.ticker == event.ticker and lot.quantity
        )
        by_id = {claim.cohort_id: claim.amount for claim in claims}
        lots = tuple(
            replace(lot, accrual=lot.accrual + by_id.get(lot.cohort.cohort_id, D(0)))
            for lot in book.lots
        )
        marks = dict(book.marks)
        marks[event.ticker] = point
        new = replace(
            book,
            lots=lots,
            marks=tuple(sorted(marks.items())),
            undated_claims=book.undated_claims + claims,
            action_keys=book.action_keys + (action.action_id + ":EX",),
            unresolved=book.unresolved + ("PAY_DATE_UNKNOWN:" + action.action_id,),
        )
        return book.commit(
            new,
            event.event_id,
            point,
            posted,
            "DIVIDEND_EX_PAY_DATE_UNKNOWN",
            event.ticker,
            amount=sum(by_id.values(), D(0)),
        )
    if (
        action is None
        or action.available > posted
        or not action.economic_ready()
        or action.available > action.effective
    ):
        # Preserve inventory and claims; never invent an economic value/date.
        return book.commit(
            replace(book, unresolved=book.unresolved + (event.event_id,)),
            event.event_id,
            point,
            posted,
            "ACTION_UNRESOLVED",
            event.ticker,
        )
    result: object
    if event.kind == "SPLIT":
        if action.ratio is None:
            raise ValueError("SPLIT_RATIO")
        result = actions.split(
            book,
            action.action_id,
            event.ticker,
            action.ratio,
            point,
            posted,
            action.available,
        )
    elif event.kind == "DIVIDEND":
        if action.amount is None or action.pay_at is None:
            raise ValueError("DIVIDEND_AMOUNT_PAY")
        div = actions.Dividend(
            action.action_id,
            event.ticker,
            action.amount,
            action.available,
            action.effective,
            action.pay_at,
        )
        result = actions.ex_dividend(book, div, point, posted)
    elif event.kind == "DIVIDEND_PAY":
        result = actions.pay_dividend(book, action.action_id, point, posted)
    else:
        raise ValueError("SPECIAL_ACTION_UNRESOLVED")
    if not isinstance(result, V2Book):
        raise AssertionError("V2_ACTION_STATE")
    if event.kind == "SPLIT" and any(
        p.ticker == event.ticker and p.quantity != p.quantity.to_integral_value()
        for p in result.positions
    ):
        result = result.commit(
            replace(
                result, unresolved=result.unresolved + (event.event_id + ":CIL_REFERENCE_UNKNOWN",)
            ),
            event.event_id + ":CIL",
            point,
            posted,
            "CASH_IN_LIEU_UNRESOLVED",
            event.ticker,
        )
    return result


@dataclass(frozen=True)
class BorrowStressEvent:
    ticker: str
    session: str
    kind: str
    seed: int
    scenario_id: str


def fixed_short_stress(
    tickers: tuple[str, ...],
    sessions: tuple[str, ...],
    *,
    seed: int,
    reject_per_million: int,
    recall_per_million: int,
) -> tuple[BorrowStressEvent, ...]:
    """Explicit caller probabilities; no implicit historical availability assumption.

    Pure calendar/symbol hash, invariant to enumeration order and any price/profit data.
    Results are scenario instructions, not a locate provider or empirical frequencies.
    """
    import hashlib

    if (
        min(reject_per_million, recall_per_million) < 0
        or reject_per_million + recall_per_million > 1_000_000
    ):
        raise ValueError("STRESS_PROBABILITIES")
    result = []
    for ticker in sorted(set(tickers)):
        for day in sorted(set(sessions)):
            draw = (
                int(hashlib.sha256(f"{seed}|{ticker}|{day}".encode()).hexdigest(), 16) % 1_000_000
            )
            kind = (
                "REJECT"
                if draw < reject_per_million
                else "RECALL_BUY_IN"
                if draw < reject_per_million + recall_per_million
                else ""
            )
            if kind:
                result.append(
                    BorrowStressEvent(ticker, day, kind, seed, "CONDITIONAL_SCENARIO_NOT_OBSERVED")
                )
    return tuple(result)
