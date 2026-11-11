"""Live invariant witnesses; release status cannot replace these calculations."""

from dataclasses import replace
from decimal import Decimal

import numpy as np

from ...stage012.calendar_schedule import MarketClock
from .book import Account, Lot, Order, Request
from .checkpoint import seal, unseal
from .protocol import Scenario
from .special import EX, OGNQuote, distribution, observe, pay_cil

D = Decimal


def engineering_witnesses() -> dict[str, bool]:
    """Small fabricated book, deliberately independent of historical prices."""
    a = Account("EQUAL", "FABRICATED_CERTIFICATION", Scenario())
    a.prices[0] = D(100)
    for key, qty in (("old", 10), ("new", -6)):
        a.lots[key] = Lot(key, 0, 0, 240, 10, 1 if qty > 0 else -1, qty, D(1), pending=D(qty))
        order = Order(key, 0, 2, 3, (Request(key, D(qty), "ENTRY"),), D(qty), 2, 10)
        a.fill(order, D(100), 6, 3)
    assert a.quantity[0] == 4
    old = a.lots["old"]
    close = Order(
        "exit", 0, 242, 243, (Request("old", -old.quantity, "EXIT"),), -old.quantity, 242, None
    )
    a.fill(close, D(101), 246, 243)
    assert a.quantity[0] == -6
    a.accrue(np.full(20, 100_000_000 * 3 * 86400, dtype=np.int64), 4500)
    expected = D(6) * 100 * D(".02") * 3 / 365
    assert abs(a.borrow_paid - expected) < D("1e-20")
    a.ex_dividend("ordinary", 0, D(1), 10000, 5000, "FABRICATED")
    assert a.claim_total() == -6
    a.pay_dividend("ordinary", 10000)
    first = a.cash
    a.pay_dividend("ordinary", 10000)
    assert a.cash == first
    a.reconcile()
    copied = unseal(seal(a))
    assert isinstance(copied, Account)
    copied.reconcile()
    assert copied.cash == a.cash and copied.journal_hash == a.journal_hash
    # Net account rounding and cash-in-lieu cannot manufacture aggregate assets.
    clock = MarketClock("2021-01-01", "2022-01-01")
    state = distribution((("L", D(10), D(1000)), ("S", D(-10), D(0))), clock)
    assert state.physical_whole == 0 and state.physical_fraction == 0
    from datetime import timedelta

    q = OGNQuote(EX, EX + timedelta(minutes=1), EX + timedelta(minutes=3), D(37), "FABRICATED")
    state = observe(state, q, q.available)
    _, amounts, total = pay_cil(replace(state, whole_settled=True), state.pay_at)
    assert sum((v for _, v in amounts), D(0)) == total == 0
    return {name: True for name in ("G_ACCOUNTING", "G_EXECUTION", "G_RISK", "G_REPRODUCIBILITY")}
