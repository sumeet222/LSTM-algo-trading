"""Small reproducible synthetic-only ledger oracles; no prices read from disk."""

from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from pathlib import Path

import pandas as pd

from .clocks import execution_plan, session_clock
from .config import fingerprint, write_json
from .p3_accounting import ARITHMETIC, ActionInstruction, PhysicalBook
from .p3_domain import (
    MODE,
    SHARE_BASIS,
    Fill,
    Forecast,
    Frictions,
    Permission,
    PriceReference,
    UniverseSpec,
)
from .p3_engine import PortfolioEngine
from .p3_events import json_value
from .p3_execution import ExecutionOffer
from .p3_policy import Policy
from .p3_replay import ReplayFrame, replay, scenario_matrix

D = Decimal
START = pd.Timestamp("2020-08-03T13:30Z")


def toy_engine(
    universe: UniverseSpec, *, policy: str = "A", bps: int = 5, borrow: D = D(0), cash: D = D(10000)
) -> PortfolioEngine:
    return PortfolioEngine(
        universe,
        Permission(MODE),
        Policy(universe, policy),
        Frictions(universe, D(bps), borrow),
        cash,
        START,
    )


def toy_forecast(
    universe: UniverseSpec, origin: int = 1, reverse: bool = False, day: str = "2020-08-03"
) -> Forecast:
    return Forecast(
        universe,
        f"SYN:F:{day}:{origin}",
        execution_plan(session_clock(day), origin),
        (-2.0, -1.0, 0.0, 1.0, 2.0) if reverse else (2.0, 1.0, 0.0, -1.0, -2.0),
    )


def toy_refs(
    book: PhysicalBook, at: pd.Timestamp, price: D = D(100), cutoff: pd.Timestamp | None = None
) -> tuple[PriceReference, ...]:
    observation = at if cutoff is None else cutoff
    return tuple(
        PriceReference(
            book.universe,
            s,
            price,
            observation,
            observation,
            "SYN:P:" + s + observation.isoformat(),
            "SYNTHETIC_MINUTE_EVENT" if cutoff is None else "HOURLY_CLOSE_PROXY",
            book.share_basis(s),
            period_start=None if cutoff is None else cutoff - pd.Timedelta(hours=1),
        )
        for s in book.universe.symbols
    )


def toy_entry(engine: PortfolioEngine, forecast: Forecast) -> bool:
    assert forecast.plan.entry is not None and forecast.plan.cutoff is not None
    rows = toy_refs(engine.book, forecast.plan.entry, cutoff=forecast.plan.cutoff)
    return engine.enter(
        forecast, forecast.plan.entry, tuple(ExecutionOffer(engine.universe, r) for r in rows), rows
    )


def toy_script(universe: UniverseSpec) -> tuple[ReplayFrame, ...]:
    """One immutable two-origin conflict script for all 24 fresh accounts."""
    seed = toy_engine(universe)
    frames = []
    for origin, reverse in ((1, False), (2, True)):
        f = toy_forecast(universe, origin, reverse)
        assert f.plan.entry is not None and f.plan.cutoff is not None
        rows = toy_refs(seed.book, f.plan.entry, cutoff=f.plan.cutoff)
        frames.append(
            ReplayFrame(
                universe,
                f"SYN:ENTRY:{origin}",
                f.plan.entry,
                rows,
                tuple(ExecutionOffer(universe, r) for r in rows),
                f,
            )
        )
    for origin in (1, 2):
        f = toy_forecast(universe, origin)
        assert f.plan.exit is not None and f.plan.cutoff is not None
        rows = toy_refs(seed.book, f.plan.exit, cutoff=f.plan.cutoff + pd.Timedelta(hours=4))
        frames.append(
            ReplayFrame(
                universe,
                f"SYN:EXIT:{origin}",
                f.plan.exit,
                rows,
                tuple(ExecutionOffer(universe, r) for r in rows),
            )
        )
    frames.append(
        ReplayFrame(
            universe, "SYN:DAILY_CLOSE", pd.Timestamp("2020-08-03T20:00Z"), borrow_close=True
        )
    )
    return tuple(frames)


