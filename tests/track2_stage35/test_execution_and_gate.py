import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage35.common import D, Price
from lstm_data.trading.track2.stage35.execution_clock import ScheduledEvent, schedule, window
from lstm_data.trading.track2.stage35.execution_model import (
    CostScenario,
    SyntheticBar,
    propose_fill,
)
from lstm_data.trading.track2.stage35.gate import (
    REQUIRED,
    historical_start,
    require_backtest_approval,
)


def test_exact_entry_exit_and_after_close():
    clock = MarketClock("2024-01-01", "2024-12-10")
    origin = datetime(2024, 1, 8, 15, 30, tzinfo=timezone.utc)
    entry = window(clock, origin, origin)
    exit = window(clock, origin, origin, "EXIT")
    assert entry.decision == origin + timedelta(
        minutes=2
    ) and entry.first_minute == origin + timedelta(minutes=3)
    assert exit.first_minute == datetime(2024, 1, 8, 19, 33, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        window(clock, origin, origin + timedelta(minutes=10))
    with pytest.raises(ValueError):
        window(clock, origin, origin, delay=5)
    # 11:30 origin before Thanksgiving has an endpoint at15:30; half-day clock retained.
    early = datetime(2024, 11, 29, 14, 30, tzinfo=timezone.utc)
    assert window(clock, early, early, "EXIT").first_minute == datetime(
        2024, 12, 2, 15, 3, tzinfo=timezone.utc
    )
    late = datetime(2024, 11, 27, 20, 30, tzinfo=timezone.utc)
    assert clock.endpoint(late) == datetime(2024, 11, 29, 18, 0, tzinfo=timezone.utc)
    assert window(clock, late, late, "EXIT").first_minute == datetime(
        2024, 12, 2, 14, 30, tzinfo=timezone.utc
    )


def test_bar_proxy_partial_no_current_volume_and_missing():
    clock = MarketClock("2024-01-01", "2024-01-20")
    origin = datetime(2024, 1, 8, 15, 30, tzinfo=timezone.utc)
    w = window(clock, origin, origin)
    start = w.first_minute
    scenario = CostScenario("base", D(5), D(5), D(".005"), D(1))
    bar = SyntheticBar(start, start + timedelta(minutes=3), D(100), D(1000), origin)
    result = propose_fill(clock, w, D(30), bar, scenario, bar.available_at)
    assert (
        result.status == "PARTIAL"
        and result.quantity == 10
        and result.price == D("100.1")
        and result.fee == 1
    )
    with pytest.raises(ValueError):
        propose_fill(
            clock,
            w,
            D(30),
            replace(bar, prior_volume_available_at=start + timedelta(minutes=1)),
            scenario,
            bar.available_at,
        )
    with pytest.raises(ValueError):
        propose_fill(clock, w, D(30), replace(bar, start=w.submission), scenario, bar.available_at)
    with pytest.raises(ValueError):
        propose_fill(clock, w, D(30), replace(bar, kind="HISTORICAL"), scenario, bar.available_at)
    assert propose_fill(clock, w, D(30), None, scenario, bar.available_at).status == "CANCELLED"
    assert (
        propose_fill(
            clock, replace(w, kind="EXIT", deadline=None), D(-30), None, scenario, bar.available_at
        ).status
        == "UNRESOLVED"
    )
    assert (
        propose_fill(clock, w, D(30), replace(bar, halted=True), scenario, bar.available_at).status
        == "CANCELLED"
    )
    assert (
        propose_fill(
            clock,
            w,
            D(30),
            replace(bar, start=origin + timedelta(minutes=6)),
            scenario,
            bar.available_at,
        ).status
        == "CANCELLED"
    )


def test_stable_receipt_queue_and_gate_no_outputs(tmp_path):
    at = datetime(2024, 1, 8, 15, 30, tzinfo=timezone.utc)
    events = (
        ScheduledEvent("b", at, at + timedelta(minutes=3), 2),
        ScheduledEvent("a", at, at + timedelta(minutes=2), 1),
    )
    assert schedule(events) == schedule(tuple(reversed(events)))
    with pytest.raises(ValueError):
        schedule(events + (events[0],))
    for missing in REQUIRED:
        report = {"gates": {k: {"status": "PASS"} for k in REQUIRED}}
        report["gates"][missing]["status"] = "HOLD"
        with pytest.raises(PermissionError):
            require_backtest_approval(report)
    report = {"gates": {k: {"status": "PASS"} for k in REQUIRED}}
    report["gates"]["G_HUMAN"].update(
        reviewer_kind="EXTERNAL_HUMAN", external_approval_id="fake", created_by="codex"
    )
    with pytest.raises(PermissionError, match="HUMAN"):
        require_backtest_approval(report)
    report["gates"]["G_HUMAN"]["created_by"] = "human_fixture"
    with pytest.raises(PermissionError, match="NOT_ACTIVATED"):
        require_backtest_approval(report)
    path = tmp_path / "gate.json"
    path.write_text(json.dumps(report))
    output = tmp_path / "economics"
    with pytest.raises(PermissionError):
        historical_start(path, output)
    assert not output.exists()


def test_scenario_cost_monotonicity_both_sides():
    for quantity in (D(10), D(-10)):
        prices = []
        fees = []
        for bps in (D(1), D(5), D(15)):
            p, f = CostScenario("candidate", bps, bps, bps / D(1000), bps / D(10)).cost(
                quantity, D(100)
            )
            prices.append(p)
            fees.append(f)
        assert fees == sorted(fees)
        assert prices == sorted(prices, reverse=quantity < 0)


def test_execution_into_book_and_missing_exit():
    from lstm_data.trading.track2.stage012.cohort_state import Cohort
    from lstm_data.trading.track2.stage35.accounting import Book
    from lstm_data.trading.track2.stage35.execution_model import apply_synthetic

    clock = MarketClock("2024-01-01", "2024-01-20")
    origin = datetime(2024, 1, 8, 15, 30, tzinfo=timezone.utc)
    w = window(clock, origin, origin)
    c = Cohort(
        "a",
        "AAPL",
        10.0,
        1000.0,
        origin,
        clock.endpoint(origin),
        origin + timedelta(minutes=5),
        "RAW_UNADJUSTED",
        ("synthetic",),
    )
    mark = Price(w.decision, w.decision, D(100), "synthetic")
    book = Book.funded(D(100000)).mark("mark", "AAPL", mark, w.decision)
    book = book.reserve("reserve", (c,), mark, w.decision)
    bar = SyntheticBar(
        w.first_minute, w.first_minute + timedelta(minutes=3), D(100), D(1000), origin
    )
    costs = CostScenario("synthetic", D(0), D(0), D(0), D(0))
    book, outcome = apply_synthetic(
        book, clock, w, "AAPL", (("a", D(10)),), bar, costs, bar.available_at, "fill"
    )
    assert outcome.status == "FILLED" and book.positions[0].quantity == 10
    exit = window(clock, origin, origin, "EXIT")
    book, outcome = apply_synthetic(
        book, clock, exit, "AAPL", (("a", D(-10)),), None, costs, exit.first_minute, "missing"
    )
    assert outcome.status == "UNRESOLVED" and book.positions[0].quantity == 10 and book.unresolved


def test_order_minimum_commission_not_repeated_on_partial_fills():
    from lstm_data.trading.track2.stage35.execution_model import CommissionState

    scenario = CostScenario("base", D(5), D(5), D(".005"), D(1))
    state = CommissionState("one_external_order")
    state, first = state.next_fill(D(10), scenario)
    state, second = state.next_fill(D(10), scenario)
    assert first == 1 and second == 0 and state.paid == 1
    state, third = state.next_fill(D(280), scenario)
    assert third == D(".5") and state.paid == D("1.5")


def test_failed_fill_keeps_observed_adverse_mark_and_holds():
    from lstm_data.trading.track2.stage012.cohort_state import Cohort
    from lstm_data.trading.track2.stage35.accounting import Book
    from lstm_data.trading.track2.stage35.execution_model import apply_synthetic

    origin = datetime(2024, 1, 8, 15, 30, tzinfo=timezone.utc)
    clock = MarketClock("2024-01-01", "2024-01-20")
    w = window(clock, origin, origin)

    def c(key, q):
        return Cohort(
            key,
            "AAPL",
            q,
            q * 100,
            origin,
            clock.endpoint(origin),
            origin + timedelta(minutes=5),
            "RAW_UNADJUSTED",
            ("synthetic",),
        )

    p = Price(w.decision, w.decision, D(100), "synthetic")
    book = Book.funded(D(100000)).mark("initial", "AAPL", p, p.at)
    book = book.reserve("reserve", (c("old", 10.0), c("new", 1.0)), p, p.at)
    at = w.first_minute
    p = Price(at, at, D(100), "synthetic")
    book = book.execute("old_fill", "AAPL", (("old", D(10)),), p, at, D(100), D(10))
    start = at + timedelta(minutes=1)
    bar = SyntheticBar(start, start + timedelta(minutes=3), D(2000), D(1000), origin)
    updated, result = apply_synthetic(
        book,
        clock,
        w,
        "AAPL",
        (("new", D(1)),),
        bar,
        CostScenario("zero", D(0), D(0), D(0), D(0)),
        bar.available_at,
        "gap",
    )
    assert result.status == "UNRESOLVED" and updated.positions[0].quantity == 10
    assert (
        dict(updated.marks)["AAPL"].value == 2000 and updated.nav() == 119000 and updated.unresolved
    )
    updated.reconcile()
