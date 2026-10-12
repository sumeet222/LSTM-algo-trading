"""Policy A independent hand sizing, netting, clocks and prospective caps."""

from decimal import Decimal as D

import pandas as pd
import pytest

from lstm_data.clocks import execution_plan, session_clock
from lstm_data.p3_domain import MODE, Forecast, Frictions, Permission, PriceReference, UniverseSpec
from lstm_data.p3_engine import PortfolioEngine
from lstm_data.p3_execution import ExecutionOffer
from lstm_data.p3_policy import Policy, admission, net_target, rank_intent

NAMES = ("AA", "BB", "CC", "DD", "EE")


def engine(names=NAMES, policy="A", bps=0, borrow=D(0), cash=10000):
    u = UniverseSpec("toy-v1", names)
    return PortfolioEngine(
        u,
        Permission(MODE),
        Policy(u, policy),
        Frictions(u, D(bps), borrow),
        D(cash),
        pd.Timestamp("2020-08-03T13:30Z"),
    )


def forecast(e, origin=1, reverse=False, day="2020-08-03", issued=None, key=None):
    p = execution_plan(session_clock(day), origin, issued_at=issued)
    scores = (-2.0, -1.0, 0.0, 1.0, 2.0) if reverse else (2.0, 1.0, 0.0, -1.0, -2.0)
    return Forecast(e.universe, key or f"SYN:F:{day}:{origin}", p, scores)


def references(e, at, *, price: int | D = 100, cutoff=None):
    observation = at if cutoff is None else cutoff
    kind = "SYNTHETIC_MINUTE_EVENT" if cutoff is None else "HOURLY_CLOSE_PROXY"
    return tuple(
        PriceReference(
            e.universe,
            s,
            D(price),
            observation,
            observation,
            "SYN:P:" + s + observation.isoformat(),
            kind,
            e.book.share_basis(s),
            period_start=None if cutoff is None else cutoff - pd.Timedelta(hours=1),
        )
        for s in e.universe.symbols
    )


def entry(e, f, price: int | D = 100):
    assert f.plan.entry is not None and f.plan.cutoff is not None
    refs = references(e, f.plan.entry, price=price, cutoff=f.plan.cutoff)
    return e.enter(f, f.plan.entry, tuple(ExecutionOffer(e.universe, r) for r in refs), refs)


def exit_at(e, at, key="SYN:EXPIRY", price=100):
    refs = references(e, at, price=price, cutoff=at - pd.Timedelta(minutes=3))
    e.expire(at, tuple(ExecutionOffer(e.universe, r) for r in refs), key)


@pytest.mark.parametrize("names", [NAMES, ("FOX", "ZEN", "MAP", "ORB", "TIN")])
def test_495_99_and_asynchronous_expiry(names):
    e = engine(names)
    f1, f2 = forecast(e), forecast(e, 2)
    assert entry(e, f1) and entry(e, f2)
    assert e.sleeves[0].quantities[0][1] == D("24.75")
    assert e.book.quantity(names[0]) == D("49.5")
    assert e.book.quantity(names[-1]) == D("-49.5")
    assert sum(abs(q) * 100 for _, q in e.book.balances) == 9900
    exit_at(e, f1.plan.exit)
    assert len(e.sleeves) == 1 and e.book.quantity(names[0]) == D("24.75")
    exit_at(e, f2.plan.exit, "SYN:EXPIRY2")
    assert not e.sleeves and all(q == 0 for _, q in e.book.balances) and e.book.cash == 10000


def test_opposite_virtual_sleeves_net_zero_then_physical_reopening_with_fees():
    e = engine(bps=5)
    f1, f2 = forecast(e), forecast(e, 2, True)
    assert entry(e, f1) and entry(e, f2)
    # Equity falls by 2.475 at first entry, so second sleeve's frozen size differs.
    assert e.sleeves[0].quantities[0][1] == D("24.75")
    assert e.sleeves[1].quantities[0][1] == D("-24.743874375")
    assert e.book.quantity(NAMES[0]) == D(".006125625")
    before = e.book.execution_fees
    exit_at(e, f1.plan.exit)
    assert e.book.quantity(NAMES[0]) == D("-24.743874375")
    assert e.book.execution_fees - before == D("2.475")
    # Zero-cost same-equity opposing sleeves genuinely offset to zero.
    z = engine()
    assert entry(z, forecast(z)) and entry(z, forecast(z, 2, True))
    assert net_target(z.universe, z.sleeves) == tuple((s, D(0)) for s in NAMES)
    assert z.book.balances == tuple((s, D(0)) for s in NAMES)
    assert len(z.sleeves) == 2 and z.book.execution_fees == 0


