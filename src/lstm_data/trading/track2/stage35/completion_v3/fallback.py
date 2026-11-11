"""Frozen conditional ordinary rules B-F; never overrides a supported field.

Yield proxy is a standalone sensitivity overlay, never a factual dividend event
or input to forecasts, eligibility, prices or pretrade NAV.
"""

from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal
from functools import lru_cache

import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

from ...stage012.calendar_schedule import MarketClock
from .actions import Action, Truth, identifier

D = Decimal
POLICY_ID = "ORDINARY_DIVIDEND_V3_1"
SCENARIOS = (
    "OBSERVED_ACTION_BASE",
    "CONDITIONAL_ORDINARY_IMPUTED",
    "LOW_DIVIDEND_SENSITIVITY",
    "HIGH_DIVIDEND_SENSITIVITY",
    "UNRESOLVED",
)


@lru_cache(maxsize=1)
def trading_days() -> frozenset[date]:
    clock = MarketClock("2010-01-01", "2025-12-31")
    return frozenset(date.fromisoformat(str(d)[:10]) for d in clock.calendar.index)


@lru_cache(maxsize=1)
def bank_holidays() -> frozenset[date]:
    return frozenset(
        date.fromisoformat(str(stamp)[:10])
        for stamp in USFederalHolidayCalendar().holidays(
            datetime(2010, 1, 1), datetime(2027, 12, 31)
        )
    )


def bank_day(day: date) -> bool:
    return day.weekday() < 5 and day not in bank_holidays()


def settlement_day(day: date) -> bool:
    return day in trading_days() and bank_day(day)


def shift_business(day: date, amount: int) -> date:
    direction = 1 if amount > 0 else -1
    for _ in range(abs(amount)):
        day += timedelta(days=direction)
        while not settlement_day(day):
            day += timedelta(days=direction)
    return day


def ex_from_record(record: date, ordinary: bool = True) -> date:
    if not ordinary or not settlement_day(record):
        raise ValueError("RECORD_OR_SPECIAL_EXDATE_HOLD")
    return record if record >= date(2024, 5, 29) else shift_business(record, -1)


def assumed_pay(ex: date, lag: int = 30) -> date:
    if lag not in (14, 30, 45):
        raise ValueError("UNREVIEWED_PAY_LAG")
    day = ex + timedelta(days=lag)
    while not bank_day(day):
        day += timedelta(days=1)
    return day


def complete_ordinary(event: Action, *, pay_lag: int = 30, ex_shift: int = 0) -> Action:
    """B/C only. A fully supported field is immutable, even under stress selection."""
    if (
        event.action_type != "CASH_DIVIDEND"
        or event.special
        or event.status in (Truth.CONFLICTED_HOLD, Truth.SPECIAL_ACTION_HOLD)
    ):
        raise ValueError("ORDINARY_FALLBACK_EXCLUDES_SPECIAL")
    if ex_shift not in (-1, 0, 1):
        raise ValueError("UNREVIEWED_EXDATE_STRESS")
    ex = event.ex_date
    pay = event.payable_date
    fields = list(event.inferred_fields)
    rules = []
    params = list(event.assumption_params)
    if ex is None:
        if event.record_date is None:
            raise ValueError("EVENT_CALENDAR_UNKNOWN")
        ex = shift_business(ex_from_record(event.record_date), ex_shift)
        fields.append("ex_date")
        rules.append("B_SETTLEMENT_CYCLE_EXDATE")
        params.append(("record_date", event.record_date.isoformat()))
        params.append(("ex_shift_business_days", str(ex_shift)))
    if pay is None:
        pay = assumed_pay(ex, pay_lag)
        fields.append("payable_date")
        rules.append("C_ASSUMED_PAY_DATE_" + str(pay_lag) + "D")
        params.append(("calendar_lag", str(pay_lag)))
    if not rules:
        return event
    result = replace(
        event,
        ex_date=ex,
        effective_date=ex,
        payable_date=pay,
        status=Truth.ASSUMED_ORDINARY,
        inferred_fields=tuple(fields),
        assumption_rule_id=POLICY_ID + ":" + ",".join(rules),
        assumption_params=tuple(params),
        confidence="CONDITIONAL_NOT_VERIFIED_HISTORY",
    )
    result.validate()
    return result