def physical_trade(
    book: PhysicalBook, symbol: str, quantity: D, at: pd.Timestamp, price: D, key: str
) -> None:
    target = tuple((s, quantity if s == symbol else q) for s, q in book.balances)
    ref = next(r for r in toy_refs(book, at, price) if r.symbol == symbol)
    for order in book.orders_for_target(target, at, key):
        book.fill(
            Fill(
                book.universe,
                key + ":FILL",
                order,
                at,
                order.quantity,
                ref,
                book.frictions.fee(order.quantity, price),
            )
        )


def reconstruct(trace: list[dict], universe: UniverseSpec) -> dict:
    """Independent journal replay; no calls to the portfolio/accounting engine."""
    cash, shares, ids, sequence = D(0), dict.fromkeys(universe.symbols, D(0)), {}, 0
    last = None
    with localcontext(ARITHMETIC):
        for event in trace:
            assert event["sequence"] == sequence + 1 and event["event_id"] not in ids
            assert event["universe_id"] == universe.universe_id and not event["research_ready"]
            at = pd.Timestamp(event["at"])
            assert last is None or at >= last
            parent = event["parent_id"]
            assert parent is None or parent in ids
            p = event["payload"]
            if event["kind"] == "ACCOUNT":
                cash = D(p["cash"])
            elif event["kind"] == "CASH":
                assert cash == D(p["cash_before"])
                cash += D(p["movement"])
                assert cash == D(p["cash_after"])
            elif event["kind"] == "POSITION":
                assert shares[p["symbol"]] == D(p["before"])
                shares[p["symbol"]] = D(p["after"])
            ids[event["event_id"]] = event
            sequence, last = event["sequence"], at
    return {"cash": cash, "shares": tuple(shares.items()), "events": sequence}


