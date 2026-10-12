from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from lstm_data.corporate_actions import Action, SourceEvidence
from lstm_data.labels import UNIVERSE
from lstm_data.m2 import ScheduledCalendar
from lstm_data.stock_source import (
    StockBar,
    StockCalendar,
    StockHistory,
    convert_split_basis,
    proxy_reference,
    source_reason,
)


def session_bars(calendar, day, *, symbol="AAPL", unknown=False):
    clock = calendar.clock(day)
    slots = [(i, h) for i, h in enumerate(clock.hours, 1)]
    if clock.terminal_stub is not None:
        slots.append((0, clock.terminal_stub))
    return tuple(
        StockBar(
            symbol,
            day,
            i,
            h.start,
            h.end,
            100.0,
            103.0,
            99.0,
            102.0,
            10.0,
            (f"{symbol}:{day}:{i}",),
            available_at=None if unknown else h.end,
            basis="UNKNOWN" if unknown else "SYNTHETIC",
            action_verified=not unknown,
            action_ref="synthetic",
            evidence_ref="synthetic",
        )
        for i, h in slots
    )


@pytest.mark.parametrize("day,hours", [("2020-07-01", 6), ("2020-11-27", 3)])
def test_daily_volume_includes_stub_but_neural_grid_excludes_it(day, hours):
    calendar = StockCalendar(day, day)
    bars = session_bars(calendar, day)
    history = StockHistory(calendar, bars, synthetic=True)
    daily = history.daily["AAPL", day]
    assert len(calendar.steps) == hours and len(bars) == hours + 1
    assert daily.volume == (hours + 1) * 10 and daily.close == 102
    row = history.hour("AAPL", calendar.steps[-1])
    assert row is not None and row.slot == hours
    assert proxy_reference(bars[-1], 1.0, "synthetic") is None


def test_missing_hour_invalidates_full_volume_without_manufacturing_a_daily_close():
    calendar = StockCalendar("2020-07-01", "2020-07-01")
    bars = session_bars(calendar, "2020-07-01")
    history = StockHistory(calendar, tuple(b for b in bars if b.slot != 2), synthetic=True)
    assert history.daily["AAPL", "2020-07-01"].volume is None
    assert history.daily["AAPL", "2020-07-01"].close == 102
    assert history.hour("AAPL", calendar.steps[1]) is None


def test_unknown_late_wrong_slot_duplicate_and_nonfinite_source_fail_closed():
    calendar = StockCalendar("2020-07-01", "2020-07-01")
    row = session_bars(calendar, "2020-07-01", unknown=True)[0]
    assert source_reason(row, row.end) == "SOURCE_PUBLICATION_UNKNOWN"
    assert proxy_reference(row, None) is None
    reference = proxy_reference(row, 2.0, "explicit-conversion")
    assert reference is not None and reference.available_at is None and reference.raw_close == 204
    documented = replace(
        row,
        basis="DOCUMENTED",
        available_at=row.end,
        action_verified=True,
        evidence_ref="caller-documentation",
    )
    assert proxy_reference(documented, 2.0, "factor") is None
    assert proxy_reference(documented, 2.0, "factor", conversion_known_at=row.end) is not None
    assert (
        source_reason(
            replace(row, basis="SYNTHETIC", available_at=row.end, action_verified=True), row.end
        )
        == "SYNTHETIC_NOT_AUTHORIZED"
    )
    with pytest.raises(ValueError, match="DUPLICATE"):
        StockHistory(calendar, (row, row))
    with pytest.raises(ValueError, match="OFF_SCHEDULE"):
        StockHistory(calendar, (replace(row, session="2020-07-01", slot=2),))
    for change in ({"high": 98.0}, {"close": float("inf")}, {"volume": -1.0}):
        with pytest.raises(ValueError):
            replace(row, **change)
    assert replace(row, volume=0.0).volume == 0
    assert replace(row, open=100.0, close=100.0, high=100.0, low=100.0).zero_range


def test_split_prices_and_volumes_reciprocal_without_mutating_raw_or_inventing_publication():
    calendar = StockCalendar("2020-07-01", "2020-07-01")
    row = replace(session_bars(calendar, "2020-07-01")[0], share_basis="pre", price_basis="RAW")
    et = ZoneInfo("America/New_York")
    action = Action(
        SourceEvidence(
            "split",
            "a" * 64,
            datetime(2020, 7, 2, 8, tzinfo=et),
            datetime(2020, 7, 2, 8, tzinfo=et),
        ),
        "AAPL",
        "SPLIT",
        datetime(2020, 7, 2, 9, 30, tzinfo=et),
        0,
        Decimal(4),
        "pre",
        "post",
        fractional_policy="EXACT_FRACTIONAL_ASSUMPTION",
    )
    cutoff = pd.Timestamp("2020-07-02T14:30Z")
    converted = convert_split_basis(row, action, cutoff)
    assert converted.close == row.close / 4 and converted.volume == row.volume * 4
    assert row.close == 102 and row.volume == 10 and row.share_basis == "pre"
    assert converted.share_basis == "post"
    assert proxy_reference(converted, 4.0, "future-factor") is None
    assert converted.available_at == row.available_at  # Native publication is preserved.
    assert source_reason(converted, row.end, synthetic=True) == "ACTION_BASIS_NOT_AVAILABLE_AT_STEP"
    with pytest.raises(ValueError, match="UNVERIFIED"):
        convert_split_basis(
            row, replace(action, source=replace(action.source, publication_at=None)), cutoff
        )
    with pytest.raises(ValueError, match="UNVERIFIED"):
        convert_split_basis(row, action, row.end)


def test_calendar_memoization_preserves_original_m2_origin_semantics_across_dst_and_half_day():
    calendar = StockCalendar("2020-10-20", "2020-12-01")
    original = ScheduledCalendar("2020-10-20", "2020-12-01")
    for step in calendar.steps:
        if step.session in ("2020-11-02", "2020-11-30"):
            for origin in (1, 2):
                assert calendar.previous_origins(step, origin) == original.previous_origins(
                    step, origin
                )
    assert "2020-11-27" not in calendar.previous_origins(calendar.steps[-1], 1)
    assert UNIVERSE == ("AAPL", "JPM", "JNJ", "WMT", "CAT")