def carry_amount(
    event: Action,
    history: tuple[Action, ...],
    asof: date,
    *,
    interval_months: int,
    regular_series_evidence: str,
    known_splits: tuple[Action, ...] = (),
    factor: Decimal = D(1),
) -> Action:
    if event.amount is not None:
        return event
    if not regular_series_evidence:
        raise ValueError("REGULAR_SERIES_EVIDENCE_REQUIRED")
    if event.special or event.action_type != "CASH_DIVIDEND" or interval_months not in (1, 3):
        raise ValueError("REGULAR_SERIES_NOT_ESTABLISHED")
    cutoff = event.ex_date or asof
    if cutoff > asof:
        raise ValueError("EVENT_AFTER_REFERENCE_FRONTIER")
    previous = sorted(
        (
            r
            for r in history
            if r.symbol == event.symbol
            and r.ex_date is not None
            and r.ex_date < cutoff
            and r.ex_date <= asof
            and r.amount is not None
            and r.status in (Truth.VERIFIED_PRIMARY, Truth.VERIFIED_MULTI_SOURCE)
            and not r.special
            and (r.declared_at is None or r.declared_at <= asof)
        ),
        key=lambda r: r.ex_date or date.min,
    )
    if not previous:
        raise ValueError("NO_VERIFIED_PAST_AMOUNT")
    last = previous[-1]
    if last.ex_date is None or last.amount is None:
        raise ValueError("REFERENCE_FIELDS")
    stale = pd.Timestamp(last.ex_date) + pd.DateOffset(months=2 * interval_months)
    if pd.Timestamp(cutoff) > stale:
        raise ValueError("AMOUNT_REFERENCE_STALE_TWO_INTERVALS")
    amount = last.amount
    for split in known_splits:
        effective = split.effective_date or split.ex_date
        if split.symbol == event.symbol and effective and last.ex_date < effective <= cutoff:
            if (
                split.status not in (Truth.VERIFIED_PRIMARY, Truth.VERIFIED_MULTI_SOURCE)
                or split.split_ratio_new_old is None
                or split.declared_at is not None
                and split.declared_at > asof
            ):
                raise ValueError("SPLIT_CONVERSION_NOT_KNOWN")
            amount /= split.split_ratio_new_old
    if factor not in (D(0), D(1), D("1.5")):
        raise ValueError("UNREVIEWED_AMOUNT_STRESS")
    result = replace(
        event,
        amount=amount * factor,
        status=Truth.ASSUMED_ORDINARY,
        inferred_fields=event.inferred_fields + ("amount_per_share_raw_basis",),
        assumption_rule_id=POLICY_ID + ":D_ASSUMED_REGULAR_AMOUNT_CARRY_FORWARD",
        assumption_params=event.assumption_params
        + (
            ("regular_series_evidence", regular_series_evidence),
            ("reference_event", last.event_id),
            ("reference_cutoff", asof.isoformat()),
            ("interval_months", str(interval_months)),
            ("factor", str(factor)),
        ),
        confidence="CONDITIONAL_NOT_VERIFIED_HISTORY",
    )
    result.validate()
    return result


def recurring_candidates(
    symbol: str,
    history: tuple[Action, ...],
    start: date,
    stop: date,
    *,
    interval_months: int,
    payer_evidence: str,
    suspension_known_at: date | None = None,
) -> tuple[Action, ...]:
    if interval_months not in (1, 3) or not payer_evidence:
        raise ValueError("PAYER_CADENCE_NOT_ESTABLISHED")
    # Freeze reference strictly before the proposed missing-event interval. Later
    # observations cannot determine earlier existence or amounts.
    prior = tuple(
        r
        for r in history
        if r.symbol == symbol
        and r.ex_date
        and r.ex_date < start
        and r.status in (Truth.VERIFIED_PRIMARY, Truth.VERIFIED_MULTI_SOURCE)
        and not r.special
    )
    if len(prior) < 2:
        raise ValueError("TWO_VERIFIED_PRIOR_PAYOUTS_REQUIRED")
    last = max(prior, key=lambda r: r.ex_date or date.min)
    if last.ex_date is None:
        raise ValueError("LAST_REFERENCE")
    result = []
    for step in (1, 2):
        at = date.fromisoformat(
            str(pd.Timestamp(last.ex_date) + pd.DateOffset(months=step * interval_months))[:10]
        )
        while at not in trading_days():
            at += timedelta(days=1)
        if at < start or at > stop:
            continue
        if suspension_known_at is not None and suspension_known_at <= at:
            continue
        event = Action(
            identifier(symbol, "CASH_DIVIDEND", at, None),
            symbol,
            "CASH_DIVIDEND",
            at,
            None,
            None,
            None,
            Truth.ASSUMED_ORDINARY,
            last.sources,
            sub_type="ASSUMED_REGULAR_ORDINARY",
            inferred_fields=("event_existence", "ex_date"),
            assumption_rule_id=POLICY_ID + ":E_ASSUMED_RECURRING_EVENT",
            assumption_params=(("payer_evidence", payer_evidence),),
        )
        try:
            event = carry_amount(
                event,
                prior,
                at,
                interval_months=interval_months,
                regular_series_evidence=payer_evidence,
            )
        except ValueError as exc:
            if str(exc) == "AMOUNT_REFERENCE_STALE_TWO_INTERVALS":
                continue
            raise
        result.append(
            replace(
                complete_ordinary(event),
                assumption_rule_id=POLICY_ID + ":E_RECURRING+D_CARRY+C_PAY30",
            )
        )
    return tuple(result)


def yield_proxy_adjustment(
    signed_notional: Decimal,
    elapsed_seconds: Decimal,
    *,
    annual_rate: Decimal = D(".015"),
    verified_distribution_overlap: bool = False,
    verified_nonpayer: bool = False,
) -> Decimal:
    """Standalone F sensitivity only. Caller supplies an explicit as-of exposure.

    Never booked as a corporate action or as pretrade cash/NAV; cannot double-pay
    an interval already represented by actual cash events or a verified zero.
    """
    if annual_rate not in (D(0), D(".015"), D(".03")) or elapsed_seconds < 0:
        raise ValueError("PROXY_RECIPE")
    if verified_distribution_overlap or verified_nonpayer:
        return D(0)
    return signed_notional * annual_rate * elapsed_seconds / D(365 * 86400)