def evidence(universe: UniverseSpec) -> dict:
    Permission(MODE).ensure()
    traces, oracles = {}, []

    def check(case: str, field: str, expected: object, actual: object, calculation: str) -> None:
        good = expected == actual
        oracles.append(
            {
                "case": case,
                "field": field,
                "expected": json_value(expected),
                "actual": json_value(actual),
                "calculation": calculation,
                "status": "PASS" if good else "CORRECT",
            }
        )
        if not good:
            raise ValueError("INDEPENDENT_ORACLE_FAILED:" + case + ":" + field)

    def save(name: str, engine: PortfolioEngine) -> None:
        trace = engine.ledger.export()
        recovered = reconstruct(trace, universe)
        check(
            name,
            "reconstructed_cash",
            engine.book.cash,
            recovered["cash"],
            "Cash movements in sequence",
        )
        check(
            name,
            "reconstructed_shares",
            engine.book.balances,
            recovered["shares"],
            "Position deltas in sequence",
        )
        traces[name] = {"trace_id": engine.ledger.trace_id, "events": trace}

    long, short = universe.symbols[0], universe.symbols[-1]
    for name, entry_qty, exit_price, expected_cash, fee in (
        ("BUY_SELL", D(5), D(110), D("1049.475"), D(".525")),
        ("SHORT_COVER", D(-5), D(90), D("1049.525"), D(".475")),
    ):
        e = toy_engine(universe, cash=D(1000))
        at = pd.Timestamp("2020-08-03T14:33Z")
        physical_trade(e.book, long, entry_qty, at, D(100), "SYN:OPEN")
        check(
            name,
            "entry_cash",
            D("499.75") if entry_qty > 0 else D("1499.75"),
            e.book.cash,
            "1000 - signed 5*100 - .25",
        )
        check(
            name,
            "entry_equity",
            D("999.75"),
            e.book.valuation(toy_refs(e.book, at), at)["accrual_equity"],
            "Cash + long assets - short liability",
        )
        physical_trade(
            e.book, long, D(0), pd.Timestamp("2020-08-03T18:33Z"), exit_price, "SYN:EXIT"
        )
        check(
            name,
            "ending_cash",
            expected_cash,
            e.book.cash,
            "Actual sale/cover notional and 5bps fee",
        )
        check(name, "fee", fee, e.book.execution_fees, "500*.0005 + exit notional*.0005")
        save(name, e)

    script = toy_script(universe)
    for policy in ("A", "B"):
        e = replay(
            Permission(MODE),
            universe,
            script,
            policy,
            Frictions(universe, D(0), D(".03")),
            D(10000),
            START,
        )
        check(
            "POLICY_" + policy,
            "borrow",
            D(".4125") if policy == "A" else D(".20625"),
            e.borrow.total,
            "2475 day-max * .03/360 per physically short name",
        )
        check(
            "POLICY_" + policy,
            "veto",
            [] if policy == "A" else ["POLICY_B_VIRTUAL_CONFLICT"],
            e.rejections,
            "Policy B checks each active virtual leg",
        )
        save("POLICY_" + policy, e)
    zero = replay(
        Permission(MODE), universe, script[:2], "A", Frictions(universe, D(0)), D(10000), START
    )
    check(
        "OFFSET",
        "physical",
        tuple((s, D(0)) for s in universe.symbols),
        zero.book.balances,
        "+24.75 and -24.75 virtual quantities sum to zero",
    )
    check("OFFSET", "virtual_sleeves", 2, len(zero.sleeves), "Both accepted sleeves persist")
    save("OFFSET", zero)

    missing = toy_engine(universe)
    f = toy_forecast(universe)
    toy_entry(missing, f)
    assert f.plan.exit is not None
    missing.expire(f.plan.exit, (), "SYN:MISSING_EXIT")
    check(
        "MISSING_EXIT",
        "terminal_NAV",
        None,
        missing.valuation(f.plan.exit, (), "SYN:TERMINAL")["NAV"],
        "Missing marks/exit: no artificial terminal sale",
    )
    retry_at = f.plan.exit + pd.Timedelta(minutes=1)
    minute = tuple(ExecutionOffer(universe, r) for r in toy_refs(missing.book, retry_at))
    missing.retry(retry_at, minute, "SYN:1434_RETRY")
    check(
        "MISSING_EXIT", "cash_after_retry", D("9995.05"), missing.book.cash, "10000 - 4950*.0005*2"
    )
    save("MISSING_EXIT", missing)

    partial = toy_engine(universe)
    assert f.plan.entry is not None
    refs = toy_refs(partial.book, f.plan.entry, cutoff=f.plan.cutoff)
    proposal = tuple(
        ExecutionOffer(universe, r, D(0), "REJECTED")
        if r.symbol == short
        else ExecutionOffer(universe, r)
        for r in refs
    )
    partial.enter(f, f.plan.entry, proposal, refs)
    check(
        "PARTIAL_PAIR", "cash_after_one_leg", D("7523.7625"), partial.book.cash, "10000-2475-1.2375"
    )
    at = f.plan.entry + pd.Timedelta(minutes=1)
    partial.retry(
        at, tuple(ExecutionOffer(universe, r) for r in toy_refs(partial.book, at)), "SYN:FLATTEN"
    )
    check(
        "PARTIAL_PAIR",
        "cash_after_flat",
        D("9997.525"),
        partial.book.cash,
        "Two actual 2475 notionals cost 2.475",
    )
    save("PARTIAL_PAIR", partial)

    emergency = toy_engine(universe)
    toy_entry(emergency, f)
    at = pd.Timestamp("2020-08-03T15:00Z")
    emergency.monitor(at, toy_refs(emergency.book, at, D(300)), "SYN:EMERGENCY")
    half_at = at + pd.Timedelta(minutes=1)
    emergency.retry(
        half_at,
        tuple(
            ExecutionOffer(universe, r, D(".5"), "PARTIAL")
            for r in toy_refs(emergency.book, half_at, D(300))
        ),
        "SYN:HALF",
    )
    check(
        "EMERGENCY",
        "residual_long",
        D("12.375"),
        emergency.book.quantity(long),
        "24.75 minus actual half fill",
    )
    check(
        "EMERGENCY",
        "paid_fee_after_half",
        D("6.1875"),
        emergency.book.execution_fees,
        "2.475 entry + 7425*.0005 partial liquidation",
    )
    later = at + pd.Timedelta(minutes=2)
    emergency.retry(
        later,
        tuple(ExecutionOffer(universe, r) for r in toy_refs(emergency.book, later, D(300))),
        "SYN:FINAL_FLAT",
    )
    check(
        "EMERGENCY",
        "paid_fee_flat",
        D("9.90"),
        emergency.book.execution_fees,
        "2.475 + 14850*.0005",
    )
    check(
        "EMERGENCY",
        "sleeves",
        0,
        len(emergency.sleeves),
        "Terminate only when physical target is achieved",
    )
    save("EMERGENCY", emergency)

    carry = toy_engine(universe, bps=0)
    f = toy_forecast(universe, day="2020-11-25")
    toy_entry(carry, f)
    assert f.plan.exit is not None and f.plan.entry is not None
    carry.expire(f.plan.exit, (), "SYN:OVERNIGHT_MISSING")
    boundary = pd.Timestamp("2020-11-30T14:30Z")
    actions = (
        ActionInstruction(
            universe,
            "SYN:SPLIT",
            short,
            "SPLIT",
            boundary,
            f.plan.entry,
            D(4),
            SHARE_BASIS,
            post_split_basis="SYN:POST",
            fractional_policy="EXACT_FRACTIONAL_ASSUMPTION",
        ),
        ActionInstruction(
            universe,
            "SYN:DIV",
            short,
            "DIVIDEND",
            boundary,
            f.plan.entry,
            D(".5"),
            "SYN:POST",
            sequence=1,
        ),
    )
    carry.apply_actions(actions, boundary)
    marks = tuple(
        r
        if r.symbol != short
        else PriceReference(
            universe, short, D(25), boundary, boundary, "SYN:POST_MARK", "MARK", "SYN:POST"
        )
        for r in toy_refs(carry.book, boundary)
    )
    check(
        "OVERNIGHT",
        "short_post_split",
        D(-99),
        carry.book.quantity(short),
        "-24.75*4 split primitive",
    )
    check(
        "OVERNIGHT",
        "dividend_liability",
        D("-49.5"),
        carry.book.claims[0]["amount"],
        "-99*.5 physical claim",
    )
    check(
        "OVERNIGHT",
        "toy_accrual_equity",
        D("9950.5"),
        carry.book.valuation(marks, boundary)["accrual_equity"],
        "Split changes units only; unknown-pay-date dividend reduces accrual equity 49.5",
    )
    check(
        "OVERNIGHT",
        "NAV",
        None,
        carry.valuation(boundary, marks, "SYN:OVERNIGHT_NAV")["NAV"],
        "Real execution/overnight financing/pay date unresolved",
    )
    save("OVERNIGHT", carry)
    return {
        "scope": "SYNTHETIC_ACCOUNTING_ONLY",
        "universe": json_value(universe),
        "P2_handoff_sha": Permission(MODE).ensure(),
        "script_id": fingerprint(json_value(script)),
        "traces": traces,
        "expected_vs_actual": oracles,
        "matrix": scenario_matrix(Permission(MODE), universe, script, D(10000), START),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=[MODE])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    permission = Permission(args.mode)
    permission.ensure()
    destinations = [
        args.out / name
        for name in (
            "synthetic_ledger.json",
            "expected_vs_actual.json",
            "scenario_matrix.json",
            "alternate_universe.json",
        )
    ]
    if any(p.exists() for p in destinations):
        raise ValueError("AUDIT_OUTPUT_EXISTS_USE_NEW_DIRECTORY")
    universe = UniverseSpec("P3_TOY_V1", ("AA", "BB", "CC", "DD", "EE"))
    result = evidence(universe)
    alternate = evidence(UniverseSpec("P3_TOY_ALT_V1", ("FOX", "ZEN", "MAP", "ORB", "TIN")))
    write_json(
        destinations[0],
        {k: v for k, v in result.items() if k not in {"matrix", "expected_vs_actual"}},
    )
    write_json(destinations[1], {"scope": result["scope"], "rows": result["expected_vs_actual"]})
    write_json(destinations[2], {"scope": result["scope"], "rows": result["matrix"]})
    write_json(
        destinations[3],
        {
            "scope": alternate["scope"],
            "universe": alternate["universe"],
            "offset_trace": alternate["traces"]["OFFSET"],
            "oracle_rows": alternate["expected_vs_actual"],
            "matrix_trace_ids": [r["trace_id"] for r in alternate["matrix"]],
        },
    )
    print("SYNTHETIC_ACCOUNTING_ONLY: independent oracles and 24 fresh paths verified; G4 HOLD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