def test_independent_post_cost_cap_exact_boundary_and_epsilon():
    e = engine()
    physical = tuple(
        (s, D("25.25") if i == 0 else -D("25.25") if i == 4 else D(0)) for i, s in enumerate(NAMES)
    )
    target = tuple(
        (s, D(50) if i == 0 else D(-50) if i == 4 else D(0)) for i, s in enumerate(NAMES)
    )
    prices: dict[str, D] = dict.fromkeys(NAMES, D(100))
    assert admission(e.book.frictions, D(10000), physical, target, prices)["accepted"]
    costly = admission(Frictions(e.universe, D(5)), D(10000), physical, target, prices)
    assert costly["projected_fee"] == D("2.475")
    assert costly["post_cost_equity"] == D("9997.525") and not costly["accepted"]
    assert not admission(e.book.frictions, D("9999.9999"), physical, target, prices)["accepted"]


def test_missing_contemporary_leg_and_partial_partner_failure():
    e = engine(bps=5)
    f = forecast(e)
    assert f.plan.entry is not None
    refs = references(e, f.plan.entry, cutoff=f.plan.cutoff)
    assert not e.enter(f, f.plan.entry, (ExecutionOffer(e.universe, refs[0]),), refs)
    assert e.book.cash == 10000 and not e.sleeves and not e.book.outstanding
    p = engine(bps=5)
    f = forecast(p)
    assert f.plan.entry is not None
    refs = references(p, f.plan.entry, cutoff=f.plan.cutoff)
    offers = tuple(
        ExecutionOffer(p.universe, r, D(0), "REJECTED")
        if r.symbol == NAMES[-1]
        else ExecutionOffer(p.universe, r)
        for r in refs
    )
    assert p.enter(f, f.plan.entry, offers, refs)
    assert p.book.quantity(NAMES[0]) == D("24.75") and p.book.quantity(NAMES[-1]) == 0
    assert p.book.execution_fees == D("1.2375")
    assert p.book.cash == D("7523.7625") and p.pending_reason == "PARTIAL_PAIR_ENTRY"


def test_ties_negative_scores_delayed_clock_and_early_close():
    e = engine()
    f = forecast(e)
    negative = Forecast(e.universe, "SYN:NEG", f.plan, (-1.0, -2.0, -3.0, -4.0, -5.0))
    assert rank_intent(negative).long == NAMES[0]
    delayed = forecast(e, issued=pd.Timestamp("2020-08-03T14:34:20Z"), key="SYN:DELAY")
    assert delayed.plan.entry == pd.Timestamp("2020-08-03T14:36Z")
    assert delayed.plan.exit == pd.Timestamp("2020-08-03T18:36Z") and entry(e, delayed)
    early = engine()
    f = forecast(early, day="2020-11-27")
    assert not f.plan.calendar_valid and not entry(early, f)
    assert early.book.cash == 10000


def test_new_scores_do_not_rebalance_old_sleeve_and_full_rejection():
    e = engine()
    assert entry(e, forecast(e))
    frozen = e.sleeves[0]
    assert not entry(e, forecast(e, 2), price=104)
    assert e.sleeves == (frozen,) and e.book.quantity(NAMES[0]) == D("24.75")
    assert e.rejections == ["POST_COST_100_CAP"]


def test_delayed_exit_keeps_exact_cutoff_and_exit_publication_cut_differs():
    from dataclasses import replace

    e = engine()
    f = forecast(e, issued=pd.Timestamp("2020-08-03T14:34:20Z"), key="SYN:DELAYED")
    assert entry(e, f)
    assert f.plan.exit is not None and f.plan.cutoff is not None
    cutoff = f.plan.cutoff + pd.Timedelta(hours=4)
    refs = tuple(
        replace(r, available_at=cutoff + pd.Timedelta(minutes=1))
        for r in references(e, f.plan.exit, cutoff=cutoff)
    )
    e.expire(f.plan.exit, tuple(ExecutionOffer(e.universe, r) for r in refs), "SYN:DELAY_EXIT")
    assert not e.sleeves and not e.pending_target and e.book.cash == 10000
    prior = engine()
    f = forecast(prior)
    assert f.plan.entry is not None and f.plan.cutoff is not None
    late = tuple(
        replace(r, available_at=f.plan.cutoff + pd.Timedelta(minutes=1))
        for r in references(prior, f.plan.entry, cutoff=f.plan.cutoff)
    )
    assert not prior.enter(
        f, f.plan.entry, tuple(ExecutionOffer(prior.universe, r) for r in late), late
    )
    assert prior.rejections == ["PAIR_REFERENCE_INELIGIBLE"]


def test_simultaneous_virtual_offset_from_flat_emits_no_external_orders():
    e = engine()
    assert entry(e, forecast(e)) and entry(e, forecast(e, 2, True))
    fresh = engine(bps=5)
    target = net_target(fresh.universe, e.sleeves)
    assert (
        fresh.book.orders_for_target(target, pd.Timestamp("2020-08-03T15:33Z"), "SYN:COMBINED")
        == ()
    )
    assert fresh.book.cash == 10000 and fresh.book.execution_fees == 0
