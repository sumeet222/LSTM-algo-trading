"""Fabricated feature/label fixtures only. No file, archive or provider reads."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pandas as pd

from .baseline_inputs import BaselineInput
from .clocks import execution_plan
from .config import fingerprint
from .ft0_tensor import StockTensor
from .ft0_transforms import ORDER, SCALED, FitObservation, fit_floors, fit_scaler
from .labels import UNIVERSE as LEGACY_KEYS
from .labels import FitWindow
from .m2 import ScheduledCalendar, scheduled_window
from .p3_domain import UniverseSpec


def certificates(universe: UniverseSpec, window: FitWindow):
    """Ordinal shim only for unchanged P2 fitting validators, never economic names."""
    source, action = (
        fingerprint([universe.universe_id, "SYN:FEATURE"]),
        fingerprint([universe.universe_id, "SYN:ACTION"]),
    )
    days = (
        window.start + pd.Timedelta(days=1),
        window.start + pd.Timedelta(days=2),
        window.start + pd.Timedelta(days=3),
    )
    scaled, floors = [], []
    for symbol in LEGACY_KEYS:
        for i, at in enumerate(days):
            day = at.tz_convert("America/New_York").date().isoformat()
            for kind in SCALED:
                origin = 1 + i % 2
                key = (symbol, day, origin if kind == "M2" else i + 1)
                scaled.append(
                    FitObservation(
                        symbol,
                        at,
                        kind,
                        key,
                        float(i - 1),
                        "SYN:SCALER:" + symbol + kind + str(i),
                        source,
                        action,
                        "SYNTHETIC",
                        at,
                        origin if kind == "M2" else None,
                    )
                )
            for kind, value in (
                ("RMS12", 0.01),
                ("RMS60", 0.02),
                ("RMS63", 0.03),
                ("VOLUME_H", 100.0),
                ("VOLUME_D", 1000.0),
            ):
                floors.append(
                    FitObservation(
                        symbol,
                        at,
                        kind,
                        (symbol, day, i + 1),
                        value,
                        "SYN:FLOOR:" + symbol + kind + str(i),
                        source,
                        action,
                        "SYNTHETIC",
                        at,
                    )
                )
    return fit_scaler(tuple(scaled), window, "SYN:SCALER_FIT", allow_synthetic=True), fit_floors(
        tuple(floors), window, "SYN:FLOOR_FIT", allow_synthetic=True
    )


def feature_input(
    universe: UniverseSpec,
    day: str = "2020-08-20",
    origin: int = 1,
    latest: tuple[float, ...] = (2.0, 1.0, 0.0, -1.0, -2.0),
) -> BaselineInput:
    window = FitWindow(
        "SYNTHETIC:MOMENTUM",
        pd.Timestamp("2020-07-01T04:00Z"),
        pd.Timestamp("2020-08-01T04:00Z"),
        pd.Timestamp("2020-08-01T04:00Z"),
        "INNER_TRAIN",
    )
    scaler, floors = certificates(universe, window)
    calendar = ScheduledCalendar("2020-07-01", day)
    plan = execution_plan(calendar.clock(day), origin)
    steps = scheduled_window(calendar, day, origin)
    raw = tuple(
        tuple(tuple(latest[i] if c == 0 and j == 47 else 0.0 for c in range(16)) for j in range(48))
        for i in range(5)
    )
    values = []
    for stock in raw:
        rows = []
        for step, row in zip(steps, stock):
            rows.append(
                tuple(
                    scaler.apply(
                        f,
                        v,
                        step.end,
                        source_binding=scaler.source_binding,
                        action_binding=scaler.action_binding,
                    )[0]
                    for f, v in zip(ORDER, row)
                )
            )
        values.append(tuple(rows))
    mask = tuple(tuple((True,) * 16 for _ in steps) for _ in universe.symbols)
    lineage = tuple(
        tuple(
            tuple(f"SYN:FT0:{symbol}:{step.session}:{step.slot}:{f}" for f in ORDER)
            for step in steps
        )
        for symbol in universe.symbols
    )
    clocks = tuple(tuple((step.end,) * 16 for step in steps) for _ in universe.symbols)
    stock = StockTensor(
        universe.symbols,
        steps,
        ORDER,
        raw,
        tuple(values),
        mask,
        tuple(tuple(("SYNTHETIC_VALID",) * 16 for _ in steps) for _ in universe.symbols),
        lineage,
        True,
        floors.certificate_id,
        ("SYN:M2",) * 5,
        scaler.certificate_id,
        "ASOF",
        scaler.source_binding,
        scaler.action_binding,
        False,
        True,
    )
    return BaselineInput(
        universe, f"SYN:INPUT:{day}:{origin}", plan, stock, scaler, floors, clocks, "SYNTHETIC"
    )


def proxy_offers(
    universe: UniverseSpec, at: pd.Timestamp, cutoff: pd.Timestamp, price: Decimal = Decimal(100)
):
    from .p3_domain import PriceReference
    from .p3_execution import ExecutionOffer

    return tuple(
        ExecutionOffer(
            universe,
            PriceReference(
                universe,
                s,
                price,
                cutoff,
                cutoff,
                "SYN:PROXY:" + s + cutoff.isoformat(),
                "HOURLY_CLOSE_PROXY",
                period_start=cutoff - pd.Timedelta(hours=1),
            ),
        )
        for s in universe.symbols
    )


def change_latest(row: BaselineInput, values: tuple[float, ...]) -> BaselineInput:
    raw = tuple(
        stock[:-1] + ((values[i],) + stock[-1][1:],) for i, stock in enumerate(row.stock.raw_values)
    )
    scaled = tuple(
        stock[:-1] + ((values[i],) + stock[-1][1:],) for i, stock in enumerate(row.stock.values)
    )
    return replace(row, stock=replace(row.stock, raw_values=raw, values=scaled))


def ridge_data(universe: UniverseSpec, stage: str = "WF1", *, zero_labels: bool = False):
    """Dense fabricated calendar sample, enough63-tail sessions; no history loads."""
    import math

    from .baseline_fit import FitData
    from .baseline_ridge import RidgeOrigin
    from .hourly_proxy import HourlyCloseReference, proxy_label_sample
    from .labels import ActionScope, ForecastEvidence
    from .market_features import DailyScaleSample, MarketMeasures, MarketVector

    ends = {"WF1": "2023-06-30", "WF2": "2023-12-31", "PRECONFIRMATION": "2024-06-30"}
    end = ends[stage]
    calendar = ScheduledCalendar("2020-07-01", end)
    base = feature_input(universe, latest=(0.0,) * 5)
    # Include a short training prefix preceding the frozen63-session tail, not a new boundary.
    from .calendar import schedule

    sessions = tuple(pd.Timestamp(d).date().isoformat() for d in schedule("2020-07-01", end).index)[
        -100:
    ]
    origins, stock_records, floor_records = [], [], []
    market_by_time = {}
    measures, daily = [], []
    for day in sessions:
        for origin in (1, 2):
            plan = execution_plan(calendar.clock(day), origin)
            if not plan.calendar_valid:
                continue
            steps = scheduled_window(calendar, day, origin)
            assert plan.cutoff is not None and plan.exit is not None
            ids = tuple(
                tuple(
                    tuple(f"SYN:FT0:{s}:{step.session}:{step.slot}:{f}" for f in ORDER)
                    for step in steps
                )
                for s in universe.symbols
            )
            stock = replace(base.stock, steps=steps, lineage=ids)
            times = tuple(tuple((step.end,) * 16 for step in steps) for _ in universe.symbols)
            inputs = replace(
                base,
                input_id=f"SYN:RIDGE_INPUT:{day}:{origin}",
                plan=plan,
                stock=stock,
                available_at=times,
            )
            entries, exits = [], []
            for i, alias in enumerate(LEGACY_KEYS):
                entries.append(
                    HourlyCloseReference(
                        alias,
                        f"SYN:LABEL_ENTRY:{day}:{origin}:{i}",
                        plan.cutoff - pd.Timedelta(hours=1),
                        plan.cutoff,
                        100.0,
                        "SYN:LABEL_SOURCE",
                        "SYNTHETIC",
                        plan.cutoff,
                        "SYNTHETIC",
                        "SYN:EVIDENCE",
                    )
                )
                close = plan.cutoff + pd.Timedelta(hours=4)
                exits.append(
                    HourlyCloseReference(
                        alias,
                        f"SYN:LABEL_EXIT:{day}:{origin}:{i}",
                        close - pd.Timedelta(hours=1),
                        close,
                        100.0 * math.exp(0.0 if zero_labels else (i - 2) * 0.01),
                        "SYN:LABEL_SOURCE",
                        "SYNTHETIC",
                        close,
                        "SYNTHETIC",
                        "SYN:EVIDENCE",
                    )
                )
                for kind in SCALED:
                    stock_records.append(
                        FitObservation(
                            alias,
                            plan.cutoff,
                            kind,
                            (alias, day, origin),
                            0.0,
                            f"SYN:FIT:{day}:{origin}:{alias}:{kind}",
                            base.stock.source_binding,
                            base.stock.action_binding,
                            "SYNTHETIC",
                            plan.cutoff,
                            origin if kind == "M2" else None,
                        )
                    )
                for kind, value in (
                    ("RMS12", 0.01),
                    ("RMS60", 0.02),
                    ("RMS63", 0.03),
                    ("VOLUME_H", 100.0),
                    ("VOLUME_D", 1000.0),
                ):
                    floor_records.append(
                        FitObservation(
                            alias,
                            plan.cutoff,
                            kind,
                            (alias, day, origin),
                            value,
                            f"SYN:FLOOR:{day}:{origin}:{alias}:{kind}",
                            base.stock.source_binding,
                            base.stock.action_binding,
                            "SYNTHETIC",
                            plan.cutoff,
                        )
                    )
            label = proxy_label_sample(
                plan,
                ForecastEvidence(True, plan.cutoff, LEGACY_KEYS, "SYNTHETIC", inputs.input_id),
                tuple(entries),
                tuple(exits),
                observed_at=plan.exit,
                actions=ActionScope(
                    plan.cutoff, plan.exit, LEGACY_KEYS, "SYNTHETIC", "SYN:ACTION_COVERAGE"
                ),
                test_scenario=True,
            )
            origins.append(RidgeOrigin(inputs, label))
            for step in steps:
                market_by_time[step.end] = MarketVector(
                    step.end,
                    (0.0, 0.0, 0.0, 0.0, 0.0),
                    "VECTOR_VALID",
                    ("SYN:MARKET:" + step.end.isoformat(),),
                    "SYNTHETIC",
                )
            measures.append(
                MarketMeasures(
                    timestamp=plan.cutoff,
                    hourly_return=0.0,
                    rms12=0.01,
                    rms60=0.02,
                    daily_rms63=0.03,
                    momentum5=0.0,
                    momentum20=0.0,
                    reason="OBSERVATION_VALID",
                    evidence_ids=("SYN:MEASURES",),
                    basis="SYNTHETIC",
                )
            )
        clock = calendar.clock(day)
        assert clock.close is not None
        daily.append(DailyScaleSample(clock.close, 0.03, "SYNTHETIC"))
    return FitData(
        universe,
        tuple(origins),
        tuple(stock_records),
        tuple(floor_records),
        tuple(market_by_time[t] for t in sorted(market_by_time)),
        tuple(measures),
        tuple(daily),
        "SYNTHETIC",
    )


def random_fixture(universe: UniverseSpec):
    from .baseline_random import RandomOpportunity
    from .p3_audit import START, toy_engine, toy_forecast, toy_refs
    from .p3_execution import ExecutionOffer
    from .p3_replay import ReplayFrame

    engine = toy_engine(universe)
    opportunities, frames = [], []
    for origin in (1, 2):
        f = toy_forecast(universe, origin)
        assert f.plan.entry is not None and f.plan.cutoff is not None
        opportunities.append(
            RandomOpportunity(
                universe,
                f"SYN:OP:{origin}",
                f"SYN:INPUT:{origin}",
                f.plan,
                f.plan.cutoff,
                True,
                "SYNTHETIC",
            )
        )
        refs = toy_refs(
            engine.book,
            f.plan.entry,
            Decimal(100) if origin == 1 else Decimal("102.02"),
            f.plan.cutoff,
        )
        frames.append(
            ReplayFrame(
                universe,
                f"SYN:ENTRY:{origin}",
                f.plan.entry,
                refs,
                tuple(ExecutionOffer(universe, r) for r in refs),
            )
        )
    f = toy_forecast(universe, 1)
    assert f.plan.exit is not None
    # A missing scheduled reference followed by an explicitly fabricated minute open.
    marks = toy_refs(engine.book, f.plan.exit, cutoff=f.plan.exit - pd.Timedelta(minutes=3))
    frames.append(ReplayFrame(universe, "SYN:MISSING_EXIT", f.plan.exit, marks))
    retry = f.plan.exit + pd.Timedelta(minutes=1)
    refs = toy_refs(engine.book, retry)
    frames.append(
        ReplayFrame(
            universe,
            "SYN:1434_RETRY",
            retry,
            refs,
            tuple(ExecutionOffer(universe, r) for r in refs),
        )
    )
    f = toy_forecast(universe, 2)
    assert f.plan.exit is not None and f.plan.cutoff is not None
    refs = toy_refs(engine.book, f.plan.exit, cutoff=f.plan.cutoff + pd.Timedelta(hours=4))
    frames.append(
        ReplayFrame(
            universe,
            "SYN:EXIT2",
            f.plan.exit,
            refs,
            tuple(ExecutionOffer(universe, r) for r in refs),
        )
    )
    frames.append(
        ReplayFrame(universe, "SYN:CLOSE", pd.Timestamp("2020-08-03T20:00Z"), borrow_close=True)
    )
    for origin in (1, 2):
        early = toy_forecast(universe, origin, day="2020-11-27")
        assert early.plan.cutoff is not None
        opportunities.append(
            RandomOpportunity(
                universe,
                f"SYN:EARLY:{origin}",
                f"SYN:EARLY_INPUT:{origin}",
                early.plan,
                early.plan.cutoff,
                True,
                "SYNTHETIC",
            )
        )
    return tuple(opportunities), tuple(frames), START
